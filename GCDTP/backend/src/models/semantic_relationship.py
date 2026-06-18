"""
Semantic Relationship Model

Represents semantic relationships between entities.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from dataclasses import dataclass, field


class RelationshipType(str, Enum):
    """Relationship types in the semantic layer."""
    RELATED_TO = "related_to"
    CAUSED_BY = "caused_by"
    DEPENDS_ON = "depends_on"
    DOCUMENTED_BY = "documented_by"
    OBSERVED_BY = "observed_by"
    GENERATED_BY = "generated_by"


@dataclass
class SemanticRelationship:
    """
    Semantic relationship between entities.
    
    Relationship types:
    - related_to: General relationship
    - caused_by: Causal relationship
    - depends_on: Dependency
    - documented_by: Documentation relationship
    - observed_by: Observation relationship
    - generated_by: Generation relationship
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_entity_id: str = ""
    target_entity_id: str = ""
    relationship_type: RelationshipType = RelationshipType.RELATED_TO
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "source_entity_id": self.source_entity_id,
            "target_entity_id": self.target_entity_id,
            "relationship_type": self.relationship_type.value if isinstance(self.relationship_type, Enum) else self.relationship_type,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SemanticRelationship":
        """Create from dictionary."""
        rel_type = data.get("relationship_type")
        if isinstance(rel_type, str):
            rel_type = RelationshipType(rel_type)
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            source_entity_id=data.get("source_entity_id", ""),
            target_entity_id=data.get("target_entity_id", ""),
            relationship_type=rel_type or RelationshipType.RELATED_TO,
            created_at=data.get("created_at", datetime.utcnow())
        )
