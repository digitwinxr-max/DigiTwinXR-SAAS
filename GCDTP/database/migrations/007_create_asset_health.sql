-- Migration: Create asset_health table
-- Version: 007
-- Description: Asset health derived from events

CREATE TABLE asset_health (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    health_score INTEGER NOT NULL DEFAULT 100 CHECK (health_score >= 0 AND health_score <= 100),
    health_status VARCHAR(20) NOT NULL DEFAULT 'HEALTHY',
    active_event_count INTEGER NOT NULL DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    calculation_method VARCHAR(50) NOT NULL DEFAULT 'RULE_BASED'
);

-- Unique constraint: one health record per asset
CREATE UNIQUE INDEX idx_asset_health_asset_id ON asset_health(asset_id);

-- Index for querying by health status
CREATE INDEX idx_asset_health_status ON asset_health(health_status);

-- Index for sorting by health score
CREATE INDEX idx_asset_health_score ON asset_health(health_score DESC);

COMMENT ON TABLE asset_health IS 'Derived health state for assets based on active events';
COMMENT ON COLUMN asset_health.health_score IS 'Score from 0-100, calculated from active events';
COMMENT ON COLUMN asset_health.health_status IS 'HEALTHY (80-100), DEGRADED (40-79), CRITICAL (0-39)';
COMMENT ON COLUMN asset_health.active_event_count IS 'Count of ACTIVE events for this asset';
COMMENT ON COLUMN asset_health.calculation_method IS 'RULE_BASED, ML_BASED, etc.';