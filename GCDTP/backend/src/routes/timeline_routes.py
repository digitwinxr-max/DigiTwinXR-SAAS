"""
Timeline Routes

FastAPI routes for timeline replay API.
"""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query

from ..schemas.timeline import (
    TimelineSnapshotCreate,
    TimelineSnapshotResponse,
    TimelinePlaybackRequest,
    TimelinePlaybackResponse,
    TimelineRangeResponse,
    SystemTimelineResponse,
    SystemStateSnapshot,
    AssetTimelineResponse,
    AssetStateChange,
    EventTimelineResponse,
    EventTimelineEntry,
)
from ..services.timeline_service import timeline_service


router = APIRouter(prefix="/timeline", tags=["timeline"])


# Snapshot Routes
@router.post("/snapshot", response_model=TimelineSnapshotResponse)
async def create_snapshot(data: TimelineSnapshotCreate):
    """
    Create a timeline snapshot from existing records.
    
    This endpoint captures point-in-time state.
    NO writes to live tables.
    """
    snapshot = timeline_service.capture_snapshot(
        snapshot_type=data.snapshot_type,
        entity_type=data.entity_type,
        entity_id=data.entity_id,
        snapshot_data=data.snapshot_data,
        timestamp=data.timestamp
    )
    return snapshot.serialize()


# Frame Routes
@router.get("/frame")
async def get_frame(
    timestamp: datetime = Query(..., description="Target timestamp"),
    window_seconds: int = Query(60, ge=1, le=3600, description="Time window in seconds")
):
    """
    Get a timeline frame at a specific timestamp.
    
    Returns events and states within the time window.
    """
    frame = timeline_service.build_frame(timestamp, window_seconds)
    return frame.to_dict()


# Range Routes
@router.get("/range", response_model=TimelineRangeResponse)
async def get_range(
    start_time: datetime = Query(..., description="Start of range"),
    end_time: datetime = Query(..., description="End of range"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[str] = Query(None, description="Filter by entity ID"),
    snapshot_type: Optional[str] = Query(None, description="Filter by snapshot type"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    Get snapshots within a time range.
    
    Returns paginated list of snapshots.
    """
    snapshots = timeline_service.get_range(
        start_time=start_time,
        end_time=end_time,
        entity_type=entity_type,
        entity_id=entity_id,
        snapshot_type=snapshot_type,
        limit=limit,
        offset=offset
    )
    
    return TimelineRangeResponse(
        start_time=start_time,
        end_time=end_time,
        total_snapshots=len(snapshots),
        snapshots=[s.serialize() for s in snapshots]
    )


# Playback Routes
@router.get("/playback", response_model=TimelinePlaybackResponse)
async def get_playback(
    start_time: datetime = Query(..., description="Playback start time"),
    end_time: datetime = Query(..., description="Playback end time"),
    frame_interval: int = Query(60, ge=1, le=3600, description="Seconds between frames"),
    entity_id: Optional[str] = Query(None, description="Filter by entity ID"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type")
):
    """
    Generate playback frames for a time range.
    
    Returns chronological frames for timeline visualization.
    Timeline Replay is read-only.
    """
    frames = timeline_service.playback(
        start_time=start_time,
        end_time=end_time,
        frame_interval=frame_interval,
        entity_id=entity_id,
        entity_type=entity_type
    )
    
    return TimelinePlaybackResponse(
        start_time=start_time,
        end_time=end_time,
        total_frames=len(frames),
        frames=[f.to_dict() for f in frames]
    )


# System Routes
@router.get("/system", response_model=SystemTimelineResponse)
async def get_system_timeline(
    start_time: Optional[datetime] = Query(None, description="Start of range"),
    end_time: Optional[datetime] = Query(None, description="End of range"),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Get system-wide timeline snapshots.
    
    Returns system state at various points in time.
    """
    # Get all system snapshots
    snapshots = timeline_service.get_range(
        start_time=start_time or datetime.min,
        end_time=end_time or datetime.utcnow(),
        entity_type="system",
        limit=limit
    )
    
    system_snapshots = []
    for s in snapshots:
        data = s.snapshot_data
        system_snapshots.append(SystemStateSnapshot(
            timestamp=s.timestamp,
            total_assets=data.get("total_assets", 0),
            total_sensors=data.get("total_sensors", 0),
            total_events=data.get("total_events", 0),
            healthy_assets=data.get("healthy_assets", 0),
            degraded_assets=data.get("degraded_assets", 0),
            critical_assets=data.get("critical_assets", 0),
            snapshot_data=data
        ))
    
    time_range = {}
    if snapshots:
        time_range["start"] = snapshots[0].timestamp
        time_range["end"] = snapshots[-1].timestamp
    
    return SystemTimelineResponse(
        snapshots=system_snapshots,
        time_range=time_range
    )


# Asset Routes
@router.get("/asset/{asset_id}", response_model=AssetTimelineResponse)
async def get_asset_timeline(
    asset_id: str,
    start_time: Optional[datetime] = Query(None, description="Start of range"),
    end_time: Optional[datetime] = Query(None, description="End of range")
):
    """
    Get timeline for a specific asset.
    
    Returns state changes for the asset over time.
    """
    snapshots = timeline_service.get_range(
        start_time=start_time or datetime.min,
        end_time=end_time or datetime.utcnow(),
        entity_type="asset",
        entity_id=asset_id
    )
    
    state_changes = []
    current_state = None
    
    for snapshot in snapshots:
        change = AssetStateChange(
            timestamp=snapshot.timestamp,
            change_type="update",
            previous_state=current_state,
            new_state=snapshot.snapshot_data
        )
        state_changes.append(change)
        current_state = snapshot.snapshot_data
    
    # Get latest state
    latest_state = timeline_service.reconstruct_asset_state(asset_id)
    
    return AssetTimelineResponse(
        asset_id=asset_id,
        state_changes=state_changes,
        current_state=latest_state or {}
    )


# Event Routes
@router.get("/event/{event_id}", response_model=EventTimelineResponse)
async def get_event_timeline(
    event_id: str,
    start_time: Optional[datetime] = Query(None, description="Start of range"),
    end_time: Optional[datetime] = Query(None, description="End of range")
):
    """
    Get timeline for a specific event.
    
    Returns event history including resolution.
    """
    snapshots = timeline_service.get_range(
        start_time=start_time or datetime.min,
        end_time=end_time or datetime.utcnow(),
        entity_type="event",
        entity_id=event_id
    )
    
    events = []
    for snapshot in snapshots:
        data = snapshot.snapshot_data
        events.append(EventTimelineEntry(
            event_id=event_id,
            timestamp=snapshot.timestamp,
            message=data.get("message", ""),
            severity=data.get("severity", "UNKNOWN"),
            asset_id=data.get("asset_id"),
            resolved=data.get("resolved", False),
            resolved_at=data.get("resolved_at")
        ))
    
    time_range = {}
    if events:
        time_range["start"] = events[0].timestamp
        time_range["end"] = events[-1].timestamp
    
    return EventTimelineResponse(
        events=events,
        total_events=len(events),
        time_range=time_range
    )


# Health Routes
@router.get("/health/{asset_id}")
async def get_health_timeline(
    asset_id: str,
    start_time: Optional[datetime] = Query(None, description="Start of range"),
    end_time: Optional[datetime] = Query(None, description="End of range")
):
    """
    Get health state timeline for an asset.
    
    Returns health changes over time.
    """
    snapshots = timeline_service.get_range(
        start_time=start_time or datetime.min,
        end_time=end_time or datetime.utcnow(),
        entity_type="health",
        entity_id=asset_id
    )
    
    return {
        "asset_id": asset_id,
        "health_changes": [s.serialize() for s in snapshots],
        "current_health": timeline_service.reconstruct_health_state(asset_id)
    }
