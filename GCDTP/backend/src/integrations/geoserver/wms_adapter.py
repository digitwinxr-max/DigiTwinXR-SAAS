"""
WMS Adapter

Web Map Service adapter for GeoServer.
Provides endpoint abstraction for WMS operations.
"""

from typing import Dict, List, Optional, Any
from backend.src.integrations.geoserver.geoserver_client import GeoServerClient
from backend.src.integrations.geoserver.geoserver_types import ServiceEndpoint, ServiceType


class WMSAdapter:
    """
    WMS Service adapter.
    
    Responsibilities:
    - WMS endpoint management
    - Map rendering requests
    - Feature info requests
    - Legend graphic requests
    
    Note: No data ownership.
    """
    
    def __init__(self, client: Optional[GeoServerClient] = None):
        self.client = client or GeoServerClient()
    
    def get_capabilities_url(
        self,
        workspace: Optional[str] = None,
        base_url: str = "http://localhost:8080/geoserver"
    ) -> str:
        """
        Get WMS capabilities URL.
        
        Args:
            workspace: Optional workspace
            base_url: Base GeoServer URL
            
        Returns:
            Capabilities URL
        """
        if workspace:
            return f"{base_url}/{workspace}/wms?service=WMS&version=1.3.0&request=GetCapabilities"
        return f"{base_url}/wms?service=WMS&version=1.3.0&request=GetCapabilities"
    
    def get_map_url(
        self,
        workspace: str,
        layers: List[str],
        bbox: Dict[str, float],
        width: int = 800,
        height: int = 600,
        format: str = "image/png",
        base_url: str = "http://localhost:8080/geoserver",
        styles: Optional[List[str]] = None,
        srs: str = "EPSG:4326"
    ) -> str:
        """
        Build WMS GetMap URL.
        
        Args:
            workspace: Workspace name
            layers: Layer names
            bbox: Bounding box {minx, miny, maxx, maxy}
            width: Image width
            height: Image height
            format: Output format
            base_url: Base GeoServer URL
            styles: Style names
            srs: Spatial reference system
            
        Returns:
            GetMap URL
        """
        params = {
            "service": "WMS",
            "version": "1.3.0",
            "request": "GetMap",
            "layers": ",".join(layers),
            "bbox": f"{bbox['minx']},{bbox['miny']},{bbox['maxx']},{bbox['maxy']}",
            "width": str(width),
            "height": str(height),
            "format": format,
            "crs": srs,
        }
        
        if styles:
            params["styles"] = ",".join(styles)
        
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{base_url}/{workspace}/wms?{query}"
    
    def get_feature_info_url(
        self,
        workspace: str,
        layers: List[str],
        bbox: Dict[str, float],
        width: int,
        height: int,
        x: int,
        y: int,
        info_format: str = "application/vnd.ogc.gml",
        base_url: str = "http://localhost:8080/geoserver",
        query_layers: Optional[List[str]] = None
    ) -> str:
        """
        Build WMS GetFeatureInfo URL.
        
        Args:
            workspace: Workspace name
            layers: Layer names
            bbox: Bounding box
            width: Image width
            height: Image height
            x: X coordinate of click
            y: Y coordinate of click
            info_format: Output format
            base_url: Base GeoServer URL
            query_layers: Layers to query
            
        Returns:
            GetFeatureInfo URL
        """
        params = {
            "service": "WMS",
            "version": "1.3.0",
            "request": "GetFeatureInfo",
            "layers": ",".join(layers),
            "query_layers": ",".join(query_layers or layers),
            "bbox": f"{bbox['minx']},{bbox['miny']},{bbox['maxx']},{bbox['maxy']}",
            "width": str(width),
            "height": str(height),
            "x": str(x),
            "y": str(y),
            "info_format": info_format,
        }
        
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{base_url}/{workspace}/wms?{query}"
    
    def get_legend_url(
        self,
        workspace: str,
        layer: str,
        style: Optional[str] = None,
        width: int = 20,
        height: int = 20,
        base_url: str = "http://localhost:8080/geoserver",
        format: str = "image/png"
    ) -> str:
        """
        Build WMS GetLegendGraphic URL.
        
        Args:
            workspace: Workspace name
            layer: Layer name
            style: Style name
            width: Icon width
            height: Icon height
            base_url: Base GeoServer URL
            format: Output format
            
        Returns:
            GetLegendGraphic URL
        """
        params = {
            "service": "WMS",
            "request": "GetLegendGraphic",
            "layer": layer,
            "width": str(width),
            "height": str(height),
            "format": format,
        }
        
        if style:
            params["style"] = style
        
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{base_url}/{workspace}/wms?{query}"
    
    def configure_wms_service(
        self,
        workspace: str,
        enabled: bool = True,
        version: str = "1.3.0"
    ) -> Dict[str, Any]:
        """
        Configure WMS service for a workspace.
        
        Args:
            workspace: Workspace name
            enabled: Enable/disable service
            version: WMS version
            
        Returns:
            Configuration result
        """
        try:
            result = self.client.configure_wms(workspace, enabled)
            
            endpoint = ServiceEndpoint(
                id="",
                workspace_id="",
                service_type=ServiceType.WMS,
                is_enabled=enabled,
                version=version
            )
            
            return {
                "success": True,
                "workspace": workspace,
                "service": "wms",
                "enabled": enabled,
                "version": version
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
