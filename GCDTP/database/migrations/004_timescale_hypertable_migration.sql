-- Migration: Convert measurements to TimescaleDB hypertable
-- Version: 004
-- Description: Enable TimescaleDB and convert measurements table to hypertable

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Convert measurements table to hypertable
-- The time column is 'timestamp' which contains the measurement time
SELECT create_hypertable('measurements', 'timestamp',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- Create optimized indexes for time-series queries
-- Index for querying measurements by sensor ordered by time (most common query)
CREATE INDEX IF NOT EXISTS idx_measurements_sensor_time
    ON measurements (sensor_id, timestamp DESC);

-- Index for time-ordered global queries
CREATE INDEX IF NOT EXISTS idx_measurements_time_desc
    ON measurements (timestamp DESC);

-- Add compression policy for old chunks (compress after 7 days)
-- This reduces storage for historical data
SELECT add_compression_policy('measurements', INTERVAL '7 days', if_not_exists => TRUE);

-- Add a retention policy to drop old chunks after 90 days (optional, commented out by default)
-- Uncomment if you want automatic data retention
-- SELECT add_retention_policy('measurements', INTERVAL '90 days', if_not_exists => TRUE);

-- Verify hypertable creation
-- This should show that measurements is now a hypertable
-- SELECT hypertable_name, num_chunks FROM timescaledb_information.hypertables WHERE hypertable_name = 'measurements';
