"""Measurement Pydantic schemas."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class MeasurementBase(BaseModel):
    """Base measurement schema."""
    value: float = Field(..., description="Measurement value")
    quality: str = Field(default="good", description="Data quality: good, uncertain, bad")


class MeasurementCreate(MeasurementBase):
    """Schema for creating a measurement."""
    sensor_id: UUID
    timestamp: Optional[datetime] = None


class MeasurementResponse(MeasurementBase):
    """Schema for measurement response."""
    id: UUID
    sensor_id: UUID
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class MeasurementWithSensorResponse(MeasurementResponse):
    """Schema for measurement response with sensor info."""
    sensor_name: Optional[str] = None
    sensor_type: Optional[str] = None


class MeasurementListResponse(BaseModel):
    """Schema for list of measurements response."""
    items: List[MeasurementResponse]
    total: int