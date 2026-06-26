-- Migration 042: Cognitive Copilot Foundation
-- Creates tables for copilot sessions and messages
-- This is read-only AI context - NO LLM integration yet

BEGIN;

-- Create role enum for messages
DO $$ BEGIN
    CREATE TYPE message_role AS ENUM (
        'user',
        'assistant',
        'system'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create copilot_sessions table
CREATE TABLE IF NOT EXISTS copilot_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_activity_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create copilot_messages table
CREATE TABLE IF NOT EXISTS copilot_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES copilot_sessions(id) ON DELETE CASCADE,
    role message_role NOT NULL,
    message TEXT NOT NULL,
    context_data JSONB,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for copilot_sessions
CREATE INDEX IF NOT EXISTS idx_copilot_sessions_created ON copilot_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_copilot_sessions_activity ON copilot_sessions(last_activity_at DESC);

-- Create indexes for copilot_messages
CREATE INDEX IF NOT EXISTS idx_copilot_messages_session ON copilot_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_copilot_messages_timestamp ON copilot_messages(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_copilot_messages_role ON copilot_messages(role);

-- Add comments
COMMENT ON TABLE copilot_sessions IS 'Cognitive Copilot sessions - stores conversation context';
COMMENT ON TABLE copilot_messages IS 'Copilot messages - user queries and assistant responses';
COMMENT ON COLUMN copilot_messages.context_data IS 'JSON context used to generate response';

-- Create view for session summaries
CREATE OR REPLACE VIEW copilot_session_summary AS
SELECT 
    s.id,
    s.session_name,
    s.created_at,
    s.last_activity_at,
    COUNT(m.id) as message_count,
    COUNT(m.id) FILTER (WHERE m.role = 'user') as user_message_count,
    COUNT(m.id) FILTER (WHERE m.role = 'assistant') as assistant_message_count
FROM copilot_sessions s
LEFT JOIN copilot_messages m ON s.id = m.session_id
GROUP BY s.id;

-- Create function to update last activity
CREATE OR REPLACE FUNCTION update_session_activity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE copilot_sessions 
    SET last_activity_at = NOW()
    WHERE id = NEW.session_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for auto-updating session activity
CREATE TRIGGER trigger_update_session_activity
AFTER INSERT ON copilot_messages
FOR EACH ROW
EXECUTE FUNCTION update_session_activity();

COMMIT;
