"""
Style Manager

Manages GeoServer SLD styles.
"""

import uuid
from typing import Dict, List, Optional
from backend.src.integrations.geoserver.geoserver_client import GeoServerClient
from backend.src.integrations.geoserver.geoserver_types import Style
from backend.src.core.events import get_event_bus, EventType


class StyleManager:
    """
    Manages SLD styles.
    
    Responsibilities:
    - SLD style registration
    - Default styles
    - Layer style assignment
    - Style lookup
    """
    
    def __init__(self, client: Optional[GeoServerClient] = None):
        self.client = client or GeoServerClient()
        self.event_bus = get_event_bus()
        
        # Local storage
        self._styles: Dict[str, Style] = {}
        self._layer_styles: Dict[str, str] = {}  # layer_id -> style_id
        self._workspace_styles: Dict[str, List[str]] = {}  # workspace_id -> [style_ids]
    
    def close(self):
        """Close the client."""
        self.client.close()
    
    def register_style(
        self,
        workspace_id: str,
        name: str,
        sld_content: str = "",
        filename: str = "",
        is_default: bool = False,
        layer_id: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> Style:
        """
        Register a new style.
        
        Args:
            workspace_id: Workspace ID
            name: Style name
            sld_content: SLD content
            filename: SLD filename
            is_default: Is default style
            layer_id: Optional layer ID
            created_by: User creating
            
        Returns:
            Created Style
        """
        style = Style(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            name=name,
            filename=filename,
            sld_content=sld_content,
            is_default=is_default,
            layer_id=layer_id,
            created_by=created_by
        )
        
        # Sync to GeoServer
        if sld_content:
            try:
                self.client.create_style(name, sld_content, workspace_id)
            except Exception:
                pass
        
        # Store locally
        self._styles[style.id] = style
        
        if workspace_id not in self._workspace_styles:
            self._workspace_styles[workspace_id] = []
        self._workspace_styles[workspace_id].append(style.id)
        
        # Assign to layer if specified
        if layer_id:
            self._layer_styles[layer_id] = style.id
        
        return style
    
    def get_style(self, style_id: str) -> Optional[Style]:
        """Get a style by ID."""
        return self._styles.get(style_id)
    
    def get_style_by_name(
        self,
        workspace_id: str,
        name: str
    ) -> Optional[Style]:
        """Get a style by name in a workspace."""
        for style in self._styles.values():
            if style.workspace_id == workspace_id and style.name == name:
                return style
        return None
    
    def get_styles_for_workspace(self, workspace_id: str) -> List[Style]:
        """Get all styles in a workspace."""
        style_ids = self._workspace_styles.get(workspace_id, [])
        return [self._styles[sid] for sid in style_ids if sid in self._styles]
    
    def get_default_style_for_layer(self, layer_id: str) -> Optional[Style]:
        """Get the default style for a layer."""
        style_id = self._layer_styles.get(layer_id)
        if style_id:
            return self._styles.get(style_id)
        return None
    
    def get_styles_for_layer(self, layer_id: str) -> List[Style]:
        """Get all styles for a layer."""
        return [s for s in self._styles.values() if s.layer_id == layer_id]
    
    def assign_style_to_layer(
        self,
        style_id: str,
        layer_id: str,
        as_default: bool = False
    ) -> bool:
        """
        Assign a style to a layer.
        
        Args:
            style_id: Style ID
            layer_id: Layer ID
            as_default: Set as default style
            
        Returns:
            True if assigned
        """
        style = self._styles.get(style_id)
        if not style:
            return False
        
        style.layer_id = layer_id
        
        if as_default:
            # Remove default from other styles for this layer
            for s in self._styles.values():
                if s.layer_id == layer_id:
                    s.is_default = False
            style.is_default = True
        
        self._layer_styles[layer_id] = style_id
        
        # Publish event
        self.event_bus.publish(
            EventType.STYLE_ASSIGNED,
            source="style_manager",
            data={
                "style_id": style_id,
                "layer_id": layer_id,
                "name": style.name,
                "is_default": as_default
            }
        )
        
        return True
    
    def remove_style_from_layer(self, style_id: str, layer_id: str) -> bool:
        """Remove a style from a layer."""
        style = self._styles.get(style_id)
        if not style:
            return False
        
        style.layer_id = None
        style.is_default = False
        
        if self._layer_styles.get(layer_id) == style_id:
            del self._layer_styles[layer_id]
        
        return True
    
    def update_style(
        self,
        style: Style,
        **kwargs
    ) -> Style:
        """
        Update a style.
        
        Args:
            style: Style to update
            **kwargs: Fields to update
            
        Returns:
            Updated Style
        """
        for key, value in kwargs.items():
            if hasattr(style, key):
                setattr(style, key, value)
        
        style.updated_at = datetime.utcnow()
        return style
    
    def delete_style(self, style_id: str) -> bool:
        """
        Delete a style.
        
        Args:
            style_id: Style ID
            
        Returns:
            True if deleted
        """
        style = self._styles.get(style_id)
        if not style:
            return False
        
        # Remove from layer association
        if style.layer_id and self._layer_styles.get(style.layer_id) == style_id:
            del self._layer_styles[style.layer_id]
        
        # Remove from workspace index
        workspace_id = style.workspace_id
        if workspace_id in self._workspace_styles:
            if style_id in self._workspace_styles[workspace_id]:
                self._workspace_styles[workspace_id].remove(style_id)
        
        del self._styles[style_id]
        return True
    
    def get_style_count(self, workspace_id: Optional[str] = None) -> int:
        """Get style count."""
        if workspace_id:
            return len(self._workspace_styles.get(workspace_id, []))
        return len(self._styles)
    
    # =========================================================================
    # Default Styles
    # =========================================================================
    
    def create_default_styles(self, workspace_id: str) -> List[Style]:
        """Create default styles for a workspace."""
        default_styles = [
            ("point", self._get_point_style()),
            ("line", self._get_line_style()),
            ("polygon", self._get_polygon_style()),
            ("raster", self._get_raster_style()),
        ]
        
        styles = []
        for name, sld in default_styles:
            style = self.register_style(
                workspace_id=workspace_id,
                name=name,
                sld_content=sld,
                filename=f"{name}.sld",
                is_default=True
            )
            styles.append(style)
        
        return styles
    
    def _get_point_style(self) -> str:
        """Get default point style SLD."""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld">
  <NamedLayer>
    <Name>point</Name>
    <UserStyle>
      <FeatureTypeStyle>
        <Rule>
          <PointSymbolizer>
            <Graphic>
              <Mark>
                <WellKnownName>circle</WellKnownName>
                <Fill>
                  <CssParameter name="fill">#FF0000</CssParameter>
                </Fill>
              </Mark>
              <Size>6</Size>
            </Graphic>
          </PointSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>'''
    
    def _get_line_style(self) -> str:
        """Get default line style SLD."""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld">
  <NamedLayer>
    <Name>line</Name>
    <UserStyle>
      <FeatureTypeStyle>
        <Rule>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#0000FF</CssParameter>
              <CssParameter name="stroke-width">2</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>'''
    
    def _get_polygon_style(self) -> str:
        """Get default polygon style SLD."""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld">
  <NamedLayer>
    <Name>polygon</Name>
    <UserStyle>
      <FeatureTypeStyle>
        <Rule>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#00FF00</CssParameter>
              <CssParameter name="fill-opacity">0.5</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#008000</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>'''
    
    def _get_raster_style(self) -> str:
        """Get default raster style SLD."""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld">
  <NamedLayer>
    <Name>raster</Name>
    <UserStyle>
      <FeatureTypeStyle>
        <Rule>
          <RasterSymbolizer>
            <Opacity>1.0</Opacity>
          </RasterSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>'''
