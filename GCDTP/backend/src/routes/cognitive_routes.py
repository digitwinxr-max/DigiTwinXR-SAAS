"""
Cognitive Twin Routes

FastAPI routes for Cognitive Twin Engine.
ADVISORY ONLY - NO automation, NO autonomous decisions.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from ..schemas.cognitive import (
    CognitiveSessionCreate,
    CognitiveSessionResponse,
    CognitiveSessionsListResponse,
    CognitiveQueryCreate,
    CognitiveQueryResponse,
    CognitiveQueryWithContextResponse,
    ContextSourceResponse,
    ConfidenceResponse,
    InsightsListResponse,
    ExplanationsListResponse,
    InsightGraphResponse,
    HistoryResponse,
    HistoryItem
)
from ..services.cognitive_twin_service import cognitive_twin_service


router = APIRouter(prefix="/cognitive", tags=["cognitive"])


@router.post("/session", response_model=CognitiveSessionResponse)
async def create_session(data: CognitiveSessionCreate):
    """
    Create a new cognitive session.
    """
    session = cognitive_twin_service.create_session(data)
    
    return CognitiveSessionResponse(
        id=session.id,
        name=session.name,
        description=session.description,
        asset_id=session.asset_id,
        user_id=session.user_id,
        context_summary=session.context_summary,
        query_count=session.query_count,
        created_at=session.created_at,
        updated_at=session.updated_at
    )


@router.get("/sessions", response_model=CognitiveSessionsListResponse)
async def get_sessions(limit: int = Query(20, ge=1, le=100)):
    """
    Get all cognitive sessions.
    """
    sessions = cognitive_twin_service.get_sessions(limit)
    
    return CognitiveSessionsListResponse(
        sessions=[
            CognitiveSessionResponse(
                id=s.id,
                name=s.name,
                description=s.description,
                asset_id=s.asset_id,
                user_id=s.user_id,
                context_summary=s.context_summary,
                query_count=s.query_count,
                created_at=s.created_at,
                updated_at=s.updated_at
            )
            for s in sessions
        ],
        total=len(sessions)
    )


@router.get("/session/{session_id}", response_model=CognitiveSessionResponse)
async def get_session(session_id: str):
    """
    Get session by ID.
    """
    session = cognitive_twin_service.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return CognitiveSessionResponse(
        id=session.id,
        name=session.name,
        description=session.description,
        asset_id=session.asset_id,
        user_id=session.user_id,
        context_summary=session.context_summary,
        query_count=session.query_count,
        created_at=session.created_at,
        updated_at=session.updated_at
    )


@router.post("/query", response_model=CognitiveQueryWithContextResponse)
async def ask_question(data: CognitiveQueryCreate, session_id: str = Query(..., description="Session ID")):
    """
    Ask a question to the Cognitive Twin.
    
    ADVISORY ONLY - retrieves context and generates explanation.
    NO autonomous decisions, NO actions.
    """
    query, contexts = cognitive_twin_service.ask_question(
        session_id=session_id,
        question=data.question,
        asset_id=data.asset_id
    )
    
    return CognitiveQueryWithContextResponse(
        query=CognitiveQueryResponse(
            id=query.id,
            session_id=query.session_id,
            question=query.question,
            answer=query.answer,
            confidence=query.confidence,
            explanation=query.explanation,
            created_at=query.created_at
        ),
        context=[
            ContextSourceResponse(
                id=c.id,
                source_type=c.source_type.value,
                reference_id=c.reference_id,
                weight=c.weight,
                summary=c.summary,
                detail=c.detail,
                relevance_score=c.relevance_score,
                created_at=c.created_at
            )
            for c in contexts
        ]
    )


@router.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(
    session_id: str,
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get query history for a session.
    """
    items = cognitive_twin_service.get_session_history(session_id)
    
    return HistoryResponse(
        session_id=session_id,
        items=items[:limit],
        total=len(items)
    )


@router.get("/context/{query_id}")
async def get_context(query_id: str):
    """
    Get context for a query.
    """
    contexts = cognitive_twin_service.get_query_context(query_id)
    
    return {
        "query_id": query_id,
        "context": [
            ContextSourceResponse(
                id=c.id,
                source_type=c.source_type.value,
                reference_id=c.reference_id,
                weight=c.weight,
                summary=c.summary,
                detail=c.detail,
                relevance_score=c.relevance_score,
                created_at=c.created_at
            )
            for c in contexts
        ],
        "total": len(contexts)
    }


@router.get("/insights", response_model=InsightsListResponse)
async def get_insights(limit: int = Query(20, ge=1, le=100)):
    """
    Get recent insights.
    """
    return cognitive_twin_service.get_insights(limit)


@router.get("/explanations", response_model=ExplanationsListResponse)
async def get_explanations(limit: int = Query(20, ge=1, le=100)):
    """
    Get recent explanations.
    """
    return cognitive_twin_service.get_explanations(limit)


@router.get("/confidence/{query_id}")
async def get_confidence(query_id: str):
    """
    Get confidence for a query.
    """
    confidence = cognitive_twin_service.get_confidence(query_id)
    
    if not confidence:
        raise HTTPException(status_code=404, detail="Query not found")
    
    return confidence


@router.get("/graph/{query_id}", response_model=InsightGraphResponse)
async def get_graph(query_id: str):
    """
    Get insight graph for a query.
    """
    return cognitive_twin_service.build_insight_graph(query_id)
