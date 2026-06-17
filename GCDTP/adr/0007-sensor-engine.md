# ADR-0007: Sensor Engine

## Status

Accepted

## Context

GCDTP assets can be equipped with sensors for monitoring various physical properties. The system needs to track sensors as separate entities that are associated with assets.

## Decision

We will implement a Sensor Engine that:

1. **Sensors are separate entities** - Sensors exist independently but are linked to assets
2. **Foreign key relationship** - Each sensor belongs to exactly one asset
3. **Cascade delete** - Deleting an asset deletes all its sensors
4. **Sensor types** - Predefined types: temperature, pressure, humidity, vibration, flow, voltage
5. **Status tracking** - Sensors have status: active, inactive, maintenance

## Database Schema

```sql
CREATE TABLE sensors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    sensor_type VARCHAR(100) NOT NULL,
    unit VARCHAR(50),
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sensors_asset_id ON sensors(asset_id);
CREATE INDEX idx_sensors_sensor_type ON sensors(sensor_type);
CREATE INDEX idx_sensors_status ON sensors(status);
```

## API Design

### Sensor Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /sensors | Create a new sensor |
| GET | /sensors | List all sensors (paginated) |
| GET | /sensors/{id} | Get sensor by ID |
| PUT | /sensors/{id} | Update a sensor |
| DELETE | /sensors/{id} | Delete a sensor |

### Asset-Sensor Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /assets/{id}/sensors | Get all sensors for an asset |
| GET | /sensors/asset/{asset_id} | Get sensors by asset ID |

## Sensor Schema

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| asset_id | UUID | Foreign key to assets |
| name | VARCHAR(255) | Sensor name |
| sensor_type | VARCHAR(100) | Type of sensor |
| unit | VARCHAR(50) | Measurement unit |
| description | TEXT | Description |
| status | VARCHAR(50) | active/inactive/maintenance |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update time |

## Sensor Types

- **temperature** - Temperature measurements
- **pressure** - Pressure measurements
- **humidity** - Humidity measurements
- **vibration** - Vibration measurements
- **flow** - Flow rate measurements
- **voltage** - Electrical voltage measurements

## Decision Made By

GCDTP Core Team

## Date

2026-06-16

## Consequences

### Positive
- Clear separation between assets and sensors
- Cascade delete prevents orphaned sensors
- Standard CRUD operations for sensors
- Asset-centric queries via /assets/{id}/sensors
- Supports all common sensor types

### Negative
- Additional complexity in data model
- Requires FK validation on sensor creation

### Neutral
- Sensors are visualization-only (no measurements/telemetry)
- Ready for future measurement storage

## Future Considerations

- Measurement storage (TimescaleDB)
- Sensor data telemetry
- Alerting based on sensor readings
- Sensor calibration tracking
