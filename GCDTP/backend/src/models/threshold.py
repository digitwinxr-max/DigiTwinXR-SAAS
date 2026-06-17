"""Threshold rule model."""
from datetime import datetime
from uuid import UUID
from sqlalchemy import Column, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from ..database.config import Base


class ThresholdRule(Base):
    """Threshold rule model for measurement evaluation."""
    
    __tablename__ = "threshold_rules"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=UUID)
    sensor_id = Column(PG_UUID(as_uuid=True), ForeignKey("sensors.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(255), nullable=False)
    rule_type = Column(String(50), nullable=False, default="range")
    warning_min = Column(Float, nullable=True)
    warning_max = Column(Float, nullable=True)
    critical_min = Column(Float, nullable=True)
    critical_max = Column(Float, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationship to sensor
    sensor = relationship("Sensor", back_populates="threshold_rules")
    
    def evaluate(self, value: float) -> str:
        """Evaluate a measurement value against this threshold rule.
        
        Returns:
            'CRITICAL' if value < critical_min OR value > critical_max
            'WARNING' if value < warning_min OR value > warning_max
            'OK' otherwise
        """
        # Check critical thresholds first
        if self.critical_min is not None and value < self.critical_min:
            return "CRITICAL"
        if self.critical_max is not None and value > self.critical_max:
            return "CRITICAL"
        
        # Check warning thresholds
        if self.warning_min is not None and value < self.warning_min:
            return "WARNING"
        if self.warning_max is not None and value > self.warning_max:
            return "WARNING"
        
        return "OK"
    
    def to_evaluation_result(self, measurement_id: UUID) -> dict:
        """Convert rule to evaluation result format."""
        return {
            "rule_id": str(self.id),
            "sensor_id": str(self.sensor_id) if self.sensor_id else None,
            "rule_name": self.name,
        }