"""Event Pydantic schemas."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class EventBase(BaseModel):
    """Base event schema."""
    event_type: str = Field(default="THRESHOLD_VIOLATION", description="Event type")
    severity: str = Field(..., description="OK, WARNING, CRITICAL")
    message: str = Field(..., description="Event message")
    value: Optional[float] = Field(None, description="Measurement value that triggered event")
    status: str = Field(default="ACTIVE", description="ACTIVE or RESOLVED")


class EventCreate(BaseModel):
    """Schema for creating an event."""
    sensor_id: UUID
    asset_id: UUID
    event_type: str = Field(default="THRESHOLD_VIOLATION")
    severity: str = Field(..., description="OK, WARNING, CRITICAL")
    message: str
    value: Optional[float] = None
    threshold_rule_id: Optional[UUID] = None
    timestamp: Optional[datetime] = None


class EventResponse(EventBase):
    """Schema for event response."""
    id: UUID
    sensor_id: UUID
    asset_id: UUID
    threshold_rule_id: Optional[UUID]
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class EventWithDetailsResponse(EventResponse):
    """Schema for event response with sensor and asset details."""
    sensor_name: Optional[str] = None
    sensor_type: Optional[str] = None
    asset_name: Optional[str] = None
    rule_name: Optional[str] = None


class EventListResponse(BaseModel):
    """Schema for list of events response."""
    items: List[EventResponse]
    total: int


class EventResolveRequest(BaseModel):
    """Schema for resolving an event."""
    resolution_notes: Optional[str] = Field(None, description="Optional notes about the resolution")


class EvaluationResultInput(BaseModel):
    """Schema for evaluation result from threshold engine."""
    status: str  # OK, WARNING, CRITICAL
    rule_id: str
    sensor_id: str
    rule_name: Optional[str] = None
    message: Optional[str] = None


class MeasurementInput(BaseModel):
    """Schema for measurement input when creating event from evaluation."""
    id: UUID
    sensor_id: UUID
    value: float
    timestamp: datetime