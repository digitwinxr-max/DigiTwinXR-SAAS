"""
EMQX MQTT Integration Module

External telemetry ingestion layer for FastAPI.
FastAPI remains authoritative for business logic.

Components:
- MQTT Client
- Topic Registry
- Subscription Manager
- Message Router
- Device Registry
- MQTT Validator
"""

from .mqtt_types import (
    QoSLevel,
    ConnectionStatus,
    MessageDirection,
    DeviceActivity,
    DeviceGroup,
    Device,
    MQTTTopic,
    Subscription,
    MQTTMessage,
    TopicSubscriptionCount,
    DeviceStatusSummary,
)

from .mqtt_client import MQTTClient, MQTTClientError, MQTTTopicBuilder
from .topic_registry import TopicRegistry
from .subscription_manager import SubscriptionManager, WildcardSubscriptionManager
from .message_router import MessageRouter, MeasurementRouter
from .device_registry import DeviceRegistry
from .mqtt_validator import MQTTValidator


__all__ = [
    # Enums
    "QoSLevel",
    "ConnectionStatus",
    "MessageDirection",
    "DeviceActivity",
    # Types
    "DeviceGroup",
    "Device",
    "MQTTTopic",
    "Subscription",
    "MQTTMessage",
    "TopicSubscriptionCount",
    "DeviceStatusSummary",
    # Client
    "MQTTClient",
    "MQTTClientError",
    "MQTTTopicBuilder",
    # Managers
    "TopicRegistry",
    "SubscriptionManager",
    "WildcardSubscriptionManager",
    "MessageRouter",
    "MeasurementRouter",
    "DeviceRegistry",
    # Validators
    "MQTTValidator",
]
