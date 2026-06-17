-- Migration: 008_create_asset_relationships.sql
-- Asset Relationship Graph Engine
-- Creates the asset_relationships table for hierarchical asset modeling

-- Create ENUM type for relationship types
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

-- Create asset_relationships table
CREATE TABLE IF NOT EXISTS asset_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    child_asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    relationship_type relationship_type NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevent self-referencing relationships
    CONSTRAINT no_self_reference CHECK (parent_asset_id != child_asset_id),
    
    -- Prevent duplicate relationships
    CONSTRAINT unique_relationship UNIQUE (parent_asset_id, child_asset_id, relationship_type)
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_relationships_parent_asset_id 
    ON asset_relationships(parent_asset_id);

CREATE INDEX IF NOT EXISTS idx_relationships_child_asset_id 
    ON asset_relationships(child_asset_id);

CREATE INDEX IF NOT EXISTS idx_relationships_type 
    ON asset_relationships(relationship_type);

-- Composite index for common query patterns
CREATE INDEX IF NOT EXISTS idx_relationships_parent_type 
    ON asset_relationships(parent_asset_id, relationship_type);

CREATE INDEX IF NOT EXISTS idx_relationships_child_type 
    ON asset_relationships(child_asset_id, relationship_type);

-- Add comments for documentation
COMMENT ON TABLE asset_relationships IS 
    'Stores hierarchical and associative relationships between assets for graph-based modeling';

COMMENT ON COLUMN asset_relationships.parent_asset_id IS 
    'The parent/containing asset in the relationship';

COMMENT ON COLUMN asset_relationships.child_asset_id IS 
    'The child/contained asset in the relationship';

COMMENT ON COLUMN asset_relationships.relationship_type IS 
    'Type of relationship: contains, connected_to, feeds, monitors, controls';

-- Migration record
INSERT INTO schema_migrations (version, applied_at)
VALUES ('008', CURRENT_TIMESTAMP)
ON CONFLICT (version) DO NOTHING;
