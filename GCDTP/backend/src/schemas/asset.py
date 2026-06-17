"""Asset Pydantic schemas."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    """Geographic coordinates schema."""
    longitude: float
    latitude: float


class AssetBase(BaseModel):
    """Base asset schema."""
    name: str = Field(..., min_length=1, max_length=255)
    asset_type: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    status: str = Field(default="active", max_length=50)


class AssetCreate(AssetBase):
    """Schema for creating an asset."""
    pass


class AssetUpdate(BaseModel):
    """Schema for updating an asset."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    asset_type: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    status: Optional[str] = Field(None, max_length=50)


class AssetResponse(AssetBase):
    """Schema for asset response."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssetListResponse(BaseModel):
    """Schema for list of assets response."""
    items: List[AssetResponse]
    total: int


class GeoJSONFeature(BaseModel):
    """GeoJSON Feature for a single asset."""
    type: str = "Feature"
    id: str
    geometry: dict
    properties: dict


class GeoJSONFeatureCollection(BaseModel):
    """GeoJSON FeatureCollection for assets."""
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]
