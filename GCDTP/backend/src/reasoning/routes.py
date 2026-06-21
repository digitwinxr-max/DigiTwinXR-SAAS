"""Reasoning Routes"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

from .fusion_engine import FusionEngine, get_fusion_engine
from .schemas import DomainSource

router = APIRouter(prefix="/reasoning", tags=["reasoning"])


class FusionRequest(BaseModel):
    query: str
    domains: List[str]


@router.post("/fuse")
async def fuse_domains(request: FusionRequest):
    """Fuse results from multiple domains."""
    engine = get_fusion_engine()
    domains = [DomainSource(d) for d in request.domains]
    from .schemas import FusionQuery
    result = engine.fuse(FusionQuery(query=request.query, domains=domains))
    return {
        "query": result.query,
        "confidence": result.confidence,
        "context": result.fused_context,
        "requires_review": result.requires_review
    }
