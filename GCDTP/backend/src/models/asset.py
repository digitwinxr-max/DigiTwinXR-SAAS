"""Asset SQLAlchemy model."""
import uuid
from sqlalchemy import Column, String, Text, Float, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID, DOUBLE_PRECISION
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

# Try to import Geometry, fall back to JSON for non-PostgreSQL databases
try:
    from geoalchemy2 import Geometry
    HAS_GEOMETRY = True
except ImportError:
    HAS_GEOMETRY = False


def get_geometry_column():
    """Get the appropriate geometry column based on database support."""
    if HAS_GEOMETRY:
        return Geometry(geometry_type='POINT', srid=4326, nullable=True)
    return Column(JSON, nullable=True)


class Asset(Base):
    """Asset database model with spatial support."""
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    asset_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    longitude = Column(DOUBLE_PRECISION, nullable=True)
    latitude = Column(DOUBLE_PRECISION, nullable=True)
    location = get_geometry_column()
    status = Column(String(50), nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship to sensors
    sensors = relationship("Sensor", back_populates="asset", cascade="all, delete-orphan")

    # Relationship to health
    health = relationship("AssetHealth", back_populates="asset", uselist=False, cascade="all, delete-orphan")
