-- Migration 038: Unified Semantic Layer
-- Creates tables for semantic metadata layer
-- This layer ONLY adds semantic descriptions and cross-domain references
-- It does NOT change existing engines

BEGIN;

-- Create entity type enum
DO $$ BEGIN
    CREATE TYPE entity_type AS ENUM (
        'asset',
        'sensor',
        'measurement',
        'event',
        'health',
        'relationship',
        'scenario',
        'recovery',
        'timeline',
        'work_order',
        'document'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create relationship type enum
DO $$ BEGIN
    CREATE TYPE relationship_type AS ENUM (
        'related_to',
        'caused_by',
        'depends_on',
        'documented_by',
        'observed_by',
        'generated_by'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create semantic_entities table
CREATE TABLE IF NOT EXISTS semantic_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type entity_type NOT NULL,
    entity_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(255),
    ontology_class VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(entity_type, entity_id)
);

-- Create indexes for semantic_entities
CREATE INDEX IF NOT EXISTS idx_semantic_entities_type ON semantic_entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_semantic_entities_entity_id ON semantic_entities(entity_id);
CREATE INDEX IF NOT EXISTS idx_semantic_entities_ontology_class ON semantic_entities(ontology_class);
CREATE INDEX IF NOT EXISTS idx_semantic_entities_category ON semantic_entities(category);
CREATE INDEX IF NOT EXISTS idx_semantic_entities_name ON semantic_entities(name);

-- Create semantic_tags table
CREATE TABLE IF NOT EXISTS semantic_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES semantic_entities(id) ON DELETE CASCADE,
    tag_name VARCHAR(255) NOT NULL,
    tag_value TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(entity_id, tag_name)
);

-- Create indexes for semantic_tags
CREATE INDEX IF NOT EXISTS idx_semantic_tags_entity_id ON semantic_tags(entity_id);
CREATE INDEX IF NOT EXISTS idx_semantic_tags_tag_name ON semantic_tags(tag_name);
CREATE INDEX IF NOT EXISTS idx_semantic_tags_tag_value ON semantic_tags(tag_value);

-- Create semantic_relationships table
CREATE TABLE IF NOT EXISTS semantic_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_entity_id UUID NOT NULL REFERENCES semantic_entities(id) ON DELETE CASCADE,
    target_entity_id UUID NOT NULL REFERENCES semantic_entities(id) ON DELETE CASCADE,
    relationship_type relationship_type NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(source_entity_id, target_entity_id, relationship_type)
);

-- Create indexes for semantic_relationships
CREATE INDEX IF NOT EXISTS idx_semantic_relationships_source ON semantic_relationships(source_entity_id);
CREATE INDEX IF NOT EXISTS idx_semantic_relationships_target ON semantic_relationships(target_entity_id);
CREATE INDEX IF NOT EXISTS idx_semantic_relationships_type ON semantic_relationships(relationship_type);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updated_at
CREATE TRIGGER update_semantic_entities_updated_at
    BEFORE UPDATE ON semantic_entities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create views
CREATE OR REPLACE VIEW semantic_entities_with_tags AS
SELECT 
    e.id,
    e.entity_type,
    e.entity_id,
    e.name,
    e.description,
    e.category,
    e.ontology_class,
    e.created_at,
    COALESCE(
        json_agg(
            json_build_object('tag_name', t.tag_name, 'tag_value', t.tag_value)
        ) FILTER (WHERE t.id IS NOT NULL),
        '[]'::json
    ) as tags
FROM semantic_entities e
LEFT JOIN semantic_tags t ON e.id = t.entity_id
GROUP BY e.id, e.entity_type, e.entity_id, e.name, e.description, e.category, e.ontology_class, e.created_at;

CREATE OR REPLACE VIEW semantic_graph_view AS
SELECT 
    r.id,
    r.relationship_type,
    s.id as source_id,
    s.name as source_name,
    s.entity_type as source_type,
    s.category as source_category,
    t.id as target_id,
    t.name as target_name,
    t.entity_type as target_type,
    t.category as target_category
FROM semantic_relationships r
JOIN semantic_entities s ON r.source_entity_id = s.id
JOIN semantic_entities t ON r.target_entity_id = t.id;

CREATE OR REPLACE VIEW tag_summary AS
SELECT 
    tag_name,
    COUNT(DISTINCT entity_id) as entity_count,
    COUNT(*) as total_tags
FROM semantic_tags
GROUP BY tag_name
ORDER BY entity_count DESC;

COMMENT ON TABLE semantic_entities IS 'Semantic metadata for platform entities';
COMMENT ON TABLE semantic_tags IS 'Tags for semantic entities';
COMMENT ON TABLE semantic_relationships IS 'Relationships between semantic entities';

COMMIT;
