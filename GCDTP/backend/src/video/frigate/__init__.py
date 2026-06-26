"""Frigate Integration Layer"""
from .models import (
    CameraStatus,
    RetentionPolicy,
    CameraConfig,
    CameraRegistryEntry,
    EventMetadata,
    RetentionMetadata,
    FrigateHealthStatus,
    FrigateRegistry,
    get_frigate_registry,
)
from .service import FrigateService, get_frigate_service
from .routes import router as frigate_router

__all__ = [
    "CameraStatus",
    "RetentionPolicy",
    "CameraConfig",
    "CameraRegistryEntry",
    "EventMetadata",
    "RetentionMetadata",
    "FrigateHealthStatus",
    "FrigateRegistry",
    "get_frigate_registry",
    "FrigateService",
    "get_frigate_service",
    "frigate_router",
]
