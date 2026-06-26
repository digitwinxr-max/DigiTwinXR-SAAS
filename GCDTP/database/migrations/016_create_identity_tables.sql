-- Migration 016: Identity & Access Management
-- Creates organizations, users, roles, and permissions tables
-- Maintains foreign keys and backward compatibility

BEGIN;

-- Create user_status enum
DO $$ BEGIN
    CREATE TYPE user_status AS ENUM (
        'active',
        'inactive',
        'suspended',
        'pending_verification'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create role_type enum
DO $$ BEGIN
    CREATE TYPE role_type AS ENUM (
        'system',
        'organization',
        'custom'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create membership_role enum
DO $$ BEGIN
    CREATE TYPE membership_role AS ENUM (
        'owner',
        'admin',
        'member'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create organizations table
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    settings JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for organizations
CREATE INDEX IF NOT EXISTS idx_organizations_slug ON organizations(slug);
CREATE INDEX IF NOT EXISTS idx_organizations_is_active ON organizations(is_active);

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id VARCHAR(255) UNIQUE,  -- Keycloak user ID
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(255),
    status user_status NOT NULL DEFAULT 'active',
    is_superuser BOOLEAN DEFAULT FALSE,
    keycloak_realm VARCHAR(100),
    keycloak_token TEXT,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for users
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_external_id ON users(external_id);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);

-- Create roles table
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    role_type role_type NOT NULL DEFAULT 'custom',
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    parent_role_id UUID REFERENCES roles(id) ON DELETE SET NULL,
    is_system_role BOOLEAN DEFAULT FALSE,
    inherits_permissions BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(name, organization_id)
);

-- Create indexes for roles
CREATE INDEX IF NOT EXISTS idx_roles_name ON roles(name);
CREATE INDEX IF NOT EXISTS idx_roles_organization_id ON roles(organization_id);
CREATE INDEX IF NOT EXISTS idx_roles_parent_role_id ON roles(parent_role_id);

-- Create permissions table
CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    resource VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(resource, action)
);

-- Create indexes for permissions
CREATE INDEX IF NOT EXISTS idx_permissions_code ON permissions(code);
CREATE INDEX IF NOT EXISTS idx_permissions_resource ON permissions(resource);

-- Create user_roles junction table
CREATE TABLE IF NOT EXISTS user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    granted_by UUID REFERENCES users(id) ON DELETE SET NULL,
    granted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(user_id, role_id, organization_id)
);

-- Create indexes for user_roles
CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_role_id ON user_roles(role_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_organization_id ON user_roles(organization_id);

-- Create role_permissions junction table
CREATE TABLE IF NOT EXISTS role_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    granted_by UUID REFERENCES users(id) ON DELETE SET NULL,
    granted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(role_id, permission_id)
);

-- Create indexes for role_permissions
CREATE INDEX IF NOT EXISTS idx_role_permissions_role_id ON role_permissions(role_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_permission_id ON role_permissions(permission_id);

-- Create organization_members table
CREATE TABLE IF NOT EXISTS organization_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    membership_role membership_role NOT NULL DEFAULT 'member',
    invited_by UUID REFERENCES users(id) ON DELETE SET NULL,
    invited_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    joined_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(organization_id, user_id)
);

-- Create indexes for organization_members
CREATE INDEX IF NOT EXISTS idx_org_members_org_id ON organization_members(organization_id);
CREATE INDEX IF NOT EXISTS idx_org_members_user_id ON organization_members(user_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_organizations_updated_at
    BEFORE UPDATE ON organizations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_roles_updated_at
    BEFORE UPDATE ON roles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert system permissions
INSERT INTO permissions (code, name, description, resource, action) VALUES
    ('CREATE_ASSET', 'Create Asset', 'Permission to create new assets', 'asset', 'create'),
    ('UPDATE_ASSET', 'Update Asset', 'Permission to update assets', 'asset', 'update'),
    ('DELETE_ASSET', 'Delete Asset', 'Permission to delete assets', 'asset', 'delete'),
    ('VIEW_ASSET', 'View Asset', 'Permission to view assets', 'asset', 'view'),
    ('CREATE_WORK_ORDER', 'Create Work Order', 'Permission to create work orders', 'work_order', 'create'),
    ('UPDATE_WORK_ORDER', 'Update Work Order', 'Permission to update work orders', 'work_order', 'update'),
    ('DELETE_WORK_ORDER', 'Delete Work Order', 'Permission to delete work orders', 'work_order', 'delete'),
    ('ASSIGN_WORK_ORDER', 'Assign Work Order', 'Permission to assign work orders', 'work_order', 'assign'),
    ('COMPLETE_WORK_ORDER', 'Complete Work Order', 'Permission to complete work orders', 'work_order', 'complete'),
    ('VIEW_WORK_ORDER', 'View Work Order', 'Permission to view work orders', 'work_order', 'view'),
    ('UPLOAD_DOCUMENT', 'Upload Document', 'Permission to upload documents', 'document', 'create'),
    ('UPDATE_DOCUMENT', 'Update Document', 'Permission to update documents', 'document', 'update'),
    ('DELETE_DOCUMENT', 'Delete Document', 'Permission to delete documents', 'document', 'delete'),
    ('VIEW_DOCUMENT', 'View Document', 'Permission to view documents', 'document', 'view'),
    ('VIEW_TIMELINE', 'View Timeline', 'Permission to view operational timeline', 'timeline', 'view'),
    ('MANAGE_TIMELINE', 'Manage Timeline', 'Permission to manage timeline', 'timeline', 'manage'),
    ('MANAGE_USERS', 'Manage Users', 'Permission to manage users', 'user', 'manage'),
    ('MANAGE_ROLES', 'Manage Roles', 'Permission to manage roles', 'role', 'manage'),
    ('MANAGE_ORGANIZATION', 'Manage Organization', 'Permission to manage organization', 'organization', 'manage'),
    ('VIEW_SENSORS', 'View Sensors', 'Permission to view sensors', 'sensor', 'view'),
    ('MANAGE_SENSORS', 'Manage Sensors', 'Permission to manage sensors', 'sensor', 'manage'),
    ('VIEW_EVENTS', 'View Events', 'Permission to view events', 'event', 'view'),
    ('MANAGE_EVENTS', 'Manage Events', 'Permission to manage events', 'event', 'manage')
ON CONFLICT (code) DO NOTHING;

-- Insert system roles
INSERT INTO roles (name, description, role_type, is_system_role, inherits_permissions) VALUES
    ('SuperAdmin', 'Full system access', 'system', TRUE, TRUE),
    ('OrganizationAdmin', 'Organization administration', 'system', TRUE, TRUE),
    ('Operator', 'Operational access', 'system', TRUE, TRUE),
    ('Inspector', 'Inspection access', 'system', TRUE, TRUE),
    ('Technician', 'Maintenance access', 'system', TRUE, TRUE),
    ('Viewer', 'Read-only access', 'system', TRUE, FALSE)
ON CONFLICT (name, organization_id) DO NOTHING;

-- Create view for user permissions
CREATE OR REPLACE VIEW user_permissions_view AS
SELECT 
    u.id AS user_id,
    u.username,
    u.email,
    r.id AS role_id,
    r.name AS role_name,
    r.organization_id,
    p.code AS permission_code,
    p.resource,
    p.action
FROM users u
JOIN user_roles ur ON u.id = ur.user_id
JOIN roles r ON ur.role_id = r.id
LEFT JOIN role_permissions rp ON r.id = rp.role_id
LEFT JOIN permissions p ON rp.permission_id = p.id
WHERE u.status = 'active' 
    AND (ur.expires_at IS NULL OR ur.expires_at > NOW())
    AND r.is_system_role = TRUE;

-- Create view for organization members
CREATE OR REPLACE VIEW organization_members_view AS
SELECT 
    om.id,
    om.organization_id,
    o.name AS organization_name,
    om.user_id,
    u.username,
    u.email,
    u.full_name,
    om.membership_role,
    om.is_active,
    om.invited_at,
    om.joined_at
FROM organization_members om
JOIN organizations o ON om.organization_id = o.id
JOIN users u ON om.user_id = u.id;

COMMENT ON TABLE organizations IS 'Organizations for multi-tenancy';
COMMENT ON TABLE users IS 'User accounts with Keycloak integration';
COMMENT ON TABLE roles IS 'Role-based access control roles';
COMMENT ON TABLE permissions IS 'Granular permissions';
COMMENT ON TABLE user_roles IS 'User to role assignments';
COMMENT ON TABLE role_permissions IS 'Role to permission assignments';
COMMENT ON TABLE organization_members IS 'Organization membership';

COMMIT;
