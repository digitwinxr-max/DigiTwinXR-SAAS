"""Sensor Pydantic schemas."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class SensorBase(BaseModel):
    """Base sensor schema."""
    name: str = Field(..., min_length=1, max_length=255)
    sensor_type: str = Field(..., min_length=1, max_length=100)
    unit: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    status: str = Field(default="active", max_length=50)


class SensorCreate(SensorBase):
    """Schema for creating a sensor."""
    asset_id: UUID


class SensorUpdate(BaseModel):
    """Schema for updating a sensor."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    sensor_type: Optional[str] = Field(None, min_length=1, max_length=100)
    unit: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    status: Optional[str] = Field(None, max_length=50)


class SensorResponse(SensorBase):
    """Schema for sensor response."""
    id: UUID
    asset_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SensorWithAssetResponse(SensorResponse):
    """Schema for sensor response with asset info."""
    asset_name: Optional[str] = None
    asset_type: Optional[str] = None


class SensorListResponse(BaseModel):
    """Schema for list of sensors response."""
    items: List[SensorResponse]
    total: int