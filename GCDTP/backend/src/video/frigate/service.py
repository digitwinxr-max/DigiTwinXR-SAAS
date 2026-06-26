"""
Frigate Service

Service layer for Frigate integration.
NO object detection, tracking, automation, or AI inference.
"""

import httpx
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .models import (
    FrigateRegistry,
    get_frigate_registry,
    CameraRegistryEntry,
    CameraConfig,
    CameraStatus,
    EventMetadata,
    RetentionMetadata,
    RetentionPolicy,
    FrigateHealthStatus,
)


logger = logging.getLogger(__name__)


class FrigateService:
    """
    Frigate service client.
    
    Features:
    - Camera registry management
    - Event metadata retrieval
    - Retention configuration
    - Health checks
    
    LIMITATIONS:
    - NO object detection
    - NO tracking
    - NO automation
    - NO workflow execution
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:5000",
        api_key: Optional[str] = None,
        registry: Optional[FrigateRegistry] = None
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.registry = registry or get_frigate_registry()
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=30.0
            )
        return self._client
    
    async def close(self):
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    async def health_check(self) -> FrigateHealthStatus:
        """
        Check Frigate service health.
        
        Returns:
            FrigateHealthStatus with service health info
        """
        try:
            client = await self._get_client()
            response = await client.get("/api/stats")
            
            if response.status_code == 200:
                data = response.json()
                service_config = data.get("service", {})
                
                return FrigateHealthStatus(
                    service="frigate",
                    status="healthy",
                    version=service_config.get("version"),
                    cpu_percent=service_config.get("cpu_usages", {}).get("cpu0", {}).get("cpu", 0),
                    memory_percent=service_config.get("memory", {}).get("percent"),
                    gpu_enabled=data.get("gpu_usages") is not None,
                    gpu_temp=None,
                    last_check=datetime.now()
                )
            else:
                return FrigateHealthStatus(
                    service="frigate",
                    status="unavailable",
                    version=None,
                    cpu_percent=None,
                    memory_percent=None,
                    gpu_enabled=False,
                    gpu_temp=None,
                    last_check=datetime.now()
                )
                
        except Exception as e:
            logger.error(f"Frigate health check failed: {e}")
            return FrigateHealthStatus(
                service="frigate",
                status="error",
                version=None,
                cpu_percent=None,
                memory_percent=None,
                gpu_enabled=False,
                gpu_temp=None,
                last_check=datetime.now()
            )
    
    async def get_cameras(self) -> List[Dict[str, Any]]:
        """
        Get cameras from Frigate API.
        
        Returns:
            List of camera configurations
        """
        try:
            client = await self._get_client()
            response = await client.get("/api/config")
            
            if response.status_code == 200:
                config = response.json()
                return config.get("cameras", {})
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get cameras: {e}")
            return {}
    
    async def sync_cameras(self) -> List[CameraRegistryEntry]:
        """
        Sync cameras from Frigate to local registry.
        
        Returns:
            List of synced cameras
        """
        cameras = await self.get_cameras()
        synced = []
        
        for name, config in cameras.items():
            camera_config = CameraConfig(
                name=name,
                host=self.base_url,
                port=5000,
                enabled=config.get("enabled", True),
                width=config.get("width", 1920),
                height=config.get("height", 1080),
                fps=config.get("fps", 30),
                detection_enabled=config.get("detect", {}).get("enabled", False),
                record_enabled=config.get("record", {}).get("enabled", True)
            )
            
            entry = CameraRegistryEntry(
                id=f"frigate_{name}",
                name=name,
                host=self.base_url,
                port=5000,
                status=CameraStatus.UNKNOWN,
                enabled=camera_config.enabled,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                config=camera_config,
                frigate_name=name
            )
            
            self.registry.register_camera(entry)
            synced.append(entry)
        
        return synced
    
    async def get_events(
        self,
        camera: Optional[str] = None,
        limit: int = 100
    ) -> List[EventMetadata]:
        """
        Get events from Frigate API.
        
        Args:
            camera: Filter by camera name
            limit: Maximum number of events
        
        Returns:
            List of event metadata
        """
        try:
            client = await self._get_client()
            params = {"limit": limit}
            if camera:
                params["camera"] = camera
            
            response = await client.get("/api/events", params=params)
            
            if response.status_code == 200:
                events = response.json()
                result = []
                
                for event in events:
                    metadata = EventMetadata(
                        event_id=str(event.get("id")),
                        camera=event.get("camera", ""),
                        start_time=datetime.fromisoformat(event.get("start_time", "").replace("Z", "+00:00")),
                        end_time=datetime.fromisoformat(event["end_time"].replace("Z", "+00:00")) if event.get("end_time") else None,
                        label=event.get("label"),
                        confidence=event.get("confidence"),
                        thumbnail_url=f"/api/events/{event.get('id')}/thumbnail",
                        clip_url=f"/api/events/{event.get('id')}/clip" if event.get("has_clip") else None,
                        has_clip=event.get("has_clip", False),
                        has_snapshot=event.get("has_snapshot", False)
                    )
                    self.registry.add_event(metadata)
                    result.append(metadata)
                
                return result
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get events: {e}")
            return []
    
    async def get_retention_config(self) -> Dict[str, RetentionMetadata]:
        """
        Get retention configuration from Frigate.
        
        Returns:
            Dictionary of retention metadata by camera
        """
        try:
            client = await self._get_client()
            response = await client.get("/api/config")
            
            if response.status_code == 200:
                config = response.json()
                retention_data = {}
                
                for camera_name, camera_config in config.get("cameras", {}).items():
                    record_config = camera_config.get("record", {})
                    
                    if record_config.get("enabled"):
                        retain = record_config.get("retain", {})
                        days = retain.get("days", 7)
                        
                        retention = RetentionMetadata(
                            camera=camera_name,
                            policy=RetentionPolicy.DAYS_7 if days == 7 else RetentionPolicy.CUSTOM,
                            days=days,
                            max_storage_gb=None,
                            current_storage_gb=0.0,
                            recordings_count=0,
                            oldest_recording=None,
                            newest_recording=None
                        )
                        
                        self.registry.set_retention(retention)
                        retention_data[camera_name] = retention
                
                return retention_data
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get retention config: {e}")
            return {}


# Singleton instance
_service: Optional[FrigateService] = None


def get_frigate_service() -> FrigateService:
    """Get or create Frigate service singleton."""
    global _service
    if _service is None:
        _service = FrigateService()
    return _service
