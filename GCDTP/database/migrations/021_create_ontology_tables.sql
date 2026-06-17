-- Migration 021: Semantic Ontology Layer
-- Creates ontology_domains, ontology_classes, ontology_relationships, ontology_taxonomies, ontology_capabilities, semantic_tags, and ontology_sync_history tables
-- Maintains backward compatibility

BEGIN;

-- Create ontology_domain enum
DO $$ BEGIN
    CREATE TYPE ontology_domain AS ENUM (
        'electrical',
        'water',
        'transport',
        'buildings',
        'telecommunications',
        'environment',
        'energy',
        'industrial',
        'custom'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create sync_status enum
DO $$ BEGIN
    CREATE TYPE ontology_sync_status AS ENUM (
        'pending',
        'syncing',
        'completed',
        'failed'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create ontology_domains table
CREATE TABLE IF NOT EXISTS ontology_domains (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    domain_type ontology_domain NOT NULL,
    parent_domain_id UUID REFERENCES ontology_domains(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for ontology_domains
CREATE INDEX IF NOT EXISTS idx_ontology_domains_name ON ontology_domains(name);
CREATE INDEX IF NOT EXISTS idx_ontology_domains_type ON ontology_domains(domain_type);
CREATE INDEX IF NOT EXISTS idx_ontology_domains_parent ON ontology_domains(parent_domain_id);

-- Create ontology_classes table
CREATE TABLE IF NOT EXISTS ontology_classes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_id UUID REFERENCES ontology_domains(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    parent_class_id UUID REFERENCES ontology_classes(id) ON DELETE SET NULL,
    level INTEGER DEFAULT 0,
    path VARCHAR(1000),
    properties JSONB DEFAULT '{}',
    capabilities JSONB DEFAULT '{}',
    is_abstract BOOLEAN DEFAULT FALSE,
    is_system BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    UNIQUE(domain_id, name)
);

-- Create indexes for ontology_classes
CREATE INDEX IF NOT EXISTS idx_ontology_classes_domain ON ontology_classes(domain_id);
CREATE INDEX IF NOT EXISTS idx_ontology_classes_parent ON ontology_classes(parent_class_id);
CREATE INDEX IF NOT EXISTS idx_ontology_classes_path ON ontology_classes(path);
CREATE INDEX IF NOT EXISTS idx_ontology_classes_name ON ontology_classes(name);

-- Create ontology_relationships table
CREATE TABLE IF NOT EXISTS ontology_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_class_id UUID REFERENCES ontology_classes(id) ON DELETE CASCADE,
    target_class_id UUID REFERENCES ontology_classes(id) ON DELETE CASCADE,
    relationship_type VARCHAR(100) NOT NULL,
    description TEXT,
    properties JSONB DEFAULT '{}',
    cardinality VARCHAR(20) DEFAULT 'many-to-many',  -- one-to-one, one-to-many, many-to-one, many-to-many
    is_directional BOOLEAN DEFAULT TRUE,
    inverse_relationship VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    UNIQUE(source_class_id, target_class_id, relationship_type)
);

-- Create indexes for ontology_relationships
CREATE INDEX IF NOT EXISTS idx_relationships_source ON ontology_relationships(source_class_id);
CREATE INDEX IF NOT EXISTS idx_relationships_target ON ontology_relationships(target_class_id);
CREATE INDEX IF NOT EXISTS idx_relationships_type ON ontology_relationships(relationship_type);

-- Create ontology_taxonomies table
CREATE TABLE IF NOT EXISTS ontology_taxonomies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_id UUID REFERENCES ontology_domains(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    root_class_id UUID REFERENCES ontology_classes(id) ON DELETE SET NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    version VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    UNIQUE(domain_id, name)
);

-- Create indexes for ontology_taxonomies
CREATE INDEX IF NOT EXISTS idx_taxonomies_domain ON ontology_taxonomies(domain_id);
CREATE INDEX IF NOT EXISTS idx_taxonomies_root ON ontology_taxonomies(root_class_id);

-- Create ontology_capabilities table
CREATE TABLE IF NOT EXISTS ontology_capabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    class_id UUID REFERENCES ontology_classes(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    capability_type VARCHAR(100),
    parameters JSONB DEFAULT '{}',
    requirements JSONB DEFAULT '[]',
    inherited BOOLEAN DEFAULT FALSE,
    parent_capability_id UUID REFERENCES ontology_capabilities(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    UNIQUE(class_id, name)
);

-- Create indexes for ontology_capabilities
CREATE INDEX IF NOT EXISTS idx_capabilities_class ON ontology_capabilities(class_id);
CREATE INDEX IF NOT EXISTS idx_capabilities_parent ON ontology_capabilities(parent_capability_id);
CREATE INDEX IF NOT EXISTS idx_capabilities_name ON ontology_capabilities(name);

-- Create semantic_tags table
CREATE TABLE IF NOT EXISTS ontology_semantic_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL,  -- 'asset', 'document', 'work_order', 'device', 'organization'
    entity_id VARCHAR(255) NOT NULL,
    class_id UUID REFERENCES ontology_classes(id) ON DELETE CASCADE,
    confidence DECIMAL(5,4) DEFAULT 1.0,
    source VARCHAR(100),
    assigned_by VARCHAR(255),
    assigned_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    UNIQUE(entity_type, entity_id, class_id)
);

-- Create indexes for ontology_semantic_tags
CREATE INDEX IF NOT EXISTS idx_semantic_tags_entity ON ontology_semantic_tags(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_semantic_tags_class ON ontology_semantic_tags(class_id);
CREATE INDEX IF NOT EXISTS idx_semantic_tags_source ON ontology_semantic_tags(source);

-- Create ontology_sync_history table
CREATE TABLE IF NOT EXISTS ontology_sync_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(255) NOT NULL,
    operation VARCHAR(20) NOT NULL,  -- 'classify', 'tag', 'update', 'remove'
    status ontology_sync_status NOT NULL DEFAULT 'pending',
    class_id UUID REFERENCES ontology_classes(id) ON DELETE SET NULL,
    tag_id UUID REFERENCES ontology_semantic_tags(id) ON DELETE SET NULL,
    error_message TEXT,
    synced_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for ontology_sync_history
CREATE INDEX IF NOT EXISTS idx_sync_history_entity ON ontology_sync_history(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_sync_history_status ON ontology_sync_history(status);
CREATE INDEX IF NOT EXISTS idx_sync_history_synced_at ON ontology_sync_history(synced_at DESC);

-- Create classification_history table
CREATE TABLE IF NOT EXISTS classification_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(255) NOT NULL,
    old_class_id UUID REFERENCES ontology_classes(id) ON DELETE SET NULL,
    new_class_id UUID REFERENCES ontology_classes(id) ON DELETE SET NULL,
    changed_by VARCHAR(255),
    changed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    reason TEXT,
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for classification_history
CREATE INDEX IF NOT EXISTS idx_classification_history_entity ON classification_history(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_classification_history_class ON classification_history(new_class_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_ontology_domains_updated_at
    BEFORE UPDATE ON ontology_domains
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ontology_classes_updated_at
    BEFORE UPDATE ON ontology_classes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ontology_capabilities_updated_at
    BEFORE UPDATE ON ontology_capabilities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create view for class hierarchy
CREATE OR REPLACE VIEW class_hierarchy AS
WITH RECURSIVE class_tree AS (
    SELECT 
        c.id,
        c.domain_id,
        c.name,
        c.display_name,
        c.parent_class_id,
        c.level,
        c.path,
        ARRAY[c.name] as hierarchy
    FROM ontology_classes c
    WHERE c.parent_class_id IS NULL
    
    UNION ALL
    
    SELECT 
        c.id,
        c.domain_id,
        c.name,
        c.display_name,
        c.parent_class_id,
        c.level,
        c.path,
        ct.hierarchy || c.name
    FROM ontology_classes c
    JOIN class_tree ct ON c.parent_class_id = ct.id
)
SELECT * FROM class_tree;

-- Create view for capability inheritance
CREATE OR REPLACE VIEW capability_inheritance AS
WITH RECURSIVE capability_tree AS (
    SELECT 
        cap.id,
        cap.class_id,
        cap.name,
        cap.display_name,
        cap.parent_capability_id,
        cap.inherited,
        ARRAY[cap.name] as inheritance_path,
        0 as depth
    FROM ontology_capabilities cap
    WHERE cap.parent_capability_id IS NULL
    
    UNION ALL
    
    SELECT 
        cap.id,
        cap.class_id,
        cap.name,
        cap.display_name,
        cap.parent_capability_id,
        TRUE as inherited,
        ct.inheritance_path || cap.name,
        ct.depth + 1
    FROM ontology_capabilities cap
    JOIN capability_tree ct ON cap.parent_capability_id = ct.id
)
SELECT * FROM capability_tree;

-- Create view for entity classifications
CREATE OR REPLACE VIEW entity_classifications AS
SELECT 
    st.entity_type,
    st.entity_id,
    st.class_id,
    oc.name as class_name,
    oc.display_name as class_display_name,
    od.name as domain_name,
    od.domain_type,
    st.confidence,
    st.source,
    st.assigned_at
FROM ontology_semantic_tags st
JOIN ontology_classes oc ON st.class_id = oc.id
JOIN ontology_domains od ON oc.domain_id = od.id;

COMMENT ON TABLE ontology_domains IS 'Ontology domains (electrical, water, transport, etc.)';
COMMENT ON TABLE ontology_classes IS 'Ontology classes forming taxonomies';
COMMENT ON TABLE ontology_relationships IS 'Relationships between ontology classes';
COMMENT ON TABLE ontology_taxonomies IS 'Taxonomy definitions';
COMMENT ON TABLE ontology_capabilities IS 'Capabilities associated with classes';
COMMENT ON TABLE ontology_semantic_tags IS 'Semantic tags assigned to entities';
COMMENT ON TABLE ontology_sync_history IS 'Ontology sync audit trail';

COMMIT;
