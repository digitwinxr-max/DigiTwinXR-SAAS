# ADR-0019: Scenario Simulation Engine

## Status

Accepted

## Context

Infrastructure operators need a safe way to explore "what-if" scenarios without affecting live operations. Currently:

- Events affect health in real-time
- Operators cannot predict cascade effects before they occur
- Recovery planning requires waiting for actual failures

### The Problem

**Operators need to know:**

1. "What if Transformer A fails?"
2. "What would be the impact on downstream assets?"
3. "How would recovery affect system health?"

**Without simulation:**

```
1. Failure occurs in real system
2. Health degrades
3. Operators react to cascade
4. Recovery happens
```

**With simulation:**

```
1. Operator creates failure scenario
2. Simulation runs with virtual events
3. Impact is predicted
4. Operator plans response
5. No live system affected
```

## Decision

Create a Scenario Simulation Engine that creates isolated virtual events, propagations, and health calculations without modifying live data.

### Database Layer

**scenarios** table:

```sql
CREATE TABLE scenarios (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    scenario_type ENUM(failure, recovery, maintenance, custom),
    root_asset_id UUID,
    severity ENUM(WARNING, CRITICAL),
    status ENUM(draft, completed),
    created_at TIMESTAMP
);
```

**scenario_results** table:

```sql
CREATE TABLE scenario_results (
    id UUID PRIMARY KEY,
    scenario_id UUID,
    asset_id UUID,
    predicted_health FLOAT,
    current_health FLOAT,
    delta_health FLOAT,
    propagation_depth INTEGER,
    relationship_path TEXT,
    created_at TIMESTAMP
);
```

## Reality Layer vs Simulation Layer

### The Two Worlds

```
┌─────────────────────────────────────────────────────────────┐
│                     REALITY LAYER                          │
│  (Actual system state - cannot be modified by simulation)  │
├─────────────────────────────────────────────────────────────┤
│  events              - Actual events that occurred         │
│  propagated_events    - Actual consequences                │
│  asset_health        - Actual calculated health            │
│  measurements         - Real sensor readings                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   SIMULATION LAYER                          │
│  (Sandbox - can experiment without consequences)            │
├─────────────────────────────────────────────────────────────┤
│  virtual_events      - Hypothetical events (memory only)   │
│  virtual_propagation - Hypothetical consequences (memory)  │
│  virtual_health      - Predicted health (memory only)      │
│  scenario_results    - Stored predictions (isolated table) │
└─────────────────────────────────────────────────────────────┘
```

### Why the Separation Matters

1. **Audit Trail Integrity**: Real events are immutable facts
2. **No Accidental Corruption**: Simulation cannot break production
3. **Clear Mental Model**: "What-if" vs "What-is"
4. **Trust**: Operators know simulations are safe

## Virtual Events

### Definition

A **VirtualEvent** exists only in memory during simulation:

```python
class VirtualEvent:
    asset_id: UUID
    severity: WARNING | CRITICAL
    message: str
    timestamp: datetime  # Generated during simulation
```

### Why Not Write to Events Table?

| Real Events | Virtual Events |
|-------------|----------------|
| Immutable facts | Hypothetical scenarios |
| Audit trail | Sandbox experiments |
| Trigger alerts | No alerts |
| Affect health | Predict health |
| Persisted | In-memory only |

### Example

```python
# Real event (what happened)
Event(asset_id=transformer_a, severity=CRITICAL, message="Overload detected")

# Virtual event (what if)
VirtualEvent(asset_id=transformer_a, severity=CRITICAL, message="Simulated failure")
```

## Virtual Propagation

### Definition

**VirtualPropagation** simulates cascade effects:

```python
class VirtualPropagation:
    source_event: VirtualEvent
    affected_asset_id: UUID
    propagation_type: str  # downstream_failure, child_failure, etc.
    depth: int  # 1, 2, or 3
    severity: WARNING | CRITICAL
```

### Uses Existing Relationship Graph

```
Asset Relationship Graph (ADR-0016):
    Transformer A ─feeds→ Building A ─contains→ Equipment A

Simulation traverses the same graph:
    VirtualEvent at Transformer A
        → VirtualPropagation to Building A (depth 1, feeds)
            → VirtualPropagation to Equipment A (depth 2, contains)
```

### Propagation Rules

Same rules as Failure Propagation Engine (ADR-0017):

| Relationship | Direction | Propagation Type |
|--------------|-----------|------------------|
| contains | Upward | child_failure |
| feeds | Downstream | downstream_failure |
| controls | Downstream | dependency_impact |
| connected_to | Bidirectional | dependency_impact |
| monitors | None | Informational only |

## Virtual Health

### Definition

**VirtualHealth** calculates predicted health:

```python
class VirtualHealth:
    asset_id: UUID
    live_health: float      # Actual current health
    local_virtual_penalty: float    # From virtual events
    virtual_dependency_penalty: float  # From virtual propagations
    predicted_health: float  # What health would be
    depth: int               # Distance from root
```

### Health Calculation Formula

```
predicted_health = live_health - local_penalty - dependency_penalty

where:
  local_penalty = WARNING × 10, CRITICAL × 20
  dependency_penalty = Σ((100 - source_health) × weight × decay)
```

### Example

```
Transformer A (root):
  live_health: 100
  virtual_event: CRITICAL
  local_penalty: 20
  dependency_penalty: 0
  predicted_health: 80

Building A (depth 1, feeds):
  live_health: 100
  virtual_propagation from Transformer A
  dependency_penalty: (100-80) × 0.7 × 1.0 = 14
  predicted_health: 86

Equipment A (depth 2, contains):
  live_health: 100
  virtual_propagation from Building A
  dependency_penalty: (100-86) × 0.5 × 0.5 = 3.5
  predicted_health: 96.5
```

## Digital Twins as What-If Systems

### The Digital Twin Purpose

A digital twin serves two purposes:

1. **Mirror Reality**: Show current state
2. **Predict Future**: Explore what-if scenarios

```
┌────────────────────────────────────────────────────────────┐
│                    DIGITAL TWIN                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│   ┌──────────────┐         ┌──────────────┐               │
│   │   REALITY    │  ←──→   │  SIMULATION   │               │
│   │   (Mirror)   │         │   (What-If)   │               │
│   └──────────────┘         └──────────────┘               │
│          │                        │                         │
│          ▼                        ▼                         │
│   Current Health           Predicted Health                 │
│   Live Events              Virtual Events                  │
│   Active Alerts            Hypotheticals                   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Why Operators Need What-If

1. **Proactive Planning**: Know impacts before failures
2. **Recovery Testing**: Validate recovery procedures
3. **Maintenance Windows**: Understand maintenance impact
4. **Training**: Explore scenarios without risk

## API Design

### Endpoints

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

### Results Response

```json
{
  "affected_assets": [
    {
      "asset_id": "uuid",
      "asset_name": "Building A",
      "current_health": 100,
      "predicted_health": 80,
      "delta_health": -20,
      "propagation_depth": 1
    }
  ],
  "max_depth": 3,
  "worst_health": 18,
  "average_health": 64
}
```

### Compare Response

```json
{
  "current_health": 72,
  "predicted_health": 41,
  "delta": -31
}
```

## Consequences

### Positive

1. **Safe Experimentation**: No risk to live systems
2. **Proactive Planning**: Know impacts before they occur
3. **Recovery Validation**: Test recovery procedures
4. **Training**: Explore without consequences
5. **Clear Separation**: Reality vs simulation is obvious

### Negative

1. **Complexity**: Two mental models to maintain
2. **Stale Predictions**: Results are point-in-time
3. **No Real Alerts**: Simulations don't trigger alerts

### Neutral

1. **Isolated Storage**: Results in separate tables
2. **Manual Cleanup**: Old scenarios should be deleted
3. **No Persistence**: Virtual objects are ephemeral

## Constraints Enforced

- **NO AI/ML/LLMs**: Rule-based simulation only
- **NO notifications**: Simulations don't alert
- **NO live writes**: Events/Health tables unchanged
- **NO external dependencies**: PostgreSQL only
- **NO Node-RED/Kafka**: No external brokers
- **NO WebSockets**: REST API only

## Implementation Checklist

- [x] Database migration (011_create_simulation_tables.sql)
- [x] Scenario model
- [x] ScenarioResult model
- [x] Scenario schemas
- [x] SimulationService
- [x] Scenario routes
- [x] Frontend API client
- [x] ScenarioStudio page
- [x] ScenarioImpactTree component
- [x] ScenarioOverlay component
- [x] GeoPortal integration
- [x] Backend tests
- [x] Frontend tests