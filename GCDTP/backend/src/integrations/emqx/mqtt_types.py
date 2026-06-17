"""
MQTT Types

Core data types for EMQX MQTT integration.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class QoSLevel(str, Enum):
    """MQTT Quality of Service level."""
    QOS_0 = "qos_0"  # At most once
    QOS_1 = "qos_1"  # At least once
    QOS_2 = "qos_2"  # Exactly once


class ConnectionStatus(str, Enum):
    """Device connection status."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class MessageDirection(str, Enum):
    """Message direction."""
    INCOMING = "incoming"
    OUTGOING = "outgoing"


class DeviceActivity(str, Enum):
    """Device activity status."""
    ACTIVE = "active"    # Recent messages
    IDLE = "idle"       # Connected but no recent messages
    OFFLINE = "offline" # Disconnected


@dataclass
class DeviceGroup:
    """
    Device group for organization.
    """
    id: str
    name: str
    description: str = ""
    parent_group_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "parent_group_id": self.parent_group_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class Device:
    """
    IoT device connected via EMQX MQTT.
    """
    id: str
    device_id: str
    name: str
    type: str = ""
    
    # Grouping
    group_id: Optional[str] = None
    asset_id: Optional[str] = None
    
    # Connection
    status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    qos: QoSLevel = QoSLevel.QOS_0
    client_id: str = ""
    username: str = ""
    
    # Timestamps
    last_connected_at: Optional[datetime] = None
    last_disconnected_at: Optional[datetime] = None
    last_message_at: Optional[datetime] = None
    
    # State
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "device_id": self.device_id,
            "name": self.name,
            "type": self.type,
            "group_id": self.group_id,
            "asset_id": self.asset_id,
            "status": self.status.value,
            "qos": self.qos.value,
            "client_id": self.client_id,
            "last_connected_at": self.last_connected_at.isoformat() if self.last_connected_at else None,
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None,
            "is_active": self.is_active,
        }
    
    @property
    def is_connected(self) -> bool:
        """Check if device is connected."""
        return self.status == ConnectionStatus.CONNECTED
    
    @property
    def activity_status(self) -> DeviceActivity:
        """Get activity status."""
        if not self.is_connected:
            return DeviceActivity.OFFLINE
        
        if self.last_message_at:
            time_since = (datetime.utcnow() - self.last_message_at).total_seconds()
            if time_since < 300:  # 5 minutes
                return DeviceActivity.ACTIVE
        
        return DeviceActivity.IDLE


@dataclass
class MQTTTopic:
    """
    Registered MQTT topic.
    """
    id: str
    topic_name: str
    qos: QoSLevel = QoSLevel.QOS_1
    description: str = ""
    
    # State
    is_enabled: bool = True
    is_system: bool = False
    retain: bool = False
    
    # Audit
    created_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "topic_name": self.topic_name,
            "description": self.description,
            "qos": self.qos.value,
            "is_enabled": self.is_enabled,
            "is_system": self.is_system,
            "retain": self.retain,
        }
    
    def matches(self, topic: str) -> bool:
        """Check if this topic matches the given topic."""
        if not self.is_enabled:
            return False
        
        return self.topic_matches(self.topic_name, topic)
    
    @staticmethod
    def topic_matches(pattern: str, topic: str) -> bool:
        """
        Match topic against pattern with wildcards.
        
        Supports:
        - + for single level
        - # for multi-level
        """
        pattern_parts = pattern.split('/')
        topic_parts = topic.split('/')
        
        pattern_idx = 0
        topic_idx = 0
        
        while pattern_idx < len(pattern_parts) and topic_idx < len(topic_parts):
            if pattern_parts[pattern_idx] == '#':
                return True
            elif pattern_parts[pattern_idx] == '+':
                pattern_idx += 1
                topic_idx += 1
            elif pattern_parts[pattern_idx] == topic_parts[topic_idx]:
                pattern_idx += 1
                topic_idx += 1
            else:
                return False
        
        return (pattern_idx == len(pattern_parts) and 
                topic_idx == len(topic_parts))


@dataclass
class Subscription:
    """
    Device subscription to a topic.
    """
    id: str
    topic_id: str
    device_id: str
    qos: QoSLevel = QoSLevel.QOS_1
    subscription_type: str = "topic"
    filter_pattern: str = ""
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "topic_id": self.topic_id,
            "device_id": self.device_id,
            "qos": self.qos.value,
            "subscription_type": self.subscription_type,
            "is_active": self.is_active,
        }


@dataclass
class MQTTMessage:
    """
    MQTT message record.
    """
    id: str
    topic_name: str
    payload: Dict[str, Any]
    qos: QoSLevel = QoSLevel.QOS_0
    direction: MessageDirection = MessageDirection.INCOMING
    retained: bool = False
    
    # References
    topic_id: Optional[str] = None
    device_id: Optional[str] = None
    message_id: str = ""
    
    # Routing
    routing_target: str = ""
    error_message: str = ""
    
    # Timestamps
    received_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "topic_name": self.topic_name,
            "payload": self.payload,
            "qos": self.qos.value,
            "direction": self.direction.value,
            "retained": self.retained,
            "device_id": self.device_id,
            "received_at": self.received_at.isoformat(),
        }
    
    @property
    def is_incoming(self) -> bool:
        """Check if message is incoming."""
        return self.direction == MessageDirection.INCOMING
    
    @property
    def is_outgoing(self) -> bool:
        """Check if message is outgoing."""
        return self.direction == MessageDirection.OUTGOING


@dataclass
class TopicSubscriptionCount:
    """Summary of topic subscriptions."""
    topic: MQTTTopic
    subscriber_count: int = 0
    message_count: int = 0
    last_message_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        data = self.topic.to_dict()
        data["subscriber_count"] = self.subscriber_count
        data["message_count"] = self.message_count
        data["last_message_at"] = self.last_message_at.isoformat() if self.last_message_at else None
        return data


@dataclass
class DeviceStatusSummary:
    """Summary of device status."""
    device: Device
    group_name: Optional[str] = None
    asset_name: Optional[str] = None
    activity_status: DeviceActivity = DeviceActivity.OFFLINE
    
    def to_dict(self) -> Dict:
        data = self.device.to_dict()
        data["group_name"] = self.group_name
        data["asset_name"] = self.asset_name
        data["activity_status"] = self.activity_status.value
        return data
