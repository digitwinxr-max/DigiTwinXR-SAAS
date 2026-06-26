"""
Cognitive Query Model

Cognitive Twin query record.
"""

import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CognitiveQuery:
    """
    Cognitive Query record.
    
    Represents a question asked to the Cognitive Twin.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    question: str = ""
    answer: Optional[str] = None
    confidence: float = 0.0
    explanation: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "question": self.question,
            "answer": self.answer,
            "confidence": self.confidence,
            "explanation": self.explanation,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CognitiveQuery":
        """Create from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            session_id=data.get("session_id", ""),
            question=data.get("question", ""),
            answer=data.get("answer"),
            confidence=data.get("confidence", 0.0),
            explanation=data.get("explanation"),
            created_at=created_at or datetime.utcnow()
        )
    
    def get_confidence_display(self) -> str:
        """Get confidence as percentage."""
        return f"{self.confidence * 100:.0f}%"
