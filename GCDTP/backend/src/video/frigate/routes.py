"""Frigate Routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from .service import FrigateService, get_frigate_service
from .models import CameraStatus, RetentionPolicy

router = APIRouter(prefix="/frigate", tags=["frigate"])


class CameraCreate(BaseModel):
    id: str
    name: str
    host: str
    port: int = 5000
    enabled: bool = True
    frigate_name: Optional[str] = None


class HealthResponse(BaseModel):
    service: str
    status: str
    version: Optional[str]
    gpu_enabled: bool


@router.get("/health", response_model=HealthResponse)
async def get_health():
    """Get Frigate service health."""
    service = get_frigate_service()
    health = await service.health_check()
    return HealthResponse(
        service=health.service,
        status=health.status,
        version=health.version,
        gpu_enabled=health.gpu_enabled
    )


@router.get("/cameras")
async def list_cameras(enabled_only: bool = False):
    """List registered cameras."""
    service = get_frigate_service()
    cameras = service.registry.list_cameras(enabled_only)
    return {
        "cameras": [
            {
                "id": c.id,
                "name": c.name,
                "status": c.status.value,
                "enabled": c.enabled,
                "host": c.host,
                "port": c.port
            }
            for c in cameras
        ]
    }


@router.post("/cameras")
async def register_camera(request: CameraCreate):
    """Register a camera."""
    from .models import CameraRegistryEntry, CameraConfig
    
    service = get_frigate_service()
    config = CameraConfig(name=request.name, host=request.host, port=request.port, enabled=request.enabled)
    entry = CameraRegistryEntry(
        id=request.id,
        name=request.name,
        host=request.host,
        port=request.port,
        status=CameraStatus.UNKNOWN,
        enabled=request.enabled,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        config=config,
        frigate_name=request.frigate_name
    )
    service.registry.register_camera(entry)
    return {"id": entry.id, "name": entry.name}


@router.post("/cameras/sync")
async def sync_cameras():
    """Sync cameras from Frigate."""
    service = get_frigate_service()
    cameras = await service.sync_cameras()
    return {"synced": len(cameras), "cameras": [c.name for c in cameras]}


@router.get("/events")
async def list_events(
    camera: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
):
    """List events from registry."""
    service = get_frigate_service()
    events = service.registry.list_events(camera, start_time, end_time)
    return {
        "events": [
            {
                "event_id": e.event_id,
                "camera": e.camera,
                "start_time": e.start_time.isoformat(),
                "end_time": e.end_time.isoformat() if e.end_time else None,
                "label": e.label,
                "has_clip": e.has_clip
            }
            for e in events
        ]
    }


@router.get("/retention")
async def list_retention():
    """List retention configuration."""
    service = get_frigate_service()
    retention = service.registry.list_retention()
    return {
        "retention": [
            {
                "camera": r.camera,
                "policy": r.policy.value,
                "days": r.days
            }
            for r in retention
        ]
    }
