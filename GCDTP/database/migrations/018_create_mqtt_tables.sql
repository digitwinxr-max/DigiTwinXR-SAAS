-- Migration 018: EMQX MQTT Integration
-- Creates devices, mqtt_topics, mqtt_subscriptions, mqtt_messages, and device_groups tables
-- Maintains backward compatibility

BEGIN;

-- Create qos_level enum
DO $$ BEGIN
    CREATE TYPE qos_level AS ENUM (
        'qos_0',
        'qos_1',
        'qos_2'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create connection_status enum
DO $$ BEGIN
    CREATE TYPE connection_status AS ENUM (
        'connected',
        'disconnected',
        'error'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create device_groups table
CREATE TABLE IF NOT EXISTS device_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_group_id UUID REFERENCES device_groups(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for device_groups
CREATE INDEX IF NOT EXISTS idx_device_groups_name ON device_groups(name);
CREATE INDEX IF NOT EXISTS idx_device_groups_parent ON device_groups(parent_group_id);

-- Create devices table
CREATE TABLE IF NOT EXISTS devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100),
    group_id UUID REFERENCES device_groups(id) ON DELETE SET NULL,
    asset_id UUID REFERENCES assets(id) ON DELETE SET NULL,
    status connection_status NOT NULL DEFAULT 'disconnected',
    qos qos_level DEFAULT 'qos_0',
    client_id VARCHAR(255),
    username VARCHAR(255),
    last_connected_at TIMESTAMP WITH TIME ZONE,
    last_disconnected_at TIMESTAMP WITH TIME ZONE,
    last_message_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for devices
CREATE INDEX IF NOT EXISTS idx_devices_device_id ON devices(device_id);
CREATE INDEX IF NOT EXISTS idx_devices_group_id ON devices(group_id);
CREATE INDEX IF NOT EXISTS idx_devices_asset_id ON devices(asset_id);
CREATE INDEX IF NOT EXISTS idx_devices_status ON devices(status);
CREATE INDEX IF NOT EXISTS idx_devices_type ON devices(type);

-- Create mqtt_topics table
CREATE TABLE IF NOT EXISTS mqtt_topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_name VARCHAR(500) UNIQUE NOT NULL,
    description TEXT,
    qos qos_level DEFAULT 'qos_1',
    is_enabled BOOLEAN DEFAULT TRUE,
    is_system BOOLEAN DEFAULT FALSE,
    retain BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for mqtt_topics
CREATE INDEX IF NOT EXISTS idx_topics_topic_name ON mqtt_topics(topic_name);
CREATE INDEX IF NOT EXISTS idx_topics_is_enabled ON mqtt_topics(is_enabled);

-- Create mqtt_subscriptions table
CREATE TABLE IF NOT EXISTS mqtt_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_id UUID REFERENCES mqtt_topics(id) ON DELETE CASCADE,
    device_id UUID REFERENCES devices(id) ON DELETE CASCADE,
    subscription_type VARCHAR(50) NOT NULL DEFAULT 'topic',
    filter_pattern VARCHAR(500),
    qos qos_level DEFAULT 'qos_1',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(topic_id, device_id)
);

-- Create indexes for mqtt_subscriptions
CREATE INDEX IF NOT EXISTS idx_subscriptions_topic_id ON mqtt_subscriptions(topic_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_device_id ON mqtt_subscriptions(device_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_is_active ON mqtt_subscriptions(is_active);

-- Create mqtt_messages table
CREATE TABLE IF NOT EXISTS mqtt_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_id UUID REFERENCES mqtt_topics(id) ON DELETE SET NULL,
    device_id UUID REFERENCES devices(id) ON DELETE SET NULL,
    message_id VARCHAR(255),
    topic_name VARCHAR(500) NOT NULL,
    payload JSONB,
    qos qos_level DEFAULT 'qos_0',
    retained BOOLEAN DEFAULT FALSE,
    direction VARCHAR(10) NOT NULL,  -- 'incoming' or 'outgoing'
    routing_target VARCHAR(255),
    error_message TEXT,
    received_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for mqtt_messages
CREATE INDEX IF NOT EXISTS idx_messages_topic_id ON mqtt_messages(topic_id);
CREATE INDEX IF NOT EXISTS idx_messages_device_id ON mqtt_messages(device_id);
CREATE INDEX IF NOT EXISTS idx_messages_topic_name ON mqtt_messages(topic_name);
CREATE INDEX IF NOT EXISTS idx_messages_received_at ON mqtt_messages(received_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_direction ON mqtt_messages(direction);

-- Create device_group_membership table
CREATE TABLE IF NOT EXISTS device_group_membership (
    device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    group_id UUID NOT NULL REFERENCES device_groups(id) ON DELETE CASCADE,
    joined_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    PRIMARY KEY (device_id, group_id)
);

-- Create indexes for device_group_membership
CREATE INDEX IF NOT EXISTS idx_membership_device ON device_group_membership(device_id);
CREATE INDEX IF NOT EXISTS idx_membership_group ON device_group_membership(group_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_device_groups_updated_at
    BEFORE UPDATE ON device_groups
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_devices_updated_at
    BEFORE UPDATE ON devices
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_topics_updated_at
    BEFORE UPDATE ON mqtt_topics
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at
    BEFORE UPDATE ON mqtt_subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create view for device status summary
CREATE OR REPLACE VIEW device_status_summary AS
SELECT 
    d.id,
    d.device_id,
    d.name,
    d.type,
    d.status,
    d.group_id,
    dg.name AS group_name,
    d.asset_id,
    a.name AS asset_name,
    d.last_connected_at,
    d.last_message_at,
    CASE 
        WHEN d.last_message_at IS NOT NULL 
            AND d.last_message_at > NOW() - INTERVAL '5 minutes'
        THEN 'active'
        WHEN d.status = 'connected' THEN 'idle'
        ELSE 'offline'
    END AS activity_status
FROM devices d
LEFT JOIN device_groups dg ON d.group_id = dg.id
LEFT JOIN assets a ON d.asset_id = a.id;

-- Create view for topic subscription counts
CREATE OR REPLACE VIEW topic_subscription_counts AS
SELECT 
    t.id,
    t.topic_name,
    t.qos,
    t.is_enabled,
    COUNT(DISTINCT s.device_id) AS subscriber_count,
    COUNT(DISTINCT m.id) AS message_count,
    MAX(m.received_at) AS last_message_at
FROM mqtt_topics t
LEFT JOIN mqtt_subscriptions s ON t.id = s.topic_id AND s.is_active = TRUE
LEFT JOIN mqtt_messages m ON t.id = m.topic_id
GROUP BY t.id, t.topic_name, t.qos, t.is_enabled;

-- Create view for message throughput
CREATE OR REPLACE VIEW message_throughput AS
SELECT 
    date_trunc('hour', received_at) AS hour,
    COUNT(*) AS total_messages,
    COUNT(DISTINCT device_id) AS unique_devices,
    COUNT(DISTINCT topic_name) AS unique_topics
FROM mqtt_messages
WHERE received_at > NOW() - INTERVAL '24 hours'
GROUP BY date_trunc('hour', received_at)
ORDER BY hour DESC;

COMMENT ON TABLE devices IS 'IoT devices connected via EMQX MQTT';
COMMENT ON TABLE device_groups IS 'Device groupings for organization';
COMMENT ON TABLE mqtt_topics IS 'Registered MQTT topics';
COMMENT ON TABLE mqtt_subscriptions IS 'Device topic subscriptions';
COMMENT ON TABLE mqtt_messages IS 'MQTT message history';

COMMIT;
