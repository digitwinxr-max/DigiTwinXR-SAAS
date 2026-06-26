"""
DeepStream Pipeline Service

GPU pipeline management.
NO autonomous analytics or execution.
"""

import logging
from typing import Dict, List, Optional, Any

from .models import (
    DeepStreamRegistry,
    get_deepstream_registry,
    GPUInventoryEntry,
    GPUStatus,
    PipelineMetadata,
    PipelineType,
    PipelineStatus,
    StreamMetadata,
    AnalyticsMetadata,
)


logger = logging.getLogger(__name__)


class DeepStreamService:
    """
    DeepStream GPU pipeline service.
    
    Features:
    - GPU inventory management
    - Pipeline metadata management
    - Stream metadata
    - Analytics metadata storage
    
    LIMITATIONS:
    - NO autonomous analytics
    - NO execution
    """
    
    def __init__(self, registry: Optional[DeepStreamRegistry] = None):
        self.registry = registry or get_deepstream_registry()
    
    def register_gpu(
        self,
        gpu_id: str,
        name: str,
        compute_capability: str,
        memory_total_mb: int
    ) -> GPUInventoryEntry:
        """
        Register a GPU.
        
        Args:
            gpu_id: GPU identifier
            name: GPU name
            compute_capability: CUDA compute capability
            memory_total_mb: Total memory in MB
        
        Returns:
            GPUInventoryEntry
        """
        gpu = GPUInventoryEntry(
            gpu_id=gpu_id,
            name=name,
            compute_capability=compute_capability,
            memory_total_mb=memory_total_mb,
            memory_available_mb=memory_total_mb,
            status=GPUStatus.AVAILABLE,
            utilization_percent=0.0,
            temperature_celsius=None,
            power_usage_watts=None
        )
        return self.registry.register_gpu(gpu)
    
    def create_pipeline(
        self,
        pipeline_id: str,
        name: str,
        pipeline_type: PipelineType,
        gpu_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Optional[PipelineMetadata]:
        """
        Create a pipeline metadata entry.
        
        Args:
            pipeline_id: Pipeline identifier
            name: Pipeline name
            pipeline_type: Type of pipeline
            gpu_id: GPU to use
            config: Pipeline configuration
        
        Returns:
            PipelineMetadata or None
        """
        # Verify GPU exists if specified
        if gpu_id and not self.registry.get_gpu(gpu_id):
            return None
        
        pipeline = PipelineMetadata(
            pipeline_id=pipeline_id,
            name=name,
            pipeline_type=pipeline_type,
            status=PipelineStatus.STOPPED,
            gpu_id=gpu_id,
            streams=[],
            config=config or {},
            created_at=None,
            updated_at=None
        )
        return self.registry.register_pipeline(pipeline)
    
    def add_stream_to_pipeline(
        self,
        pipeline_id: str,
        stream: StreamMetadata
    ) -> bool:
        """
        Add a stream to a pipeline.
        
        Args:
            pipeline_id: Pipeline ID
            stream: Stream metadata
        
        Returns:
            True if successful
        """
        pipeline = self.registry.get_pipeline(pipeline_id)
        if pipeline:
            pipeline.streams.append(stream)
            return True
        return False
    
    def record_analytics(
        self,
        analytics_id: str,
        pipeline_id: str,
        events: List[Dict[str, Any]],
        metrics: Dict[str, float]
    ) -> AnalyticsMetadata:
        """
        Record analytics metadata.
        
        Args:
            analytics_id: Analytics ID
            pipeline_id: Pipeline ID
            events: List of events
            metrics: Performance metrics
        
        Returns:
            AnalyticsMetadata
        """
        analytics = AnalyticsMetadata(
            analytics_id=analytics_id,
            pipeline_id=pipeline_id,
            timestamp=None,
            events=events,
            metrics=metrics,
            requires_review=True
        )
        return self.registry.add_analytics(analytics)
    
    def get_pipeline_stats(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """
        Get pipeline statistics.
        
        Args:
            pipeline_id: Pipeline ID
        
        Returns:
            Statistics dictionary
        """
        pipeline = self.registry.get_pipeline(pipeline_id)
        if not pipeline:
            return None
        
        analytics = self.registry.list_analytics(pipeline_id=pipeline_id)
        
        return {
            "pipeline_id": pipeline_id,
            "name": pipeline.name,
            "status": pipeline.status.value,
            "gpu_id": pipeline.gpu_id,
            "stream_count": len(pipeline.streams),
            "analytics_count": len(analytics),
            "pending_review": sum(1 for a in analytics if a.requires_review)
        }


# Singleton instance
_service: Optional[DeepStreamService] = None


def get_deepstream_service() -> DeepStreamService:
    """Get or create DeepStream service singleton."""
    global _service
    if _service is None:
        _service = DeepStreamService()
    return _service
