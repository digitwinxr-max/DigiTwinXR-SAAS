"""
GeoServer Client

Client for communicating with GeoServer REST API.
FastAPI remains authoritative for business logic.
GeoServer provides spatial publishing only.
"""

import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
from backend.src.integrations.geoserver.geoserver_types import (
    Workspace,
    PublishedLayer,
    Style,
    ServiceEndpoint,
    LayerGroup,
    LayerType,
    ServiceType,
)


class GeoServerClientError(Exception):
    """GeoServer client error."""
    pass


class GeoServerClient:
    """
    Client for GeoServer REST API.
    
    Responsibilities:
    - Workspace management
    - Layer publishing
    - Style management
    - Service configuration
    
    Note: All business logic remains in FastAPI.
    GeoServer provides spatial publishing only.
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8080/geoserver",
        username: str = "admin",
        password: str = "geoserver"
    ):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self._client: Optional[httpx.Client] = None
    
    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                auth=(self.username, self.password),
                timeout=30.0
            )
        return self._client
    
    def close(self):
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None
    
    # =========================================================================
    # Workspace Operations
    # =========================================================================
    
    def get_workspaces(self) -> List[Dict[str, Any]]:
        """Get all workspaces."""
        try:
            response = self._get_client().get("/rest/workspaces.json")
            response.raise_for_status()
            data = response.json()
            return data.get("workspaces", {}).get("workspace", [])
        except httpx.HTTPError as e:
            raise GeoServerClientError(f"Failed to get workspaces: {e}")
    
    def create_workspace(self, name: str, uri: str) -> Dict[str, Any]:
        """Create a workspace."""
        payload = {
            "workspace": {
                "name": name,
                "uri": uri
            }
        }
        try:
            response = self._get_client().post(
                "/rest/workspaces",
                json=payload
            )
            response.raise_for_status()
            return {"name": name, "uri": uri}
        except httpx.HTTPError as e:
            raise GeoServerClientError(f"Failed to create workspace: {e}")
    
    def delete_workspace(self, name: str, recurse: bool = False) -> bool:
        """Delete a workspace."""
        try:
            params = {"recurse": str(recurse).lower()}
            response = self._get_client().delete(
                f"/rest/workspaces/{name}",
                params=params
            )
            return response.status_code in [200, 204]
        except httpx.HTTPError as e:
            raise GeoServerClientError(f"Failed to delete workspace: {e}")
    
    # =========================================================================
    # Layer Operations
    # =========================================================================
    
    def get_layers(self, workspace: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all layers."""
        try:
            if workspace:
                url = f"/rest/workspaces/{workspace}/layers.json"
            else:
                url = "/rest/layers.json"
            
            response = self._get_client().get(url)
            response.raise_for_status()
            data = response.json()
            return data.get("layers", {}).get("layer", [])
        except httpx.HTTPError as e:
            raise GeoServerClientError(f"Failed to get layers: {e}")
    
    def publish_layer(
        self,
        workspace: str,
        datastore: str,
        layer_name: str,
        title: str = "",
        abstract: str = ""
    ) -> Dict[str, Any]:
        """Publish a layer from a datastore."""
        payload = {
            "featureType": {
                "name": layer_name,
                "title": title,
                "abstract": abstract
            }
        }
        try:
            response = self._get_client().post(
                f"/rest/workspaces/{workspace}/datastores/{datastore}/featuretypes",
                json=payload
            )
            response.raise_for_status()
            return {"workspace": workspace, "layer": layer_name}
        except httpx.HTTPError as e:
            raise GeoServerClientError(f"Failed to publish layer: {e}")
    
    def update_layer(
        self,
        workspace: str,
        layer_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Update a layer."""
        try:
            response = self._get_client().put(
                f"/rest/workspaces/{workspace}/layers/{layer_name}.json",
                json=kwargs
            )
            response.raise_for_status()
            return {"workspace": workspace, "layer": layer_name, "updated": True}
        except httpx.HTTPError as e:
            raise GeoServerClientError(f"Failed to update layer: {e}")
    
    def delete_layer(self, workspace: str, layer_name: str) -> bool:
        """Delete a layer."""
        try:
            response = self._get_client().delete(
                f"/rest/workspaces/{workspace}/layers/{layer_name}"
            )
            return response.status_code in [200, 204]
        except httpx.HTTPError as e:
            raise GeoServerClientError(f"Failed to delete layer: {e}")
    
    # =========================================================================
    # Style Operations
    # =========================================================================
    
    def get_styles(self, workspace: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all styles."""
        try:
            if workspace:
                url = f"/rest/workspaces/{workspace}/styles.json"
            else:
                url = "/rest/styles.json"
            
            response = self._get_client().get(url)
            response.raise_for_status()
            data = response.json()
            return data.get("styles", {}).get("style", [])
        except httpx.HTTPError as e:
            raise GeoServerClientError(f"Failed to get styles: {e}")
    
    def create_style(
        self,
        name: str,
        sld_content: str,
        workspace: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new style."""
        headers = {"Content-Type": "application/vnd.ogc.sld+xml"}
        try:
            if workspace:
                url = f"/rest/workspaces/{workspace}/styles/{name}.sld"
            else:
                url = f"/rest/styles/{name}.sld"
            
            response = self._get_client().put(
                url,
                content=sld_content,
                headers=headers
            )
            response.raise_for_status()
            return {"name": name, "workspace": workspace}
        except httpx.HTTPError as e:
            raise GeoServerClientError(f"Failed to create style: {e}")
    
    def assign_style_to_layer(
        self,
        style_name: str,
        layer_name: str,
        workspace: str
    ) -> bool:
        """Assign a style to a layer."""
        payload = {"layer": {"defaultStyle": {"name": style_name}}}
        try:
            response = self._get_client().put(
                f"/rest/workspaces/{workspace}/layers/{layer_name}.json",
                json=payload
            )
            response.raise_for_status()
            return True
        except httpx.HTTPError as e:
            raise GeoServerClientError(f"Failed to assign style: {e}")
    
    # =========================================================================
    # Service Operations
    # =========================================================================
    
    def get_services(self, workspace: Optional[str] = None) -> Dict[str, Any]:
        """Get service configuration."""
        try:
            if workspace:
                url = f"/rest/services/{workspace}.json"
            else:
                url = "/rest/services.json"
            
            response = self._get_client().get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise GeoServerClientError(f"Failed to get services: {e}")
    
    def configure_wms(
        self,
        workspace: str,
        enabled: bool = True
    ) -> Dict[str, Any]:
        """Configure WMS service."""
        payload = {"wms": {"enabled": enabled}}
        try:
            response = self._get_client().put(
                f"/rest/services/wms/workspaces/{workspace}.json",
                json=payload
            )
            response.raise_for_status()
            return {"workspace": workspace, "wms_enabled": enabled}
        except httpx.HTTPError as e:
            raise GeoServerClientError(f"Failed to configure WMS: {e}")
    
    def configure_wfs(
        self,
        workspace: str,
        enabled: bool = True
    ) -> Dict[str, Any]:
        """Configure WFS service."""
        payload = {"wfs": {"enabled": enabled}}
        try:
            response = self._get_client().put(
                f"/rest/services/wfs/workspaces/{workspace}.json",
                json=payload
            )
            response.raise_for_status()
            return {"workspace": workspace, "wfs_enabled": enabled}
        except httpx.HTTPError as e:
            raise GeoServerClientError(f"Failed to configure WFS: {e}")
    
    def configure_wcs(
        self,
        workspace: str,
        enabled: bool = True
    ) -> Dict[str, Any]:
        """Configure WCS service."""
        payload = {"wcs": {"enabled": enabled}}
        try:
            response = self._get_client().put(
                f"/rest/services/wcs/workspaces/{workspace}.json",
                json=payload
            )
            response.raise_for_status()
            return {"workspace": workspace, "wcs_enabled": enabled}
        except httpx.HTTPError as e:
            raise GeoServerClientError(f"Failed to configure WCS: {e}")
    
    # =========================================================================
    # Layer Groups
    # =========================================================================
    
    def get_layer_groups(self, workspace: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get layer groups."""
        try:
            if workspace:
                url = f"/rest/workspaces/{workspace}/layergroups.json"
            else:
                url = "/rest/layergroups.json"
            
            response = self._get_client().get(url)
            response.raise_for_status()
            data = response.json()
            return data.get("layerGroups", {}).get("layerGroup", [])
        except httpx.HTTPError as e:
            raise GeoServerClientError(f"Failed to get layer groups: {e}")
    
    def create_layer_group(
        self,
        name: str,
        workspace: str,
        layers: List[str],
        styles: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a layer group."""
        payload = {
            "layerGroup": {
                "name": name,
                "workspace": workspace,
                "layers": layers,
                "styles": styles or []
            }
        }
        try:
            response = self._get_client().post(
                f"/rest/workspaces/{workspace}/layergroups",
                json=payload
            )
            response.raise_for_status()
            return {"name": name, "workspace": workspace, "layers": layers}
        except httpx.HTTPError as e:
            raise GeoServerClientError(f"Failed to create layer group: {e}")
    
    # =========================================================================
    # Capabilities
    # =========================================================================
    
    def get_wms_capabilities(self, workspace: Optional[str] = None) -> str:
        """Get WMS capabilities document."""
        try:
            if workspace:
                url = f"/{workspace}/wms?service=WMS&request=GetCapabilities"
            else:
                url = "/wms?service=WMS&request=GetCapabilities"
            
            response = self._get_client().get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as e:
            raise GeoServerClientError(f"Failed to get WMS capabilities: {e}")
    
    def get_wfs_capabilities(self, workspace: Optional[str] = None) -> str:
        """Get WFS capabilities document."""
        try:
            if workspace:
                url = f"/{workspace}/wfs?service=WFS&request=GetCapabilities"
            else:
                url = "/wfs?service=WFS&request=GetCapabilities"
            
            response = self._get_client().get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as e:
            raise GeoServerClientError(f"Failed to get WFS capabilities: {e}")
    
    # =========================================================================
    # Health Check
    # =========================================================================
    
    def health_check(self) -> bool:
        """Check GeoServer health."""
        try:
            response = self._get_client().get("/rest/about/status.json")
            return response.status_code == 200
        except httpx.HTTPError:
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """Get GeoServer information."""
        try:
            response = self._get_client().get("/rest/about/version.json")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise GeoServerClientError(f"Failed to get info: {e}")
