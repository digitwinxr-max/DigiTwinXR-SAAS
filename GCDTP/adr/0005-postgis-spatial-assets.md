# ADR-0005: PostGIS Spatial Assets

## Status

Accepted

## Context

The GCDTP Asset Engine needs to support geographic/spatial data for assets. Assets can have geographic coordinates (longitude/latitude) and the system should support spatial queries and GeoJSON output for integration with mapping applications.

## Decision

We will use PostGIS to extend the PostgreSQL database with spatial capabilities:

1. **PostGIS Extension** - Enable PostGIS for spatial data types and functions
2. **Geometry Column** - Add `location` column with `GEOMETRY(Point, 4326)` type (WGS84)
3. **Auto-population** - Use database triggers to automatically populate geometry from longitude/latitude
4. **Spatial Index** - Create GIST index on geometry column for efficient spatial queries
5. **Backend Support** - Use GeoAlchemy2 for ORM support with PostGIS

## Database Schema

```sql
-- Enable extensions
CREATE EXTENSION IF NOT EXISTS postgis;

-- Assets table with geometry
CREATE TABLE assets (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    asset_type VARCHAR(100) NOT NULL,
    description TEXT,
    longitude DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    location GEOMETRY(Point, 4326),
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Spatial index
CREATE INDEX idx_assets_location ON assets USING GIST(location);

-- Trigger for auto-populating geometry
CREATE OR REPLACE FUNCTION update_asset_location()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.longitude IS NOT NULL AND NEW.latitude IS NOT NULL THEN
        NEW.location := ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326);
    ELSE
        NEW.location := NULL;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';
```

## API Design

### Existing Endpoints (Unchanged)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /assets | Create asset |
| GET | /assets | List assets |
| GET | /assets/{id} | Get asset |
| PUT | /assets/{id} | Update asset |
| DELETE | /assets/{id} | Delete asset |

### New Endpoint

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /assets/geojson | Get all assets as GeoJSON FeatureCollection |

### GeoJSON Response Format

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "id": "uuid",
      "geometry": {
        "type": "Point",
        "coordinates": [longitude, latitude]
      },
      "properties": {
        "name": "Asset Name",
        "asset_type": "sensor",
        "status": "active"
      }
    }
  ]
}
```

## Implementation Details

### Backend Helper Functions

```python
class AssetService:
    @staticmethod
    def create_point(longitude: float, latitude: float) -> WKTElement:
        """Create PostGIS POINT from coordinates."""
        
    @staticmethod
    def update_point(asset: Asset) -> None:
        """Update asset geometry from coordinates."""
```

### Coordinate Schema

Assets expose coordinates through the standard JSON structure:

```json
{
  "longitude": -122.4194,
  "latitude": 37.7749
}
```

The internal geometry (WKB) is **never exposed** to API consumers.

## Decision Made By

GCDTP Core Team

## Date

2026-06-16

## Consequences

### Positive
- Standard spatial data support using PostGIS
- Efficient spatial queries with GIST index
- GeoJSON output for mapping integration
- Coordinates auto-synced to geometry via triggers
- SRID 4326 (WGS84) standard for GPS coordinates

### Negative
- Requires PostGIS-enabled PostgreSQL
- Migration from non-spatial requires data transformation
- Additional complexity in testing (need PostGIS or mocks)

### Neutral
- Geometry stored in WKB format internally
- GeoJSON coordinates use [lon, lat] order per GeoJSON spec

## Future Considerations

- Spatial queries (within radius, bounding box)
- Time-series spatial data (TimescaleDB integration)
- Map visualization frontend
