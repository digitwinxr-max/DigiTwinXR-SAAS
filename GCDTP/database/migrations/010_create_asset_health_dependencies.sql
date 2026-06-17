-- Migration: 010_create_asset_health_dependencies.sql
-- Dependency-Aware Health Propagation
-- Creates the asset_health_dependencies table for tracking dependency-based health penalties

-- Create ENUM type for relationship types (reuse from relationships)
DO $$ BEGIN
    CREATE TYPE relationship_type AS ENUM (
        'contains',
        'connected_to',
        'feeds',
        'monitors',
        'controls'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create asset_health_dependencies table
CREATE TABLE IF NOT EXISTS asset_health_dependencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    source_asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    relationship_type relationship_type NOT NULL,
    impact_weight FLOAT NOT NULL DEFAULT 1.0,
    penalty FLOAT NOT NULL DEFAULT 0.0,
    depth INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevent duplicate dependency entries
    CONSTRAINT unique_dependency UNIQUE (
        asset_id, 
        source_asset_id, 
        relationship_type
    )
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_health_dep_asset_id 
    ON asset_health_dependencies(asset_id);

CREATE INDEX IF NOT EXISTS idx_health_dep_source_asset_id 
    ON asset_health_dependencies(source_asset_id);

CREATE INDEX IF NOT EXISTS idx_health_dep_relationship_type 
    ON asset_health_dependencies(relationship_type);

CREATE INDEX IF NOT EXISTS idx_health_dep_depth 
    ON asset_health_dependencies(depth);

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_health_dep_asset_depth 
    ON asset_health_dependencies(asset_id, depth);

CREATE INDEX IF NOT EXISTS idx_health_dep_asset_penalty 
    ON asset_health_dependencies(asset_id, penalty);

-- Add comments for documentation
COMMENT ON TABLE asset_health_dependencies IS 
    'Stores calculated dependency-based health penalties between related assets';

COMMENT ON COLUMN asset_health_dependencies.asset_id IS 
    'The asset receiving the health penalty';

COMMENT ON COLUMN asset_health_dependencies.source_asset_id IS 
    'The asset causing the health penalty';

COMMENT ON COLUMN asset_health_dependencies.relationship_type IS 
    'Type of relationship between assets';

COMMENT ON COLUMN asset_health_dependencies.impact_weight IS 
    'Weight factor for this relationship type (0.0-1.0)';

COMMENT ON COLUMN asset_health_dependencies.penalty IS 
    'Calculated health penalty amount';

COMMENT ON COLUMN asset_health_dependencies.depth IS 
    'How many hops from the source asset';

-- Relationship weight constants (for reference)
-- contains = 0.5
-- feeds = 0.7
-- controls = 0.6
-- connected_to = 0.3
-- monitors = 0.0

-- Migration record
INSERT INTO schema_migrations (version, applied_at)
VALUES ('010', CURRENT_TIMESTAMP)
ON CONFLICT (version) DO NOTHING;
