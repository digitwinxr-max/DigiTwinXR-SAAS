"""Autonomy Routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from .governance import GovernanceLayer, get_governance_layer, AutonomyLevel, ActionCategory
from .approval import ApprovalWorkflow, get_approval_workflow, ApprovalStatus
from .audit import AuditLogger, get_audit_logger

router = APIRouter(prefix="/autonomy", tags=["autonomy"])


# Governance Routes

class LevelSetRequest(BaseModel):
    level: str


class AuditRequest(BaseModel):
    audit_id: str
    user: str
    action: str
    category: str
    details: Dict[str, Any]
    explanation: Optional[str] = None
    evidence: List[str] = []


@router.get("/level")
async def get_autonomy_level():
    """Get current autonomy level."""
    layer = get_governance_layer()
    return {"level": layer.get_autonomy_level().value, "level_4_allowed": False}


@router.post("/level")
async def set_autonomy_level(request: LevelSetRequest):
    """Set autonomy level (LEVEL 4 FORBIDDEN)."""
    layer = get_governance_layer()
    
    # LEVEL 4 IS FORBIDDEN
    if request.level == "level_4":
        raise HTTPException(status_code=400, detail="LEVEL 4 AUTONOMY IS FORBIDDEN")
    
    try:
        level = AutonomyLevel(request.level)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid autonomy level")
    
    success = layer.set_autonomy_level(level)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to set level")
    
    return {"level": level.value}


# Approval Routes

class ApprovalRequestCreate(BaseModel):
    request_id: str
    requester: str
    action: str
    details: Dict[str, Any]


class ApprovalDecision(BaseModel):
    reviewer: str
    comment: Optional[str] = None


@router.post("/approvals")
async def create_approval_request(request: ApprovalRequestCreate):
    """Create an approval request."""
    workflow = get_approval_workflow()
    approval = workflow.request_approval(
        request.request_id, request.requester, request.action, request.details
    )
    return {"id": approval.request_id, "status": approval.status}


@router.post("/approvals/{request_id}/approve")
async def approve_request(request_id: str, decision: ApprovalDecision):
    """Approve a request."""
    workflow = get_approval_workflow()
    approval = workflow.approve(request_id, decision.reviewer, decision.comment)
    if not approval:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"id": approval.request_id, "status": approval.status}


@router.post("/approvals/{request_id}/reject")
async def reject_request(request_id: str, decision: ApprovalDecision):
    """Reject a request."""
    workflow = get_approval_workflow()
    approval = workflow.reject(request_id, decision.reviewer, decision.comment)
    if not approval:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"id": approval.request_id, "status": approval.status}


@router.get("/approvals/pending")
async def list_pending():
    """List pending approvals."""
    workflow = get_approval_workflow()
    pending = workflow.list_pending()
    return {"pending": [{"id": p.request_id, "action": p.action} for p in pending]}


# Audit Routes

class AuditLogRequest(BaseModel):
    entry_id: str
    operation: str
    user: str
    details: Dict[str, Any]
    evidence: List[str] = []
    reversible: bool = False


@router.post("/audit")
async def log_audit(request: AuditLogRequest):
    """Log an audit entry."""
    logger = get_audit_logger()
    entry = logger.log(
        request.entry_id, request.operation, request.user,
        request.details, request.evidence, request.reversible
    )
    return {"id": entry.entry_id}


@router.get("/audit")
async def get_audit(
    operation: Optional[str] = None,
    user: Optional[str] = None
):
    """Get audit entries."""
    logger = get_audit_logger()
    entries = logger.get_entries(operation, user)
    return {
        "entries": [
            {
                "id": e.entry_id,
                "operation": e.operation,
                "user": e.user,
                "timestamp": e.timestamp.isoformat()
            }
            for e in entries
        ]
    }


# Rollback Routes

class RollbackRequest(BaseModel):
    rollback_id: str
    action_id: str
    original_state: Dict[str, Any]
    reverted_by: str
    reason: str


@router.post("/rollback")
async def record_rollback(request: RollbackRequest):
    """Record a rollback."""
    layer = get_governance_layer()
    rollback = layer.record_rollback(
        request.rollback_id, request.action_id,
        request.original_state, request.reverted_by, request.reason
    )
    return {"id": rollback.rollback_id}


@router.get("/rollback")
async def get_rollbacks(action_id: Optional[str] = None):
    """Get rollback records."""
    layer = get_governance_layer()
    rollbacks = layer.get_rollback_records(action_id)
    return {
        "rollbacks": [
            {
                "id": r.rollback_id,
                "action_id": r.action_id,
                "reverted_by": r.reverted_by,
                "reason": r.reason
            }
            for r in rollbacks
        ]
    }
