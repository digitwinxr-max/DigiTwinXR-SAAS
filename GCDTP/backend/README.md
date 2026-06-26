# Backend

This directory contains the backend services and application logic built with FastAPI.

## Structure

```
backend/
├── src/
│   ├── database/      # Database configuration
│   ├── models/        # SQLAlchemy models (with PostGIS support)
│   ├── schemas/       # Pydantic schemas
│   ├── routes/        # API route definitions
│   ├── services/      # Business logic (geometry helpers)
│   └── main.py       # Application entry point
├── tests/             # Backend-specific tests
├── Dockerfile         # Container configuration
└── requirements.txt    # Python dependencies
```

## API Endpoints

### Asset Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /assets | Create a new asset |
| GET | /assets | List all assets (paginated) |
| GET | /assets/geojson | Get all assets as GeoJSON FeatureCollection |
| GET | /assets/{id} | Get asset by ID |
| PUT | /assets/{id} | Update an asset |
| DELETE | /assets/{id} | Delete an asset |
| GET | /assets/{id}/sensors | Get sensors for an asset |

### Sensor Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /sensors | Create a new sensor |
| GET | /sensors | List all sensors (paginated) |
| GET | /sensors/{id} | Get sensor by ID |
| PUT | /sensors/{id} | Update a sensor |
| DELETE | /sensors/{id} | Delete a sensor |
| GET | /sensors/asset/{asset_id} | Get sensors by asset ID |
| GET | /sensors/{id}/measurements | Get measurements for sensor |

### Measurement Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /measurements | Create a new measurement |
| GET | /measurements | List measurements (paginated) |
| GET | /measurements/{id} | Get measurement by ID |
| DELETE | /measurements/{id} | Delete a measurement |
| GET | /measurements/sensor/{sensor_id} | Get measurements by sensor |

### Measurement Query Parameters

- `limit` - Max results (default: 100, max: 10000)
- `start_time` - Filter by start time (ISO 8601)
- `end_time` - Filter by end time (ISO 8601)
- `sensor_id` - Filter by sensor ID

### Threshold Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /thresholds | Create a threshold rule |
| GET | /thresholds | List all rules (paginated) |
| GET | /thresholds/{id} | Get rule by ID |
| PUT | /thresholds/{id} | Update a rule |
| DELETE | /thresholds/{id} | Delete a rule |
| GET | /thresholds/sensor/{id} | Get rules for sensor |
| POST | /thresholds/evaluate | Evaluate a measurement |

### Evaluation Request/Response

**Request:**
```json
{
  "sensor_id": "uuid",
  "value": 25.5,
  "measurement_id": "uuid"
}
```

**Response:**
```json
{
  "status": "OK|WARNING|CRITICAL",
  "rule_id": "uuid",
  "sensor_id": "uuid",
  "rule_name": "Rule Name",
  "message": "Value 25.5 triggered WARNING threshold"
}
```

### Event Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /events/manual | Create event manually |
| POST | /events/from-evaluation | Create event from threshold evaluation |
| GET | /events | List events (paginated) |
| GET | /events/active | List only active events |
| GET | /events/{id} | Get event by ID |
| PATCH | /events/{id}/resolve | Mark event as resolved |
| GET | /events/sensor/{id} | Get events for sensor |
| GET | /events/asset/{id} | Get events for asset |

### Event Creation Rules

- OK status → No event created
- WARNING/CRITICAL → Event created with links to sensor, asset, and rule

### Event Query Parameters

- `status` - Filter by ACTIVE or RESOLVED
- `severity` - Filter by WARNING or CRITICAL
- `sensor_id` - Filter by sensor
- `asset_id` - Filter by asset
- `limit` - Max results (default: 100)

### Health Endpoints

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

| Score | Status |
|-------|--------|
| 80-100 | HEALTHY |
| 40-79 | DEGRADED |
| 0-39 | CRITICAL |

### System Health Endpoint

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |

## Spatial Features

### Helper Functions

```python
# Create PostGIS geometry from coordinates
AssetService.create_point(longitude, latitude)

# Update asset geometry from longitude/latitude
AssetService.update_point(asset)
```

### GeoJSON Endpoint

`GET /assets/geojson` returns a GeoJSON FeatureCollection:

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

## Getting Started

### Local Development

```bash
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8080
```

### Docker

```bash
docker build -t gcdtp-backend ./backend
docker run -p 8080:8080 gcdtp-backend
```

## Dependencies

- FastAPI - Web framework
- SQLAlchemy - ORM
- PostgreSQL with TimescaleDB - Time-series database
- GeoAlchemy2 - PostGIS integration
- Pydantic - Data validation
- Uvicorn - ASGI server

## TimescaleDB Hypertable

Measurements are stored as a TimescaleDB hypertable for optimal time-series performance:

- **Automatic partitioning** by 1-day time intervals
- **Compression** of chunks older than 7 days
- **Optimized indexes**: `(sensor_id, timestamp DESC)` and `(timestamp DESC)`
- **Retention policies** available for automatic data cleanup

The hypertable is compatible with all existing API endpoints - no code changes required.

## Event System

GCDTP implements a centralized event propagation system with standardized event types and a single dispatcher.

### Event Types

All event types are defined in `src/events/event_types.py`:

```python
from backend.src.events import EventType

# Available event types
EventType.MEASUREMENT_CREATED   # New measurement recorded
EventType.THRESHOLD_EVALUATED   # Threshold rule evaluated
EventType.EVENT_CREATED         # New event created
EventType.EVENT_RESOLVED        # Event resolved
EventType.HEALTH_UPDATED        # Asset health recalculated
EventType.ASSET_UPDATED         # Asset created or updated
```

### Event Dispatcher

Single entry point for all event emissions:

```python
from backend.src.events import emit

# Emit an event
emit(
    event_type=EventType.EVENT_CREATED,
    source="EventService",
    payload={"event_id": str(event.id)},
    asset_id=event.asset_id,
    sensor_id=event.sensor_id,
)
```

### Subscribe to Events

```python
from backend.src.events import subscribe

# Subscribe to events
def handle_event(event):
    print(f"Received: {event.event_type}")

unsubscribe = subscribe(
    callback=handle_event,
    event_types=[EventType.EVENT_CREATED, EventType.EVENT_RESOLVED],
    asset_id=optional_asset_id,  # Optional filter
)

# Later: unsubscribe()
```

### Event Payload Structure

All events follow a standard schema:

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

### Services Integration

All services emit events via the dispatcher:

| Service | Event Emitted |
|---------|----------------|
| MeasurementService | measurement.created |
| ThresholdService | threshold.evaluated |
| EventService | event.created, event.resolved |
| HealthService | health.updated |
| PropagationService | propagation.created |

## Asset Relationship Graph

Manage hierarchical and associative relationships between assets.

### Relationship Types

| Type | Description |
|------|-------------|
| contains | Parent contains child (hierarchical ownership) |
| connected_to | Assets are physically/logically connected |
| feeds | Parent provides input/energy to child |
| monitors | Parent monitors/measures child |
| controls | Parent commands/controls child |

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /relationships | Create relationship |
| GET | /relationships | List relationships |
| GET | /relationships/{id} | Get single relationship |
| DELETE | /relationships/{id} | Delete relationship |
| GET | /relationships/graph/{asset_id} | Get hierarchical graph |
| GET | /relationships/children/{asset_id} | Get direct children |
| GET | /relationships/parents/{asset_id} | Get direct parents |
| GET | /relationships/types | List available types |

### Graph Query Parameters

```
GET /relationships/graph/{id}?direction=down&max_depth=10
```

- `direction`: "up", "down", or "both"
- `max_depth`: 1-100 (default: 10)

### Graph Response Format

```json
{
  "asset_id": "uuid",
  "asset_name": "Site Alpha",
  "asset_type": "site",
  "health_status": "HEALTHY",
  "health_score": 95,
  "children": [
    {
      "asset_id": "uuid",
      "asset_name": "Building A",
      "relationship_type": "contains",
      "children": []
    }
  ],
  "parents": [],
  "depth": 1
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

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /propagation/event/{event_id} | Get propagations for event |
| GET | /propagation/asset/{asset_id} | Get impacts on asset |
| GET | /propagation/chain/{asset_id} | Get impact chain |
| GET | /propagation/impacts | List all impacts |
| GET | /propagation/types | List propagation types |
| POST | /propagation/propagate/{event_id} | Manual trigger |

### Query Parameters

```
GET /propagation/chain/{id}?max_depth=10
GET /propagation/impacts?severity=CRITICAL&min_depth=2
```

### Propagation Behavior

- **MAX_DEPTH = 3** (configurable)
- WARNING and CRITICAL events trigger propagation
- Propagations auto-cleanup when source event is resolved
- Cycles prevented via visited set

### Impact Chain Response

```json
{
  "source_event_id": "uuid",
  "source_asset_name": "Transformer A",
  "source_severity": "CRITICAL",
  "chain": [
    {
      "asset_id": "uuid",
      "asset_name": "Building A",
      "severity": "WARNING",
      "depth": 1,
      "relationship_type": "feeds",
      "propagation_type": "downstream_failure",
      "children": []
    }
  ],
  "total_affected": 5
}
```

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

| Relationship | Weight | Description |
|-------------|--------|-------------|
| feeds | 0.7 | Provider failure affects consumers |
| controls | 0.6 | Controller failure affects controlled |
| contains | 0.5 | Parent affected by child |
| connected_to | 0.3 | Connected assets share dependency |
| monitors | 0.0 | No health impact |

### Depth Decay

| Depth | Decay | Description |
|-------|-------|-------------|
| 1 | 1.0 | Direct dependency |
| 2 | 0.5 | Through one hop |
| 3 | 0.25 | Through two+ hops |

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health/tree/{asset_id} | Get health tree with dependencies |
| GET | /health/contributors/{asset_id} | Get health contributors |
| GET | /health/network | Network-wide health summary |
| POST | /health/recalculate-network | Recalculate all |
| GET | /health/weights | Relationship weights info |
| GET | /health/decay | Depth decay info |

### Health Tree Response

```json
{
  "asset_id": "uuid",
  "asset_name": "Building A",
  "health_score": 44,
  "health_status": "DEGRADED",
  "local_penalty": 0,
  "dependency_penalty": 56,
  "total_penalty": 56,
  "contributors": [
    {
      "asset_id": "uuid",
      "asset_name": "Transformer A",
      "health_score": 20,
      "penalty": 56,
      "depth": 1,
      "relationship_type": "feeds"
    }
  ],
  "depth": 0,
  "max_depth": 3
}
```

## Scenario Simulation Engine

Simulate failures and recoveries without affecting live data.

### Scenario Types

| Type | Description |
|------|-------------|
| failure | Simulate a failure event |
| recovery | Simulate a recovery |
| maintenance | Simulate maintenance |
| custom | Custom scenario |

### Severity Penalties

| Severity | Penalty |
|----------|---------|
| WARNING | -10 |
| CRITICAL | -20 |

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /scenarios | Create scenario |
| GET | /scenarios | List scenarios |
| GET | /scenarios/{id} | Get scenario |
| DELETE | /scenarios/{id} | Delete scenario |
| POST | /scenarios/{id}/run | Execute simulation |
| GET | /scenarios/{id}/results | Get results |
| GET | /scenarios/{id}/impact-tree | Get tree view |
| GET | /scenarios/{id}/compare | Compare with live |

### Isolation

- Virtual events (memory only, not written to events table)
- Virtual propagations (memory only, not written to propagated_events)
- Virtual health (memory only, not written to asset_health)
- Results stored in scenario_results (isolated table)

### Results Response

```json
{
  "affected_assets": [...],
  "max_depth": 3,
  "worst_health": 18,
  "average_health": 64
}
```

## Running Tests

```bash
pytest tests/
```

## Resilience Analysis

### Resilience Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /resilience/analyze/{id} | Analyze single asset |
| POST | /resilience/analyze-network | Analyze all assets |
| GET | /resilience/asset/{id} | Get existing analysis |
| GET | /resilience/top-critical | Get top critical assets |
| GET | /resilience/network | Get network metrics |
| GET | /resilience/recommendations/{id} | Get recommendations |

### Criticality Formula

```
criticality = (upstream × 0.3) + (downstream × 0.4) + (dependency × 0.2) + (events × 0.1)
```

### Resilience Formula

```
resilience = 100 - dependency_penalty - propagation_penalty - event_penalty
```

### Single Point of Failure

An asset is SPOF if removing it disconnects more than one downstream branch.

### Isolation

- Reads from: assets, asset_relationships, asset_health_dependencies, events
- Writes to: resilience_analyses, resilience_recommendations
- Never touches: events (live), propagated_events, asset_health

## Network Topology Engine

### Module Structure

```
backend/src/services/topology/
├── topology_types.py      # Core data types
├── graph_builder.py       # Build graphs from assets
├── flow_models.py         # Physics abstraction
├── topology_engine.py     # Main engine
└── topology_validator.py  # Validation
```

### Key Features

- **Multi-domain support**: electrical, water, transport
- **Flow simulation**: capacity, resistance, utilization
- **Path tracing**: BFS/DFS, shortest path, all paths
- **Graph validation**: orphans, connectivity, consistency

### Infrastructure Layers

| Layer | Flow Type | Load Metric |
|-------|-----------|-------------|
| electrical | power | MW |
| water | water | m³/h |
| transport | traffic | vehicles/h |

### Example Usage

```python
from backend.src.services.topology import TopologyEngine

engine = TopologyEngine()
graph = engine.build_topology(raw_assets)

# Find path
path = engine.find_path(graph, "source", "target")

# Simulate flow
result = engine.simulate_flow(graph, "source", initial_load=100.0)
```

### Flow Status

- **STABLE**: utilization < 0.8
- **DEGRADED**: 0.8 <= utilization < 1.0
- **OVERLOADED**: utilization >= 1.0

## Routing, Flow, and Resilience Engines

### Module Structure

```
backend/src/services/routing/
├── routing_types.py      # Route, FlowAllocation, RoutingResult
├── cost_models.py        # Domain-specific cost calculations
├── routing_engine.py     # Dijkstra-based path discovery
├── flow_engine.py        # Load distribution across routes
└── resilience_engine.py  # Network robustness measurement
```

### Three Independent Engines

| Engine | Responsibility | Key Methods |
|--------|----------------|-------------|
| RoutingEngine | Path discovery | find_shortest_path, find_all_paths |
| FlowEngine | Load distribution | allocate_flow, detect_overload |
| ResilienceEngine | Network stability | compute_resilience_score |

### Cost Model Domains

| Domain | Factor | Description |
|--------|--------|-------------|
| electrical | 1.2 | Power transmission costs |
| water | 1.0 | Baseline water costs |
| transport | 0.8 | Traffic flows freely |

### Example Usage

```python
from backend.src.services.routing import (
    RoutingEngine, FlowEngine, ResilienceEngine
)

# Find route
routing = RoutingEngine()
route = routing.find_shortest_path(graph, "source", "dest")

# Allocate flow
flow = FlowEngine()
dist = flow.allocate_flow(route, total_load=100.0)

# Measure resilience
resilience = ResilienceEngine()
metrics = resilience.compute_resilience_score(graph, route)
```

### Allocation Strategies

- **equal**: Distribute load equally across routes
- **capacity**: Proportional to route capacity
- **cost**: Inverse proportional to route cost
