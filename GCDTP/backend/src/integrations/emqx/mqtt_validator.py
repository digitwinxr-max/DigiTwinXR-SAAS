"""
MQTT Validator

Validates MQTT topics, subscriptions, devices, and configurations.
"""

from typing import Dict, List, Set, Optional
from backend.src.integrations.emqx.mqtt_types import (
    MQTTTopic,
    Subscription,
    Device,
    QoSLevel,
)


class MQTTValidator:
    """
    Validates MQTT-related entities.
    
    Checks:
    - Duplicate topics
    - Invalid QoS
    - Wildcard conflicts
    - Subscription loops
    - Device conflicts
    """
    
    def __init__(self):
        self.issues: List[str] = []
    
    def validate_topic(self, topic: MQTTTopic) -> List[str]:
        """
        Validate an MQTT topic.
        
        Args:
            topic: Topic to validate
            
        Returns:
            List of validation issues
        """
        self.issues = []
        
        # Required fields
        if not topic.id:
            self.issues.append("Topic ID is required")
        
        if not topic.topic_name or not topic.topic_name.strip():
            self.issues.append("Topic name is required")
        
        # Topic name format
        if topic.topic_name:
            topic_issues = self.validate_topic_name(topic.topic_name)
            self.issues.extend(topic_issues)
        
        return self.issues.copy()
    
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
        
        # Must start with /
        if not topic_name.startswith('/'):
            issues.append("Topic name must start with /")
        
        # No null bytes
        if '\x00' in topic_name:
            issues.append("Topic name cannot contain null bytes")
        
        # Check wildcards
        if '#' in topic_name and not topic_name.endswith('#'):
            issues.append("Multi-level wildcard '#' can only appear at the end")
        
        if topic_name.count('#') > 1:
            issues.append("Only one multi-level wildcard allowed")
        
        if topic_name.endswith('/#') and len(topic_name) > 2:
            # This is valid
            pass
        elif '#' in topic_name:
            issues.append("'#' wildcard must be at the end after '/'")
        
        # + wildcard checks
        plus_count = topic_name.count('+')
        if plus_count > 0:
            parts = topic_name.split('/')
            for i, part in enumerate(parts):
                if part == '+':
                    # + cannot be at the end
                    if i == len(parts) - 1:
                        issues.append("Single-level wildcard '+' cannot be at the end")
        
        return issues
    
    def validate_subscription(self, subscription: Subscription) -> List[str]:
        """
        Validate a subscription.
        
        Args:
            subscription: Subscription to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Required fields
        if not subscription.id:
            issues.append("Subscription ID is required")
        
        if not subscription.topic_id:
            issues.append("Topic ID is required")
        
        if not subscription.device_id:
            issues.append("Device ID is required")
        
        return issues
    
    def validate_device(self, device: Device) -> List[str]:
        """
        Validate a device.
        
        Args:
            device: Device to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Required fields
        if not device.id:
            issues.append("Device ID is required")
        
        if not device.device_id or not device.device_id.strip():
            issues.append("Device ID is required")
        
        if not device.name or not device.name.strip():
            issues.append("Device name is required")
        
        return issues
    
    def validate_qos(self, qos: QoSLevel) -> List[str]:
        """
        Validate a QoS level.
        
        Args:
            qos: QoS level to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        valid_qos = [QoSLevel.QOS_0, QoSLevel.QOS_1, QoSLevel.QOS_2]
        if qos not in valid_qos:
            issues.append(f"Invalid QoS level: {qos}")
        
        return issues
    
    def check_duplicate_topic(
        self,
        topic_name: str,
        existing_topics: Set[str]
    ) -> bool:
        """
        Check for duplicate topic.
        
        Args:
            topic_name: Topic name
            existing_topics: Set of existing topic names
            
        Returns:
            True if duplicate
        """
        return topic_name in existing_topics
    
    def check_wildcard_conflict(
        self,
        topic_name: str,
        existing_topics: List[str]
    ) -> List[str]:
        """
        Check for wildcard conflicts.
        
        Args:
            topic_name: Topic name to check
            existing_topics: List of existing topics
            
        Returns:
            List of conflicts
        """
        conflicts = []
        
        for existing in existing_topics:
            # Check if topics would match the same messages
            if existing != topic_name:
                # Multi-level wildcard conflict
                if '#' in existing:
                    pattern = existing.replace('#', '')
                    if topic_name.startswith(pattern.rstrip('/')):
                        conflicts.append(f"Conflicts with: {existing}")
                
                # Single-level wildcard check
                if '+' in existing:
                    parts1 = existing.split('/')
                    parts2 = topic_name.split('/')
                    if len(parts1) == len(parts2):
                        match = True
                        for p1, p2 in zip(parts1, parts2):
                            if p1 not in ('+', p2):
                                match = False
                                break
                        if match:
                            conflicts.append(f"Conflicts with: {existing}")
        
        return conflicts
    
    def check_subscription_loop(
        self,
        source_topic: str,
        target_topic: str,
        existing_routes: List[Dict]
    ) -> bool:
        """
        Check for subscription loops.
        
        Args:
            source_topic: Source topic
            target_topic: Target topic
            existing_routes: Existing routing rules
            
        Returns:
            True if loop detected
        """
        # Build routing graph
        graph: Dict[str, Set[str]] = {}
        
        for route in existing_routes:
            source = route.get("source", "")
            target = route.get("target", "")
            if source not in graph:
                graph[source] = set()
            graph[source].add(target)
        
        # Add proposed route
        if source_topic not in graph:
            graph[source_topic] = set()
        graph[source_topic].add(target_topic)
        
        # Detect cycle using DFS
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        
        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        return has_cycle(source_topic)
    
    def check_device_conflict(
        self,
        device_id: str,
        client_id: str,
        existing_devices: List[Device]
    ) -> List[str]:
        """
        Check for device conflicts.
        
        Args:
            device_id: Device ID to check
            client_id: Client ID to check
            existing_devices: List of existing devices
            
        Returns:
            List of conflicts
        """
        conflicts = []
        
        for device in existing_devices:
            if device.device_id == device_id:
                conflicts.append(f"Device ID '{device_id}' already exists")
            
            if device.client_id == client_id:
                conflicts.append(f"Client ID '{client_id}' already connected")
        
        return conflicts
    
    def validate_device_group(self, name: str) -> List[str]:
        """
        Validate device group name.
        
        Args:
            name: Group name
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not name or not name.strip():
            issues.append("Group name is required")
        
        if name and len(name) > 100:
            issues.append("Group name must be 100 characters or less")
        
        return issues
    
    def validate_payload(self, payload: Dict) -> List[str]:
        """
        Validate MQTT payload.
        
        Args:
            payload: Payload to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not isinstance(payload, dict):
            issues.append("Payload must be a JSON object")
        
        return issues
    
    def get_validation_summary(self) -> Dict:
        """
        Get validation summary.
        
        Returns:
            Summary dictionary
        """
        return {
            "issues": self.issues,
            "issue_count": len(self.issues),
            "has_critical": any("required" in i.lower() for i in self.issues),
        }
