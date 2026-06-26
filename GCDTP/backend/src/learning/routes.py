"""Learning Routes"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Any

from .memory import get_learning_memory
from .feedback import get_feedback_service

router = APIRouter(prefix="/learning", tags=["learning"])


class FeedbackCreate(BaseModel):
    feedback_id: str
    source: str
    target_type: str
    target_id: str
    feedback_type: str
    rating: Optional[float] = None
    comment: Optional[str] = None


@router.post("/feedback")
async def add_feedback(request: FeedbackCreate):
    """Add human feedback."""
    service = get_feedback_service()
    feedback = service.process_feedback(
        request.feedback_id, request.source, request.target_type,
        request.target_id, request.feedback_type, request.rating, request.comment
    )
    return {"id": feedback.feedback_id}


@router.get("/feedback")
async def list_feedback(target_id: Optional[str] = None):
    """List feedback."""
    memory = get_learning_memory()
    feedback = memory.list_feedback(target_id=target_id)
    return {"feedback": [{"id": f.feedback_id, "rating": f.rating} for f in feedback]}


@router.get("/history")
async def get_history(entity_type: Optional[str] = None, entity_id: Optional[str] = None):
    """Get knowledge history."""
    memory = get_learning_memory()
    history = memory.get_history(entity_type, entity_id)
    return {"history": [{"id": h.history_id, "action": h.action} for h in history]}
