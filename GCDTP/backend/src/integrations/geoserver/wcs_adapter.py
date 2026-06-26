"""
WCS Adapter

Web Coverage Service adapter for GeoServer.
Provides endpoint abstraction for WCS operations.
"""

from typing import Dict, List, Optional, Any
from backend.src.integrations.geoserver.geoserver_client import GeoServerClient
from backend.src.integrations.geoserver.geoserver_types import ServiceEndpoint, ServiceType


class WCSAdapter:
    """
    WCS Service adapter.
    
    Responsibilities:
    - WCS endpoint management
    - Coverage request building
    - Describe coverage
    - Get coverage
    
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
        Get WCS capabilities URL.
        
        Args:
            workspace: Optional workspace
            base_url: Base GeoServer URL
            
        Returns:
            Capabilities URL
        """
        if workspace:
            return f"{base_url}/{workspace}/wcs?service=WCS&version=2.0.1&request=GetCapabilities"
        return f"{base_url}/wcs?service=WCS&version=2.0.1&request=GetCapabilities"
    
    def describe_coverage_url(
        self,
        workspace: str,
        coverage_name: str,
        base_url: str = "http://localhost:8080/geoserver",
        version: str = "2.0.1"
    ) -> str:
        """
        Build WCS DescribeCoverage URL.
        
        Args:
            workspace: Workspace name
            coverage_name: Coverage name
            base_url: Base GeoServer URL
            version: WCS version
            
        Returns:
            DescribeCoverage URL
        """
        params = {
            "service": "WCS",
            "version": version,
            "request": "DescribeCoverage",
            "coverageId": f"{workspace}:{coverage_name}",
        }
        
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{base_url}/{workspace}/wcs?{query}"
    
    def get_coverage_url(
        self,
        workspace: str,
        coverage_name: str,
        base_url: str = "http://localhost:8080/geoserver",
        version: str = "2.0.1",
        format: str = "image/geotiff",
        subset: Optional[Dict[str, Any]] = None,
        mediatype: Optional[str] = None,
        size: Optional[List[int]] = None
    ) -> str:
        """
        Build WCS GetCoverage URL.
        
        Args:
            workspace: Workspace name
            coverage_name: Coverage name
            base_url: Base GeoServer URL
            version: WCS version
            format: Output format
            subset: Subsetting parameters
            mediatype: Media type
            size: Output size [width, height]
            
        Returns:
            GetCoverage URL
        """
        params = {
            "service": "WCS",
            "version": version,
            "request": "GetCoverage",
            "coverageId": f"{workspace}:{coverage_name}",
            "format": format,
        }
        
        if subset:
            for key, value in subset.items():
                if isinstance(value, dict):
                    params[f"subset={key}"] = f"({value.get('low', '')},{value.get('high', '')})"
                else:
                    params[f"subset={key}"] = f"({value})"
        
        if mediatype:
            params["mediatype"] = mediatype
        
        if size:
            params["size"] = f"{size[0]},{size[1]}"
        
        # Build query string
        parts = []
        for key, value in params.items():
            if key.startswith("subset="):
                parts.append(f"{key}={value}")
            else:
                parts.append(f"{key}={value}")
        
        return f"{base_url}/{workspace}/wcs?" + "&".join(parts)
    
    def configure_wcs_service(
        self,
        workspace: str,
        enabled: bool = True,
        version: str = "2.0.1"
    ) -> Dict[str, Any]:
        """
        Configure WCS service for a workspace.
        
        Args:
            workspace: Workspace name
            enabled: Enable/disable service
            version: WCS version
            
        Returns:
            Configuration result
        """
        try:
            result = self.client.configure_wcs(workspace, enabled)
            
            return {
                "success": True,
                "workspace": workspace,
                "service": "wcs",
                "enabled": enabled,
                "version": version
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_native_formats(self) -> List[str]:
        """Get supported native formats."""
        return [
            "image/geotiff",
            "image/tiff",
            "image/png",
            "image/jpeg",
            "application/x-hdf5",
            "application/x-netcdf",
        ]
    
    def get_output_formats(self) -> List[str]:
        """Get supported output formats."""
        return [
            "image/geotiff",
            "image/tiff",
            "image/png",
            "image/png8",
            "image/png24",
            "image/png32",
            "image/jpeg",
            "application/x-gzip",
            "application/x-netcdf",
            "application/x-hdf5",
        ]
