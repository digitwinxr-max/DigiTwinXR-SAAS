"""
GeoServer Validator

Validates workspaces, layers, styles, and services.
"""

from typing import Dict, List, Set, Optional
from backend.src.integrations.geoserver.geoserver_types import (
    Workspace,
    PublishedLayer,
    Style,
    ServiceEndpoint,
    LayerType,
    ServiceType,
)


class GeoServerValidator:
    """
    Validates GeoServer-related entities.
    
    Checks:
    - Duplicate layers
    - Invalid styles
    - Workspace conflicts
    - Service conflicts
    - Group consistency
    """
    
    def __init__(self):
        self.issues: List[str] = []
    
    def validate_workspace(self, workspace: Workspace) -> List[str]:
        """
        Validate a workspace.
        
        Args:
            workspace: Workspace to validate
            
        Returns:
            List of validation issues
        """
        self.issues = []
        
        # Required fields
        if not workspace.id:
            self.issues.append("Workspace ID is required")
        
        if not workspace.name or not workspace.name.strip():
            self.issues.append("Workspace name is required")
        
        if not workspace.uri or not workspace.uri.strip():
            self.issues.append("Workspace URI is required")
        
        # Name validation
        if workspace.name:
            if len(workspace.name) > 100:
                self.issues.append("Workspace name must be 100 characters or less")
            
            if not workspace.name.replace("_", "").replace("-", "").isalnum():
                self.issues.append("Workspace name must be alphanumeric (with _ or -)")
        
        return self.issues.copy()
    
    def validate_layer(self, layer: PublishedLayer) -> List[str]:
        """
        Validate a layer.
        
        Args:
            layer: Layer to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Required fields
        if not layer.id:
            issues.append("Layer ID is required")
        
        if not layer.workspace_id:
            issues.append("Workspace ID is required")
        
        if not layer.name or not layer.name.strip():
            issues.append("Layer name is required")
        
        # Name validation
        if layer.name:
            if len(layer.name) > 255:
                issues.append("Layer name must be 255 characters or less")
        
        # SRS validation
        if layer.srs and not layer.srs.startswith("EPSG:"):
            issues.append("SRS must be in EPSG format (e.g., EPSG:4326)")
        
        return issues
    
    def validate_style(self, style: Style) -> List[str]:
        """
        Validate a style.
        
        Args:
            style: Style to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Required fields
        if not style.id:
            issues.append("Style ID is required")
        
        if not style.workspace_id:
            issues.append("Workspace ID is required")
        
        if not style.name or not style.name.strip():
            issues.append("Style name is required")
        
        # Name validation
        if style.name:
            if len(style.name) > 255:
                issues.append("Style name must be 255 characters or less")
            
            if not style.name.replace("_", "").replace("-", "").isalnum():
                issues.append("Style name must be alphanumeric (with _ or -)")
        
        return issues
    
    def validate_service_endpoint(self, endpoint: ServiceEndpoint) -> List[str]:
        """
        Validate a service endpoint.
        
        Args:
            endpoint: Endpoint to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Required fields
        if not endpoint.id:
            issues.append("Endpoint ID is required")
        
        if not endpoint.workspace_id:
            issues.append("Workspace ID is required")
        
        if not isinstance(endpoint.service_type, ServiceType):
            issues.append("Valid service type is required")
        
        return issues
    
    def check_duplicate_layer(
        self,
        workspace_id: str,
        layer_name: str,
        existing_layers: Dict[str, PublishedLayer]
    ) -> bool:
        """
        Check for duplicate layer.
        
        Args:
            workspace_id: Workspace ID
            layer_name: Layer name
            existing_layers: Existing layers
            
        Returns:
            True if duplicate
        """
        for layer in existing_layers.values():
            if layer.workspace_id == workspace_id and layer.name == layer_name:
                return True
        return False
    
    def check_workspace_conflict(
        self,
        name: str,
        uri: str,
        existing_workspaces: Dict[str, Workspace]
    ) -> List[str]:
        """
        Check for workspace conflicts.
        
        Args:
            name: Workspace name
            uri: Workspace URI
            existing_workspaces: Existing workspaces
            
        Returns:
            List of conflicts
        """
        conflicts = []
        
        for workspace in existing_workspaces.values():
            if workspace.name == name:
                conflicts.append(f"Workspace name '{name}' already exists")
            
            if workspace.uri == uri:
                conflicts.append(f"Workspace URI '{uri}' already exists")
        
        return conflicts
    
    def check_service_conflict(
        self,
        workspace_id: str,
        service_type: ServiceType,
        existing_endpoints: List[ServiceEndpoint]
    ) -> bool:
        """
        Check for service conflicts.
        
        Args:
            workspace_id: Workspace ID
            service_type: Service type
            existing_endpoints: Existing endpoints
            
        Returns:
            True if conflict
        """
        for endpoint in existing_endpoints:
            if (endpoint.workspace_id == workspace_id and 
                endpoint.service_type == service_type):
                return True
        return False
    
    def validate_sld_content(self, sld_content: str) -> List[str]:
        """
        Validate SLD content.
        
        Args:
            sld_content: SLD XML content
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not sld_content or not sld_content.strip():
            issues.append("SLD content is empty")
            return issues
        
        # Check for basic XML structure
        if "<?xml" not in sld_content:
            issues.append("SLD content must be valid XML")
        
        if "<StyledLayerDescriptor" not in sld_content:
            issues.append("SLD must contain StyledLayerDescriptor element")
        
        return issues
    
    def validate_bounding_box(
        self,
        minx: float,
        miny: float,
        maxx: float,
        maxy: float
    ) -> List[str]:
        """
        Validate bounding box coordinates.
        
        Args:
            minx: Minimum X
            miny: Minimum Y
            maxx: Maximum X
            maxy: Maximum Y
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if minx >= maxx:
            issues.append("minx must be less than maxx")
        
        if miny >= maxy:
            issues.append("miny must be less than maxy")
        
        # Reasonable coordinate bounds (Earth)
        if minx < -180 or maxx > 180:
            issues.append("X coordinates must be within [-180, 180]")
        
        if miny < -90 or maxy > 90:
            issues.append("Y coordinates must be within [-90, 90]")
        
        return issues
    
    def validate_layer_group_consistency(
        self,
        layer_ids: List[str],
        available_layers: Dict[str, PublishedLayer]
    ) -> List[str]:
        """
        Validate layer group consistency.
        
        Args:
            layer_ids: Layer IDs in group
            available_layers: Available layers
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not layer_ids:
            issues.append("Layer group must contain at least one layer")
        
        for layer_id in layer_ids:
            if layer_id not in available_layers:
                issues.append(f"Layer '{layer_id}' does not exist")
        
        return issues
    
    def get_validation_summary(self) -> Dict:
        """
        Get validation summary.
        
        Returns:
            Summary dictionary
        """
        return {
            "issues": self.issues,
            "issue_count": len(self.issues),
            "has_critical": any("required" in i.lower() for i in self.issues),
        }
