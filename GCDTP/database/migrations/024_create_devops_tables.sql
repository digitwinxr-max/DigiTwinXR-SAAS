-- Migration 024: Deployment & DevOps Layer
-- Creates DevOps-related tables for configuration, secrets, backups, and deployment management
-- Maintains backward compatibility

BEGIN;

-- Create status enums
DO $$ BEGIN
    CREATE TYPE deployment_status AS ENUM (
        'pending',
        'running',
        'completed',
        'failed',
        'rolled_back'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE backup_status AS ENUM (
        'pending',
        'running',
        'completed',
        'failed',
        'cancelled'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE restore_status AS ENUM (
        'pending',
        'running',
        'completed',
        'failed',
        'cancelled'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE feature_flag_status AS ENUM (
        'active',
        'inactive',
        'scheduled',
        'paused'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE probe_type AS ENUM (
        'readiness',
        'liveness',
        'startup',
        'dependency'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create environment_profiles table
CREATE TABLE IF NOT EXISTS environment_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_name VARCHAR(100) NOT NULL UNIQUE,
    environment VARCHAR(50) NOT NULL,  -- development, test, staging, production
    profile_type VARCHAR(50) NOT NULL,  -- local, docker, enterprise
    description TEXT,
    is_active BOOLEAN DEFAULT FALSE,
    config_overrides JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for environment_profiles
CREATE INDEX IF NOT EXISTS idx_env_profiles_env ON environment_profiles(environment);
CREATE INDEX IF NOT EXISTS idx_env_profiles_active ON environment_profiles(is_active) WHERE is_active = TRUE;

-- Create system_configurations table
CREATE TABLE IF NOT EXISTS system_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_key VARCHAR(255) NOT NULL,
    config_value TEXT,
    value_type VARCHAR(50) DEFAULT 'string',  -- string, number, boolean, json
    environment VARCHAR(50) NOT NULL,  -- development, test, staging, production, global
    profile_name VARCHAR(100),  -- NULL for environment-wide, or specific profile
    is_secret BOOLEAN DEFAULT FALSE,
    is_runtime_override BOOLEAN DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(config_key, environment, profile_name)
);

-- Create indexes for system_configurations
CREATE INDEX IF NOT EXISTS idx_sys_config_key ON system_configurations(config_key);
CREATE INDEX IF NOT EXISTS idx_sys_config_env ON system_configurations(environment);
CREATE INDEX IF NOT EXISTS idx_sys_config_runtime ON system_configurations(is_runtime_override) WHERE is_runtime_override = TRUE;

-- Create feature_flags table
CREATE TABLE IF NOT EXISTS feature_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    flag_name VARCHAR(100) NOT NULL UNIQUE,
    flag_key VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    status feature_flag_status NOT NULL DEFAULT 'inactive',
    rollout_percentage INTEGER DEFAULT 0 CHECK (rollout_percentage >= 0 AND rollout_percentage <= 100),
    target_organizations JSONB DEFAULT '[]',  -- Organization IDs for org-specific features
    scheduled_activation TIMESTAMP WITH TIME ZONE,
    scheduled_deactivation TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for feature_flags
CREATE INDEX IF NOT EXISTS idx_feature_flags_key ON feature_flags(flag_key);
CREATE INDEX IF NOT EXISTS idx_feature_flags_status ON feature_flags(status);
CREATE INDEX IF NOT EXISTS idx_feature_flags_scheduled ON feature_flags(scheduled_activation) WHERE scheduled_activation IS NOT NULL;

-- Create backup_jobs table
CREATE TABLE IF NOT EXISTS backup_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    backup_type VARCHAR(50) NOT NULL,  -- postgresql, config, metadata, snapshot
    status backup_status NOT NULL DEFAULT 'pending',
    backup_size_bytes BIGINT,
    duration_seconds INTEGER,
    backup_path VARCHAR(500),
    compression_algorithm VARCHAR(50),
    encryption_enabled BOOLEAN DEFAULT FALSE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for backup_jobs
CREATE INDEX IF NOT EXISTS idx_backup_jobs_status ON backup_jobs(status);
CREATE INDEX IF NOT EXISTS idx_backup_jobs_type ON backup_jobs(backup_type);
CREATE INDEX IF NOT EXISTS idx_backup_jobs_created_at ON backup_jobs(created_at DESC);

-- Create restore_jobs table
CREATE TABLE IF NOT EXISTS restore_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    backup_id UUID REFERENCES backup_jobs(id) ON DELETE SET NULL,
    status restore_status NOT NULL DEFAULT 'pending',
    restore_type VARCHAR(50) NOT NULL,  -- full, point_in_time, selective
    target_environment VARCHAR(50),
    point_in_time TIMESTAMP WITH TIME ZONE,
    selective_items JSONB DEFAULT '[]',
    dry_run BOOLEAN DEFAULT FALSE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for restore_jobs
CREATE INDEX IF NOT EXISTS idx_restore_jobs_status ON restore_jobs(status);
CREATE INDEX IF NOT EXISTS idx_restore_jobs_backup ON restore_jobs(backup_id);
CREATE INDEX IF NOT EXISTS idx_restore_jobs_created_at ON restore_jobs(created_at DESC);

-- Create deployment_history table
CREATE TABLE IF NOT EXISTS deployment_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deployment_id VARCHAR(100) NOT NULL UNIQUE,
    version VARCHAR(50) NOT NULL,
    environment VARCHAR(50) NOT NULL,
    status deployment_status NOT NULL DEFAULT 'pending',
    deployment_type VARCHAR(50) NOT NULL,  -- blue_green, rolling, canary, recreate
    rollback_from_version VARCHAR(50),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    deployed_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for deployment_history
CREATE INDEX IF NOT EXISTS idx_deployment_history_env ON deployment_history(environment);
CREATE INDEX IF NOT EXISTS idx_deployment_history_status ON deployment_history(status);
CREATE INDEX IF NOT EXISTS idx_deployment_history_version ON deployment_history(version);

-- Create release_history table
CREATE TABLE IF NOT EXISTS release_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    release_version VARCHAR(50) NOT NULL UNIQUE,
    release_name VARCHAR(255),
    changelog TEXT,
    migration_version INTEGER,
    rollback_version VARCHAR(50),
    compatibility_matrix JSONB DEFAULT '{}',
    is_stable BOOLEAN DEFAULT FALSE,
    released_at TIMESTAMP WITH TIME ZONE,
    released_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for release_history
CREATE INDEX IF NOT EXISTS idx_release_history_version ON release_history(release_version);
CREATE INDEX IF NOT EXISTS idx_release_history_stable ON release_history(is_stable) WHERE is_stable = TRUE;

-- Create secret_metadata table (metadata only, no actual secrets)
CREATE TABLE IF NOT EXISTS secret_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    secret_name VARCHAR(100) NOT NULL UNIQUE,
    secret_type VARCHAR(50) NOT NULL,  -- database, keycloak, geoserver, emqx, neo4j, nodered
    secret_path VARCHAR(255),  -- Path/reference in secret store
    backend VARCHAR(50) DEFAULT 'env',  -- env, docker_secret, vault, aws_secrets, azure_keyvault
    description TEXT,
    last_rotated_at TIMESTAMP WITH TIME ZONE,
    rotation_required BOOLEAN DEFAULT FALSE,
    rotation_interval_days INTEGER,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for secret_metadata
CREATE INDEX IF NOT EXISTS idx_secret_metadata_type ON secret_metadata(secret_type);
CREATE INDEX IF NOT EXISTS idx_secret_metadata_backend ON secret_metadata(backend);
CREATE INDEX IF NOT EXISTS idx_secret_metadata_rotation ON secret_metadata(rotation_required) WHERE rotation_required = TRUE;

-- Create dr_plans table
CREATE TABLE IF NOT EXISTS dr_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_name VARCHAR(100) NOT NULL UNIQUE,
    plan_type VARCHAR(50) NOT NULL,  -- database_failure, emqx_failure, geoserver_failure, neo4j_failure, nodered_failure, full_outage
    target_rto_minutes INTEGER NOT NULL,  -- Recovery Time Objective
    target_rpo_minutes INTEGER NOT NULL,  -- Recovery Point Objective
    plan_steps JSONB NOT NULL DEFAULT '[]',
    dependencies JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT FALSE,
    last_tested_at TIMESTAMP WITH TIME ZONE,
    last_successful_test BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for dr_plans
CREATE INDEX IF NOT EXISTS idx_dr_plans_type ON dr_plans(plan_type);
CREATE INDEX IF NOT EXISTS idx_dr_plans_active ON dr_plans(is_active) WHERE is_active = TRUE;

-- Create health_probes table
CREATE TABLE IF NOT EXISTS health_probes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    probe_name VARCHAR(100) NOT NULL UNIQUE,
    probe_type probe_type NOT NULL,
    endpoint VARCHAR(255),
    target_service VARCHAR(100),
    check_interval_seconds INTEGER DEFAULT 30,
    timeout_seconds INTEGER DEFAULT 10,
    failure_threshold INTEGER DEFAULT 3,
    success_threshold INTEGER DEFAULT 1,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for health_probes
CREATE INDEX IF NOT EXISTS idx_health_probes_type ON health_probes(probe_type);
CREATE INDEX IF NOT EXISTS idx_health_probes_enabled ON health_probes(is_enabled) WHERE is_enabled = TRUE;

-- Create service_registry table
CREATE TABLE IF NOT EXISTS service_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name VARCHAR(100) NOT NULL UNIQUE,
    service_type VARCHAR(50) NOT NULL,  -- module, adapter, integration
    version VARCHAR(50),
    status VARCHAR(50) DEFAULT 'active',  -- active, inactive, degraded, maintenance
    endpoint VARCHAR(255),
    dependencies JSONB DEFAULT '[]',
    health_check_enabled BOOLEAN DEFAULT TRUE,
    last_health_check TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for service_registry
CREATE INDEX IF NOT EXISTS idx_service_registry_type ON service_registry(service_type);
CREATE INDEX IF NOT EXISTS idx_service_registry_status ON service_registry(status);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_env_profiles_updated_at
    BEFORE UPDATE ON environment_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sys_config_updated_at
    BEFORE UPDATE ON system_configurations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_feature_flags_updated_at
    BEFORE UPDATE ON feature_flags
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_secret_metadata_updated_at
    BEFORE UPDATE ON secret_metadata
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_dr_plans_updated_at
    BEFORE UPDATE ON dr_plans
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_health_probes_updated_at
    BEFORE UPDATE ON health_probes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_service_registry_updated_at
    BEFORE UPDATE ON service_registry
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create view for active feature flags
CREATE OR REPLACE VIEW active_feature_flags AS
SELECT 
    flag_name,
    flag_key,
    status,
    rollout_percentage,
    scheduled_activation,
    scheduled_deactivation
FROM feature_flags
WHERE status = 'active'
   OR (status = 'scheduled' AND scheduled_activation <= NOW())
ORDER BY flag_name;

-- Create view for deployment summary
CREATE OR REPLACE VIEW deployment_summary AS
SELECT 
    environment,
    COUNT(*) as total_deployments,
    COUNT(*) FILTER (WHERE status = 'completed') as successful,
    COUNT(*) FILTER (WHERE status = 'failed') as failed,
    MAX(started_at) as last_deployment
FROM deployment_history
GROUP BY environment;

-- Create view for backup summary
CREATE OR REPLACE VIEW backup_summary AS
SELECT 
    backup_type,
    COUNT(*) as total_backups,
    COUNT(*) FILTER (WHERE status = 'completed') as successful,
    SUM(backup_size_bytes) FILTER (WHERE status = 'completed') as total_size_bytes,
    AVG(duration_seconds) FILTER (WHERE status = 'completed') as avg_duration_seconds,
    MAX(completed_at) as last_backup
FROM backup_jobs
GROUP BY backup_type;

-- Create view for DR plans summary
CREATE OR REPLACE VIEW dr_plans_summary AS
SELECT 
    plan_type,
    COUNT(*) as total_plans,
    COUNT(*) FILTER (WHERE is_active = TRUE) as active_plans,
    COUNT(*) FILTER (WHERE last_successful_test = TRUE) as tested_plans,
    AVG(target_rto_minutes) as avg_rto_minutes,
    AVG(target_rpo_minutes) as avg_rpo_minutes
FROM dr_plans
GROUP BY plan_type;

-- Create view for service health
CREATE OR REPLACE VIEW service_health AS
SELECT 
    service_name,
    service_type,
    version,
    status,
    last_health_check
FROM service_registry
ORDER BY service_name;

COMMENT ON TABLE environment_profiles IS 'Environment and profile configurations';
COMMENT ON TABLE system_configurations IS 'System configuration parameters';
COMMENT ON TABLE feature_flags IS 'Feature flag management';
COMMENT ON TABLE backup_jobs IS 'Backup job tracking';
COMMENT ON TABLE restore_jobs IS 'Restore job tracking';
COMMENT ON TABLE deployment_history IS 'Deployment history tracking';
COMMENT ON TABLE release_history IS 'Release version history';
COMMENT ON TABLE secret_metadata IS 'Secret metadata (no actual secrets)';
COMMENT ON TABLE dr_plans IS 'Disaster recovery plans';
COMMENT ON TABLE health_probes IS 'Health probe configurations';
COMMENT ON TABLE service_registry IS 'Internal service registry';

COMMIT;
