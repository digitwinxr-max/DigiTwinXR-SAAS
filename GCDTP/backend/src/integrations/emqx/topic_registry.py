"""
Topic Registry

Registry for managing MQTT topics.
Supports topic registration, wildcard patterns, and lookups.
"""

import uuid
from typing import Dict, List, Optional, Set
from backend.src.integrations.emqx.mqtt_types import MQTTTopic, QoSLevel


class TopicRegistry:
    """
    Registry for MQTT topics.
    
    Responsibilities:
    - Register topics
    - Update topics
    - Enable/disable topics
    - Lookup topics
    - Wildcard matching
    """
    
    def __init__(self):
        self._topics: Dict[str, MQTTTopic] = {}  # id -> MQTTTopic
        self._topic_names: Dict[str, str] = {}  # topic_name -> id
        self._device_topics: Dict[str, List[str]] = {}  # device_id -> [topic_ids]
    
    def register_topic(
        self,
        topic_name: str,
        qos: QoSLevel = QoSLevel.QOS_1,
        description: str = "",
        is_system: bool = False,
        created_by: Optional[str] = None
    ) -> MQTTTopic:
        """
        Register a new topic.
        
        Args:
            topic_name: Topic name
            qos: Quality of Service level
            description: Topic description
            is_system: Is a system topic
            created_by: User who created
            
        Returns:
            Created MQTTTopic
        """
        topic = MQTTTopic(
            id=str(uuid.uuid4()),
            topic_name=topic_name,
            qos=qos,
            description=description,
            is_system=is_system,
            created_by=created_by
        )
        
        self._topics[topic.id] = topic
        self._topic_names[topic_name] = topic.id
        
        return topic
    
    def get_topic(self, topic_id: str) -> Optional[MQTTTopic]:
        """Get topic by ID."""
        return self._topics.get(topic_id)
    
    def get_topic_by_name(self, topic_name: str) -> Optional[MQTTTopic]:
        """Get topic by name."""
        topic_id = self._topic_names.get(topic_name)
        if topic_id:
            return self._topics.get(topic_id)
        return None
    
    def update_topic(
        self,
        topic: MQTTTopic,
        **kwargs
    ) -> MQTTTopic:
        """
        Update a topic.
        
        Args:
            topic: Topic to update
            **kwargs: Fields to update
            
        Returns:
            Updated MQTTTopic
        """
        old_name = topic.topic_name
        
        for key, value in kwargs.items():
            if hasattr(topic, key):
                setattr(topic, key, value)
        
        # Update name index if name changed
        if topic.topic_name != old_name:
            if old_name in self._topic_names:
                del self._topic_names[old_name]
            self._topic_names[topic.topic_name] = topic.id
        
        return topic
    
    def enable_topic(self, topic_id: str) -> Optional[MQTTTopic]:
        """Enable a topic."""
        topic = self._topics.get(topic_id)
        if topic:
            topic.is_enabled = True
        return topic
    
    def disable_topic(self, topic_id: str) -> Optional[MQTTTopic]:
        """Disable a topic."""
        topic = self._topics.get(topic_id)
        if topic:
            topic.is_enabled = False
        return topic
    
    def delete_topic(self, topic_id: str) -> bool:
        """
        Delete a topic.
        
        Args:
            topic_id: Topic ID
            
        Returns:
            True if deleted
        """
        topic = self._topics.get(topic_id)
        if not topic:
            return False
        
        if topic.is_system:
            return False  # Cannot delete system topics
        
        # Remove from indices
        del self._topics[topic_id]
        if topic.topic_name in self._topic_names:
            del self._topic_names[topic.topic_name]
        
        return True
    
    def find_matching_topics(self, topic_name: str) -> List[MQTTTopic]:
        """
        Find all registered topics that match the given topic.
        
        Args:
            topic_name: Topic name to match
            
        Returns:
            List of matching topics
        """
        matches: List[MQTTTopic] = []
        
        for topic in self._topics.values():
            if topic.matches(topic_name):
                matches.append(topic)
        
        return matches
    
    def find_topics_by_pattern(self, pattern: str) -> List[MQTTTopic]:
        """
        Find topics matching a wildcard pattern.
        
        Args:
            pattern: Wildcard pattern (+ or #)
            
        Returns:
            List of matching topics
        """
        matches: List[MQTTTopic] = []
        
        for topic in self._topics.values():
            if MQTTTopic.topic_matches(pattern, topic.topic_name):
                matches.append(topic)
        
        return matches
    
    def get_all_topics(
        self,
        enabled_only: bool = False,
        system_only: bool = False
    ) -> List[MQTTTopic]:
        """
        Get all topics.
        
        Args:
            enabled_only: Only enabled topics
            system_only: Only system topics
            
        Returns:
            List of topics
        """
        topics = list(self._topics.values())
        
        if enabled_only:
            topics = [t for t in topics if t.is_enabled]
        
        if system_only:
            topics = [t for t in topics if t.is_system]
        
        return topics
    
    def get_topics_by_device(self, device_id: str) -> List[MQTTTopic]:
        """
        Get topics registered for a device.
        
        Args:
            device_id: Device ID
            
        Returns:
            List of topics
        """
        topic_ids = self._device_topics.get(device_id, [])
        return [self._topics[tid] for tid in topic_ids if tid in self._topics]
    
    def register_device_topic(
        self,
        device_id: str,
        topic_name: str,
        qos: QoSLevel = QoSLevel.QOS_1
    ) -> MQTTTopic:
        """
        Register a topic for a device.
        
        Args:
            device_id: Device ID
            topic_name: Topic name (can include {device_id})
            qos: Quality of Service level
            
        Returns:
            Created MQTTTopic
        """
        # Replace {device_id} placeholder
        actual_topic = topic_name.format(device_id=device_id)
        
        # Check if already exists
        existing = self.get_topic_by_name(actual_topic)
        if existing:
            return existing
        
        # Register topic
        topic = self.register_topic(
            topic_name=actual_topic,
            qos=qos,
            is_system=True  # Device topics are system topics
        )
        
        # Track device association
        if device_id not in self._device_topics:
            self._device_topics[device_id] = []
        self._device_topics[device_id].append(topic.id)
        
        return topic
    
    def get_topic_count(self) -> int:
        """Get total topic count."""
        return len(self._topics)
    
    def get_enabled_count(self) -> int:
        """Get enabled topic count."""
        return len([t for t in self._topics.values() if t.is_enabled])
    
    def validate_topic_name(self, topic_name: str) -> List[str]:
        """
        Validate a topic name.
        
        Args:
            topic_name: Topic name to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not topic_name:
            issues.append("Topic name is required")
            return issues
        
        # Topic must start with /
        if not topic_name.startswith('/'):
            issues.append("Topic must start with /")
        
        # No null bytes
        if '\x00' in topic_name:
            issues.append("Topic cannot contain null bytes")
        
        # Check for invalid characters (excluding wildcards)
        invalid_chars = ['+', '#']
        for char in invalid_chars:
            # But wildcards are allowed in specific positions
            if char in topic_name:
                # Check position
                if topic_name.count(char) > 1:
                    issues.append(f"Multiple '{char}' wildcards not allowed")
                # + cannot be at end
                if char == '+' and topic_name.endswith('+'):
                    issues.append("'+' wildcard cannot be at the end")
                # # cannot be in middle
                if char == '#' and '#' in topic_name[:-1]:
                    issues.append("'#' wildcard can only be at the end")
        
        return issues
