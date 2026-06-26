"""
Workspace Manager

Manages GeoServer workspaces.
"""

import uuid
from typing import Dict, List, Optional
from datetime import datetime
from backend.src.integrations.geoserver.geoserver_client import GeoServerClient
from backend.src.integrations.geoserver.geoserver_types import Workspace
from backend.src.core.events import get_event_bus, EventType


class WorkspaceManager:
    """
    Manages GeoServer workspaces.
    
    Responsibilities:
    - Create workspaces
    - Delete workspaces
    - Update workspaces
    - List workspaces
    """
    
    def __init__(self, client: Optional[GeoServerClient] = None):
        self.client = client or GeoServerClient()
        self.event_bus = get_event_bus()
        
        # Local storage for workspace metadata
        self._workspaces: Dict[str, Workspace] = {}
    
    def close(self):
        """Close the client."""
        self.client.close()
    
    def create_workspace(
        self,
        name: str,
        uri: str,
        description: str = "",
        is_default: bool = False,
        is_isolated: bool = False,
        created_by: Optional[str] = None
    ) -> Workspace:
        """
        Create a new workspace.
        
        Args:
            name: Workspace name
            uri: Workspace URI
            description: Description
            is_default: Is default workspace
            is_isolated: Is isolated workspace
            created_by: User creating the workspace
            
        Returns:
            Created Workspace
        """
        workspace = Workspace(
            id=str(uuid.uuid4()),
            name=name,
            uri=uri,
            description=description,
            is_default=is_default,
            is_isolated=is_isolated,
            created_by=created_by
        )
        
        # Sync to GeoServer
        try:
            self.client.create_workspace(name, uri)
        except Exception:
            pass  # GeoServer may not be running
        
        # Store locally
        self._workspaces[workspace.id] = workspace
        
        # Publish event
        self.event_bus.publish(
            EventType.WORKSPACE_CREATED,
            source="workspace_manager",
            data={
                "workspace_id": workspace.id,
                "name": workspace.name,
                "uri": workspace.uri
            }
        )
        
        return workspace
    
    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """Get a workspace by ID."""
        return self._workspaces.get(workspace_id)
    
    def get_workspace_by_name(self, name: str) -> Optional[Workspace]:
        """Get a workspace by name."""
        for workspace in self._workspaces.values():
            if workspace.name == name:
                return workspace
        return None
    
    def get_workspaces(
        self,
        default_only: bool = False
    ) -> List[Workspace]:
        """Get all workspaces."""
        workspaces = list(self._workspaces.values())
        
        if default_only:
            workspaces = [w for w in workspaces if w.is_default]
        
        return workspaces
    
    def update_workspace(
        self,
        workspace: Workspace,
        **kwargs
    ) -> Workspace:
        """
        Update a workspace.
        
        Args:
            workspace: Workspace to update
            **kwargs: Fields to update
            
        Returns:
            Updated Workspace
        """
        for key, value in kwargs.items():
            if hasattr(workspace, key):
                setattr(workspace, key, value)
        
        workspace.updated_at = datetime.utcnow()
        return workspace
    
    def delete_workspace(
        self,
        workspace_id: str,
        recurse: bool = False
    ) -> bool:
        """
        Delete a workspace.
        
        Args:
            workspace_id: Workspace ID
            recurse: Delete contents recursively
            
        Returns:
            True if deleted
        """
        workspace = self._workspaces.get(workspace_id)
        if not workspace:
            return False
        
        # Delete from GeoServer
        try:
            self.client.delete_workspace(workspace.name, recurse)
        except Exception:
            pass
        
        # Remove locally
        del self._workspaces[workspace_id]
        return True
    
    def get_workspace_count(self) -> int:
        """Get total workspace count."""
        return len(self._workspaces)
    
    def get_default_workspace(self) -> Optional[Workspace]:
        """Get the default workspace."""
        for workspace in self._workspaces.values():
            if workspace.is_default:
                return workspace
        return None
    
    def set_default_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """Set a workspace as default."""
        workspace = self._workspaces.get(workspace_id)
        if not workspace:
            return None
        
        # Remove default from all others
        for w in self._workspaces.values():
            w.is_default = False
        
        workspace.is_default = True
        return workspace
