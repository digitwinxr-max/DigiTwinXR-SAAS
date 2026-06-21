"""Reasoning Session Routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from .session import ReasoningSessionManager, get_reasoning_manager, SessionStatus

router = APIRouter(prefix="/reasoning", tags=["reasoning"])


class CreateSessionRequest(BaseModel):
    user_intent: str
    entities: Optional[List[Dict[str, Any]]] = None


@router.post("/sessions")
async def create_session(request: CreateSessionRequest):
    manager = get_reasoning_manager()
    session = manager.create_session(request.user_intent, request.entities)
    return {"session_id": session.session_id, "status": session.get_state().status.value}


@router.get("/sessions")
async def list_sessions():
    manager = get_reasoning_manager()
    sessions = manager.list_sessions()
    return {"sessions": [{"session_id": s.session_id, "status": s.status.value} for s in sessions]}


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    manager = get_reasoning_manager()
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    state = session.get_state()
    return {
        "session_id": state.session_id,
        "status": state.status.value,
        "current_step": state.current_step,
        "steps": [{"step_id": s.step_id, "description": s.description, "status": s.status.value} for s in state.steps],
        "inference_count": len(state.inference_history),
        "final_conclusion": state.final_conclusion
    }


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    manager = get_reasoning_manager()
    if not manager.delete_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted"}
