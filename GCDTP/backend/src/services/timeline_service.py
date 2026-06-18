"""
Timeline Service

Provides temporal replay capabilities.
This engine reconstructs historical states from existing records.
Timeline Replay is read-only and immutable.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from ..models.timeline_snapshot import TimelineSnapshot, SnapshotType, TimelineFrame
from ..schemas.timeline import (
    TimelineSnapshotCreate,
    TimelinePlaybackRequest,
    TimelineFrameEvent,
)


class TimelineService:
    """
    Service for timeline replay operations.
    
    This service provides:
    - Snapshot capture (from existing records)
    - Historical state reconstruction
    - Playback capabilities
    - Range queries
    
    NO writes to live tables.
    Snapshots are immutable.
    NO AI, NO prediction, NO analytics.
    """
    
    def __init__(self):
        # In-memory snapshot storage
        self._snapshots: Dict[str, TimelineSnapshot] = {}
        # Index by timestamp
        self._snapshots_by_time: Dict[datetime, List[str]] = defaultdict(list)
        # Index by entity
        self._snapshots_by_entity: Dict[Tuple[str, str], List[str]] = defaultdict(list)
    
    def capture_snapshot(
        self,
        snapshot_type: str,
        entity_type: str,
        entity_id: str,
        snapshot_data: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ) -> TimelineSnapshot:
        """
        Capture a snapshot from existing records.
        
        This method ONLY captures data from existing models.
        It does NOT write to live tables.
        
        Args:
            snapshot_type: Type of snapshot (asset, health, event, measurement, system)
            entity_type: Type of entity
            entity_id: ID of entity
            snapshot_data: Data to capture
            timestamp: Optional timestamp (defaults to now)
            
        Returns:
            Created TimelineSnapshot
        """
        snapshot = TimelineSnapshot(
            snapshot_type=SnapshotType(snapshot_type),
            entity_type=entity_type,
            entity_id=entity_id,
            snapshot_data=snapshot_data,
            timestamp=timestamp or datetime.utcnow()
        )
        
        self._snapshots[snapshot.id] = snapshot
        
        # Update indexes
        self._snapshots_by_time[snapshot.timestamp].append(snapshot.id)
        self._snapshots_by_entity[(entity_type, entity_id)].append(snapshot.id)
        
        return snapshot
    
    def get_snapshot(self, snapshot_id: str) -> Optional[TimelineSnapshot]:
        """Get a snapshot by ID."""
        return self._snapshots.get(snapshot_id)
    
    def get_range(
        self,
        start_time: datetime,
        end_time: datetime,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        snapshot_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[TimelineSnapshot]:
        """
        Get snapshots within a time range.
        
        Args:
            start_time: Start of range
            end_time: End of range
            entity_type: Optional entity type filter
            entity_id: Optional entity ID filter
            snapshot_type: Optional snapshot type filter
            limit: Max results
            offset: Result offset
            
        Returns:
            List of snapshots in range
        """
        results = []
        
        for snapshot in self._snapshots.values():
            # Check time range
            if snapshot.timestamp < start_time or snapshot.timestamp > end_time:
                continue
            
            # Check entity filters
            if entity_type and snapshot.entity_type != entity_type:
                continue
            if entity_id and snapshot.entity_id != entity_id:
                continue
            
            # Check snapshot type
            if snapshot_type and snapshot.snapshot_type.value != snapshot_type:
                continue
            
            results.append(snapshot)
        
        # Sort by timestamp
        results.sort(key=lambda s: s.timestamp)
        
        # Apply pagination
        return results[offset:offset + limit]
    
    def build_frame(
        self,
        timestamp: datetime,
        window_seconds: int = 60
    ) -> TimelineFrame:
        """
        Build a timeline frame at a specific timestamp.
        
        Args:
            timestamp: Target timestamp
            window_seconds: Time window for events
            
        Returns:
            TimelineFrame with events and states
        """
        frame = TimelineFrame(timestamp=timestamp)
        
        # Find snapshots within window
        window_start = timestamp - timedelta(seconds=window_seconds)
        window_end = timestamp + timedelta(seconds=window_seconds)
        
        events = []
        states = {}
        
        for snapshot in self._snapshots.values():
            if snapshot.timestamp < window_start or snapshot.timestamp > window_end:
                continue
            
            # Add to frame states (most recent first)
            key = (snapshot.entity_type, snapshot.entity_id)
            if key not in states or snapshot.timestamp > states[key]["timestamp"]:
                states[key] = {
                    "timestamp": snapshot.timestamp,
                    "data": snapshot.snapshot_data
                }
            
            # Track events
            if snapshot.snapshot_type == SnapshotType.EVENT_STATE:
                events.append({
                    "event_id": snapshot.entity_id,
                    "event_type": snapshot.entity_type,
                    "message": snapshot.snapshot_data.get("message", ""),
                    "severity": snapshot.snapshot_data.get("severity"),
                    "timestamp": snapshot.timestamp
                })
        
        # Build frame
        for key, state in states.items():
            frame.add_state(key[0], key[1], state["data"])
        
        for event in sorted(events, key=lambda e: e["timestamp"]):
            frame.add_event(event)
        
        return frame
    
    def playback(
        self,
        start_time: datetime,
        end_time: datetime,
        frame_interval: int = 60,
        entity_id: Optional[str] = None,
        entity_type: Optional[str] = None
    ) -> List[TimelineFrame]:
        """
        Generate playback frames for a time range.
        
        Args:
            start_time: Playback start
            end_time: Playback end
            frame_interval: Seconds between frames
            entity_id: Optional entity filter
            entity_type: Optional entity type filter
            
        Returns:
            List of timeline frames
        """
        frames = []
        current_time = start_time
        
        while current_time <= end_time:
            frame = self.build_frame(current_time)
            
            # Filter frames by entity if specified
            if entity_id or entity_type:
                filtered_events = []
                filtered_states = {}
                
                for event in frame.events:
                    if entity_id and event.get("asset_id") != entity_id:
                        continue
                    filtered_events.append(event)
                
                for etype, eid_states in frame.states.items():
                    for eid, state in eid_states.items():
                        if entity_id and eid != entity_id:
                            continue
                        if entity_type and etype != entity_type:
                            continue
                        filtered_states[etype] = {eid: state}
                
                frame.events = filtered_events
                frame.states = filtered_states
            
            frames.append(frame)
            current_time += timedelta(seconds=frame_interval)
        
        return frames
    
    def reconstruct_asset_state(
        self,
        asset_id: str,
        timestamp: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Reconstruct asset state at a specific time.
        
        NO writes to live tables.
        
        Args:
            asset_id: Asset ID
            timestamp: Target time (defaults to now)
            
        Returns:
            Asset state at time
        """
        target_time = timestamp or datetime.utcnow()
        
        snapshots = self.get_range(
            start_time=datetime.min,
            end_time=target_time,
            entity_type="asset",
            entity_id=asset_id,
            limit=1
        )
        
        # Sort by timestamp descending and get most recent
        snapshots.sort(key=lambda s: s.timestamp, reverse=True)
        
        if snapshots:
            return snapshots[0].snapshot_data
        return None
    
    def reconstruct_health_state(
        self,
        asset_id: str,
        timestamp: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Reconstruct health state at a specific time.
        
        Args:
            asset_id: Asset ID
            timestamp: Target time
            
        Returns:
            Health state at time
        """
        target_time = timestamp or datetime.utcnow()
        
        snapshots = self.get_range(
            start_time=datetime.min,
            end_time=target_time,
            entity_type="health",
            entity_id=asset_id,
            limit=1
        )
        
        snapshots.sort(key=lambda s: s.timestamp, reverse=True)
        
        if snapshots:
            return snapshots[0].snapshot_data
        return None
    
    def reconstruct_event_state(
        self,
        event_id: str,
        timestamp: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Reconstruct event state at a specific time.
        
        Args:
            event_id: Event ID
            timestamp: Target time
            
        Returns:
            Event state at time
        """
        target_time = timestamp or datetime.utcnow()
        
        snapshots = self.get_range(
            start_time=datetime.min,
            end_time=target_time,
            entity_type="event",
            entity_id=event_id,
            limit=1
        )
        
        snapshots.sort(key=lambda s: s.timestamp, reverse=True)
        
        if snapshots:
            return snapshots[0].snapshot_data
        return None
    
    def reconstruct_system_state(
        self,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Reconstruct full system state at a specific time.
        
        Combines all entity states at the given time.
        
        Args:
            timestamp: Target time
            
        Returns:
            System state snapshot
        """
        target_time = timestamp or datetime.utcnow()
        
        # Get all snapshots up to target time
        snapshots = self.get_range(
            start_time=datetime.min,
            end_time=target_time,
            limit=10000
        )
        
        # Build system state
        system_state = {
            "timestamp": target_time,
            "assets": {},
            "sensors": {},
            "events": {},
            "health": {},
            "measurements": {}
        }
        
        for snapshot in snapshots:
            stype = snapshot.snapshot_type.value
            eid = snapshot.entity_id
            
            if stype == SnapshotType.ASSET_STATE.value:
                system_state["assets"][eid] = snapshot.snapshot_data
            elif stype == SnapshotType.HEALTH_STATE.value:
                system_state["health"][eid] = snapshot.snapshot_data
            elif stype == SnapshotType.EVENT_STATE.value:
                system_state["events"][eid] = snapshot.snapshot_data
            elif stype == SnapshotType.MEASUREMENT_STATE.value:
                system_state["measurements"][eid] = snapshot.snapshot_data
        
        return system_state
    
    def generate_system_snapshot(
        self,
        timestamp: Optional[datetime] = None,
        asset_count: int = 0,
        sensor_count: int = 0,
        event_count: int = 0,
        healthy_count: int = 0,
        degraded_count: int = 0,
        critical_count: int = 0
    ) -> TimelineSnapshot:
        """
        Generate a system-wide snapshot.
        
        This captures the overall system state at a point in time.
        
        Args:
            timestamp: Snapshot time
            asset_count: Total assets
            sensor_count: Total sensors
            event_count: Active events
            healthy_count: Healthy assets
            degraded_count: Degraded assets
            critical_count: Critical assets
            
        Returns:
            System state snapshot
        """
        snapshot_data = {
            "total_assets": asset_count,
            "total_sensors": sensor_count,
            "total_events": event_count,
            "healthy_assets": healthy_count,
            "degraded_assets": degraded_count,
            "critical_assets": critical_count,
            "health_distribution": {
                "healthy": healthy_count,
                "degraded": degraded_count,
                "critical": critical_count
            }
        }
        
        return self.capture_snapshot(
            snapshot_type=SnapshotType.SYSTEM_STATE.value,
            entity_type="system",
            entity_id="system",
            snapshot_data=snapshot_data,
            timestamp=timestamp
        )


# Global instance
timeline_service = TimelineService()
