"""
Timeline Engine

Main coordinator for operational timeline and time-travel capabilities.
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from backend.src.services.timeline.timeline_types import (
    Timeline,
    TimelineEvent,
    TimelineSegment,
    TimelineSnapshot,
    Severity,
    TimelineEventType,
)
from backend.src.services.timeline.event_recorder import EventRecorder
from backend.src.services.timeline.snapshot_manager import SnapshotManager
from backend.src.core.events import get_event_bus, EventType


class TimelineEngine:
    """
    Main coordinator for operational timeline.
    
    Coordinates recording, snapshot capture, and timeline building.
    """
    
    def __init__(self):
        self.recorder = EventRecorder()
        self.snapshot_manager = SnapshotManager()
        self.timelines: Dict[str, Timeline] = {}
        self.current_timeline: Optional[Timeline] = None
        self._is_recording = False
    
    def start_recording(
        self,
        name: str = "recording",
        description: str = ""
    ) -> Timeline:
        """
        Start recording a new timeline.
        
        Args:
            name: Timeline name
            description: Timeline description
            
        Returns:
            Created Timeline
        """
        if self._is_recording:
            raise RuntimeError("Already recording")
        
        timeline_id = str(uuid.uuid4())
        
        timeline = Timeline(
            timeline_id=timeline_id,
            name=name,
            description=description,
            start_time=datetime.utcnow(),
            end_time=None,
            events=[],
            snapshots=[],
            segments=[],
            metadata={},
            tags=[]
        )
        
        self.timelines[timeline_id] = timeline
        self.current_timeline = timeline
        self._is_recording = True
        
        # Start event recording
        self.recorder.start_recording()
        
        return timeline
    
    def stop_recording(self) -> Optional[Timeline]:
        """
        Stop recording.
        
        Returns:
            Completed Timeline or None
        """
        if not self._is_recording:
            return None
        
        self._is_recording = False
        
        # Stop event recording
        events = self.recorder.stop_recording()
        
        if self.current_timeline:
            self.current_timeline.end_time = datetime.utcnow()
            self.current_timeline.events = events
        
        timeline = self.current_timeline
        self.current_timeline = None
        
        return timeline
    
    def capture_snapshot(
        self,
        label: Optional[str] = None,
        graph: Optional[Any] = None,
        metadata: Optional[Dict] = None
    ) -> TimelineSnapshot:
        """
        Capture a snapshot during recording.
        
        Args:
            label: Snapshot label
            graph: Current graph state
            metadata: Additional metadata
            
        Returns:
            Created TimelineSnapshot
        """
        snapshot_id = label or f"snap-{uuid.uuid4().hex[:8]}"
        
        snapshot = self.snapshot_manager.capture_snapshot(
            snapshot_id=snapshot_id,
            graph=graph,
            metadata=metadata
        )
        
        if self.current_timeline:
            self.current_timeline.snapshots.append(snapshot)
        
        return snapshot
    
    def add_event(
        self,
        event_type: TimelineEventType,
        source_engine: str,
        entity_id: str,
        payload: Optional[Dict] = None,
        severity: Severity = Severity.INFO
    ) -> TimelineEvent:
        """
        Manually add an event to the timeline.
        
        Args:
            event_type: Type of event
            source_engine: Source engine name
            entity_id: Entity ID
            payload: Event payload
            severity: Event severity
            
        Returns:
            Created TimelineEvent
        """
        event = self.recorder.record_event(
            event_type=event_type,
            source_engine=source_engine,
            entity_id=entity_id,
            payload=payload,
            severity=severity
        )
        
        if self.current_timeline:
            self.current_timeline.events.append(event)
        
        return event
    
    def get_timeline(self, timeline_id: Optional[str] = None) -> Optional[Timeline]:
        """
        Get a timeline by ID.
        
        Args:
            timeline_id: Timeline ID (uses current if None)
            
        Returns:
            Timeline or None
        """
        if timeline_id:
            return self.timelines.get(timeline_id)
        return self.current_timeline
    
    def list_timelines(self) -> List[Dict]:
        """List all timelines."""
        return [t.to_dict() for t in self.timelines.values()]
    
    def build_incident_timeline(
        self,
        incident_id: str,
        start_time: datetime,
        end_time: datetime,
        events: List[TimelineEvent],
        snapshots: Optional[List[TimelineSnapshot]] = None
    ) -> TimelineSegment:
        """
        Build a timeline segment for an incident.
        
        Args:
            incident_id: Incident identifier
            start_time: Start time
            end_time: End time
            events: Events in the incident
            snapshots: Optional snapshots
            
        Returns:
            Built TimelineSegment
        """
        segment = TimelineSegment(
            segment_id=f"incident-{incident_id}",
            start_time=start_time,
            end_time=end_time,
            events=events,
            snapshots=snapshots or []
        )
        
        return segment
    
    def export_timeline(
        self,
        timeline_id: str,
        format: str = "json"
    ) -> Optional[Dict]:
        """
        Export a timeline.
        
        Args:
            timeline_id: Timeline ID
            format: Export format (json, csv)
            
        Returns:
            Exported timeline data
        """
        timeline = self.timelines.get(timeline_id)
        if not timeline:
            return None
        
        if format == "json":
            return {
                "timeline": timeline.to_dict(),
                "events": [e.to_dict() for e in timeline.events],
                "snapshots": [s.to_dict() for s in timeline.snapshots],
            }
        
        return timeline.to_dict()
    
    def delete_timeline(self, timeline_id: str) -> bool:
        """Delete a timeline."""
        if timeline_id in self.timelines:
            del self.timelines[timeline_id]
            return True
        return False
    
    def get_recording_status(self) -> Dict:
        """Get current recording status."""
        return {
            "is_recording": self._is_recording,
            "current_timeline": self.current_timeline.timeline_id if self.current_timeline else None,
            "total_timelines": len(self.timelines),
            "event_count": len(self.recorder.recorded_events),
            "snapshot_count": len(self.snapshot_manager.snapshots),
        }
    
    def reset(self) -> None:
        """Reset the timeline engine."""
        self.recorder.stop_recording()
        self.recorder.clear_events()
        self.snapshot_manager.clear_snapshots()
        self.timelines.clear()
        self.current_timeline = None
        self._is_recording = False
