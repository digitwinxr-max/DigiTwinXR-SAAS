-- Migration 047: Cognitive Twin Engine
-- Convergence layer - aggregates context from all platform engines
-- ADVISORY ONLY - NO automation, NO actions, NO autonomous decisions

BEGIN;

-- Create source_type enum
DO $$ BEGIN
    CREATE TYPE source_type AS ENUM (
        'semantic',
        'timeline',
        'logbook',
        'knowledge',
        'rag',
        'prediction',
        'root_cause',
        'agent',
        'health',
        'event'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create cognitive_sessions table
CREATE TABLE IF NOT EXISTS cognitive_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    asset_id UUID REFERENCES assets(id),
    user_id VARCHAR(255),
    context_summary TEXT,
    query_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create cognitive_queries table
CREATE TABLE IF NOT EXISTS cognitive_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES cognitive_sessions(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    answer TEXT,
    confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1),
    explanation TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create cognitive_context table
CREATE TABLE IF NOT EXISTS cognitive_context (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_id UUID NOT NULL REFERENCES cognitive_queries(id) ON DELETE CASCADE,
    source_type source_type NOT NULL,
    reference_id TEXT,
    weight FLOAT NOT NULL CHECK (weight >= 0 AND weight <= 1),
    summary TEXT NOT NULL,
    detail TEXT,
    relevance_score FLOAT CHECK (relevance_score >= 0 AND relevance_score <= 1),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for cognitive_sessions
CREATE INDEX IF NOT EXISTS idx_cog_session_asset ON cognitive_sessions(asset_id);
CREATE INDEX IF NOT EXISTS idx_cog_session_user ON cognitive_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_cog_session_date ON cognitive_sessions(created_at DESC);

-- Create indexes for cognitive_queries
CREATE INDEX IF NOT EXISTS idx_cog_query_session ON cognitive_queries(session_id);
CREATE INDEX IF NOT EXISTS idx_cog_query_date ON cognitive_queries(created_at DESC);

-- Create indexes for cognitive_context
CREATE INDEX IF NOT EXISTS idx_cog_context_query ON cognitive_context(query_id);
CREATE INDEX IF NOT EXISTS idx_cog_context_source ON cognitive_context(source_type);
CREATE INDEX IF NOT EXISTS idx_cog_context_weight ON cognitive_context(weight DESC);

-- Create views for cognitive insights
CREATE OR REPLACE VIEW cognitive_insights AS
SELECT 
    cq.id as query_id,
    cq.session_id,
    cs.name as session_name,
    cs.asset_id,
    cq.question,
    cq.answer,
    cq.confidence,
    cq.explanation,
    cq.created_at,
    COUNT(cc.id) as context_count,
    ARRAY_AGG(cc.source_type) as sources,
    ARRAY_AGG(cc.weight ORDER BY cc.weight DESC) as weights
FROM cognitive_queries cq
JOIN cognitive_sessions cs ON cq.session_id = cs.id
LEFT JOIN cognitive_context cc ON cq.id = cc.query_id
GROUP BY cq.id, cs.name, cs.asset_id, cq.question, cq.answer, cq.confidence, cq.explanation, cq.created_at;

-- Create view for context aggregation
CREATE OR REPLACE VIEW context_aggregation AS
SELECT 
    cq.id as query_id,
    cq.question,
    cc.source_type,
    COUNT(*) as source_count,
    AVG(cc.weight) as avg_weight,
    AVG(cc.relevance_score) as avg_relevance,
    STRING_AGG(SUBSTRING(cc.summary, 1, 100), ' | ') as context_snippets
FROM cognitive_queries cq
JOIN cognitive_context cc ON cq.id = cc.query_id
GROUP BY cq.id, cq.question, cc.source_type;

-- Create view for session analytics
CREATE OR REPLACE VIEW session_analytics AS
SELECT 
    cs.id,
    cs.name,
    cs.asset_id,
    cs.user_id,
    cs.query_count,
    cs.context_summary,
    cs.created_at,
    COUNT(DISTINCT cq.id) as total_queries,
    AVG(cq.confidence) as avg_confidence,
    COUNT(DISTINCT cc.source_type) as unique_sources,
    COUNT(cc.id) as total_contexts
FROM cognitive_sessions cs
LEFT JOIN cognitive_queries cq ON cs.id = cq.session_id
LEFT JOIN cognitive_context cc ON cq.id = cc.query_id
GROUP BY cs.id;

-- Create function to merge context from multiple sources
CREATE OR REPLACE FUNCTION merge_context_sources(query_uuid UUID)
RETURNS TABLE (
    source_type source_type,
    combined_summary TEXT,
    total_weight FLOAT,
    context_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cc.source_type,
        STRING_AGG(SUBSTRING(cc.summary, 1, 200), E'\n---\n') as combined_summary,
        SUM(cc.weight) as total_weight,
        COUNT(*) as context_count
    FROM cognitive_context cc
    WHERE cc.query_id = query_uuid
    GROUP BY cc.source_type
    ORDER BY SUM(cc.weight) DESC;
END;
$$ LANGUAGE plpgsql;

-- Create function to calculate confidence from context
CREATE OR REPLACE FUNCTION calculate_cognitive_confidence(
    context_count INTEGER,
    avg_weight FLOAT,
    unique_sources INTEGER,
    avg_relevance FLOAT
)
RETURNS FLOAT AS $$
DECLARE
    coverage_score FLOAT;
    weight_score FLOAT;
    diversity_score FLOAT;
    relevance_score FLOAT;
BEGIN
    -- Coverage: more context = higher confidence (up to 40%)
    coverage_score := LEAST(context_count * 0.05, 0.4);
    
    -- Weight: higher weights = higher confidence (up to 30%)
    weight_score := LEAST(avg_weight * 0.3, 0.3);
    
    -- Diversity: more source types = higher confidence (up to 15%)
    diversity_score := LEAST(unique_sources * 0.05, 0.15);
    
    -- Relevance: higher relevance = higher confidence (up to 15%)
    relevance_score := LEAST(avg_relevance * 0.15, 0.15);
    
    RETURN LEAST(GREATEST(coverage_score + weight_score + diversity_score + relevance_score, 0), 1);
END;
$$ LANGUAGE plpgsql;

-- Create function to rank context sources
CREATE OR REPLACE FUNCTION rank_context_sources(query_uuid UUID)
RETURNS TABLE (
    source_type source_type,
    total_weight FLOAT,
    context_count INTEGER,
    rank INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cc.source_type,
        SUM(cc.weight) as total_weight,
        COUNT(*) as context_count,
        ROW_NUMBER() OVER (ORDER BY SUM(cc.weight) DESC)::INTEGER as rank
    FROM cognitive_context cc
    WHERE cc.query_id = query_uuid
    GROUP BY cc.source_type;
END;
$$ LANGUAGE plpgsql;

-- Add comments
COMMENT ON TABLE cognitive_sessions IS 'ADVISORY ONLY - Cognitive Twin sessions, NO automation';
COMMENT ON TABLE cognitive_queries IS 'Questions and answers in cognitive sessions';
COMMENT ON TABLE cognitive_context IS 'Aggregated context from all platform engines';
COMMENT ON FUNCTION merge_context_sources IS 'Merge context from multiple sources';
COMMENT ON FUNCTION calculate_cognitive_confidence IS 'Calculate confidence from context metrics';
COMMENT ON FUNCTION rank_context_sources IS 'Rank context sources by weight';

COMMIT;
