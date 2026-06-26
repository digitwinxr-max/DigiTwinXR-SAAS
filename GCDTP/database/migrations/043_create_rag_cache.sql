-- Migration 043: RAG Engine (Retrieval-Augmented Generation)
-- Creates tables for RAG query audit and context caching
-- These are audit records only - NO operational writes

BEGIN;

-- Create source_type enum
DO $$ BEGIN
    CREATE TYPE rag_source_type AS ENUM (
        'semantic',
        'health',
        'event',
        'timeline',
        'logbook',
        'knowledge',
        'asset',
        'sensor'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create rag_queries table (audit only)
CREATE TABLE IF NOT EXISTS rag_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES copilot_sessions(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create rag_context_chunks table (audit only)
CREATE TABLE IF NOT EXISTS rag_context_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_id UUID NOT NULL REFERENCES rag_queries(id) ON DELETE CASCADE,
    source_type rag_source_type NOT NULL,
    source_id UUID,
    content TEXT NOT NULL,
    relevance_score FLOAT NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create rag_answers table (audit only)
CREATE TABLE IF NOT EXISTS rag_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_id UUID NOT NULL REFERENCES rag_queries(id) ON DELETE CASCADE,
    answer TEXT NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for rag_queries
CREATE INDEX IF NOT EXISTS idx_rag_queries_session ON rag_queries(session_id);
CREATE INDEX IF NOT EXISTS idx_rag_queries_created ON rag_queries(created_at DESC);

-- Create indexes for rag_context_chunks
CREATE INDEX IF NOT EXISTS idx_rag_chunks_query ON rag_context_chunks(query_id);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_source_type ON rag_context_chunks(source_type);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_relevance ON rag_context_chunks(relevance_score DESC);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_source ON rag_context_chunks(source_id);

-- Create indexes for rag_answers
CREATE INDEX IF NOT EXISTS idx_rag_answers_query ON rag_answers(query_id);
CREATE INDEX IF NOT EXISTS idx_rag_answers_model ON rag_answers(model_name);

-- Add comments
COMMENT ON TABLE rag_queries IS 'RAG query audit - stores user queries for traceability';
COMMENT ON TABLE rag_context_chunks IS 'RAG context audit - stores retrieved context chunks for explainability';
COMMENT ON TABLE rag_answers IS 'RAG answer audit - stores generated answers for accountability';
COMMENT ON COLUMN rag_context_chunks.relevance_score IS 'Score 0-1 indicating chunk relevance';

-- Create view for RAG session summaries
CREATE OR REPLACE VIEW rag_session_summary AS
SELECT 
    rq.session_id,
    COUNT(DISTINCT rq.id) as query_count,
    COUNT(DISTINCT rc.id) as chunk_count,
    COUNT(DISTINCT ra.id) as answer_count,
    MAX(rq.created_at) as last_query_at
FROM rag_queries rq
LEFT JOIN rag_context_chunks rc ON rq.id = rc.query_id
LEFT JOIN rag_answers ra ON rq.id = ra.query_id
GROUP BY rq.session_id;

-- Create function to get chunks by query
CREATE OR REPLACE FUNCTION get_rag_chunks_by_type(query_uuid UUID)
RETURNS TABLE (
    source_type rag_source_type,
    chunk_count BIGINT,
    avg_relevance FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        rc.source_type,
        COUNT(*) as chunk_count,
        AVG(rc.relevance_score) as avg_relevance
    FROM rag_context_chunks rc
    WHERE rc.query_id = query_uuid
    GROUP BY rc.source_type
    ORDER BY avg_relevance DESC;
END;
$$ LANGUAGE plpgsql;

COMMIT;
