"""
Tests for Identity and Access Management

Tests organizations, users, roles, permissions,
RBAC, organization isolation, and Keycloak adapter.
"""

import pytest
from datetime import datetime, timedelta
from backend.src.security import (
    RoleEngine,
    OrganizationEngine,
    KeycloakAdapter,
    SecurityValidator,
    User,
    Role,
    Organization,
    Permission,
    UserStatus,
    RoleType,
    MembershipRole,
)


class TestSecurityTypes:
    """Tests for security types."""
    
    def test_create_user(self):
        """Test creating a user."""
        user = User(
            id="user-1",
            email="test@example.com",
            username="testuser"
        )
        
        assert user.id == "user-1"
        assert user.email == "test@example.com"
        assert user.status == UserStatus.ACTIVE
    
    def test_user_is_active(self):
        """Test user active check."""
        user = User(
            id="user-1",
            email="test@example.com",
            username="testuser",
            status=UserStatus.ACTIVE
        )
        
        assert user.is_active is True
    
    def test_user_display_name(self):
        """Test user display name."""
        user = User(
            id="user-1",
            email="test@example.com",
            username="testuser",
            full_name="Test User"
        )
        
        assert user.display_name == "Test User"
    
    def test_create_role(self):
        """Test creating a role."""
        role = Role(
            id="role-1",
            name="Operator",
            description="Operational access"
        )
        
        assert role.name == "Operator"
        assert role.is_system_role is False
    
    def test_role_has_permission(self):
        """Test role permission check."""
        role = Role(
            id="role-1",
            name="Test",
            permissions={"CREATE_ASSET", "VIEW_ASSET"}
        )
        
        assert role.has_permission("CREATE_ASSET") is True
        assert role.has_permission("DELETE_ASSET") is False
    
    def test_role_inherited_permissions(self):
        """Test inherited permissions."""
        role = Role(
            id="role-1",
            name="Test",
            permissions={"CREATE_ASSET"},
            inherited_permissions={"VIEW_ASSET"}
        )
        
        assert role.has_permission("VIEW_ASSET") is True
    
    def test_create_organization(self):
        """Test creating an organization."""
        org = Organization(
            id="org-1",
            name="Test Org",
            slug="test-org"
        )
        
        assert org.name == "Test Org"
        assert org.slug == "test-org"
        assert org.is_active is True


class TestRoleEngine:
    """Tests for role engine."""
    
    @pytest.fixture
    def engine(self):
        """Create role engine."""
        return RoleEngine()
    
    @pytest.fixture
    def sample_user(self):
        """Create sample user."""
        return User(
            id="user-1",
            email="test@example.com",
            username="testuser"
        )
    
    def test_create_role(self, engine):
        """Test creating a role."""
        role = engine.create_role(
            name="Operator",
            description="Operational access",
            permissions=["CREATE_ASSET", "VIEW_ASSET"]
        )
        
        assert role is not None
        assert role.id is not None
        assert role.name == "Operator"
    
    def test_create_system_role(self, engine):
        """Test creating a system role."""
        role = engine.create_role(
            name="SuperAdmin",
            description="Full access",
            role_type=RoleType.SYSTEM,
            is_system_role=True
        )
        
        assert role.is_system_role is True
        assert role.role_type == RoleType.SYSTEM
    
    def test_get_role(self, engine):
        """Test getting a role."""
        role = engine.create_role(name="TestRole")
        
        retrieved = engine.get_role(role.id)
        
        assert retrieved is not None
        assert retrieved.name == "TestRole"
    
    def test_update_role(self, engine):
        """Test updating a role."""
        role = engine.create_role(name="Original")
        
        updated = engine.update_role(role, name="Updated")
        
        assert updated.name == "Updated"
    
    def test_delete_role(self, engine):
        """Test deleting a role."""
        role = engine.create_role(name="ToDelete")
        role_id = role.id
        
        result = engine.delete_role(role_id)
        
        assert result is True
        assert engine.get_role(role_id) is None
    
    def test_cannot_delete_system_role(self, engine):
        """Test cannot delete system role."""
        role = engine.create_role(
            name="SystemRole",
            is_system_role=True
        )
        
        with pytest.raises(ValueError):
            engine.delete_role(role.id)
    
    def test_assign_role_to_user(self, engine, sample_user):
        """Test assigning role to user."""
        role = engine.create_role(name="Operator")
        
        user_role = engine.assign_role_to_user(sample_user, role)
        
        assert user_role is not None
        assert user_role.role_id == role.id
    
    def test_remove_role_from_user(self, engine, sample_user):
        """Test removing role from user."""
        role = engine.create_role(name="Operator")
        engine.assign_role_to_user(sample_user, role)
        
        result = engine.remove_role_from_user(sample_user.id, role.id)
        
        assert result is True
    
    def test_get_user_permissions(self, engine, sample_user):
        """Test getting user permissions."""
        role = engine.create_role(
            name="Operator",
            permissions=["CREATE_ASSET", "VIEW_ASSET"]
        )
        engine.assign_role_to_user(sample_user, role)
        
        permissions = engine.get_user_permissions(sample_user.id)
        
        assert "CREATE_ASSET" in permissions
        assert "VIEW_ASSET" in permissions
    
    def test_grant_permission(self, engine):
        """Test granting permission."""
        role = engine.create_role(name="TestRole")
        
        updated = engine.grant_permission(role, "DELETE_ASSET")
        
        assert "DELETE_ASSET" in updated.permissions
    
    def test_revoke_permission(self, engine):
        """Test revoking permission."""
        role = engine.create_role(
            name="TestRole",
            permissions=["CREATE_ASSET", "DELETE_ASSET"]
        )
        
        updated = engine.revoke_permission(role, "DELETE_ASSET")
        
        assert "DELETE_ASSET" not in updated.permissions
    
    def test_check_permission(self, engine, sample_user):
        """Test checking permission."""
        role = engine.create_role(
            name="Operator",
            permissions=["CREATE_ASSET"]
        )
        engine.assign_role_to_user(sample_user, role)
        
        has_permission = engine.check_permission(sample_user.id, "CREATE_ASSET")
        
        assert has_permission is True
    
    def test_list_roles(self, engine):
        """Test listing roles."""
        engine.create_role(name="Role1")
        engine.create_role(name="Role2")
        
        roles = engine.list_roles()
        
        assert len(roles) == 2


class TestOrganizationEngine:
    """Tests for organization engine."""
    
    @pytest.fixture
    def engine(self):
        """Create organization engine."""
        return OrganizationEngine()
    
    @pytest.fixture
    def sample_user(self):
        """Create sample user."""
        return User(
            id="user-1",
            email="test@example.com",
            username="testuser"
        )
    
    def test_create_organization(self, engine):
        """Test creating an organization."""
        org = engine.create_organization(
            name="Test Org",
            slug="test-org"
        )
        
        assert org is not None
        assert org.name == "Test Org"
        assert org.slug == "test-org"
    
    def test_get_organization(self, engine):
        """Test getting organization."""
        org = engine.create_organization(name="Test", slug="test")
        
        retrieved = engine.get_organization(org.id)
        
        assert retrieved is not None
        assert retrieved.name == "Test"
    
    def test_update_organization(self, engine):
        """Test updating organization."""
        org = engine.create_organization(name="Original", slug="original")
        
        updated = engine.update_organization(org, name="Updated")
        
        assert updated.name == "Updated"
    
    def test_add_member(self, engine, sample_user):
        """Test adding member."""
        org = engine.create_organization(name="Test", slug="test")
        
        membership = engine.add_member(org, sample_user)
        
        assert membership is not None
        assert membership.user_id == sample_user.id
    
    def test_remove_member(self, engine, sample_user):
        """Test removing member."""
        org = engine.create_organization(name="Test", slug="test")
        engine.add_member(org, sample_user)
        
        result = engine.remove_member(org.id, sample_user.id)
        
        assert result is True
    
    def test_update_member_role(self, engine, sample_user):
        """Test updating member role."""
        org = engine.create_organization(name="Test", slug="test")
        engine.add_member(org, sample_user)
        
        updated = engine.update_member_role(org.id, sample_user.id, MembershipRole.ADMIN)
        
        assert updated.membership_role == MembershipRole.ADMIN
    
    def test_is_member(self, engine, sample_user):
        """Test checking membership."""
        org = engine.create_organization(name="Test", slug="test")
        engine.add_member(org, sample_user)
        
        is_member = engine.is_member(org.id, sample_user.id)
        
        assert is_member is True
    
    def test_get_members(self, engine, sample_user):
        """Test getting members."""
        org = engine.create_organization(name="Test", slug="test")
        engine.add_member(org, sample_user)
        
        members = engine.get_members(org.id)
        
        assert len(members) == 1
    
    def test_get_user_organizations(self, engine, sample_user):
        """Test getting user's organizations."""
        org1 = engine.create_organization(name="Org1", slug="org1")
        org2 = engine.create_organization(name="Org2", slug="org2")
        engine.add_member(org1, sample_user)
        engine.add_member(org2, sample_user)
        
        orgs = engine.get_user_organizations(sample_user.id)
        
        assert len(orgs) == 2
    
    def test_activate_organization(self, engine):
        """Test activating organization."""
        org = engine.create_organization(name="Test", slug="test")
        engine.deactivate_organization(org)
        
        activated = engine.activate_organization(org)
        
        assert activated.is_active is True


class TestKeycloakAdapter:
    """Tests for Keycloak adapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create Keycloak adapter."""
        return KeycloakAdapter(realm_name="test-realm")
    
    def test_sync_user(self, adapter):
        """Test syncing user from Keycloak."""
        keycloak_user = {
            "id": "kc-user-1",
            "email": "test@example.com",
            "username": "testuser",
            "firstName": "Test",
            "lastName": "User",
            "enabled": True
        }
        
        user = adapter.sync_user(keycloak_user)
        
        assert user.external_id == "kc-user-1"
        assert user.email == "test@example.com"
        assert user.username == "testuser"
    
    def test_map_keycloak_roles(self, adapter):
        """Test mapping Keycloak roles to local."""
        keycloak_roles = ["admin", "operator", "inspector"]
        
        local_roles = adapter.map_keycloak_roles_to_local(keycloak_roles)
        
        assert "OrganizationAdmin" in local_roles
        assert "Operator" in local_roles
        assert "Inspector" in local_roles
    
    def test_map_local_role_to_keycloak(self, adapter):
        """Test mapping local role to Keycloak."""
        keycloak_role = adapter.map_local_role_to_keycloak("OrganizationAdmin")
        
        assert keycloak_role == "admin"
    
    def test_validate_token(self, adapter):
        """Test token validation."""
        token = "test-token"
        
        claims = adapter.validate_token(token)
        
        assert claims is not None
        assert "active" in claims
    
    def test_create_keycloak_user_data(self, adapter):
        """Test creating Keycloak user data."""
        user_data = adapter.create_keycloak_user_data(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User"
        )
        
        assert user_data["email"] == "test@example.com"
        assert user_data["username"] == "testuser"


class TestSecurityValidator:
    """Tests for security validator."""
    
    @pytest.fixture
    def validator(self):
        """Create validator."""
        return SecurityValidator()
    
    def test_validate_valid_user(self, validator):
        """Test validating valid user."""
        user = User(
            id="user-1",
            email="test@example.com",
            username="testuser"
        )
        
        issues = validator.validate_user(user)
        
        assert len(issues) == 0
    
    def test_validate_missing_email(self, validator):
        """Test validation with missing email."""
        user = User(
            id="user-1",
            email="",
            username="testuser"
        )
        
        issues = validator.validate_user(user)
        
        assert any("email" in i.lower() for i in issues)
    
    def test_validate_invalid_email(self, validator):
        """Test validation with invalid email."""
        user = User(
            id="user-1",
            email="invalid-email",
            username="testuser"
        )
        
        issues = validator.validate_user(user)
        
        assert any("invalid" in i.lower() for i in issues)
    
    def test_validate_role(self, validator):
        """Test validating role."""
        role = Role(
            id="role-1",
            name="TestRole"
        )
        
        issues = validator.validate_role(role)
        
        assert len(issues) == 0
    
    def test_validate_system_role_type(self, validator):
        """Test validating system role type."""
        role = Role(
            id="role-1",
            name="TestRole",
            is_system_role=True,
            role_type=RoleType.CUSTOM  # Should be SYSTEM
        )
        
        issues = validator.validate_role(role)
        
        assert len(issues) > 0
    
    def test_validate_organization(self, validator):
        """Test validating organization."""
        org = Organization(
            id="org-1",
            name="Test Org",
            slug="test-org"
        )
        
        issues = validator.validate_organization(org)
        
        assert len(issues) == 0
    
    def test_validate_invalid_slug(self, validator):
        """Test validating invalid slug."""
        org = Organization(
            id="org-1",
            name="Test",
            slug="invalid slug!"
        )
        
        issues = validator.validate_organization(org)
        
        assert any("slug" in i.lower() for i in issues)
    
    def test_validate_role_assignment(self, validator):
        """Test validating role assignment."""
        user = User(
            id="user-1",
            email="test@example.com",
            username="testuser",
            status=UserStatus.ACTIVE
        )
        role = Role(
            id="role-1",
            name="TestRole"
        )
        
        issues = validator.validate_role_assignment(user, role)
        
        assert len(issues) == 0
    
    def test_validate_role_assignment_inactive_user(self, validator):
        """Test validating assignment to inactive user."""
        user = User(
            id="user-1",
            email="test@example.com",
            username="testuser",
            status=UserStatus.INACTIVE
        )
        role = Role(
            id="role-1",
            name="TestRole"
        )
        
        issues = validator.validate_role_assignment(user, role)
        
        assert len(issues) > 0
    
    def test_validate_email(self, validator):
        """Test email validation."""
        issues = validator.validate_email("test@example.com")
        
        assert len(issues) == 0
    
    def test_validate_invalid_email_format(self, validator):
        """Test invalid email validation."""
        issues = validator.validate_email("invalid")
        
        assert len(issues) > 0
    
    def test_validate_username(self, validator):
        """Test username validation."""
        issues = validator.validate_username("testuser")
        
        assert len(issues) == 0
    
    def test_validate_short_username(self, validator):
        """Test short username validation."""
        issues = validator.validate_username("ab")
        
        assert len(issues) > 0


class TestUserStatus:
    """Tests for user status."""
    
    def test_all_statuses(self):
        """Test all status values."""
        statuses = [
            UserStatus.ACTIVE,
            UserStatus.INACTIVE,
            UserStatus.SUSPENDED,
            UserStatus.PENDING_VERIFICATION
        ]
        
        assert len(statuses) == 4
    
    def test_status_values(self):
        """Test status values."""
        assert UserStatus.ACTIVE.value == "active"
        assert UserStatus.INACTIVE.value == "inactive"


class TestRoleType:
    """Tests for role type."""
    
    def test_all_types(self):
        """Test all role types."""
        types = [
            RoleType.SYSTEM,
            RoleType.ORGANIZATION,
            RoleType.CUSTOM
        ]
        
        assert len(types) == 3
    
    def test_type_values(self):
        """Test type values."""
        assert RoleType.SYSTEM.value == "system"
        assert RoleType.CUSTOM.value == "custom"


class TestMembershipRole:
    """Tests for membership role."""
    
    def test_all_roles(self):
        """Test all membership roles."""
        roles = [
            MembershipRole.OWNER,
            MembershipRole.ADMIN,
            MembershipRole.MEMBER
        ]
        
        assert len(roles) == 3
    
    def test_role_values(self):
        """Test role values."""
        assert MembershipRole.OWNER.value == "owner"
        assert MembershipRole.ADMIN.value == "admin"


class TestPermissionInheritance:
    """Tests for permission inheritance."""
    
    @pytest.fixture
    def engine(self):
        """Create role engine."""
        return RoleEngine()
    
    def test_inherited_permissions(self, engine):
        """Test inherited permissions."""
        parent = engine.create_role(
            name="ParentRole",
            permissions=["VIEW_ASSET", "UPDATE_ASSET"]
        )
        
        child = engine.create_role(
            name="ChildRole",
            permissions=["CREATE_ASSET"],
            parent_role_id=parent.id,
            inherits_permissions=True
        )
        
        permissions = engine.get_role_permissions(child.id)
        
        assert "VIEW_ASSET" in permissions
        assert "CREATE_ASSET" in permissions


class TestOrganizationIsolation:
    """Tests for organization isolation."""
    
    @pytest.fixture
    def org_engine(self):
        """Create organization engine."""
        return OrganizationEngine()
    
    @pytest.fixture
    def role_engine(self):
        """Create role engine."""
        return RoleEngine()
    
    def test_organization_users_isolation(self, org_engine):
        """Test organization users are isolated."""
        org1 = org_engine.create_organization(name="Org1", slug="org1")
        org2 = org_engine.create_organization(name="Org2", slug="org2")
        
        user = User(id="user-1", email="test@example.com", username="testuser")
        
        org_engine.add_member(org1, user)
        
        members1 = org_engine.get_members(org1.id)
        members2 = org_engine.get_members(org2.id)
        
        assert len(members1) == 1
        assert len(members2) == 0
