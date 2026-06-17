"""
Keycloak Adapter

Adapter for Keycloak integration.
FastAPI remains authoritative for business logic.
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from backend.src.security.user_types import (
    User,
    UserStatus,
    Role,
    Organization,
)


class KeycloakAdapter:
    """
    Adapter for Keycloak integration.
    
    Responsibilities:
    - Realm mapping
    - User synchronization
    - Token validation
    - Role mapping
    - Organization mapping
    
    Note: All business logic remains in FastAPI services.
    Keycloak is used only for authentication and user data.
    """
    
    def __init__(self, realm_url: str = "", realm_name: str = "master"):
        self.realm_url = realm_url
        self.realm_name = realm_name
        self._users: Dict[str, Dict] = {}  # external_id -> Keycloak user data
    
    # =========================================================================
    # User Synchronization
    # =========================================================================
    
    def sync_user(self, keycloak_user: Dict) -> User:
        """
        Synchronize user from Keycloak to local model.
        
        Args:
            keycloak_user: Keycloak user data
            
        Returns:
            Synchronized User
        """
        external_id = keycloak_user.get("id")
        
        user = User(
            id=str(uuid.uuid4()),
            external_id=external_id,
            email=keycloak_user.get("email", ""),
            username=keycloak_user.get("username", ""),
            first_name=keycloak_user.get("firstName", ""),
            last_name=keycloak_user.get("lastName", ""),
            full_name=keycloak_user.get("firstName", "") + " " + keycloak_user.get("lastName", ""),
            status=self._map_keycloak_status(keycloak_user.get("enabled", True)),
            keycloak_realm=self.realm_name
        )
        
        # Store Keycloak data
        self._users[external_id] = keycloak_user
        
        return user
    
    def update_from_keycloak(self, user: User, keycloak_user: Dict) -> User:
        """
        Update user from Keycloak data.
        
        Args:
            user: Current user
            keycloak_user: Keycloak user data
            
        Returns:
            Updated User
        """
        user.email = keycloak_user.get("email", user.email)
        user.username = keycloak_user.get("username", user.username)
        user.first_name = keycloak_user.get("firstName", user.first_name)
        user.last_name = keycloak_user.get("lastName", user.last_name)
        user.full_name = f"{keycloak_user.get('firstName', '')} {keycloak_user.get('lastName', '')}".strip()
        user.status = self._map_keycloak_status(keycloak_user.get("enabled", True))
        user.updated_at = datetime.utcnow()
        
        return user
    
    def get_keycloak_user(self, external_id: str) -> Optional[Dict]:
        """Get Keycloak user data."""
        return self._users.get(external_id)
    
    # =========================================================================
    # Token Validation
    # =========================================================================
    
    def validate_token(self, token: str) -> Optional[Dict]:
        """
        Validate a Keycloak token.
        
        Args:
            token: JWT token
            
        Returns:
            Token claims if valid, None otherwise
            
        Note: In production, this would call Keycloak's token validation endpoint.
        For now, returns a placeholder structure.
        """
        # In production:
        # 1. Verify JWT signature with Keycloak's public key
        # 2. Check token expiration
        # 3. Check realm
        # 4. Return token claims
        
        return {
            "active": True,
            "sub": "user-external-id",
            "realm": self.realm_name,
            "type": "Bearer",
        }
    
    def extract_user_from_token(self, token: str) -> Optional[str]:
        """
        Extract user ID from token.
        
        Args:
            token: JWT token
            
        Returns:
            External user ID
        """
        claims = self.validate_token(token)
        if claims and claims.get("active"):
            return claims.get("sub")
        return None
    
    # =========================================================================
    # Role Mapping
    # =========================================================================
    
    def map_keycloak_roles_to_local(self, keycloak_roles: List[str]) -> List[str]:
        """
        Map Keycloak roles to local role names.
        
        Args:
            keycloak_roles: Keycloak role names
            
        Returns:
            Local role names
        """
        # Keycloak role -> Local role mapping
        mapping = {
            "admin": "OrganizationAdmin",
            "operator": "Operator",
            "inspector": "Inspector",
            "technician": "Technician",
            "viewer": "Viewer",
            "super-admin": "SuperAdmin",
        }
        
        return [
            mapping.get(role, role)
            for role in keycloak_roles
        ]
    
    def map_local_role_to_keycloak(self, local_role: str) -> Optional[str]:
        """
        Map local role to Keycloak role.
        
        Args:
            local_role: Local role name
            
        Returns:
            Keycloak role name
        """
        mapping = {
            "OrganizationAdmin": "admin",
            "Operator": "operator",
            "Inspector": "inspector",
            "Technician": "technician",
            "Viewer": "viewer",
            "SuperAdmin": "super-admin",
        }
        
        return mapping.get(local_role)
    
    # =========================================================================
    # Organization Mapping
    # =========================================================================
    
    def get_user_organizations(self, keycloak_user: Dict) -> List[str]:
        """
        Get organization IDs from Keycloak user.
        
        Args:
            keycloak_user: Keycloak user data
            
        Returns:
            List of organization IDs
        """
        # Keycloak stores realm and client roles
        # Organization membership could be stored as client roles
        # or in user attributes
        
        organizations = []
        
        # Check user attributes
        attributes = keycloak_user.get("attributes", {})
        if "organizations" in attributes:
            organizations.extend(attributes["organizations"])
        
        return organizations
    
    def map_organization(self, keycloak_realm: str, org_data: Dict) -> Organization:
        """
        Map Keycloak realm/client to organization.
        
        Args:
            keycloak_realm: Keycloak realm name
            org_data: Organization data
            
        Returns:
            Organization
        """
        return Organization(
            id=str(uuid.uuid4()),
            name=org_data.get("name", keycloak_realm),
            slug=org_data.get("slug", keycloak_realm.lower()),
            description=org_data.get("description", ""),
            metadata={
                "keycloak_realm": keycloak_realm,
                "keycloak_client": org_data.get("client_id"),
            }
        )
    
    # =========================================================================
    # Session Information
    # =========================================================================
    
    def get_session_info(self, token: str) -> Optional[Dict]:
        """
        Get session information from token.
        
        Args:
            token: JWT token
            
        Returns:
            Session information
        """
        claims = self.validate_token(token)
        if not claims:
            return None
        
        return {
            "user_id": claims.get("sub"),
            "realm": claims.get("realm", self.realm_name),
            "type": claims.get("type", "Bearer"),
            "session_state": claims.get("session_state"),
            "scope": claims.get("scope", ""),
        }
    
    def is_session_active(self, token: str) -> bool:
        """Check if session is active."""
        claims = self.validate_token(token)
        return claims is not None and claims.get("active", False)
    
    # =========================================================================
    # User Lookup
    # =========================================================================
    
    def find_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Find user by email in Keycloak.
        
        Args:
            email: User email
            
        Returns:
            Keycloak user data
        """
        for user_data in self._users.values():
            if user_data.get("email") == email:
                return user_data
        return None
    
    def find_user_by_username(self, username: str) -> Optional[Dict]:
        """
        Find user by username in Keycloak.
        
        Args:
            username: Username
            
        Returns:
            Keycloak user data
        """
        for user_data in self._users.values():
            if user_data.get("username") == username:
                return user_data
        return None
    
    # =========================================================================
    # Helper Methods
    # =========================================================================
    
    def _map_keycloak_status(self, enabled: bool) -> UserStatus:
        """Map Keycloak enabled status to UserStatus."""
        return UserStatus.ACTIVE if enabled else UserStatus.INACTIVE
    
    def create_keycloak_user_data(
        self,
        email: str,
        username: str,
        first_name: str = "",
        last_name: str = "",
        enabled: bool = True
    ) -> Dict:
        """
        Create Keycloak user data structure.
        
        Args:
            email: User email
            username: Username
            first_name: First name
            last_name: Last name
            enabled: Is enabled
            
        Returns:
            Keycloak user data dict
        """
        return {
            "id": str(uuid.uuid4()),
            "email": email,
            "username": username,
            "firstName": first_name,
            "lastName": last_name,
            "enabled": enabled,
            "emailVerified": False,
            "createdTimestamp": datetime.utcnow().isoformat(),
            "attributes": {},
        }
