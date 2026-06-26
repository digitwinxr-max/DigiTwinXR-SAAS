"""Frigate Integration Models

Camera registry, event metadata, retention metadata.
NO object detection, tracking, automation, or AI inference.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class CameraStatus(str, Enum):
    """Camera connection status."""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    UNKNOWN = "unknown"


class RetentionPolicy(str, Enum):
    """Retention policy types."""
    LIVE_ONLY = "live_only"
    HOURS_24 = "24_hours"
    DAYS_3 = "3_days"
    DAYS_7 = "7_days"
    DAYS_14 = "14_days"
    DAYS_30 = "30_days"
    CUSTOM = "custom"


@dataclass
class CameraConfig:
    """Camera configuration metadata."""
    name: str
    host: str
    port: int = 5000
    enabled: bool = True
    width: int = 1920
    height: int = 1080
    fps: int = 30
    codec: str = "h264"
    rtsp_url: Optional[str] = None
    detection_enabled: bool = False
    record_enabled: bool = True


@dataclass
class CameraRegistryEntry:
    """Camera in the registry."""
    id: str
    name: str
    host: str
    port: int
    status: CameraStatus
    enabled: bool
    created_at: datetime
    updated_at: datetime
    config: CameraConfig
    frigate_name: Optional[str] = None
    frigate_id: Optional[str] = None
    location: Optional[str] = None
    zone: Optional[str] = None


@dataclass
class EventMetadata:
    """Event metadata from Frigate."""
    event_id: str
    camera: str
    start_time: datetime
    end_time: Optional[datetime]
    label: Optional[str]
    confidence: Optional[float]
    thumbnail_url: Optional[str]
    clip_url: Optional[str]
    has_clip: bool
    has_snapshot: bool
    studio_created: bool = False


@dataclass
class RetentionMetadata:
    """Retention configuration metadata."""
    camera: str
    policy: RetentionPolicy
    days: int
    max_storage_gb: Optional[float]
    current_storage_gb: float
    recordings_count: int
    oldest_recording: Optional[datetime]
    newest_recording: Optional[datetime]


@dataclass
class FrigateHealthStatus:
    """Frigate service health status."""
    service: str
    status: str
    version: Optional[str]
    cpu_percent: Optional[float]
    memory_percent: Optional[float]
    gpu_enabled: bool
    gpu_temp: Optional[float]
    last_check: datetime


class FrigateRegistry:
    """
    Camera registry and metadata management.
    
    ALLOWED:
    - Camera registration
    - Event metadata storage
    - Retention metadata
    - Health checks
    
    FORBIDDEN:
    - Object detection
    - Tracking
    - Automation
    - Workflow execution
    """
    
    def __init__(self):
        self._cameras: Dict[str, CameraRegistryEntry] = {}
        self._events: Dict[str, EventMetadata] = {}
        self._retention: Dict[str, RetentionMetadata] = {}
    
    def register_camera(self, entry: CameraRegistryEntry) -> CameraRegistryEntry:
        """Register a camera."""
        self._cameras[entry.id] = entry
        return entry
    
    def get_camera(self, camera_id: str) -> Optional[CameraRegistryEntry]:
        """Get camera by ID."""
        return self._cameras.get(camera_id)
    
    def list_cameras(self, enabled_only: bool = False) -> List[CameraRegistryEntry]:
        """List all cameras."""
        cameras = list(self._cameras.values())
        if enabled_only:
            cameras = [c for c in cameras if c.enabled]
        return cameras
    
    def update_camera_status(self, camera_id: str, status: CameraStatus) -> bool:
        """Update camera status."""
        if camera_id in self._cameras:
            self._cameras[camera_id].status = status
            self._cameras[camera_id].updated_at = datetime.now()
            return True
        return False
    
    def add_event(self, event: EventMetadata) -> EventMetadata:
        """Add event metadata."""
        self._events[event.event_id] = event
        return event
    
    def get_event(self, event_id: str) -> Optional[EventMetadata]:
        """Get event by ID."""
        return self._events.get(event_id)
    
    def list_events(
        self,
        camera: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[EventMetadata]:
        """List events with filters."""
        events = list(self._events.values())
        
        if camera:
            events = [e for e in events if e.camera == camera]
        if start_time:
            events = [e for e in events if e.start_time >= start_time]
        if end_time:
            events = [e for e in events if e.start_time <= end_time]
        
        return sorted(events, key=lambda e: e.start_time, reverse=True)
    
    def set_retention(self, retention: RetentionMetadata) -> RetentionMetadata:
        """Set retention metadata."""
        self._retention[retention.camera] = retention
        return retention
    
    def get_retention(self, camera: str) -> Optional[RetentionMetadata]:
        """Get retention metadata."""
        return self._retention.get(camera)
    
    def list_retention(self) -> List[RetentionMetadata]:
        """List all retention metadata."""
        return list(self._retention.values())
    
    def delete_camera(self, camera_id: str) -> bool:
        """Delete a camera."""
        if camera_id in self._cameras:
            del self._cameras[camera_id]
            return True
        return False


# Singleton instance
_registry: Optional[FrigateRegistry] = None


def get_frigate_registry() -> FrigateRegistry:
    """Get or create Frigate registry singleton."""
    global _registry
    if _registry is None:
        _registry = FrigateRegistry()
    return _registry
