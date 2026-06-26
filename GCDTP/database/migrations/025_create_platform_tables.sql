-- Migration 025: Enterprise Packaging Layer
-- Creates platform tables for editions, catalogs, bundles, and license management
-- Maintains backward compatibility

BEGIN;

-- Create enums
DO $$ BEGIN
    CREATE TYPE edition_type AS ENUM (
        'community',
        'professional',
        'enterprise',
        'government',
        'utility',
        'industrial',
        'custom'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE bundle_type AS ENUM (
        'docker',
        'offline',
        'enterprise',
        'upgrade',
        'backup'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE installation_profile AS ENUM (
        'minimal',
        'standard',
        'enterprise',
        'full'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE platform_status AS ENUM (
        'active',
        'deprecated',
        'removed',
        'beta',
        'preview'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create platform_editions table
CREATE TABLE IF NOT EXISTS platform_editions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    edition_name VARCHAR(100) NOT NULL UNIQUE,
    edition_type edition_type NOT NULL,
    description TEXT,
    features JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for platform_editions
CREATE INDEX IF NOT EXISTS idx_platform_editions_type ON platform_editions(edition_type);
CREATE INDEX IF NOT EXISTS idx_platform_editions_active ON platform_editions(is_active) WHERE is_active = TRUE;

-- Create component_catalog table
CREATE TABLE IF NOT EXISTS component_catalog (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    component_name VARCHAR(100) NOT NULL UNIQUE,
    component_key VARCHAR(100) NOT NULL UNIQUE,
    component_type VARCHAR(50) NOT NULL,  -- engine, integration, security, observability, performance, devops
    version VARCHAR(50) NOT NULL,
    status platform_status DEFAULT 'active',
    description TEXT,
    dependencies JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for component_catalog
CREATE INDEX IF NOT EXISTS idx_component_catalog_key ON component_catalog(component_key);
CREATE INDEX IF NOT EXISTS idx_component_catalog_type ON component_catalog(component_type);
CREATE INDEX IF NOT EXISTS idx_component_catalog_status ON component_catalog(status);

-- Create bundle_definitions table
CREATE TABLE IF NOT EXISTS bundle_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bundle_name VARCHAR(100) NOT NULL UNIQUE,
    bundle_key VARCHAR(100) NOT NULL UNIQUE,
    bundle_type bundle_type NOT NULL,
    description TEXT,
    components JSONB DEFAULT '[]',
    dependencies JSONB DEFAULT '[]',
    requirements JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for bundle_definitions
CREATE INDEX IF NOT EXISTS idx_bundle_definitions_key ON bundle_definitions(bundle_key);
CREATE INDEX IF NOT EXISTS idx_bundle_definitions_type ON bundle_definitions(bundle_type);

-- Create installation_profiles table
CREATE TABLE IF NOT EXISTS installation_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_name VARCHAR(100) NOT NULL UNIQUE,
    profile_type installation_profile NOT NULL,
    description TEXT,
    included_components JSONB DEFAULT '[]',
    optional_components JSONB DEFAULT '[]',
    system_requirements JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for installation_profiles
CREATE INDEX IF NOT EXISTS idx_installation_profiles_type ON installation_profiles(profile_type);

-- Create upgrade_history table
CREATE TABLE IF NOT EXISTS upgrade_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_version VARCHAR(50) NOT NULL,
    to_version VARCHAR(50) NOT NULL,
    migration_version INTEGER NOT NULL,
    upgrade_type VARCHAR(50) NOT NULL,  -- major, minor, patch
    status VARCHAR(50) NOT NULL DEFAULT 'pending',  -- pending, in_progress, completed, failed, rolled_back
    rollback_from_version VARCHAR(50),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    upgrade_plan JSONB DEFAULT '{}',
    errors JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for upgrade_history
CREATE INDEX IF NOT EXISTS idx_upgrade_history_from ON upgrade_history(from_version);
CREATE INDEX IF NOT EXISTS idx_upgrade_history_to ON upgrade_history(to_version);
CREATE INDEX IF NOT EXISTS idx_upgrade_history_status ON upgrade_history(status);

-- Create compatibility_matrix table
CREATE TABLE IF NOT EXISTS compatibility_matrix (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    component_name VARCHAR(100) NOT NULL,
    component_version VARCHAR(50) NOT NULL,
    compatible_versions JSONB DEFAULT '{}',
    incompatible_versions JSONB DEFAULT '[]',
    requirements JSONB DEFAULT '{}',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(component_name, component_version)
);

-- Create indexes for compatibility_matrix
CREATE INDEX IF NOT EXISTS idx_compatibility_matrix_component ON compatibility_matrix(component_name);

-- Create license_metadata table (metadata only, no enforcement)
CREATE TABLE IF NOT EXISTS license_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    license_key VARCHAR(255) NOT NULL UNIQUE,
    license_type VARCHAR(50) NOT NULL,  -- trial, standard, enterprise
    edition edition_type NOT NULL,
    issued_to VARCHAR(255),
    organizations JSONB DEFAULT '[]',
    features JSONB DEFAULT '[]',
    max_users INTEGER,
    max_assets INTEGER,
    expiry_date DATE,
    issued_at DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for license_metadata
CREATE INDEX IF NOT EXISTS idx_license_metadata_type ON license_metadata(license_type);
CREATE INDEX IF NOT EXISTS idx_license_metadata_edition ON license_metadata(edition);
CREATE INDEX IF NOT EXISTS idx_license_metadata_expiry ON license_metadata(expiry_date);

-- Create release_bundles table
CREATE TABLE IF NOT EXISTS release_bundles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    release_version VARCHAR(50) NOT NULL UNIQUE,
    bundle_type bundle_type NOT NULL,
    bundle_path VARCHAR(500),
    bundle_size_bytes BIGINT,
    checksum VARCHAR(64),
    components JSONB DEFAULT '[]',
    included_editions JSONB DEFAULT '[]',
    release_notes TEXT,
    is_stable BOOLEAN DEFAULT FALSE,
    released_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for release_bundles
CREATE INDEX IF NOT EXISTS idx_release_bundles_version ON release_bundles(release_version);
CREATE INDEX IF NOT EXISTS idx_release_bundles_type ON release_bundles(bundle_type);
CREATE INDEX IF NOT EXISTS idx_release_bundles_stable ON release_bundles(is_stable) WHERE is_stable = TRUE;

-- Create platform_registry table
CREATE TABLE IF NOT EXISTS platform_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module_name VARCHAR(100) NOT NULL UNIQUE,
    module_key VARCHAR(100) NOT NULL UNIQUE,
    module_type VARCHAR(50) NOT NULL,
    version VARCHAR(50) NOT NULL,
    status platform_status DEFAULT 'active',
    owner VARCHAR(100),
    capabilities JSONB DEFAULT '[]',
    dependencies JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    installed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for platform_registry
CREATE INDEX IF NOT EXISTS idx_platform_registry_key ON platform_registry(module_key);
CREATE INDEX IF NOT EXISTS idx_platform_registry_type ON platform_registry(module_type);
CREATE INDEX IF NOT EXISTS idx_platform_registry_status ON platform_registry(status);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_platform_editions_updated_at
    BEFORE UPDATE ON platform_editions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_component_catalog_updated_at
    BEFORE UPDATE ON component_catalog
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bundle_definitions_updated_at
    BEFORE UPDATE ON bundle_definitions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_installation_profiles_updated_at
    BEFORE UPDATE ON installation_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_compatibility_matrix_updated_at
    BEFORE UPDATE ON compatibility_matrix
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_license_metadata_updated_at
    BEFORE UPDATE ON license_metadata
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_platform_registry_updated_at
    BEFORE UPDATE ON platform_registry
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create view for active editions
CREATE OR REPLACE VIEW active_editions AS
SELECT 
    edition_name,
    edition_type,
    description,
    features
FROM platform_editions
WHERE is_active = TRUE
ORDER BY edition_name;

-- Create view for active components
CREATE OR REPLACE VIEW active_components AS
SELECT 
    component_name,
    component_key,
    component_type,
    version,
    description,
    dependencies
FROM component_catalog
WHERE status = 'active'
ORDER BY component_type, component_name;

-- Create view for available bundles
CREATE OR REPLACE VIEW available_bundles AS
SELECT 
    release_version,
    bundle_type,
    bundle_size_bytes,
    is_stable,
    released_at
FROM release_bundles
ORDER BY released_at DESC;

-- Create view for upgrade paths
CREATE OR REPLACE VIEW upgrade_paths AS
SELECT 
    from_version,
    to_version,
    migration_version,
    upgrade_type,
    status,
    started_at,
    completed_at
FROM upgrade_history
ORDER BY from_version, to_version;

-- Create view for license summary
CREATE OR REPLACE VIEW license_summary AS
SELECT 
    license_type,
    edition,
    COUNT(*) as license_count,
    COUNT(*) FILTER (WHERE expiry_date > CURRENT_DATE) as active_count,
    MAX(expiry_date) as latest_expiry
FROM license_metadata
GROUP BY license_type, edition;

COMMENT ON TABLE platform_editions IS 'Platform edition definitions';
COMMENT ON TABLE component_catalog IS 'Component catalog and registry';
COMMENT ON TABLE bundle_definitions IS 'Bundle definition templates';
COMMENT ON TABLE installation_profiles IS 'Installation profile configurations';
COMMENT ON TABLE upgrade_history IS 'Upgrade and migration history';
COMMENT ON TABLE compatibility_matrix IS 'Component compatibility matrix';
COMMENT ON TABLE license_metadata IS 'License metadata (no enforcement)';
COMMENT ON TABLE release_bundles IS 'Release bundle tracking';
COMMENT ON TABLE platform_registry IS 'Platform module registry';

COMMIT;
