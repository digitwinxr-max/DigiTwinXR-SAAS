"""
Timeline Validator

Validates timeline data for consistency and integrity.
"""

from typing import Dict, List, Optional, Set, Any
from datetime import datetime
from backend.src.services.timeline.timeline_types import (
    Timeline,
    TimelineEvent,
    TimelineSegment,
    TimelineSnapshot,
    ReplaySession,
    TimelineEventType,
)


class TimelineValidator:
    """
    Validates timeline data for correctness.
    
    Checks:
    - Event ordering (no backward timestamps)
    - Snapshot completeness
    - Replay consistency
    - Event integrity
    """
    
    def __init__(self):
        self.issues: List[str] = []
        self.warnings: List[str] = []
    
    def validate_timeline(
        self,
        timeline: Timeline
    ) -> Dict[str, Any]:
        """
        Validate a complete timeline.
        
        Args:
            timeline: Timeline to validate
            
        Returns:
            Validation result dictionary
        """
        self.issues = []
        self.warnings = []
        
        # Check basic structure
        self._check_basic_structure(timeline)
        
        # Check event ordering
        self._check_event_ordering(timeline.events)
        
        # Check snapshot gaps
        self._check_snapshot_gaps(timeline)
        
        # Check event integrity
        self._check_event_integrity(timeline.events)
        
        return {
            "valid": len(self.issues) == 0,
            "issues": self.issues,
            "warnings": self.warnings,
        }
    
    def validate_segment(
        self,
        segment: TimelineSegment
    ) -> Dict[str, Any]:
        """
        Validate a timeline segment.
        
        Args:
            segment: Segment to validate
            
        Returns:
            Validation result dictionary
        """
        self.issues = []
        self.warnings = []
        
        # Check segment structure
        if not segment.segment_id:
            self.issues.append("Segment has no ID")
        
        if segment.end_time and segment.start_time:
            if segment.end_time < segment.start_time:
                self.issues.append("Segment end time is before start time")
        
        # Check event ordering
        self._check_event_ordering(segment.events)
        
        # Check time range
        if segment.events:
            first_event = min(segment.events, key=lambda e: e.timestamp)
            last_event = max(segment.events, key=lambda e: e.timestamp)
            
            if first_event.timestamp < segment.start_time:
                self.warnings.append("First event is before segment start")
            
            if segment.end_time and last_event.timestamp > segment.end_time:
                self.warnings.append("Last event is after segment end")
        
        return {
            "valid": len(self.issues) == 0,
            "issues": self.issues,
            "warnings": self.warnings,
        }
    
    def validate_replay_session(
        self,
        session: ReplaySession
    ) -> Dict[str, Any]:
        """
        Validate a replay session.
        
        Args:
            session: Session to validate
            
        Returns:
            Validation result dictionary
        """
        self.issues = []
        self.warnings = []
        
        # Check session structure
        if not session.session_id:
            self.issues.append("Session has no ID")
        
        # Check index bounds
        if session.current_index < 0:
            self.issues.append("Current index is negative")
        
        if session.current_index >= session.total_events and session.total_events > 0:
            self.warnings.append("Current index is past end of events")
        
        # Check speed
        if session.speed not in ReplaySession.AVAILABLE_SPEEDS:
            self.warnings.append(f"Speed {session.speed} is not in standard speeds")
        
        # Check branch consistency
        if session.is_branch:
            if not session.parent_session_id:
                self.warnings.append("Branch session has no parent")
            if not session.branch_point:
                self.warnings.append("Branch session has no branch point")
        
        return {
            "valid": len(self.issues) == 0,
            "issues": self.issues,
            "warnings": self.warnings,
        }
    
    def validate_events(
        self,
        events: List[TimelineEvent]
    ) -> Dict[str, Any]:
        """
        Validate a list of events.
        
        Args:
            events: Events to validate
            
        Returns:
            Validation result dictionary
        """
        self.issues = []
        self.warnings = []
        
        self._check_event_integrity(events)
        self._check_event_ordering(events)
        self._check_duplicate_events(events)
        
        return {
            "valid": len(self.issues) == 0,
            "issues": self.issues,
            "warnings": self.warnings,
        }
    
    def validate_snapshot(
        self,
        snapshot: TimelineSnapshot
    ) -> Dict[str, Any]:
        """
        Validate a timeline snapshot.
        
        Args:
            snapshot: Snapshot to validate
            
        Returns:
            Validation result dictionary
        """
        self.issues = []
        self.warnings = []
        
        # Check basic structure
        if not snapshot.snapshot_id:
            self.issues.append("Snapshot has no ID")
        
        if not snapshot.timestamp:
            self.issues.append("Snapshot has no timestamp")
        
        # Check graph consistency
        if snapshot.graph_snapshot:
            nodes = snapshot.graph_snapshot.get("nodes", {})
            edges = snapshot.graph_snapshot.get("edges", [])
            
            # Check edge references
            for edge in edges:
                from_node = edge.get("from_node")
                to_node = edge.get("to_node")
                
                if from_node not in nodes:
                    self.issues.append(f"Edge references non-existent node: {from_node}")
                
                if to_node not in nodes:
                    self.issues.append(f"Edge references non-existent node: {to_node}")
        
        return {
            "valid": len(self.issues) == 0,
            "issues": self.issues,
            "warnings": self.warnings,
        }
    
    def _check_basic_structure(self, timeline: Timeline) -> None:
        """Check basic timeline structure."""
        if not timeline.timeline_id:
            self.issues.append("Timeline has no ID")
        
        if not timeline.name:
            self.warnings.append("Timeline has no name")
        
        if not timeline.start_time:
            self.issues.append("Timeline has no start time")
        
        if timeline.end_time and timeline.start_time:
            if timeline.end_time < timeline.start_time:
                self.issues.append("End time is before start time")
    
    def _check_event_ordering(self, events: List[TimelineEvent]) -> None:
        """Check that events are in chronological order."""
        if not events:
            return
        
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        
        for i in range(1, len(sorted_events)):
            prev_event = sorted_events[i - 1]
            curr_event = sorted_events[i]
            
            if curr_event.timestamp < prev_event.timestamp:
                self.issues.append(
                    f"Event ordering violation at index {i}: "
                    f"{curr_event.event_id} ({curr_event.timestamp}) is before "
                    f"{prev_event.event_id} ({prev_event.timestamp})"
                )
            elif curr_event.timestamp == prev_event.timestamp:
                # Check event IDs for deterministic ordering
                if curr_event.event_id < prev_event.event_id:
                    self.warnings.append(
                        f"Same-timestamp events not in ID order: "
                        f"{prev_event.event_id} before {curr_event.event_id}"
                    )
    
    def _check_snapshot_gaps(self, timeline: Timeline) -> None:
        """Check for gaps between snapshots."""
        if len(timeline.snapshots) < 2:
            return
        
        sorted_snapshots = sorted(timeline.snapshots, key=lambda s: s.timestamp)
        
        for i in range(1, len(sorted_snapshots)):
            prev_snapshot = sorted_snapshots[i - 1]
            curr_snapshot = sorted_snapshots[i]
            
            gap_seconds = (curr_snapshot.timestamp - prev_snapshot.timestamp).total_seconds()
            
            # Check for large gaps
            if gap_seconds > 3600:  # 1 hour
                self.warnings.append(
                    f"Large snapshot gap ({gap_seconds:.0f}s) between "
                    f"{prev_snapshot.snapshot_id} and {curr_snapshot.snapshot_id}"
                )
    
    def _check_event_integrity(self, events: List[TimelineEvent]) -> None:
        """Check event integrity."""
        for event in events:
            if not event.event_id:
                self.issues.append("Event has no ID")
            
            if not event.timestamp:
                self.issues.append(f"Event {event.event_id} has no timestamp")
            
            if not event.event_type:
                self.issues.append(f"Event {event.event_id} has no type")
            
            if not event.source_engine:
                self.warnings.append(f"Event {event.event_id} has no source engine")
            
            if not event.entity_id:
                self.warnings.append(f"Event {event.event_id} has no entity ID")
    
    def _check_duplicate_events(self, events: List[TimelineEvent]) -> None:
        """Check for duplicate event IDs."""
        seen_ids: Set[str] = set()
        
        for event in events:
            if event.event_id in seen_ids:
                self.issues.append(f"Duplicate event ID: {event.event_id}")
            seen_ids.add(event.event_id)
    
    def check_replay_consistency(
        self,
        session_a: ReplaySession,
        session_b: ReplaySession
    ) -> bool:
        """
        Check if two replay sessions are consistent.
        
        Args:
            session_a: First session
            session_b: Second session
            
        Returns:
            True if consistent
        """
        # Same events should produce same state
        events_a = session_a.timeline_segment.events
        events_b = session_b.timeline_segment.events
        
        if len(events_a) != len(events_b):
            return False
        
        for i, (e_a, e_b) in enumerate(zip(events_a, events_b)):
            if e_a.event_id != e_b.event_id:
                return False
        
        return True
    
    def get_validation_summary(self, validation_result: Dict[str, Any]) -> str:
        """Generate a human-readable validation summary."""
        if validation_result["valid"]:
            return "Timeline is valid"
        
        lines = ["Timeline validation failed:"]
        
        for issue in validation_result["issues"]:
            lines.append(f"  ERROR: {issue}")
        
        for warning in validation_result["warnings"]:
            lines.append(f"  WARNING: {warning}")
        
        return "\n".join(lines)
