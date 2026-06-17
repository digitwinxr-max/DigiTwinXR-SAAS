"""Asset health Pydantic schemas."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class AssetHealthBase(BaseModel):
    """Base asset health schema."""
    health_score: int = Field(..., ge=0, le=100, description="Health score (0-100)")
    health_status: str = Field(..., description="HEALTHY, DEGRADED, CRITICAL")
    active_event_count: int = Field(default=0, ge=0, description="Count of active events")
    dependency_penalty: float = Field(default=0.0, ge=0, description="Penalty from dependencies")
    calculation_method: str = Field(default="RULE_BASED", description="Calculation method")


class AssetHealthResponse(AssetHealthBase):
    """Schema for asset health response."""
    id: UUID
    asset_id: UUID
    last_updated: datetime

    class Config:
        from_attributes = True


class AssetHealthWithAssetResponse(AssetHealthResponse):
    """Schema for asset health response with asset details."""
    asset_name: Optional[str] = None
    asset_type: Optional[str] = None


class AssetHealthListResponse(BaseModel):
    """Schema for list of asset health response."""
    items: List[AssetHealthWithAssetResponse]
    total: int


class HealthRecalculateResponse(BaseModel):
    """Schema for health recalculation response."""
    asset_id: UUID
    health_score: int
    health_status: str
    active_event_count: int
    dependency_penalty: float = 0.0
    message: str


class HealthSummaryResponse(BaseModel):
    """Schema for overall health summary."""
    total_assets: int
    healthy_count: int
    degraded_count: int
    critical_count: int
    average_health_score: float