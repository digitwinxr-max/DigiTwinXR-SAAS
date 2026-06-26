"""YOLO Routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from .registry import YOLORegistryService, get_yolo_service
from .models import ModelType, ModelSize

router = APIRouter(prefix="/yolo", tags=["yolo"])


class ModelRegister(BaseModel):
    model_id: str
    name: str
    model_type: str
    model_size: str
    version: str = "latest"


class DetectionRecord(BaseModel):
    detection_id: str
    model_id: str
    frame_id: str
    class_id: int
    confidence: float
    bbox: List[int]


class ApprovalRequest(BaseModel):
    approved_by: str


@router.get("/models")
async def list_models():
    """List registered YOLO models."""
    service = get_yolo_service()
    models = service.registry.list_models()
    return {
        "models": [
            {
                "id": m.model_id,
                "name": m.name,
                "type": m.model_type.value,
                "size": m.model_size.value,
                "version": m.version
            }
            for m in models
        ]
    }


@router.post("/models")
async def register_model(request: ModelRegister):
    """Register a YOLO model."""
    service = get_yolo_service()
    try:
        model_type = ModelType(request.model_type)
        model_size = ModelSize(request.model_size)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid model type or size")
    
    model = service.register_model(
        model_id=request.model_id,
        name=request.name,
        model_type=model_type,
        model_size=model_size,
        classes=service.registry.DEFAULT_CLASSES,
        version=request.version
    )
    return {"id": model.model_id, "name": model.name}


@router.get("/classes")
async def list_classes():
    """List detection classes."""
    service = get_yolo_service()
    classes = service.registry.list_classes()
    return {
        "classes": [
            {
                "id": c.class_id,
                "name": c.name,
                "category": c.category
            }
            for c in classes
        ]
    }


@router.post("/detections")
async def record_detection(request: DetectionRecord):
    """Record a detection (requires human approval)."""
    service = get_yolo_service()
    detection = service.record_detection(
        detection_id=request.detection_id,
        model_id=request.model_id,
        frame_id=request.frame_id,
        class_id=request.class_id,
        confidence=request.confidence,
        bbox=(request.bbox[0], request.bbox[1], request.bbox[2], request.bbox[3])
    )
    return {"id": detection.detection_id, "approved": detection.approved}


@router.post("/detections/{detection_id}/approve")
async def approve_detection(detection_id: str, request: ApprovalRequest):
    """Approve a detection."""
    service = get_yolo_service()
    detection = service.approve_detection(detection_id, request.approved_by)
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    return {"id": detection.detection_id, "approved": detection.approved}


@router.get("/detections")
async def list_detections(approved_only: bool = False):
    """List detections."""
    service = get_yolo_service()
    detections = service.registry.list_detections(approved_only=approved_only)
    return {
        "detections": [
            {
                "id": d.detection_id,
                "model_id": d.model_id,
                "class_name": d.class_name,
                "confidence": d.confidence,
                "approved": d.approved
            }
            for d in detections
        ]
    }


@router.get("/pending")
async def get_pending():
    """Get detections pending approval."""
    service = get_yolo_service()
    pending = service.registry.get_pending_approvals()
    return {"pending": len(pending)}
