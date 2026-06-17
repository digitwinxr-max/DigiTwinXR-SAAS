"""Measurement API routes."""
from typing import Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database.config import get_db
from ..schemas.measurement import (
    MeasurementCreate,
    MeasurementResponse,
    MeasurementListResponse,
)
from ..services.measurement_service import MeasurementService

router = APIRouter(prefix="/measurements", tags=["measurements"])


@router.post("", response_model=MeasurementResponse, status_code=201)
def create_measurement(
    measurement_data: MeasurementCreate,
    db: Session = Depends(get_db)
):
    """Create a new measurement."""
    service = MeasurementService(db)
    
    # Check if sensor exists
    if not service.sensor_exists(measurement_data.sensor_id):
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    measurement = service.create_measurement(measurement_data)
    return measurement


@router.get("", response_model=MeasurementListResponse)
def get_measurements(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=10000),
    sensor_id: Optional[UUID] = Query(None, description="Filter by sensor ID"),
    start_time: Optional[datetime] = Query(None, description="Filter by start time"),
    end_time: Optional[datetime] = Query(None, description="Filter by end time"),
    db: Session = Depends(get_db)
):
    """Get all measurements with optional filtering."""
    service = MeasurementService(db)
    measurements, total = service.get_measurements(
        skip=skip,
        limit=limit,
        sensor_id=sensor_id,
        start_time=start_time,
        end_time=end_time,
    )
    return MeasurementListResponse(items=measurements, total=total)


@router.get("/{measurement_id}", response_model=MeasurementResponse)
def get_measurement(
    measurement_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a measurement by ID."""
    service = MeasurementService(db)
    measurement = service.get_measurement(measurement_id)
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")
    return measurement


@router.delete("/{measurement_id}", status_code=204)
def delete_measurement(
    measurement_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a measurement."""
    service = MeasurementService(db)
    success = service.delete_measurement(measurement_id)
    if not success:
        raise HTTPException(status_code=404, detail="Measurement not found")
    return None


# Sensor-measurement relationship endpoint
@router.get("/sensor/{sensor_id}", response_model=MeasurementListResponse)
def get_measurements_by_sensor(
    sensor_id: UUID,
    limit: int = Query(100, ge=1, le=10000),
    start_time: Optional[datetime] = Query(None, description="Filter by start time"),
    end_time: Optional[datetime] = Query(None, description="Filter by end time"),
    db: Session = Depends(get_db)
):
    """Get all measurements for a specific sensor."""
    service = MeasurementService(db)
    
    # Check if sensor exists
    if not service.sensor_exists(sensor_id):
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    measurements = service.get_measurements_by_sensor(
        sensor_id=sensor_id,
        limit=limit,
        start_time=start_time,
        end_time=end_time,
    )
    return MeasurementListResponse(items=measurements, total=len(measurements))