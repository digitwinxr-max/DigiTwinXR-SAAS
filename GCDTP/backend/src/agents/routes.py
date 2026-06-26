"""Agent Routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from .registry import AgentRegistryService, get_agent_service
from .models import AgentType

router = APIRouter(prefix="/agents", tags=["agents"])


class InvocationRequest(BaseModel):
    capability: str
    input_data: Dict[str, Any]


class ApprovalRequest(BaseModel):
    approved_by: str


@router.get("/")
async def list_agents():
    """List registered agents."""
    service = get_agent_service()
    agents = service.registry.list_agents()
    return {
        "agents": [
            {
                "id": a.agent_id,
                "name": a.name,
                "type": a.agent_type.value,
                "capabilities": [c.name for c in a.capabilities]
            }
            for a in agents
        ]
    }


@router.post("/request")
async def request_invocation(agent_id: str, request: InvocationRequest):
    """Request agent invocation (requires approval)."""
    service = get_agent_service()
    invocation = service.request_invocation(agent_id, request.capability, request.input_data)
    if not invocation:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"invocation_id": invocation.invocation_id, "status": invocation.status}


@router.post("/approve/{invocation_id}")
async def approve_invocation(invocation_id: str, request: ApprovalRequest):
    """Approve an invocation."""
    service = get_agent_service()
    invocation = service.registry.approve_invocation(invocation_id, request.approved_by)
    if not invocation:
        raise HTTPException(status_code=404, detail="Invocation not found")
    return {"id": invocation.invocation_id, "approved_by": invocation.approved_by}


@router.get("/invocations")
async def list_invocations(pending_only: bool = False):
    """List invocations."""
    service = get_agent_service()
    invocations = service.registry.list_invocations(pending_only=pending_only)
    return {
        "invocations": [
            {
                "id": i.invocation_id,
                "agent_id": i.agent_id,
                "capability": i.capability,
                "status": i.status
            }
            for i in invocations
        ]
    }
