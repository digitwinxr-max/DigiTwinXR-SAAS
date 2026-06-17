# ADR-0017: Cascading Failure Engine

## Status

Accepted

## Context

GCDTP manages infrastructure assets that are interconnected through relationships defined in ADR-0016 (Asset Relationship Graph Engine). When a failure occurs at one asset, it can have consequences for other assets through these relationships.

### The Problem

**Event** vs **Consequence**:

| Concept | Definition | Example |
|---------|------------|---------|
| **Event** | Something that happened | "Sensor X exceeded temperature threshold" |
| **Consequence** | Who is affected | "Motor A is affected because Sensor X monitors it" |

In a flat model (without relationships), we can only track that an event occurred. We cannot answer:
- What assets are affected?
- How far does the impact propagate?
- What are the cascading effects?

### Why Graph Topology Enables Digital Twins

A digital twin requires understanding **cause and effect**:

```
Physical Reality:
  
  Transformer A fails
       │
       │ contains
       ▼
  Building A loses power
       │
       │ contains
       ▼
  Equipment A stops
       │
       │ monitored by
       ▼
  Sensor X detects anomaly

Flat Model:
  Event: Sensor X exceeded threshold
  Impact: Unknown

Graph Model:
  Event: Sensor X exceeded threshold
  Impact: 
    - Equipment A (monitored by)
    - Building A (contains)
    - Transformer A (feeds)
```

Without graph topology, we cannot trace the chain of consequences.

## Decision

Implement a cascading failure engine that propagates infrastructure impacts through the Asset Relationship Graph.

### Database Layer

Create `propagated_events` table:

```sql
CREATE TABLE propagated_events (
    id UUID PRIMARY KEY,
    source_event_id UUID REFERENCES events(id),
    source_asset_id UUID REFERENCES assets(id),
    affected_asset_id UUID REFERENCES assets(id),
    propagation_type ENUM('child_failure', 'upstream_failure', 
                          'downstream_failure', 'dependency_impact'),
    severity VARCHAR(20),
    depth INTEGER,
    created_at TIMESTAMP,
    
    UNIQUE (source_event_id, affected_asset_id, propagation_type)
);
```

## Propagation Rules

### Relationship-Based Propagation

| Relationship | Direction | Propagation Type | Example |
|--------------|-----------|------------------|---------|
| **contains** | Upward | child_failure | Child fails → Parent affected |
| **feeds** | Downstream | downstream_failure | Power grid fails → Facility loses power |
| **controls** | Downstream | dependency_impact | Controller fails → Motor stops |
| **connected_to** | Bidirectional | dependency_impact | Equipment A fails → Equipment B affected |
| **monitors** | None | Informational only | Sensor alerts don't affect monitored asset health |

### Why These Rules?

1. **contains → Upward**
   - When a child asset fails, its parent is affected
   - Example: Equipment fails → Building degraded

2. **feeds → Downstream**
   - When a power source fails, consumers are affected
   - Example: Generator fails → Facility loses power

3. **controls → Downstream**
   - When a controller fails, controlled assets are affected
   - Example: PLC fails → Valve stops responding

4. **connected_to → Bidirectional**
   - Connected assets share dependency
   - Example: Network switch fails → Servers affected

5. **monitors → No propagation**
   - Monitoring is observation, not dependency
   - Example: Sensor alert doesn't damage the equipment

## Why Cycles Must Be Prevented

### The Problem

Asset relationships can create cycles:

```
A contains B
B contains C
C feeds A  ← Cycle!
```

If we propagate without cycle detection:

```
Event at A
  → B affected (contains)
  → C affected (contains)
  → A affected (feeds) ← Infinite loop!
```

### Solution: Visited Set

```python
def propagate(event, asset_id, visited=None, depth=0):
    if visited is None:
        visited = set()
    
    if depth >= MAX_DEPTH:
        return  # Stop at max depth
    
    if asset_id in visited:
        return  # Prevent cycles
    
    visited.add(asset_id)
    
    # Propagate to related assets
    for related in get_related_assets(asset_id):
        propagate(event, related, visited, depth + 1)
```

## Why Propagation Depth Is Limited

### The Problem

Without depth limits, a single failure could propagate through the entire infrastructure:

```
Event at Sensor X
  → Depth 1: Motor A (monitors)
  → Depth 2: Equipment A (contains)
  → Depth 3: Building A (contains)
  → Depth 4: Site Alpha (contains)
  → Depth 5: Region (contains)
  → ... (continues indefinitely)
```

### Solution: MAX_DEPTH = 3

```python
MAX_DEPTH = 3  # Default maximum propagation depth

def propagate(event, asset_id, depth=0):
    if depth >= MAX_DEPTH:
        return  # Stop propagation
    
    # Propagate one level deeper
    for child in get_children(asset_id):
        propagate(event, child, depth + 1)
```

**Rationale**:
- Depth 1: Direct impact
- Depth 2: Secondary impact
- Depth 3: Tertiary impact (reasonable boundary)

Deeper propagation can be requested explicitly via API.

## Why Health Remains Derived State

### The Design

Health is calculated from events, not propagated:

```
Events → Health Calculation → Health Score

NOT:

Events → Propagation → Propagated Events → Health
```

### Rationale

1. **Single Source of Truth**: Health is calculated from actual events, not indirect propagation

2. **Separation of Concerns**:
   - Events: What happened (factual)
   - Propagation: Who is affected (derived)
   - Health: Asset condition (calculated)

3. **Transparency**: Users can see both:
   - Direct events on an asset
   - Propagated impacts from related assets

4. **Flexibility**: Health rules can change without affecting propagation logic

### Implementation

```python
# Health is calculated from direct events only
def calculate_health(asset_id):
    events = get_direct_events(asset_id)  # Not propagated events
    health = 100
    
    for event in events:
        if event.severity == 'CRITICAL':
            health -= 20
        elif event.severity == 'WARNING':
            health -= 10
    
    return max(0, health)
```

## Event vs Propagation: Key Distinction

| Aspect | Event | Propagation |
|--------|-------|-------------|
| **What it represents** | Something happened | Who is affected |
| **Source** | Sensor/monitor trigger | Relationship traversal |
| **Uniqueness** | Unique per occurrence | One per (event, asset, type) |
| **Lifecycle** | Created/resolved | Created with event, deleted with event |
| **User action** | Can be resolved | Automatically cleaned up |

### Example

```
Sensor X detects high temperature

Event Created:
  - Event ID: evt-001
  - Asset: Motor A
  - Severity: WARNING
  - Message: "Temperature exceeded 80°C"

Propagation Created:
  - Propagation ID: prop-001
  - Source Event: evt-001
  - Affected Asset: Building A
  - Type: upstream_failure
  - Depth: 1

When evt-001 is resolved:
  - prop-001 is automatically deleted
  - No manual cleanup needed
```

## API Design

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /propagation/event/{event_id} | Get propagations for event |
| GET | /propagation/asset/{asset_id} | Get impacts on asset |
| GET | /propagation/chain/{asset_id} | Get impact chain |
| GET | /propagation/impacts | List all impacts |
| GET | /propagation/types | List propagation types |
| POST | /propagation/propagate/{event_id} | Manual trigger |

### Response Structure

```json
{
  "source_event_id": "evt-001",
  "source_asset_name": "Sensor X",
  "source_severity": "WARNING",
  "chain": [
    {
      "asset_id": "motor-a",
      "asset_name": "Motor A",
      "severity": "WARNING",
      "depth": 1,
      "relationship_type": "contains",
      "propagation_type": "child_failure",
      "children": [...]
    }
  ],
  "total_affected": 5
}
```

## Consequences

### Positive

1. **Impact Visibility**: Know all assets affected by a failure
2. **Root Cause Analysis**: Trace cascading effects back to source
3. **Infrastructure Awareness**: Understand dependency chains
4. **Automatic Cleanup**: Propagations deleted when events resolved
5. **No External Dependencies**: Pure PostgreSQL implementation

### Negative

1. **Performance**: Traversal costs increase with graph size
2. **Complexity**: More tables, relationships, and code
3. **Data Volume**: Propagations grow with events and relationships

### Neutral

1. **Propagation is Derived**: Doesn't affect underlying events or health
2. **Configurable Depth**: Can adjust MAX_DEPTH as needed
3. **Manual Trigger Available**: Can reprocess events if needed

## Constraints Enforced

- No AI/ML prediction
- No notifications/alerts
- No Node-RED or external brokers
- No WebSockets
- No external graph databases (PostgreSQL only)
- No Neo4j or Redis/Kafka
- Existing Health Engine logic unchanged
- Existing Event Engine behavior unchanged

## Future Considerations

1. **Aggregate Impact Score**: Calculate total impact across all propagations
2. **Propagation Policies**: Different rules for different asset types
3. **Time-Decay**: Propagations that age out over time
4. **Conditional Propagation**: Only propagate under certain conditions
5. **Impact Metrics**: Track historical propagation patterns

## Implementation Checklist

- [x] Database migration (009_create_propagated_events.sql)
- [x] Extended event types for propagation
- [x] PropagatedEvent model
- [x] PropagatedEvent schemas
- [x] FailurePropagationService
- [x] EventService integration
- [x] Propagation routes
- [x] Frontend API client
- [x] ImpactChain page
- [x] GeoPortal integration
- [x] Backend tests
- [x] Frontend tests