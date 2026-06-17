# ADR-0008: Measurement Engine

## Status

Accepted

## Context

GCDTP sensors collect measurement data over time. The system needs to store and retrieve these measurements for visualization and analysis.

## Decision

We will implement a Measurement Engine that:

1. **Measurements belong to sensors** - Each measurement is linked to a sensor
2. **Foreign key relationship** - Cascade delete when sensor is deleted
3. **Quality tracking** - Each measurement has a quality indicator
4. **Time-series support** - Measurements include timestamps for ordering
5. **Filtering** - Support filtering by time range and sensor

## Database Schema

```sql
CREATE TABLE measurements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sensor_id UUID NOT NULL REFERENCES sensors(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    value DOUBLE PRECISION NOT NULL,
    quality VARCHAR(20) NOT NULL DEFAULT 'good',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_measurements_sensor_id ON measurements(sensor_id);
CREATE INDEX idx_measurements_timestamp ON measurements(timestamp);
CREATE INDEX idx_measurements_quality ON measurements(quality);
```

## API Design

### Measurement Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /measurements | Create a new measurement |
| GET | /measurements | List measurements (with filtering) |
| GET | /measurements/{id} | Get measurement by ID |
| DELETE | /measurements/{id} | Delete a measurement |

### Sensor-Measurement Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /sensors/{id}/measurements | Get measurements for a sensor |
| GET | /measurements/sensor/{sensor_id} | Alternative endpoint |

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| limit | int | Max results (default: 100) |
| start_time | datetime | Filter measurements after this time |
| end_time | datetime | Filter measurements before this time |
| sensor_id | UUID | Filter by specific sensor |

## Measurement Schema

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| sensor_id | UUID | Foreign key to sensors |
| timestamp | TIMESTAMP | When measurement was taken |
| value | DOUBLE | Measurement value |
| quality | VARCHAR | good, uncertain, bad |
| created_at | TIMESTAMP | Record creation time |

## Quality Values

- **good**: Measurement is reliable
- **uncertain**: Measurement may have issues
- **bad**: Measurement is unreliable

## Visualization

### Line Chart Component

- Uses Recharts library
- Displays timestamp on X-axis, value on Y-axis
- Tooltip shows timestamp, value, and quality
- Responsive container for mobile/desktop

### Chart Features

- No live updates (static data)
- No streaming
- No aggregation
- No statistics (mean, min, max, etc.)

## Decision Made By

GCDTP Core Team

## Date

2026-06-16

## Consequences

### Positive
- Simple time-series storage
- Quality tracking for data reliability
- Time range filtering for large datasets
- Line chart visualization for sensor data
- Cascade delete prevents orphaned measurements

### Negative
- Basic storage without TimescaleDB optimizations
- No compression for historical data
- Limited to float values

### Neutral
- Ready for future statistical analysis
- Ready for future alerting/thresholds

## Future Considerations

- TimescaleDB for time-series optimization
- Threshold rules and alerting
- Statistical functions (mean, min, max, stddev)
- Data aggregation (hourly, daily averages)
- Measurement events/notifications
