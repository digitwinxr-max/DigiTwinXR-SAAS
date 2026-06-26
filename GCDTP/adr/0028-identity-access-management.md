# ADR-0028: Identity & Access Management

## Status

Accepted

## Context

GCDTP has implemented comprehensive asset management, work orders, and documents. However, there is no mechanism for user authentication, authorization, and multi-tenancy.

### The Need

```
Organization
    ↓
Users
    ↓
Roles
    ↓
Permissions
    ↓
Assets
    ↓
Work Orders
    ↓
Documents
```

This creates a complete security model.

## Decision

Create Identity & Access Management:

```
backend/src/security/
├── user_types.py           # Core types
├── role_engine.py          # RBAC engine
├── permission_engine.py    # Permission management
├── organization_engine.py   # Organization management
├── keycloak_adapter.py     # Keycloak integration
├── security_validator.py    # Validation
└── __init__.py
```

## Architecture

### Key Principle

**FastAPI remains authoritative for business logic.**

```
┌─────────────────────────────────────────────────────────────────┐
│                         ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Keycloak                                                        │
│    │                                                              │
│    ├── Authentication                                             │
│    ├── User Data                                                 │
│    └── Token Management                                           │
│           │                                                       │
│           ▼                                                       │
│  FastAPI (Authoritative)                                         │
│    │                                                              │
│    ├── Role Engine (RBAC)                                         │
│    ├── Permission Engine                                           │
│    ├── Organization Engine                                         │
│    └── Business Logic                                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Core Types

### Organization

```python
@dataclass
class Organization:
    id: str
    name: str
    slug: str
    description: str
    is_active: bool
    created_at: datetime
```

### User

```python
@dataclass
class User:
    id: str
    external_id: str  # Keycloak ID
    email: str
    username: str
    first_name: str
    last_name: str
    status: UserStatus
    is_superuser: bool
```

### Role

```python
@dataclass
class Role:
    id: str
    name: str
    role_type: RoleType  # SYSTEM, ORGANIZATION, CUSTOM
    permissions: Set[str]
    parent_role_id: Optional[str]  # For inheritance
    inherits_permissions: bool
```

### Permission

```python
@dataclass
class Permission:
    id: str
    code: str
    resource: str
    action: str
```

## Role Model

### System Roles

| Role | Permissions |
|------|------------|
| SuperAdmin | All permissions |
| OrganizationAdmin | Organization management |
| Operator | Asset/work order operations |
| Inspector | Inspection access |
| Technician | Maintenance access |
| Viewer | Read-only access |

### Custom Roles

Organizations can create custom roles with specific permissions.

## Permissions

### Asset Permissions

- CREATE_ASSET
- UPDATE_ASSET
- DELETE_ASSET
- VIEW_ASSET

### Work Order Permissions

- CREATE_WORK_ORDER
- ASSIGN_WORK_ORDER
- COMPLETE_WORK_ORDER
- VIEW_WORK_ORDER

### Document Permissions

- UPLOAD_DOCUMENT
- DELETE_DOCUMENT
- VIEW_DOCUMENT

### Administrative Permissions

- MANAGE_USERS
- MANAGE_ROLES
- MANAGE_ORGANIZATION
- VIEW_TIMELINE

## Keycloak Adapter

### Responsibilities

1. **Realm Mapping** - Map Keycloak realms to organizations
2. **User Synchronization** - Sync users from Keycloak to local model
3. **Token Validation** - Validate Keycloak tokens
4. **Role Mapping** - Map Keycloak roles to local roles

### Not Responsible For

- Business logic
- Permission checks
- Data ownership
- Organization boundaries

## Database Schema

### organizations

```sql
CREATE TABLE organizations (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE
);
```

### users

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    external_id VARCHAR(255),  -- Keycloak ID
    email VARCHAR(255) UNIQUE,
    username VARCHAR(100) UNIQUE,
    is_superuser BOOLEAN DEFAULT FALSE
);
```

### roles

```sql
CREATE TABLE roles (
    id UUID PRIMARY KEY,
    name VARCHAR(100),
    role_type role_type,
    organization_id UUID,
    parent_role_id UUID REFERENCES roles(id),
    is_system_role BOOLEAN
);
```

### permissions

```sql
CREATE TABLE permissions (
    id UUID PRIMARY KEY,
    code VARCHAR(100) UNIQUE,
    resource VARCHAR(100),
    action VARCHAR(50)
);
```

### user_roles

```sql
CREATE TABLE user_roles (
    user_id UUID REFERENCES users(id),
    role_id UUID REFERENCES roles(id),
    organization_id UUID,
    expires_at TIMESTAMP
);
```

## EventBus Integration

### User Events

- USER_CREATED
- USER_UPDATED
- USER_DEACTIVATED

### Role Events

- ROLE_ASSIGNED
- ROLE_REMOVED
- PERMISSION_GRANTED
- PERMISSION_REVOKED

### Organization Events

- ORGANIZATION_CREATED
- ORGANIZATION_UPDATED
- ORGANIZATION_MEMBER_ADDED
- ORGANIZATION_MEMBER_REMOVED

## Consequences

### Positive

1. **Multi-tenancy** - Organizations are isolated
2. **RBAC** - Fine-grained access control
3. **Keycloak Integration** - Standard auth
4. **Event Integration** - Timeline includes security events
5. **Permission Inheritance** - Role hierarchies

### Negative

1. **Complexity** - More entities to manage
2. **Keycloak Dependency** - Requires Keycloak setup
3. **Migration** - New tables required

### Neutral

1. **Business logic stays in FastAPI** - No logic in Keycloak
2. **Local permission model** - Keycloak roles are mapped
3. **Backward compatible** - SuperAdmin can access everything

## Acceptance Criteria

- [x] Organizations
- [x] Users
- [x] Roles
- [x] Permissions
- [x] Membership
- [x] RBAC
- [x] Authorization checks
- [x] Permission inheritance
- [x] Role assignment
- [x] Organization isolation
- [x] Keycloak adapter
- [x] EventBus integration
- [x] Database migration
- [x] 60+ tests
- [x] ADR documentation
