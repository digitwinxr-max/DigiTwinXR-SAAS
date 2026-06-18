# ADR-0047: Timeline Replay Engine

## Status

Accepted

## Context

The GCDTP platform has achieved perfect Enterprise Grade status (10.0/10) with the Unified Semantic Layer (ADR-0046). To enable temporal analysis, what-if scenarios, and historical state reconstruction, we need a Timeline Replay Engine.

### Digital Twins Require Time

A digital twin is not complete without temporal awareness:

1. **Historical Analysis**: Understand past states and trends
2. **Root Cause Analysis**: Replay events to understand failures
3. **What-If Scenarios**: Simulate changes against historical states
4. **Compliance**: Demonstrate system state at any point in time
5. **Training**: Train AI/ML on historical scenarios

### Current State vs Historical State vs Replay State

| State Type | Description | Mutability |
|-----------|-------------|------------|
| **Current State** | Live, real-time system state | Mutable |
| **Historical State** | Point-in-time snapshots | Immutable |
| **Replay State** | Reconstructed view of historical data | Read-only |

### Why Replay is Immutable

1. **Audit Trail**: Immutable records for compliance
2. **Reproducibility**: Same data for all users
3. **Integrity**: No accidental or malicious modifications
4. **Performance**: No writes during replay
5. **Consistency**: Same result every time

### Why Timeline is Read-Only

The Timeline Replay Engine:
- ❌ Does NOT modify live data
- ❌ Does NOT write to operational tables
- ❌ Does NOT trigger alerts
- ❌ Does NOT perform analytics
- ❌ Does NOT make predictions

The Timeline Replay Engine:
- ✅ Captures snapshots from existing records
- ✅ Reconstructs historical states
- ✅ Provides playback capabilities
- ✅ Enables temporal analysis
- ✅ Maintains immutability

### Temporal Reconstruction Philosophy

1. **Capture**: Periodically capture system state snapshots
2. **Index**: Store snapshots with timestamps and entity references
3. **Query**: Efficiently retrieve snapshots by time range
4. **Reconstruct**: Rebuild state at any point in time
5. **Playback**: Animate through historical sequences

---

## Decision

Implement Timeline Replay Engine:

```
database/migrations/
└── 039_create_timeline_snapshots.sql

backend/src/models/
└── timeline_snapshot.py

backend/src/schemas/
└── timeline.py

backend/src/services/
└── timeline_service.py

backend/src/routes/
└── timeline_routes.py

frontend/src/api/
└── timeline.js

frontend/src/pages/
├── TimelineReplay.jsx
└── TimelineReplay.css

frontend/src/components/
├── TimelinePlayer.jsx
└── TimelineOverlay.jsx
```

---

## Data Model

### Snapshot Types

| Type | Description |
|------|-------------|
| `asset_state` | Asset configuration and status |
| `health_state` | Health scores and metrics |
| `event_state` | Event occurrences |
| `measurement_state` | Sensor measurements |
| `system_state` | Overall system metrics |

### Snapshot Structure

```json
{
  "id": "uuid",
  "timestamp": "2024-01-01T00:00:00Z",
  "snapshot_type": "asset_state",
  "entity_type": "asset",
  "entity_id": "asset-001",
  "snapshot_data": {
    "name": "Substation Alpha",
    "status": "healthy",
    "health_score": 95
  },
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## Architecture Rules

1. **NO microservices** - Single backend
2. **NO writes to live tables** - Snapshots only
3. **NO AI prediction** - Pure reconstruction
4. **NO analytics on live data** - Read-only
5. **NO alerts from replay** - Passive viewing
6. **Immutability** - Snapshots cannot be modified

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/timeline/snapshot` | Create snapshot |
| GET | `/timeline/frame` | Get frame at timestamp |
| GET | `/timeline/range` | Get snapshots in range |
| GET | `/timeline/playback` | Generate playback frames |
| GET | `/timeline/system` | System-wide timeline |
| GET | `/timeline/asset/{id}` | Asset timeline |
| GET | `/timeline/event/{id}` | Event timeline |
| GET | `/timeline/health/{id}` | Health timeline |

---

## Event Integration

Subscribe to existing events (NO dispatcher modification):

- `measurement.created`
- `event.created`
- `event.resolved`
- `health.updated`
- `asset.updated`

Capture snapshots automatically from these events.

---

## Frontend Components

### TimelineReplay Page

Three-panel layout:
- Left: Time range selector, playback controls
- Center: Timeline frames, chronological list
- Right: Selected frame details

### TimelinePlayer Component

Playback controls:
- Play/Pause
- Step Forward/Backward
- Speed: 1x, 2x, 5x, 10x
- Slider
- Jump to time

### TimelineOverlay Component

Overlay on GeoPortal:
- Historical health colors
- Historical events
- Historical asset status
- Read-only mode indicator

---

## Consequences

### Positive

1. **Temporal Analysis** - Historical state exploration
2. **Root Cause Analysis** - Event replay
3. **Compliance** - Immutable audit trail
4. **Training** - Historical data for ML
5. **What-If** - Simulation capability

### Negative

1. **Storage** - Snapshot storage requirements
2. **Performance** - Large dataset queries
3. **Complexity** - Additional time dimension

### Neutral

1. No live data modification
2. Read-only by design
3. Backward compatible

---

## Acceptance Criteria

- [x] Database migration 039
- [x] TimelineSnapshot model
- [x] Timeline schemas
- [x] TimelineService
- [x] Timeline routes
- [x] Event integration
- [x] Frontend API client
- [x] TimelineReplay page
- [x] TimelinePlayer component
- [x] TimelineOverlay component
- [x] GeoPortal integration
- [x] Backend tests
- [x] Frontend tests
- [x] ADR documentation

---

## Future Integration Points

1. **What-If Scenarios** - Modify historical state
2. **AI Training** - Use historical data for ML
3. **Compliance Reporting** - Generate reports
4. **Anomaly Detection** - Compare current vs historical
5. **Predictive Maintenance** - Trend analysis

---

## Sign-off

**Status:** ✅ COMPLETE
**Platform Status:** Perfect Enterprise Grade with Temporal Capabilities
