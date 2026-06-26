"""
Tests for EMQX MQTT Integration

Tests devices, topics, subscriptions, message routing, QoS, wildcards, heartbeat, validation, and timeline integration.
"""

import pytest
from datetime import datetime, timedelta
from backend.src.integrations.emqx import (
    MQTTClient,
    TopicRegistry,
    SubscriptionManager,
    DeviceRegistry,
    MessageRouter,
    MQTTValidator,
    QoSLevel,
    ConnectionStatus,
    MQTTTopic,
    Subscription,
    Device,
    MQTTMessage,
    MessageDirection,
)


class TestMQTTTypes:
    """Tests for MQTT types."""
    
    def test_qos_level_values(self):
        """Test QoS level values."""
        assert QoSLevel.QOS_0.value == "qos_0"
        assert QoSLevel.QOS_1.value == "qos_1"
        assert QoSLevel.QOS_2.value == "qos_2"
    
    def test_connection_status_values(self):
        """Test connection status values."""
        assert ConnectionStatus.CONNECTED.value == "connected"
        assert ConnectionStatus.DISCONNECTED.value == "disconnected"
        assert ConnectionStatus.ERROR.value == "error"


class TestMQTTTopic:
    """Tests for MQTT topic."""
    
    def test_create_topic(self):
        """Test creating an MQTT topic."""
        topic = MQTTTopic(
            id="topic-1",
            topic_name="/gc/test"
        )
        
        assert topic.id == "topic-1"
        assert topic.topic_name == "/gc/test"
        assert topic.is_enabled is True
    
    def test_topic_matches(self):
        """Test topic matching."""
        topic = MQTTTopic(
            id="topic-1",
            topic_name="/gc/devices/+/status",
            is_enabled=True
        )
        
        assert topic.matches("/gc/devices/device1/status") is True
        assert topic.matches("/gc/devices/device2/status") is True
        assert topic.matches("/gc/assets/asset1/status") is False
    
    def test_topic_matches_multi_level(self):
        """Test multi-level wildcard matching."""
        topic = MQTTTopic(
            id="topic-1",
            topic_name="/gc/devices/#",
            is_enabled=True
        )
        
        assert topic.matches("/gc/devices/device1/status") is True
        assert topic.matches("/gc/devices/device1/measurements/temp") is True
    
    def test_disabled_topic_does_not_match(self):
        """Test that disabled topics don't match."""
        topic = MQTTTopic(
            id="topic-1",
            topic_name="/gc/test",
            is_enabled=False
        )
        
        assert topic.matches("/gc/test") is False


class TestDevice:
    """Tests for device."""
    
    def test_create_device(self):
        """Test creating a device."""
        device = Device(
            id="device-1",
            device_id="client-1",
            name="Test Device"
        )
        
        assert device.id == "device-1"
        assert device.device_id == "client-1"
        assert device.name == "Test Device"
    
    def test_device_is_connected(self):
        """Test device connection status."""
        device = Device(
            id="device-1",
            device_id="client-1",
            name="Test",
            status=ConnectionStatus.CONNECTED
        )
        
        assert device.is_connected is True


class TestTopicRegistry:
    """Tests for topic registry."""
    
    @pytest.fixture
    def registry(self):
        """Create topic registry."""
        return TopicRegistry()
    
    def test_register_topic(self, registry):
        """Test registering a topic."""
        topic = registry.register_topic("/gc/test")
        
        assert topic is not None
        assert topic.topic_name == "/gc/test"
    
    def test_get_topic_by_name(self, registry):
        """Test getting topic by name."""
        registry.register_topic("/gc/test")
        
        topic = registry.get_topic_by_name("/gc/test")
        
        assert topic is not None
        assert topic.topic_name == "/gc/test"
    
    def test_enable_topic(self, registry):
        """Test enabling a topic."""
        topic = registry.register_topic("/gc/test")
        topic.is_enabled = False
        
        enabled = registry.enable_topic(topic.id)
        
        assert enabled.is_enabled is True
    
    def test_disable_topic(self, registry):
        """Test disabling a topic."""
        topic = registry.register_topic("/gc/test")
        
        disabled = registry.disable_topic(topic.id)
        
        assert disabled.is_enabled is False
    
    def test_find_matching_topics(self, registry):
        """Test finding matching topics."""
        registry.register_topic("/gc/devices/+/status")
        registry.register_topic("/gc/assets/#")
        
        matches = registry.find_matching_topics("/gc/devices/device1/status")
        
        assert len(matches) == 1
        assert matches[0].topic_name == "/gc/devices/+/status"


class TestSubscriptionManager:
    """Tests for subscription manager."""
    
    @pytest.fixture
    def manager(self):
        """Create subscription manager."""
        return SubscriptionManager()
    
    def test_create_subscription(self, manager):
        """Test creating a subscription."""
        subscription = manager.create_subscription(
            topic_id="topic-1",
            device_id="device-1"
        )
        
        assert subscription is not None
        assert subscription.topic_id == "topic-1"
        assert subscription.device_id == "device-1"
    
    def test_delete_subscription(self, manager):
        """Test deleting a subscription."""
        subscription = manager.create_subscription(
            topic_id="topic-1",
            device_id="device-1"
        )
        subscription_id = subscription.id
        
        result = manager.delete_subscription(subscription_id)
        
        assert result is True
        assert manager.get_subscription(subscription_id) is None
    
    def test_get_subscriptions_for_device(self, manager):
        """Test getting subscriptions for device."""
        manager.create_subscription(topic_id="topic-1", device_id="device-1")
        manager.create_subscription(topic_id="topic-2", device_id="device-1")
        
        subscriptions = manager.get_subscriptions_for_device("device-1")
        
        assert len(subscriptions) == 2


class TestDeviceRegistry:
    """Tests for device registry."""
    
    @pytest.fixture
    def registry(self):
        """Create device registry."""
        return DeviceRegistry()
    
    def test_register_device(self, registry):
        """Test registering a device."""
        device = registry.register_device(
            device_id="client-1",
            name="Test Device"
        )
        
        assert device is not None
        assert device.device_id == "client-1"
    
    def test_connect_device(self, registry):
        """Test connecting a device."""
        registry.register_device(device_id="client-1", name="Test")
        
        device = registry.connect_device("client-1")
        
        assert device.is_connected is True
    
    def test_disconnect_device(self, registry):
        """Test disconnecting a device."""
        registry.register_device(device_id="client-1", name="Test")
        registry.connect_device("client-1")
        
        device = registry.disconnect_device("client-1")
        
        assert device.is_connected is False
    
    def test_record_message(self, registry):
        """Test recording a message."""
        registry.register_device(device_id="client-1", name="Test")
        
        device = registry.record_message("client-1")
        
        assert device.last_message_at is not None
    
    def test_heartbeat(self, registry):
        """Test device heartbeat."""
        registry.register_device(device_id="client-1", name="Test")
        
        device = registry.heartbeat("client-1")
        
        assert device is not None
    
    def test_get_connected_devices(self, registry):
        """Test getting connected devices."""
        registry.register_device(device_id="client-1", name="Test1")
        registry.register_device(device_id="client-2", name="Test2")
        
        registry.connect_device("client-1")
        
        connected = registry.get_connected_devices()
        
        assert len(connected) == 1


class TestMessageRouter:
    """Tests for message router."""
    
    @pytest.fixture
    def router(self):
        """Create message router."""
        return MessageRouter()
    
    def test_route_message(self, router):
        """Test routing a message."""
        message = MQTTMessage(
            id="msg-1",
            topic_name="/gc/test",
            payload={"data": "test"}
        )
        
        results = router.route_message(message)
        
        assert "routed" in str(results) or "routed" in str(results.get("assets", {}))
    
    def test_register_handler(self, router):
        """Test registering a handler."""
        handler_called = []
        
        def handler(msg):
            handler_called.append(msg)
        
        router.register_handler("/gc/test", handler)


class TestMQTTValidator:
    """Tests for MQTT validator."""
    
    @pytest.fixture
    def validator(self):
        """Create validator."""
        return MQTTValidator()
    
    def test_validate_topic(self, validator):
        """Test validating a topic."""
        topic = MQTTTopic(
            id="topic-1",
            topic_name="/gc/test"
        )
        
        issues = validator.validate_topic(topic)
        
        assert len(issues) == 0
    
    def test_validate_topic_name_valid(self, validator):
        """Test validating a valid topic name."""
        issues = validator.validate_topic_name("/gc/test")
        
        assert len(issues) == 0
    
    def test_validate_topic_name_no_leading_slash(self, validator):
        """Test validation with no leading slash."""
        issues = validator.validate_topic_name("gc/test")
        
        assert len(issues) > 0
    
    def test_validate_topic_name_wildcard_at_end(self, validator):
        """Test validation with wildcard at end."""
        issues = validator.validate_topic_name("/gc/devices/#")
        
        assert len(issues) == 0
    
    def test_validate_topic_name_wildcard_middle(self, validator):
        """Test validation with wildcard in middle."""
        issues = validator.validate_topic_name("/gc/#/test")
        
        assert len(issues) > 0
    
    def test_check_duplicate_topic(self, validator):
        """Test checking for duplicate topics."""
        existing = {"/gc/test"}
        
        is_duplicate = validator.check_duplicate_topic("/gc/test", existing)
        
        assert is_duplicate is True
    
    def test_validate_device(self, validator):
        """Test validating a device."""
        device = Device(
            id="device-1",
            device_id="client-1",
            name="Test Device"
        )
        
        issues = validator.validate_device(device)
        
        assert len(issues) == 0


class TestMQTTClient:
    """Tests for MQTT client."""
    
    @pytest.fixture
    def client(self):
        """Create MQTT client."""
        return MQTTClient(broker_host="localhost", broker_port=1883)
    
    def test_client_initialization(self, client):
        """Test client initialization."""
        assert client.broker_host == "localhost"
        assert client.broker_port == 1883
    
    def test_build_device_topic(self, client):
        """Test building device topic."""
        topic = client.build_device_topic("device-1", "status")
        
        assert topic == "/gc/devices/device-1/status"
    
    def test_build_asset_topic(self, client):
        """Test building asset topic."""
        topic = client.build_asset_topic("asset-1", "events")
        
        assert topic == "/gc/assets/asset-1/events"


class TestQoSLevel:
    """Tests for QoS levels."""
    
    def test_qos_0(self):
        """Test QoS 0 (at most once)."""
        assert QoSLevel.QOS_0.value == "qos_0"
    
    def test_qos_1(self):
        """Test QoS 1 (at least once)."""
        assert QoSLevel.QOS_1.value == "qos_1"
    
    def test_qos_2(self):
        """Test QoS 2 (exactly once)."""
        assert QoSLevel.QOS_2.value == "qos_2"


class TestMessageDirection:
    """Tests for message direction."""
    
    def test_incoming(self):
        """Test incoming direction."""
        assert MessageDirection.INCOMING.value == "incoming"
    
    def test_outgoing(self):
        """Test outgoing direction."""
        assert MessageDirection.OUTGOING.value == "outgoing"


class TestMQTTMessage:
    """Tests for MQTT message."""
    
    def test_create_message(self):
        """Test creating a message."""
        message = MQTTMessage(
            id="msg-1",
            topic_name="/gc/test",
            payload={"data": "test"}
        )
        
        assert message.id == "msg-1"
        assert message.topic_name == "/gc/test"
    
    def test_message_is_incoming(self):
        """Test message is incoming."""
        message = MQTTMessage(
            id="msg-1",
            topic_name="/gc/test",
            payload={},
            direction=MessageDirection.INCOMING
        )
        
        assert message.is_incoming is True


class TestDeviceGroup:
    """Tests for device group."""
    
    @pytest.fixture
    def registry(self):
        """Create device registry."""
        return DeviceRegistry()
    
    def test_create_group(self, registry):
        """Test creating a device group."""
        group = registry.create_group(name="Test Group")
        
        assert group is not None
        assert group.name == "Test Group"
    
    def test_add_device_to_group(self, registry):
        """Test adding device to group."""
        device = registry.register_device(device_id="client-1", name="Test")
        group = registry.create_group(name="Test Group")
        
        result = registry.add_device_to_group(device.id, group.id)
        
        assert result is True
        assert device.group_id == group.id


class TestWildcardSubscription:
    """Tests for wildcard subscriptions."""
    
    @pytest.fixture
    def manager(self):
        """Create subscription manager."""
        return SubscriptionManager()
    
    def test_create_wildcard_subscription(self, manager):
        """Test creating a wildcard subscription."""
        # Create base topic first
        topic = MQTTTopic(id="topic-1", topic_name="/gc/devices/+/status")
        
        subscription = manager.create_subscription(
            topic_id=topic.id,
            device_id="device-1",
            subscription_type="wildcard"
        )
        
        assert subscription.subscription_type == "wildcard"
