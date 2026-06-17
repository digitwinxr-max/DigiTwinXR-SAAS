"""Threshold rule Pydantic schemas."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class ThresholdRuleBase(BaseModel):
    """Base threshold rule schema."""
    name: str = Field(..., min_length=1, max_length=255, description="Rule name")
    rule_type: str = Field(default="range", description="Type: range, static")
    warning_min: Optional[float] = Field(None, description="Warning threshold minimum")
    warning_max: Optional[float] = Field(None, description="Warning threshold maximum")
    critical_min: Optional[float] = Field(None, description="Critical threshold minimum")
    critical_max: Optional[float] = Field(None, description="Critical threshold maximum")
    is_active: bool = Field(default=True, description="Whether rule is active")


class ThresholdRuleCreate(ThresholdRuleBase):
    """Schema for creating a threshold rule."""
    sensor_id: Optional[UUID] = Field(None, description="Sensor ID (null for global rules)")
    
    @field_validator("rule_type")
    @classmethod
    def validate_rule_type(cls, v):
        if v not in ["range", "static"]:
            raise ValueError("rule_type must be 'range' or 'static'")
        return v


class ThresholdRuleUpdate(BaseModel):
    """Schema for updating a threshold rule."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    rule_type: Optional[str] = None
    warning_min: Optional[float] = None
    warning_max: Optional[float] = None
    critical_min: Optional[float] = None
    critical_max: Optional[float] = None
    is_active: Optional[bool] = None
    
    @field_validator("rule_type")
    @classmethod
    def validate_rule_type(cls, v):
        if v is not None and v not in ["range", "static"]:
            raise ValueError("rule_type must be 'range' or 'static'")
        return v


class ThresholdRuleResponse(ThresholdRuleBase):
    """Schema for threshold rule response."""
    id: UUID
    sensor_id: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True


class ThresholdRuleListResponse(BaseModel):
    """Schema for list of threshold rules response."""
    items: List[ThresholdRuleResponse]
    total: int


class EvaluationInput(BaseModel):
    """Schema for evaluation input."""
    measurement_id: UUID
    sensor_id: UUID
    value: float


class EvaluationResult(BaseModel):
    """Schema for evaluation result."""
    status: str  # OK, WARNING, CRITICAL
    rule_id: str
    sensor_id: str
    rule_name: Optional[str] = None
    message: Optional[str] = None