"""
Agent Action Model

Represents an action proposed by an agent.
Actions require human approval before execution.
"""

import uuid
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


class ApprovalStatus(str, Enum):
    """Action approval statuses."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"


@dataclass
class AgentAction:
    """
    Agent action.
    
    Proposed by agent, requires human approval.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = ""
    action_type: str = ""
    action_payload: Dict[str, Any] = field(default_factory=dict)
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "action_type": self.action_type,
            "action_payload": self.action_payload,
            "approval_status": self.approval_status.value if isinstance(self.approval_status, Enum) else self.approval_status,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "executed_at": self.executed_at.isoformat() if isinstance(self.executed_at, datetime) else self.executed_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentAction":
        """Create from dictionary."""
        approval_status = data.get("approval_status")
        if isinstance(approval_status, str):
            approval_status = ApprovalStatus(approval_status)
        
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        
        executed_at = data.get("executed_at")
        if isinstance(executed_at, str):
            executed_at = datetime.fromisoformat(executed_at.replace("Z", "+00:00"))
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            task_id=data.get("task_id", ""),
            action_type=data.get("action_type", ""),
            action_payload=data.get("action_payload", {}),
            approval_status=approval_status or ApprovalStatus.PENDING,
            created_at=created_at or datetime.utcnow(),
            executed_at=executed_at
        )
    
    def is_pending(self) -> bool:
        """Check if action is pending approval."""
        return self.approval_status == ApprovalStatus.PENDING
    
    def is_approved(self) -> bool:
        """Check if action is approved."""
        return self.approval_status == ApprovalStatus.APPROVED
    
    def can_execute(self) -> bool:
        """Check if action can be executed."""
        return self.approval_status == ApprovalStatus.APPROVED
    
    def get_type_display_name(self) -> str:
        """Get human-readable action type."""
        names = {
            "analyze": "Analyze Context",
            "diagnose": "Diagnose Issue",
            "recommend": "Create Recommendation",
            "suggest_maintenance": "Suggest Maintenance",
            "suggest_recovery": "Suggest Recovery",
            "retrieve_knowledge": "Retrieve Knowledge",
            "analyze_timeline": "Analyze Timeline"
        }
        return names.get(self.action_type, self.action_type)
