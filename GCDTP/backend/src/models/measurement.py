"""Measurement SQLAlchemy model."""
import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base


class Measurement(Base):
    """Measurement database model."""
    __tablename__ = "measurements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sensor_id = Column(UUID(as_uuid=True), ForeignKey("sensors.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now())
    value = Column(Float, nullable=False)
    quality = Column(String(20), nullable=False, default="good")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to sensor
    sensor = relationship("Sensor", back_populates="measurements")