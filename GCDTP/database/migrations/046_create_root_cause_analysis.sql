-- Migration 046: Root Cause Analysis Engine
-- READ ONLY engine - explains WHY failures occurred
-- NO automation, NO event modification, NO work orders

BEGIN;

-- Create analysis_type enum
DO $$ BEGIN
    CREATE TYPE analysis_type AS ENUM (
        'failure',
        'health_degradation',
        'dependency_chain',
        'event_sequence'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create factor_type enum
DO $$ BEGIN
    CREATE TYPE factor_type AS ENUM (
        'measurement',
        'event',
        'health',
        'relationship',
        'timeline',
        'logbook',
        'knowledge'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create root_cause_analysis table
CREATE TABLE IF NOT EXISTS root_cause_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID NOT NULL REFERENCES assets(id),
    event_id UUID REFERENCES events(id),
    analysis_type analysis_type NOT NULL,
    probable_cause TEXT NOT NULL,
    confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    summary TEXT,
    impacted_assets UUID[] DEFAULT '{}',
    root_assets UUID[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create cause_factor table
CREATE TABLE IF NOT EXISTS cause_factor (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES root_cause_analysis(id) ON DELETE CASCADE,
    factor_type factor_type NOT NULL,
    reference_id TEXT,
    weight FLOAT NOT NULL CHECK (weight >= 0 AND weight <= 1),
    description TEXT NOT NULL,
    evidence TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create cause_chain table
CREATE TABLE IF NOT EXISTS cause_chain (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES root_cause_analysis(id) ON DELETE CASCADE,
    depth INTEGER NOT NULL CHECK (depth >= 0),
    source_asset_id UUID NOT NULL REFERENCES assets(id),
    target_asset_id UUID NOT NULL REFERENCES assets(id),
    relationship_type VARCHAR(100),
    description TEXT,
    propagation_time_seconds INTEGER,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for root_cause_analysis
CREATE INDEX IF NOT EXISTS idx_rca_asset ON root_cause_analysis(asset_id);
CREATE INDEX IF NOT EXISTS idx_rca_event ON root_cause_analysis(event_id);
CREATE INDEX IF NOT EXISTS idx_rca_type ON root_cause_analysis(analysis_type);
CREATE INDEX IF NOT EXISTS idx_rca_confidence ON root_cause_analysis(confidence DESC);
CREATE INDEX IF NOT EXISTS idx_rca_date ON root_cause_analysis(created_at DESC);

-- Create indexes for cause_factor
CREATE INDEX IF NOT EXISTS idx_factor_analysis ON cause_factor(analysis_id);
CREATE INDEX IF NOT EXISTS idx_factor_type ON cause_factor(factor_type);
CREATE INDEX IF NOT EXISTS idx_factor_weight ON cause_factor(weight DESC);

-- Create indexes for cause_chain
CREATE INDEX IF NOT EXISTS idx_chain_analysis ON cause_chain(analysis_id);
CREATE INDEX IF NOT EXISTS idx_chain_depth ON cause_chain(depth);
CREATE INDEX IF NOT EXISTS idx_chain_source ON cause_chain(source_asset_id);
CREATE INDEX IF NOT EXISTS idx_chain_target ON cause_chain(target_asset_id);

-- Create views for RCA summaries
CREATE OR REPLACE VIEW rca_high_confidence AS
SELECT 
    rca.id,
    rca.asset_id,
    a.name as asset_name,
    rca.analysis_type,
    rca.probable_cause,
    rca.confidence,
    rca.summary,
    rca.created_at,
    COUNT(cf.id) as factor_count,
    COUNT(cc.id) as chain_count
FROM root_cause_analysis rca
LEFT JOIN cause_factor cf ON rca.id = cf.analysis_id
LEFT JOIN cause_chain cc ON rca.id = cc.analysis_id
LEFT JOIN assets a ON rca.asset_id = a.id
WHERE rca.confidence >= 0.7
GROUP BY rca.id, a.name;

-- Create view for asset RCA history
CREATE OR REPLACE VIEW asset_rca_history AS
SELECT 
    asset_id,
    a.name as asset_name,
    COUNT(*) as analysis_count,
    AVG(confidence) as avg_confidence,
    MAX(confidence) as max_confidence,
    ARRAY_AGG(DISTINCT analysis_type) as analysis_types,
    MIN(rca.created_at) as first_analysis,
    MAX(rca.created_at) as last_analysis
FROM root_cause_analysis rca
JOIN assets a ON rca.asset_id = a.id
GROUP BY asset_id, a.name;

-- Create function for factor ranking
CREATE OR REPLACE FUNCTION rank_factors(analysis_uuid UUID)
RETURNS TABLE (
    factor_id UUID,
    factor_type factor_type,
    description TEXT,
    weight FLOAT,
    rank INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cf.id,
        cf.factor_type,
        cf.description,
        cf.weight,
        ROW_NUMBER() OVER (ORDER BY cf.weight DESC)::INTEGER as rank
    FROM cause_factor cf
    WHERE cf.analysis_id = analysis_uuid
    ORDER BY cf.weight DESC;
END;
$$ LANGUAGE plpgsql;

-- Create function for chain reconstruction
CREATE OR REPLACE FUNCTION reconstruct_chain(analysis_uuid UUID)
RETURNS TABLE (
    depth INTEGER,
    source_name TEXT,
    target_name TEXT,
    relationship_type VARCHAR,
    description TEXT,
    propagation_time INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cc.depth,
        sa.name as source_name,
        ta.name as target_name,
        cc.relationship_type,
        cc.description,
        cc.propagation_time_seconds
    FROM cause_chain cc
    JOIN assets sa ON cc.source_asset_id = sa.id
    JOIN assets ta ON cc.target_asset_id = ta.id
    WHERE cc.analysis_id = analysis_uuid
    ORDER BY cc.depth ASC;
END;
$$ LANGUAGE plpgsql;

-- Create function for confidence calculation
CREATE OR REPLACE FUNCTION calculate_confidence(
    factor_count INTEGER,
    avg_factor_weight FLOAT,
    chain_depth INTEGER,
    evidence_count INTEGER
)
RETURNS FLOAT AS $$
DECLARE
    factor_score FLOAT;
    chain_score FLOAT;
    evidence_score FLOAT;
    total_score FLOAT;
BEGIN
    -- Factor contribution (up to 40%)
    factor_score := LEAST(factor_count * 0.1, 0.4) * avg_factor_weight;
    
    -- Chain depth contribution (up to 30%)
    chain_score := LEAST(chain_depth * 0.1, 0.3);
    
    -- Evidence contribution (up to 30%)
    evidence_score := LEAST(evidence_count * 0.1, 0.3);
    
    -- Total confidence
    total_score := factor_score + chain_score + evidence_score;
    
    RETURN LEAST(GREATEST(total_score, 0), 1);
END;
$$ LANGUAGE plpgsql;

-- Add comments
COMMENT ON TABLE root_cause_analysis IS 'READ ONLY - Root Cause Analysis records';
COMMENT ON TABLE cause_factor IS 'Contributing factors for RCA';
COMMENT ON TABLE cause_chain IS 'Causal chain of asset dependencies';
COMMENT ON FUNCTION rank_factors IS 'Rank factors by weight for an analysis';
COMMENT ON FUNCTION reconstruct_chain IS 'Reconstruct causal chain with asset names';
COMMENT ON FUNCTION calculate_confidence IS 'Calculate confidence score based on factors and evidence';

COMMIT;
