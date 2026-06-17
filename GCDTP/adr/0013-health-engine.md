# ADR-0013: Health Engine

## Status

Accepted

## Context

GCDTP has implemented:
1. **Measurement Engine** (ADR-0008) - Stores sensor measurements
2. **Threshold Engine** (ADR-0010) - Evaluates measurements against rules
3. **Event Engine** (ADR-0011) - Stores threshold violation events

We now need a derived state layer that provides an at-a-glance view of asset health based on active events.

## Why Derived State?

### Health as System Memory

Health is **derived state** - it represents an aggregation of events, not source of truth. This is important for several reasons:

```
┌─────────────────┐
│  Measurements   │  ← Source of truth
├─────────────────┤
│  Events         │  ← Source of truth (threshold violations)
├─────────────────┤
│  Health         │  ← DERIVED STATE (from events)
├─────────────────┤
│  Alerts         │  ← Future: notifications based on health
└─────────────────┘
```

### One-Way Dependency

Health depends on events, but events do NOT depend on health:

```
Events ──────────► Health
    │                  ▲
    │                  │
    └── (no backflow) ─┘
```

This is critical: **health must never write back to events**.

## Database Schema

```sql
CREATE TABLE asset_health (
    id UUID PRIMARY KEY,
    asset_id UUID REFERENCES assets(id),  -- Unique
    health_score INTEGER CHECK (0-100),
    health_status VARCHAR(20),           -- HEALTHY, DEGRADED, CRITICAL
    active_event_count INTEGER,
    last_updated TIMESTAMP,
    calculation_method VARCHAR(50)        -- RULE_BASED
);
```

## Health Calculation Rules

```python
def calculate_asset_health(asset_id):
    score = 100
    events = get_active_events(asset_id)
    
    for event in events:
        if event.severity == "CRITICAL":
            score -= 20
        elif event.severity == "WARNING":
            score -= 10
    
    score = clamp(score, 0, 100)
    status = derive_status(score)
    
    return {
        "health_score": score,
        "health_status": status,
        "active_event_count": len(events)
    }

def derive_status(score):
    if score >= 80: return "HEALTHY"
    if score >= 40: return "DEGRADED"
    return "CRITICAL"
```

## Health Status Thresholds

| Score | Status | Color |
|-------|--------|-------|
| 80-100 | HEALTHY | Green |
| 40-79 | DEGRADED | Yellow |
| 0-39 | CRITICAL | Red |

## Event Integration

Health recalculation is triggered by:

1. **Event Creation** - When a new event is created
2. **Event Resolution** - When an event is resolved

### Why Trigger on Both?

- **Creation**: New events decrease health
- **Resolution**: Resolved events improve health

This ensures health is always synchronized with the current event state.

## API Design

### Health Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health/summary | Overall health statistics |
| GET | /health/assets | All asset health records |
| GET | /health/assets/{id} | Single asset health |
| POST | /health/recalculate/{id} | Manual recalculation |
| POST | /health/recalculate-all | Recalculate all |

### Response Schema

```json
{
  "asset_id": "uuid",
  "health_score": 80,
  "health_status": "HEALTHY",
  "active_event_count": 1,
  "last_updated": "2026-06-16T10:00:00Z",
  "calculation_method": "RULE_BASED"
}
```

### Summary Response

```json
{
  "total_assets": 10,
  "healthy_count": 7,
  "degraded_count": 2,
  "critical_count": 1,
  "average_health_score": 75.5
}
```

## Idempotent Updates

Health recalculation is **idempotent** - calling it multiple times with the same inputs produces the same result. This is important because:

1. Events can be created/resolved multiple times
2. Race conditions are handled gracefully
3. Manual recalculation is safe

## Why Health Must Never Write Back to Events

This is a critical architectural constraint:

```
Events ──────────► Health
    │                  │
    │    ┌─────────────┘
    │    │ (read only)
    │    ▼
    │  NO WRITING BACK
    │
    └───────────────────► (source of truth)
```

### What This Prevents

1. **Circular Dependencies**: Events → Health → Events → Health...
2. **Data Corruption**: Health accidentally modifying event history
3. **Complexity**: Two-way sync is error-prone

### What This Enables

1. **Simplicity**: Health is a read-only view
2. **Testability**: Health can be recalculated from events at any time
3. **Auditability**: Events remain the source of truth

## Frontend Views

### Health Dashboard
- Summary cards (healthy, degraded, critical counts)
- Asset health table with filters
- Health score and status for each asset

### Health Badge Component
- Compact display of health status
- Color-coded (green/yellow/red)
- Optional score display

## What Health Is NOT

1. **Not Source of Truth** - Events are
2. **Not Alerts** - No notifications
3. **Not Automation** - No automatic remediation
4. **Not Real-time** - Calculated on-demand
5. **Not ML-based** - Pure rule-based (currently)

## Future Considerations

- **ML-based Health**: Machine learning for anomaly detection
- **Predictive Health**: Forecast health based on trends
- **Composite Health**: Health of systems, not just assets
- **Health History**: Track health over time
- **Custom Calculations**: Configurable health algorithms

## Consequences

### Positive
- Simple rule-based calculation
- Always synchronized with events
- Easy to understand and debug
- Read-only (can't corrupt source of truth)

### Negative
- Additional database table
- Health recalculation on every event change
- No historical tracking of health changes

### Neutral
- Health is only as accurate as event data
- No real-time updates (calculated on demand)
- Rule-based (no ML yet)

## Why Not Calculate Health at Query Time?

We could calculate health on-the-fly when queried, but storing it provides:

1. **Performance**: Faster queries for dashboards
2. **History**: Could track health over time (future)
3. **Consistency**: Same calculation every time

However, we ensure recalculation is always available to handle:
- Missing health records
- Stale data
- Debugging scenarios