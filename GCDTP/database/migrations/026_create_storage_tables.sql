-- Migration 026: Object Storage Layer (MinIO)
-- Creates tables for MinIO object storage management
-- PostgreSQL remains authoritative for metadata

BEGIN;

-- Create enums
DO $$ BEGIN
    CREATE TYPE bucket_status AS ENUM (
        'active',
        'suspended',
        'archived'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE object_status AS ENUM (
        'available',
        'deleted',
        'archived',
        'legal_hold'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE retention_status AS ENUM (
        'active',
        'expired',
        'released'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE upload_status AS ENUM (
        'pending',
        'in_progress',
        'completed',
        'failed',
        'aborted'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create storage_buckets table
CREATE TABLE IF NOT EXISTS storage_buckets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bucket_name VARCHAR(255) NOT NULL UNIQUE,
    bucket_type VARCHAR(50) NOT NULL,  -- documents, attachments, images, cad, bim, pointclouds, rasters, datasets, backups, temporary
    status bucket_status DEFAULT 'active',
    description TEXT,
    max_size_bytes BIGINT,
    max_object_count INTEGER,
    encryption_enabled BOOLEAN DEFAULT FALSE,
    version_enabled BOOLEAN DEFAULT TRUE,
    owner_organization_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for storage_buckets
CREATE INDEX IF NOT EXISTS idx_storage_buckets_name ON storage_buckets(bucket_name);
CREATE INDEX IF NOT EXISTS idx_storage_buckets_type ON storage_buckets(bucket_type);
CREATE INDEX IF NOT EXISTS idx_storage_buckets_status ON storage_buckets(status);
CREATE INDEX IF NOT EXISTS idx_storage_buckets_org ON storage_buckets(owner_organization_id);

-- Create stored_objects table
CREATE TABLE IF NOT EXISTS stored_objects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bucket_id UUID NOT NULL REFERENCES storage_buckets(id) ON DELETE CASCADE,
    object_key VARCHAR(1024) NOT NULL,
    version_id VARCHAR(255),
    content_type VARCHAR(255),
    size_bytes BIGINT NOT NULL DEFAULT 0,
    checksum VARCHAR(128),
    checksum_algorithm VARCHAR(20) DEFAULT 'SHA256',
    status object_status DEFAULT 'available',
    is_latest BOOLEAN DEFAULT TRUE,
    owner_user_id UUID,
    owner_organization_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(bucket_id, object_key, version_id)
);

-- Create indexes for stored_objects
CREATE INDEX IF NOT EXISTS idx_stored_objects_bucket ON stored_objects(bucket_id);
CREATE INDEX IF NOT EXISTS idx_stored_objects_key ON stored_objects(object_key);
CREATE INDEX IF NOT EXISTS idx_stored_objects_status ON stored_objects(status);
CREATE INDEX IF NOT EXISTS idx_stored_objects_owner ON stored_objects(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_stored_objects_org ON stored_objects(owner_organization_id);

-- Create object_versions table
CREATE TABLE IF NOT EXISTS object_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    object_id UUID NOT NULL REFERENCES stored_objects(id) ON DELETE CASCADE,
    version_id VARCHAR(255) NOT NULL,
    size_bytes BIGINT NOT NULL DEFAULT 0,
    checksum VARCHAR(128),
    is_latest BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_by UUID,
    metadata JSONB DEFAULT '{}',
    UNIQUE(object_id, version_id)
);

-- Create indexes for object_versions
CREATE INDEX IF NOT EXISTS idx_object_versions_object ON object_versions(object_id);
CREATE INDEX IF NOT EXISTS idx_object_versions_version ON object_versions(version_id);

-- Create multipart_uploads table
CREATE TABLE IF NOT EXISTS multipart_uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    upload_id VARCHAR(255) NOT NULL UNIQUE,
    bucket_id UUID NOT NULL REFERENCES storage_buckets(id) ON DELETE CASCADE,
    object_key VARCHAR(1024) NOT NULL,
    content_type VARCHAR(255),
    total_size_bytes BIGINT,
    chunk_size_bytes INTEGER,
    total_chunks INTEGER,
    status upload_status DEFAULT 'pending',
    initiated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    initiated_by UUID,
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for multipart_uploads
CREATE INDEX IF NOT EXISTS idx_multipart_uploads_bucket ON multipart_uploads(bucket_id);
CREATE INDEX IF NOT EXISTS idx_multipart_uploads_object ON multipart_uploads(object_key);
CREATE INDEX IF NOT EXISTS idx_multipart_uploads_status ON multipart_uploads(status);

-- Create object_metadata table
CREATE TABLE IF NOT EXISTS object_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    object_id UUID NOT NULL REFERENCES stored_objects(id) ON DELETE CASCADE,
    metadata_key VARCHAR(255) NOT NULL,
    metadata_value TEXT,
    metadata_type VARCHAR(50) DEFAULT 'string',  -- string, number, boolean, json, array
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(object_id, metadata_key)
);

-- Create indexes for object_metadata
CREATE INDEX IF NOT EXISTS idx_object_metadata_object ON object_metadata(object_id);
CREATE INDEX IF NOT EXISTS idx_object_metadata_key ON object_metadata(metadata_key);

-- Create retention_policies table
CREATE TABLE IF NOT EXISTS retention_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_name VARCHAR(255) NOT NULL UNIQUE,
    bucket_id UUID REFERENCES storage_buckets(id) ON DELETE SET NULL,
    retention_days INTEGER,
    retention_mode VARCHAR(50),  -- governance, compliance
    is_default BOOLEAN DEFAULT FALSE,
    status retention_status DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for retention_policies
CREATE INDEX IF NOT EXISTS idx_retention_policies_bucket ON retention_policies(bucket_id);
CREATE INDEX IF NOT EXISTS idx_retention_policies_default ON retention_policies(is_default) WHERE is_default = TRUE;

-- Create storage_registry table
CREATE TABLE IF NOT EXISTS storage_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    registry_key VARCHAR(255) NOT NULL UNIQUE,
    object_id UUID REFERENCES stored_objects(id) ON DELETE SET NULL,
    reference_type VARCHAR(50) NOT NULL,  -- asset, document, work_order, simulation, backup
    reference_id UUID NOT NULL,
    owner_organization_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for storage_registry
CREATE INDEX IF NOT EXISTS idx_storage_registry_object ON storage_registry(object_id);
CREATE INDEX IF NOT EXISTS idx_storage_registry_reference ON storage_registry(reference_type, reference_id);
CREATE INDEX IF NOT EXISTS idx_storage_registry_org ON storage_registry(owner_organization_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_storage_buckets_updated_at
    BEFORE UPDATE ON storage_buckets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stored_objects_updated_at
    BEFORE UPDATE ON stored_objects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_object_metadata_updated_at
    BEFORE UPDATE ON object_metadata
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_retention_policies_updated_at
    BEFORE UPDATE ON retention_policies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_storage_registry_updated_at
    BEFORE UPDATE ON storage_registry
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create views
CREATE OR REPLACE VIEW active_buckets AS
SELECT 
    bucket_name,
    bucket_type,
    status,
    description,
    encryption_enabled,
    version_enabled
FROM storage_buckets
WHERE status = 'active'
ORDER BY bucket_name;

CREATE OR REPLACE VIEW latest_objects AS
SELECT 
    so.object_key,
    so.content_type,
    so.size_bytes,
    so.checksum,
    so.status,
    so.created_at,
    so.owner_organization_id,
    sb.bucket_name
FROM stored_objects so
JOIN storage_buckets sb ON so.bucket_id = sb.id
WHERE so.is_latest = TRUE AND so.status = 'available'
ORDER BY so.object_key;

CREATE OR REPLACE VIEW object_version_history AS
SELECT 
    so.object_key,
    ov.version_id,
    ov.size_bytes,
    ov.checksum,
    ov.is_latest,
    ov.created_at,
    ov.created_by
FROM stored_objects so
JOIN object_versions ov ON so.id = ov.object_id
ORDER BY so.object_key, ov.created_at DESC;

CREATE OR REPLACE VIEW bucket_usage_stats AS
SELECT 
    sb.bucket_name,
    sb.bucket_type,
    COUNT(so.id) as object_count,
    COALESCE(SUM(so.size_bytes), 0) as total_size_bytes,
    MAX(so.created_at) as last_object_added
FROM storage_buckets sb
LEFT JOIN stored_objects so ON sb.id = so.bucket_id AND so.is_latest = TRUE AND so.status = 'available'
GROUP BY sb.bucket_name, sb.bucket_type
ORDER BY sb.bucket_name;

CREATE OR REPLACE VIEW pending_multipart_uploads AS
SELECT 
    mu.upload_id,
    mu.object_key,
    mu.content_type,
    mu.total_size_bytes,
    mu.total_chunks,
    mu.initiated_at,
    mu.expires_at
FROM multipart_uploads mu
WHERE mu.status IN ('pending', 'in_progress')
ORDER BY mu.initiated_at DESC;

COMMENT ON TABLE storage_buckets IS 'Storage bucket definitions';
COMMENT ON TABLE stored_objects IS 'Object metadata (MinIO stores actual files)';
COMMENT ON TABLE object_versions IS 'Object version history';
COMMENT ON TABLE multipart_uploads IS 'Multipart upload tracking';
COMMENT ON TABLE object_metadata IS 'Object custom metadata';
COMMENT ON TABLE retention_policies IS 'Retention policy definitions';
COMMENT ON TABLE storage_registry IS 'Storage reference registry';

COMMIT;
