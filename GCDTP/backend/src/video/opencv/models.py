"""
OpenCV Processing Models

Image processing framework models.
NO AI, classification, tracking, YOLO, or DeepStream.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ProcessingOperation(str, Enum):
    """Supported image processing operations."""
    RESIZE = "resize"
    CROP = "crop"
    ROTATE = "rotate"
    FLIP = "flip"
    HISTOGRAM = "histogram"
    COLOR_CONVERT = "color_convert"
    BLUR = "blur"
    SHARPEN = "sharpen"
    THRESHOLD = "threshold"
    EDGE_DETECT = "edge_detect"


class ColorSpace(str, Enum):
    """Color space conversion targets."""
    RGB = "rgb"
    BGR = "bgr"
    GRAY = "gray"
    HSV = "hsv"
    LAB = "lab"
    YUV = "yuv"


@dataclass
class ProcessingConfig:
    """Configuration for a processing operation."""
    operation: ProcessingOperation
    params: Dict[str, Any]
    order: int = 0


@dataclass
class ProcessingPipeline:
    """Pipeline of image processing operations."""
    pipeline_id: str
    name: str
    operations: List[ProcessingConfig]
    created_at: datetime
    updated_at: datetime


@dataclass
class ProcessingResult:
    """Result of an image processing operation."""
    operation: ProcessingOperation
    success: bool
    output_shape: Optional[Tuple[int, int, int]]
    processing_time_ms: float
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HistogramData:
    """Histogram data for an image."""
    channels: List[str]
    values: List[List[int]]
    bins: int
    range_min: int
    range_max: int


@dataclass
class FrameInfo:
    """Frame extraction metadata."""
    frame_id: str
    video_path: str
    timestamp_ms: float
    frame_number: int
    width: int
    height: int
    codec: str
    fps: float


class ProcessingRegistry:
    """
    Registry for image processing operations.
    
    ALLOWED:
    - resize, crop, rotate, flip
    - histogram, color conversion
    - blur, sharpen, threshold
    - Frame extraction
    
    FORBIDDEN:
    - AI inference
    - Classification
    - Object tracking
    - YOLO detection
    - DeepStream
    """
    
    SUPPORTED_OPERATIONS = [
        ProcessingOperation.RESIZE,
        ProcessingOperation.CROP,
        ProcessingOperation.ROTATE,
        ProcessingOperation.FLIP,
        ProcessingOperation.HISTOGRAM,
        ProcessingOperation.COLOR_CONVERT,
        ProcessingOperation.BLUR,
        ProcessingOperation.SHARPEN,
        ProcessingOperation.THRESHOLD,
        ProcessingOperation.EDGE_DETECT,
    ]
    
    SUPPORTED_COLOR_SPACES = [
        ColorSpace.RGB,
        ColorSpace.BGR,
        ColorSpace.GRAY,
        ColorSpace.HSV,
        ColorSpace.LAB,
        ColorSpace.YUV,
    ]
    
    def __init__(self):
        self._pipelines: Dict[str, ProcessingPipeline] = {}
    
    def create_pipeline(self, pipeline_id: str, name: str) -> ProcessingPipeline:
        """Create a new processing pipeline."""
        pipeline = ProcessingPipeline(
            pipeline_id=pipeline_id,
            name=name,
            operations=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self._pipelines[pipeline_id] = pipeline
        return pipeline
    
    def get_pipeline(self, pipeline_id: str) -> Optional[ProcessingPipeline]:
        """Get a pipeline by ID."""
        return self._pipelines.get(pipeline_id)
    
    def add_operation(
        self,
        pipeline_id: str,
        operation: ProcessingOperation,
        params: Dict[str, Any]
    ) -> Optional[ProcessingConfig]:
        """Add an operation to a pipeline."""
        pipeline = self._pipelines.get(pipeline_id)
        if not pipeline:
            return None
        
        config = ProcessingConfig(
            operation=operation,
            params=params,
            order=len(pipeline.operations)
        )
        pipeline.operations.append(config)
        pipeline.updated_at = datetime.now()
        return config
    
    def list_pipelines(self) -> List[ProcessingPipeline]:
        """List all pipelines."""
        return list(self._pipelines.values())
    
    def delete_pipeline(self, pipeline_id: str) -> bool:
        """Delete a pipeline."""
        if pipeline_id in self._pipelines:
            del self._pipelines[pipeline_id]
            return True
        return False


# Singleton instance
_registry: Optional[ProcessingRegistry] = None


def get_processing_registry() -> ProcessingRegistry:
    """Get or create processing registry singleton."""
    global _registry
    if _registry is None:
        _registry = ProcessingRegistry()
    return _registry
