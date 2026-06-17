-- Migration 017: Node-RED Workflow Integration
-- Creates workflow_definitions, workflow_instances, workflow_executions, and workflow_connectors tables
-- Maintains backward compatibility

BEGIN;

-- Create execution_status enum
DO $$ BEGIN
    CREATE TYPE execution_status AS ENUM (
        'pending',
        'running',
        'completed',
        'failed',
        'cancelled',
        'retrying'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create trigger_type enum
DO $$ BEGIN
    CREATE TYPE trigger_type AS ENUM (
        'eventbus',
        'timeline',
        'manual',
        'scheduled',
        'asset_event',
        'workorder_event',
        'document_event'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create connector_type enum
DO $$ BEGIN
    CREATE TYPE connector_type AS ENUM (
        'http',
        'rest',
        'webhook',
        'file',
        'email',
        'mqtt',
        'geoserver',
        'emqx'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create workflow_definitions table
CREATE TABLE IF NOT EXISTS workflow_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    flow_json JSONB NOT NULL DEFAULT '{}',
    trigger_type trigger_type NOT NULL DEFAULT 'manual',
    trigger_config JSONB DEFAULT '{}',
    is_enabled BOOLEAN DEFAULT TRUE,
    is_template BOOLEAN DEFAULT FALSE,
    version INTEGER NOT NULL DEFAULT 1,
    created_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_executed_at TIMESTAMP WITH TIME ZONE,
    execution_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for workflow_definitions
CREATE INDEX IF NOT EXISTS idx_workflows_trigger_type ON workflow_definitions(trigger_type);
CREATE INDEX IF NOT EXISTS idx_workflows_is_enabled ON workflow_definitions(is_enabled);
CREATE INDEX IF NOT EXISTS idx_workflows_name ON workflow_definitions(name);
CREATE INDEX IF NOT EXISTS idx_workflows_created_at ON workflow_definitions(created_at DESC);

-- Create workflow_instances table
CREATE TABLE IF NOT EXISTS workflow_instances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflow_definitions(id) ON DELETE CASCADE,
    name VARCHAR(255),
    status execution_status NOT NULL DEFAULT 'pending',
    input_data JSONB DEFAULT '{}',
    output_data JSONB DEFAULT '{}',
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    context JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for workflow_instances
CREATE INDEX IF NOT EXISTS idx_instances_workflow_id ON workflow_instances(workflow_id);
CREATE INDEX IF NOT EXISTS idx_instances_status ON workflow_instances(status);
CREATE INDEX IF NOT EXISTS idx_instances_started_at ON workflow_instances(started_at DESC);

-- Create workflow_executions table
CREATE TABLE IF NOT EXISTS workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflow_definitions(id) ON DELETE CASCADE,
    instance_id UUID REFERENCES workflow_instances(id) ON DELETE SET NULL,
    execution_order INTEGER NOT NULL DEFAULT 1,
    node_id VARCHAR(100),
    node_name VARCHAR(255),
    status execution_status NOT NULL,
    input_data JSONB DEFAULT '{}',
    output_data JSONB DEFAULT '{}',
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for workflow_executions
CREATE INDEX IF NOT EXISTS idx_executions_workflow_id ON workflow_executions(workflow_id);
CREATE INDEX IF NOT EXISTS idx_executions_instance_id ON workflow_executions(instance_id);
CREATE INDEX IF NOT EXISTS idx_executions_started_at ON workflow_executions(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_executions_status ON workflow_executions(status);

-- Create workflow_connectors table
CREATE TABLE IF NOT EXISTS workflow_connectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflow_definitions(id) ON DELETE CASCADE,
    connector_type connector_type NOT NULL,
    name VARCHAR(100) NOT NULL,
    config JSONB NOT NULL DEFAULT '{}',
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for workflow_connectors
CREATE INDEX IF NOT EXISTS idx_connectors_workflow_id ON workflow_connectors(workflow_id);
CREATE INDEX IF NOT EXISTS idx_connectors_type ON workflow_connectors(connector_type);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_workflows_updated_at
    BEFORE UPDATE ON workflow_definitions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_instances_updated_at
    BEFORE UPDATE ON workflow_instances
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_connectors_updated_at
    BEFORE UPDATE ON workflow_connectors
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create view for workflow summary
CREATE OR REPLACE VIEW workflow_summary AS
SELECT 
    w.id,
    w.name,
    w.description,
    w.trigger_type,
    w.is_enabled,
    w.version,
    w.created_at,
    w.updated_at,
    w.last_executed_at,
    w.execution_count,
    COUNT(DISTINCT wi.id) AS total_instances,
    COUNT(DISTINCT CASE WHEN wi.status = 'running' THEN wi.id END) AS running_instances,
    COUNT(DISTINCT CASE WHEN wi.status = 'failed' THEN wi.id END) AS failed_instances,
    COUNT(DISTINCT wc.id) AS connector_count
FROM workflow_definitions w
LEFT JOIN workflow_instances wi ON w.id = wi.workflow_id
LEFT JOIN workflow_connectors wc ON w.id = wc.workflow_id
GROUP BY w.id;

-- Create view for execution history
CREATE OR REPLACE VIEW workflow_execution_history AS
SELECT 
    we.id,
    we.workflow_id,
    w.name AS workflow_name,
    we.instance_id,
    we.node_id,
    we.node_name,
    we.status,
    we.input_data,
    we.output_data,
    we.error_message,
    we.started_at,
    we.completed_at,
    we.duration_ms,
    CASE 
        WHEN we.completed_at IS NOT NULL AND we.started_at IS NOT NULL 
        THEN EXTRACT(EPOCH FROM (we.completed_at - we.started_at)) * 1000
        ELSE NULL
    END AS actual_duration_ms
FROM workflow_executions we
JOIN workflow_definitions w ON we.workflow_id = w.id
ORDER BY we.started_at DESC;

COMMENT ON TABLE workflow_definitions IS 'Workflow definitions (Node-RED flows)';
COMMENT ON TABLE workflow_instances IS 'Active workflow executions';
COMMENT ON TABLE workflow_executions IS 'Node-level execution history';
COMMENT ON TABLE workflow_connectors IS 'External connectors for workflows';

COMMIT;
