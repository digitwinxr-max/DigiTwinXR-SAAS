"""
Layer Manager

Manages GeoServer published layers.
"""

import uuid
from typing import Dict, List, Optional
from backend.src.integrations.geoserver.geoserver_client import GeoServerClient
from backend.src.integrations.geoserver.geoserver_types import (
    PublishedLayer,
    LayerType,
    BoundingBox,
)
from backend.src.core.events import get_event_bus, EventType


class LayerManager:
    """
    Manages published layers.
    
    Responsibilities:
    - Publish layers
    - Unpublish layers
    - Update layers
    - Group layers
    - Manage metadata
    """
    
    def __init__(self, client: Optional[GeoServerClient] = None):
        self.client = client or GeoServerClient()
        self.event_bus = get_event_bus()
        
        # Local storage
        self._layers: Dict[str, PublishedLayer] = {}
        self._workspace_layers: Dict[str, List[str]] = {}  # workspace_id -> [layer_ids]
    
    def close(self):
        """Close the client."""
        self.client.close()
    
    def publish_layer(
        self,
        workspace_id: str,
        name: str,
        layer_type: LayerType = LayerType.VECTOR,
        title: str = "",
        abstract: str = "",
        native_name: str = "",
        keywords: Optional[List[str]] = None,
        srs: str = "EPSG:4326",
        bounding_box: Optional[BoundingBox] = None,
        created_by: Optional[str] = None
    ) -> PublishedLayer:
        """
        Publish a new layer.
        
        Args:
            workspace_id: Workspace ID
            name: Layer name
            layer_type: Layer type
            title: Layer title
            abstract: Layer abstract
            native_name: Native name in data store
            keywords: Keywords
            srs: Spatial reference system
            bounding_box: Bounding box
            created_by: User publishing
            
        Returns:
            Created PublishedLayer
        """
        layer = PublishedLayer(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            name=name,
            layer_type=layer_type,
            native_name=native_name or name,
            title=title or name,
            abstract=abstract,
            keywords=keywords or [],
            srs=srs
        )
        
        if bounding_box:
            layer.bbox_minx = bounding_box.minx
            layer.bbox_miny = bounding_box.miny
            layer.bbox_maxx = bounding_box.maxx
            layer.bbox_maxy = bounding_box.maxy
        
        # Store locally
        self._layers[layer.id] = layer
        
        if workspace_id not in self._workspace_layers:
            self._workspace_layers[workspace_id] = []
        self._workspace_layers[workspace_id].append(layer.id)
        
        # Publish event
        self.event_bus.publish(
            EventType.LAYER_PUBLISHED,
            source="layer_manager",
            data={
                "layer_id": layer.id,
                "workspace_id": workspace_id,
                "name": layer.name,
                "layer_type": layer.layer_type.value
            }
        )
        
        return layer
    
    def get_layer(self, layer_id: str) -> Optional[PublishedLayer]:
        """Get a layer by ID."""
        return self._layers.get(layer_id)
    
    def get_layer_by_name(
        self,
        workspace_id: str,
        name: str
    ) -> Optional[PublishedLayer]:
        """Get a layer by name in a workspace."""
        for layer in self._layers.values():
            if layer.workspace_id == workspace_id and layer.name == name:
                return layer
        return None
    
    def get_layers_for_workspace(
        self,
        workspace_id: str,
        published_only: bool = False
    ) -> List[PublishedLayer]:
        """Get all layers in a workspace."""
        layer_ids = self._workspace_layers.get(workspace_id, [])
        layers = [self._layers[lid] for lid in layer_ids if lid in self._layers]
        
        if published_only:
            layers = [l for l in layers if l.is_published]
        
        return layers
    
    def update_layer(
        self,
        layer: PublishedLayer,
        **kwargs
    ) -> PublishedLayer:
        """
        Update a layer.
        
        Args:
            layer: Layer to update
            **kwargs: Fields to update
            
        Returns:
            Updated PublishedLayer
        """
        for key, value in kwargs.items():
            if hasattr(layer, key):
                setattr(layer, key, value)
        
        layer.updated_at = datetime.utcnow()
        
        # Publish event
        self.event_bus.publish(
            EventType.LAYER_UPDATED,
            source="layer_manager",
            data={
                "layer_id": layer.id,
                "workspace_id": layer.workspace_id,
                "name": layer.name
            }
        )
        
        return layer
    
    def unpublish_layer(self, layer_id: str) -> bool:
        """
        Unpublish a layer.
        
        Args:
            layer_id: Layer ID
            
        Returns:
            True if unpublished
        """
        layer = self._layers.get(layer_id)
        if not layer:
            return False
        
        layer.is_published = False
        return True
    
    def delete_layer(self, layer_id: str) -> bool:
        """
        Delete a layer.
        
        Args:
            layer_id: Layer ID
            
        Returns:
            True if deleted
        """
        layer = self._layers.get(layer_id)
        if not layer:
            return False
        
        # Remove from workspace index
        workspace_id = layer.workspace_id
        if workspace_id in self._workspace_layers:
            if layer_id in self._workspace_layers[workspace_id]:
                self._workspace_layers[workspace_id].remove(layer_id)
        
        del self._layers[layer_id]
        return True
    
    def set_layer_published(
        self,
        layer_id: str,
        published: bool
    ) -> Optional[PublishedLayer]:
        """Set layer published status."""
        layer = self._layers.get(layer_id)
        if layer:
            layer.is_published = published
        return layer
    
    def set_layer_queryable(
        self,
        layer_id: str,
        queryable: bool
    ) -> Optional[PublishedLayer]:
        """Set layer queryable status."""
        layer = self._layers.get(layer_id)
        if layer:
            layer.is_queryable = queryable
        return layer
    
    def get_layer_count(self, workspace_id: Optional[str] = None) -> int:
        """Get layer count."""
        if workspace_id:
            return len(self._workspace_layers.get(workspace_id, []))
        return len(self._layers)
    
    def get_published_layers(
        self,
        layer_type: Optional[LayerType] = None
    ) -> List[PublishedLayer]:
        """Get all published layers."""
        layers = [l for l in self._layers.values() if l.is_published]
        
        if layer_type:
            layers = [l for l in layers if l.layer_type == layer_type]
        
        return layers
