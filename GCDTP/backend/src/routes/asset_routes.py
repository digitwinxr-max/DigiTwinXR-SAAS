"""Asset API routes."""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database.config import get_db
from ..schemas.asset import (
    AssetCreate,
    AssetUpdate,
    AssetResponse,
    AssetListResponse,
    GeoJSONFeatureCollection,
)
from ..schemas.sensor import SensorListResponse
from ..services.asset_service import AssetService
from ..services.sensor_service import SensorService

router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("", response_model=AssetResponse, status_code=201)
def create_asset(
    asset_data: AssetCreate,
    db: Session = Depends(get_db)
):
    """Create a new asset."""
    service = AssetService(db)
    asset = service.create_asset(asset_data)
    return asset


@router.get("", response_model=AssetListResponse)
def get_assets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all assets with pagination."""
    service = AssetService(db)
    assets, total = service.get_assets(skip=skip, limit=limit)
    return AssetListResponse(items=assets, total=total)


@router.get("/geojson", response_model=GeoJSONFeatureCollection)
def get_assets_geojson(
    db: Session = Depends(get_db)
):
    """Get all assets as GeoJSON FeatureCollection.
    
    Returns a GeoJSON FeatureCollection with each asset as a Feature.
    """
    service = AssetService(db)
    features = service.get_assets_geojson()
    return GeoJSONFeatureCollection(features=features)


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(
    asset_id: UUID,
    db: Session = Depends(get_db)
):
    """Get an asset by ID."""
    service = AssetService(db)
    asset = service.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: UUID,
    asset_data: AssetUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing asset."""
    service = AssetService(db)
    asset = service.update_asset(asset_id, asset_data)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.delete("/{asset_id}", status_code=204)
def delete_asset(
    asset_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete an asset."""
    service = AssetService(db)
    success = service.delete_asset(asset_id)
    if not success:
        raise HTTPException(status_code=404, detail="Asset not found")
    return None


@router.get("/{asset_id}/sensors", response_model=SensorListResponse)
def get_asset_sensors(
    asset_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all sensors for a specific asset."""
    # First check if asset exists
    asset_service = AssetService(db)
    asset = asset_service.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Get sensors for this asset
    sensor_service = SensorService(db)
    sensors = sensor_service.get_sensors_by_asset(asset_id)
    return SensorListResponse(items=sensors, total=len(sensors))
