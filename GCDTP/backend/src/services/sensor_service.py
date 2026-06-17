"""Sensor service for business logic."""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..models.sensor import Sensor
from ..models.asset import Asset
from ..schemas.sensor import SensorCreate, SensorUpdate


class SensorService:
    """Service class for sensor operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_sensor(self, sensor_data: SensorCreate) -> Sensor:
        """Create a new sensor."""
        sensor = Sensor(
            asset_id=sensor_data.asset_id,
            name=sensor_data.name,
            sensor_type=sensor_data.sensor_type,
            unit=sensor_data.unit,
            description=sensor_data.description,
            status=sensor_data.status,
        )
        self.db.add(sensor)
        self.db.commit()
        self.db.refresh(sensor)
        return sensor

    def get_sensor(self, sensor_id: UUID) -> Optional[Sensor]:
        """Get a sensor by ID."""
        return self.db.query(Sensor).filter(Sensor.id == sensor_id).first()

    def get_sensors(self, skip: int = 0, limit: int = 100) -> tuple[List[Sensor], int]:
        """Get all sensors with pagination."""
        total = self.db.query(Sensor).count()
        sensors = self.db.query(Sensor).offset(skip).limit(limit).all()
        return sensors, total

    def update_sensor(self, sensor_id: UUID, sensor_data: SensorUpdate) -> Optional[Sensor]:
        """Update an existing sensor."""
        sensor = self.get_sensor(sensor_id)
        if not sensor:
            return None
        
        update_data = sensor_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(sensor, field, value)
        
        self.db.commit()
        self.db.refresh(sensor)
        return sensor

    def delete_sensor(self, sensor_id: UUID) -> bool:
        """Delete a sensor."""
        sensor = self.get_sensor(sensor_id)
        if not sensor:
            return False
        
        self.db.delete(sensor)
        self.db.commit()
        return True

    def get_sensors_by_asset(self, asset_id: UUID) -> List[Sensor]:
        """Get all sensors for a specific asset."""
        return self.db.query(Sensor).filter(Sensor.asset_id == asset_id).all()

    def asset_exists(self, asset_id: UUID) -> bool:
        """Check if an asset exists."""
        return self.db.query(Asset).filter(Asset.id == asset_id).first() is not None