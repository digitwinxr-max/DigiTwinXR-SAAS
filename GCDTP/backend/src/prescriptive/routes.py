"""Prescriptive Routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from .engine import PrescriptiveEngine, get_prescriptive_engine, RecommendationType, Priority

router = APIRouter(prefix="/prescriptive", tags=["prescriptive"])


class RecommendationCreate(BaseModel):
    recommendation_id: str
    type: str
    priority: str
    confidence: float
    title: str
    description: str
    evidence: List[str] = []
    action_items: List[str] = []


@router.get("/recommendations")
async def list_recommendations(
    rec_type: Optional[str] = None,
    approved_only: bool = False
):
    """List recommendations."""
    engine = get_prescriptive_engine()
    rtype = RecommendationType(rec_type) if rec_type else None
    recommendations = engine.list_recommendations(rtype, approved_only=approved_only)
    return {
        "recommendations": [
            {
                "id": r.recommendation_id,
                "type": r.type.value,
                "priority": r.priority.value,
                "confidence": r.confidence,
                "title": r.title,
                "approved": r.approved
            }
            for r in recommendations
        ]
    }


@router.post("/recommendations")
async def create_recommendation(request: RecommendationCreate):
    """Create a recommendation."""
    engine = get_prescriptive_engine()
    recommendation = engine.generate_recommendation(
        request.recommendation_id,
        RecommendationType(request.type),
        Priority(request.priority),
        request.confidence,
        request.title,
        request.description,
        request.evidence,
        request.action_items
    )
    return {"id": recommendation.recommendation_id}


@router.post("/approve/{recommendation_id}")
async def approve_recommendation(recommendation_id: str, approved_by: str):
    """Approve a recommendation."""
    engine = get_prescriptive_engine()
    recommendation = engine.approve_recommendation(recommendation_id, approved_by)
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return {"id": recommendation.recommendation_id, "approved": recommendation.approved}
