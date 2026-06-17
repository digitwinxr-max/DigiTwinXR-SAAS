-- Migration: Create sensors table
-- Version: 002
-- Description: Sensors table linked to assets

CREATE TABLE IF NOT EXISTS sensors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    sensor_type VARCHAR(100) NOT NULL,
    unit VARCHAR(50),
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster lookups
CREATE INDEX idx_sensors_asset_id ON sensors(asset_id);
CREATE INDEX idx_sensors_sensor_type ON sensors(sensor_type);
CREATE INDEX idx_sensors_status ON sensors(status);

-- Trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION update_sensors_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_sensors_updated_at
    BEFORE UPDATE ON sensors
    FOR EACH ROW
    EXECUTE FUNCTION update_sensors_updated_at();
