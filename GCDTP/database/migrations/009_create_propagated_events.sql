-- Migration: 009_create_propagated_events.sql
-- Cascading Failure Engine
-- Creates the propagated_events table for tracking consequence propagation

-- Create ENUM types for propagation
DO $$ BEGIN
    CREATE TYPE propagation_type AS ENUM (
        'child_failure',
        'upstream_failure',
        'downstream_failure',
        'dependency_impact'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE event_severity AS ENUM (
        'WARNING',
        'CRITICAL'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create propagated_events table
CREATE TABLE IF NOT EXISTS propagated_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    source_asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    affected_asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    propagation_type propagation_type NOT NULL,
    severity event_severity NOT NULL,
    depth INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevent duplicate propagation records
    CONSTRAINT unique_propagation UNIQUE (
        source_event_id, 
        affected_asset_id, 
        propagation_type
    )
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_propagated_source_event_id 
    ON propagated_events(source_event_id);

CREATE INDEX IF NOT EXISTS idx_propagated_source_asset_id 
    ON propagated_events(source_asset_id);

CREATE INDEX IF NOT EXISTS idx_propagated_affected_asset_id 
    ON propagated_events(affected_asset_id);

CREATE INDEX IF NOT EXISTS idx_propagated_depth 
    ON propagated_events(depth);

CREATE INDEX IF NOT EXISTS idx_propagated_severity 
    ON propagated_events(severity);

CREATE INDEX IF NOT EXISTS idx_propagated_type 
    ON propagated_events(propagation_type);

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_propagated_affected_severity 
    ON propagated_events(affected_asset_id, severity);

CREATE INDEX IF NOT EXISTS idx_propagated_source_affected 
    ON propagated_events(source_asset_id, affected_asset_id);

-- Add comments for documentation
COMMENT ON TABLE propagated_events IS 
    'Stores propagated consequences from failure events through asset relationships';

COMMENT ON COLUMN propagated_events.source_event_id IS 
    'The original event that triggered the propagation';

COMMENT ON COLUMN propagated_events.source_asset_id IS 
    'The asset where the original event occurred';

COMMENT ON COLUMN propagated_events.affected_asset_id IS 
    'The asset affected by propagation';

COMMENT ON COLUMN propagated_events.propagation_type IS 
    'Type of propagation: child_failure, upstream_failure, downstream_failure, dependency_impact';

COMMENT ON COLUMN propagated_events.severity IS 
    'Severity of the propagated impact';

COMMENT ON COLUMN propagated_events.depth IS 
    'How many hops from the source event';

-- Migration record
INSERT INTO schema_migrations (version, applied_at)
VALUES ('009', CURRENT_TIMESTAMP)
ON CONFLICT (version) DO NOTHING;
