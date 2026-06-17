-- Migration 020: Graph Intelligence Layer (Neo4j)
-- Creates graph_projection_jobs, graph_sync_history, graph_query_history, and graph_snapshots tables
-- Maintains backward compatibility

BEGIN;

-- Create projection_status enum
DO $$ BEGIN
    CREATE TYPE projection_status AS ENUM (
        'pending',
        'running',
        'completed',
        'failed',
        'cancelled'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create entity_type enum
DO $$ BEGIN
    CREATE TYPE graph_entity_type AS ENUM (
        'asset',
        'relationship',
        'work_order',
        'document',
        'device',
        'user',
        'organization',
        'timeline_event'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create graph_projection_jobs table
CREATE TABLE IF NOT EXISTS graph_projection_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    entity_type graph_entity_type NOT NULL,
    status projection_status NOT NULL DEFAULT 'pending',
    filters JSONB DEFAULT '{}',
    options JSONB DEFAULT '{}',
    node_count INTEGER,
    relationship_count INTEGER,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    created_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for graph_projection_jobs
CREATE INDEX IF NOT EXISTS idx_projection_jobs_status ON graph_projection_jobs(status);
CREATE INDEX IF NOT EXISTS idx_projection_jobs_entity_type ON graph_projection_jobs(entity_type);
CREATE INDEX IF NOT EXISTS idx_projection_jobs_created_at ON graph_projection_jobs(created_at DESC);

-- Create graph_sync_history table
CREATE TABLE IF NOT EXISTS graph_sync_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    projection_job_id UUID REFERENCES graph_projection_jobs(id) ON DELETE SET NULL,
    sync_type VARCHAR(50) NOT NULL,
    entity_type graph_entity_type NOT NULL,
    entity_id VARCHAR(255),
    operation VARCHAR(20) NOT NULL,  -- 'create', 'update', 'delete'
    status projection_status NOT NULL,
    node_id VARCHAR(255),  -- Neo4j node ID
    relationship_id VARCHAR(255),  -- Neo4j relationship ID
    error_message TEXT,
    synced_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for graph_sync_history
CREATE INDEX IF NOT EXISTS idx_sync_history_job_id ON graph_sync_history(projection_job_id);
CREATE INDEX IF NOT EXISTS idx_sync_history_entity ON graph_sync_history(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_sync_history_synced_at ON graph_sync_history(synced_at DESC);

-- Create graph_query_history table
CREATE TABLE IF NOT EXISTS graph_query_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_type VARCHAR(50) NOT NULL,
    cypher_query TEXT NOT NULL,
    parameters JSONB DEFAULT '{}',
    result_count INTEGER,
    execution_time_ms INTEGER,
    cached BOOLEAN DEFAULT FALSE,
    cache_key VARCHAR(255),
    executed_by VARCHAR(255),
    executed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for graph_query_history
CREATE INDEX IF NOT EXISTS idx_query_history_type ON graph_query_history(query_type);
CREATE INDEX IF NOT EXISTS idx_query_history_executed_at ON graph_query_history(executed_at DESC);
CREATE INDEX IF NOT EXISTS idx_query_history_cache_key ON graph_query_history(cache_key) WHERE cache_key IS NOT NULL;

-- Create graph_snapshots table
CREATE TABLE IF NOT EXISTS graph_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    entity_type graph_entity_type,
    filter_criteria JSONB DEFAULT '{}',
    snapshot_data JSONB,
    node_count INTEGER,
    relationship_count INTEGER,
    created_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for graph_snapshots
CREATE INDEX IF NOT EXISTS idx_snapshots_entity_type ON graph_snapshots(entity_type);
CREATE INDEX IF NOT EXISTS idx_snapshots_created_at ON graph_snapshots(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_snapshots_expires_at ON graph_snapshots(expires_at) WHERE expires_at IS NOT NULL;

-- Create centrality_scores table
CREATE TABLE IF NOT EXISTS centrality_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_id UUID REFERENCES graph_snapshots(id) ON DELETE CASCADE,
    entity_type graph_entity_type NOT NULL,
    entity_id VARCHAR(255) NOT NULL,
    centrality_type VARCHAR(50) NOT NULL,
    score DOUBLE PRECISION NOT NULL,
    rank INTEGER,
    computed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(snapshot_id, entity_type, entity_id, centrality_type)
);

-- Create indexes for centrality_scores
CREATE INDEX IF NOT EXISTS idx_centrality_snapshot ON centrality_scores(snapshot_id);
CREATE INDEX IF NOT EXISTS idx_centrality_entity ON centrality_scores(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_centrality_type ON centrality_scores(centrality_type);
CREATE INDEX IF NOT EXISTS idx_centrality_rank ON centrality_scores(centrality_type, rank);

-- Create dependency_chains table
CREATE TABLE IF NOT EXISTS dependency_chains (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_id UUID REFERENCES graph_snapshots(id) ON DELETE CASCADE,
    chain_type VARCHAR(50) NOT NULL,  -- 'failure_impact', 'cascade', 'dependency'
    start_entity_type graph_entity_type NOT NULL,
    start_entity_id VARCHAR(255) NOT NULL,
    end_entity_type graph_entity_type,
    end_entity_id VARCHAR(255),
    chain_length INTEGER,
    chain_data JSONB NOT NULL,  -- [{entity_type, entity_id, depth}]
    computed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for dependency_chains
CREATE INDEX IF NOT EXISTS idx_chains_snapshot ON dependency_chains(snapshot_id);
CREATE INDEX IF NOT EXISTS idx_chains_type ON dependency_chains(chain_type);
CREATE INDEX IF NOT EXISTS idx_chains_start_entity ON dependency_chains(start_entity_type, start_entity_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_projection_jobs_updated_at
    BEFORE UPDATE ON graph_projection_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create view for projection job summary
CREATE OR REPLACE VIEW projection_job_summary AS
SELECT 
    j.id,
    j.name,
    j.entity_type,
    j.status,
    j.node_count,
    j.relationship_count,
    j.started_at,
    j.completed_at,
    j.created_at,
    j.created_by,
    EXTRACT(EPOCH FROM (COALESCE(j.completed_at, NOW()) - j.started_at)) AS duration_seconds
FROM graph_projection_jobs j;

-- Create view for sync statistics
CREATE OR REPLACE VIEW sync_statistics AS
SELECT 
    entity_type,
    operation,
    COUNT(*) AS operation_count,
    COUNT(*) FILTER (WHERE status = 'completed') AS successful,
    COUNT(*) FILTER (WHERE status = 'failed') AS failed,
    MIN(synced_at) AS first_sync,
    MAX(synced_at) AS last_sync
FROM graph_sync_history
GROUP BY entity_type, operation;

-- Create view for query performance
CREATE OR REPLACE VIEW query_performance AS
SELECT 
    query_type,
    COUNT(*) AS execution_count,
    AVG(execution_time_ms) AS avg_execution_time_ms,
    MIN(execution_time_ms) AS min_execution_time_ms,
    MAX(execution_time_ms) AS max_execution_time_ms,
    AVG(result_count) AS avg_result_count,
    COUNT(*) FILTER (WHERE cached = TRUE) AS cache_hits
FROM graph_query_history
WHERE executed_at > NOW() - INTERVAL '7 days'
GROUP BY query_type;

-- Create view for critical entities
CREATE OR REPLACE VIEW critical_entities AS
SELECT 
    cs.entity_type,
    cs.entity_id,
    cs.centrality_type,
    cs.score,
    cs.rank,
    a.name AS asset_name,
    a.asset_type,
    a.status AS asset_status
FROM centrality_scores cs
LEFT JOIN assets a ON cs.entity_id = a.id::VARCHAR AND cs.entity_type = 'asset'
WHERE cs.snapshot_id = (
    SELECT id FROM graph_snapshots 
    WHERE is_active = TRUE AND entity_type IS NULL 
    ORDER BY created_at DESC LIMIT 1
)
ORDER BY cs.rank ASC NULLS LAST;

COMMENT ON TABLE graph_projection_jobs IS 'Graph projection job tracking';
COMMENT ON TABLE graph_sync_history IS 'Graph sync audit trail';
COMMENT ON TABLE graph_query_history IS 'Graph query execution history';
COMMENT ON TABLE graph_snapshots IS 'Graph snapshot storage';
COMMENT ON TABLE centrality_scores IS 'Computed centrality scores';
COMMENT ON TABLE dependency_chains IS 'Computed dependency chains';

COMMIT;
