# ADR-0018: Dependency-Aware Health Propagation

## Status

Accepted

## Context

The GCDTP system manages infrastructure assets that are interconnected through relationships (ADR-0016). When an asset's health degrades due to events, related assets may also be affected through dependency chains.

### The Problem

**Events vs Propagation vs Health**:

| Concept | Definition | Data Flow |
|---------|------------|----------|
| **Event** | Something that happened (factual) | Source of truth |
| **Propagation** | Who is affected (consequence) | Derived from events |
| **Health** | Asset condition (calculated) | Derived from events + dependencies |

Without dependency-aware health, an asset's health only reflects its own events:

```
Asset A: Event → CRITICAL → Health = 20
Asset B: No events → HEALTHY → Health = 100

But Asset A feeds Asset B!
Asset B should be aware that its provider is failing.
```

### Why Health Must Never Write Back Into Events

**Critical Rule**: Health is derived state. Events are facts.

```
Events (Facts):
  - "Temperature exceeded 80°C at 10:00"
  - "Pressure dropped below threshold at 10:15"

Health (Derived):
  - Asset health = 65 (calculated from events)
  
NOT:
  - Events modified based on health
```

**Why this matters:**

1. **Audit Trail**: Events are immutable facts for compliance
2. **Causality**: Health changes don't cause events
3. **Separation**: Events → Propagation → Health is one-way
4. **Debugging**: Can trace health back to actual events

## Decision

Implement dependency-aware health that reflects both local events and impacts from related assets.

### Database Layer

Create `asset_health_dependencies` table:

```sql
CREATE TABLE asset_health_dependencies (
    id UUID PRIMARY KEY,
    asset_id UUID REFERENCES assets(id),
    source_asset_id UUID REFERENCES assets(id),
    relationship_type ENUM,
    impact_weight FLOAT,
    penalty FLOAT,
    depth INTEGER,
    created_at TIMESTAMP,
    
    UNIQUE (asset_id, source_asset_id, relationship_type)
);
```

## Relationship Weights

Each relationship type has a weight representing its impact on health:

| Relationship | Weight | Rationale |
|-------------|--------|----------|
| **feeds** | 0.7 | High dependency - power/fuel/feed is critical |
| **controls** | 0.6 | Control systems are important |
| **contains** | 0.5 | Containment implies ownership/responsibility |
| **connected_to** | 0.3 | Lower dependency - just connectivity |
| **monitors** | 0.0 | No health impact - observation only |

### Why These Weights?

1. **feeds = 0.7**: If the power grid fails, everything dependent fails. Highest weight.

2. **controls = 0.6**: A controller failure affects all controlled assets. High but not critical.

3. **contains = 0.5**: Parent is responsible for children, but containment doesn't guarantee failure.

4. **connected_to = 0.3**: Connectivity is important, but often has redundancy.

5. **monitors = 0.0**: Monitoring is observation, not dependency. A sensor monitoring a motor doesn't affect the motor's health.

## Depth Decay

### Why Depth Decay Prevents Runaway Penalties

Without decay, a single failure could cascade infinitely:

```
Event at Sensor X (depth 0)
  → Depth 1: Motor A (penalty × 1.0)
  → Depth 2: Equipment A (penalty × 1.0)
  → Depth 3: Building A (penalty × 1.0)
  → Depth 4: Site Alpha (penalty × 1.0)
  → ... (infinite penalty)
```

### Depth Decay Formula

```
decay(depth) =
    1.0   if depth = 1
    0.5   if depth = 2
    0.25  if depth >= 3
```

### Example

```
Event: Transformer A has health 20 (CRITICAL)

Depth 1 (feeds Building A):
    Penalty = (100 - 20) × 0.7 × 1.0 = 56

Depth 2 (Building A contains Equipment B):
    Penalty = 56 × 0.5 = 28

Depth 3 (Equipment B feeds Facility C):
    Penalty = 28 × 0.25 = 7

Result: Farther assets receive progressively smaller penalties
```

## Penalty Formula

### Individual Penalty

```
penalty = (100 - source_health_score) × relationship_weight × depth_decay
```

### Total Dependency Penalty

```
dependency_penalty = Σ(penalties from all affected sources)
```

### Final Health Score

```
health = 100 - local_event_penalty - dependency_penalty
```

Where:
- `local_event_penalty` = CRITICAL × 20 + WARNING × 10
- `dependency_penalty` = Sum of all dependency penalties

### Clamping

```
health = clamp(health, 0, 100)
```

Health never goes below 0 or above 100.

## Example Calculation

### Scenario

```
Transformer A
├── feeds Building A (weight 0.7)
│   └── contains Equipment B (weight 0.5)
│       └── feeds Facility C (weight 0.7)
│
├── feeds Substation B (weight 0.7)
│
└── monitors Station D (weight 0.0) ← No impact
```

### Asset Healths

| Asset | Local Events | Health Score |
|-------|-------------|--------------|
| Transformer A | CRITICAL | 20 |
| Building A | None | 100 |
| Equipment B | WARNING | 90 |
| Facility C | None | 100 |
| Substation B | None | 100 |

### Dependency Penalties

**Building A**:
```
Penalty from Transformer A:
  = (100 - 20) × 0.7 × 1.0
  = 56
```

**Equipment B**:
```
Penalty from Transformer A (via Building A):
  = (100 - 20) × 0.7 × 1.0 × 0.5
  = 28

Penalty from Building A:
  = (100 - 100) × 0.5 × 1.0
  = 0

Total = 28
```

**Facility C**:
```
Penalty from Transformer A:
  = (100 - 20) × 0.7 × 1.0 × 0.5 × 0.25
  = 7

Penalty from Equipment B:
  = (100 - 90) × 0.7 × 0.25
  = 1.75

Total = 8.75
```

### Final Health

| Asset | Local Penalty | Dependency Penalty | Final Health |
|-------|--------------|-------------------|--------------|
| Transformer A | 80 | 0 | 20 |
| Building A | 0 | 56 | 44 |
| Equipment B | 10 | 28 | 62 |
| Facility C | 0 | 8.75 | 91.25 |

## Why Network Health Is Required for Digital Twins

### The Gap

Flat health model:
```
Asset Health = Local Events Only

Problem: What if Asset A feeds Asset B and Asset A fails?
Asset B still shows "HEALTHY" if it has no local events!
```

### The Solution

Network health model:
```
Asset Health = Local Events + Dependencies

Asset B receives penalty from Asset A through "feeds" relationship
Asset B now shows "DEGRADED" because its provider is failing
```

### Benefits

1. **Realistic Assessment**: Asset health reflects real-world conditions
2. **Early Warning**: See cascading effects before local failures occur
3. **Root Cause**: Trace health degradation to upstream failures
4. **Infrastructure View**: Understand system-wide health, not just individual assets

## API Design

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health/tree/{asset_id} | Get health tree for asset |
| GET | /health/contributors/{asset_id} | Get health contributors |
| GET | /health/network | Network-wide health summary |
| POST | /health/recalculate-network | Recalculate all |
| GET | /health/weights | Relationship weights info |
| GET | /health/decay | Depth decay info |

### Response Structure

```json
{
  "asset_id": "xxx",
  "asset_name": "Building A",
  "health_score": 44,
  "health_status": "DEGRADED",
  "local_penalty": 0,
  "dependency_penalty": 56,
  "total_penalty": 56,
  "contributors": [
    {
      "asset_id": "yyy",
      "asset_name": "Transformer A",
      "health_score": 20,
      "penalty": 56,
      "depth": 1,
      "relationship_type": "feeds"
    }
  ]
}
```

## Consequences

### Positive

1. **Accurate Health**: Reflects real-world asset conditions
2. **Cascade Visibility**: See downstream effects of failures
3. **No Event Modification**: Events remain immutable facts
4. **Automatic**: Dependency penalties recalculated with events

### Negative

1. **Complexity**: Health calculation is more complex
2. **Performance**: Recalculation requires traversing relationships
3. **Tuning**: Weights and decay may need adjustment

### Neutral

1. **Derived State**: Health can be recalculated at any time
2. **No Circular Updates**: Dependencies don't affect events
3. **Configurable**: Weights can be adjusted per use case

## Constraints Enforced

- No AI/ML prediction
- No notifications/alerts
- No Event Engine modifications
- No Failure Propagation Engine modifications
- Health remains derived only
- No Redis/Kafka/Neo4j

## Implementation Notes

### HealthService Integration

```python
def calculate_asset_health(asset_id):
    # 1. Calculate local penalty from events
    local_penalty = calculate_local_penalty(asset_id)
    
    # 2. Get dependency penalties
    dependency_penalty = get_dependency_penalty(asset_id)
    
    # 3. Calculate final health
    health = 100 - local_penalty - dependency_penalty
    
    # 4. Clamp to valid range
    health = clamp(health, 0, 100)
    
    return health
```

### DependencyHealthService

```python
def recalculate_network_health():
    # 1. Clear existing dependencies
    clear_all_dependency_penalties()
    
    # 2. For each asset:
    for asset in get_all_assets():
        # Find all related assets
        related = get_related_assets(asset, max_depth=3)
        
        # Calculate penalties
        for source in related:
            penalty = calculate_penalty(source, relationship, depth)
            store_dependency_penalty(asset, source, penalty)
    
    # 3. Recalculate all health scores
    for asset in get_all_assets():
        recalculate_health(asset)
```

## Future Considerations

1. **Custom Weights**: Per-relationship-type weight configuration
2. **Time Decay**: Penalties that fade over time
3. **Conditional Propagation**: Only propagate under certain conditions
4. **Historical Tracking**: Track dependency penalties over time
5. **Alerting Thresholds**: Custom thresholds for dependency alerts

## Implementation Checklist

- [x] Database migration (010_create_asset_health_dependencies.sql)
- [x] AssetHealthDependency model
- [x] Health dependency schemas
- [x] DependencyHealthService
- [x] HealthService integration
- [x] Network health routes
- [x] Frontend API client
- [x] NetworkHealth page
- [x] GeoPortal integration
- [x] Backend tests
- [x] Frontend tests