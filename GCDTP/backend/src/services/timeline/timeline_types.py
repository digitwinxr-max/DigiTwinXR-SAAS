"""
Timeline Types

Core data types for operational timeline and digital twin time machine.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from enum import Enum
from copy import deepcopy


class Severity(str, Enum):
    """Event severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class TimelineEventType(str, Enum):
    """Timeline event types."""
    # Infrastructure events
    NODE_FAILED = "node_failed"
    NODE_RECOVERED = "node_recovered"
    NODE_DEGRADED = "node_degraded"
    EDGE_FAILED = "edge_failed"
    EDGE_RECOVERED = "edge_recovered"
    EDGE_OVERLOADED = "edge_overloaded"
    
    # Flow events
    FLOW_CHANGED = "flow_changed"
    LOAD_INCREASED = "load_increased"
    LOAD_DECREASED = "load_decreased"
    BOTTLENECK_DETECTED = "bottleneck_detected"
    
    # Route events
    ROUTE_CHANGED = "route_changed"
    ROUTE_FOUND = "route_found"
    ROUTE_FAILED = "route_failed"
    
    # Analysis events
    RESILIENCE_UPDATED = "resilience_updated"
    CRITICAL_NODE_IDENTIFIED = "critical_node_identified"
    CRITICAL_EDGE_IDENTIFIED = "critical_edge_identified"
    
    # Timeline events
    SNAPSHOT_CREATED = "snapshot_created"
    TIMELINE_STARTED = "timeline_started"
    TIMELINE_STOPPED = "timeline_stopped"
    REPLAY_STARTED = "replay_started"
    REPLAY_PAUSED = "replay_paused"
    REPLAY_RESUMED = "replay_resumed"
    REPLAY_COMPLETED = "replay_completed"
    REPLAY_STOPPED = "replay_stopped"
    SEEK_POSITION_CHANGED = "seek_position_changed"
    
    # Recovery events
    RECOVERY_STARTED = "recovery_started"
    RECOVERY_COMPLETED = "recovery_completed"
    RECOVERY_FAILED = "recovery_failed"


class ReplayState(str, Enum):
    """Replay session state."""
    IDLE = "idle"
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"


class DiffType(str, Enum):
    """Type of difference."""
    ADDED = "added"
    REMOVED = "removed"
    CHANGED = "changed"
    UNCHANGED = "unchanged"


@dataclass
class TimelineEvent:
    """
    A recorded event in the timeline.
    
    Represents something that happened in the system.
    """
    event_id: str
    timestamp: datetime
    event_type: TimelineEventType
    source_engine: str
    entity_id: str  # Node or edge ID
    payload: Dict[str, Any] = field(default_factory=dict)
    severity: Severity = Severity.INFO
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value,
            "source_engine": self.source_engine,
            "entity_id": self.entity_id,
            "payload": self.payload,
            "severity": self.severity.value,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "TimelineEvent":
        data = data.copy()
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        data["event_type"] = TimelineEventType(data["event_type"])
        data["severity"] = Severity(data["severity"])
        return cls(**data)


@dataclass
class AssetState:
    """State of an asset at a point in time."""
    asset_id: str
    status: str
    health: float
    load: float
    capacity: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "asset_id": self.asset_id,
            "status": self.status,
            "health": self.health,
            "load": self.load,
            "capacity": self.capacity,
            "metadata": self.metadata,
        }


@dataclass
class FlowState:
    """State of flow through the network."""
    route_id: str
    source: str
    destination: str
    path: List[str]
    load: float
    utilization: float
    status: str
    
    def to_dict(self) -> Dict:
        return {
            "route_id": self.route_id,
            "source": self.source,
            "destination": self.destination,
            "path": self.path,
            "load": self.load,
            "utilization": self.utilization,
            "status": self.status,
        }


@dataclass
class ResilienceState:
    """Resilience metrics at a point in time."""
    timestamp: datetime
    network_score: float
    critical_nodes: List[str]
    critical_edges: List[str]
    bottlenecks: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "network_score": self.network_score,
            "critical_nodes": self.critical_nodes,
            "critical_edges": self.critical_edges,
            "bottlenecks": self.bottlenecks,
        }


@dataclass
class TopologySnapshot:
    """
    Complete snapshot of topology state.
    
    Captures graph structure and node/edge states.
    """
    snapshot_id: str
    timestamp: datetime
    nodes: Dict[str, Dict] = field(default_factory=dict)
    edges: List[Dict] = field(default_factory=list)
    asset_states: Dict[str, AssetState] = field(default_factory=dict)
    flow_states: List[FlowState] = field(default_factory=list)
    resilience_state: Optional[ResilienceState] = None
    
    def to_dict(self) -> Dict:
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp.isoformat(),
            "nodes": self.nodes,
            "edges": self.edges,
            "asset_states": {k: v.to_dict() for k, v in self.asset_states.items()},
            "flow_states": [f.to_dict() for f in self.flow_states],
            "resilience_state": self.resilience_state.to_dict() if self.resilience_state else None,
        }


@dataclass
class TimelineSnapshot:
    """
    Complete timeline snapshot including all state.
    
    Used for save/restore and comparison.
    """
    snapshot_id: str
    timestamp: datetime
    graph_snapshot: Optional[Dict] = None
    asset_states: Dict[str, AssetState] = field(default_factory=dict)
    flow_states: List[FlowState] = field(default_factory=list)
    resilience_state: Optional[ResilienceState] = None
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp.isoformat(),
            "graph_snapshot": self.graph_snapshot,
            "asset_states": {k: v.to_dict() for k, v in self.asset_states.items()},
            "flow_states": [f.to_dict() for f in self.flow_states],
            "resilience_state": self.resilience_state.to_dict() if self.resilience_state else None,
            "context": self.context,
            "metadata": self.metadata,
        }


@dataclass
class TimelineSegment:
    """
    A segment of the timeline.
    
    Contains events and snapshots within a time range.
    """
    segment_id: str
    start_time: datetime
    end_time: datetime
    events: List[TimelineEvent] = field(default_factory=list)
    snapshots: List[TimelineSnapshot] = field(default_factory=list)
    
    duration_seconds: float = 0.0
    event_count: int = 0
    snapshot_count: int = 0
    
    def __post_init__(self):
        if self.events:
            self.event_count = len(self.events)
        if self.snapshots:
            self.snapshot_count = len(self.snapshots)
        if self.end_time and self.start_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict:
        return {
            "segment_id": self.segment_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_seconds": self.duration_seconds,
            "event_count": self.event_count,
            "snapshot_count": self.snapshot_count,
            "events": [e.to_dict() for e in self.events],
            "snapshots": [s.to_dict() for s in self.snapshots],
        }


@dataclass
class ReplaySession:
    """
    A replay session for time-travel playback.
    
    Tracks playback state and position.
    """
    session_id: str
    timeline_segment: TimelineSegment
    speed: float = 1.0
    current_index: int = 0
    current_time: Optional[datetime] = None
    state: ReplayState = ReplayState.IDLE
    
    # Branching support
    is_branch: bool = False
    parent_session_id: Optional[str] = None
    branch_point: Optional[datetime] = None
    
    # Filters
    filters: Dict[str, Any] = field(default_factory=dict)
    
    # Available speeds
    AVAILABLE_SPEEDS = [0.25, 0.5, 1.0, 2.0, 10.0, 100.0]
    
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "speed": self.speed,
            "current_index": self.current_index,
            "current_time": self.current_time.isoformat() if self.current_time else None,
            "state": self.state.value,
            "is_branch": self.is_branch,
            "parent_session_id": self.parent_session_id,
            "filters": self.filters,
        }
    
    @property
    def total_events(self) -> int:
        """Total number of events in session."""
        return len(self.timeline_segment.events)
    
    @property
    def progress(self) -> float:
        """Playback progress (0-1)."""
        if self.total_events == 0:
            return 0.0
        return self.current_index / self.total_events
    
    @property
    def is_complete(self) -> bool:
        """Check if replay is complete."""
        return self.current_index >= self.total_events


@dataclass
class DiffResult:
    """Result of comparing two snapshots."""
    snapshot_a_id: str
    snapshot_b_id: str
    timestamp_a: datetime
    timestamp_b: datetime
    
    # Node changes
    nodes_added: List[str] = field(default_factory=list)
    nodes_removed: List[str] = field(default_factory=list)
    nodes_changed: Dict[str, Dict] = field(default_factory=dict)
    
    # Edge changes
    edges_added: List[Dict] = field(default_factory=list)
    edges_removed: List[Dict] = field(default_factory=list)
    
    # State changes
    asset_states_changed: Dict[str, Dict] = field(default_factory=dict)
    flow_states_changed: Dict[str, Dict] = field(default_factory=list)
    
    # Summary
    total_changes: int = 0
    summary: str = ""
    
    def __post_init__(self):
        self.total_changes = (
            len(self.nodes_added) +
            len(self.nodes_removed) +
            len(self.nodes_changed) +
            len(self.edges_added) +
            len(self.edges_removed) +
            len(self.asset_states_changed) +
            len(self.flow_states_changed)
        )
    
    def to_dict(self) -> Dict:
        return {
            "snapshot_a_id": self.snapshot_a_id,
            "snapshot_b_id": self.snapshot_b_id,
            "timestamp_a": self.timestamp_a.isoformat(),
            "timestamp_b": self.timestamp_b.isoformat(),
            "nodes_added": self.nodes_added,
            "nodes_removed": self.nodes_removed,
            "nodes_changed": self.nodes_changed,
            "edges_added": self.edges_added,
            "edges_removed": self.edges_removed,
            "asset_states_changed": self.asset_states_changed,
            "flow_states_changed": self.flow_states_changed,
            "total_changes": self.total_changes,
            "summary": self.summary,
        }


@dataclass
class TimelineQuery:
    """Query parameters for timeline search."""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    event_types: Set[TimelineEventType] = field(default_factory=set)
    severities: Set[Severity] = field(default_factory=set)
    entity_ids: Set[str] = field(default_factory=set)
    source_engines: Set[str] = field(default_factory=set)
    search_text: Optional[str] = None
    limit: int = 100
    
    def to_dict(self) -> Dict:
        return {
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "event_types": [e.value for e in self.event_types],
            "severities": [s.value for s in self.severities],
            "entity_ids": list(self.entity_ids),
            "source_engines": list(self.source_engines),
            "search_text": self.search_text,
            "limit": self.limit,
        }


@dataclass
class Timeline:
    """
    Complete operational timeline.
    
    Contains all events and snapshots for a period.
    """
    timeline_id: str
    name: str
    description: str
    start_time: datetime
    end_time: Optional[datetime]
    
    events: List[TimelineEvent] = field(default_factory=list)
    snapshots: List[TimelineSnapshot] = field(default_factory=list)
    segments: List[TimelineSegment] = field(default_factory=list)
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "timeline_id": self.timeline_id,
            "name": self.name,
            "description": self.description,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "event_count": len(self.events),
            "snapshot_count": len(self.snapshots),
            "segment_count": len(self.segments),
            "metadata": self.metadata,
            "tags": self.tags,
        }
    
    @property
    def duration_seconds(self) -> float:
        """Duration of timeline in seconds."""
        if not self.end_time:
            return 0.0
        return (self.end_time - self.start_time).total_seconds()
    
    @property
    def event_count(self) -> int:
        """Number of events."""
        return len(self.events)
