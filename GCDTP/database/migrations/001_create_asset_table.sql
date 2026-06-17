-- Migration: Create asset table with PostGIS spatial support
-- Version: 001
-- Description: Initial asset table schema with geometry column

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    asset_type VARCHAR(100) NOT NULL,
    description TEXT,
    longitude DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    location GEOMETRY(Point, 4326),
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster lookups
CREATE INDEX idx_assets_asset_type ON assets(asset_type);
CREATE INDEX idx_assets_status ON assets(status);

-- Spatial index for geometry queries
CREATE INDEX idx_assets_location ON assets USING GIST(location);

-- Trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_assets_updated_at
    BEFORE UPDATE ON assets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger to auto-update location from longitude/latitude
CREATE OR REPLACE FUNCTION update_asset_location()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.longitude IS NOT NULL AND NEW.latitude IS NOT NULL THEN
        NEW.location := ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326);
    ELSE
        NEW.location := NULL;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_assets_location
    BEFORE INSERT OR UPDATE OF longitude, latitude ON assets
    FOR EACH ROW
    EXECUTE FUNCTION update_asset_location();
