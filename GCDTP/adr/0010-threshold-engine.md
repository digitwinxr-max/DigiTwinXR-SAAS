# ADR-0010: Threshold Engine

## Status

Accepted

## Context

GCDTP sensors generate measurements over time. We need a way to evaluate whether those measurements are within acceptable ranges. This evaluation layer is designed to exist **before** the event system.

## Why a Rule-Based Evaluation Layer?

### Separation of Concerns

The GCDTP architecture follows a layered approach:

```
┌─────────────────┐
│  Measurements   │  ← Data collection (Task 006)
├─────────────────┤
│  Evaluation     │  ← Rule-based threshold checking (Task 008)
├─────────────────┤
│  Events         │  ← Future: event generation from evaluations
├─────────────────┤
│  Actions        │  ← Future: notifications, alerts, etc.
└─────────────────┘
```

### Why Not Skip Directly to Events?

1. **Testability** - Rules can be tested independently
2. **Reusability** - Same rules can be used for multiple purposes
3. **Flexibility** - Easy to change what happens with evaluations
4. **Performance** - Evaluation is synchronous and fast
5. **Debugging** - Easy to understand what rules triggered

## Decision

We will implement a Threshold Engine that:

1. **Stores rules** - Threshold rules with warning/critical ranges
2. **Evaluates measurements** - Returns OK/WARNING/CRITICAL status
3. **Supports global rules** - Rules without sensor_id apply to all sensors
4. **No event generation** - Pure evaluation layer only

## Database Schema

```sql
CREATE TABLE threshold_rules (
    id UUID PRIMARY KEY,
    sensor_id UUID REFERENCES sensors(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    rule_type VARCHAR(50) DEFAULT 'range',
    warning_min DOUBLE PRECISION,
    warning_max DOUBLE PRECISION,
    critical_min DOUBLE PRECISION,
    critical_max DOUBLE PRECISION,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP
);
```

## Rule Types

### range
Default rule type. Evaluates if value is within acceptable range.

### static
Future support for static value comparisons (e.g., equals, not equals).

## Evaluation Logic

```python
def evaluate(value, rule):
    # Check critical thresholds first
    if rule.critical_min and value < rule.critical_min:
        return "CRITICAL"
    if rule.critical_max and value > rule.critical_max:
        return "CRITICAL"
    
    # Check warning thresholds
    if rule.warning_min and value < rule.warning_min:
        return "WARNING"
    if rule.warning_max and value > rule.warning_max:
        return "WARNING"
    
    return "OK"
```

## API Design

### Threshold Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /thresholds | Create a new threshold rule |
| GET | /thresholds | List all rules (with filtering) |
| GET | /thresholds/{id} | Get rule by ID |
| PUT | /thresholds/{id} | Update a rule |
| DELETE | /thresholds/{id} | Delete a rule |
| GET | /thresholds/sensor/{id} | Get rules for sensor |

### Evaluation Endpoint

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /thresholds/evaluate | Evaluate a measurement |

### Evaluation Request

```json
{
  "sensor_id": "uuid",
  "value": 25.5,
  "measurement_id": "uuid"
}
```

### Evaluation Response

```json
{
  "status": "OK|WARNING|CRITICAL",
  "rule_id": "uuid",
  "sensor_id": "uuid",
  "rule_name": "Rule Name",
  "message": "Value 25.5 triggered WARNING threshold"
}
```

## Threshold Rule Schema

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| sensor_id | UUID | FK to sensors (nullable for global rules) |
| name | VARCHAR | Rule name |
| rule_type | VARCHAR | range or static |
| warning_min | DOUBLE | Warning threshold minimum |
| warning_max | DOUBLE | Warning threshold maximum |
| critical_min | DOUBLE | Critical threshold minimum |
| critical_max | DOUBLE | Critical threshold maximum |
| is_active | BOOLEAN | Whether rule is active |
| created_at | TIMESTAMP | Creation time |

## Global vs Sensor-Specific Rules

### Sensor-Specific Rules
- `sensor_id` points to a specific sensor
- Only applies to that sensor's measurements
- Example: "Temperature Sensor 1 should stay below 30°C"

### Global Rules
- `sensor_id` is NULL
- Applies to all sensors (unless overridden by sensor-specific rule)
- Example: "All temperature sensors should warn above 35°C"

## Priority

When both global and sensor-specific rules exist:
1. Check sensor-specific rules first
2. Return the most severe status
3. Global rules serve as defaults

## Future Event System Integration

This threshold engine is designed to integrate with a future event system:

```python
# Future: Event generation (not implemented yet)
def on_measurement_created(measurement):
    result = evaluate_measurement(measurement.sensor_id, measurement.value)
    if result.status != "OK":
        create_event(
            event_type="threshold_violation",
            measurement_id=measurement.id,
            evaluation_result=result,
        )
```

The event system can:
- Subscribe to evaluation results
- Generate notifications
- Trigger alerts
- Update dashboards
- Trigger automated actions

## Decision Made By

GCDTP Core Team

## Date

2026-06-16

## Consequences

### Positive
- Clear separation between data and evaluation
- Rules are reusable and testable
- Easy to add new rule types
- Fast synchronous evaluation
- Ready for future event system

### Negative
- Additional database table
- Additional API complexity
- Rules must be managed separately from measurements

### Neutral
- No events generated yet (future work)
- No automatic threshold suggestions
- No ML-based anomaly detection

## Future Considerations

- **Event system**: Generate events from evaluation results
- **Notification channels**: Email, SMS, Slack, etc.
- **Alert acknowledgments**: Mark alerts as acknowledged
- **Threshold templates**: Predefined rules for common sensor types
- **ML-based detection**: Anomaly detection beyond fixed thresholds
- **Historical analysis**: Track threshold violations over time