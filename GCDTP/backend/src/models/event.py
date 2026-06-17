"""Event model for storing threshold violations and system events."""
from datetime import datetime
from uuid import UUID
from sqlalchemy import Column, String, Text, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from ..database.config import Base


class Event(Base):
    """Event database model for threshold violations."""
    
    __tablename__ = "events"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=UUID)
    sensor_id = Column(PG_UUID(as_uuid=True), ForeignKey("sensors.id", ondelete="CASCADE"), nullable=False)
    asset_id = Column(PG_UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(100), nullable=False, default="THRESHOLD_VIOLATION")
    severity = Column(String(20), nullable=False)  # OK, WARNING, CRITICAL
    message = Column(Text, nullable=False)
    value = Column(Float, nullable=True)
    threshold_rule_id = Column(PG_UUID(as_uuid=True), ForeignKey("threshold_rules.id", ondelete="SET NULL"), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    status = Column(String(20), nullable=False, default="ACTIVE")  # ACTIVE, RESOLVED
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    sensor = relationship("Sensor", foreign_keys=[sensor_id])
    asset = relationship("Asset", foreign_keys=[asset_id])
    threshold_rule = relationship("ThresholdRule", foreign_keys=[threshold_rule_id])
    
    def __repr__(self):
        return f"<Event {self.id}: {self.event_type} - {self.severity}>"
    
    def resolve(self):
        """Mark event as resolved."""
        self.status = "RESOLVED"
        return self