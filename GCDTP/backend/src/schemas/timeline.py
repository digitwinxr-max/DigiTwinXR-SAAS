"""
Timeline Schemas

Pydantic schemas for timeline replay API.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# Snapshot Schemas
class TimelineSnapshotBase(BaseModel):
    """Base timeline snapshot schema."""
    timestamp: datetime
    snapshot_type: str
    entity_type: str
    entity_id: str


class TimelineSnapshotCreate(TimelineSnapshotBase):
    """Schema for creating a timeline snapshot."""
    snapshot_data: Dict[str, Any]


class TimelineSnapshotResponse(TimelineSnapshotBase):
    """Schema for timeline snapshot response."""
    id: str
    snapshot_data: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


# Frame Schemas
class TimelineFrameEvent(BaseModel):
    """Event within a timeline frame."""
    event_id: str
    event_type: str
    message: str
    severity: Optional[str] = None
    asset_id: Optional[str] = None
    timestamp: datetime


class TimelineFrameState(BaseModel):
    """State within a timeline frame."""
    entity_type: str
    entity_id: str
    state_data: Dict[str, Any]


class TimelineFrame(BaseModel):
    """Schema for a timeline frame."""
    timestamp: datetime
    events: List[TimelineFrameEvent] = []
    states: Dict[str, Dict[str, Any]] = {}


# Playback Schemas
class TimelinePlaybackRequest(BaseModel):
    """Schema for timeline playback request."""
    start_time: datetime
    end_time: datetime
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    snapshot_types: Optional[List[str]] = None
    frame_interval: int = Field(default=60, ge=1, le=3600)  # seconds


class TimelinePlaybackResponse(BaseModel):
    """Schema for timeline playback response."""
    start_time: datetime
    end_time: datetime
    total_frames: int
    frames: List[TimelineFrame]


# Range Schemas
class TimelineRangeResponse(BaseModel):
    """Schema for timeline range query response."""
    start_time: datetime
    end_time: datetime
    total_snapshots: int
    snapshots: List[TimelineSnapshotResponse]


# System State Schemas
class SystemStateSnapshot(BaseModel):
    """Schema for system state snapshot."""
    timestamp: datetime
    total_assets: int
    total_sensors: int
    total_events: int
    healthy_assets: int
    degraded_assets: int
    critical_assets: int
    snapshot_data: Dict[str, Any]


class SystemTimelineResponse(BaseModel):
    """Schema for system timeline response."""
    snapshots: List[SystemStateSnapshot]
    time_range: Dict[str, datetime]


# Asset Timeline Schemas
class AssetStateChange(BaseModel):
    """Schema for asset state change."""
    timestamp: datetime
    change_type: str
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Dict[str, Any]


class AssetTimelineResponse(BaseModel):
    """Schema for asset timeline response."""
    asset_id: str
    state_changes: List[AssetStateChange]
    current_state: Dict[str, Any]


# Event Timeline Schemas
class EventTimelineEntry(BaseModel):
    """Schema for event timeline entry."""
    event_id: str
    timestamp: datetime
    message: str
    severity: str
    asset_id: Optional[str] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class EventTimelineResponse(BaseModel):
    """Schema for event timeline response."""
    events: List[EventTimelineEntry]
    total_events: int
    time_range: Dict[str, datetime]


# Snapshot Query Schemas
class SnapshotQuery(BaseModel):
    """Schema for snapshot query parameters."""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    snapshot_type: Optional[str] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
