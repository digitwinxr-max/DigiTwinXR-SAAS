"""Sensor SQLAlchemy model."""
import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database.config import Base


class Sensor(Base):
    """Sensor database model."""
    __tablename__ = "sensors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    sensor_type = Column(String(100), nullable=False)
    unit = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship to asset
    asset = relationship("Asset", back_populates="sensors")

    # Relationship to measurements
    measurements = relationship("Measurement", back_populates="sensor", cascade="all, delete-orphan")

    # Relationship to threshold rules
    threshold_rules = relationship("ThresholdRule", back_populates="sensor", cascade="all, delete-orphan")
