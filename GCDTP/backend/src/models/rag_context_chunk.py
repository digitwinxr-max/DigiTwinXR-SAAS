"""
RAG Context Chunk Model

Represents a retrieved context chunk for audit purposes.
These are audit records only - NO operational writes.
"""

import uuid
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


class SourceType(str, Enum):
    """Source types for RAG context chunks."""
    SEMANTIC = "semantic"
    HEALTH = "health"
    EVENT = "event"
    TIMELINE = "timeline"
    LOGBOOK = "logbook"
    KNOWLEDGE = "knowledge"
    ASSET = "asset"
    SENSOR = "sensor"


@dataclass
class RAGContextChunk:
    """
    RAG context chunk audit record.
    
    Stores retrieved context for explainability.
    This is read-only audit - no operational modifications.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query_id: str = ""
    source_type: SourceType = SourceType.ASSET
    source_id: Optional[str] = None
    content: str = ""
    relevance_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "query_id": self.query_id,
            "source_type": self.source_type.value if isinstance(self.source_type, Enum) else self.source_type,
            "source_id": self.source_id,
            "content": self.content,
            "relevance_score": self.relevance_score,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RAGContextChunk":
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
            source_type=source_type or SourceType.ASSET,
            source_id=data.get("source_id"),
            content=data.get("content", ""),
            relevance_score=data.get("relevance_score", 0.0),
            created_at=created_at or datetime.utcnow()
        )
