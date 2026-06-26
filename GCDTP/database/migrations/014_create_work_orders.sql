-- Migration 014: Work Order Engine
-- Creates work_orders, inspection_tasks, and maintenance_tasks tables
-- Maintains foreign key relationship to assets

BEGIN;

-- Create priority enum
DO $$ BEGIN
    CREATE TYPE work_order_priority AS ENUM ('low', 'medium', 'high', 'critical');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create status enum
DO $$ BEGIN
    CREATE TYPE work_order_status AS ENUM (
        'pending', 
        'in_progress', 
        'completed', 
        'cancelled',
        'on_hold'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create category enum
DO $$ BEGIN
    CREATE TYPE work_order_category AS ENUM (
        'inspection',
        'preventive',
        'corrective',
        'emergency',
        'routine'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create work_orders table
CREATE TABLE IF NOT EXISTS work_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority work_order_priority NOT NULL DEFAULT 'medium',
    status work_order_status NOT NULL DEFAULT 'pending',
    category work_order_category NOT NULL DEFAULT 'routine',
    assigned_to VARCHAR(255),
    created_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    due_date TIMESTAMP WITH TIME ZONE,
    estimated_hours DECIMAL(10, 2),
    actual_hours DECIMAL(10, 2),
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    created_session_id VARCHAR(255),
    CONSTRAINT valid_priority CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    CONSTRAINT valid_status CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled', 'on_hold')),
    CONSTRAINT valid_category CHECK (category IN ('inspection', 'preventive', 'corrective', 'emergency', 'routine'))
);

-- Create indexes for work_orders
CREATE INDEX IF NOT EXISTS idx_work_orders_asset_id ON work_orders(asset_id);
CREATE INDEX IF NOT EXISTS idx_work_orders_status ON work_orders(status);
CREATE INDEX IF NOT EXISTS idx_work_orders_priority ON work_orders(priority);
CREATE INDEX IF NOT EXISTS idx_work_orders_category ON work_orders(category);
CREATE INDEX IF NOT EXISTS idx_work_orders_assigned_to ON work_orders(assigned_to);
CREATE INDEX IF NOT EXISTS idx_work_orders_created_at ON work_orders(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_work_orders_due_date ON work_orders(due_date);

-- Create inspection_tasks table
CREATE TABLE IF NOT EXISTS inspection_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    work_order_id UUID NOT NULL REFERENCES work_orders(id) ON DELETE CASCADE,
    asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    inspection_type VARCHAR(100) NOT NULL,
    inspection_method VARCHAR(100),
    checklist JSONB DEFAULT '[]',
    results JSONB DEFAULT '{}',
    inspector VARCHAR(255),
    inspection_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    findings TEXT,
    recommendations TEXT,
    condition_rating INTEGER CHECK (condition_rating >= 1 AND condition_rating <= 5),
    next_inspection_date TIMESTAMP WITH TIME ZONE,
    attachments JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT valid_inspection_type CHECK (inspection_type IN ('visual', 'technical', 'safety', 'environmental', 'performance'))
);

-- Create indexes for inspection_tasks
CREATE INDEX IF NOT EXISTS idx_inspection_tasks_work_order_id ON inspection_tasks(work_order_id);
CREATE INDEX IF NOT EXISTS idx_inspection_tasks_asset_id ON inspection_tasks(asset_id);
CREATE INDEX IF NOT EXISTS idx_inspection_tasks_inspection_date ON inspection_tasks(inspection_date DESC);
CREATE INDEX IF NOT EXISTS idx_inspection_tasks_next_date ON inspection_tasks(next_inspection_date);

-- Create maintenance_tasks table
CREATE TABLE IF NOT EXISTS maintenance_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    work_order_id UUID NOT NULL REFERENCES work_orders(id) ON DELETE CASCADE,
    asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    maintenance_type VARCHAR(100) NOT NULL,
    parts_used JSONB DEFAULT '[]',
    labor_hours DECIMAL(10, 2) DEFAULT 0,
    technician VARCHAR(255),
    task_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    failure_symptoms TEXT,
    root_cause TEXT,
    corrective_action TEXT,
    cost DECIMAL(12, 2) DEFAULT 0,
    warranty_info JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT valid_maintenance_type CHECK (maintenance_type IN ('repair', 'replacement', 'calibration', 'alignment', 'lubrication', 'cleaning', 'upgrade')),
    CONSTRAINT valid_task_status CHECK (task_status IN ('pending', 'in_progress', 'completed', 'cancelled'))
);

-- Create indexes for maintenance_tasks
CREATE INDEX IF NOT EXISTS idx_maintenance_tasks_work_order_id ON maintenance_tasks(work_order_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_tasks_asset_id ON maintenance_tasks(asset_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_tasks_status ON maintenance_tasks(task_status);
CREATE INDEX IF NOT EXISTS idx_maintenance_tasks_completed_at ON maintenance_tasks(completed_at);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_work_orders_updated_at
    BEFORE UPDATE ON work_orders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_inspection_tasks_updated_at
    BEFORE UPDATE ON inspection_tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_maintenance_tasks_updated_at
    BEFORE UPDATE ON maintenance_tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create view for work order summary
CREATE OR REPLACE VIEW work_order_summary AS
SELECT 
    wo.id,
    wo.asset_id,
    a.name AS asset_name,
    a.asset_type AS asset_type,
    wo.title,
    wo.description,
    wo.priority,
    wo.status,
    wo.category,
    wo.assigned_to,
    wo.created_at,
    wo.updated_at,
    wo.completed_at,
    wo.due_date,
    COUNT(DISTINCT it.id) AS inspection_count,
    COUNT(DISTINCT mt.id) AS maintenance_count,
    CASE 
        WHEN wo.status = 'completed' THEN 'closed'
        WHEN wo.due_date < NOW() AND wo.status NOT IN ('completed', 'cancelled') THEN 'overdue'
        WHEN wo.status = 'in_progress' THEN 'active'
        ELSE 'open'
    END AS work_order_state
FROM work_orders wo
LEFT JOIN assets a ON wo.asset_id = a.id
LEFT JOIN inspection_tasks it ON wo.id = it.work_order_id
LEFT JOIN maintenance_tasks mt ON wo.id = mt.work_order_id
GROUP BY wo.id, a.name, a.asset_type, wo.title, wo.description, wo.priority, wo.status, wo.category, wo.assigned_to, wo.created_at, wo.updated_at, wo.completed_at, wo.due_date;

COMMENT ON TABLE work_orders IS 'Asset-centric work orders for inspection and maintenance';
COMMENT ON TABLE inspection_tasks IS 'Inspection tasks linked to work orders';
COMMENT ON TABLE maintenance_tasks IS 'Maintenance tasks linked to work orders';

COMMIT;
