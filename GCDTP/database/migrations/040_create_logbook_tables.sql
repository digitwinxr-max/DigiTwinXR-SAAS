-- Migration 040: Digital Logbook Engine
-- Creates tables for immutable operational logbook
-- Entries are append-only, no edits or deletes

BEGIN;

-- Create entry_type enum
DO $$ BEGIN
    CREATE TYPE entry_type AS ENUM (
        'observation',
        'incident',
        'maintenance',
        'inspection',
        'investigation',
        'annotation'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create severity enum
DO $$ BEGIN
    CREATE TYPE log_severity AS ENUM (
        'info',
        'warning',
        'critical'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create logbook_entries table
CREATE TABLE IF NOT EXISTS logbook_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    entry_type entry_type NOT NULL,
    entity_type VARCHAR(100),
    entity_id VARCHAR(255),
    severity log_severity NOT NULL DEFAULT 'info',
    content TEXT NOT NULL,
    author VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    timeline_snapshot_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for logbook_entries
CREATE INDEX IF NOT EXISTS idx_logbook_entity_type ON logbook_entries(entity_type);
CREATE INDEX IF NOT EXISTS idx_logbook_entity_id ON logbook_entries(entity_id);
CREATE INDEX IF NOT EXISTS idx_logbook_severity ON logbook_entries(severity);
CREATE INDEX IF NOT EXISTS idx_logbook_timestamp ON logbook_entries(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_logbook_entry_type ON logbook_entries(entry_type);
CREATE INDEX IF NOT EXISTS idx_logbook_author ON logbook_entries(author);
CREATE INDEX IF NOT EXISTS idx_logbook_timeline ON logbook_entries(timeline_snapshot_id);

-- Create composite index for common queries
CREATE INDEX IF NOT EXISTS idx_logbook_entity ON logbook_entries(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_logbook_severity_time ON logbook_entries(severity, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_logbook_type_time ON logbook_entries(entry_type, timestamp DESC);

-- Add comments
COMMENT ON TABLE logbook_entries IS 'Immutable operational logbook - entries are append-only';
COMMENT ON COLUMN logbook_entries.entry_type IS 'Type of entry: observation, incident, maintenance, inspection, investigation, annotation';
COMMENT ON COLUMN logbook_entries.severity IS 'Severity level: info, warning, critical';
COMMENT ON COLUMN logbook_entries.content IS 'Full narrative content of the entry';
COMMENT ON COLUMN logbook_entries.author IS 'Author of the entry';
COMMENT ON COLUMN logbook_entries.timeline_snapshot_id IS 'Optional reference to timeline snapshot for temporal linking';
COMMENT ON COLUMN logbook_entries.created_at IS 'System timestamp when entry was created - immutable';

-- Create view for recent entries
CREATE OR REPLACE VIEW recent_logbook_entries AS
SELECT 
    id,
    title,
    entry_type,
    entity_type,
    entity_id,
    severity,
    content,
    author,
    timestamp,
    timeline_snapshot_id,
    created_at
FROM logbook_entries
ORDER BY timestamp DESC
LIMIT 100;

-- Create view for entries by severity
CREATE OR REPLACE VIEW logbook_by_severity AS
SELECT 
    severity,
    COUNT(*) as entry_count,
    MIN(timestamp) as first_entry,
    MAX(timestamp) as last_entry
FROM logbook_entries
GROUP BY severity;

-- Create view for entries by type
CREATE OR REPLACE VIEW logbook_by_type AS
SELECT 
    entry_type,
    COUNT(*) as entry_count,
    MIN(timestamp) as first_entry,
    MAX(timestamp) as last_entry
FROM logbook_entries
GROUP BY entry_type;

-- Create function to get entries for entity
CREATE OR REPLACE FUNCTION get_entity_logbook_entries(
    req_entity_type VARCHAR(100),
    req_entity_id VARCHAR(255)
)
RETURNS TABLE (
    id UUID,
    title VARCHAR(500),
    entry_type entry_type,
    severity log_severity,
    content TEXT,
    author VARCHAR(255),
    "timestamp" TIMESTAMP WITH TIME ZONE,
    timeline_snapshot_id UUID,
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        l.id,
        l.title,
        l.entry_type,
        l.severity,
        l.content,
        l.author,
        l.timestamp,
        l.timeline_snapshot_id,
        l.created_at
    FROM logbook_entries l
    WHERE l.entity_type = req_entity_type
      AND l.entity_id = req_entity_id
    ORDER BY l.timestamp DESC;
END;
$$ LANGUAGE plpgsql;

-- Create function to get incident history
CREATE OR REPLACE FUNCTION get_incident_history(
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW() - INTERVAL '30 days',
    end_time TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
RETURNS TABLE (
    id UUID,
    title VARCHAR(500),
    entity_type VARCHAR(100),
    entity_id VARCHAR(255),
    severity log_severity,
    content TEXT,
    author VARCHAR(255),
    "timestamp" TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        l.id,
        l.title,
        l.entity_type,
        l.entity_id,
        l.severity,
        l.content,
        l.author,
        l.timestamp
    FROM logbook_entries l
    WHERE l.entry_type = 'incident'
      AND l.timestamp >= start_time
      AND l.timestamp <= end_time
    ORDER BY l.timestamp DESC;
END;
$$ LANGUAGE plpgsql;

COMMIT;
