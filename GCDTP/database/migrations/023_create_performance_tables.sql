-- Migration 023: Performance & Scaling Layer
-- Creates performance-related tables for caching, rate limiting, bulk operations, and API versioning
-- Maintains backward compatibility

BEGIN;

-- Create cache_entries table
CREATE TABLE IF NOT EXISTS cache_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cache_key VARCHAR(500) NOT NULL,
    cache_type VARCHAR(50) NOT NULL DEFAULT 'memory',  -- memory, query, snapshot, ontology, graph, metrics
    value BYTEA,
    value_text TEXT,
    ttl_seconds INTEGER,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    accessed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    access_count INTEGER DEFAULT 0,
    hits INTEGER DEFAULT 0,
    misses INTEGER DEFAULT 0,
    UNIQUE(cache_type, cache_key)
);

-- Create indexes for cache_entries
CREATE INDEX IF NOT EXISTS idx_cache_entries_key ON cache_entries(cache_key);
CREATE INDEX IF NOT EXISTS idx_cache_entries_type ON cache_entries(cache_type);
CREATE INDEX IF NOT EXISTS idx_cache_entries_accessed ON cache_entries(accessed_at);
CREATE INDEX IF NOT EXISTS idx_cache_entries_created ON cache_entries(created_at);

-- Create rate_limit_rules table
CREATE TABLE IF NOT EXISTS rate_limit_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name VARCHAR(100) NOT NULL,
    limit_type VARCHAR(50) NOT NULL,  -- user, organization, global
    target_id VARCHAR(255),  -- user_id or org_id, NULL for global
    requests_per_minute INTEGER NOT NULL DEFAULT 60,
    requests_per_hour INTEGER,
    requests_per_day INTEGER,
    burst_limit INTEGER DEFAULT 10,
    algorithm VARCHAR(50) DEFAULT 'token_bucket',  -- token_bucket, sliding_window, fixed_window
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(limit_type, target_id)
);

-- Create indexes for rate_limit_rules
CREATE INDEX IF NOT EXISTS idx_rate_limit_rules_type ON rate_limit_rules(limit_type);
CREATE INDEX IF NOT EXISTS idx_rate_limit_rules_active ON rate_limit_rules(is_active);

-- Create rate_limit_violations table
CREATE TABLE IF NOT EXISTS rate_limit_violations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_id UUID REFERENCES rate_limit_rules(id) ON DELETE SET NULL,
    client_ip VARCHAR(50),
    user_id VARCHAR(255),
    organization_id VARCHAR(255),
    request_count INTEGER,
    limit_exceeded INTEGER,
    violated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for rate_limit_violations
CREATE INDEX IF NOT EXISTS idx_rate_limit_violations_user ON rate_limit_violations(user_id);
CREATE INDEX IF NOT EXISTS idx_rate_limit_violations_org ON rate_limit_violations(organization_id);
CREATE INDEX IF NOT EXISTS idx_rate_limit_violations_time ON rate_limit_violations(violated_at DESC);

-- Create bulk_jobs table
CREATE TABLE IF NOT EXISTS bulk_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type VARCHAR(50) NOT NULL,  -- create, update, delete
    entity_type VARCHAR(50) NOT NULL,  -- asset, document, work_order
    status VARCHAR(50) NOT NULL DEFAULT 'pending',  -- pending, running, completed, failed, cancelled
    total_items INTEGER DEFAULT 0,
    processed_items INTEGER DEFAULT 0,
    failed_items INTEGER DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for bulk_jobs
CREATE INDEX IF NOT EXISTS idx_bulk_jobs_status ON bulk_jobs(status);
CREATE INDEX IF NOT EXISTS idx_bulk_jobs_type ON bulk_jobs(job_type);
CREATE INDEX IF NOT EXISTS idx_bulk_jobs_created_at ON bulk_jobs(created_at DESC);

-- Create bulk_job_items table
CREATE TABLE IF NOT EXISTS bulk_job_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES bulk_jobs(id) ON DELETE CASCADE,
    item_id VARCHAR(255) NOT NULL,
    item_data JSONB,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',  -- pending, processing, completed, failed
    error_message TEXT,
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for bulk_job_items
CREATE INDEX IF NOT EXISTS idx_bulk_job_items_job ON bulk_job_items(job_id);
CREATE INDEX IF NOT EXISTS idx_bulk_job_items_status ON bulk_job_items(status);

-- Create query_statistics table
CREATE TABLE IF NOT EXISTS query_statistics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_hash VARCHAR(64) NOT NULL,
    query_template TEXT NOT NULL,
    execution_count INTEGER DEFAULT 0,
    total_time_ms BIGINT DEFAULT 0,
    avg_time_ms INTEGER DEFAULT 0,
    min_time_ms INTEGER DEFAULT 0,
    max_time_ms INTEGER DEFAULT 0,
    last_executed_at TIMESTAMP WITH TIME ZONE,
    last_execution_time_ms INTEGER,
    estimated_cost INTEGER,
    index_hints TEXT,
    slow_query BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for query_statistics
CREATE INDEX IF NOT EXISTS idx_query_stats_hash ON query_statistics(query_hash);
CREATE INDEX IF NOT EXISTS idx_query_stats_slow ON query_statistics(slow_query) WHERE slow_query = TRUE;
CREATE INDEX IF NOT EXISTS idx_query_stats_avg_time ON query_statistics(avg_time_ms DESC);

-- Create api_versions table
CREATE TABLE IF NOT EXISTS api_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version VARCHAR(20) NOT NULL UNIQUE,
    display_name VARCHAR(100),
    status VARCHAR(50) NOT NULL DEFAULT 'active',  -- active, deprecated, sunset
    release_date DATE,
    sunset_date DATE,
    migration_guide TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for api_versions
CREATE INDEX IF NOT EXISTS idx_api_versions_status ON api_versions(status);
CREATE INDEX IF NOT EXISTS idx_api_versions_default ON api_versions(is_default) WHERE is_default = TRUE;

-- Create performance_profiles table
CREATE TABLE IF NOT EXISTS performance_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_name VARCHAR(100) NOT NULL UNIQUE,
    cache_enabled BOOLEAN DEFAULT TRUE,
    cache_ttl_seconds INTEGER DEFAULT 300,
    max_connections INTEGER DEFAULT 20,
    query_timeout_seconds INTEGER DEFAULT 30,
    batch_size INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for performance_profiles
CREATE INDEX IF NOT EXISTS idx_perf_profiles_active ON performance_profiles(is_active) WHERE is_active = TRUE;

-- Create connection_pool_stats table
CREATE TABLE IF NOT EXISTS connection_pool_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pool_name VARCHAR(100) NOT NULL,  -- postgresql, neo4j, geoserver, emqx
    total_connections INTEGER DEFAULT 0,
    active_connections INTEGER DEFAULT 0,
    idle_connections INTEGER DEFAULT 0,
    waiting_requests INTEGER DEFAULT 0,
    max_connections INTEGER DEFAULT 0,
    avg_wait_time_ms INTEGER DEFAULT 0,
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for connection_pool_stats
CREATE INDEX IF NOT EXISTS idx_conn_pool_stats_name ON connection_pool_stats(pool_name);
CREATE INDEX IF NOT EXISTS idx_conn_pool_stats_recorded ON connection_pool_stats(recorded_at DESC);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_rate_limit_rules_updated_at
    BEFORE UPDATE ON rate_limit_rules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_query_statistics_updated_at
    BEFORE UPDATE ON query_statistics
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_performance_profiles_updated_at
    BEFORE UPDATE ON performance_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create view for cache hit rates
CREATE OR REPLACE VIEW cache_hit_rates AS
SELECT 
    cache_type,
    SUM(hits) as total_hits,
    SUM(misses) as total_misses,
    SUM(hits + misses) as total_requests,
    CASE 
        WHEN SUM(hits + misses) > 0 
        THEN ROUND(SUM(hits)::NUMERIC / SUM(hits + misses) * 100, 2)
        ELSE 0 
    END as hit_rate_percent,
    MAX(accessed_at) as last_accessed
FROM cache_entries
GROUP BY cache_type;

-- Create view for bulk job progress
CREATE OR REPLACE VIEW bulk_job_progress AS
SELECT 
    id,
    job_type,
    entity_type,
    status,
    total_items,
    processed_items,
    failed_items,
    ROUND(processed_items::NUMERIC / NULLIF(total_items, 0) * 100, 2) as progress_percent,
    CASE 
        WHEN status = 'completed' THEN EXTRACT(EPOCH FROM (completed_at - started_at))
        WHEN started_at IS NOT NULL THEN EXTRACT(EPOCH FROM (NOW() - started_at))
        ELSE NULL
    END as elapsed_seconds
FROM bulk_jobs
ORDER BY created_at DESC;

-- Create view for slow queries
CREATE OR REPLACE VIEW slow_queries AS
SELECT 
    query_hash,
    query_template,
    execution_count,
    avg_time_ms,
    max_time_ms,
    last_executed_at,
    last_execution_time_ms,
    estimated_cost
FROM query_statistics
WHERE slow_query = TRUE
ORDER BY avg_time_ms DESC
LIMIT 50;

-- Create view for rate limit summary
CREATE OR REPLACE VIEW rate_limit_summary AS
SELECT 
    limit_type,
    COUNT(*) as rule_count,
    SUM(requests_per_minute) as total_rpm,
    COUNT(*) FILTER (WHERE is_active = TRUE) as active_rules
FROM rate_limit_rules
GROUP BY limit_type;

COMMENT ON TABLE cache_entries IS 'Performance cache storage';
COMMENT ON TABLE rate_limit_rules IS 'Rate limiting configuration';
COMMENT ON TABLE bulk_jobs IS 'Bulk operation job tracking';
COMMENT ON TABLE query_statistics IS 'Query performance tracking';
COMMENT ON TABLE api_versions IS 'API version management';
COMMENT ON TABLE performance_profiles IS 'Performance profile configuration';
COMMENT ON TABLE connection_pool_stats IS 'Connection pool monitoring';

COMMIT;
