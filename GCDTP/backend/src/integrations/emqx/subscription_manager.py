"""
Subscription Manager

Manages MQTT topic subscriptions for devices.
Handles subscription lifecycle and QoS management.
"""

import uuid
from typing import Dict, List, Optional, Set
from backend.src.integrations.emqx.mqtt_types import (
    Subscription,
    MQTTTopic,
    QoSLevel,
)


class SubscriptionManager:
    """
    Manages device subscriptions to MQTT topics.
    
    Responsibilities:
    - Create/remove subscriptions
    - Track subscription state
    - Handle wildcard subscriptions
    - Manage QoS levels
    """
    
    def __init__(self):
        # Subscription ID -> Subscription
        self._subscriptions: Dict[str, Subscription] = {}
        # Topic ID -> [Subscription IDs]
        self._topic_subscriptions: Dict[str, List[str]] = {}
        # Device ID -> [Subscription IDs]
        self._device_subscriptions: Dict[str, List[str]] = {}
    
    def create_subscription(
        self,
        topic_id: str,
        device_id: str,
        qos: QoSLevel = QoSLevel.QOS_1,
        subscription_type: str = "topic"
    ) -> Subscription:
        """
        Create a subscription.
        
        Args:
            topic_id: Topic ID to subscribe to
            device_id: Device ID subscribing
            qos: Quality of Service level
            subscription_type: Type of subscription
            
        Returns:
            Created Subscription
        """
        subscription = Subscription(
            id=str(uuid.uuid4()),
            topic_id=topic_id,
            device_id=device_id,
            qos=qos,
            subscription_type=subscription_type
        )
        
        # Store subscription
        self._subscriptions[subscription.id] = subscription
        
        # Index by topic
        if topic_id not in self._topic_subscriptions:
            self._topic_subscriptions[topic_id] = []
        self._topic_subscriptions[topic_id].append(subscription.id)
        
        # Index by device
        if device_id not in self._device_subscriptions:
            self._device_subscriptions[device_id] = []
        self._device_subscriptions[device_id].append(subscription.id)
        
        return subscription
    
    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Get subscription by ID."""
        return self._subscriptions.get(subscription_id)
    
    def delete_subscription(self, subscription_id: str) -> bool:
        """
        Delete a subscription.
        
        Args:
            subscription_id: Subscription ID
            
        Returns:
            True if deleted
        """
        subscription = self._subscriptions.get(subscription_id)
        if not subscription:
            return False
        
        # Remove from indices
        if subscription.topic_id in self._topic_subscriptions:
            self._topic_subscriptions[subscription.topic_id].remove(subscription_id)
        
        if subscription.device_id in self._device_subscriptions:
            self._device_subscriptions[subscription.device_id].remove(subscription_id)
        
        del self._subscriptions[subscription_id]
        return True
    
    def get_subscriptions_for_topic(self, topic_id: str) -> List[Subscription]:
        """Get all subscriptions for a topic."""
        subscription_ids = self._topic_subscriptions.get(topic_id, [])
        return [self._subscriptions[sid] for sid in subscription_ids if sid in self._subscriptions]
    
    def get_subscriptions_for_device(self, device_id: str) -> List[Subscription]:
        """Get all subscriptions for a device."""
        subscription_ids = self._device_subscriptions.get(device_id, [])
        return [self._subscriptions[sid] for sid in subscription_ids if sid in self._subscriptions]
    
    def get_active_subscriptions_for_topic(self, topic_id: str) -> List[Subscription]:
        """Get active subscriptions for a topic."""
        subs = self.get_subscriptions_for_topic(topic_id)
        return [s for s in subs if s.is_active]
    
    def activate_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Activate a subscription."""
        subscription = self._subscriptions.get(subscription_id)
        if subscription:
            subscription.is_active = True
        return subscription
    
    def deactivate_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Deactivate a subscription."""
        subscription = self._subscriptions.get(subscription_id)
        if subscription:
            subscription.is_active = False
        return subscription
    
    def update_subscription_qos(
        self,
        subscription_id: str,
        qos: QoSLevel
    ) -> Optional[Subscription]:
        """Update subscription QoS level."""
        subscription = self._subscriptions.get(subscription_id)
        if subscription:
            subscription.qos = qos
        return subscription
    
    def get_subscription_count(self) -> int:
        """Get total subscription count."""
        return len(self._subscriptions)
    
    def get_active_count(self) -> int:
        """Get active subscription count."""
        return len([s for s in self._subscriptions.values() if s.is_active])
    
    def get_device_count(self) -> int:
        """Get number of devices with subscriptions."""
        return len(self._device_subscriptions)


class WildcardSubscriptionManager:
    """
    Manages wildcard subscriptions.
    
    Wildcard subscriptions allow devices to receive messages
    matching a pattern rather than a specific topic.
    """
    
    def __init__(self):
        # Pattern -> Subscription
        self._wildcard_subscriptions: Dict[str, Subscription] = {}
    
    def create_wildcard_subscription(
        self,
        device_id: str,
        pattern: str,
        qos: QoSLevel = QoSLevel.QOS_1
    ) -> Subscription:
        """
        Create a wildcard subscription.
        
        Args:
            device_id: Device ID
            pattern: Wildcard pattern (+ or #)
            qos: Quality of Service level
            
        Returns:
            Created Subscription
        """
        subscription = Subscription(
            id=str(uuid.uuid4()),
            topic_id="",  # No specific topic
            device_id=device_id,
            qos=qos,
            subscription_type="wildcard",
            filter_pattern=pattern
        )
        
        self._wildcard_subscriptions[pattern] = subscription
        return subscription
    
    def get_wildcard_subscription(self, pattern: str) -> Optional[Subscription]:
        """Get wildcard subscription by pattern."""
        return self._wildcard_subscriptions.get(pattern)
    
    def delete_wildcard_subscription(self, pattern: str) -> bool:
        """Delete a wildcard subscription."""
        if pattern in self._wildcard_subscriptions:
            del self._wildcard_subscriptions[pattern]
            return True
        return False
    
    def find_matching_wildcards(
        self,
        topic_name: str
    ) -> List[Subscription]:
        """
        Find all wildcard subscriptions matching a topic.
        
        Args:
            topic_name: Topic name to match
            
        Returns:
            List of matching subscriptions
        """
        matches: List[Subscription] = []
        
        for pattern, subscription in self._wildcard_subscriptions.items():
            if MQTTTopic.topic_matches(pattern, topic_name):
                matches.append(subscription)
        
        return matches
    
    def get_all_wildcards(self) -> List[Subscription]:
        """Get all wildcard subscriptions."""
        return list(self._wildcard_subscriptions.values())
