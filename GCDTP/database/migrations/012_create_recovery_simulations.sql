-- Migration: 012_create_recovery_simulations.sql
-- Recovery Simulation Engine
-- Creates tables for recovery simulations and results

-- Create ENUM types
DO $$ BEGIN
    CREATE TYPE recovery_type AS ENUM (
        'manual',
        'automatic',
        'staged',
        'reroute'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create recovery_simulations table
CREATE TABLE IF NOT EXISTS recovery_simulations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID REFERENCES scenarios(id) ON DELETE CASCADE,
    strategy_name VARCHAR(255) NOT NULL,
    recovery_type recovery_type NOT NULL DEFAULT 'manual',
    estimated_duration_minutes INTEGER DEFAULT 60,
    recovery_order INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for recovery_simulations
CREATE INDEX IF NOT EXISTS idx_recovery_scenario_id 
    ON recovery_simulations(scenario_id);

CREATE INDEX IF NOT EXISTS idx_recovery_type 
    ON recovery_simulations(recovery_type);

CREATE INDEX IF NOT EXISTS idx_recovery_order 
    ON recovery_simulations(recovery_order);

-- Create recovery_results table
CREATE TABLE IF NOT EXISTS recovery_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recovery_simulation_id UUID NOT NULL REFERENCES recovery_simulations(id) ON DELETE CASCADE,
    asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    before_health FLOAT NOT NULL DEFAULT 0.0,
    after_health FLOAT NOT NULL DEFAULT 0.0,
    improvement FLOAT NOT NULL DEFAULT 0.0,
    recovery_depth INTEGER DEFAULT 0,
    remaining_risk VARCHAR(20) DEFAULT 'NONE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for recovery_results
CREATE INDEX IF NOT EXISTS idx_recovery_results_simulation_id 
    ON recovery_results(recovery_simulation_id);

CREATE INDEX IF NOT EXISTS idx_recovery_results_asset_id 
    ON recovery_results(asset_id);

CREATE INDEX IF NOT EXISTS idx_recovery_results_depth 
    ON recovery_results(recovery_depth);

-- Add comments for documentation
COMMENT ON TABLE recovery_simulations IS 
    'Stores recovery simulation definitions linked to scenarios';

COMMENT ON COLUMN recovery_simulations.scenario_id IS 
    'Link to parent scenario for context';

COMMENT ON COLUMN recovery_simulations.strategy_name IS 
    'Human-readable name for the recovery strategy';

COMMENT ON COLUMN recovery_simulations.recovery_type IS 
    'Type of recovery: manual, automatic, staged, or reroute';

COMMENT ON COLUMN recovery_simulations.estimated_duration_minutes IS 
    'Estimated time to complete recovery';

COMMENT ON COLUMN recovery_simulations.recovery_order IS 
    'Order of this recovery in a multi-stage plan';

COMMENT ON TABLE recovery_results IS 
    'Stores recovery simulation results';

COMMENT ON COLUMN recovery_results.before_health IS 
    'Asset health before recovery';

COMMENT ON COLUMN recovery_results.after_health IS 
    'Asset health after recovery';

COMMENT ON COLUMN recovery_results.improvement IS 
    'Health improvement from recovery';

COMMENT ON COLUMN recovery_results.remaining_risk IS 
    'Remaining risk level after recovery';

-- Recovery rules (for reference):
-- manual: restore +20 per asset
-- automatic: restore +30 per asset
-- staged: restore +15 per depth level
-- reroute: restore based on connected_to relationships

-- Migration record
INSERT INTO schema_migrations (version, applied_at)
VALUES ('012', CURRENT_TIMESTAMP)
ON CONFLICT (version) DO NOTHING;
