"""
Timeline Query Engine

Provides query capabilities for timeline data.
"""

from typing import Dict, List, Optional, Set
from datetime import datetime
from backend.src.services.timeline.timeline_types import (
    Timeline,
    TimelineEvent,
    TimelineSegment,
    TimelineQuery,
    TimelineEventType,
    Severity,
)


class TimelineQueryEngine:
    """
    Query engine for timeline data.
    
    Provides filtering and search capabilities.
    """
    
    def __init__(self, timeline: Optional[Timeline] = None):
        self.timeline = timeline
    
    def set_timeline(self, timeline: Timeline) -> None:
        """Set the timeline to query."""
        self.timeline = timeline
    
    def query(self, query: TimelineQuery) -> List[TimelineEvent]:
        """
        Execute a timeline query.
        
        Args:
            query: Query parameters
            
        Returns:
            Matching events
        """
        if not self.timeline:
            return []
        
        events = self.timeline.events
        
        # Filter by time range
        if query.start_time:
            events = [e for e in events if e.timestamp >= query.start_time]
        
        if query.end_time:
            events = [e for e in events if e.timestamp <= query.end_time]
        
        # Filter by event types
        if query.event_types:
            events = [e for e in events if e.event_type in query.event_types]
        
        # Filter by severities
        if query.severities:
            events = [e for e in events if e.severity in query.severities]
        
        # Filter by entity IDs
        if query.entity_ids:
            events = [e for e in events if e.entity_id in query.entity_ids]
        
        # Filter by source engines
        if query.source_engines:
            events = [e for e in events if e.source_engine in query.source_engines]
        
        # Filter by search text
        if query.search_text:
            search_lower = query.search_text.lower()
            events = [
                e for e in events
                if search_lower in e.entity_id.lower() or
                   search_lower in e.event_type.value.lower() or
                   search_lower in str(e.payload).lower()
            ]
        
        # Apply limit
        return events[:query.limit]
    
    def get_events_between(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[TimelineEvent]:
        """Get events within time range."""
        return self.query(TimelineQuery(
            start_time=start_time,
            end_time=end_time
        ))
    
    def get_events_by_type(
        self,
        event_types: List[TimelineEventType]
    ) -> List[TimelineEvent]:
        """Get events by type."""
        return self.query(TimelineQuery(
            event_types=set(event_types)
        ))
    
    def get_events_by_asset(self, asset_id: str) -> List[TimelineEvent]:
        """Get all events related to an asset."""
        return self.query(TimelineQuery(
            entity_ids={asset_id}
        ))
    
    def get_failures(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[TimelineEvent]:
        """Get all failure events."""
        failure_types = {
            TimelineEventType.NODE_FAILED,
            TimelineEventType.EDGE_FAILED,
            TimelineEventType.ROUTE_FAILED,
        }
        
        return self.query(TimelineQuery(
            start_time=start_time,
            end_time=end_time,
            event_types=failure_types,
            severities={Severity.ERROR, Severity.CRITICAL}
        ))
    
    def get_recoveries(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[TimelineEvent]:
        """Get all recovery events."""
        recovery_types = {
            TimelineEventType.NODE_RECOVERED,
            TimelineEventType.EDGE_RECOVERED,
            TimelineEventType.RECOVERY_COMPLETED,
        }
        
        return self.query(TimelineQuery(
            start_time=start_time,
            end_time=end_time,
            event_types=recovery_types
        ))
    
    def get_route_changes(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[TimelineEvent]:
        """Get all route change events."""
        return self.query(TimelineQuery(
            start_time=start_time,
            end_time=end_time,
            event_types={TimelineEventType.ROUTE_CHANGED}
        ))
    
    def get_flow_anomalies(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[TimelineEvent]:
        """Get all flow anomaly events."""
        anomaly_types = {
            TimelineEventType.BOTTLENECK_DETECTED,
            TimelineEventType.LOAD_INCREASED,
            TimelineEventType.EDGE_OVERLOADED,
        }
        
        return self.query(TimelineQuery(
            start_time=start_time,
            end_time=end_time,
            event_types=anomaly_types,
            severities={Severity.WARNING, Severity.ERROR}
        ))
    
    def get_critical_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[TimelineEvent]:
        """Get critical severity events."""
        return self.query(TimelineQuery(
            start_time=start_time,
            end_time=end_time,
            severities={Severity.CRITICAL, Severity.ERROR}
        ))
    
    def get_events_by_severity(
        self,
        severity: Severity
    ) -> List[TimelineEvent]:
        """Get events by severity."""
        return self.query(TimelineQuery(
            severities={severity}
        ))
    
    def search(self, text: str, limit: int = 100) -> List[TimelineEvent]:
        """Full-text search in timeline."""
        return self.query(TimelineQuery(
            search_text=text,
            limit=limit
        ))
    
    def get_event_timeline(
        self,
        entity_id: str
    ) -> List[TimelineEvent]:
        """Get chronological events for an entity."""
        events = self.get_events_by_asset(entity_id)
        return sorted(events, key=lambda e: e.timestamp)
    
    def get_event_summary(self) -> Dict:
        """Get summary statistics of events."""
        if not self.timeline:
            return {}
        
        events = self.timeline.events
        
        summary = {
            "total_events": len(events),
            "by_type": {},
            "by_severity": {},
            "by_source": {},
            "time_range": {
                "first": None,
                "last": None,
            }
        }
        
        if events:
            for event in events:
                # By type
                type_key = event.event_type.value
                summary["by_type"][type_key] = summary["by_type"].get(type_key, 0) + 1
                
                # By severity
                sev_key = event.severity.value
                summary["by_severity"][sev_key] = summary["by_severity"].get(sev_key, 0) + 1
                
                # By source
                src_key = event.source_engine
                summary["by_source"][src_key] = summary["by_source"].get(src_key, 0) + 1
            
            # Time range
            sorted_events = sorted(events, key=lambda e: e.timestamp)
            summary["time_range"]["first"] = sorted_events[0].timestamp.isoformat()
            summary["time_range"]["last"] = sorted_events[-1].timestamp.isoformat()
        
        return summary
    
    def get_incidents(self) -> List[Dict]:
        """Identify incident patterns."""
        if not self.timeline:
            return []
        
        incidents = []
        current_incident = None
        
        # Sort events by time
        events = sorted(self.timeline.events, key=lambda e: e.timestamp)
        
        for event in events:
            # Check if this is a failure event
            if event.event_type in {
                TimelineEventType.NODE_FAILED,
                TimelineEventType.EDGE_FAILED,
                TimelineEventType.ROUTE_FAILED,
            }:
                # Start new incident
                if current_incident:
                    incidents.append(current_incident)
                
                current_incident = {
                    "start_time": event.timestamp,
                    "end_time": event.timestamp,
                    "failed_entities": [event.entity_id],
                    "events": [event],
                    "status": "ongoing"
                }
            
            elif current_incident:
                # Add to current incident
                current_incident["events"].append(event)
                current_incident["end_time"] = event.timestamp
                
                # Check if recovered
                if event.event_type in {
                    TimelineEventType.NODE_RECOVERED,
                    TimelineEventType.EDGE_RECOVERED,
                }:
                    if event.entity_id in current_incident.get("recovered_entities", []):
                        pass
                    else:
                        current_incident.setdefault("recovered_entities", []).append(event.entity_id)
                    
                    # Check if all recovered
                    if set(current_incident["failed_entities"]) == set(current_incident.get("recovered_entities", [])):
                        current_incident["status"] = "resolved"
                        incidents.append(current_incident)
                        current_incident = None
        
        # Add ongoing incident
        if current_incident:
            incidents.append(current_incident)
        
        return incidents
    
    def get_causal_chain(
        self,
        start_event: TimelineEvent
    ) -> List[TimelineEvent]:
        """Trace causal chain from an event."""
        if not self.timeline:
            return []
        
        chain = [start_event]
        current_event = start_event
        
        # Find events after this one that might be caused by it
        events_after = [
            e for e in self.timeline.events
            if e.timestamp > start_event.timestamp
        ]
        
        for event in sorted(events_after, key=lambda e: e.timestamp):
            # Simple heuristic: events of same entity after failure
            if event.entity_id == current_event.entity_id:
                chain.append(event)
                current_event = event
        
        return chain
