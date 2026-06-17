-- Migration: Create events table
-- Version: 006
-- Description: Event storage for threshold violations and system events

CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sensor_id UUID REFERENCES sensors(id) ON DELETE CASCADE,
    asset_id UUID REFERENCES assets(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL DEFAULT 'THRESHOLD_VIOLATION',
    severity VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    value DOUBLE PRECISION,
    threshold_rule_id UUID REFERENCES threshold_rules(id) ON DELETE SET NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common query patterns
CREATE INDEX idx_events_sensor_id ON events(sensor_id);
CREATE INDEX idx_events_asset_id ON events(asset_id);
CREATE INDEX idx_events_status ON events(status);
CREATE INDEX idx_events_timestamp ON events(timestamp DESC);
CREATE INDEX idx_events_severity ON events(severity);

-- Composite index for active events by severity
CREATE INDEX idx_events_status_severity ON events(status, severity) WHERE status = 'ACTIVE';

-- Index for event lookups by type
CREATE INDEX idx_events_type ON events(event_type);

COMMENT ON TABLE events IS 'System events from threshold violations and other sources';
COMMENT ON COLUMN events.severity IS 'OK, WARNING, CRITICAL - from threshold evaluation';
COMMENT ON COLUMN events.status IS 'ACTIVE (open), RESOLVED (closed)';
COMMENT ON COLUMN events.event_type IS 'THRESHOLD_VIOLATION, etc.';