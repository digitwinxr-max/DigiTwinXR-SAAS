"""
User and Security Types

Core data types for Identity and Access Management.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from enum import Enum


class UserStatus(str, Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class RoleType(str, Enum):
    """Role type."""
    SYSTEM = "system"
    ORGANIZATION = "organization"
    CUSTOM = "custom"


class MembershipRole(str, Enum):
    """Organization membership role."""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


@dataclass
class Organization:
    """
    Organization for multi-tenancy.
    """
    id: str
    name: str
    slug: str
    description: str = ""
    settings: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "settings": self.settings,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class User:
    """
    User account with Keycloak integration.
    """
    id: str
    email: str
    username: str
    first_name: str = ""
    last_name: str = ""
    full_name: str = ""
    status: UserStatus = UserStatus.ACTIVE
    is_superuser: bool = False
    
    # Keycloak integration
    external_id: Optional[str] = None  # Keycloak user ID
    keycloak_realm: Optional[str] = None
    keycloak_token: Optional[str] = None
    
    # Metadata
    last_login: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "status": self.status.value,
            "is_superuser": self.is_superuser,
            "external_id": self.external_id,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat(),
        }
    
    @property
    def is_active(self) -> bool:
        """Check if user is active."""
        return self.status == UserStatus.ACTIVE
    
    @property
    def display_name(self) -> str:
        """Get display name."""
        return self.full_name or self.username


@dataclass
class Permission:
    """
    Permission definition.
    """
    id: str
    code: str
    name: str
    description: str = ""
    resource: str = ""
    action: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "resource": self.resource,
            "action": self.action,
        }


@dataclass
class Role:
    """
    Role definition with optional inheritance.
    """
    id: str
    name: str
    description: str = ""
    role_type: RoleType = RoleType.CUSTOM
    organization_id: Optional[str] = None
    parent_role_id: Optional[str] = None
    is_system_role: bool = False
    inherits_permissions: bool = True
    
    # Computed
    permissions: Set[str] = field(default_factory=set)
    inherited_permissions: Set[str] = field(default_factory=set)
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "role_type": self.role_type.value,
            "organization_id": self.organization_id,
            "is_system_role": self.is_system_role,
            "permissions": list(self.permissions),
        }
    
    def has_permission(self, permission_code: str) -> bool:
        """Check if role has permission."""
        return (
            permission_code in self.permissions or
            permission_code in self.inherited_permissions
        )
    
    def get_all_permissions(self) -> Set[str]:
        """Get all permissions including inherited."""
        return self.permissions | self.inherited_permissions


@dataclass
class UserRole:
    """
    User to role assignment.
    """
    id: str
    user_id: str
    role_id: str
    organization_id: Optional[str] = None
    granted_by: Optional[str] = None
    granted_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "role_id": self.role_id,
            "organization_id": self.organization_id,
            "granted_by": self.granted_by,
            "granted_at": self.granted_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }
    
    @property
    def is_expired(self) -> bool:
        """Check if assignment is expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at


@dataclass
class RolePermission:
    """
    Role to permission assignment.
    """
    id: str
    role_id: str
    permission_id: str
    granted_by: Optional[str] = None
    granted_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "role_id": self.role_id,
            "permission_id": self.permission_id,
            "granted_by": self.granted_by,
            "granted_at": self.granted_at.isoformat(),
        }


@dataclass
class OrganizationMembership:
    """
    Organization membership.
    """
    id: str
    organization_id: str
    user_id: str
    membership_role: MembershipRole = MembershipRole.MEMBER
    invited_by: Optional[str] = None
    invited_at: datetime = field(default_factory=datetime.utcnow)
    joined_at: Optional[datetime] = None
    is_active: bool = True
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "user_id": self.user_id,
            "membership_role": self.membership_role.value,
            "invited_by": self.invited_by,
            "invited_at": self.invited_at.isoformat(),
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
            "is_active": self.is_active,
        }


@dataclass
class UserWithPermissions:
    """
    User with computed permissions.
    """
    user: User
    roles: List[Role] = field(default_factory=list)
    permissions: Set[str] = field(default_factory=set)
    organizations: List[Organization] = field(default_factory=list)
    
    def has_permission(self, permission_code: str) -> bool:
        """Check if user has permission."""
        if self.user.is_superuser:
            return True
        return permission_code in self.permissions
    
    def has_any_permission(self, *permission_codes: str) -> bool:
        """Check if user has any of the permissions."""
        if self.user.is_superuser:
            return True
        return any(code in self.permissions for code in permission_codes)
    
    def has_all_permissions(self, *permission_codes: str) -> bool:
        """Check if user has all of the permissions."""
        if self.user.is_superuser:
            return True
        return all(code in self.permissions for code in permission_codes)
    
    def to_dict(self) -> Dict:
        return {
            "user": self.user.to_dict(),
            "roles": [r.to_dict() for r in self.roles],
            "permissions": list(self.permissions),
            "organizations": [o.to_dict() for o in self.organizations],
        }


@dataclass
class SecurityContext:
    """
    Security context for request handling.
    """
    user: User
    organization_id: Optional[str] = None
    permissions: Set[str] = field(default_factory=set)
    is_authenticated: bool = True
    
    def has_permission(self, permission_code: str) -> bool:
        """Check permission."""
        if self.user.is_superuser:
            return True
        return permission_code in self.permissions
    
    def is_member_of(self, organization_id: str) -> bool:
        """Check organization membership."""
        return self.organization_id == organization_id
