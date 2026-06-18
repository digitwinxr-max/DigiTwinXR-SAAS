"""
Agent Task Model

Represents an agent task with approval workflow.
Tasks require human approval before execution.
"""

import uuid
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


class TaskStatus(str, Enum):
    """Task statuses."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"


@dataclass
class AgentTask:
    """
    Agent task with approval workflow.
    
    Human approval is required before execution.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    task_type: str = ""
    status: TaskStatus = TaskStatus.PENDING
    requested_by: str = ""
    approved_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = None
    context_data: Dict[str, Any] = field(default_factory=dict)
    result_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "task_type": self.task_type,
            "status": self.status.value if isinstance(self.status, Enum) else self.status,
            "requested_by": self.requested_by,
            "approved_by": self.approved_by,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "executed_at": self.executed_at.isoformat() if isinstance(self.executed_at, datetime) else self.executed_at,
            "context_data": self.context_data,
            "result_data": self.result_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentTask":
        """Create from dictionary."""
        status = data.get("status")
        if isinstance(status, str):
            status = TaskStatus(status)
        
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        
        executed_at = data.get("executed_at")
        if isinstance(executed_at, str):
            executed_at = datetime.fromisoformat(executed_at.replace("Z", "+00:00"))
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            agent_id=data.get("agent_id", ""),
            task_type=data.get("task_type", ""),
            status=status or TaskStatus.PENDING,
            requested_by=data.get("requested_by", ""),
            approved_by=data.get("approved_by"),
            created_at=created_at or datetime.utcnow(),
            executed_at=executed_at,
            context_data=data.get("context_data", {}),
            result_data=data.get("result_data", {})
        )
    
    def is_pending(self) -> bool:
        """Check if task is pending approval."""
        return self.status == TaskStatus.PENDING
    
    def is_approved(self) -> bool:
        """Check if task is approved."""
        return self.status == TaskStatus.APPROVED
    
    def can_execute(self) -> bool:
        """Check if task can be executed."""
        return self.status == TaskStatus.APPROVED
    
    def can_approve(self) -> bool:
        """Check if task can be approved."""
        return self.status == TaskStatus.PENDING
