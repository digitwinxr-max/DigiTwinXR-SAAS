"""
Knowledge Reference Model

Represents relationships between knowledge documents.
This is pure metadata - NO AI, NO embeddings.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


class RelationshipType(str, Enum):
    """Types of document relationships."""
    REFERENCES = "references"
    EXTENDS = "extends"
    SUPERSEDES = "supersedes"
    RELATED_TO = "related_to"


@dataclass
class KnowledgeReference:
    """
    Relationship between two knowledge documents.
    
    Defines knowledge graph structure.
    Read-only relationships.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_document_id: str = ""
    target_document_id: str = ""
    relationship_type: RelationshipType = RelationshipType.RELATED_TO
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "source_document_id": self.source_document_id,
            "target_document_id": self.target_document_id,
            "relationship_type": self.relationship_type.value if isinstance(self.relationship_type, Enum) else self.relationship_type,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeReference":
        """Create from dictionary."""
        rel_type = data.get("relationship_type")
        if isinstance(rel_type, str):
            rel_type = RelationshipType(rel_type)
        
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            source_document_id=data.get("source_document_id", ""),
            target_document_id=data.get("target_document_id", ""),
            relationship_type=rel_type or RelationshipType.RELATED_TO,
            created_at=created_at or datetime.utcnow()
        )
    
    def get_relationship_icon(self) -> str:
        """Get icon for relationship type."""
        icons = {
            RelationshipType.REFERENCES: "→",
            RelationshipType.EXTENDS: "↗",
            RelationshipType.SUPERSEDES: "↑",
            RelationshipType.RELATED_TO: "↔"
        }
        return icons.get(self.relationship_type, "↔")
