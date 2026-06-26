"""
Organization Engine

Manages organizations and membership.
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from backend.src.security.user_types import (
    Organization,
    OrganizationMembership,
    MembershipRole,
    User,
)
from backend.src.security.security_validator import SecurityValidator
from backend.src.core.events import get_event_bus, EventType


class OrganizationEngine:
    """
    Engine for organization management.
    
    Responsibilities:
    - Create/update/delete organizations
    - Manage membership
    - Handle role assignments within organizations
    """
    
    def __init__(self):
        self.validator = SecurityValidator()
        self.event_bus = get_event_bus()
        self._organizations: Dict[str, Organization] = {}
        self._memberships: Dict[str, List[OrganizationMembership]] = {}  # org_id -> members
        self._user_memberships: Dict[str, List[OrganizationMembership]] = {}  # user_id -> memberships
    
    def create_organization(
        self,
        name: str,
        slug: str,
        description: str = "",
        settings: Optional[Dict] = None,
        owner_id: Optional[str] = None
    ) -> Organization:
        """
        Create a new organization.
        
        Args:
            name: Organization name
            slug: URL-friendly slug
            description: Description
            settings: Organization settings
            owner_id: Owner user ID
            
        Returns:
            Created Organization
        """
        organization = Organization(
            id=str(uuid.uuid4()),
            name=name,
            slug=slug,
            description=description,
            settings=settings or {},
            metadata={"owner_id": owner_id} if owner_id else {}
        )
        
        # Validate
        issues = self.validator.validate_organization(organization)
        if issues:
            raise ValueError(f"Validation failed: {', '.join(issues)}")
        
        # Store
        self._organizations[organization.id] = organization
        
        # Publish event
        self.event_bus.publish(
            EventType.ORGANIZATION_CREATED,
            source="organization_engine",
            data={
                "organization_id": organization.id,
                "name": organization.name,
                "slug": organization.slug,
            }
        )
        
        return organization
    
    def get_organization(self, organization_id: str) -> Optional[Organization]:
        """Get organization by ID."""
        return self._organizations.get(organization_id)
    
    def get_organization_by_slug(self, slug: str) -> Optional[Organization]:
        """Get organization by slug."""
        for org in self._organizations.values():
            if org.slug == slug:
                return org
        return None
    
    def update_organization(
        self,
        organization: Organization,
        **kwargs
    ) -> Organization:
        """
        Update an organization.
        
        Args:
            organization: Organization to update
            **kwargs: Fields to update
            
        Returns:
            Updated Organization
        """
        for key, value in kwargs.items():
            if hasattr(organization, key):
                setattr(organization, key, value)
        
        organization.updated_at = datetime.utcnow()
        
        # Validate
        issues = self.validator.validate_organization(organization)
        if issues:
            raise ValueError(f"Validation failed: {', '.join(issues)}")
        
        # Publish event
        self.event_bus.publish(
            EventType.ORGANIZATION_UPDATED,
            source="organization_engine",
            data={
                "organization_id": organization.id,
                "name": organization.name,
                "updated_fields": list(kwargs.keys()),
            }
        )
        
        return organization
    
    def delete_organization(self, organization_id: str) -> bool:
        """
        Delete an organization.
        
        Args:
            organization_id: Organization to delete
            
        Returns:
            True if deleted
        """
        if organization_id not in self._organizations:
            return False
        
        del self._organizations[organization_id]
        
        # Clean up memberships
        if organization_id in self._memberships:
            del self._memberships[organization_id]
        
        return True
    
    def add_member(
        self,
        organization: Organization,
        user: User,
        membership_role: MembershipRole = MembershipRole.MEMBER,
        invited_by: Optional[str] = None
    ) -> OrganizationMembership:
        """
        Add a member to an organization.
        
        Args:
            organization: Target organization
            user: User to add
            membership_role: Membership role
            invited_by: User who invited
            
        Returns:
            Created Membership
        """
        # Check for existing membership
        if organization.id in self._memberships:
            for m in self._memberships[organization.id]:
                if m.user_id == user.id:
                    raise ValueError("User is already a member")
        
        membership = OrganizationMembership(
            id=str(uuid.uuid4()),
            organization_id=organization.id,
            user_id=user.id,
            membership_role=membership_role,
            invited_by=invited_by,
            joined_at=datetime.utcnow()
        )
        
        # Store
        if organization.id not in self._memberships:
            self._memberships[organization.id] = []
        self._memberships[organization.id].append(membership)
        
        if user.id not in self._user_memberships:
            self._user_memberships[user.id] = []
        self._user_memberships[user.id].append(membership)
        
        # Publish event
        self.event_bus.publish(
            EventType.ORGANIZATION_MEMBER_ADDED,
            source="organization_engine",
            data={
                "organization_id": organization.id,
                "user_id": user.id,
                "membership_role": membership_role.value,
                "invited_by": invited_by,
            }
        )
        
        return membership
    
    def remove_member(
        self,
        organization_id: str,
        user_id: str
    ) -> bool:
        """
        Remove a member from an organization.
        
        Args:
            organization_id: Organization ID
            user_id: User ID
            
        Returns:
            True if removed
        """
        if organization_id not in self._memberships:
            return False
        
        memberships = self._memberships[organization_id]
        for i, m in enumerate(memberships):
            if m.user_id == user_id:
                memberships.pop(i)
                
                # Remove from user memberships
                if user_id in self._user_memberships:
                    for j, um in enumerate(self._user_memberships[user_id]):
                        if um.organization_id == organization_id:
                            self._user_memberships[user_id].pop(j)
                            break
                
                # Publish event
                self.event_bus.publish(
                    EventType.ORGANIZATION_MEMBER_REMOVED,
                    source="organization_engine",
                    data={
                        "organization_id": organization_id,
                        "user_id": user_id,
                    }
                )
                return True
        
        return False
    
    def update_member_role(
        self,
        organization_id: str,
        user_id: str,
        new_role: MembershipRole
    ) -> OrganizationMembership:
        """
        Update a member's role.
        
        Args:
            organization_id: Organization ID
            user_id: User ID
            new_role: New membership role
            
        Returns:
            Updated Membership
        """
        if organization_id not in self._memberships:
            raise ValueError("Organization not found")
        
        for membership in self._memberships[organization_id]:
            if membership.user_id == user_id:
                membership.membership_role = new_role
                
                # Publish event
                self.event_bus.publish(
                    EventType.ORGANIZATION_MEMBER_ROLE_CHANGED,
                    source="organization_engine",
                    data={
                        "organization_id": organization_id,
                        "user_id": user_id,
                        "new_role": new_role.value,
                    }
                )
                return membership
        
        raise ValueError("Member not found")
    
    def get_members(self, organization_id: str) -> List[OrganizationMembership]:
        """Get all members of an organization."""
        return self._memberships.get(organization_id, [])
    
    def get_user_organizations(self, user_id: str) -> List[OrganizationMembership]:
        """Get all organizations a user is a member of."""
        return self._user_memberships.get(user_id, [])
    
    def is_member(self, organization_id: str, user_id: str) -> bool:
        """Check if user is a member of organization."""
        memberships = self._memberships.get(organization_id, [])
        for m in memberships:
            if m.user_id == user_id and m.is_active:
                return True
        return False
    
    def get_member_role(self, organization_id: str, user_id: str) -> Optional[MembershipRole]:
        """Get user's membership role in organization."""
        memberships = self._memberships.get(organization_id, [])
        for m in memberships:
            if m.user_id == user_id and m.is_active:
                return m.membership_role
        return None
    
    def list_organizations(self) -> List[Organization]:
        """List all organizations."""
        return list(self._organizations.values())
    
    def activate_organization(self, organization: Organization) -> Organization:
        """Activate an organization."""
        organization.is_active = True
        organization.updated_at = datetime.utcnow()
        return organization
    
    def deactivate_organization(self, organization: Organization) -> Organization:
        """Deactivate an organization."""
        organization.is_active = False
        organization.updated_at = datetime.utcnow()
        return organization
