"""OpenCV Processing Layer"""
from .models import (
    ProcessingOperation,
    ColorSpace,
    ProcessingConfig,
    ProcessingPipeline,
    ProcessingResult,
    HistogramData,
    FrameInfo,
    ProcessingRegistry,
    get_processing_registry,
)
from .processors import ImageProcessor, FrameExtractor
from .routes import router as opencv_router

__all__ = [
    "ProcessingOperation",
    "ColorSpace",
    "ProcessingConfig",
    "ProcessingPipeline",
    "ProcessingResult",
    "HistogramData",
    "FrameInfo",
    "ProcessingRegistry",
    "get_processing_registry",
    "ImageProcessor",
    "FrameExtractor",
    "opencv_router",
]
