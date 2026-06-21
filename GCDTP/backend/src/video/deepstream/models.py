"""
DeepStream GPU Analytics Models

GPU pipeline metadata.
NO autonomous analytics or execution.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class GPUStatus(str, Enum):
    """GPU availability status."""
    AVAILABLE = "available"
    IN_USE = "in_use"
    UNAVAILABLE = "unavailable"
    ERROR = "error"


class PipelineType(str, Enum):
    """DeepStream pipeline types."""
    DETECTION = "detection"
    CLASSIFICATION = "classification"
    TRACKING = "tracking"
    ANALYTICS = "analytics"
    STREAMING = "streaming"


class PipelineStatus(str, Enum):
    """Pipeline status."""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class GPUInventoryEntry:
    """GPU inventory entry."""
    gpu_id: str
    name: str
    compute_capability: str
    memory_total_mb: int
    memory_available_mb: int
    status: GPUStatus
    utilization_percent: float
    temperature_celsius: Optional[float]
    power_usage_watts: Optional[float]


@dataclass
class StreamMetadata:
    """Video stream metadata."""
    stream_id: str
    uri: str
    codec: str
    resolution: str
    fps: float
    bitrate: Optional[int]
    latency_ms: Optional[float]


@dataclass
class PipelineMetadata:
    """DeepStream pipeline metadata."""
    pipeline_id: str
    name: str
    pipeline_type: PipelineType
    status: PipelineStatus
    gpu_id: Optional[str]
    streams: List[StreamMetadata]
    config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass
class AnalyticsMetadata:
    """Analytics metadata from pipeline."""
    analytics_id: str
    pipeline_id: str
    timestamp: datetime
    events: List[Dict[str, Any]]
    metrics: Dict[str, float]
    requires_review: bool = True


class DeepStreamRegistry:
    """
    DeepStream GPU registry.
    
    ALLOWED:
    - GPU inventory
    - Pipeline registry
    - Stream metadata
    - Analytics metadata
    
    FORBIDDEN:
    - Autonomous analytics
    - Execution
    """
    
    def __init__(self):
        self._gpus: Dict[str, GPUInventoryEntry] = {}
        self._pipelines: Dict[str, PipelineMetadata] = {}
        self._analytics: Dict[str, AnalyticsMetadata] = {}
    
    def register_gpu(self, gpu: GPUInventoryEntry) -> GPUInventoryEntry:
        """Register a GPU."""
        self._gpus[gpu.gpu_id] = gpu
        return gpu
    
    def get_gpu(self, gpu_id: str) -> Optional[GPUInventoryEntry]:
        """Get GPU by ID."""
        return self._gpus.get(gpu_id)
    
    def list_gpus(self) -> List[GPUInventoryEntry]:
        """List all GPUs."""
        return list(self._gpus.values())
    
    def register_pipeline(self, pipeline: PipelineMetadata) -> PipelineMetadata:
        """Register a pipeline."""
        self._pipelines[pipeline.pipeline_id] = pipeline
        return pipeline
    
    def get_pipeline(self, pipeline_id: str) -> Optional[PipelineMetadata]:
        """Get pipeline by ID."""
        return self._pipelines.get(pipeline_id)
    
    def list_pipelines(
        self,
        pipeline_type: Optional[PipelineType] = None,
        status: Optional[PipelineStatus] = None
    ) -> List[PipelineMetadata]:
        """List pipelines with filters."""
        pipelines = list(self._pipelines.values())
        
        if pipeline_type:
            pipelines = [p for p in pipelines if p.pipeline_type == pipeline_type]
        if status:
            pipelines = [p for p in pipelines if p.status == status]
        
        return pipelines
    
    def add_analytics(self, analytics: AnalyticsMetadata) -> AnalyticsMetadata:
        """Add analytics metadata."""
        self._analytics[analytics.analytics_id] = analytics
        return analytics
    
    def list_analytics(
        self,
        pipeline_id: Optional[str] = None,
        requires_review: Optional[bool] = None
    ) -> List[AnalyticsMetadata]:
        """List analytics with filters."""
        analytics = list(self._analytics.values())
        
        if pipeline_id:
            analytics = [a for a in analytics if a.pipeline_id == pipeline_id]
        if requires_review is not None:
            analytics = [a for a in analytics if a.requires_review == requires_review]
        
        return analytics
    
    def delete_pipeline(self, pipeline_id: str) -> bool:
        """Delete a pipeline."""
        if pipeline_id in self._pipelines:
            del self._pipelines[pipeline_id]
            return True
        return False


# Singleton instance
_registry: Optional[DeepStreamRegistry] = None


def get_deepstream_registry() -> DeepStreamRegistry:
    """Get or create DeepStream registry singleton."""
    global _registry
    if _registry is None:
        _registry = DeepStreamRegistry()
    return _registry
