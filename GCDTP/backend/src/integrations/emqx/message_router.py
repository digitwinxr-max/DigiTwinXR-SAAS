"""
Message Router

Bridges MQTT messages into FastAPI services.
Routes messages to:
- EventBus
- Timeline Engine
- Measurement Engine
- Health Engine
- Simulation Engine
- Node-RED workflows
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from backend.src.integrations.emqx.mqtt_types import MQTTMessage, QoSLevel
from backend.src.core.events import get_event_bus, EventType


class MessageRouter:
    """
    Routes MQTT messages to appropriate FastAPI services.
    
    Responsibilities:
    - Parse incoming messages
    - Route to EventBus
    - Route to Timeline Engine
    - Route to Measurement Engine
    - Route to Health Engine
    - Route to Simulation Engine
    - Route to Node-RED
    
    Note: All business logic remains in FastAPI.
    """
    
    def __init__(self):
        self.event_bus = get_event_bus()
        self._handlers: Dict[str, List[Callable]] = {}
        self._route_rules: Dict[str, str] = {}  # topic_pattern -> service
    
    # =========================================================================
    # Message Handling
    # =========================================================================
    
    def route_message(
        self,
        message: MQTTMessage
    ) -> Dict[str, Any]:
        """
        Route a message to appropriate services.
        
        Args:
            message: MQTT message to route
            
        Returns:
            Routing result
        """
        results = {}
        
        # Route based on topic
        if message.topic_name.startswith("gc/measurements/"):
            results["measurements"] = self._route_to_measurements(message)
        
        if message.topic_name.startswith("gc/assets/"):
            results["assets"] = self._route_to_assets(message)
        
        if message.topic_name.startswith("gc/health/"):
            results["health"] = self._route_to_health(message)
        
        if message.topic_name.startswith("gc/simulation/"):
            results["simulation"] = self._route_to_simulation(message)
        
        if message.topic_name.startswith("gc/timeline/"):
            results["timeline"] = self._route_to_timeline(message)
        
        # Publish to EventBus
        self._publish_to_eventbus(message)
        
        # Call custom handlers
        self._call_handlers(message)
        
        return results
    
    def _route_to_measurements(self, message: MQTTMessage) -> Dict[str, Any]:
        """Route message to Measurement Engine."""
        # In production, would call MeasurementEngine
        return {
            "routed": True,
            "service": "measurements"
        }
    
    def _route_to_assets(self, message: MQTTMessage) -> Dict[str, Any]:
        """Route message to Asset events."""
        # Extract asset ID from topic
        parts = message.topic_name.split("/")
        if len(parts) >= 3:
            asset_id = parts[2]
            
            # Publish asset event
            self.event_bus.publish(
                EventType.ASSET_UPDATED,
                source="mqtt_router",
                data={
                    "asset_id": asset_id,
                    "payload": message.payload,
                    "topic": message.topic_name
                }
            )
        
        return {
            "routed": True,
            "service": "assets"
        }
    
    def _route_to_health(self, message: MQTTMessage) -> Dict[str, Any]:
        """Route message to Health Engine."""
        return {
            "routed": True,
            "service": "health"
        }
    
    def _route_to_simulation(self, message: MQTTMessage) -> Dict[str, Any]:
        """Route message to Simulation Engine."""
        return {
            "routed": True,
            "service": "simulation"
        }
    
    def _route_to_timeline(self, message: MQTTMessage) -> Dict[str, Any]:
        """Route message to Timeline Engine."""
        return {
            "routed": True,
            "service": "timeline"
        }
    
    def _publish_to_eventbus(self, message: MQTTMessage) -> None:
        """Publish message to EventBus."""
        self.event_bus.publish(
            EventType.MQTT_MESSAGE_RECEIVED,
            source="mqtt_router",
            data={
                "topic": message.topic_name,
                "payload": message.payload,
                "qos": message.qos.value,
                "device_id": message.device_id
            }
        )
    
    def _call_handlers(self, message: MQTTMessage) -> None:
        """Call custom handlers for the topic."""
        handlers = self._handlers.get(message.topic_name, [])
        for handler in handlers:
            try:
                handler(message)
            except Exception:
                pass  # Log error in production
    
    # =========================================================================
    # Topic-Based Routing
    # =========================================================================
    
    def register_route(
        self,
        topic_pattern: str,
        service: str
    ) -> None:
        """
        Register a routing rule.
        
        Args:
            topic_pattern: Topic pattern (supports wildcards)
            service: Target service name
        """
        self._route_rules[topic_pattern] = service
    
    def get_route(self, topic_name: str) -> Optional[str]:
        """Get the route for a topic."""
        for pattern, service in self._route_rules.items():
            if MQTTMessage.topic_matches_topic(pattern, topic_name):
                return service
        return None
    
    # =========================================================================
    # Custom Handlers
    # =========================================================================
    
    def register_handler(
        self,
        topic: str,
        handler: Callable[[MQTTMessage], Any]
    ) -> None:
        """
        Register a handler for a topic.
        
        Args:
            topic: Topic name
            handler: Handler function
        """
        if topic not in self._handlers:
            self._handlers[topic] = []
        self._handlers[topic].append(handler)
    
    def unregister_handler(
        self,
        topic: str,
        handler: Callable[[MQTTMessage], Any]
    ) -> None:
        """Unregister a handler."""
        if topic in self._handlers:
            if handler in self._handlers[topic]:
                self._handlers[topic].remove(handler)


class MeasurementRouter:
    """
    Specialized router for sensor measurements.
    """
    
    def __init__(self):
        self.event_bus = get_event_bus()
    
    def route_measurement(
        self,
        device_id: str,
        measurements: Dict[str, Any],
        timestamp: datetime
    ) -> Dict[str, Any]:
        """
        Route sensor measurements.
        
        Args:
            device_id: Device ID
            measurements: Measurement data
            timestamp: Measurement timestamp
            
        Returns:
            Routing result
        """
        # Validate measurements
        validated = self._validate_measurements(measurements)
        
        # Publish to EventBus
        self.event_bus.publish(
            EventType.SENSOR_DATA_RECEIVED,
            source="measurement_router",
            data={
                "device_id": device_id,
                "measurements": validated,
                "timestamp": timestamp.isoformat()
            }
        )
        
        return {
            "device_id": device_id,
            "measurements_count": len(validated),
            "timestamp": timestamp.isoformat()
        }
    
    def _validate_measurements(
        self,
        measurements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate and normalize measurements."""
        validated = {}
        
        for key, value in measurements.items():
            # Skip non-numeric values
            if isinstance(value, (int, float)):
                # Validate range
                if -1e9 <= value <= 1e9:
                    validated[key] = value
        
        return validated
