"""
Event Recorder

Records events from the EventBus to create operational timelines.
Acts as the system's black box recorder.
"""

import uuid
from typing import Dict, List, Optional, Callable
from datetime import datetime
from backend.src.core.events import EventBus, EventType, SimulationEvent, get_event_bus
from backend.src.services.timeline.timeline_types import (
    TimelineEvent,
    TimelineEventType,
    Severity,
)


class EventRecorder:
    """
    Records events from the EventBus.
    
    Subscribes to EventBus events and records them to a timeline.
    Acts as the system's black box recorder.
    """
    
    # Map EventBus event types to Timeline event types
    EVENT_TYPE_MAP = {
        EventType.NODE_FAILED: TimelineEventType.NODE_FAILED,
        EventType.NODE_RECOVERED: TimelineEventType.NODE_RECOVERED,
        EventType.NODE_DEGRADED: TimelineEventType.NODE_DEGRADED,
        EventType.EDGE_FAILED: TimelineEventType.EDGE_FAILED,
        EventType.EDGE_RECOVERED: TimelineEventType.EDGE_RECOVERED,
        EventType.EDGE_OVERLOADED: TimelineEventType.EDGE_OVERLOADED,
        EventType.LOAD_INCREASED: TimelineEventType.LOAD_INCREASED,
        EventType.LOAD_DECREASED: TimelineEventType.LOAD_DECREASED,
        EventType.FLOW_CHANGED: TimelineEventType.FLOW_CHANGED,
        EventType.BOTTLENECK_DETECTED: TimelineEventType.BOTTLENECK_DETECTED,
        EventType.ROUTE_CHANGED: TimelineEventType.ROUTE_CHANGED,
        EventType.ROUTE_FOUND: TimelineEventType.ROUTE_FOUND,
        EventType.ROUTE_FAILED: TimelineEventType.ROUTE_FAILED,
        EventType.RESILIENCE_UPDATED: TimelineEventType.RESILIENCE_UPDATED,
        EventType.CRITICAL_NODE_IDENTIFIED: TimelineEventType.CRITICAL_NODE_IDENTIFIED,
        EventType.CRITICAL_EDGE_IDENTIFIED: TimelineEventType.CRITICAL_EDGE_IDENTIFIED,
        EventType.SIMULATION_STARTED: TimelineEventType.TIMELINE_STARTED,
        EventType.SIMULATION_STOPPED: TimelineEventType.TIMELINE_STOPPED,
        EventType.RECOVERY_STARTED: TimelineEventType.RECOVERY_STARTED,
        EventType.RECOVERY_COMPLETED: TimelineEventType.RECOVERY_COMPLETED,
    }
    
    # Map EventBus event types to severity
    SEVERITY_MAP = {
        EventType.NODE_FAILED: Severity.ERROR,
        EventType.EDGE_FAILED: Severity.ERROR,
        EventType.ROUTE_FAILED: Severity.ERROR,
        EventType.BOTTLENECK_DETECTED: Severity.WARNING,
        EventType.LOAD_INCREASED: Severity.WARNING,
        EventType.NODE_DEGRADED: Severity.WARNING,
        EventType.EDGE_OVERLOADED: Severity.WARNING,
        EventType.ROUTE_CHANGED: Severity.INFO,
        EventType.FLOW_CHANGED: Severity.INFO,
        EventType.NODE_RECOVERED: Severity.INFO,
        EventType.EDGE_RECOVERED: Severity.INFO,
        EventType.SIMULATION_STARTED: Severity.INFO,
        EventType.SIMULATION_STOPPED: Severity.INFO,
    }
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        self.event_bus = event_bus or get_event_bus()
        self.recorded_events: List[TimelineEvent] = []
        self._subscription = None
        self._is_recording = False
        self._recording_start: Optional[datetime] = None
    
    def start_recording(self) -> None:
        """Start recording events."""
        if self._is_recording:
            return
        
        self._is_recording = True
        self._recording_start = datetime.utcnow()
        self.recorded_events = []
        
        # Subscribe to EventBus
        self._subscription = self.event_bus.subscribe(
            event_types=list(self.EVENT_TYPE_MAP.keys()),
            callback=self._on_event
        )
    
    def stop_recording(self) -> List[TimelineEvent]:
        """Stop recording and return recorded events."""
        self._is_recording = False
        
        if self._subscription:
            self.event_bus.unsubscribe(self._subscription)
            self._subscription = None
        
        return self.recorded_events.copy()
    
    def record_event(
        self,
        event_type: TimelineEventType,
        source_engine: str,
        entity_id: str,
        payload: Optional[Dict] = None,
        severity: Optional[Severity] = None,
        metadata: Optional[Dict] = None
    ) -> TimelineEvent:
        """
        Manually record an event.
        
        Args:
            event_type: Type of event
            source_engine: Source engine name
            entity_id: Entity ID (node or edge)
            payload: Event payload
            severity: Event severity
            metadata: Additional metadata
            
        Returns:
            Created TimelineEvent
        """
        event = TimelineEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            event_type=event_type,
            source_engine=source_engine,
            entity_id=entity_id,
            payload=payload or {},
            severity=severity or Severity.INFO,
            metadata=metadata or {}
        )
        
        self.recorded_events.append(event)
        return event
    
    def batch_record(self, events: List[Dict]) -> List[TimelineEvent]:
        """
        Record a batch of events.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            Created TimelineEvents
        """
        created = []
        for event_data in events:
            event = TimelineEvent(
                event_id=event_data.get("event_id", str(uuid.uuid4())),
                timestamp=datetime.fromisoformat(event_data["timestamp"]) if "timestamp" in event_data else datetime.utcnow(),
                event_type=TimelineEventType(event_data["event_type"]),
                source_engine=event_data["source_engine"],
                entity_id=event_data["entity_id"],
                payload=event_data.get("payload", {}),
                severity=Severity(event_data.get("severity", "info")),
                metadata=event_data.get("metadata", {})
            )
            self.recorded_events.append(event)
            created.append(event)
        
        return created
    
    def filter_events(
        self,
        event_types: Optional[List[TimelineEventType]] = None,
        severities: Optional[List[Severity]] = None,
        entity_ids: Optional[List[str]] = None,
        source_engines: Optional[List[str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[TimelineEvent]:
        """
        Filter recorded events.
        
        Args:
            event_types: Filter by event types
            severities: Filter by severities
            entity_ids: Filter by entity IDs
            source_engines: Filter by source engines
            start_time: Filter by start time
            end_time: Filter by end time
            
        Returns:
            Filtered events
        """
        filtered = self.recorded_events
        
        if event_types:
            filtered = [e for e in filtered if e.event_type in event_types]
        
        if severities:
            filtered = [e for e in filtered if e.severity in severities]
        
        if entity_ids:
            filtered = [e for e in filtered if e.entity_id in entity_ids]
        
        if source_engines:
            filtered = [e for e in filtered if e.source_engine in source_engines]
        
        if start_time:
            filtered = [e for e in filtered if e.timestamp >= start_time]
        
        if end_time:
            filtered = [e for e in filtered if e.timestamp <= end_time]
        
        return filtered
    
    def get_events(self) -> List[TimelineEvent]:
        """Get all recorded events."""
        return self.recorded_events.copy()
    
    def clear_events(self) -> None:
        """Clear all recorded events."""
        self.recorded_events = []
    
    def _on_event(self, event: SimulationEvent) -> None:
        """Handle EventBus event."""
        if not self._is_recording:
            return
        
        # Convert EventBus event to Timeline event
        timeline_event = self._convert_event(event)
        if timeline_event:
            self.recorded_events.append(timeline_event)
    
    def _convert_event(self, event: SimulationEvent) -> Optional[TimelineEvent]:
        """Convert EventBus event to TimelineEvent."""
        # Map event type
        timeline_type = self.EVENT_TYPE_MAP.get(event.event_type)
        if not timeline_type:
            return None
        
        # Map severity
        severity = self.SEVERITY_MAP.get(event.event_type, Severity.INFO)
        
        # Extract entity ID from data
        entity_id = event.data.get("entity_id", event.data.get("node_id", "unknown"))
        
        # Extract relevant data
        payload = {
            k: v for k, v in event.data.items()
            if k not in ["entity_id", "node_id"]
        }
        
        return TimelineEvent(
            event_id=str(uuid.uuid4()),
            timestamp=event.timestamp,
            event_type=timeline_type,
            source_engine=event.source,
            entity_id=entity_id,
            payload=payload,
            severity=severity,
            metadata={
                "original_event_type": event.event_type.value,
                "iteration": event.iteration
            }
        )
    
    def persist_session(self, filepath: str) -> None:
        """
        Persist recording session to file.
        
        Args:
            filepath: Path to save file
        """
        import json
        
        data = {
            "session_id": str(uuid.uuid4()),
            "recording_start": self._recording_start.isoformat() if self._recording_start else None,
            "recording_end": datetime.utcnow().isoformat(),
            "event_count": len(self.recorded_events),
            "events": [e.to_dict() for e in self.recorded_events]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_session(self, filepath: str) -> None:
        """
        Load recording session from file.
        
        Args:
            filepath: Path to load file
        """
        import json
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.recorded_events = [
            TimelineEvent.from_dict(e) for e in data.get("events", [])
        ]
    
    def get_stats(self) -> Dict:
        """Get recording statistics."""
        stats = {
            "is_recording": self._is_recording,
            "total_events": len(self.recorded_events),
            "events_by_type": {},
            "events_by_severity": {},
            "events_by_source": {},
        }
        
        for event in self.recorded_events:
            # By type
            type_key = event.event_type.value
            stats["events_by_type"][type_key] = stats["events_by_type"].get(type_key, 0) + 1
            
            # By severity
            sev_key = event.severity.value
            stats["events_by_severity"][sev_key] = stats["events_by_severity"].get(sev_key, 0) + 1
            
            # By source
            src_key = event.source_engine
            stats["events_by_source"][src_key] = stats["events_by_source"].get(src_key, 0) + 1
        
        return stats
