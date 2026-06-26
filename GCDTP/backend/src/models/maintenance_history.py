"""
Maintenance History Model

Records maintenance work history for analysis.
"""

import uuid
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


class MaintenanceType(str, Enum):
    """Types of maintenance."""
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    PREDICTIVE = "predictive"
    EMERGENCY = "emergency"
    INSPECTION = "inspection"


@dataclass
class MaintenanceHistory:
    """
    Maintenance history record.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    asset_id: str = ""
    work_order_id: Optional[str] = None
    maintenance_type: MaintenanceType = MaintenanceType.PREVENTIVE
    maintenance_date: datetime = field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    cost: Optional[float] = None
    duration_hours: Optional[float] = None
    performed_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "asset_id": self.asset_id,
            "work_order_id": self.work_order_id,
            "maintenance_type": self.maintenance_type.value if isinstance(self.maintenance_type, Enum) else self.maintenance_type,
            "maintenance_date": self.maintenance_date.isoformat() if isinstance(self.maintenance_date, datetime) else self.maintenance_date,
            "notes": self.notes,
            "cost": self.cost,
            "duration_hours": self.duration_hours,
            "performed_by": self.performed_by,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MaintenanceHistory":
        """Create from dictionary."""
        maintenance_type = data.get("maintenance_type")
        if isinstance(maintenance_type, str):
            maintenance_type = MaintenanceType(maintenance_type)
        
        maintenance_date = data.get("maintenance_date")
        if isinstance(maintenance_date, str):
            maintenance_date = datetime.fromisoformat(maintenance_date.replace("Z", "+00:00"))
        
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            asset_id=data.get("asset_id", ""),
            work_order_id=data.get("work_order_id"),
            maintenance_type=maintenance_type or MaintenanceType.PREVENTIVE,
            maintenance_date=maintenance_date or datetime.utcnow(),
            notes=data.get("notes"),
            cost=data.get("cost"),
            duration_hours=data.get("duration_hours"),
            performed_by=data.get("performed_by"),
            created_at=created_at or datetime.utcnow()
        )
    
    def get_type_display(self) -> str:
        """Get human-readable maintenance type."""
        names = {
            MaintenanceType.PREVENTIVE: "Preventive",
            MaintenanceType.CORRECTIVE: "Corrective",
            MaintenanceType.PREDICTIVE: "Predictive",
            MaintenanceType.EMERGENCY: "Emergency",
            MaintenanceType.INSPECTION: "Inspection"
        }
        return names.get(self.maintenance_type, "Unknown")
