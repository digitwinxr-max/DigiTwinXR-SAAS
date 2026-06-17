"""Scenario model for simulation engine."""
import enum
from datetime import datetime
from uuid import UUID
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from .base import Base


class ScenarioType(str, enum.Enum):
    """Types of scenarios."""
    FAILURE = "failure"
    RECOVERY = "recovery"
    MAINTENANCE = "maintenance"
    CUSTOM = "custom"


class ScenarioStatus(str, enum.Enum):
    """Status of a scenario."""
    DRAFT = "draft"
    COMPLETED = "completed"


class Scenario(Base):
    """Scenario model for failure/recovery simulations.
    
    Scenarios are completely isolated from live data. They create
    virtual events, propagations, and health calculations that
    only exist in memory during simulation.
    """
    
    __tablename__ = "scenarios"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=UUID)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    scenario_type = Column(
        Enum(ScenarioType, name='scenario_type', create_type=False),
        nullable=False,
        default=ScenarioType.FAILURE
    )
    root_asset_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey('assets.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    severity = Column(String(20), nullable=False, default="CRITICAL")
    status = Column(
        Enum(ScenarioStatus, name='scenario_status', create_type=False),
        nullable=False,
        default=ScenarioStatus.DRAFT
    )
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    root_asset = relationship("Asset", foreign_keys=[root_asset_id])
    results = relationship(
        "ScenarioResult",
        back_populates="scenario",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return (
            f"<Scenario("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"type={self.scenario_type}, "
            f"status={self.status})>"
        )
    
    @property
    def is_completed(self) -> bool:
        """Check if scenario has been executed."""
        return self.status == ScenarioStatus.COMPLETED
    
    @property
    def result_count(self) -> int:
        """Get number of results."""
        return len(self.results) if self.results else 0