"""
Approval Module

Human approval workflow for all AI actions.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


class ApprovalStatus:
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class ApprovalRequest:
    """Approval request."""
    request_id: str
    timestamp: datetime
    requester: str
    action: str
    details: Dict[str, Any]
    status: str
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    comment: Optional[str]


class ApprovalWorkflow:
    """
    Approval workflow for human-in-the-loop.
    """
    
    def __init__(self):
        self._requests: Dict[str, ApprovalRequest] = {}
    
    def request_approval(
        self,
        request_id: str,
        requester: str,
        action: str,
        details: Dict[str, Any]
    ) -> ApprovalRequest:
        """Create an approval request."""
        request = ApprovalRequest(
            request_id=request_id,
            timestamp=datetime.now(),
            requester=requester,
            action=action,
            details=details,
            status=ApprovalStatus.PENDING,
            reviewed_by=None,
            reviewed_at=None,
            comment=None
        )
        self._requests[request_id] = request
        return request
    
    def approve(self, request_id: str, reviewer: str, comment: Optional[str] = None) -> ApprovalRequest:
        """Approve a request."""
        request = self._requests.get(request_id)
        if request:
            request.status = ApprovalStatus.APPROVED
            request.reviewed_by = reviewer
            request.reviewed_at = datetime.now()
            request.comment = comment
        return request
    
    def reject(self, request_id: str, reviewer: str, comment: Optional[str] = None) -> ApprovalRequest:
        """Reject a request."""
        request = self._requests.get(request_id)
        if request:
            request.status = ApprovalStatus.REJECTED
            request.reviewed_by = reviewer
            request.reviewed_at = datetime.now()
            request.comment = comment
        return request
    
    def list_pending(self) -> List[ApprovalRequest]:
        """List pending requests."""
        return [r for r in self._requests.values() if r.status == ApprovalStatus.PENDING]


_workflow: Optional[ApprovalWorkflow] = None


def get_approval_workflow() -> ApprovalWorkflow:
    """Get or create approval workflow singleton."""
    global _workflow
    if _workflow is None:
        _workflow = ApprovalWorkflow()
    return _workflow
