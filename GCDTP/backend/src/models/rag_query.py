"""
RAG Query Model

Represents a RAG query for audit purposes.
These are audit records only - NO operational writes.
"""

import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class RAGQuery:
    """
    RAG query audit record.
    
    Stores query for traceability and audit.
    This is read-only audit - no operational modifications.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: Optional[str] = None
    query: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "query": self.query,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RAGQuery":
        """Create from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            session_id=data.get("session_id"),
            query=data.get("query", ""),
            created_at=created_at or datetime.utcnow()
        )
