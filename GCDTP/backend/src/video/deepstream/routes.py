"""DeepStream Routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from .pipelines import DeepStreamService, get_deepstream_service
from .models import PipelineType, PipelineStatus

router = APIRouter(prefix="/deepstream", tags=["deepstream"])


class GPUCreate(BaseModel):
    gpu_id: str
    name: str
    compute_capability: str
    memory_total_mb: int


class PipelineCreate(BaseModel):
    pipeline_id: str
    name: str
    pipeline_type: str
    gpu_id: Optional[str] = None


@router.get("/gpus")
async def list_gpus():
    """List registered GPUs."""
    service = get_deepstream_service()
    gpus = service.registry.list_gpus()
    return {
        "gpus": [
            {
                "id": g.gpu_id,
                "name": g.name,
                "status": g.status.value,
                "memory_total_mb": g.memory_total_mb
            }
            for g in gpus
        ]
    }


@router.post("/gpus")
async def register_gpu(request: GPUCreate):
    """Register a GPU."""
    service = get_deepstream_service()
    gpu = service.register_gpu(
        request.gpu_id, request.name, request.compute_capability, request.memory_total_mb
    )
    return {"id": gpu.gpu_id, "name": gpu.name}


@router.get("/pipelines")
async def list_pipelines(pipeline_type: Optional[str] = None):
    """List pipelines."""
    service = get_deepstream_service()
    ptype = PipelineType(pipeline_type) if pipeline_type else None
    pipelines = service.registry.list_pipelines(pipeline_type=ptype)
    return {
        "pipelines": [
            {
                "id": p.pipeline_id,
                "name": p.name,
                "type": p.pipeline_type.value,
                "status": p.status.value
            }
            for p in pipelines
        ]
    }


@router.post("/pipelines")
async def create_pipeline(request: PipelineCreate):
    """Create a pipeline."""
    service = get_deepstream_service()
    try:
        ptype = PipelineType(request.pipeline_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid pipeline type")
    
    pipeline = service.create_pipeline(
        request.pipeline_id, request.name, ptype, request.gpu_id
    )
    if not pipeline:
        raise HTTPException(status_code=400, detail="GPU not found")
    return {"id": pipeline.pipeline_id, "name": pipeline.name}


@router.get("/analytics")
async def list_analytics(requires_review: Optional[bool] = None):
    """List analytics."""
    service = get_deepstream_service()
    analytics = service.registry.list_analytics(requires_review=requires_review)
    return {"analytics": [{"id": a.analytics_id, "pipeline_id": a.pipeline_id} for a in analytics]}
