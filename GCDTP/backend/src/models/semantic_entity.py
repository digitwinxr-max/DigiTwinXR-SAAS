"""
Semantic Entity Model

Represents semantic metadata for platform objects.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List
from dataclasses import dataclass, field


class EntityType(str, Enum):
    """Entity types in the semantic layer."""
    ASSET = "asset"
    SENSOR = "sensor"
    MEASUREMENT = "measurement"
    EVENT = "event"
    HEALTH = "health"
    RELATIONSHIP = "relationship"
    SCENARIO = "scenario"
    RECOVERY = "recovery"
    TIMELINE = "timeline"
    WORK_ORDER = "work_order"
    DOCUMENT = "document"


@dataclass
class SemanticEntity:
    """
    Semantic entity representing metadata about platform objects.
    
    This model ONLY adds semantic descriptions and cross-domain references.
    It does NOT change existing engines.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: EntityType = EntityType.ASSET
    entity_id: str = ""
    name: str = ""
    description: Optional[str] = None
    category: Optional[str] = None
    ontology_class: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "entity_type": self.entity_type.value if isinstance(self.entity_type, Enum) else self.entity_type,
            "entity_id": self.entity_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "ontology_class": self.ontology_class,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SemanticEntity":
        """Create from dictionary."""
        entity_type = data.get("entity_type")
        if isinstance(entity_type, str):
            entity_type = EntityType(entity_type)
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            entity_type=entity_type or EntityType.ASSET,
            entity_id=data.get("entity_id", ""),
            name=data.get("name", ""),
            description=data.get("description"),
            category=data.get("category"),
            ontology_class=data.get("ontology_class"),
            created_at=data.get("created_at", datetime.utcnow()),
            updated_at=data.get("updated_at", datetime.utcnow())
        )
