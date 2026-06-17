"""Measurement service for business logic.

Note: This service is fully compatible with TimescaleDB hypertables.
The existing queries leverage the hypertable's time-based partitioning
and the optimized indexes (sensor_id, timestamp DESC) automatically.
No changes required to support TimescaleDB.
"""
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models.measurement import Measurement
from ..models.sensor import Sensor
from ..schemas.measurement import MeasurementCreate
from ..events import emit, EventType


class MeasurementService:
    """Service class for measurement operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_measurement(self, measurement_data: MeasurementCreate) -> Measurement:
        """Create a new measurement."""
        measurement = Measurement(
            sensor_id=measurement_data.sensor_id,
            timestamp=measurement_data.timestamp or datetime.utcnow(),
            value=measurement_data.value,
            quality=measurement_data.quality,
        )
        self.db.add(measurement)
        self.db.commit()
        self.db.refresh(measurement)
        
        # Emit measurement.created event
        emit(
            event_type=EventType.MEASUREMENT_CREATED,
            source="MeasurementService",
            payload={
                "measurement_id": str(measurement.id),
                "value": measurement.value,
                "quality": measurement.quality,
            },
            sensor_id=measurement.sensor_id,
        )
        
        return measurement

    def get_measurement(self, measurement_id: UUID) -> Optional[Measurement]:
        """Get a measurement by ID."""
        return self.db.query(Measurement).filter(Measurement.id == measurement_id).first()

    def get_measurements(
        self,
        skip: int = 0,
        limit: int = 100,
        sensor_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> tuple[List[Measurement], int]:
        """Get all measurements with optional filtering."""
        query = self.db.query(Measurement)

        # Apply filters
        if sensor_id:
            query = query.filter(Measurement.sensor_id == sensor_id)
        if start_time:
            query = query.filter(Measurement.timestamp >= start_time)
        if end_time:
            query = query.filter(Measurement.timestamp <= end_time)

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        measurements = query.order_by(desc(Measurement.timestamp)).offset(skip).limit(limit).all()

        return measurements, total

    def delete_measurement(self, measurement_id: UUID) -> bool:
        """Delete a measurement."""
        measurement = self.get_measurement(measurement_id)
        if not measurement:
            return False

        self.db.delete(measurement)
        self.db.commit()
        return True

    def get_measurements_by_sensor(
        self,
        sensor_id: UUID,
        limit: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Measurement]:
        """Get all measurements for a specific sensor."""
        query = self.db.query(Measurement).filter(Measurement.sensor_id == sensor_id)

        if start_time:
            query = query.filter(Measurement.timestamp >= start_time)
        if end_time:
            query = query.filter(Measurement.timestamp <= end_time)

        return query.order_by(desc(Measurement.timestamp)).limit(limit).all()

    def sensor_exists(self, sensor_id: UUID) -> bool:
        """Check if a sensor exists."""
        return self.db.query(Sensor).filter(Sensor.id == sensor_id).first() is not None