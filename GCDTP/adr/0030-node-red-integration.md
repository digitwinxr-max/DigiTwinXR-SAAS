# ADR-0030: Node-RED Integration Layer

## Status

Accepted

## Context

GCDTP has implemented comprehensive business logic in FastAPI:
- Asset management
- Work orders
- Documents
- Security
- Timeline Engine
- Cesium 3D visualization

We need external workflow orchestration for:
- Workflow automation
- Connectors to external systems
- Event routing
- Integration with IoT and SCADA systems

### The Decision

Introduce Node-RED as an **external orchestration layer** while **FastAPI remains authoritative** for business logic.

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTEGRATION ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  FastAPI (Authoritative)         Node-RED (Orchestration)       │
│  ┌─────────────────────┐        ┌─────────────────────┐        │
│  │                     │        │                     │        │
│  │  Business Logic     │  ←→   │  Workflows          │        │
│  │  Data Models        │        │  Connectors         │        │
│  │  Validators         │        │  Automation         │        │
│  │  EventBus           │        │  External Systems   │        │
│  │                     │        │                     │        │
│  └─────────────────────┘        └─────────────────────┘        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Decision

Create Node-RED Integration Layer:

```
backend/src/integrations/node_red/
├── node_red_client.py      # Node-RED API client
├── workflow_adapter.py      # FastAPI bridge
├── flow_manager.py         # Flow management
├── connector_registry.py    # Connector types
├── workflow_types.py        # Core types
├── workflow_validator.py    # Validation
└── __init__.py
```

## Key Principle

**FastAPI remains authoritative for all business logic.**

Node-RED provides only:
- Workflow orchestration
- Connector management
- External system integration
- Event routing

No business logic migration to Node-RED.

## Supported Triggers

| Trigger | Description |
|---------|-------------|
| EventBus | GCDTP EventBus events |
| Timeline | Timeline Engine events |
| Manual | User-triggered |
| Scheduled | Cron-based execution |
| Asset Events | Asset lifecycle |
| Work Order Events | Work order lifecycle |
| Document Events | Document lifecycle |

## Supported Connectors

| Connector | Description |
|-----------|-------------|
| HTTP | HTTP requests |
| REST | REST API calls |
| Webhook | Webhook delivery |
| File | File operations |
| Email | Email notifications (metadata) |
| MQTT | IoT messaging (future) |
| GeoServer | GIS integration (future) |
| EMQX | MQTT broker (future) |

## Workflow Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    WORKFLOW LIFECYCLE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CREATE ──→ ENABLE ──→ EXECUTE ──→ COMPLETE                    │
│     │          │          │           │                          │
│     │          │          ▼           ▼                          │
│     │          │      RUNNING ──→ FAILED ──→ RETRY              │
│     │          │          │                                   │
│     │          │          ▼                                   │
│     └─────── DISABLE ──→ CANCELLED                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Database Schema

### workflow_definitions

```sql
CREATE TABLE workflow_definitions (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    flow_json JSONB NOT NULL,
    trigger_type trigger_type,
    trigger_config JSONB,
    is_enabled BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

### workflow_instances

```sql
CREATE TABLE workflow_instances (
    id UUID PRIMARY KEY,
    workflow_id UUID REFERENCES workflow_definitions(id),
    status execution_status,
    input_data JSONB,
    output_data JSONB,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    retry_count INTEGER
);
```

## EventBus Integration

Workflow events published to Timeline Engine:

- WORKFLOW_CREATED
- WORKFLOW_STARTED
- WORKFLOW_COMPLETED
- WORKFLOW_FAILED
- WORKFLOW_CANCELLED
- WORKFLOW_RETRIED

## Consequences

### Positive

1. **External orchestration** - Node-RED handles workflow automation
2. **Connectors** - Easy integration with external systems
3. **Event routing** - Route events to workflows
4. **Timeline integration** - All workflows tracked in timeline
5. **No logic migration** - Business logic stays in FastAPI

### Negative

1. **Node-RED dependency** - Requires Node-RED deployment
2. **Dual management** - Two systems to maintain
3. **Complexity** - More moving parts

### Neutral

1. **FastAPI authoritative** - No business logic changes
2. **Additive only** - Existing features unchanged
3. **Async integration** - Event-driven communication

## Acceptance Criteria

- [x] Node-RED client for API communication
- [x] Workflow adapter for FastAPI bridge
- [x] Flow manager for lifecycle management
- [x] Connector registry for external integrations
- [x] Workflow validator
- [x] All trigger types supported
- [x] All connector types supported
- [x] EventBus integration
- [x] Timeline integration
- [x] Database migration
- [x] 50+ tests
- [x] ADR documentation
