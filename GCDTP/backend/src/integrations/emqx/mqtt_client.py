"""
MQTT Client

Client for communicating with EMQX MQTT broker.
FastAPI remains authoritative for business logic.
EMQX provides telemetry ingestion and device connectivity only.
"""

import json
import uuid
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from backend.src.integrations.emqx.mqtt_types import QoSLevel


class MQTTClientError(Exception):
    """MQTT client error."""
    pass


class MQTTClient:
    """
    Client for EMQX MQTT integration.
    
    Responsibilities:
    - Device connection management
    - Topic publishing
    - Message handling
    - QoS management
    
    Note: All business logic remains in FastAPI.
    EMQX provides connectivity and telemetry only.
    """
    
    def __init__(
        self,
        broker_host: str = "localhost",
        broker_port: int = 1883,
        username: str = "",
        password: str = "",
        client_id: str = ""
    ):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.username = username
        self.password = password
        self.client_id = client_id or f"fastapi-{uuid.uuid4().hex[:8]}"
        
        self._connected = False
        self._message_handlers: Dict[str, List[Callable]] = {}
        self._connection_handlers: List[Callable] = []
        self._disconnection_handlers: List[Callable] = []
    
    def connect(self) -> bool:
        """
        Connect to EMQX broker.
        
        Returns:
            True if connected
        """
        try:
            # In production, would use paho-mqtt:
            # self._client = mqtt.Client(client_id=self.client_id)
            # self._client.username_pw_set(self.username, self.password)
            # self._client.on_connect = self._on_connect
            # self._client.on_disconnect = self._on_disconnect
            # self._client.on_message = self._on_message
            # self._client.connect(self.broker_host, self.broker_port)
            
            self._connected = True
            return True
        except Exception as e:
            raise MQTTClientError(f"Failed to connect: {e}")
    
    def disconnect(self) -> bool:
        """
        Disconnect from EMQX broker.
        
        Returns:
            True if disconnected
        """
        try:
            # In production: self._client.disconnect()
            self._connected = False
            return True
        except Exception as e:
            raise MQTTClientError(f"Failed to disconnect: {e}")
    
    @property
    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected
    
    # =========================================================================
    # Publishing
    # =========================================================================
    
    def publish(
        self,
        topic: str,
        payload: Dict[str, Any],
        qos: QoSLevel = QoSLevel.QOS_1,
        retain: bool = False
    ) -> bool:
        """
        Publish a message to a topic.
        
        Args:
            topic: Topic name
            payload: Message payload
            qos: Quality of Service level
            retain: Retain message
            
        Returns:
            True if published
        """
        if not self._connected:
            raise MQTTClientError("Not connected to broker")
        
        try:
            # In production:
            # result = self._client.publish(
            #     topic,
            #     json.dumps(payload),
            #     qos=qos.value
            # )
            # return result.rc == 0
            
            return True
        except Exception as e:
            raise MQTTClientError(f"Failed to publish: {e}")
    
    def publish_measurement(
        self,
        device_id: str,
        measurements: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ) -> bool:
        """
        Publish device measurements.
        
        Args:
            device_id: Device ID
            measurements: Measurement data
            timestamp: Optional timestamp
            
        Returns:
            True if published
        """
        payload = {
            "device_id": device_id,
            "measurements": measurements,
            "timestamp": (timestamp or datetime.utcnow()).isoformat()
        }
        
        topic = f"gc/measurements/{device_id}"
        return self.publish(topic, payload, QoSLevel.QOS_1)
    
    def publish_asset_event(
        self,
        asset_id: str,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> bool:
        """
        Publish asset event.
        
        Args:
            asset_id: Asset ID
            event_type: Event type
            event_data: Event data
            
        Returns:
            True if published
        """
        payload = {
            "asset_id": asset_id,
            "event_type": event_type,
            "data": event_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        topic = f"gc/assets/{asset_id}/events"
        return self.publish(topic, payload, QoSLevel.QOS_1)
    
    def publish_command(
        self,
        device_id: str,
        command: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish command to device.
        
        Args:
            device_id: Device ID
            command: Command name
            parameters: Command parameters
            
        Returns:
            True if published
        """
        payload = {
            "command": command,
            "parameters": parameters or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        topic = f"gc/devices/{device_id}/commands"
        return self.publish(topic, payload, QoSLevel.QOS_1)
    
    # =========================================================================
    # Subscribing
    # =========================================================================
    
    def subscribe(
        self,
        topic: str,
        handler: Callable[[str, Dict], None],
        qos: QoSLevel = QoSLevel.QOS_1
    ) -> bool:
        """
        Subscribe to a topic.
        
        Args:
            topic: Topic name (supports wildcards)
            handler: Message handler function
            qos: Quality of Service level
            
        Returns:
            True if subscribed
        """
        if not self._connected:
            raise MQTTClientError("Not connected to broker")
        
        try:
            # In production:
            # self._client.message_callback_add(topic, handler)
            # self._client.subscribe(topic, qos=qos.value)
            
            if topic not in self._message_handlers:
                self._message_handlers[topic] = []
            self._message_handlers[topic].append(handler)
            
            return True
        except Exception as e:
            raise MQTTClientError(f"Failed to subscribe: {e}")
    
    def unsubscribe(self, topic: str) -> bool:
        """
        Unsubscribe from a topic.
        
        Args:
            topic: Topic name
            
        Returns:
            True if unsubscribed
        """
        if not self._connected:
            raise MQTTClientError("Not connected to broker")
        
        try:
            # In production: self._client.unsubscribe(topic)
            if topic in self._message_handlers:
                del self._message_handlers[topic]
            return True
        except Exception as e:
            raise MQTTClientError(f"Failed to unsubscribe: {e}")
    
    # =========================================================================
    # Event Handlers
    # =========================================================================
    
    def on_connect(self, handler: Callable) -> None:
        """Register connection handler."""
        self._connection_handlers.append(handler)
    
    def on_disconnect(self, handler: Callable) -> None:
        """Register disconnection handler."""
        self._disconnection_handlers.append(handler)
    
    def _handle_connect(self) -> None:
        """Handle connection event."""
        self._connected = True
        for handler in self._connection_handlers:
            handler()
    
    def _handle_disconnect(self) -> None:
        """Handle disconnection event."""
        self._connected = False
        for handler in self._disconnection_handlers:
            handler()
    
    def _handle_message(self, topic: str, payload: Dict) -> None:
        """Handle incoming message."""
        handlers = self._message_handlers.get(topic, [])
        for handler in handlers:
            try:
                handler(topic, payload)
            except Exception:
                pass  # Log error in production
    
    # =========================================================================
    # Topic Helpers
    # =========================================================================
    
    @staticmethod
    def build_device_topic(device_id: str, suffix: str) -> str:
        """
        Build device topic path.
        
        Args:
            device_id: Device ID
            suffix: Topic suffix
            
        Returns:
            Full topic path
        """
        return f"gc/devices/{device_id}/{suffix}"
    
    @staticmethod
    def build_asset_topic(asset_id: str, suffix: str) -> str:
        """
        Build asset topic path.
        
        Args:
            asset_id: Asset ID
            suffix: Topic suffix
            
        Returns:
            Full topic path
        """
        return f"gc/assets/{asset_id}/{suffix}"
    
    # =========================================================================
    # Health Check
    # =========================================================================
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check client health.
        
        Returns:
            Health status
        """
        return {
            "connected": self._connected,
            "client_id": self.client_id,
            "broker": f"{self.broker_host}:{self.broker_port}",
            "subscribed_topics": len(self._message_handlers),
        }


class MQTTTopicBuilder:
    """
    Helper class for building MQTT topic names.
    """
    
    # Topic hierarchy:
    # gc/{entity}/{id}/{category}
    
    PREFIX = "gc"
    
    @classmethod
    def measurements(cls, device_id: str) -> str:
        """Build measurements topic."""
        return f"{cls.PREFIX}/measurements/{device_id}"
    
    @classmethod
    def commands(cls, device_id: str) -> str:
        """Build commands topic."""
        return f"{cls.PREFIX}/devices/{device_id}/commands"
    
    @classmethod
    def events(cls, entity: str, entity_id: str) -> str:
        """Build events topic."""
        return f"{cls.PREFIX}/{entity}/{entity_id}/events"
    
    @classmethod
    def status(cls, entity: str, entity_id: str) -> str:
        """Build status topic."""
        return f"{cls.PREFIX}/{entity}/{entity_id}/status"
    
    @classmethod
    def telemetry(cls, device_id: str) -> str:
        """Build telemetry topic."""
        return f"{cls.PREFIX}/telemetry/{device_id}"
    
    @classmethod
    def alerts(cls, asset_id: str) -> str:
        """Build alerts topic."""
        return f"{cls.PREFIX}/assets/{asset_id}/alerts"
    
    @classmethod
    def health_check(cls) -> str:
        """Build health check topic."""
        return f"{cls.PREFIX}/system/health"
    
    @classmethod
    def wildcard_all_devices(cls) -> str:
        """Build wildcard for all devices."""
        return f"{cls.PREFIX}/devices/+/commands"
    
    @classmethod
    def wildcard_all_assets(cls) -> str:
        """Build wildcard for all assets."""
        return f"{cls.PREFIX}/assets/+/events"
