"""
RAG Answer Model

Represents a RAG answer for audit purposes.
These are audit records only - NO operational writes.
"""

import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class RAGAnswer:
    """
    RAG answer audit record.
    
    Stores generated answer for accountability.
    This is read-only audit - no operational modifications.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query_id: str = ""
    answer: str = ""
    model_name: str = "template"
    confidence: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "query_id": self.query_id,
            "answer": self.answer,
            "model_name": self.model_name,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RAGAnswer":
        """Create from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            query_id=data.get("query_id", ""),
            answer=data.get("answer", ""),
            model_name=data.get("model_name", "template"),
            confidence=data.get("confidence"),
            created_at=created_at or datetime.utcnow()
        )
