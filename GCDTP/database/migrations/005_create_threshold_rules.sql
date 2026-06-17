-- Migration: Create threshold_rules table
-- Version: 005
-- Description: Threshold rules for measurement evaluation

CREATE TABLE threshold_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sensor_id UUID REFERENCES sensors(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    rule_type VARCHAR(50) NOT NULL DEFAULT 'range',
    warning_min DOUBLE PRECISION,
    warning_max DOUBLE PRECISION,
    critical_min DOUBLE PRECISION,
    critical_max DOUBLE PRECISION,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for querying rules by sensor
CREATE INDEX idx_threshold_rules_sensor_id ON threshold_rules(sensor_id);

-- Index for active rules (commonly queried)
CREATE INDEX idx_threshold_rules_active ON threshold_rules(is_active) WHERE is_active = TRUE;

-- Allow null sensor_id for global rules that apply to all sensors of a type
-- This is useful for setting default thresholds
COMMENT ON COLUMN threshold_rules.sensor_id IS 'Nullable for global rules that apply to all sensors';