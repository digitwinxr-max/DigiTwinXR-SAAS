-- Migration 044: Agent Framework
-- Creates tables for AI Agent Framework with human approval
-- Agents propose actions - humans approve - execution follows

BEGIN;

-- Create agent_type enum
DO $$ BEGIN
    CREATE TYPE agent_type AS ENUM (
        'diagnostic_agent',
        'maintenance_agent',
        'recovery_agent',
        'knowledge_agent',
        'timeline_agent'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create task_status enum
DO $$ BEGIN
    CREATE TYPE task_status AS ENUM (
        'pending',
        'approved',
        'rejected',
        'executed',
        'failed'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create approval_status enum
DO $$ BEGIN
    CREATE TYPE approval_status AS ENUM (
        'pending',
        'approved',
        'rejected',
        'executed',
        'failed'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create agent_definition table
CREATE TABLE IF NOT EXISTS agent_definition (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    agent_type agent_type NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create agent_task table
CREATE TABLE IF NOT EXISTS agent_task (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agent_definition(id),
    task_type VARCHAR(100) NOT NULL,
    status task_status NOT NULL DEFAULT 'pending',
    requested_by VARCHAR(255) NOT NULL,
    approved_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    executed_at TIMESTAMP WITH TIME ZONE,
    context_data JSONB DEFAULT '{}'::jsonb,
    result_data JSONB DEFAULT '{}'::jsonb
);

-- Create agent_action table
CREATE TABLE IF NOT EXISTS agent_action (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES agent_task(id) ON DELETE CASCADE,
    action_type VARCHAR(100) NOT NULL,
    action_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    approval_status approval_status NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    executed_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for agent_definition
CREATE INDEX IF NOT EXISTS idx_agent_def_type ON agent_definition(agent_type);
CREATE INDEX IF NOT EXISTS idx_agent_def_enabled ON agent_definition(enabled);

-- Create indexes for agent_task
CREATE INDEX IF NOT EXISTS idx_agent_task_agent ON agent_task(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_task_status ON agent_task(status);
CREATE INDEX IF NOT EXISTS idx_agent_task_requested_by ON agent_task(requested_by);
CREATE INDEX IF NOT EXISTS idx_agent_task_created ON agent_task(created_at DESC);

-- Create indexes for agent_action
CREATE INDEX IF NOT EXISTS idx_agent_action_task ON agent_action(task_id);
CREATE INDEX IF NOT EXISTS idx_agent_action_status ON agent_action(approval_status);
CREATE INDEX IF NOT EXISTS idx_agent_action_created ON agent_action(created_at DESC);

-- Add comments
COMMENT ON TABLE agent_definition IS 'AI Agent definitions - agents propose, humans approve';
COMMENT ON TABLE agent_task IS 'Agent tasks with approval workflow';
COMMENT ON TABLE agent_action IS 'Individual actions proposed by agents';
COMMENT ON COLUMN agent_task.context_data IS 'Context used for task proposal';
COMMENT ON COLUMN agent_task.result_data IS 'Result after execution';
COMMENT ON COLUMN agent_action.action_payload IS 'Action details and parameters';

-- Create view for pending tasks
CREATE OR REPLACE VIEW agent_pending_tasks AS
SELECT 
    t.*,
    a.name as agent_name,
    a.agent_type
FROM agent_task t
JOIN agent_definition a ON t.agent_id = a.id
WHERE t.status = 'pending'
ORDER BY t.created_at DESC;

-- Create view for task statistics
CREATE OR REPLACE VIEW agent_task_stats AS
SELECT 
    agent_id,
    COUNT(*) as total_tasks,
    COUNT(*) FILTER (WHERE status = 'pending') as pending_tasks,
    COUNT(*) FILTER (WHERE status = 'approved') as approved_tasks,
    COUNT(*) FILTER (WHERE status = 'executed') as executed_tasks,
    COUNT(*) FILTER (WHERE status = 'rejected') as rejected_tasks,
    COUNT(*) FILTER (WHERE status = 'failed') as failed_tasks
FROM agent_task
GROUP BY agent_id;

-- Create function to update task status
CREATE OR REPLACE FUNCTION update_task_status()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'executed' THEN
        NEW.executed_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for task status updates
CREATE TRIGGER trigger_update_task_status
BEFORE UPDATE ON agent_task
FOR EACH ROW
EXECUTE FUNCTION update_task_status();

-- Insert default agent definitions
INSERT INTO agent_definition (name, description, agent_type) VALUES
    ('Diagnostic Agent', 'Analyzes system health and identifies issues', 'diagnostic_agent'),
    ('Maintenance Agent', 'Suggests maintenance procedures', 'maintenance_agent'),
    ('Recovery Agent', 'Proposes recovery actions for failed systems', 'recovery_agent'),
    ('Knowledge Agent', 'Retrieves relevant knowledge and documentation', 'knowledge_agent'),
    ('Timeline Agent', 'Analyzes historical patterns and timelines', 'timeline_agent')
ON CONFLICT DO NOTHING;

COMMIT;
