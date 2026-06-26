"""
Timeline Snapshot Model

Represents immutable timeline snapshots for replay capabilities.
Timeline Replay is read-only and reconstructs historical states.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass, field, asdict
import json


class SnapshotType(str, Enum):
    """Types of timeline snapshots."""
    ASSET_STATE = "asset_state"
    HEALTH_STATE = "health_state"
    EVENT_STATE = "event_state"
    MEASUREMENT_STATE = "measurement_state"
    SYSTEM_STATE = "system_state"


@dataclass
class TimelineSnapshot:
    """
    Immutable timeline snapshot.
    
    This model represents a point-in-time capture of system state.
    Snapshots are read-only and cannot be modified.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    snapshot_type: SnapshotType = SnapshotType.SYSTEM_STATE
    entity_type: str = ""
    entity_id: str = ""
    snapshot_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def serialize(self) -> Dict[str, Any]:
        """
        Serialize snapshot to dictionary.
        
        Returns:
            Dictionary representation of the snapshot.
        """
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "snapshot_type": self.snapshot_type.value if isinstance(self.snapshot_type, Enum) else self.snapshot_type,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "snapshot_data": self.snapshot_data,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    def to_json(self) -> str:
        """
        Serialize snapshot to JSON string.
        
        Returns:
            JSON string representation.
        """
        return json.dumps(self.serialize())
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "TimelineSnapshot":
        """
        Deserialize snapshot from dictionary.
        
        Args:
            data: Dictionary containing snapshot data.
            
        Returns:
            TimelineSnapshot instance.
        """
        # Parse timestamp
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        
        # Parse snapshot_type
        snapshot_type = data.get("snapshot_type")
        if isinstance(snapshot_type, str):
            snapshot_type = SnapshotType(snapshot_type)
        
        # Parse created_at
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            timestamp=timestamp or datetime.utcnow(),
            snapshot_type=snapshot_type or SnapshotType.SYSTEM_STATE,
            entity_type=data.get("entity_type", ""),
            entity_id=data.get("entity_id", ""),
            snapshot_data=data.get("snapshot_data", {}),
            created_at=created_at or datetime.utcnow()
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "TimelineSnapshot":
        """
        Deserialize snapshot from JSON string.
        
        Args:
            json_str: JSON string containing snapshot data.
            
        Returns:
            TimelineSnapshot instance.
        """
        data = json.loads(json_str)
        return cls.deserialize(data)
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """
        Get data from snapshot_data.
        
        Args:
            key: Key to retrieve.
            default: Default value if key not found.
            
        Returns:
            Value from snapshot_data or default.
        """
        return self.snapshot_data.get(key, default)


class TimelineFrame:
    """
    Represents a single frame in timeline playback.
    
    A frame contains all state changes at a specific point in time.
    """
    
    def __init__(self, timestamp: datetime, events: list = None, states: dict = None):
        self.timestamp = timestamp
        self.events = events or []
        self.states = states or {}
    
    def add_event(self, event: Dict[str, Any]) -> None:
        """Add an event to this frame."""
        self.events.append(event)
    
    def add_state(self, entity_type: str, entity_id: str, state: Dict[str, Any]) -> None:
        """Add a state to this frame."""
        if entity_type not in self.states:
            self.states[entity_type] = {}
        self.states[entity_type][entity_id] = state
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert frame to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "events": self.events,
            "states": self.states
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TimelineFrame":
        """Create frame from dictionary."""
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        
        return cls(
            timestamp=timestamp,
            events=data.get("events", []),
            states=data.get("states", {})
        )
