# ADR-0015: System-Wide Event Propagation Hardening

## Status

Accepted

## Context

GCDTP has implemented multiple engines that generate events:
1. **Measurement Engine** - Creates measurements
2. **Threshold Engine** - Evaluates measurements against rules
3. **Event Engine** - Stores threshold violations
4. **Health Engine** - Calculates asset health from events

Each engine currently operates independently without a standardized event system. This creates:
- Inconsistent event handling across services
- No centralized view of system activity
- Difficulty in debugging event flow
- Risk of missed events or race conditions

## Decision

We will implement a centralized event propagation system with:

1. **Central Event Registry** - Standardized event type constants
2. **Event Payload Schema** - Uniform event structure
3. **Centralized Event Dispatcher** - Single entry point for all events
4. **Unified Frontend Event Client** - Standardized event handling on client

## Why Event Standardization?

### Problem: Inconsistent Event Handling

Without standardization:
```
MeasurementService → arbitrary event calls
ThresholdService → arbitrary event calls
EventService → arbitrary event calls
HealthService → arbitrary event calls
```

Each service has its own way of handling events, making:
- Debugging difficult
- Adding new event consumers complex
- Event flow hard to trace

### Solution: Centralized Event System

```
┌──────────────────────────────────────────────┐
│           Event Dispatcher (Singleton)         │
├──────────────────────────────────────────────┤
│  emit(event_type, source, payload)          │
│  subscribe(event_types, callback)           │
└──────────────────────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
Measurement    Threshold       Event
Service       Service         Service
    │               │               │
    └───────────────┼───────────────┘
                    ▼
              All Events
```

## Event Types Registry

### Why Constants, Not Strings?

Using string literals anywhere in code leads to:
- Typos that are hard to debug
- No IDE autocomplete
- No refactoring support

### Approved Event Types

```python
class EventType(str, Enum):
    MEASUREMENT_CREATED = "measurement.created"
    THRESHOLD_EVALUATED = "threshold.evaluated"
    EVENT_CREATED = "event.created"
    EVENT_RESOLVED = "event.resolved"
    HEALTH_UPDATED = "health.updated"
    ASSET_UPDATED = "asset.updated"
    SENSOR_CREATED = "sensor.created"
    SENSOR_UPDATED = "sensor.updated"
    SENSOR_DELETED = "sensor.deleted"
```

### Rule: No String Literals

```python
# WRONG
emit("event.created", ...)

# CORRECT
emit(EventType.EVENT_CREATED, ...)
```

## Event Payload Schema

### Standard Structure

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

### Why This Structure?

| Field | Purpose |
|-------|---------|
| event_id | Unique identifier for deduplication |
| event_type | Event classification |
| timestamp | When event occurred |
| source | Which service generated it |
| correlation_id | Link related events |
| asset_id | Associated asset (if applicable) |
| sensor_id | Associated sensor (if applicable) |
| payload | Event-specific data |

### Enforced Validation

```python
def validate_event_structure(event_data: Dict) -> bool:
    required_fields = ["event_id", "event_type", "timestamp", "source"]
    for field in required_fields:
        if field not in event_data:
            raise ValueError(f"Missing required field: {field}")
    return True
```

## Centralized Event Dispatcher

### Why Single Entry Point?

The dispatcher is the ONLY way to emit events:

```python
# WRONG - Direct notification
subscriber.callback(event)

# CORRECT - Via dispatcher
emit(EventType.EVENT_CREATED, source="EventService", payload={...})
```

### Benefits

1. **Traceability** - All events go through one place
2. **Logging** - Every emission is logged
3. **Debugging** - Easy to add breakpoints
4. **Consistency** - Same behavior everywhere

### Dispatcher Features

```python
class EventDispatcher:
    # Single emit function
    def emit(self, event_type, source, payload, asset_id=None, sensor_id=None):
        ...
    
    # Subscribe to events
    def subscribe(self, callback, event_types, asset_id=None, sensor_id=None):
        ...
```

### Thread Safety

The dispatcher must be thread-safe:

```python
self._subscriptions_lock = threading.Lock()
self._history_lock = threading.Lock()

def emit(self, ...):
    with self._subscriptions_lock:
        for subscription in self._subscriptions:
            subscription.callback(event)
```

### Event History

```python
# Store last 1000 events
def get_event_history(self, event_type=None, limit=100):
    events = self._event_history
    if event_type:
        events = [e for e in events if e.event_type == event_type]
    return events[-limit:]
```

## Service Integration

### All Services Must Use Dispatcher

```
┌─────────────────────────────────────────────────────┐
│                   Services                            │
├─────────────────────────────────────────────────────┤
│ MeasurementService                                   │
│   → emit(MEASUREMENT_CREATED, ...) on create        │
│                                                      │
│ ThresholdService                                     │
│   → emit(THRESHOLD_EVALUATED, ...) on evaluate      │
│                                                      │
│ EventService                                         │
│   → emit(EVENT_CREATED, ...) on create              │
│   → emit(EVENT_RESOLVED, ...) on resolve            │
│                                                      │
│ HealthService                                        │
│   → emit(HEALTH_UPDATED, ...) on recalculate        │
└─────────────────────────────────────────────────────┘
```

### Example: EventService

```python
def create_event(self, event_data: EventCreate) -> Event:
    # ... create event in database ...
    
    # Emit event via dispatcher
    emit(
        event_type=EventType.EVENT_CREATED,
        source="EventService",
        payload={
            "event_id": str(event.id),
            "severity": event.severity,
        },
        asset_id=event.asset_id,
        sensor_id=event.sensor_id,
    )
    
    return event
```

## Frontend Event Client

### Unified Client

```javascript
import eventClient, { EVENT_TYPES } from './events/eventClient';

// Subscribe to events
const unsubscribe = eventClient.subscribe(
  [EVENT_TYPES.EVENT_CREATED, EVENT_TYPES.EVENT_RESOLVED],
  (event) => {
    // Handle event
  },
  { asset_id: 'optional-filter' }
);

// Handle incoming event
eventClient.handleEvent(backendEvent);

// Cleanup
unsubscribe();
```

### Features

1. **Deduplication** - Skip duplicate event_ids
2. **Normalization** - Standard event structure
3. **Immutability** - Events are frozen objects
4. **Caching** - Last 100 events stored

## Event Consistency Rules

### Frontend Assumptions

The frontend must assume:

1. **Events are Immutable**
   ```javascript
   // Events cannot be modified
   const frozen = Object.freeze({ ...event });
   ```

2. **Events May Arrive Out of Order**
   ```javascript
   // Sort by timestamp if ordering matters
   events.sort((a, b) => a.timestamp - b.timestamp);
   ```

3. **Duplicate Events Must Be Ignored**
   ```javascript
   if (seenEventIds.has(event.event_id)) {
     return; // Skip duplicate
   }
   ```

4. **Missing Events Must Not Break UI**
   ```javascript
   // Handle missing data gracefully
   const healthScore = healthData?.[assetId]?.health_score ?? 100;
   ```

## useSystemEvents Hook

### Standard Hook Pattern

```javascript
import { useSystemEvents, EVENT_TYPES } from './hooks/useSystemEvents';

function MyComponent() {
  useSystemEvents(
    [EVENT_TYPES.EVENT_CREATED, EVENT_TYPES.HEALTH_UPDATED],
    (event) => {
      // Handle event
    },
    { asset_id: optionalFilter }
  );
  
  // ...
}
```

### Backwards Compatibility

```javascript
// Old hook still works
import { useEventBus } from './hooks/useEventBus';

// New hook
import { useSystemEvents } from './hooks/useSystemEvents';
```

## Why Event Immutability?

### Problem: Shared State

```javascript
// DANGEROUS - Shared mutation
const handleEvent = (event) => {
  event.payload.value = 42; // Mutates original!
};
```

### Solution: Frozen Copies

```javascript
// SAFE - Immutable
const handleEvent = (event) => {
  const frozen = Object.freeze({ ...event });
  // frozen cannot be modified
};
```

## Event Flow Diagram

```
┌─────────────┐     emit()      ┌─────────────────┐
│ Measurement │ ──────────────▶│                 │
│   Service   │                 │   Dispatcher     │
└─────────────┘                 │                 │
                               │  ┌───────────┐  │
┌─────────────┐     emit()    │  │  History  │  │
│ Threshold   │ ──────────────▶│  └───────────┘  │
│   Service   │                 │        │         │
└─────────────┘                 │        ▼         │
                               │  ┌───────────┐  │
┌─────────────┐     emit()    │  │Subscribers│  │
│   Event     │ ──────────────▶│  └───────────┘  │
│   Service   │                 └────────┬────────┘
└─────────────┘                          │
                                          ▼
                               ┌─────────────────┐
                               │ Frontend Client │
                               │  - Deduplicate  │
                               │  - Normalize    │
                               │  - Freeze       │
                               │  - Cache        │
                               └────────┬────────┘
                                        │
                                        ▼
                               ┌─────────────────┐
                               │   useSystemEvents│
                               │     Hook         │
                               └─────────────────┘
```

## Consequences

### Positive

1. **Traceability** - All events through single dispatcher
2. **Debugging** - Easy to add logging/breakpoints
3. **Consistency** - Same event structure everywhere
4. **Testability** - Easy to mock dispatcher
5. **Scalability** - Thread-safe implementation

### Negative

1. **Complexity** - Additional abstraction layer
2. **Overhead** - Small performance cost for dispatching
3. **Coupling** - Services depend on dispatcher

### Neutral

1. **Memory** - Event history consumes memory
2. **Sync** - In-memory only (no persistence)

## Why No External Message Brokers?

### Constraints

- No Kafka, Redis, MQTT, or similar
- In-memory only
- No external dependencies

### Rationale

1. **Simplicity** - Reduce infrastructure complexity
2. **Performance** - In-memory is faster for local events
3. **Reliability** - Fewer failure points
4. **Cost** - No external services needed

### Future Consideration

If distributed systems are needed later:
```javascript
// Future: Add message broker adapter
class WebSocketDispatcher extends EventDispatcher {
  emit(event) {
    super.emit(event);
    this.ws.broadcast(event);
  }
}
```

## No AI, No Alerts, No Automation

This ADR is about **event propagation**, not:
- AI/ML processing
- Alert notifications
- Automated responses
- Analytics

Those are future concerns that will build on this foundation.

## Implementation Checklist

- [x] Central Event Registry (event_types.py)
- [x] Event Payload Schema (event_schema.py)
- [x] Event Dispatcher (event_dispatcher.py)
- [x] Service Integration (all services)
- [x] Frontend Event Client (eventClient.js)
- [x] useSystemEvents Hook
- [x] Backend Tests
- [x] Frontend Tests

## Future Considerations

1. **WebSocket Bridge** - Forward events to frontend
2. **Event Persistence** - Store events in database
3. **Event Aggregation** - Batch similar events
4. **Event Filtering** - Server-side filtering
5. **Dead Letter Queue** - Handle failed events