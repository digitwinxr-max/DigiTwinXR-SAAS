# ADR-0011: Event Engine

## Status

Accepted

## Context

GCDTP has implemented:
1. **Measurement Engine** (ADR-0008) - Stores sensor measurements
2. **Threshold Engine** (ADR-0010) - Evaluates measurements against rules

We now need to persist the outcomes of threshold evaluations. This layer stores events generated from threshold violations.

## Why Events, Not Alerts?

### System Memory vs. User Alerts

The Event Engine stores **system memory** - a record of what happened in the system. This is different from **alerts** which are notifications sent to users.

```
┌─────────────────┐
│  Measurements   │  ← Raw sensor data (ADR-0008)
├─────────────────┤
│  Evaluation     │  ← Threshold checking (ADR-0010)
├─────────────────┤
│  Events         │  ← System memory of violations (ADR-0011) ← THIS ADR
├─────────────────┤
│  Alerts         │  ← User notifications (Future)
└─────────────────┘
```

### Why This Separation?

1. **Historical Analysis** - Events can be queried, analyzed, and reported on
2. **Audit Trail** - Keep a record of all threshold violations
3. **Performance Tracking** - Track how often thresholds are violated
4. **Debugging** - Understand system behavior over time
5. **No Notifications Yet** - Events are stored, not pushed

## Decision

We will implement an Event Engine that:

1. **Stores events** from threshold evaluations
2. **Links events** to sensors, assets, and threshold rules
3. **Supports resolution** - Mark events as resolved
4. **Filters by status** - ACTIVE vs RESOLVED events
5. **No notifications** - Pure storage, no alert sending

## Database Schema

```sql
CREATE TABLE events (
    id UUID PRIMARY KEY,
    sensor_id UUID REFERENCES sensors(id),
    asset_id UUID REFERENCES assets(id),  -- Derived from sensor
    event_type VARCHAR(100),              -- THRESHOLD_VIOLATION
    severity VARCHAR(20),                 -- WARNING, CRITICAL
    message TEXT,
    value DOUBLE PRECISION,
    threshold_rule_id UUID REFERENCES threshold_rules(id),
    timestamp TIMESTAMP,
    status VARCHAR(20),                  -- ACTIVE, RESOLVED
    created_at TIMESTAMP
);
```

## Event Creation Logic

```python
def create_event_from_evaluation(evaluation_result, measurement):
    # Only create events for WARNING or CRITICAL
    if evaluation_result.status == "OK":
        return None  # No event for OK
    
    # Create event with links to sensor, asset, and rule
    event = Event(
        sensor_id=measurement.sensor_id,
        asset_id=get_asset_from_sensor(measurement.sensor_id),
        severity=evaluation_result.status,
        message=evaluation_result.message,
        value=measurement.value,
        threshold_rule_id=evaluation_result.rule_id,
        timestamp=measurement.timestamp,
    )
    return event
```

## API Design

### Event Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /events/manual | Create event manually |
| POST | /events/from-evaluation | Create event from threshold evaluation |
| GET | /events | List events (with filtering) |
| GET | /events/active | List only active events |
| GET | /events/{id} | Get event by ID |
| PATCH | /events/{id}/resolve | Mark event as resolved |
| GET | /events/sensor/{id} | Get events for sensor |
| GET | /events/asset/{id} | Get events for asset |

### Event Response Schema

```json
{
  "id": "uuid",
  "sensor_id": "uuid",
  "asset_id": "uuid",
  "event_type": "THRESHOLD_VIOLATION",
  "severity": "WARNING",
  "message": "Temperature exceeded warning threshold",
  "value": 28.5,
  "threshold_rule_id": "uuid",
  "timestamp": "2026-06-16T10:00:00Z",
  "status": "ACTIVE",
  "created_at": "2026-06-16T10:00:00Z"
}
```

## Event Schema

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| sensor_id | UUID | FK to sensors |
| asset_id | UUID | FK to assets (derived from sensor) |
| event_type | VARCHAR | THRESHOLD_VIOLATION |
| severity | VARCHAR | WARNING, CRITICAL |
| message | TEXT | Human-readable message |
| value | DOUBLE | Measurement value |
| threshold_rule_id | UUID | FK to threshold_rules |
| timestamp | TIMESTAMP | When the event occurred |
| status | VARCHAR | ACTIVE, RESOLVED |
| created_at | TIMESTAMP | When the event was created |

## Status Lifecycle

```
┌─────────┐      ┌───────────┐
│ ACTIVE  │ ──→  │ RESOLVED  │
└─────────┘      └───────────┘
     PATCH /events/{id}/resolve
```

Events start as **ACTIVE** and can be marked as **RESOLVED**.

## Severity Levels

| Severity | Meaning | Color |
|----------|---------|-------|
| WARNING | Value outside warning thresholds | Yellow |
| CRITICAL | Value outside critical thresholds | Red |

## Frontend Views

### Event List
- All events with filtering by status, severity, sensor, asset
- Sort by timestamp (newest first)

### Active Events
- Only ACTIVE events
- Summary cards showing counts by severity
- Quick resolve action

### Event Details
- Full event information
- Resolution form with notes
- Links to related sensor, asset, and rule

## Future: Alert System Integration

Events are designed to integrate with a future alert system:

```python
# Future: Alert generation (not implemented yet)
def on_event_created(event):
    if event.severity == "CRITICAL":
        create_alert(
            alert_type="email",
            recipient="ops-team@example.com",
            message=f"CRITICAL event: {event.message}",
        )
    elif event.severity == "WARNING":
        create_alert(
            alert_type="log",
            message=f"WARNING event: {event.message}",
        )
```

The alert system can:
- Send notifications (email, SMS, Slack)
- Create dashboards
- Trigger webhooks
- Auto-resolve based on conditions

## What Events Are NOT

1. **Not Alerts** - Events are stored, not pushed to users
2. **Not Actions** - No notifications, no webhooks, no automation
3. **Not Real-time** - No WebSocket streaming
4. **Not Acknowledgments** - Just status tracking (ACTIVE/RESOLVED)

## Consequences

### Positive
- Historical record of threshold violations
- Queryable event history for analysis
- Clear separation from notification system
- Foundation for future alert system

### Negative
- Additional database table and storage
- Need to manage event lifecycle (active → resolved)
- No real-time notifications yet

### Neutral
- Events don't automatically resolve
- No automatic cleanup of old events
- No event aggregation or deduplication

## Future Considerations

- **Event Aggregation**: Group similar events to reduce noise
- **Auto-Resolution**: Automatically resolve when value returns to normal
- **Retention Policy**: Delete or archive old events
- **Event Deduplication**: Don't create duplicate events for same condition
- **Alert Integration**: Send notifications based on events
- **Event Priorities**: Different handling for different severities
- **Event Categories**: Beyond THRESHOLD_VIOLATION (system events, etc.)