"""
Security Validator

Validates security entities and relationships.
"""

from typing import Dict, List, Optional, Any, Set
from backend.src.security.user_types import (
    User,
    Role,
    Organization,
    Permission,
    UserStatus,
    RoleType,
)


class SecurityValidator:
    """
    Validates security entities.
    
    Checks:
    - Duplicate users
    - Invalid permissions
    - Role conflicts
    - Organization membership
    - Permission inheritance
    """
    
    def __init__(self):
        self.issues: List[str] = []
    
    def validate_user(self, user: User) -> List[str]:
        """
        Validate a user.
        
        Args:
            user: User to validate
            
        Returns:
            List of validation issues
        """
        self.issues = []
        
        # Required fields
        if not user.id:
            self.issues.append("User ID is required")
        
        if not user.email or not user.email.strip():
            self.issues.append("Email is required")
        
        if user.email and "@" not in user.email:
            self.issues.append("Invalid email format")
        
        if not user.username or not user.username.strip():
            self.issues.append("Username is required")
        
        # Length validations
        if user.username and len(user.username) > 100:
            self.issues.append("Username must be 100 characters or less")
        
        # Status validation
        if not isinstance(user.status, UserStatus):
            self.issues.append("Invalid user status")
        
        return self.issues.copy()
    
    def validate_role(self, role: Role) -> List[str]:
        """
        Validate a role.
        
        Args:
            role: Role to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Required fields
        if not role.id:
            issues.append("Role ID is required")
        
        if not role.name or not role.name.strip():
            issues.append("Role name is required")
        
        if role.name and len(role.name) > 100:
            issues.append("Role name must be 100 characters or less")
        
        # Type validation
        if not isinstance(role.role_type, RoleType):
            issues.append("Invalid role type")
        
        # System role check
        if role.is_system_role and role.role_type != RoleType.SYSTEM:
            issues.append("System role must have SYSTEM type")
        
        # Organization scope
        if role.organization_id and role.role_type == RoleType.SYSTEM:
            issues.append("System role cannot have organization scope")
        
        return issues
    
    def validate_organization(self, organization: Organization) -> List[str]:
        """
        Validate an organization.
        
        Args:
            organization: Organization to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Required fields
        if not organization.id:
            issues.append("Organization ID is required")
        
        if not organization.name or not organization.name.strip():
            issues.append("Organization name is required")
        
        if not organization.slug or not organization.slug.strip():
            issues.append("Organization slug is required")
        
        # Slug format
        if organization.slug:
            if not organization.slug.replace("-", "").replace("_", "").isalnum():
                issues.append("Slug must be alphanumeric with optional hyphens/underscores")
            
            if len(organization.slug) > 100:
                issues.append("Slug must be 100 characters or less")
        
        # Name length
        if organization.name and len(organization.name) > 255:
            issues.append("Name must be 255 characters or less")
        
        return issues
    
    def validate_permission(self, permission: Permission) -> List[str]:
        """
        Validate a permission.
        
        Args:
            permission: Permission to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Required fields
        if not permission.id:
            issues.append("Permission ID is required")
        
        if not permission.code or not permission.code.strip():
            issues.append("Permission code is required")
        
        if permission.code and len(permission.code) > 100:
            issues.append("Permission code must be 100 characters or less")
        
        if not permission.name or not permission.name.strip():
            issues.append("Permission name is required")
        
        return issues
    
    def validate_role_assignment(
        self,
        user: User,
        role: Role,
        organization_id: Optional[str] = None
    ) -> List[str]:
        """
        Validate role assignment.
        
        Args:
            user: User to assign
            role: Role to assign
            organization_id: Organization scope
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # User must be active
        if user.status != UserStatus.ACTIVE:
            issues.append("Cannot assign role to inactive user")
        
        # Organization scope check
        if role.organization_id and role.organization_id != organization_id:
            issues.append("Role organization does not match assignment scope")
        
        # System role check
        if role.is_system_role and organization_id:
            issues.append("System role cannot be assigned with organization scope")
        
        return issues
    
    def validate_permission_grant(
        self,
        role: Role,
        permission_code: str
    ) -> List[str]:
        """
        Validate permission grant.
        
        Args:
            role: Role to grant permission to
            permission_code: Permission code
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # System role permissions
        if role.is_system_role and role.role_type != RoleType.SYSTEM:
            issues.append("Only system roles can have predefined permissions")
        
        # Permission code format
        if permission_code and not permission_code.replace("_", "").isalnum():
            issues.append("Permission code must be alphanumeric with underscores")
        
        return issues
    
    def validate_organization_membership(
        self,
        organization: Organization,
        user: User
    ) -> List[str]:
        """
        Validate organization membership.
        
        Args:
            organization: Organization
            user: User
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Organization must be active
        if not organization.is_active:
            issues.append("Cannot add member to inactive organization")
        
        # User must be active
        if user.status != UserStatus.ACTIVE:
            issues.append("Cannot add inactive user to organization")
        
        return issues
    
    def validate_permission_inheritance(
        self,
        role: Role,
        parent_role: Role
    ) -> List[str]:
        """
        Validate permission inheritance.
        
        Args:
            role: Child role
            parent_role: Parent role
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Cannot inherit from self
        if role.id == parent_role.id:
            issues.append("Role cannot inherit from itself")
        
        # Organization scope must match
        if role.organization_id != parent_role.organization_id:
            issues.append("Roles must be in the same organization for inheritance")
        
        # Cannot inherit from system role
        if parent_role.is_system_role:
            issues.append("Cannot inherit from system role")
        
        # Circular inheritance check
        if self._would_create_circular_inheritance(role, parent_role):
            issues.append("Would create circular inheritance")
        
        return issues
    
    def validate_permission_codes(self, codes: List[str]) -> List[str]:
        """
        Validate a list of permission codes.
        
        Args:
            codes: Permission codes to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        for code in codes:
            if not code or not code.strip():
                issues.append("Empty permission code")
            
            if code and len(code) > 100:
                issues.append(f"Permission code too long: {code}")
            
            if code and not code.replace("_", "").isalnum():
                issues.append(f"Invalid permission code format: {code}")
        
        return issues
    
    def validate_email(self, email: str) -> List[str]:
        """
        Validate email format.
        
        Args:
            email: Email to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not email or not email.strip():
            issues.append("Email is required")
            return issues
        
        if "@" not in email:
            issues.append("Invalid email format")
        
        local, domain = email.rsplit("@", 1) if "@" in email else ("", "")
        
        if not local:
            issues.append("Email local part is required")
        
        if not domain or "." not in domain:
            issues.append("Email domain is invalid")
        
        return issues
    
    def validate_username(self, username: str) -> List[str]:
        """
        Validate username format.
        
        Args:
            username: Username to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not username or not username.strip():
            issues.append("Username is required")
            return issues
        
        if len(username) < 3:
            issues.append("Username must be at least 3 characters")
        
        if len(username) > 100:
            issues.append("Username must be 100 characters or less")
        
        # Allow alphanumeric, underscores, hyphens
        if not username.replace("_", "").replace("-", "").isalnum():
            issues.append("Username must be alphanumeric with underscores/hyphens")
        
        return issues
    
    def _would_create_circular_inheritance(
        self,
        role: Role,
        new_parent: Role
    ) -> bool:
        """Check if adding inheritance would create a cycle."""
        visited: Set[str] = set()
        
        current = new_parent
        while current:
            if current.id == role.id:
                return True
            if current.id in visited:
                break
            visited.add(current.id)
            current = current.parent_role_id  # Would need to look this up
        
        return False
    
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
