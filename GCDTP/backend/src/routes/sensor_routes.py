"""Sensor API routes."""
from typing import Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database.config import get_db
from ..schemas.sensor import (
    SensorCreate,
    SensorUpdate,
    SensorResponse,
    SensorListResponse,
)
from ..schemas.measurement import MeasurementListResponse
from ..services.sensor_service import SensorService

router = APIRouter(prefix="/sensors", tags=["sensors"])


# Asset-sensor relationship endpoint (must be before /{sensor_id})
@router.get("/asset/{asset_id}", response_model=SensorListResponse)
def get_sensors_by_asset(
    asset_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all sensors for a specific asset."""
    service = SensorService(db)
    sensors = service.get_sensors_by_asset(asset_id)
    return SensorListResponse(items=sensors, total=len(sensors))


@router.post("", response_model=SensorResponse, status_code=201)
def create_sensor(
    sensor_data: SensorCreate,
    db: Session = Depends(get_db)
):
    """Create a new sensor."""
    service = SensorService(db)
    
    # Check if asset exists
    if not service.asset_exists(sensor_data.asset_id):
        raise HTTPException(status_code=404, detail="Asset not found")
    
    sensor = service.create_sensor(sensor_data)
    return sensor


@router.get("", response_model=SensorListResponse)
def get_sensors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all sensors with pagination."""
    service = SensorService(db)
    sensors, total = service.get_sensors(skip=skip, limit=limit)
    return SensorListResponse(items=sensors, total=total)


@router.get("/{sensor_id}", response_model=SensorResponse)
def get_sensor(
    sensor_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a sensor by ID."""
    service = SensorService(db)
    sensor = service.get_sensor(sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return sensor


@router.put("/{sensor_id}", response_model=SensorResponse)
def update_sensor(
    sensor_id: UUID,
    sensor_data: SensorUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing sensor."""
    service = SensorService(db)
    sensor = service.update_sensor(sensor_id, sensor_data)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return sensor


@router.delete("/{sensor_id}", status_code=204)
def delete_sensor(
    sensor_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a sensor."""
    service = SensorService(db)
    success = service.delete_sensor(sensor_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return None


@router.get("/{sensor_id}/measurements", response_model=MeasurementListResponse)
def get_sensor_measurements(
    sensor_id: UUID,
    limit: int = Query(100, ge=1, le=10000),
    start_time: Optional[datetime] = Query(None, description="Filter by start time"),
    end_time: Optional[datetime] = Query(None, description="Filter by end time"),
    db: Session = Depends(get_db)
):
    """Get all measurements for a specific sensor."""
    from ..schemas.measurement import MeasurementListResponse
    from ..services.measurement_service import MeasurementService
    
    # First check if sensor exists
    service = SensorService(db)
    sensor = service.get_sensor(sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    # Get measurements for this sensor
    measurement_service = MeasurementService(db)
    measurements = measurement_service.get_measurements_by_sensor(
        sensor_id=sensor_id,
        limit=limit,
        start_time=start_time,
        end_time=end_time,
    )
    return MeasurementListResponse(items=measurements, total=len(measurements))