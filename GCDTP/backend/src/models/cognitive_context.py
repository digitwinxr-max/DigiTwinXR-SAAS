"""
Cognitive Context Model

Context sources for Cognitive Twin queries.
"""

import uuid
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


class SourceType(str, Enum):
    """Source types for cognitive context."""
    SEMANTIC = "semantic"
    TIMELINE = "timeline"
    LOGBOOK = "logbook"
    KNOWLEDGE = "knowledge"
    RAG = "rag"
    PREDICTION = "prediction"
    ROOT_CAUSE = "root_cause"
    AGENT = "agent"
    HEALTH = "health"
    EVENT = "event"


@dataclass
class CognitiveContext:
    """
    Cognitive Context record.
    
    Represents context retrieved from a platform engine.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query_id: str = ""
    source_type: SourceType = SourceType.SEMANTIC
    reference_id: Optional[str] = None
    weight: float = 0.0
    summary: str = ""
    detail: Optional[str] = None
    relevance_score: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "query_id": self.query_id,
            "source_type": self.source_type.value if isinstance(self.source_type, Enum) else self.source_type,
            "reference_id": self.reference_id,
            "weight": self.weight,
            "summary": self.summary,
            "detail": self.detail,
            "relevance_score": self.relevance_score,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CognitiveContext":
        """Create from dictionary."""
        source_type = data.get("source_type")
        if isinstance(source_type, str):
            source_type = SourceType(source_type)
        
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            query_id=data.get("query_id", ""),
            source_type=source_type or SourceType.SEMANTIC,
            reference_id=data.get("reference_id"),
            weight=data.get("weight", 0.0),
            summary=data.get("summary", ""),
            detail=data.get("detail"),
            relevance_score=data.get("relevance_score"),
            created_at=created_at or datetime.utcnow()
        )
    
    def get_source_display(self) -> str:
        """Get human-readable source name."""
        names = {
            SourceType.SEMANTIC: "Semantic Layer",
            SourceType.TIMELINE: "Timeline Engine",
            SourceType.LOGBOOK: "Digital Logbook",
            SourceType.KNOWLEDGE: "Knowledge Repository",
            SourceType.RAG: "RAG Engine",
            SourceType.PREDICTION: "Predictive Maintenance",
            SourceType.ROOT_CAUSE: "Root Cause Analysis",
            SourceType.AGENT: "AI Agent",
            SourceType.HEALTH: "Health Engine",
            SourceType.EVENT: "Event Engine"
        }
        return names.get(self.source_type, "Unknown")
