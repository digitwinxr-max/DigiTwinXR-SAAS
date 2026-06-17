"""Recovery Simulation model."""
import enum
from datetime import datetime
from uuid import UUID
from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from .base import Base


class RecoveryType(str, enum.Enum):
    """Types of recovery strategies."""
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    STAGED = "staged"
    REROUTE = "reroute"


class RecoverySimulation(Base):
    """Recovery Simulation model for recovery strategies.
    
    Recovery simulations are linked to scenarios and provide
    different recovery strategies for failure events.
    """
    
    __tablename__ = "recovery_simulations"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=UUID)
    scenario_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey('scenarios.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    strategy_name = Column(String(255), nullable=False)
    recovery_type = Column(
        Enum(RecoveryType, name='recovery_type', create_type=False),
        nullable=False,
        default=RecoveryType.MANUAL
    )
    estimated_duration_minutes = Column(Integer, nullable=False, default=60)
    recovery_order = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    scenario = relationship("Scenario", backref="recovery_simulations")
    results = relationship(
        "RecoveryResult",
        back_populates="recovery_simulation",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return (
            f"<RecoverySimulation("
            f"id={self.id}, "
            f"strategy='{self.strategy_name}', "
            f"type={self.recovery_type})>"
        )


# Recovery restoration values
RECOVERY_VALUES = {
    RecoveryType.MANUAL: 20,
    RecoveryType.AUTOMATIC: 30,
    RecoveryType.STAGED: 15,  # per depth
    RecoveryType.REROUTE: 25,  # base value
}


# Risk levels
class RiskLevel(str, enum.Enum):
    """Risk levels for remaining risk assessment."""
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


def calculate_risk_level(health_score: float) -> RiskLevel:
    """Calculate risk level based on health score.
    
    Args:
        health_score: Asset health score (0-100)
        
    Returns:
        RiskLevel enum value
    """
    if health_score >= 90:
        return RiskLevel.NONE
    elif health_score >= 80:
        return RiskLevel.LOW
    elif health_score >= 60:
        return RiskLevel.MEDIUM
    elif health_score >= 40:
        return RiskLevel.HIGH
    else:
        return RiskLevel.CRITICAL
