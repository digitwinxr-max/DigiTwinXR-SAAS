"""
Diagnostics Engine

Provides diagnostic capabilities.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field


@dataclass
class DiagnosticEvent:
    """Represents a diagnostic event."""
    id: str
    event_type: str
    severity: str
    source: str
    message: str
    trace_id: Optional[str] = None
    request_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    resolved: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)


class DiagnosticsEngine:
    """
    Provides diagnostic capabilities.
    
    Supports:
    - Slow requests
    - Dead events
    - Trace gaps
    - Performance anomalies
    - Registry conflicts
    - EventBus diagnostics
    """
    
    def __init__(self):
        self._events: List[DiagnosticEvent] = []
        self._max_events = 1000
    
    def add_event(
        self,
        event_type: str,
        severity: str,
        source: str,
        message: str,
        trace_id: Optional[str] = None,
        request_id: Optional[str] = None,
        context: Optional[Dict] = None,
        recommendations: Optional[List[str]] = None
    ) -> DiagnosticEvent:
        """Add a diagnostic event."""
        import uuid
        event = DiagnosticEvent(
            id=str(uuid.uuid4()),
            event_type=event_type,
            severity=severity,
            source=source,
            message=message,
            trace_id=trace_id,
            request_id=request_id,
            context=context or {},
            recommendations=recommendations or []
        )
        
        self._events.append(event)
        
        # Trim if needed
        if len(self._events) > self._max_events:
            self._events = self._events[-self._max_events:]
        
        return event
    
    def get_slow_requests(
        self,
        threshold_ms: int = 1000,
        limit: int = 50
    ) -> List[Dict]:
        """Get slow requests."""
        slow = []
        for event in self._events:
            if event.event_type == "slow_request":
                duration = event.context.get("duration_ms", 0)
                if duration >= threshold_ms:
                    slow.append({
                        "request_id": event.request_id,
                        "trace_id": event.trace_id,
                        "duration_ms": duration,
                        "message": event.message,
                        "created_at": event.created_at.isoformat()
                    })
        
        return sorted(slow, key=lambda x: x["duration_ms"], reverse=True)[:limit]
    
    def get_dead_events(
        self,
        window_hours: int = 24
    ) -> List[Dict]:
        """Get dead/unprocessed events."""
        cutoff = datetime.utcnow() - timedelta(hours=window_hours)
        dead = []
        
        for event in self._events:
            if event.event_type == "dead_event" and event.created_at >= cutoff:
                dead.append({
                    "event_id": event.id,
                    "event_type": event.context.get("event_type"),
                    "message": event.message,
                    "created_at": event.created_at.isoformat()
                })
        
        return dead
    
    def get_trace_gaps(
        self,
        trace_id: str,
        expected_spans: int
    ) -> List[Dict]:
        """Get trace gaps."""
        gaps = []
        for event in self._events:
            if event.trace_id == trace_id and event.event_type == "trace_gap":
                gaps.append({
                    "gap_id": event.id,
                    "message": event.message,
                    "context": event.context,
                    "created_at": event.created_at.isoformat()
                })
        return gaps
    
    def get_performance_anomalies(
        self,
        window_hours: int = 24
    ) -> List[Dict]:
        """Get performance anomalies."""
        cutoff = datetime.utcnow() - timedelta(hours=window_hours)
        anomalies = []
        
        for event in self._events:
            if event.event_type == "performance_anomaly" and event.created_at >= cutoff:
                anomalies.append({
                    "anomaly_id": event.id,
                    "metric": event.context.get("metric"),
                    "expected": event.context.get("expected"),
                    "actual": event.context.get("actual"),
                    "deviation": event.context.get("deviation"),
                    "created_at": event.created_at.isoformat()
                })
        
        return anomalies
    
    def get_registry_conflicts(self) -> List[Dict]:
        """Get registry conflicts."""
        conflicts = []
        for event in self._events:
            if event.event_type == "registry_conflict":
                conflicts.append({
                    "conflict_id": event.id,
                    "registry": event.context.get("registry"),
                    "item": event.context.get("item"),
                    "message": event.message,
                    "created_at": event.created_at.isoformat()
                })
        return conflicts
    
    def get_eventbus_diagnostics(self) -> Dict:
        """Get EventBus diagnostics."""
        event_types = {}
        for event in self._events:
            if event.source == "eventbus":
                event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
        
        return {
            "total_events": len([e for e in self._events if e.source == "eventbus"]),
            "by_type": event_types,
            "unresolved_count": len([e for e in self._events if not e.resolved]),
            "recent_failures": len([
                e for e in self._events
                if e.source == "eventbus" and e.severity in ["error", "critical"]
            ])
        }
    
    def resolve_event(self, event_id: str) -> bool:
        """Mark an event as resolved."""
        for event in self._events:
            if event.id == event_id:
                event.resolved = True
                return True
        return False
    
    def get_unresolved_count(self) -> int:
        """Get count of unresolved events."""
        return len([e for e in self._events if not e.resolved])
