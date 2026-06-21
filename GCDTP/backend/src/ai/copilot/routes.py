"""
Human-Supervised Copilot Routes

RESTRICTED to READ-ONLY operations.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from .capability import (
    CopilotLayer,
    CopilotCapabilityRegistry,
    CapabilityType,
    ActionType,
    get_copilot_layer,
)

router = APIRouter(prefix="/copilot", tags=["copilot"])


class CapabilityRequest(BaseModel):
    query: str
    context: Dict[str, Any] = {}


class ForbiddenActionRequest(BaseModel):
    action_type: str
    details: Dict[str, Any] = {}


@router.get("/capabilities")
async def list_capabilities():
    """List all available copilot capabilities."""
    registry = CopilotCapabilityRegistry()
    capabilities = registry.list_capabilities()
    
    return {
        "capabilities": [
            {
                "type": c.capability_type.value,
                "description": c.description,
                "examples": c.examples,
                "requires_context": c.requires_context
            }
            for c in capabilities
        ],
        "forbidden_actions": [a.value for a in registry.FORBIDDEN_ACTIONS]
    }


@router.post("/ask")
async def ask(request: CapabilityRequest):
    """
    Ask a question.
    
    READ-ONLY operation.
    """
    copilot = get_copilot_layer()
    response = copilot.execute_capability(
        CapabilityType.ASK,
        request.query,
        request.context
    )
    
    return {
        "capability": response.capability.value,
        "content": response.content,
        "suggestions": response.suggestions,
        "citations": response.citations,
        "confidence": response.confidence
    }


@router.post("/explain")
async def explain(request: CapabilityRequest):
    """
    Explain a decision or context.
    
    READ-ONLY operation.
    """
    copilot = get_copilot_layer()
    response = copilot.execute_capability(
        CapabilityType.EXPLAIN,
        request.query,
        request.context
    )
    
    return {
        "capability": response.capability.value,
        "content": response.content,
        "suggestions": response.suggestions,
        "citations": response.citations,
        "confidence": response.confidence
    }


@router.post("/summarize")
async def summarize(request: CapabilityRequest):
    """
    Summarize context or data.
    
    READ-ONLY operation.
    """
    copilot = get_copilot_layer()
    response = copilot.execute_capability(
        CapabilityType.SUMMARIZE,
        request.query,
        request.context
    )
    
    return {
        "capability": response.capability.value,
        "content": response.content,
        "suggestions": response.suggestions,
        "citations": response.citations,
        "confidence": response.confidence
    }


@router.post("/recommend")
async def recommend(request: CapabilityRequest):
    """
    Generate recommendations.
    
    READ-ONLY - recommendations require human approval.
    """
    copilot = get_copilot_layer()
    response = copilot.execute_capability(
        CapabilityType.RECOMMEND,
        request.query,
        request.context
    )
    
    return {
        "capability": response.capability.value,
        "content": response.content,
        "suggestions": response.suggestions,
        "citations": response.citations,
        "confidence": response.confidence,
        "requires_approval": True,
        "message": "Recommendations require human review before action."
    }


@router.post("/forbidden-attempt")
async def attempt_forbidden(request: ForbiddenActionRequest):
    """
    Attempt a forbidden action (will be REJECTED).
    
    This endpoint exists for safety logging.
    """
    copilot = get_copilot_layer()
    
    try:
        action_type = ActionType(request.action_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid action type")
    
    forbidden = copilot.attempt_forbidden_action(action_type, request.details)
    
    return {
        "status": "rejected",
        "action_type": forbidden.action_type.value,
        "reason": forbidden.reason,
        "rejected_at": forbidden.rejected_at.isoformat()
    }


@router.get("/forbidden-attempts")
async def get_forbidden_attempts():
    """Get all forbidden action attempts."""
    copilot = get_copilot_layer()
    attempts = copilot.get_forbidden_attempts()
    
    return {
        "count": len(attempts),
        "attempts": [
            {
                "action_type": a.action_type.value,
                "reason": a.reason,
                "rejected_at": a.rejected_at.isoformat()
            }
            for a in attempts
        ]
    }
