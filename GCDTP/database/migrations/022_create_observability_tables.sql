-- Migration 022: Observability & Diagnostics Layer
-- Creates observability tables for request tracing, health monitoring, and diagnostics
-- Maintains backward compatibility

BEGIN;

-- Create error_severity enum
DO $$ BEGIN
    CREATE TYPE error_severity AS ENUM (
        'debug',
        'info',
        'warning',
        'error',
        'critical'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create health_status enum
DO $$ BEGIN
    CREATE TYPE health_status AS ENUM (
        'healthy',
        'degraded',
        'unhealthy',
        'unknown'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create trace_sessions table
CREATE TABLE IF NOT EXISTS trace_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trace_id VARCHAR(255) NOT NULL,
    request_id VARCHAR(255),
    correlation_id VARCHAR(255),
    parent_request_id VARCHAR(255),
    service_name VARCHAR(100) DEFAULT 'gcdtp',
    operation_name VARCHAR(255),
    start_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,
    status VARCHAR(50),
    user_id VARCHAR(255),
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for trace_sessions
CREATE INDEX IF NOT EXISTS idx_trace_sessions_trace_id ON trace_sessions(trace_id);
CREATE INDEX IF NOT EXISTS idx_trace_sessions_request_id ON trace_sessions(request_id);
CREATE INDEX IF NOT EXISTS idx_trace_sessions_correlation_id ON trace_sessions(correlation_id);
CREATE INDEX IF NOT EXISTS idx_trace_sessions_start_time ON trace_sessions(start_time DESC);

-- Create system_metrics table
CREATE TABLE IF NOT EXISTS system_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    metric_unit VARCHAR(50),
    tags JSONB DEFAULT '{}',
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for system_metrics
CREATE INDEX IF NOT EXISTS idx_system_metrics_name ON system_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_system_metrics_recorded_at ON system_metrics(recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_system_metrics_tags ON system_metrics USING GIN(tags);

-- Create health_checks table
CREATE TABLE IF NOT EXISTS health_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    check_name VARCHAR(100) NOT NULL,
    component VARCHAR(100) NOT NULL,
    status health_status NOT NULL DEFAULT 'unknown',
    message TEXT,
    response_time_ms INTEGER,
    details JSONB DEFAULT '{}',
    checked_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(component, check_name)
);

-- Create indexes for health_checks
CREATE INDEX IF NOT EXISTS idx_health_checks_component ON health_checks(component);
CREATE INDEX IF NOT EXISTS idx_health_checks_status ON health_checks(status);
CREATE INDEX IF NOT EXISTS idx_health_checks_checked_at ON health_checks(checked_at DESC);

-- Create diagnostic_events table
CREATE TABLE IF NOT EXISTS diagnostic_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL,
    severity error_severity NOT NULL DEFAULT 'info',
    source VARCHAR(100) NOT NULL,
    trace_id VARCHAR(255),
    request_id VARCHAR(255),
    correlation_id VARCHAR(255),
    message TEXT NOT NULL,
    context JSONB DEFAULT '{}',
    recommendations JSONB DEFAULT '[]',
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for diagnostic_events
CREATE INDEX IF NOT EXISTS idx_diagnostic_events_type ON diagnostic_events(event_type);
CREATE INDEX IF NOT EXISTS idx_diagnostic_events_severity ON diagnostic_events(severity);
CREATE INDEX IF NOT EXISTS idx_diagnostic_events_trace_id ON diagnostic_events(trace_id);
CREATE INDEX IF NOT EXISTS idx_diagnostic_events_created_at ON diagnostic_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_diagnostic_events_resolved ON diagnostic_events(resolved) WHERE NOT resolved;

-- Create error_registry table
CREATE TABLE IF NOT EXISTS error_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    error_code VARCHAR(50) NOT NULL UNIQUE,
    error_name VARCHAR(255) NOT NULL,
    severity error_severity NOT NULL DEFAULT 'error',
    category VARCHAR(100) NOT NULL,
    description TEXT,
    recovery_suggestions JSONB DEFAULT '[]',
    trace_link_template VARCHAR(500),
    http_status_code INTEGER,
    is_retryable BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for error_registry
CREATE INDEX IF NOT EXISTS idx_error_registry_code ON error_registry(error_code);
CREATE INDEX IF NOT EXISTS idx_error_registry_severity ON error_registry(severity);
CREATE INDEX IF NOT EXISTS idx_error_registry_category ON error_registry(category);

-- Create performance_counters table
CREATE TABLE IF NOT EXISTS performance_counters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    counter_name VARCHAR(100) NOT NULL,
    counter_value BIGINT NOT NULL DEFAULT 0,
    counter_type VARCHAR(50) DEFAULT 'gauge',  -- gauge, counter, histogram
    tags JSONB DEFAULT '{}',
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(counter_name, tags)
);

-- Create indexes for performance_counters
CREATE INDEX IF NOT EXISTS idx_performance_counters_name ON performance_counters(counter_name);
CREATE INDEX IF NOT EXISTS idx_performance_counters_updated_at ON performance_counters(updated_at DESC);

-- Create request_logs table
CREATE TABLE IF NOT EXISTS request_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id VARCHAR(255) NOT NULL,
    trace_id VARCHAR(255),
    correlation_id VARCHAR(255),
    method VARCHAR(10) NOT NULL,
    path VARCHAR(500) NOT NULL,
    query_params JSONB DEFAULT '{}',
    headers JSONB DEFAULT '{}',
    body_size INTEGER,
    response_status_code INTEGER,
    response_size INTEGER,
    duration_ms INTEGER,
    user_id VARCHAR(255),
    organization_id VARCHAR(255),
    ip_address VARCHAR(50),
    user_agent TEXT,
    logged_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for request_logs
CREATE INDEX IF NOT EXISTS idx_request_logs_request_id ON request_logs(request_id);
CREATE INDEX IF NOT EXISTS idx_request_logs_trace_id ON request_logs(trace_id);
CREATE INDEX IF NOT EXISTS idx_request_logs_user_id ON request_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_request_logs_logged_at ON request_logs(logged_at DESC);
CREATE INDEX IF NOT EXISTS idx_request_logs_status_code ON request_logs(response_status_code) WHERE response_status_code >= 400;

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for error_registry
CREATE TRIGGER update_error_registry_updated_at
    BEFORE UPDATE ON error_registry
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create view for system health summary
CREATE OR REPLACE VIEW system_health_summary AS
SELECT 
    component,
    check_name,
    status,
    message,
    response_time_ms,
    checked_at,
    EXTRACT(EPOCH FROM (NOW() - checked_at)) AS seconds_since_check
FROM health_checks
WHERE (component, check_name, checked_at) IN (
    SELECT component, check_name, MAX(checked_at)
    FROM health_checks
    GROUP BY component, check_name
);

-- Create view for recent errors
CREATE OR REPLACE VIEW recent_errors AS
SELECT 
    e.error_code,
    e.error_name,
    e.severity,
    e.category,
    d.trace_id,
    d.request_id,
    d.message,
    d.created_at
FROM diagnostic_events d
JOIN error_registry e ON d.event_type = e.error_code
WHERE d.severity IN ('error', 'critical')
AND d.resolved = FALSE
ORDER BY d.created_at DESC
LIMIT 100;

-- Create view for performance summary
CREATE OR REPLACE VIEW performance_summary AS
SELECT 
    counter_name,
    counter_type,
    counter_value,
    tags,
    updated_at
FROM performance_counters
WHERE (counter_name, tags, updated_at) IN (
    SELECT counter_name, tags, MAX(updated_at)
    FROM performance_counters
    GROUP BY counter_name, tags
);

-- Create view for slow requests
CREATE OR REPLACE VIEW slow_requests AS
SELECT 
    request_id,
    trace_id,
    method,
    path,
    duration_ms,
    user_id,
    logged_at
FROM request_logs
WHERE duration_ms > 1000
ORDER BY duration_ms DESC
LIMIT 50;

-- Create view for request metrics
CREATE OR REPLACE VIEW request_metrics AS
SELECT 
    date_trunc('hour', logged_at) as hour,
    COUNT(*) as total_requests,
    COUNT(*) FILTER (WHERE response_status_code >= 400) as error_requests,
    AVG(duration_ms) as avg_duration_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration_ms) as p95_duration_ms,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY duration_ms) as p99_duration_ms
FROM request_logs
WHERE logged_at > NOW() - INTERVAL '24 hours'
GROUP BY date_trunc('hour', logged_at)
ORDER BY hour DESC;

COMMENT ON TABLE trace_sessions IS 'Distributed tracing session records';
COMMENT ON TABLE system_metrics IS 'System metrics collected over time';
COMMENT ON TABLE health_checks IS 'Health check results for components';
COMMENT ON TABLE diagnostic_events IS 'Diagnostic events and anomalies';
COMMENT ON TABLE error_registry IS 'Standardized error codes and recovery suggestions';
COMMENT ON TABLE performance_counters IS 'Performance counter values';
COMMENT ON TABLE request_logs IS 'HTTP request/response logs';

COMMIT;
