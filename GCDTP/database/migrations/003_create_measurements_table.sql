-- Migration: Create measurements table
-- Version: 003
-- Description: Measurements table linked to sensors

CREATE TABLE IF NOT EXISTS measurements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sensor_id UUID NOT NULL REFERENCES sensors(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    value DOUBLE PRECISION NOT NULL,
    quality VARCHAR(20) NOT NULL DEFAULT 'good',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for faster lookups
CREATE INDEX idx_measurements_sensor_id ON measurements(sensor_id);
CREATE INDEX idx_measurements_timestamp ON measurements(timestamp);
CREATE INDEX idx_measurements_quality ON measurements(quality);
