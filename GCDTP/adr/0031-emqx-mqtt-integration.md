# ADR-0031: EMQX MQTT Integration Layer

## Status

Accepted

## Context

GCDTP needs to ingest telemetry from IoT devices and sensors. We need:
- Real-time telemetry ingestion
- Device connectivity management
- Topic-based routing
- Scalable message handling

### The Decision

Introduce EMQX MQTT broker as an **external telemetry layer** while **FastAPI remains authoritative** for business logic.

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTEGRATION ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  IoT Devices         EMQX MQTT           FastAPI                 │
│  ┌─────────┐        ┌─────────┐        ┌─────────┐            │
│  │ Sensors  │───────→│ Broker  │───────→│ Business │            │
│  │ Devices  │        │ Topics  │        │ Logic   │            │
│  └─────────┘        │ QoS     │        │ EventBus │            │
│                     └─────────┘        └─────────┘            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Decision

Create EMQX MQTT Integration Layer:

```
backend/src/integrations/emqx/
├── mqtt_client.py           # MQTT broker client
├── mqtt_types.py            # Core types
├── topic_registry.py        # Topic management
├── subscription_manager.py  # Subscription handling
├── message_router.py        # Message routing
├── device_registry.py       # Device management
├── mqtt_validator.py       # Validation
└── __init__.py
```

## Key Principle

**FastAPI remains authoritative for all business logic.**

EMQX provides only:
- Telemetry ingestion
- Topic routing
- Device connectivity
- QoS management

No business logic in EMQX.

## Supported QoS Levels

| Level | Name | Description |
|-------|------|-------------|
| 0 | At most once | Fire and forget |
| 1 | At least once | Acknowledgment |
| 2 | Exactly once | Handshake |

## Supported Events

| Event Type | Topic Pattern |
|------------|--------------|
| Sensor measurements | gc/measurements/{device_id} |
| Asset events | gc/assets/{asset_id}/events |
| Health events | gc/health/{asset_id} |
| Work order events | gc/workorders/{id} |
| Document events | gc/documents/{id} |
| Timeline events | gc/timeline/{session_id} |
| Simulation events | gc/simulation/{id} |

## Topic Hierarchy

```
gc/
├── measurements/
│   └── {device_id}
├── devices/
│   ├── {device_id}/
│   │   ├── commands/
│   │   └── status/
├── assets/
│   ├── {asset_id}/
│   │   ├── events/
│   │   ├── alerts/
│   │   └── status/
├── health/
├── workorders/
├── documents/
├── simulation/
└── timeline/
```

## Message Routing

Messages are routed to FastAPI services:

- **Measurements** → Measurement Engine
- **Asset Events** → EventBus
- **Health Events** → Health Engine
- **Simulation** → Simulation Engine
- **Timeline** → Timeline Engine
- **All** → EventBus (for logging)

## Database Schema

### devices

```sql
CREATE TABLE devices (
    id UUID PRIMARY KEY,
    device_id VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    type VARCHAR(100),
    status connection_status,
    qos qos_level,
    last_connected_at TIMESTAMP,
    last_message_at TIMESTAMP
);
```

### mqtt_topics

```sql
CREATE TABLE mqtt_topics (
    id UUID PRIMARY KEY,
    topic_name VARCHAR(500) UNIQUE,
    qos qos_level,
    is_enabled BOOLEAN,
    is_system BOOLEAN
);
```

## EventBus Integration

Device events published to Timeline Engine:

- DEVICE_REGISTERED
- DEVICE_CONNECTED
- DEVICE_DISCONNECTED
- MQTT_MESSAGE_RECEIVED
- MQTT_TOPIC_CREATED
- MQTT_TOPIC_UPDATED

## Consequences

### Positive

1. **Real-time telemetry** - Ingest sensor data in real-time
2. **Device management** - Track device connectivity
3. **Topic routing** - Organize messages by topic
4. **QoS support** - Reliable message delivery
5. **Scalable** - EMQX handles millions of connections

### Negative

1. **EMQX dependency** - Requires EMQX deployment
2. **Protocol lock-in** - MQTT only
3. **Complexity** - More infrastructure

### Neutral

1. **FastAPI authoritative** - No business logic changes
2. **Additive only** - Existing features unchanged
3. **Event-driven** - Async communication

## Acceptance Criteria

- [x] MQTT client for broker communication
- [x] Topic registry for topic management
- [x] Subscription manager for subscriptions
- [x] Message router for routing
- [x] Device registry for device management
- [x] MQTT validator
- [x] All QoS levels supported
- [x] Wildcard subscriptions
- [x] EventBus integration
- [x] Timeline integration
- [x] Database migration
- [x] 60+ tests
- [x] ADR documentation
