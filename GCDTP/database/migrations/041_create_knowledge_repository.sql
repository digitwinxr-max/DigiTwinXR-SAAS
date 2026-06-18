-- Migration 040: Knowledge Repository Engine
-- Creates tables for structured knowledge organization
-- This is metadata + organization only - NO AI, NO embeddings

BEGIN;

-- Create document_type enum
DO $$ BEGIN
    CREATE TYPE document_type AS ENUM (
        'manual',
        'sop',
        'troubleshooting',
        'adr',
        'report',
        'lesson_learned',
        'reference',
        'external'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create relationship_type enum
DO $$ BEGIN
    CREATE TYPE relationship_type AS ENUM (
        'references',
        'extends',
        'supersedes',
        'related_to'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create knowledge_documents table
CREATE TABLE IF NOT EXISTS knowledge_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    document_type document_type NOT NULL,
    category VARCHAR(100) NOT NULL,
    source VARCHAR(255),
    author VARCHAR(255) NOT NULL,
    summary TEXT,
    tags JSONB DEFAULT '[]'::jsonb,
    external_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create knowledge_references table
CREATE TABLE IF NOT EXISTS knowledge_references (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_document_id UUID NOT NULL REFERENCES knowledge_documents(id) ON DELETE CASCADE,
    target_document_id UUID NOT NULL REFERENCES knowledge_documents(id) ON DELETE CASCADE,
    relationship_type relationship_type NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT different_documents CHECK (source_document_id != target_document_id)
);

-- Create indexes for knowledge_documents
CREATE INDEX IF NOT EXISTS idx_knowledge_title ON knowledge_documents(title);
CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_documents(category);
CREATE INDEX IF NOT EXISTS idx_knowledge_document_type ON knowledge_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_author ON knowledge_documents(author);
CREATE INDEX IF NOT EXISTS idx_knowledge_tags ON knowledge_documents USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_knowledge_created ON knowledge_documents(created_at DESC);

-- Create indexes for knowledge_references
CREATE INDEX IF NOT EXISTS idx_knowledge_ref_source ON knowledge_references(source_document_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_ref_target ON knowledge_references(target_document_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_ref_type ON knowledge_references(relationship_type);

-- Add comments
COMMENT ON TABLE knowledge_documents IS 'Structured knowledge repository - documents are metadata only, NO AI embeddings';
COMMENT ON COLUMN knowledge_documents.tags IS 'Array of tag strings for categorization';
COMMENT ON COLUMN knowledge_documents.external_url IS 'Link to external document (if applicable)';
COMMENT ON TABLE knowledge_references IS 'Document relationships - defines knowledge graph structure';

-- Create view for documents with reference counts
CREATE OR REPLACE VIEW knowledge_documents_with_refs AS
SELECT 
    d.*,
    COUNT(DISTINCT r.source_document_id) FILTER (WHERE r.target_document_id != d.id) as incoming_refs,
    COUNT(DISTINCT r.target_document_id) FILTER (WHERE r.source_document_id != d.id) as outgoing_refs
FROM knowledge_documents d
LEFT JOIN knowledge_references r ON d.id = r.source_document_id OR d.id = r.target_document_id
GROUP BY d.id;

-- Create view for category summary
CREATE OR REPLACE VIEW knowledge_category_summary AS
SELECT 
    category,
    document_type,
    COUNT(*) as document_count
FROM knowledge_documents
GROUP BY category, document_type
ORDER BY category, document_type;

-- Create function to get related documents
CREATE OR REPLACE FUNCTION get_related_documents(doc_id UUID)
RETURNS TABLE (
    related_id UUID,
    related_title VARCHAR(500),
    relationship_type relationship_type
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        kr.target_document_id,
        kd.title,
        kr.relationship_type
    FROM knowledge_references kr
    JOIN knowledge_documents kd ON kr.target_document_id = kd.id
    WHERE kr.source_document_id = doc_id
    
    UNION
    
    SELECT 
        kr.source_document_id,
        kd.title,
        kr.relationship_type
    FROM knowledge_references kr
    JOIN knowledge_documents kd ON kr.source_document_id = kd.id
    WHERE kr.target_document_id = doc_id;
END;
$$ LANGUAGE plpgsql;

-- Create function to search documents
CREATE OR REPLACE FUNCTION search_knowledge_documents(
    search_query TEXT DEFAULT NULL,
    doc_category VARCHAR(100) DEFAULT NULL,
    doc_type document_type DEFAULT NULL,
    search_tags TEXT[] DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    title VARCHAR(500),
    document_type document_type,
    category VARCHAR(100),
    author VARCHAR(255),
    summary TEXT,
    tags JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        kd.id,
        kd.title,
        kd.document_type,
        kd.category,
        kd.author,
        kd.summary,
        kd.tags
    FROM knowledge_documents kd
    WHERE 
        (search_query IS NULL OR 
         kd.title ILIKE '%' || search_query || '%' OR 
         kd.summary ILIKE '%' || search_query || '%')
        AND (doc_category IS NULL OR kd.category = doc_category)
        AND (doc_type IS NULL OR kd.document_type = doc_type)
    ORDER BY kd.created_at DESC;
END;
$$ LANGUAGE plpgsql;

COMMIT;
