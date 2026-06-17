"""
Event Bus

Event-based communication system for simulation engines.
Enables loose coupling between engines and supports replay/debugging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Callable, Any, Optional
from datetime import datetime
from enum import Enum
from collections import defaultdict


class EventType(str, Enum):
    """Simulation event types."""
    # Node events
    NODE_FAILED = "node_failed"
    NODE_RECOVERED = "node_recovered"
    NODE_DEGRADED = "node_degraded"
    
    # Edge events
    EDGE_OVERLOADED = "edge_overloaded"
    EDGE_DEGRADED = "edge_degraded"
    EDGE_FAILED = "edge_failed"
    EDGE_RECOVERED = "edge_recovered"
    
    # Flow events
    LOAD_INCREASED = "load_increased"
    LOAD_DECREASED = "load_decreased"
    BOTTLENECK_DETECTED = "bottleneck_detected"
    
    # Route events
    ROUTE_CHANGED = "route_changed"
    ROUTE_FOUND = "route_found"
    ROUTE_FAILED = "route_failed"
    
    # System events
    SIMULATION_STARTED = "simulation_started"
    SIMULATION_PAUSED = "simulation_paused"
    SIMULATION_RESUMED = "simulation_resumed"
    SIMULATION_COMPLETED = "simulation_completed"
    SIMULATION_FAILED = "simulation_failed"
    
    # Analysis events
    CRITICAL_NODE_IDENTIFIED = "critical_node_identified"
    CRITICAL_EDGE_IDENTIFIED = "critical_edge_identified"
    RESILIENCE_UPDATED = "resilience_updated"
    
    # Work order events
    WORK_ORDER_CREATED = "work_order_created"
    WORK_ORDER_ASSIGNED = "work_order_assigned"
    WORK_ORDER_STARTED = "work_order_started"
    WORK_ORDER_COMPLETED = "work_order_completed"
    WORK_ORDER_CANCELLED = "work_order_cancelled"
    WORK_ORDER_STATUS_CHANGED = "work_order_status_changed"
    WORK_ORDER_PRIORITY_CHANGED = "work_order_priority_changed"
    
    # Inspection events
    INSPECTION_CREATED = "inspection_created"
    INSPECTION_COMPLETED = "inspection_completed"
    
    # Maintenance events
    MAINTENANCE_CREATED = "maintenance_created"
    MAINTENANCE_STARTED = "maintenance_started"
    MAINTENANCE_COMPLETED = "maintenance_completed"
    MAINTENANCE_CANCELLED = "maintenance_cancelled"
    
    # Document events
    DOCUMENT_CREATED = "document_created"
    DOCUMENT_UPDATED = "document_updated"
    DOCUMENT_VERSION_CREATED = "document_version_created"
    DOCUMENT_ARCHIVED = "document_archived"
    DOCUMENT_RESTORED = "document_restored"
    DOCUMENT_DELETED = "document_deleted"
    
    # User events
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DEACTIVATED = "user_deactivated"
    
    # Role events
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REMOVED = "role_removed"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_REVOKED = "permission_revoked"
    
    # Organization events
    ORGANIZATION_CREATED = "organization_created"
    ORGANIZATION_UPDATED = "organization_updated"
    ORGANIZATION_MEMBER_ADDED = "organization_member_added"
    ORGANIZATION_MEMBER_REMOVED = "organization_member_removed"
    ORGANIZATION_MEMBER_ROLE_CHANGED = "organization_member_role_changed"
    
    # Workflow events
    WORKFLOW_CREATED = "workflow_created"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    WORKFLOW_CANCELLED = "workflow_cancelled"
    WORKFLOW_RETRIED = "workflow_retried"
    
    # Device/MQTT events
    DEVICE_REGISTERED = "device_registered"
    DEVICE_CONNECTED = "device_connected"
    DEVICE_DISCONNECTED = "device_disconnected"
    MQTT_MESSAGE_RECEIVED = "mqtt_message_received"
    MQTT_TOPIC_CREATED = "mqtt_topic_created"
    MQTT_TOPIC_UPDATED = "mqtt_topic_updated"
    
    # GeoServer events
    WORKSPACE_CREATED = "workspace_created"
    LAYER_PUBLISHED = "layer_published"
    LAYER_UPDATED = "layer_updated"
    STYLE_ASSIGNED = "style_assigned"
    SERVICE_REGISTERED = "service_registered"
    
    # Graph events
    GRAPH_SYNC_STARTED = "graph_sync_started"
    GRAPH_SYNC_COMPLETED = "graph_sync_completed"
    GRAPH_QUERY_EXECUTED = "graph_query_executed"
    GRAPH_SNAPSHOT_CREATED = "graph_snapshot_created"
    
    # Ontology events
    ONTOLOGY_CLASS_CREATED = "ontology_class_created"
    ONTOLOGY_UPDATED = "ontology_updated"
    SEMANTIC_TAG_ASSIGNED = "semantic_tag_assigned"
    CLASSIFICATION_UPDATED = "classification_updated"
    ONTOLOGY_SYNC_COMPLETED = "ontology_sync_completed"


@dataclass
class SimulationEvent:
    """A simulation event."""
    event_type: EventType
    timestamp: datetime
    source: str
    data: Dict[str, Any]
    iteration: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "data": self.data,
            "iteration": self.iteration,
        }


@dataclass 
class EventHandler:
    """An event handler callback."""
    callback: Callable[[SimulationEvent], None]
    event_types: List[EventType]
    once: bool = False
    filter_fn: Optional[Callable[[Dict], bool]] = None


class EventBus:
    """
    Event bus for simulation communication.
    
    Features:
    - Publish/subscribe pattern
    - Event filtering
    - One-time handlers
    - Event replay
    - Debug tracing
    """
    
    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = defaultdict(list)
        self._event_history: List[SimulationEvent] = []
        self._enabled: bool = True
        self._max_history: int = 10000
    
    def subscribe(
        self,
        event_types: List[EventType],
        callback: Callable[[SimulationEvent], None],
        once: bool = False,
        filter_fn: Optional[Callable[[Dict], bool]] = None
    ) -> EventHandler:
        """
        Subscribe to event types.
        
        Args:
            event_types: List of event types to subscribe to
            callback: Function to call when event occurs
            once: If True, handler is removed after first call
            filter_fn: Optional function to filter events
            
        Returns:
            EventHandler object
        """
        handler = EventHandler(
            callback=callback,
            event_types=event_types,
            once=once,
            filter_fn=filter_fn
        )
        
        for event_type in event_types:
            self._handlers[event_type].append(handler)
        
        return handler
    
    def unsubscribe(self, handler: EventHandler) -> None:
        """Unsubscribe a handler."""
        for event_type in handler.event_types:
            if handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)
    
    def publish(
        self,
        event_type: EventType,
        source: str,
        data: Dict[str, Any],
        iteration: int = 0
    ) -> None:
        """
        Publish an event.
        
        Args:
            event_type: Type of event
            source: Source engine/component
            data: Event data
            iteration: Simulation iteration
        """
        if not self._enabled:
            return
        
        event = SimulationEvent(
            event_type=event_type,
            timestamp=datetime.utcnow(),
            source=source,
            data=data,
            iteration=iteration
        )
        
        # Store in history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        # Notify handlers
        handlers_to_remove = []
        
        for handler in self._handlers.get(event_type, []):
            # Check filter
            if handler.filter_fn and not handler.filter_fn(data):
                continue
            
            # Call callback
            try:
                handler.callback(event)
            except Exception:
                pass  # Don't let handler errors break event processing
            
            # Mark one-time handlers for removal
            if handler.once:
                handlers_to_remove.append(handler)
        
        # Remove one-time handlers
        for handler in handlers_to_remove:
            self.unsubscribe(handler)
    
    def replay(
        self,
        event_types: Optional[List[EventType]] = None,
        from_time: Optional[datetime] = None,
        to_time: Optional[datetime] = None,
        callback: Optional[Callable[[SimulationEvent], None]] = None
    ) -> List[SimulationEvent]:
        """
        Replay events from history.
        
        Args:
            event_types: Filter by event types
            from_time: Start time
            to_time: End time
            callback: Optional callback for each event
            
        Returns:
            List of replayed events
        """
        events = self._event_history.copy()
        
        # Filter by type
        if event_types:
            events = [e for e in events if e.event_type in event_types]
        
        # Filter by time
        if from_time:
            events = [e for e in events if e.timestamp >= from_time]
        if to_time:
            events = [e for e in events if e.timestamp <= to_time]
        
        # Replay with callback
        if callback:
            for event in events:
                callback(event)
        
        return events
    
    def get_events(
        self,
        event_type: Optional[EventType] = None,
        source: Optional[str] = None,
        limit: int = 100
    ) -> List[SimulationEvent]:
        """Get events from history."""
        events = self._event_history.copy()
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if source:
            events = [e for e in events if e.source == source]
        
        return events[-limit:]
    
    def clear_history(self) -> None:
        """Clear event history."""
        self._event_history.clear()
    
    def enable(self) -> None:
        """Enable event bus."""
        self._enabled = True
    
    def disable(self) -> None:
        """Disable event bus."""
        self._enabled = False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics."""
        stats = {
            "total_events": len(self._event_history),
            "enabled": self._enabled,
            "handlers_count": sum(len(h) for h in self._handlers.values()),
            "event_types": {},
        }
        
        for event_type in EventType:
            count = len([e for e in self._event_history if e.event_type == event_type])
            if count > 0:
                stats["event_types"][event_type.value] = count
        
        return stats


# Global event bus instance
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


def reset_event_bus() -> None:
    """Reset the global event bus."""
    global _event_bus
    _event_bus = None
