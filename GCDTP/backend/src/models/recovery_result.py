"""Recovery Result model."""
from datetime import datetime
from uuid import UUID
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from .base import Base


class RecoveryResult(Base):
    """Recovery Result model for storing recovery simulation results.
    
    Results capture the before/after health states and calculated improvements.
    """
    
    __tablename__ = "recovery_results"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=UUID)
    recovery_simulation_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey('recovery_simulations.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    asset_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey('assets.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    before_health = Column(Float, nullable=False, default=0.0)
    after_health = Column(Float, nullable=False, default=0.0)
    improvement = Column(Float, nullable=False, default=0.0)
    recovery_depth = Column(Integer, nullable=False, default=0)
    remaining_risk = Column(String(20), nullable=False, default="NONE")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    recovery_simulation = relationship("RecoverySimulation", back_populates="results")
    asset = relationship("Asset")
    
    def __repr__(self):
        return (
            f"<RecoveryResult("
            f"id={self.id}, "
            f"asset={self.asset_id}, "
            f"improvement={self.improvement})>"
        )
    
    @property
    def is_improved(self) -> bool:
        """Check if recovery improved health."""
        return self.improvement > 0
    
    @property
    def is_restored(self) -> bool:
        """Check if asset is fully restored (>= 90)."""
        return self.after_health >= 90
    
    @property
    def risk_indicator(self) -> str:
        """Get risk indicator based on remaining risk."""
        risk_colors = {
            "NONE": "#22c55e",
            "LOW": "#84cc16",
            "MEDIUM": "#eab308",
            "HIGH": "#f97316",
            "CRITICAL": "#ef4444",
        }
        return risk_colors.get(self.remaining_risk, "#6b7280")
