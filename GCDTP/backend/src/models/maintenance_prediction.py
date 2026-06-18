"""
Maintenance Prediction Model

Deterministic failure probability prediction.
NO ML, NO neural networks, NO external AI.
"""

import uuid
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


class RiskLevel(str, Enum):
    """Risk levels for predictions."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class MaintenancePrediction:
    """
    Maintenance prediction record.
    
    Deterministic prediction using formula-based scoring.
    NO ML/AI - pure mathematical calculation.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    asset_id: str = ""
    prediction_date: datetime = field(default_factory=datetime.utcnow)
    failure_probability: float = 0.0
    predicted_health: float = 100.0
    risk_level: RiskLevel = RiskLevel.LOW
    recommended_action: Optional[str] = None
    confidence: Optional[float] = None
    
    # Factor breakdown for explainability
    health_degradation_factor: float = 0.0
    active_events_factor: float = 0.0
    measurement_anomalies_factor: float = 0.0
    maintenance_age_factor: float = 0.0
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "asset_id": self.asset_id,
            "prediction_date": self.prediction_date.isoformat() if isinstance(self.prediction_date, datetime) else self.prediction_date,
            "failure_probability": self.failure_probability,
            "predicted_health": self.predicted_health,
            "risk_level": self.risk_level.value if isinstance(self.risk_level, Enum) else self.risk_level,
            "recommended_action": self.recommended_action,
            "confidence": self.confidence,
            "health_degradation_factor": self.health_degradation_factor,
            "active_events_factor": self.active_events_factor,
            "measurement_anomalies_factor": self.measurement_anomalies_factor,
            "maintenance_age_factor": self.maintenance_age_factor,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MaintenancePrediction":
        """Create from dictionary."""
        risk_level = data.get("risk_level")
        if isinstance(risk_level, str):
            risk_level = RiskLevel(risk_level)
        
        prediction_date = data.get("prediction_date")
        if isinstance(prediction_date, str):
            prediction_date = datetime.fromisoformat(prediction_date.replace("Z", "+00:00"))
        
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            asset_id=data.get("asset_id", ""),
            prediction_date=prediction_date or datetime.utcnow(),
            failure_probability=data.get("failure_probability", 0.0),
            predicted_health=data.get("predicted_health", 100.0),
            risk_level=risk_level or RiskLevel.LOW,
            recommended_action=data.get("recommended_action"),
            confidence=data.get("confidence"),
            health_degradation_factor=data.get("health_degradation_factor", 0.0),
            active_events_factor=data.get("active_events_factor", 0.0),
            measurement_anomalies_factor=data.get("measurement_anomalies_factor", 0.0),
            maintenance_age_factor=data.get("maintenance_age_factor", 0.0),
            created_at=created_at or datetime.utcnow()
        )
    
    def get_risk_display(self) -> str:
        """Get human-readable risk level."""
        return self.risk_level.value if isinstance(self.risk_level, Enum) else self.risk_level
    
    def get_probability_display(self) -> str:
        """Get percentage display."""
        return f"{self.failure_probability:.1f}%"
    
    def get_confidence_display(self) -> str:
        """Get confidence display."""
        if self.confidence is None:
            return "N/A"
        return f"{self.confidence * 100:.0f}%"
