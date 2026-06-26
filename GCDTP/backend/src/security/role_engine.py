"""
Role Engine

Manages roles, role assignments, and permission inheritance.
"""

import uuid
from typing import Dict, List, Optional, Set, Any
from datetime import datetime
from backend.src.security.user_types import (
    Role,
    RoleType,
    Permission,
    UserRole,
    User,
)
from backend.src.security.security_validator import SecurityValidator
from backend.src.core.events import get_event_bus, EventType


class RoleEngine:
    """
    Engine for role-based access control.
    
    Responsibilities:
    - Create/update/delete roles
    - Assign roles to users
    - Manage role permissions
    - Handle permission inheritance
    """
    
    def __init__(self):
        self.validator = SecurityValidator()
        self.event_bus = get_event_bus()
        self._roles: Dict[str, Role] = {}
        self._role_permissions: Dict[str, Set[str]] = {}  # role_id -> permission_codes
        self._user_roles: Dict[str, List[UserRole]] = {}  # user_id -> roles
    
    def create_role(
        self,
        name: str,
        description: str = "",
        role_type: RoleType = RoleType.CUSTOM,
        organization_id: Optional[str] = None,
        parent_role_id: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        is_system_role: bool = False
    ) -> Role:
        """
        Create a new role.
        
        Args:
            name: Role name
            description: Role description
            role_type: Type of role
            organization_id: Organization scope
            parent_role_id: Parent role for inheritance
            permissions: Initial permissions
            is_system_role: Is a system role
            
        Returns:
            Created Role
        """
        role = Role(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            role_type=role_type,
            organization_id=organization_id,
            parent_role_id=parent_role_id,
            is_system_role=is_system_role,
            permissions=set(permissions or [])
        )
        
        # Validate
        issues = self.validator.validate_role(role)
        if issues:
            raise ValueError(f"Validation failed: {', '.join(issues)}")
        
        # Store
        self._roles[role.id] = role
        self._role_permissions[role.id] = role.permissions.copy()
        
        # Handle inheritance
        if parent_role_id:
            self._setup_inheritance(role)
        
        return role
    
    def get_role(self, role_id: str) -> Optional[Role]:
        """Get role by ID."""
        return self._roles.get(role_id)
    
    def get_role_by_name(self, name: str, organization_id: Optional[str] = None) -> Optional[Role]:
        """Get role by name."""
        for role in self._roles.values():
            if role.name == name and role.organization_id == organization_id:
                return role
        return None
    
    def update_role(
        self,
        role: Role,
        **kwargs
    ) -> Role:
        """
        Update a role.
        
        Args:
            role: Role to update
            **kwargs: Fields to update
            
        Returns:
            Updated Role
        """
        for key, value in kwargs.items():
            if hasattr(role, key) and key not in ["id", "permissions"]:
                setattr(role, key, value)
        
        role.updated_at = datetime.utcnow()
        
        # Validate
        issues = self.validator.validate_role(role)
        if issues:
            raise ValueError(f"Validation failed: {', '.join(issues)}")
        
        return role
    
    def delete_role(self, role_id: str) -> bool:
        """
        Delete a role.
        
        Args:
            role_id: Role to delete
            
        Returns:
            True if deleted
        """
        role = self._roles.get(role_id)
        if not role:
            return False
        
        if role.is_system_role:
            raise ValueError("Cannot delete system role")
        
        del self._roles[role_id]
        if role_id in self._role_permissions:
            del self._role_permissions[role_id]
        
        return True
    
    def assign_role_to_user(
        self,
        user: User,
        role: Role,
        organization_id: Optional[str] = None,
        granted_by: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> UserRole:
        """
        Assign a role to a user.
        
        Args:
            user: User to assign
            role: Role to assign
            organization_id: Organization scope
            granted_by: User granting the role
            expires_at: Expiration time
            
        Returns:
            Created UserRole
        """
        # Check for existing assignment
        if user.id in self._user_roles:
            for ur in self._user_roles[user.id]:
                if ur.role_id == role.id and ur.organization_id == organization_id:
                    raise ValueError("User already has this role")
        
        user_role = UserRole(
            id=str(uuid.uuid4()),
            user_id=user.id,
            role_id=role.id,
            organization_id=organization_id,
            granted_by=granted_by,
            expires_at=expires_at
        )
        
        # Store
        if user.id not in self._user_roles:
            self._user_roles[user.id] = []
        self._user_roles[user.id].append(user_role)
        
        # Publish event
        self.event_bus.publish(
            EventType.ROLE_ASSIGNED,
            source="role_engine",
            data={
                "user_id": user.id,
                "role_id": role.id,
                "role_name": role.name,
                "organization_id": organization_id,
                "granted_by": granted_by,
            }
        )
        
        return user_role
    
    def remove_role_from_user(
        self,
        user_id: str,
        role_id: str,
        organization_id: Optional[str] = None
    ) -> bool:
        """
        Remove a role from a user.
        
        Args:
            user_id: User ID
            role_id: Role ID
            organization_id: Organization scope
            
        Returns:
            True if removed
        """
        if user_id not in self._user_roles:
            return False
        
        user_roles = self._user_roles[user_id]
        for i, ur in enumerate(user_roles):
            if ur.role_id == role_id and ur.organization_id == organization_id:
                user_roles.pop(i)
                
                # Publish event
                role = self.get_role(role_id)
                self.event_bus.publish(
                    EventType.ROLE_REMOVED,
                    source="role_engine",
                    data={
                        "user_id": user_id,
                        "role_id": role_id,
                        "role_name": role.name if role else None,
                        "organization_id": organization_id,
                    }
                )
                return True
        
        return False
    
    def get_user_roles(self, user_id: str) -> List[UserRole]:
        """Get all roles for a user."""
        return self._user_roles.get(user_id, [])
    
    def get_user_permissions(self, user_id: str) -> Set[str]:
        """
        Get all permissions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Set of permission codes
        """
        permissions: Set[str] = set()
        
        for user_role in self.get_user_roles(user_id):
            if user_role.is_expired:
                continue
            
            role = self.get_role(user_role.role_id)
            if not role:
                continue
            
            # Get direct permissions
            permissions.update(self._role_permissions.get(role.id, set()))
            
            # Get inherited permissions
            if role.inherits_permissions and role.parent_role_id:
                parent = self.get_role(role.parent_role_id)
                if parent:
                    permissions.update(self._role_permissions.get(parent.id, set()))
        
        return permissions
    
    def grant_permission(
        self,
        role: Role,
        permission_code: str,
        granted_by: Optional[str] = None
    ) -> Role:
        """
        Grant a permission to a role.
        
        Args:
            role: Role to grant permission to
            permission_code: Permission code
            granted_by: User granting
            
        Returns:
            Updated Role
        """
        # Add permission
        if role.id not in self._role_permissions:
            self._role_permissions[role.id] = set()
        
        self._role_permissions[role.id].add(permission_code)
        role.permissions.add(permission_code)
        
        # Publish event
        self.event_bus.publish(
            EventType.PERMISSION_GRANTED,
            source="role_engine",
            data={
                "role_id": role.id,
                "role_name": role.name,
                "permission_code": permission_code,
                "granted_by": granted_by,
            }
        )
        
        return role
    
    def revoke_permission(
        self,
        role: Role,
        permission_code: str
    ) -> Role:
        """
        Revoke a permission from a role.
        
        Args:
            role: Role to revoke permission from
            permission_code: Permission code
            
        Returns:
            Updated Role
        """
        # Remove permission
        if role.id in self._role_permissions:
            self._role_permissions[role.id].discard(permission_code)
        role.permissions.discard(permission_code)
        
        # Publish event
        self.event_bus.publish(
            EventType.PERMISSION_REVOKED,
            source="role_engine",
            data={
                "role_id": role.id,
                "role_name": role.name,
                "permission_code": permission_code,
            }
        )
        
        return role
    
    def get_role_permissions(self, role_id: str) -> Set[str]:
        """Get all permissions for a role."""
        return self._role_permissions.get(role_id, set()).copy()
    
    def _setup_inheritance(self, role: Role) -> None:
        """Setup permission inheritance from parent role."""
        if not role.parent_role_id:
            return
        
        parent = self.get_role(role.parent_role_id)
        if not parent:
            return
        
        # Copy inherited permissions
        if parent.inherits_permissions:
            role.inherited_permissions = self._role_permissions.get(parent.id, set()).copy()
    
    def check_permission(self, user_id: str, permission_code: str) -> bool:
        """
        Check if user has a permission.
        
        Args:
            user_id: User ID
            permission_code: Permission code
            
        Returns:
            True if user has permission
        """
        return permission_code in self.get_user_permissions(user_id)
    
    def list_roles(self, organization_id: Optional[str] = None) -> List[Role]:
        """List all roles."""
        if organization_id:
            return [r for r in self._roles.values() if r.organization_id == organization_id]
        return list(self._roles.values())


class PermissionEngine:
    """
    Engine for permission management.
    """
    
    def __init__(self):
        self._permissions: Dict[str, Permission] = {}
    
    def create_permission(
        self,
        code: str,
        name: str,
        description: str = "",
        resource: str = "",
        action: str = ""
    ) -> Permission:
        """Create a permission."""
        permission = Permission(
            id=str(uuid.uuid4()),
            code=code,
            name=name,
            description=description,
            resource=resource,
            action=action
        )
        
        self._permissions[code] = permission
        return permission
    
    def get_permission(self, code: str) -> Optional[Permission]:
        """Get permission by code."""
        return self._permissions.get(code)
    
    def get_all_permissions(self) -> List[Permission]:
        """Get all permissions."""
        return list(self._permissions.values())
    
    def get_permissions_by_resource(self, resource: str) -> List[Permission]:
        """Get permissions for a resource."""
        return [p for p in self._permissions.values() if p.resource == resource]
