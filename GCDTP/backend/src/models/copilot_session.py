"""
Cognitive Copilot Session Model

Represents a copilot conversation session.
This is read-only AI context - NO LLM integration yet.
"""

import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CopilotSession:
    """
    Cognitive Copilot session.
    
    Stores conversation context for AI explanations.
    This is read-only - no operational modifications.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_name: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity_at: datetime = field(default_factory=datetime.utcnow)
    message_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "session_name": self.session_name,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "last_activity_at": self.last_activity_at.isoformat() if isinstance(self.last_activity_at, datetime) else self.last_activity_at,
            "message_count": self.message_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CopilotSession":
        """Create from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        
        last_activity_at = data.get("last_activity_at")
        if isinstance(last_activity_at, str):
            last_activity_at = datetime.fromisoformat(last_activity_at.replace("Z", "+00:00"))
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            session_name=data.get("session_name", ""),
            created_at=created_at or datetime.utcnow(),
            last_activity_at=last_activity_at or datetime.utcnow(),
            message_count=data.get("message_count", 0)
        )
