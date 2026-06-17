"""
WFS Adapter

Web Feature Service adapter for GeoServer.
Provides endpoint abstraction for WFS operations.
"""

from typing import Dict, List, Optional, Any
from backend.src.integrations.geoserver.geoserver_client import GeoServerClient
from backend.src.integrations.geoserver.geoserver_types import ServiceEndpoint, ServiceType


class WFSAdapter:
    """
    WFS Service adapter.
    
    Responsibilities:
    - WFS endpoint management
    - Feature request building
    - Transaction support
    - Describe feature type
    
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
        Get WFS capabilities URL.
        
        Args:
            workspace: Optional workspace
            base_url: Base GeoServer URL
            
        Returns:
            Capabilities URL
        """
        if workspace:
            return f"{base_url}/{workspace}/wfs?service=WFS&version=2.0.0&request=GetCapabilities"
        return f"{base_url}/wfs?service=WFS&version=2.0.0&request=GetCapabilities"
    
    def get_feature_url(
        self,
        workspace: str,
        type_names: List[str],
        base_url: str = "http://localhost:8080/geoserver",
        version: str = "2.0.0",
        output_format: str = "application/json",
        srs_name: str = "EPSG:4326",
        count: Optional[int] = None,
        start_index: Optional[int] = None,
        bbox: Optional[Dict[str, float]] = None,
        filter: Optional[str] = None,
        property_names: Optional[List[str]] = None
    ) -> str:
        """
        Build WFS GetFeature URL.
        
        Args:
            workspace: Workspace name
            type_names: Feature type names
            base_url: Base GeoServer URL
            version: WFS version
            output_format: Output format
            srs_name: Spatial reference system
            count: Max features
            start_index: Start index
            bbox: Bounding box filter
            filter: OGC filter
            property_names: Property names to return
            
        Returns:
            GetFeature URL
        """
        params = {
            "service": "WFS",
            "version": version,
            "request": "GetFeature",
            "typeNames": ",".join(type_names),
            "outputFormat": output_format,
            "srsName": srs_name,
        }
        
        if count:
            params["count"] = str(count)
        
        if start_index is not None:
            params["startIndex"] = str(start_index)
        
        if bbox:
            params["bbox"] = f"{bbox['minx']},{bbox['miny']},{bbox['maxx']},{bbox['maxy']}"
        
        if filter:
            params["filter"] = filter
        
        if property_names:
            params["propertyName"] = ",".join(property_names)
        
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{base_url}/{workspace}/wfs?{query}"
    
    def describe_feature_type_url(
        self,
        workspace: str,
        type_name: str,
        base_url: str = "http://localhost:8080/geoserver",
        version: str = "2.0.0",
        output_format: str = "application/json"
    ) -> str:
        """
        Build WFS DescribeFeatureType URL.
        
        Args:
            workspace: Workspace name
            type_name: Feature type name
            base_url: Base GeoServer URL
            version: WFS version
            output_format: Output format
            
        Returns:
            DescribeFeatureType URL
        """
        params = {
            "service": "WFS",
            "version": version,
            "request": "DescribeFeatureType",
            "typeName": type_name,
            "outputFormat": output_format,
        }
        
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{base_url}/{workspace}/wfs?{query}"
    
    def get_transaction_url(
        self,
        workspace: str,
        base_url: str = "http://localhost:8080/geoserver",
        version: str = "2.0.0",
        output_format: str = "application/json"
    ) -> str:
        """
        Build WFS Transaction URL.
        
        Args:
            workspace: Workspace name
            base_url: Base GeoServer URL
            version: WFS version
            output_format: Output format
            
        Returns:
            Transaction URL (POST recommended)
        """
        params = {
            "service": "WFS",
            "version": version,
            "outputFormat": output_format,
        }
        
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{base_url}/{workspace}/wfs?{query}"
    
    def configure_wfs_service(
        self,
        workspace: str,
        enabled: bool = True,
        version: str = "2.0.0"
    ) -> Dict[str, Any]:
        """
        Configure WFS service for a workspace.
        
        Args:
            workspace: Workspace name
            enabled: Enable/disable service
            version: WFS version
            
        Returns:
            Configuration result
        """
        try:
            result = self.client.configure_wfs(workspace, enabled)
            
            return {
                "success": True,
                "workspace": workspace,
                "service": "wfs",
                "enabled": enabled,
                "version": version
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
