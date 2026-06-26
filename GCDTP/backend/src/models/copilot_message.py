"""
Cognitive Copilot Message Model

Represents a message in a copilot conversation.
This is read-only AI context - NO LLM integration yet.
"""

import uuid
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


class MessageRole(str, Enum):
    """Message roles in copilot conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class CopilotMessage:
    """
    Copilot message.
    
    Stores user queries and assistant responses.
    This is read-only - no operational modifications.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    role: MessageRole = MessageRole.USER
    message: str = ""
    context_data: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role.value if isinstance(self.role, Enum) else self.role,
            "message": self.message,
            "context_data": self.context_data,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CopilotMessage":
        """Create from dictionary."""
        role = data.get("role")
        if isinstance(role, str):
            role = MessageRole(role)
        
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            session_id=data.get("session_id", ""),
            role=role or MessageRole.USER,
            message=data.get("message", ""),
            context_data=data.get("context_data"),
            timestamp=timestamp or datetime.utcnow()
        )
