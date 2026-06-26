"""
Cognitive Session Model

Cognitive Twin session for tracking questions and context.
"""

import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CognitiveSession:
    """
    Cognitive Session record.
    
    Tracks a conversation session with the Cognitive Twin.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: Optional[str] = None
    asset_id: Optional[str] = None
    user_id: Optional[str] = None
    context_summary: Optional[str] = None
    query_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "asset_id": self.asset_id,
            "user_id": self.user_id,
            "context_summary": self.context_summary,
            "query_count": self.query_count,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CognitiveSession":
        """Create from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        
        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description"),
            asset_id=data.get("asset_id"),
            user_id=data.get("user_id"),
            context_summary=data.get("context_summary"),
            query_count=data.get("query_count", 0),
            created_at=created_at or datetime.utcnow(),
            updated_at=updated_at or datetime.utcnow()
        )
    
    def increment_query_count(self):
        """Increment query count and update timestamp."""
        self.query_count += 1
        self.updated_at = datetime.utcnow()
