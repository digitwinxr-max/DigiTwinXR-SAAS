"""
Cognitive Copilot Routes

FastAPI routes for Cognitive Copilot API.
This is read-only AI context - NO LLM integration yet.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from ..schemas.copilot import (
    CopilotSessionCreate,
    CopilotSessionResponse,
    CopilotMessageResponse,
    CopilotQuery,
    CopilotAnswer,
    ContextBundle,
    SessionHistory,
    ContextResponse,
    QueryResponse
)
from ..services.copilot_service import copilot_service


router = APIRouter(prefix="/copilot", tags=["copilot"])


# Session Routes
@router.post("/session", response_model=CopilotSessionResponse)
async def create_session(data: CopilotSessionCreate):
    """
    Create a new copilot session.
    
    Sessions store conversation history for context.
    """
    session = copilot_service.create_session(data.session_name)
    return session.to_dict()


@router.get("/session/{session_id}", response_model=CopilotSessionResponse)
async def get_session(session_id: str):
    """
    Get a specific session.
    """
    session = copilot_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.to_dict()


@router.get("/sessions", response_model=list)
async def list_sessions():
    """
    List all sessions.
    
    Returns sessions sorted by last activity.
    """
    sessions = copilot_service.get_all_sessions()
    return [s.to_dict() for s in sessions]


# Query Routes
@router.post("/query", response_model=QueryResponse)
async def query_copilot(data: CopilotQuery):
    """
    Query the copilot.
    
    This is a deterministic template-based response.
    NO LLM integration yet.
    
    This is READ ONLY - no operational modifications.
    """
    # Get or validate session
    session = copilot_service.get_session(data.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Add user message
    user_message = copilot_service.add_message(
        session_id=data.session_id,
        role="user",
        message=data.query
    )
    
    # Build context bundle
    context_data = {}
    if data.entity_type and data.entity_id:
        context_data = {
            "entity_type": data.entity_type,
            "entity_id": data.entity_id
        }
    
    context_bundle = copilot_service.build_context_bundle(
        entity_type=data.entity_type or "unknown",
        entity_id=data.entity_id or "unknown",
        context_data=context_data
    )
    
    # Generate response (deterministic template)
    answer = copilot_service.generate_context(data.query, context_bundle)
    
    # Add assistant message
    copilot_service.add_message(
        session_id=data.session_id,
        role="assistant",
        message=answer.answer,
        context_data={"context_used": answer.context_used, "sources": answer.sources}
    )
    
    return QueryResponse(
        query=data.query,
        answer=answer,
        context=context_bundle
    )


# History Routes
@router.get("/history/{session_id}", response_model=SessionHistory)
async def get_history(session_id: str):
    """
    Get conversation history for a session.
    """
    session = copilot_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = copilot_service.get_messages(session_id)
    
    return SessionHistory(
        session_id=session_id,
        messages=[m.to_dict() for m in messages]
    )


# Context Routes
@router.get("/context/{entity_type}/{entity_id}", response_model=ContextResponse)
async def get_context(
    entity_type: str,
    entity_id: str,
    asset: Optional[dict] = None,
    health: Optional[dict] = None,
    sensors: Optional[str] = None,
    events: Optional[str] = None
):
    """
    Get context bundle for an entity.
    
    This aggregates data from all engines:
    - Asset Engine
    - Health Engine
    - Event Engine
    - Timeline Engine
    - Logbook Engine
    - Knowledge Repository
    - Semantic Layer
    
    This is READ ONLY - no operational modifications.
    """
    context_data = {
        "entity_type": entity_type,
        "entity_id": entity_id
    }
    
    if asset:
        context_data["asset"] = asset
    if health:
        context_data["health"] = health
    if sensors:
        context_data["sensors"] = eval(sensors) if sensors else []
    if events:
        context_data["events"] = eval(events) if events else []
    
    bundle = copilot_service.build_context_bundle(
        entity_type=entity_type,
        entity_id=entity_id,
        context_data=context_data
    )
    
    return ContextResponse(
        entity_type=entity_type,
        entity_id=entity_id,
        bundle=bundle
    )


# Message Routes
@router.get("/messages/{session_id}", response_model=list)
async def get_messages(session_id: str):
    """
    Get all messages in a session.
    """
    session = copilot_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = copilot_service.get_messages(session_id)
    return [m.to_dict() for m in messages]


# Summary Routes
@router.get("/summary/{entity_type}/{entity_id}")
async def get_entity_summary(entity_type: str, entity_id: str):
    """
    Get a summary of an entity across all engines.
    
    This is READ ONLY - no operational modifications.
    """
    bundle = copilot_service.build_context_bundle(
        entity_type=entity_type,
        entity_id=entity_id
    )
    
    return {
        "asset": bundle.asset,
        "health": bundle.health,
        "events_count": len(bundle.events),
        "sensors_count": len(bundle.sensors),
        "timeline_count": len(bundle.timeline),
        "logbook_count": len(bundle.logbook),
        "knowledge_count": len(bundle.knowledge),
        "summary": bundle.summary
    }
