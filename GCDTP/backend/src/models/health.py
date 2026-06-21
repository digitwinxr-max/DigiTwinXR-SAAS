"""Asset health model - derived state from events and dependencies."""
from datetime import datetime
from uuid import UUID
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, CheckConstraint, Float
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from .base import Base


class AssetHealth(Base):
    """Asset health model - derived from active events and dependencies."""
    
    __tablename__ = "asset_health"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=UUID)
    asset_id = Column(PG_UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, unique=True)
    health_score = Column(Integer, nullable=False, default=100)
    health_status = Column(String(20), nullable=False, default="HEALTHY")
    active_event_count = Column(Integer, nullable=False, default=0)
    dependency_penalty = Column(Float, nullable=False, default=0.0)  # From related assets
    last_updated = Column(DateTime(timezone=True), default=datetime.utcnow)
    calculation_method = Column(String(50), nullable=False, default="RULE_BASED")
    
    # Relationship to asset
    asset = relationship("Asset", back_populates="health")
    
    __table_args__ = (
        CheckConstraint('health_score >= 0 AND health_score <= 100', name='check_health_score_range'),
    )
    
    def __repr__(self):
        return f"<AssetHealth {self.asset_id}: {self.health_status} ({self.health_score})>"
    
    @staticmethod
    def calculate_status(score: int) -> str:
        """Derive health status from health score.
        
        Args:
            score: Health score (0-100)
            
        Returns:
            HEALTHY (80-100), DEGRADED (40-79), CRITICAL (0-39)
        """
        if score >= 80:
            return "HEALTHY"
        elif score >= 40:
            return "DEGRADED"
        else:
            return "CRITICAL"
    
    @property
    def local_penalty(self) -> int:
        """Get the local event penalty (from active events only)."""
        return self.active_event_count * 10  # Simplified calculation
    
    @property
    def total_penalty(self) -> float:
        """Get total penalty including dependency penalties."""
        return self.local_penalty + self.dependency_penalty
    
    def update_from_events(self, critical_count: int, warning_count: int):
        """Update health based on event counts.
        
        This sets the base penalty from events. The final health score
        is calculated by HealthService which also subtracts dependency
        penalties.
        
        Args:
            critical_count: Number of active CRITICAL events
            warning_count: Number of active WARNING events
        """
        # Start at 100 and apply penalties
        score = 100
        score -= critical_count * 20  # CRITICAL = -20
        score -= warning_count * 10   # WARNING = -10
        
        # Store local penalty for reference
        self.active_event_count = critical_count + warning_count
        self.last_updated = datetime.utcnow()