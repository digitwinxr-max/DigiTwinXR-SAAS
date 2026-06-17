# ADR-0020: Recovery Simulation Engine

## Status

Accepted

## Context

After implementing the Scenario Simulation Engine (ADR-0019), operators can predict failure impacts. However, they also need to simulate **recovery strategies** to understand:

1. How long recovery will take
2. Which strategy is most effective
3. What residual risks remain after recovery
4. How to prioritize recovery efforts

### The Problem

**Without recovery simulation:**

```
1. Failure occurs
2. Impact spreads
3. Recovery begins (trial and error)
4. Monitor results
5. Adjust strategy if needed
```

**With recovery simulation:**

```
1. Failure occurs
2. Impact predicted
3. Simulate multiple recovery strategies
4. Compare outcomes
5. Select optimal strategy
6. Execute recovery
```

## Decision

Extend the Scenario Simulation Engine to simulate recovery paths and restoration strategies.

### Database Layer

**recovery_simulations** table:

```sql
CREATE TABLE recovery_simulations (
    id UUID PRIMARY KEY,
    scenario_id UUID,
    strategy_name VARCHAR(255),
    recovery_type ENUM(manual, automatic, staged, reroute),
    estimated_duration_minutes INTEGER,
    recovery_order INTEGER,
    created_at TIMESTAMP
);
```

**recovery_results** table:

```sql
CREATE TABLE recovery_results (
    id UUID PRIMARY KEY,
    recovery_simulation_id UUID,
    asset_id UUID,
    before_health FLOAT,
    after_health FLOAT,
    improvement FLOAT,
    recovery_depth INTEGER,
    remaining_risk VARCHAR(20),
    created_at TIMESTAMP
);
```

## Failure Simulation vs Recovery Simulation

### The Two Simulations

```
┌─────────────────────────────────────────────────────────────┐
│                 FAILURE SIMULATION                           │
├─────────────────────────────────────────────────────────────┤
│  Purpose:    Predict impact of failures                     │
│  Direction:  Health goes DOWN                               │
│  Formula:    predicted = live - penalties                   │
│  Result:     "What if X fails?"                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                RECOVERY SIMULATION                          │
├─────────────────────────────────────────────────────────────┤
│  Purpose:    Predict restoration of health                   │
│  Direction:  Health goes UP                                 │
│  Formula:    restored = before + recovery_value              │
│  Result:     "How do we fix it?"                            │
└─────────────────────────────────────────────────────────────┘
```

### Relationship

```
Failure Simulation          Recovery Simulation
      │                           │
      ▼                           ▼
  Predicted Health ────────► Before Health
                                │
                                ▼
                          After Recovery
```

## Recovery Strategies

### Strategy Types

| Type | Restoration | Description |
|------|-------------|-------------|
| **manual** | +20 | Human intervention required |
| **automatic** | +30 | Automated systems restore |
| **staged** | +15 per depth | Depth-dependent recovery |
| **reroute** | +25 (path-based) | Alternative paths restore |

### Detailed Rules

#### Manual Recovery

```
Manual recovery requires human intervention.
Restoration value: +20 points per asset.

Example:
  Asset health: 60
  After manual: 60 + 20 = 80
```

#### Automatic Recovery

```
Automated systems can restore faster.
Restoration value: +30 points per asset.

Example:
  Asset health: 50
  After automatic: 50 + 30 = 80
```

#### Staged Recovery

```
Recovery progresses through depth levels.
Restoration value: +15 per depth level.

Depth 0: +15
Depth 1: +30
Depth 2: +45

Example (depth 1):
  Asset health: 55
  After staged: 55 + 30 = 85
```

#### Reroute Recovery

```
Alternative paths can restore connectivity.
Restoration value: +25 (adjusted by available paths).

Multiple paths: +25 × 1.5 = 37.5
Single path: +25 × 1.0 = 25
No paths: +25 × 0.5 = 12.5

Example (single path):
  Asset health: 55
  After reroute: 55 + 25 = 80
```

## Health Clamping

All recovery calculations are clamped to valid range:

```
0 ≤ health ≤ 100
```

Examples:
- Before: 90, Recovery: +20 → After: 100 (clamped)
- Before: 10, Recovery: -30 → After: 0 (clamped, impossible scenario)

## Risk Assessment

### Risk Levels

After recovery, remaining risk is calculated:

| Health Range | Risk Level |
|--------------|-----------|
| 90-100 | NONE |
| 80-89 | LOW |
| 60-79 | MEDIUM |
| 40-59 | HIGH |
| 0-39 | CRITICAL |

### Risk Colors

| Risk | Color | Hex |
|------|-------|-----|
| NONE | Green | #22c55e |
| LOW | Lime | #84cc16 |
| MEDIUM | Yellow | #eab308 |
| HIGH | Orange | #f97316 |
| CRITICAL | Red | #ef4444 |

## Duration Estimates

Recovery duration varies by strategy:

| Strategy | Base (min) | Per Asset (min) | Example (5 assets) |
|----------|------------|-----------------|-------------------|
| manual | 120 | 15 | 195 min |
| automatic | 30 | 5 | 55 min |
| staged | 60 | 10 | 110 min |
| reroute | 45 | 8 | 85 min |

## API Design

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /recovery | Create recovery |
| GET | /recovery | List recoveries |
| GET | /recovery/{id} | Get recovery |
| DELETE | /recovery/{id} | Delete recovery |
| POST | /recovery/{id}/run | Execute recovery sim |
| GET | /recovery/{id}/results | Get results |
| GET | /recovery/{id}/tree | Get tree view |
| GET | /recovery/{id}/compare | Compare before/after |

### Compare Response

```json
{
  "recovery_id": "uuid",
  "strategy_name": "Transformer A Recovery",
  "before_health": 65.5,
  "after_health": 85.3,
  "improvement": 19.8,
  "remaining_critical": 1,
  "assets": [
    {
      "asset_id": "uuid",
      "asset_name": "Building A",
      "before_health": 70,
      "after_health": 90,
      "improvement": 20,
      "remaining_risk": "NONE"
    }
  ]
}
```

## Digital Twins as Resilience Systems

### Resilience = Reliability + Recoverability

A complete digital twin models both:

```
┌────────────────────────────────────────────────────────────┐
│                   DIGITAL TWIN                              │
├────────────────────────────────────────────────────────────┤
│                                                            │
│   RELIABILITY                      RECOVERABILITY          │
│   (Failure Domain)                 (Recovery Domain)       │
│                                                            │
│   ┌──────────────┐               ┌──────────────┐          │
│   │  Scenario    │ ───────────► │  Recovery    │          │
│   │  Simulation  │              │  Simulation  │          │
│   └──────────────┘               └──────────────┘          │
│         │                               │                   │
│         ▼                               ▼                   │
│   Health Impact                   Health Restoration        │
│   - Predicted health              - After recovery          │
│   - Cascade effects               - Duration estimates      │
│   - Worst case                    - Remaining risks         │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Why Recovery Remains Virtual

Recovery simulations must remain isolated because:

1. **Testing Strategies**: Try different approaches without committing
2. **Planning**: Know duration and resources needed upfront
3. **Comparison**: Compare strategies side-by-side
4. **Training**: Practice without real consequences

### Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    RECOVERY WORKFLOW                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Run failure simulation                                   │
│     └─► Understand impact                                    │
│                                                             │
│  2. Create recovery simulation                               │
│     └─► Select strategy type                                 │
│                                                             │
│  3. Run recovery simulation                                 │
│     └─► See restored health levels                          │
│                                                             │
│  4. Compare strategies                                      │
│     └─► Select optimal approach                             │
│                                                             │
│  5. Execute real recovery                                   │
│     └─► Apply chosen strategy                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Consequences

### Positive

1. **Informed Decisions**: Know which recovery works best
2. **Time Planning**: Estimate how long recovery takes
3. **Resource Allocation**: Plan crew and equipment
4. **Risk Awareness**: Know residual risks after recovery
5. **Training**: Practice without consequences

### Negative

1. **Complexity**: Multiple strategies to consider
2. **Estimates**: Duration estimates may vary from reality
3. **No Guarantees**: Simulations don't account for all factors

### Neutral

1. **Isolation**: Recovery results separate from failure results
2. **Linked**: Recovery linked to scenario for context
3. **Orderable**: Multiple recoveries can be sequenced

## Constraints Enforced

- **NO AI/ML/LLMs**: Rule-based simulation only
- **NO notifications**: Simulations don't alert
- **NO live writes**: Events/Health tables unchanged
- **NO external dependencies**: PostgreSQL only
- **NO Node-RED/Kafka**: No external brokers
- **NO WebSockets**: REST API only

## Implementation Checklist

- [x] Database migration (012_create_recovery_simulations.sql)
- [x] RecoverySimulation model
- [x] RecoveryResult model
- [x] Recovery schemas
- [x] RecoverySimulationService
- [x] Recovery routes
- [x] Frontend API client
- [x] RecoveryStudio page
- [x] RecoveryImpactTree component
- [x] RecoveryOverlay component
- [x] GeoPortal integration
- [x] Backend tests
- [x] Frontend tests