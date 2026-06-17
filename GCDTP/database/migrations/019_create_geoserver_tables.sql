-- Migration 019: GeoServer Integration
-- Creates geoserver_workspaces, published_layers, layer_styles, service_endpoints, and layer_groups tables
-- Maintains backward compatibility

BEGIN;

-- Create layer_type enum
DO $$ BEGIN
    CREATE TYPE layer_type AS ENUM (
        'vector',
        'raster',
        'layer_group',
        'ows'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create service_type enum
DO $$ BEGIN
    CREATE TYPE service_type AS ENUM (
        'wms',
        'wfs',
        'wcs',
        'wmts'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create geoserver_workspaces table
CREATE TABLE IF NOT EXISTS geoserver_workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    uri VARCHAR(500) NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    is_isolated BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for geoserver_workspaces
CREATE INDEX IF NOT EXISTS idx_geoserver_workspaces_name ON geoserver_workspaces(name);
CREATE INDEX IF NOT EXISTS idx_geoserver_workspaces_is_default ON geoserver_workspaces(is_default);

-- Create published_layers table
CREATE TABLE IF NOT EXISTS published_layers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES geoserver_workspaces(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    native_name VARCHAR(255),
    layer_type layer_type NOT NULL DEFAULT 'vector',
    title VARCHAR(255),
    abstract TEXT,
    keywords TEXT[],
    srs VARCHAR(50),
    bbox_minx DOUBLE PRECISION,
    bbox_miny DOUBLE PRECISION,
    bbox_maxx DOUBLE PRECISION,
    bbox_maxy DOUBLE PRECISION,
    native_bbox JSONB,
    is_published BOOLEAN DEFAULT TRUE,
    is_queryable BOOLEAN DEFAULT TRUE,
    caching_enabled BOOLEAN DEFAULT FALSE,
    cache_max_age INTEGER,
    created_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    UNIQUE(workspace_id, name)
);

-- Create indexes for published_layers
CREATE INDEX IF NOT EXISTS idx_published_layers_workspace ON published_layers(workspace_id);
CREATE INDEX IF NOT EXISTS idx_published_layers_name ON published_layers(name);
CREATE INDEX IF NOT EXISTS idx_published_layers_type ON published_layers(layer_type);
CREATE INDEX IF NOT EXISTS idx_published_layers_is_published ON published_layers(is_published);

-- Create layer_styles table
CREATE TABLE IF NOT EXISTS layer_styles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES geoserver_workspaces(id) ON DELETE CASCADE,
    layer_id UUID REFERENCES published_layers(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    filename VARCHAR(500),
    sld_content TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(workspace_id, name)
);

-- Create indexes for layer_styles
CREATE INDEX IF NOT EXISTS idx_layer_styles_workspace ON layer_styles(workspace_id);
CREATE INDEX IF NOT EXISTS idx_layer_styles_layer ON layer_styles(layer_id);
CREATE INDEX IF NOT EXISTS idx_layer_styles_is_default ON layer_styles(is_default);

-- Create service_endpoints table
CREATE TABLE IF NOT EXISTS service_endpoints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES geoserver_workspaces(id) ON DELETE CASCADE,
    service_type service_type NOT NULL,
    endpoint_url VARCHAR(500),
    is_enabled BOOLEAN DEFAULT TRUE,
    version VARCHAR(20),
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    config JSONB DEFAULT '{}',
    UNIQUE(workspace_id, service_type)
);

-- Create indexes for service_endpoints
CREATE INDEX IF NOT EXISTS idx_service_endpoints_workspace ON service_endpoints(workspace_id);
CREATE INDEX IF NOT EXISTS idx_service_endpoints_type ON service_endpoints(service_type);
CREATE INDEX IF NOT EXISTS idx_service_endpoints_is_enabled ON service_endpoints(is_enabled);

-- Create layer_groups table
CREATE TABLE IF NOT EXISTS layer_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES geoserver_workspaces(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    abstract TEXT,
    mode VARCHAR(50) DEFAULT 'single',
    created_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    UNIQUE(workspace_id, name)
);

-- Create indexes for layer_groups
CREATE INDEX IF NOT EXISTS idx_layer_groups_workspace ON layer_groups(workspace_id);
CREATE INDEX IF NOT EXISTS idx_layer_groups_name ON layer_groups(name);

-- Create layer_group_layers junction table
CREATE TABLE IF NOT EXISTS layer_group_layers (
    group_id UUID NOT NULL REFERENCES layer_groups(id) ON DELETE CASCADE,
    layer_id UUID NOT NULL REFERENCES published_layers(id) ON DELETE CASCADE,
    layer_order INTEGER DEFAULT 0,
    workspace_style_id UUID REFERENCES layer_styles(id) ON DELETE SET NULL,
    added_by VARCHAR(255),
    added_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    PRIMARY KEY (group_id, layer_id)
);

-- Create indexes for layer_group_layers
CREATE INDEX IF NOT EXISTS idx_layer_group_layers_group ON layer_group_layers(group_id);
CREATE INDEX IF NOT EXISTS idx_layer_group_layers_layer ON layer_group_layers(layer_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_geoserver_workspaces_updated_at
    BEFORE UPDATE ON geoserver_workspaces
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_published_layers_updated_at
    BEFORE UPDATE ON published_layers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_layer_styles_updated_at
    BEFORE UPDATE ON layer_styles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_service_endpoints_updated_at
    BEFORE UPDATE ON service_endpoints
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_layer_groups_updated_at
    BEFORE UPDATE ON layer_groups
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create view for workspace summary
CREATE OR REPLACE VIEW geoserver_workspace_summary AS
SELECT 
    w.id,
    w.name,
    w.uri,
    w.is_default,
    w.is_isolated,
    COUNT(DISTINCT l.id) AS layer_count,
    COUNT(DISTINCT lg.id) AS group_count,
    COUNT(DISTINCT s.id) AS style_count,
    COUNT(DISTINCT se.id) FILTER (WHERE se.is_enabled = TRUE) AS enabled_services
FROM geoserver_workspaces w
LEFT JOIN published_layers l ON w.id = l.workspace_id AND l.is_published = TRUE
LEFT JOIN layer_groups lg ON w.id = lg.workspace_id
LEFT JOIN layer_styles s ON w.id = s.workspace_id
LEFT JOIN service_endpoints se ON w.id = se.workspace_id
GROUP BY w.id, w.name, w.uri, w.is_default, w.is_isolated;

-- Create view for layer details
CREATE OR REPLACE VIEW layer_details AS
SELECT 
    l.id,
    l.workspace_id,
    w.name AS workspace_name,
    l.name AS layer_name,
    l.native_name,
    l.layer_type,
    l.title,
    l.is_published,
    l.is_queryable,
    s.name AS default_style,
    l.created_at,
    l.updated_at,
    l.metadata
FROM published_layers l
JOIN geoserver_workspaces w ON l.workspace_id = w.id
LEFT JOIN layer_styles s ON l.id = s.layer_id AND s.is_default = TRUE;

COMMENT ON TABLE geoserver_workspaces IS 'GeoServer workspaces';
COMMENT ON TABLE published_layers IS 'Published map layers';
COMMENT ON TABLE layer_styles IS 'SLD styles for layers';
COMMENT ON TABLE service_endpoints IS 'WMS/WFS/WCS service endpoints';
COMMENT ON TABLE layer_groups IS 'Layer groups for organization';

COMMIT;
