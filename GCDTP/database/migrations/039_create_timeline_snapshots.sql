-- Migration 039: Timeline Replay Engine
-- Creates tables for temporal replay capabilities
-- This engine reconstructs historical states from existing records
-- Timeline Replay is read-only and immutable

BEGIN;

-- Create snapshot_type enum
DO $$ BEGIN
    CREATE TYPE snapshot_type AS ENUM (
        'asset_state',
        'health_state',
        'event_state',
        'measurement_state',
        'system_state'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create timeline_snapshots table
CREATE TABLE IF NOT EXISTS timeline_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    snapshot_type snapshot_type NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id VARCHAR(255) NOT NULL,
    snapshot_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for timeline_snapshots
CREATE INDEX IF NOT EXISTS idx_timeline_snapshots_timestamp ON timeline_snapshots(timestamp);
CREATE INDEX IF NOT EXISTS idx_timeline_snapshots_type ON timeline_snapshots(snapshot_type);
CREATE INDEX IF NOT EXISTS idx_timeline_snapshots_entity ON timeline_snapshots(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_timeline_snapshots_entity_id ON timeline_snapshots(entity_id);
CREATE INDEX IF NOT EXISTS idx_timeline_snapshots_created ON timeline_snapshots(created_at);

-- Create composite index for common queries
CREATE INDEX IF NOT EXISTS idx_timeline_snapshots_range ON timeline_snapshots(timestamp, snapshot_type, entity_type);

-- Add comments
COMMENT ON TABLE timeline_snapshots IS 'Immutable timeline snapshots for replay capabilities';
COMMENT ON COLUMN timeline_snapshots.snapshot_type IS 'Type of snapshot: asset, health, event, measurement, or system';
COMMENT ON COLUMN timeline_snapshots.snapshot_data IS 'JSON snapshot data - immutable once created';
COMMENT ON COLUMN timeline_snapshots.entity_type IS 'Type of entity being snapshotted';
COMMENT ON COLUMN timeline_snapshots.entity_id IS 'ID of the entity being snapshotted';

-- Create view for system snapshots
CREATE OR REPLACE VIEW system_snapshots AS
SELECT 
    id,
    timestamp,
    snapshot_data,
    created_at
FROM timeline_snapshots
WHERE snapshot_type = 'system_state'
ORDER BY timestamp DESC;

-- Create view for entity history
CREATE OR REPLACE VIEW entity_history AS
SELECT 
    id,
    timestamp,
    snapshot_type,
    entity_type,
    entity_id,
    snapshot_data,
    created_at
FROM timeline_snapshots
ORDER BY timestamp DESC, entity_type, entity_id;

-- Create function to get snapshots in time range
CREATE OR REPLACE FUNCTION get_snapshots_in_range(
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    req_type snapshot_type DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    "timestamp" TIMESTAMP WITH TIME ZONE,
    snapshot_type snapshot_type,
    entity_type VARCHAR(100),
    entity_id VARCHAR(255),
    snapshot_data JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ts.id,
        ts.timestamp,
        ts.snapshot_type,
        ts.entity_type,
        ts.entity_id,
        ts.snapshot_data
    FROM timeline_snapshots ts
    WHERE ts.timestamp >= start_time 
      AND ts.timestamp <= end_time
      AND (req_type IS NULL OR ts.snapshot_type = req_type)
    ORDER BY ts.timestamp ASC;
END;
$$ LANGUAGE plpgsql;

-- Create function to get latest snapshot for entity
CREATE OR REPLACE FUNCTION get_latest_entity_snapshot(
    req_entity_type VARCHAR(100),
    req_entity_id VARCHAR(255),
    req_time TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT ts.snapshot_data
    INTO result
    FROM timeline_snapshots ts
    WHERE ts.entity_type = req_entity_type
      AND ts.entity_id = req_entity_id
      AND ts.timestamp <= req_time
    ORDER BY ts.timestamp DESC
    LIMIT 1;
    
    RETURN COALESCE(result, '{}'::jsonb);
END;
$$ LANGUAGE plpgsql;

COMMIT;
