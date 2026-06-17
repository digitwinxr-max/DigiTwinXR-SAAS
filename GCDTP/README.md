# GCDTP

> Generic Component-Driven Template Project

## Overview

GCDTP is a clean, extensible project template designed to bootstrap new applications with a structured architecture. The core of this implementation is the **Asset Engine** - a CRUD system for managing spatial assets.

## Core Features

### Asset Engine

Complete CRUD operations for spatial assets:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /assets | Create a new asset |
| GET | /assets | List all assets |
| GET | /assets/{id} | Get asset by ID |
| PUT | /assets/{id} | Update an asset |
| DELETE | /assets/{id} | Delete an asset |
| GET | /assets/geojson | Get all assets as GeoJSON |
| GET | /assets/{id}/sensors | Get sensors for an asset |

### Asset Schema

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| name | VARCHAR(255) | Asset name |
| asset_type | VARCHAR(100) | Type of asset |
| description | TEXT | Description |
| longitude | FLOAT | Geographic longitude |
| latitude | FLOAT | Geographic latitude |
| location | GEOMETRY(Point, 4326) | PostGIS geometry |
| status | VARCHAR(50) | Asset status |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update |

### Sensor Engine

Sensors are linked to assets and can be of various types:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /sensors | Create a new sensor |
| GET | /sensors | List all sensors |
| GET | /sensors/{id} | Get sensor by ID |
| PUT | /sensors/{id} | Update a sensor |
| DELETE | /sensors/{id} | Delete a sensor |
| GET | /sensors/asset/{id} | Get sensors by asset |
| GET | /sensors/{id}/measurements | Get measurements for sensor |

### Sensor Types

- temperature, pressure, humidity, vibration, flow, voltage

### Sensor Schema

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| asset_id | UUID | Foreign key to assets |
| name | VARCHAR(255) | Sensor name |
| sensor_type | VARCHAR(100) | Type of sensor |
| unit | VARCHAR(50) | Measurement unit |
| description | TEXT | Description |
| status | VARCHAR(50) | active/inactive/maintenance |

### Measurement Engine

Measurements store time-series data from sensors:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /measurements | Create a new measurement |
| GET | /measurements | List measurements (with filtering) |
| GET | /measurements/{id} | Get measurement by ID |
| DELETE | /measurements/{id} | Delete a measurement |
| GET | /measurements/sensor/{id} | Get measurements by sensor |

### Measurement Query Parameters

- `limit` - Max results (default: 100)
- `start_time` - Filter by start time
- `end_time` - Filter by end time
- `sensor_id` - Filter by sensor

### Measurement Schema

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| sensor_id | UUID | Foreign key to sensors |
| timestamp | TIMESTAMP | When measurement was taken |
| value | DOUBLE | Measurement value |
| quality | VARCHAR | good/uncertain/bad |

### Quality Values

- **good** - Reliable measurement
- **uncertain** - May have issues
- **bad** - Unreliable measurement

## Repository Structure

```
GCDTP/
├── adr/           # Architecture Decision Records
├── backend/       # FastAPI backend with asset endpoints
├── database/      # PostgreSQL/PostGIS migrations
├── frontend/      # React frontend for asset management
├── tests/         # Test suites and fixtures
├── docker-compose.yml
├── MASTER_CONTEXT.md
└── ROADMAP.md
```

## Quick Start

### Using Docker Compose

```bash
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8080
- API Docs: http://localhost:8080/docs

### Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8080
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Spatial Features

- **PostGIS Integration**: Assets store geographic data using PostGIS geometry
- **Auto-sync**: Geometry automatically populated from longitude/latitude
- **GeoJSON Export**: `/assets/geojson` endpoint returns GeoJSON FeatureCollection
- **Spatial Index**: GIST index on geometry for efficient queries
- **Map Viewer**: Leaflet-based map displaying assets with popups

## Time-Series Storage

- **TimescaleDB Hypertable**: Measurements stored in TimescaleDB for performance
- **Automatic Partitioning**: Data partitioned by time intervals
- **Compression**: Old data automatically compressed (90% storage savings)
- **Scalability**: Handles millions of measurements per day
- **No API changes**: Existing endpoints work unchanged

## Threshold Engine

Rule-based evaluation layer for measurements:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /thresholds | Create a threshold rule |
| GET | /thresholds | List rules (with filtering) |
| GET | /thresholds/{id} | Get rule by ID |
| PUT | /thresholds/{id} | Update a rule |
| DELETE | /thresholds/{id} | Delete a rule |
| GET | /thresholds/sensor/{id} | Get rules for sensor |
| POST | /thresholds/evaluate | Evaluate a measurement |

### Evaluation Result

| Status | Meaning |
|--------|---------|
| OK | Value within acceptable range |
| WARNING | Value outside warning thresholds |
| CRITICAL | Value outside critical thresholds |

### Threshold Rule Schema

| Field | Type | Description |
|-------|------|-------------|
| name | VARCHAR | Rule name |
| sensor_id | UUID | Sensor (null for global rules) |
| warning_min/max | DOUBLE | Warning thresholds |
| critical_min/max | DOUBLE | Critical thresholds |
| is_active | BOOLEAN | Rule active status |

## Event Engine

System memory layer for threshold violations:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /events/manual | Create event manually |
| POST | /events/from-evaluation | Create event from evaluation |
| GET | /events | List events (with filtering) |
| GET | /events/active | List only active events |
| GET | /events/{id} | Get event by ID |
| PATCH | /events/{id}/resolve | Mark event as resolved |
| GET | /events/sensor/{id} | Get events for sensor |
| GET | /events/asset/{id} | Get events for asset |

### Event Fields

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| sensor_id | UUID | FK to sensors |
| asset_id | UUID | FK to assets (derived from sensor) |
| severity | VARCHAR | WARNING, CRITICAL |
| status | VARCHAR | ACTIVE, RESOLVED |
| value | DOUBLE | Measurement value |
| message | TEXT | Event message |

### Event Creation Rules

- OK status → No event created
- WARNING/CRITICAL → Event created with links to sensor, asset, and rule

## Health Engine

Derived state layer for asset health based on active events:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health/summary | Overall health statistics |
| GET | /health/assets | All asset health records |
| GET | /health/assets/{id} | Single asset health |
| POST | /health/recalculate/{id} | Manual recalculation |
| POST | /health/recalculate-all | Recalculate all |

### Health Calculation Rules

| Event Type | Penalty |
|------------|---------|
| CRITICAL | -20 |
| WARNING | -10 |

### Health Status Thresholds

| Score | Status | Color |
|-------|--------|-------|
| 80-100 | HEALTHY | Green |
| 40-79 | DEGRADED | Yellow |
| 0-39 | CRITICAL | Red |

### Event Integration

Health recalculation is triggered on:
- Event creation (decreases health)
- Event resolution (improves health)

## GeoPortal v2 - Operational Intelligence

The GeoPortal is an operational intelligence dashboard showing real-time system state:

### Data Layers

| Layer | Source | Description |
|-------|--------|-------------|
| Assets | /assets/geojson | Asset locations with health-based colors |
| Events | /events/active | Active events as pulsing markers |
| Health | /health/assets | Health status per asset |

### Health Colors

| Status | Color | Score Range |
|--------|-------|-------------|
| HEALTHY | Green | 80-100 |
| DEGRADED | Orange | 40-79 |
| CRITICAL | Red | 0-39 |

### Event Markers

| Severity | Color | Style |
|----------|-------|-------|
| WARNING | Yellow | Pulsing ring |
| CRITICAL | Red | Pulsing ring |

### Popup Content

Asset popups show:
- Asset name and type
- Health status and score
- Sensor count
- Active event summary (WARNING/CRITICAL counts)

## Event System Architecture

GCDTP implements a centralized event propagation system for consistent, traceable event handling.

### Event Types

All event types are defined in `backend/src/events/event_types.py`:

| Type | Description |
|------|-------------|
| measurement.created | New measurement recorded |
| threshold.evaluated | Threshold rule evaluated |
| event.created | New event created |
| event.resolved | Event resolved |
| health.updated | Asset health recalculated |
| asset.updated | Asset created or updated |

### Event Payload Schema

All events follow a standard structure:

```json
{
  "event_id": "uuid",
  "event_type": "string",
  "timestamp": "datetime",
  "source": "string",
  "correlation_id": "uuid (optional)",
  "asset_id": "uuid (optional)",
  "sensor_id": "uuid (optional)",
  "payload": {}
}
```

### Backend Event Dispatcher

Single entry point for all event emissions:

```python
from backend.src.events import emit, EventType

emit(
    event_type=EventType.EVENT_CREATED,
    source="EventService",
    payload={"event_id": str(event.id)},
    asset_id=event.asset_id,
)
```

### Frontend Event Client

Standardized event handling on client:

```javascript
import { useSystemEvents, EVENT_TYPES } from './hooks/useSystemEvents';

useSystemEvents(
  [EVENT_TYPES.EVENT_CREATED, EVENT_TYPES.HEALTH_UPDATED],
  (event) => {
    // Handle event
  }
);
```

### Event Consistency Rules

- **Immutable**: Events cannot be modified after creation
- **Deduplication**: Duplicate event_ids are ignored
- **Out of Order**: Events may arrive out of order
- **Graceful Degradation**: Missing events don't break UI

## Asset Relationship Graph

The Asset Relationship Graph enables hierarchical and associative relationships between assets.

### Relationship Types

| Type | Description | Direction |
|------|-------------|-----------|
| contains | Parent contains child (hierarchical) | Directed |
| connected_to | Assets are physically/logically connected | Symmetric |
| feeds | Parent provides input/energy to child | Directed |
| monitors | Parent measures/monitors child | Directed |
| controls | Parent commands/controls child | Directed |

### Database Table

```sql
asset_relationships (
    id UUID PRIMARY KEY,
    parent_asset_id UUID REFERENCES assets(id),
    child_asset_id UUID REFERENCES assets(id),
    relationship_type ENUM,
    created_at TIMESTAMP
)
```

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| POST /relationships | Create relationship |
| GET /relationships | List relationships |
| DELETE /relationships/{id} | Delete relationship |
| GET /relationships/graph/{asset_id} | Get hierarchical graph |
| GET /relationships/children/{asset_id} | Get direct children |
| GET /relationships/parents/{asset_id} | Get direct parents |

### Graph Output

```json
{
  "asset_id": "xxx",
  "asset_name": "Site Alpha",
  "children": [
    {
      "asset_id": "yyy",
      "asset_name": "Building A",
      "relationship_type": "contains",
      "children": []
    }
  ]
}
```

## Cascading Failure Engine

Propagates failure impacts through the Asset Relationship Graph.

### Propagation Rules

| Relationship | Direction | Propagation Type |
|--------------|-----------|------------------|
| contains | Upward | child_failure |
| feeds | Downstream | downstream_failure |
| controls | Downstream | dependency_impact |
| connected_to | Bidirectional | dependency_impact |
| monitors | None | Informational only |

### Propagation Behavior

- **MAX_DEPTH = 3** (configurable)
- Cycles are prevented using visited set
- Propagations auto-cleanup when event is resolved
- WARNING and CRITICAL events trigger propagation

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| GET /propagation/event/{id} | Get propagations for event |
| GET /propagation/asset/{id} | Get impacts on asset |
| GET /propagation/chain/{id} | Get impact chain |
| GET /propagation/impacts | List all impacts |

## Dependency-Aware Health

Asset health reflects both local events and dependency impacts from related assets.

### Health Formula

```
Health = 100 - local_events - dependencies

where:
  local_events = CRITICAL × 20 + WARNING × 10
  dependencies = Σ((100 - source_health) × weight × decay)
```

### Relationship Weights

| Relationship | Weight | Effect |
|-------------|--------|--------|
| feeds | 0.7 | High impact |
| controls | 0.6 | Medium-high |
| contains | 0.5 | Medium |
| connected_to | 0.3 | Low |
| monitors | 0.0 | None |

### Depth Decay

| Depth | Decay | Example |
|-------|-------|---------|
| 1 | 1.0 | Direct dependency |
| 2 | 0.5 | Through one hop |
| 3 | 0.25 | Through two hops |

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| GET /health/tree/{id} | Health tree with dependencies |
| GET /health/contributors/{id} | What affects this asset |
| GET /health/network | Network-wide summary |
| POST /health/recalculate-network | Trigger recalculation |

## Frontend Pages

| Page | Route | Description |
|------|-------|-------------|
| **GeoPortal** | /geoportal | **Operational intelligence dashboard (default)** |
| Asset List | /assets | List all assets |
| Asset Details | /assets/:id | View asset details |
| Create Asset | /assets/create | Create new asset |
| Sensor List | /sensors | List all sensors |
| Sensor Details | /sensors/:id | View sensor details |
| Create Sensor | /sensors/create | Create new sensor |
| Sensor Measurements | /sensors/:id/measurements | View sensor measurements with chart |
| Sensor Thresholds | /sensors/:id/thresholds | View sensor threshold rules |
| Measurement List | /measurements | List all measurements |
| Measurement Details | /measurements/:id | View measurement details |
| Threshold List | /thresholds | List all threshold rules |
| Create Threshold | /thresholds/create | Create new threshold rule |
| Event List | /events | List all events |
| Active Events | /events/active | View active events with summary |
| Event Details | /events/:id | View event details and resolve |
| Health Dashboard | /health | View all asset health status |
| Asset Hierarchy | /hierarchy | Visualize asset relationships |
| Impact Chain | /impacts | Cascading failure propagation |
| Network Health | /network | Dependency-aware health |
| Scenario Studio | /scenarios | What-if simulations |
| Map | /map | Map viewer (deprecated) |

## Documentation

- [Master Context](MASTER_CONTEXT.md) - Project vision, goals, and constraints
- [Roadmap](ROADMAP.md) - Planned features and milestones
- [ADR-0004](adr/0004-asset-centric-architecture.md) - Asset-centric architecture
- [ADR-0005](adr/0005-postgis-spatial-assets.md) - PostGIS spatial assets
- [ADR-0006](adr/0006-leaflet-map-viewer.md) - Leaflet map viewer

## Architecture Decisions

All significant architectural decisions are documented in the `adr/` folder:
- ADR-0004: Asset-Centric Architecture
- ADR-0005: PostGIS Spatial Assets
- ADR-0006: Leaflet Map Viewer
- ADR-0007: Sensor Engine
- ADR-0008: Measurement Engine
- ADR-0009: TimescaleDB Hypertable Foundation
- ADR-0010: Threshold Engine
- ADR-0011: Event Engine
- ADR-0013: Health Engine
- ADR-0014: GeoPortal v2 - Operational Intelligence
- ADR-0015: System-Wide Event Propagation Hardening
- ADR-0016: Asset Relationship Graph Engine
- ADR-0017: Cascading Failure Engine
- ADR-0018: Dependency-Aware Health Propagation
- ADR-0019: Scenario Simulation Engine
- ADR-0020: Recovery Simulation Engine
- ADR-0021: Resilience Analysis Engine
- ADR-0022: Network Topology Engine
- ADR-0023: Routing, Flow, and Resilience Engines
- ADR-0024: Extensible Simulation Architecture
- ADR-0025: Operational Timeline Engine
- ADR-0026: Work Order Engine
- ADR-0027: Document Management Engine
- ADR-0028: Identity & Access Management
- ADR-0029: Cesium 3D Visualization Layer
- ADR-0030: Node-RED Integration Layer
- ADR-0031: EMQX MQTT Integration Layer
- ADR-0032: GeoServer Integration Layer
- ADR-0033: Graph Intelligence Layer (Neo4j)
