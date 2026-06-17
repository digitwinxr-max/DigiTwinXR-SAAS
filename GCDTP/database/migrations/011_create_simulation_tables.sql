-- Migration: 011_create_simulation_tables.sql
-- Scenario Simulation Engine
-- Creates tables for scenario simulations and results

-- Create ENUM types
DO $$ BEGIN
    CREATE TYPE scenario_type AS ENUM (
        'failure',
        'recovery',
        'maintenance',
        'custom'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE scenario_status AS ENUM (
        'draft',
        'completed'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create scenarios table
CREATE TABLE IF NOT EXISTS scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    scenario_type scenario_type NOT NULL DEFAULT 'failure',
    root_asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    severity VARCHAR(20) NOT NULL DEFAULT 'CRITICAL',
    status scenario_status NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_severity CHECK (severity IN ('WARNING', 'CRITICAL'))
);

-- Create indexes for scenarios
CREATE INDEX IF NOT EXISTS idx_scenarios_root_asset_id 
    ON scenarios(root_asset_id);

CREATE INDEX IF NOT EXISTS idx_scenarios_scenario_type 
    ON scenarios(scenario_type);

CREATE INDEX IF NOT EXISTS idx_scenarios_status 
    ON scenarios(status);

CREATE INDEX IF NOT EXISTS idx_scenarios_created_at 
    ON scenarios(created_at DESC);

-- Create scenario_results table
CREATE TABLE IF NOT EXISTS scenario_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID NOT NULL REFERENCES scenarios(id) ON DELETE CASCADE,
    asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    predicted_health FLOAT NOT NULL DEFAULT 100.0,
    current_health FLOAT NOT NULL DEFAULT 100.0,
    delta_health FLOAT NOT NULL DEFAULT 0.0,
    propagation_depth INTEGER NOT NULL DEFAULT 0,
    relationship_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for scenario_results
CREATE INDEX IF NOT EXISTS idx_scenario_results_scenario_id 
    ON scenario_results(scenario_id);

CREATE INDEX IF NOT EXISTS idx_scenario_results_asset_id 
    ON scenario_results(asset_id);

CREATE INDEX IF NOT EXISTS idx_scenario_results_depth 
    ON scenario_results(propagation_depth);

CREATE INDEX IF NOT EXISTS idx_scenario_results_delta 
    ON scenario_results(delta_health);

-- Add comments for documentation
COMMENT ON TABLE scenarios IS 
    'Stores scenario definitions for failure/recovery simulations';

COMMENT ON COLUMN scenarios.root_asset_id IS 
    'The asset where the simulation starts';

COMMENT ON COLUMN scenarios.severity IS 
    'Simulated event severity';

COMMENT ON COLUMN scenarios.status IS 
    'Draft scenarios are not executed, completed ones have results';

COMMENT ON TABLE scenario_results IS 
    'Stores simulation results - predicted vs current health';

COMMENT ON COLUMN scenario_results.predicted_health IS 
    'Simulated health after propagation';

COMMENT ON COLUMN scenario_results.current_health IS 
    'Actual health at simulation time';

COMMENT ON COLUMN scenario_results.delta_health IS 
    'Difference between predicted and current (negative = degradation)';

COMMENT ON COLUMN scenario_results.propagation_depth IS 
    'How far this asset is from the root asset';

COMMENT ON COLUMN scenario_results.relationship_path IS 
    'JSON array of relationship types leading to this asset';

-- Migration record
INSERT INTO schema_migrations (version, applied_at)
VALUES ('011', CURRENT_TIMESTAMP)
ON CONFLICT (version) DO NOTHING;
