-- Migration 027: Advanced Geospatial Analytics Layer
-- Creates tables for GIS analytics management
-- PostGIS remains authoritative for spatial data

BEGIN;

-- Create enums
DO $$ BEGIN
    CREATE TYPE dataset_type AS ENUM (
        'raster',
        'vector',
        'terrain',
        'point_cloud'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE dataset_status AS ENUM (
        'pending',
        'processing',
        'ready',
        'error',
        'archived'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE analysis_type AS ENUM (
        'slope',
        'aspect',
        'elevation',
        'buffer',
        'intersection',
        'overlay',
        'nearest_neighbor',
        'distance',
        'zonal_statistics',
        'hillshade'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE job_status AS ENUM (
        'queued',
        'running',
        'completed',
        'failed',
        'cancelled'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create raster_datasets table
CREATE TABLE IF NOT EXISTS raster_datasets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_name VARCHAR(255) NOT NULL,
    dataset_type dataset_type DEFAULT 'raster',
    file_path VARCHAR(1024),
    storage_object_id UUID,
    width INTEGER,
    height INTEGER,
    bands INTEGER,
    driver VARCHAR(50),
    crs VARCHAR(255),
    bounds GEOMETRY(POLYGON, 4326),
    no_data_value DOUBLE PRECISION,
    pixel_type VARCHAR(50),
    compression VARCHAR(50),
    status dataset_status DEFAULT 'pending',
    owner_organization_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for raster_datasets
CREATE INDEX IF NOT EXISTS idx_raster_datasets_name ON raster_datasets(dataset_name);
CREATE INDEX IF NOT EXISTS idx_raster_datasets_crs ON raster_datasets(crs);
CREATE INDEX IF NOT EXISTS idx_raster_datasets_status ON raster_datasets(status);
CREATE INDEX IF NOT EXISTS idx_raster_datasets_bounds ON raster_datasets USING GIST(bounds);

-- Create vector_datasets table
CREATE TABLE IF NOT EXISTS vector_datasets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(1024),
    storage_object_id UUID,
    geometry_type VARCHAR(50),
    crs VARCHAR(255),
    feature_count INTEGER,
    attribute_schema JSONB,
    status dataset_status DEFAULT 'pending',
    owner_organization_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for vector_datasets
CREATE INDEX IF NOT EXISTS idx_vector_datasets_name ON vector_datasets(dataset_name);
CREATE INDEX IF NOT EXISTS idx_vector_datasets_geometry ON vector_datasets(geometry_type);
CREATE INDEX IF NOT EXISTS idx_vector_datasets_crs ON vector_datasets(crs);
CREATE INDEX IF NOT EXISTS idx_vector_datasets_status ON vector_datasets(status);

-- Create spatial_indexes table
CREATE TABLE IF NOT EXISTS spatial_indexes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id UUID NOT NULL,
    dataset_type dataset_type,
    index_type VARCHAR(50) DEFAULT 'GIST',
    index_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for spatial_indexes
CREATE INDEX IF NOT EXISTS idx_spatial_indexes_dataset ON spatial_indexes(dataset_id);

-- Create coordinate_systems table
CREATE TABLE IF NOT EXISTS coordinate_systems (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    epsg_code INTEGER NOT NULL UNIQUE,
    crs_name VARCHAR(255),
    crs_type VARCHAR(50),
    proj4_definition TEXT,
    wkt_definition TEXT,
    is_geographic BOOLEAN,
    is_projected BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for coordinate_systems
CREATE INDEX IF NOT EXISTS idx_coordinate_systems_epsg ON coordinate_systems(epsg_code);
CREATE INDEX IF NOT EXISTS idx_coordinate_systems_type ON coordinate_systems(crs_type);

-- Create terrain_models table
CREATE TABLE IF NOT EXISTS terrain_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(255) NOT NULL,
    raster_dataset_id UUID REFERENCES raster_datasets(id) ON DELETE SET NULL,
    dem_source VARCHAR(50),
    resolution DOUBLE PRECISION,
    vertical_datum VARCHAR(100),
    coverage_area GEOMETRY(POLYGON, 4326),
    min_elevation DOUBLE PRECISION,
    max_elevation DOUBLE PRECISION,
    status dataset_status DEFAULT 'pending',
    owner_organization_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for terrain_models
CREATE INDEX IF NOT EXISTS idx_terrain_models_name ON terrain_models(model_name);
CREATE INDEX IF NOT EXISTS idx_terrain_models_coverage ON terrain_models USING GIST(coverage_area);
CREATE INDEX IF NOT EXISTS idx_terrain_models_status ON terrain_models(status);

-- Create raster_metadata table
CREATE TABLE IF NOT EXISTS raster_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raster_dataset_id UUID REFERENCES raster_datasets(id) ON DELETE CASCADE,
    band_index INTEGER,
    band_name VARCHAR(255),
    band_description TEXT,
    statistics JSONB,
    histogram JSONB,
    color_interpretation VARCHAR(50),
    nodata_value DOUBLE PRECISION,
    min_value DOUBLE PRECISION,
    max_value DOUBLE PRECISION,
    mean_value DOUBLE PRECISION,
    stddev_value DOUBLE PRECISION,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for raster_metadata
CREATE INDEX IF NOT EXISTS idx_raster_metadata_dataset ON raster_metadata(raster_dataset_id);
CREATE INDEX IF NOT EXISTS idx_raster_metadata_band ON raster_metadata(raster_dataset_id, band_index);

-- Create analysis_jobs table
CREATE TABLE IF NOT EXISTS analysis_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_name VARCHAR(255) NOT NULL,
    analysis_type analysis_type NOT NULL,
    input_parameters JSONB,
    input_datasets JSONB,
    output_datasets JSONB,
    status job_status DEFAULT 'queued',
    progress INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for analysis_jobs
CREATE INDEX IF NOT EXISTS idx_analysis_jobs_type ON analysis_jobs(analysis_type);
CREATE INDEX IF NOT EXISTS idx_analysis_jobs_status ON analysis_jobs(status);
CREATE INDEX IF NOT EXISTS idx_analysis_jobs_created_by ON analysis_jobs(created_by);

-- Create transformation_history table
CREATE TABLE IF NOT EXISTS transformation_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_crs VARCHAR(255) NOT NULL,
    target_crs VARCHAR(255) NOT NULL,
    transformation_type VARCHAR(50),
    dataset_id UUID,
    dataset_type dataset_type,
    accuracy_meters DOUBLE PRECISION,
    method VARCHAR(100),
    parameters JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for transformation_history
CREATE INDEX IF NOT EXISTS idx_transformation_history_crs ON transformation_history(source_crs, target_crs);
CREATE INDEX IF NOT EXISTS idx_transformation_history_dataset ON transformation_history(dataset_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_raster_datasets_updated_at
    BEFORE UPDATE ON raster_datasets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vector_datasets_updated_at
    BEFORE UPDATE ON vector_datasets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_terrain_models_updated_at
    BEFORE UPDATE ON terrain_models
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_analysis_jobs_updated_at
    BEFORE UPDATE ON analysis_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create views
CREATE OR REPLACE VIEW active_raster_datasets AS
SELECT 
    dataset_name,
    width,
    height,
    bands,
    driver,
    crs,
    status
FROM raster_datasets
WHERE status = 'ready'
ORDER BY dataset_name;

CREATE OR REPLACE VIEW active_vector_datasets AS
SELECT 
    dataset_name,
    geometry_type,
    crs,
    feature_count,
    status
FROM vector_datasets
WHERE status = 'ready'
ORDER BY dataset_name;

CREATE OR REPLACE VIEW analysis_jobs_summary AS
SELECT 
    job_name,
    analysis_type,
    status,
    progress,
    created_at,
    completed_at
FROM analysis_jobs
ORDER BY created_at DESC;

CREATE OR REPLACE VIEW terrain_models_summary AS
SELECT 
    model_name,
    resolution,
    min_elevation,
    max_elevation,
    status
FROM terrain_models
WHERE status = 'ready'
ORDER BY model_name;

COMMENT ON TABLE raster_datasets IS 'Raster dataset metadata';
COMMENT ON TABLE vector_datasets IS 'Vector dataset metadata';
COMMENT ON TABLE spatial_indexes IS 'Spatial index tracking';
COMMENT ON TABLE coordinate_systems IS 'Coordinate reference system definitions';
COMMENT ON TABLE terrain_models IS 'Digital elevation model metadata';
COMMENT ON TABLE raster_metadata IS 'Raster band metadata and statistics';
COMMENT ON TABLE analysis_jobs IS 'Geospatial analysis job tracking';
COMMENT ON TABLE transformation_history IS 'Coordinate transformation history';

COMMIT;
