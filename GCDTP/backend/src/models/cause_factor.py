"""
Cause Factor Model

Contributing factors for Root Cause Analysis.
"""

import uuid
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


class FactorType(str, Enum):
    """Types of contributing factors."""
    MEASUREMENT = "measurement"
    EVENT = "event"
    HEALTH = "health"
    RELATIONSHIP = "relationship"
    TIMELINE = "timeline"
    LOGBOOK = "logbook"
    KNOWLEDGE = "knowledge"


@dataclass
class CauseFactor:
    """
    Cause Factor record.
    
    Represents a contributing factor to a root cause.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str = ""
    factor_type: FactorType = FactorType.MEASUREMENT
    reference_id: Optional[str] = None
    weight: float = 0.0
    description: str = ""
    evidence: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "factor_type": self.factor_type.value if isinstance(self.factor_type, Enum) else self.factor_type,
            "reference_id": self.reference_id,
            "weight": self.weight,
            "description": self.description,
            "evidence": self.evidence,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CauseFactor":
        """Create from dictionary."""
        factor_type = data.get("factor_type")
        if isinstance(factor_type, str):
            factor_type = FactorType(factor_type)
        
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            analysis_id=data.get("analysis_id", ""),
            factor_type=factor_type or FactorType.MEASUREMENT,
            reference_id=data.get("reference_id"),
            weight=data.get("weight", 0.0),
            description=data.get("description", ""),
            evidence=data.get("evidence"),
            created_at=created_at or datetime.utcnow()
        )
    
    def get_weight_display(self) -> str:
        """Get percentage display."""
        return f"{self.weight * 100:.0f}%"
    
    def get_factor_type_display(self) -> str:
        """Get human-readable factor type."""
        names = {
            FactorType.MEASUREMENT: "Measurement",
            FactorType.EVENT: "Event",
            FactorType.HEALTH: "Health",
            FactorType.RELATIONSHIP: "Relationship",
            FactorType.TIMELINE: "Timeline",
            FactorType.LOGBOOK: "Logbook",
            FactorType.KNOWLEDGE: "Knowledge"
        }
        return names.get(self.factor_type, "Unknown")
