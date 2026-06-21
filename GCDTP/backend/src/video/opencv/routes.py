"""OpenCV Routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from .models import ProcessingOperation, ColorSpace, get_processing_registry
from .processors import ImageProcessor, FrameExtractor

router = APIRouter(prefix="/opencv", tags=["opencv"])


class PipelineCreate(BaseModel):
    name: str


class OperationAdd(BaseModel):
    operation: str
    params: Dict[str, Any] = {}


class ProcessRequest(BaseModel):
    operation: str
    params: Dict[str, Any] = {}


@router.get("/operations")
async def list_operations():
    """List supported operations."""
    return {
        "operations": [op.value for op in ImageProcessor.__dict__.keys() if not op.startswith("_")],
        "color_spaces": [cs.value for cs in ColorSpace]
    }


@router.get("/pipelines")
async def list_pipelines():
    """List processing pipelines."""
    registry = get_processing_registry()
    pipelines = registry.list_pipelines()
    return {
        "pipelines": [
            {
                "id": p.pipeline_id,
                "name": p.name,
                "operations": len(p.operations)
            }
            for p in pipelines
        ]
    }


@router.post("/pipelines")
async def create_pipeline(request: PipelineCreate):
    """Create a processing pipeline."""
    import uuid
    registry = get_processing_registry()
    pipeline_id = str(uuid.uuid4())
    pipeline = registry.create_pipeline(pipeline_id, request.name)
    return {"id": pipeline.pipeline_id, "name": pipeline.name}


@router.post("/pipelines/{pipeline_id}/operations")
async def add_operation(pipeline_id: str, request: OperationAdd):
    """Add an operation to a pipeline."""
    registry = get_processing_registry()
    try:
        operation = ProcessingOperation(request.operation)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid operation")
    
    config = registry.add_operation(pipeline_id, operation, request.params)
    if not config:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    return {"operation": config.operation.value, "order": config.order}


@router.post("/process")
async def process_image(request: ProcessRequest):
    """Execute a processing operation."""
    try:
        operation = ProcessingOperation(request.operation)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid operation")
    
    processor = ImageProcessor()
    result = None
    
    if operation == ProcessingOperation.RESIZE:
        result = processor.resize(
            request.params.get("width", 640),
            request.params.get("height", 480)
        )
    elif operation == ProcessingOperation.CROP:
        result = processor.crop(
            request.params.get("x", 0),
            request.params.get("y", 0),
            request.params.get("width", 100),
            request.params.get("height", 100)
        )
    elif operation == ProcessingOperation.HISTOGRAM:
        histogram = processor.calculate_histogram()
        return {
            "operation": operation.value,
            "success": True,
            "channels": histogram.channels,
            "bins": histogram.bins
        }
    elif operation == ProcessingOperation.COLOR_CONVERT:
        try:
            target = ColorSpace(request.params.get("target_space", "rgb"))
            result = processor.convert_color(target)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid color space")
    
    if result:
        return {
            "operation": result.operation.value,
            "success": result.success,
            "processing_time_ms": result.processing_time_ms,
            "metadata": result.metadata
        }
    
    return {"operation": operation.value, "success": False, "error": "Not implemented"}
