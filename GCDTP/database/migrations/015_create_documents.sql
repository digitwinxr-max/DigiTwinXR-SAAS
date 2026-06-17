-- Migration 015: Document Management Engine
-- Creates documents, document_versions, and document_tags tables
-- Maintains foreign key relationships to assets and work_orders

BEGIN;

-- Create document_type enum
DO $$ BEGIN
    CREATE TYPE document_type AS ENUM (
        'pdf',
        'image',
        'report',
        'manual',
        'drawing',
        'inspection_form',
        'maintenance_report',
        'video_metadata',
        'certificate',
        'contract',
        'other'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create document_status enum
DO $$ BEGIN
    CREATE TYPE document_status AS ENUM (
        'active',
        'archived',
        'deleted',
        'pending_review',
        'approved'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID REFERENCES assets(id) ON DELETE SET NULL,
    work_order_id UUID REFERENCES work_orders(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    document_type document_type NOT NULL DEFAULT 'other',
    file_name VARCHAR(255),
    mime_type VARCHAR(100),
    file_size BIGINT DEFAULT 0,
    storage_path VARCHAR(500),
    version INTEGER NOT NULL DEFAULT 1,
    status document_status NOT NULL DEFAULT 'active',
    checksum VARCHAR(64),
    uploaded_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    archived_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_session_id VARCHAR(255)
);

-- Create indexes for documents
CREATE INDEX IF NOT EXISTS idx_documents_asset_id ON documents(asset_id);
CREATE INDEX IF NOT EXISTS idx_documents_work_order_id ON documents(work_order_id);
CREATE INDEX IF NOT EXISTS idx_documents_document_type ON documents(document_type);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_documents_uploaded_by ON documents(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_documents_title ON documents(title);

-- Create document_versions table
CREATE TABLE IF NOT EXISTS document_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    file_name VARCHAR(255),
    mime_type VARCHAR(100),
    file_size BIGINT DEFAULT 0,
    storage_path VARCHAR(500),
    checksum VARCHAR(64),
    change_notes TEXT,
    created_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(document_id, version_number)
);

-- Create indexes for document_versions
CREATE INDEX IF NOT EXISTS idx_document_versions_document_id ON document_versions(document_id);
CREATE INDEX IF NOT EXISTS idx_document_versions_created_at ON document_versions(created_at DESC);

-- Create document_tags table
CREATE TABLE IF NOT EXISTS document_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    tag VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(document_id, tag)
);

-- Create indexes for document_tags
CREATE INDEX IF NOT EXISTS idx_document_tags_document_id ON document_tags(document_id);
CREATE INDEX IF NOT EXISTS idx_document_tags_tag ON document_tags(tag);

-- Create document_attachments table for linked files
CREATE TABLE IF NOT EXISTS document_attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    mime_type VARCHAR(100),
    file_size BIGINT DEFAULT 0,
    storage_path VARCHAR(500),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for document_attachments
CREATE INDEX IF NOT EXISTS idx_document_attachments_document_id ON document_attachments(document_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create view for document summary
CREATE OR REPLACE VIEW document_summary AS
SELECT 
    d.id,
    d.asset_id,
    a.name AS asset_name,
    d.work_order_id,
    wo.title AS work_order_title,
    d.title,
    d.description,
    d.document_type,
    d.file_name,
    d.mime_type,
    d.file_size,
    d.version,
    d.status,
    d.uploaded_by,
    d.created_at,
    d.updated_at,
    d.archived_at,
    COUNT(DISTINCT dv.id) AS version_count,
    COUNT(DISTINCT dt.id) AS tag_count,
    CASE 
        WHEN d.deleted_at IS NOT NULL THEN 'deleted'
        WHEN d.archived_at IS NOT NULL THEN 'archived'
        ELSE 'active'
    END AS document_state
FROM documents d
LEFT JOIN assets a ON d.asset_id = a.id
LEFT JOIN work_orders wo ON d.work_order_id = wo.id
LEFT JOIN document_versions dv ON d.id = dv.document_id
LEFT JOIN document_tags dt ON d.id = dt.document_id
GROUP BY d.id, a.name, wo.title, d.title, d.description, d.document_type, d.file_name, d.mime_type, d.file_size, d.version, d.status, d.uploaded_by, d.created_at, d.updated_at, d.archived_at, d.deleted_at;

-- Create view for document search
CREATE OR REPLACE VIEW document_search AS
SELECT 
    d.id,
    d.title,
    d.description,
    d.document_type,
    d.status,
    d.asset_id,
    a.name AS asset_name,
    d.work_order_id,
    wo.title AS work_order_title,
    d.created_at,
    d.updated_at,
    ARRAY_AGG(DISTINCT dt.tag) FILTER (WHERE dt.tag IS NOT NULL) AS tags,
    d.metadata
FROM documents d
LEFT JOIN assets a ON d.asset_id = a.id
LEFT JOIN work_orders wo ON d.work_order_id = wo.id
LEFT JOIN document_tags dt ON d.id = dt.document_id
WHERE d.deleted_at IS NULL
GROUP BY d.id, a.name, wo.title, d.title, d.description, d.document_type, d.status, d.asset_id, d.work_order_id, d.created_at, d.updated_at, d.metadata;

COMMENT ON TABLE documents IS 'Asset-centric document management';
COMMENT ON TABLE document_versions IS 'Version history for documents';
COMMENT ON TABLE document_tags IS 'Tags for document categorization';
COMMENT ON TABLE document_attachments IS 'Additional file attachments for documents';

COMMIT;
