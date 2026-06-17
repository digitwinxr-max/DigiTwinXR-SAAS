"""Scenario Result model for simulation results."""
from datetime import datetime
from uuid import UUID
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from .base import Base


class ScenarioResult(Base):
    """Scenario Result model for storing simulation results.
    
    Results are persisted in the database but are isolated from
    live data. They represent predicted health vs actual health
    at the time of simulation.
    """
    
    __tablename__ = "scenario_results"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=UUID)
    scenario_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey('scenarios.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    asset_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey('assets.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    predicted_health = Column(Float, nullable=False, default=100.0)
    current_health = Column(Float, nullable=False, default=100.0)
    delta_health = Column(Float, nullable=False, default=0.0)
    propagation_depth = Column(Integer, nullable=False, default=0, index=True)
    relationship_path = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    scenario = relationship("Scenario", back_populates="results")
    asset = relationship("Asset")
    
    def __repr__(self):
        return (
            f"<ScenarioResult("
            f"id={self.id}, "
            f"scenario={self.scenario_id}, "
            f"asset={self.asset_id}, "
            f"predicted={self.predicted_health}, "
            f"delta={self.delta_health})>"
        )
    
    @property
    def is_degraded(self) -> bool:
        """Check if simulation predicted degradation."""
        return self.delta_health < 0
    
    @property
    def is_improved(self) -> bool:
        """Check if simulation predicted improvement."""
        return self.delta_health > 0
    
    @property
    def severity_indicator(self) -> str:
        """Get severity indicator based on predicted health."""
        if self.predicted_health >= 80:
            return "HEALTHY"
        elif self.predicted_health >= 40:
            return "DEGRADED"
        else:
            return "CRITICAL"