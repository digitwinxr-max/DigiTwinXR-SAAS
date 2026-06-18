"""
Semantic Tag Model

Represents semantic tags for platform entities.
"""

import uuid
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class SemanticTag:
    """
    Semantic tag for entities.
    
    Examples:
    - voltage, temperature, criticality
    - location, utility, substation
    - transformer, water, power
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_id: str = ""
    tag_name: str = ""
    tag_value: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "entity_id": self.entity_id,
            "tag_name": self.tag_name,
            "tag_value": self.tag_value,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SemanticTag":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            entity_id=data.get("entity_id", ""),
            tag_name=data.get("tag_name", ""),
            tag_value=str(data.get("tag_value", "")),
            created_at=data.get("created_at", datetime.utcnow())
        )


# Predefined tag categories
class TagCategory:
    """Common tag categories."""
    
    # Asset tags
    ASSET_TYPE = "asset_type"
    LOCATION = "location"
    UTILITY = "utility"
    CRITICALITY = "criticality"
    
    # Sensor tags
    MEASUREMENT_TYPE = "measurement_type"
    UNIT = "unit"
    FREQUENCY = "frequency"
    
    # Status tags
    HEALTH_STATUS = "health_status"
    OPERATIONAL_STATUS = "operational_status"
    
    # Domain tags
    POWER = "power"
    WATER = "water"
    GAS = "gas"
    TRANSPORT = "transport"


# Common tag values
class TagValues:
    """Common tag values."""
    
    # Utilities
    ELECTRICITY = "electricity"
    WATER = "water"
    GAS = "gas"
    HEATING = "heating"
    COOLING = "cooling"
    
    # Locations
    INDOOR = "indoor"
    OUTDOOR = "outdoor"
    UNDERGROUND = "underground"
    
    # Criticality
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    
    # Status
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
