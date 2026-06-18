-- Migration 045: Predictive Maintenance Engine
-- Deterministic scoring-based failure probability prediction
-- NO ML, NO neural networks, NO external AI

BEGIN;

-- Create risk_level enum
DO $$ BEGIN
    CREATE TYPE risk_level AS ENUM (
        'LOW',
        'MEDIUM',
        'HIGH',
        'CRITICAL'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create maintenance_type enum
DO $$ BEGIN
    CREATE TYPE maintenance_type AS ENUM (
        'preventive',
        'corrective',
        'predictive',
        'emergency',
        'inspection'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create maintenance_prediction table
CREATE TABLE IF NOT EXISTS maintenance_prediction (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID NOT NULL REFERENCES assets(id),
    prediction_date TIMESTAMP WITH TIME ZONE NOT NULL,
    failure_probability FLOAT NOT NULL CHECK (failure_probability >= 0 AND failure_probability <= 100),
    predicted_health FLOAT NOT NULL CHECK (predicted_health >= 0 AND predicted_health <= 100),
    risk_level risk_level NOT NULL,
    recommended_action TEXT,
    confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1),
    health_degradation_factor FLOAT DEFAULT 0,
    active_events_factor FLOAT DEFAULT 0,
    measurement_anomalies_factor FLOAT DEFAULT 0,
    maintenance_age_factor FLOAT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create maintenance_history table
CREATE TABLE IF NOT EXISTS maintenance_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID NOT NULL REFERENCES assets(id),
    work_order_id UUID,
    maintenance_type maintenance_type NOT NULL,
    maintenance_date TIMESTAMP WITH TIME ZONE NOT NULL,
    notes TEXT,
    cost FLOAT,
    duration_hours FLOAT,
    performed_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for maintenance_prediction
CREATE INDEX IF NOT EXISTS idx_prediction_asset ON maintenance_prediction(asset_id);
CREATE INDEX IF NOT EXISTS idx_prediction_date ON maintenance_prediction(prediction_date DESC);
CREATE INDEX IF NOT EXISTS idx_prediction_risk ON maintenance_prediction(risk_level);
CREATE INDEX IF NOT EXISTS idx_prediction_probability ON maintenance_prediction(failure_probability DESC);

-- Create indexes for maintenance_history
CREATE INDEX IF NOT EXISTS idx_history_asset ON maintenance_history(asset_id);
CREATE INDEX IF NOT EXISTS idx_history_date ON maintenance_history(maintenance_date DESC);
CREATE INDEX IF NOT EXISTS idx_history_type ON maintenance_history(maintenance_type);
CREATE INDEX IF NOT EXISTS idx_history_work_order ON maintenance_history(work_order_id);

-- Create views for prediction summary
CREATE OR REPLACE VIEW predictive_summary AS
SELECT 
    asset_id,
    COUNT(*) as prediction_count,
    AVG(failure_probability) as avg_failure_probability,
    MAX(failure_probability) as max_failure_probability,
    AVG(predicted_health) as avg_predicted_health,
    COUNT(*) FILTER (WHERE risk_level = 'CRITICAL') as critical_count,
    COUNT(*) FILTER (WHERE risk_level = 'HIGH') as high_count
FROM maintenance_prediction
WHERE prediction_date > NOW() - INTERVAL '30 days'
GROUP BY asset_id;

-- Create view for high-risk assets
CREATE OR REPLACE VIEW high_risk_assets AS
SELECT 
    mp.asset_id,
    a.name as asset_name,
    a.asset_type,
    mp.failure_probability,
    mp.predicted_health,
    mp.risk_level,
    mp.recommended_action,
    mp.prediction_date
FROM maintenance_prediction mp
JOIN assets a ON mp.asset_id = a.id
WHERE mp.id IN (
    SELECT DISTINCT ON (asset_id) id
    FROM maintenance_prediction
    ORDER BY asset_id, prediction_date DESC
)
AND mp.risk_level IN ('HIGH', 'CRITICAL')
ORDER BY mp.failure_probability DESC;

-- Create function to get prediction trend
CREATE OR REPLACE FUNCTION get_prediction_trend(asset_uuid UUID, days INTEGER DEFAULT 30)
RETURNS TABLE (
    prediction_date DATE,
    failure_probability FLOAT,
    predicted_health FLOAT,
    risk_level risk_level
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        DATE(mp.prediction_date) as prediction_date,
        mp.failure_probability,
        mp.predicted_health,
        mp.risk_level
    FROM maintenance_prediction mp
    WHERE mp.asset_id = asset_uuid
    AND mp.prediction_date > NOW() - (days || ' days')::INTERVAL
    ORDER BY mp.prediction_date ASC;
END;
$$ LANGUAGE plpgsql;

-- Create function for maintenance recommendations
CREATE OR REPLACE FUNCTION get_maintenance_recommendations(asset_uuid UUID)
RETURNS TABLE (
    recommendation TEXT,
    priority VARCHAR(20),
    reason TEXT
) AS $$
DECLARE
    current_health FLOAT;
    current_probability FLOAT;
    recent_events INTEGER;
    maintenance_age INTEGER;
BEGIN
    -- Get current state
    SELECT ph.health_score INTO current_health
    FROM health_status hs
    JOIN platforms p ON hs.platform_id = p.id
    JOIN platforms_assets pa ON p.id = pa.platform_id
    WHERE pa.asset_id = asset_uuid
    ORDER BY hs.recorded_at DESC
    LIMIT 1;
    
    -- Get recent predictions
    SELECT failure_probability INTO current_probability
    FROM maintenance_prediction
    WHERE asset_id = asset_uuid
    ORDER BY prediction_date DESC
    LIMIT 1;
    
    -- Get recent events count
    SELECT COUNT(*) INTO recent_events
    FROM events
    WHERE asset_id = asset_uuid
    AND created_at > NOW() - INTERVAL '7 days';
    
    -- Get days since last maintenance
    SELECT EXTRACT(DAY FROM NOW() - maintenance_date)::INTEGER INTO maintenance_age
    FROM maintenance_history
    WHERE asset_id = asset_uuid
    ORDER BY maintenance_date DESC
    LIMIT 1;
    
    -- Generate recommendations based on deterministic rules
    IF current_probability > 75 OR current_health < 40 THEN
        RETURN QUERY SELECT 'Emergency inspection required'::TEXT, 'CRITICAL'::VARCHAR, 
            'High failure probability or critical health'::TEXT;
        RETURN QUERY SELECT 'Schedule immediate maintenance'::TEXT, 'HIGH'::VARCHAR,
            'Preventive action needed'::TEXT;
    ELSIF current_probability > 50 OR current_health < 60 THEN
        RETURN QUERY SELECT 'Schedule maintenance within 7 days'::TEXT, 'HIGH'::VARCHAR,
            'Elevated failure risk'::TEXT;
    ELSIF current_probability > 25 OR current_health < 80 THEN
        RETURN QUERY SELECT 'Plan maintenance within 30 days'::TEXT, 'MEDIUM'::VARCHAR,
            'Moderate risk level'::TEXT;
    ELSE
        RETURN QUERY SELECT 'Continue regular monitoring'::TEXT, 'LOW'::VARCHAR,
            'Normal operation'::TEXT;
    END IF;
    
    IF recent_events > 3 THEN
        RETURN QUERY SELECT 'Investigate recent events'::TEXT, 'HIGH'::VARCHAR,
            'Multiple events in past week'::TEXT;
    END IF;
    
    IF maintenance_age IS NULL OR maintenance_age > 90 THEN
        RETURN QUERY SELECT 'Perform routine maintenance'::TEXT, 'MEDIUM'::VARCHAR,
            'Overdue for maintenance'::TEXT;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Add comments
COMMENT ON TABLE maintenance_prediction IS 'Deterministic failure predictions - NO ML/AI';
COMMENT ON TABLE maintenance_history IS 'Maintenance work history';
COMMENT ON COLUMN maintenance_prediction.failure_probability IS 'Deterministic score 0-100 based on formula';
COMMENT ON COLUMN maintenance_prediction.confidence IS 'Confidence in prediction based on data quality';
COMMENT ON FUNCTION get_prediction_trend IS 'Get prediction history for trend analysis';
COMMENT ON FUNCTION get_maintenance_recommendations IS 'Generate maintenance recommendations using deterministic rules';

COMMIT;
