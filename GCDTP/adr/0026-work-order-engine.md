# ADR-0026: Work Order Engine

## Status

Accepted

## Context

After implementing the Operational Timeline Engine (ADR-0025), GCDTP has comprehensive event recording and replay capabilities. However, there is no mechanism to track maintenance activities linked to specific assets.

### The Gap

```
Asset
    ↓
(no work order tracking)
    ↓
Maintenance happens...
    ↓
(but nothing is recorded in the system)
```

### The Need

We need to track:

```
Asset
    ↓
Inspection (scheduled, findings recorded)
    ↓
Maintenance (preventive, corrective)
    ↓
Work Order (complete lifecycle tracking)
```

This creates a complete asset maintenance history.

## Decision

Create the Work Order Engine:

```
backend/src/services/work_orders/
├── work_order_types.py       # Core types
├── work_order_engine.py      # Main engine
├── inspection_engine.py      # Inspection workflow
├── maintenance_engine.py    # Maintenance workflow
├── work_order_validator.py   # Validation
└── __init__.py
```

## Core Types

### WorkOrder

```python
@dataclass
class WorkOrder:
    id: str
    asset_id: str
    title: str
    description: str
    priority: Priority  # low, medium, high, critical
    status: WorkOrderStatus  # pending, in_progress, completed, cancelled, on_hold
    category: WorkOrderCategory  # inspection, preventive, corrective, emergency, routine
    assigned_to: Optional[str]
    created_by: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    due_date: Optional[datetime]
```

### Priority

```python
class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
```

### WorkOrderCategory

```python
class WorkOrderCategory(str, Enum):
    INSPECTION = "inspection"
    PREVENTIVE = "preventive"
    CORRECTIVE = "coroner"
    EMERGENCY = "emergency"
    ROUTINE = "routine"
```

## Workflows

### Work Order Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    WORK ORDER LIFECYCLE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  PENDING ──→ IN_PROGRESS ──→ COMPLETED                          │
│     │             │                                             │
│     │             ▼                                             │
│     └───────→ ON_HOLD ───→ IN_PROGRESS                          │
│                                                                  │
│     ▼                                                          │
│  CANCELLED                                                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Inspection Workflow

```
Work Order (category=inspection)
    ↓
Create InspectionTask
    ↓
Define Checklist
    ↓
Execute Inspection
    ↓
Complete Checklist Items
    ↓
Record Findings
    ↓
Set Condition Rating (1-5)
    ↓
Add Recommendations
    ↓
Schedule Next Inspection
```

### Maintenance Workflow

```
Work Order (category=preventive/corrective)
    ↓
Create MaintenanceTask
    ↓
Start Task
    ↓
Record Failure Symptoms (if corrective)
    ↓
Add Parts
    ↓
Perform Work
    ↓
Record Root Cause
    ↓
Complete Task
    ↓
Calculate Costs
```

## Database Schema

### work_orders table

```sql
CREATE TABLE work_orders (
    id UUID PRIMARY KEY,
    asset_id UUID REFERENCES assets(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority work_order_priority DEFAULT 'medium',
    status work_order_status DEFAULT 'pending',
    category work_order_category DEFAULT 'routine',
    assigned_to VARCHAR(255),
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    due_date TIMESTAMP,
    estimated_hours DECIMAL,
    actual_hours DECIMAL,
    notes TEXT,
    metadata JSONB
);
```

### inspection_tasks table

```sql
CREATE TABLE inspection_tasks (
    id UUID PRIMARY KEY,
    work_order_id UUID REFERENCES work_orders(id),
    asset_id UUID REFERENCES assets(id),
    inspection_type VARCHAR(100),
    checklist JSONB,
    inspector VARCHAR(255),
    findings TEXT,
    condition_rating INTEGER,  -- 1-5
    next_inspection_date TIMESTAMP
);
```

### maintenance_tasks table

```sql
CREATE TABLE maintenance_tasks (
    id UUID PRIMARY KEY,
    work_order_id UUID REFERENCES work_orders(id),
    asset_id UUID REFERENCES assets(id),
    maintenance_type VARCHAR(100),
    parts_used JSONB,
    labor_hours DECIMAL,
    technician VARCHAR(255),
    failure_symptoms TEXT,
    root_cause TEXT,
    corrective_action TEXT,
    cost DECIMAL
);
```

## EventBus Integration

The Work Order Engine publishes events to the EventBus:

### Work Order Events

- WORK_ORDER_CREATED
- WORK_ORDER_ASSIGNED
- WORK_ORDER_STARTED
- WORK_ORDER_COMPLETED
- WORK_ORDER_CANCELLED
- WORK_ORDER_STATUS_CHANGED
- WORK_ORDER_PRIORITY_CHANGED

### Inspection Events

- INSPECTION_CREATED
- INSPECTION_COMPLETED

### Maintenance Events

- MAINTENANCE_CREATED
- MAINTENANCE_STARTED
- MAINTENANCE_COMPLETED
- MAINTENANCE_CANCELLED

## Asset-Centric Design

All work orders are linked to assets:

```
Asset A
    ├── Work Order #1 (inspection)
    ├── Work Order #2 (preventive maintenance)
    └── Work Order #3 (corrective maintenance)

Asset B
    ├── Work Order #4 (routine)
    └── Work Order #5 (emergency)
```

This enables:

- Asset maintenance history
- Maintenance cost tracking
- Condition-based maintenance
- Compliance reporting

## Validation Rules

### Status Transitions

```
PENDING → IN_PROGRESS, CANCELLED, ON_HOLD
IN_PROGRESS → COMPLETED, CANCELLED, ON_HOLD
ON_HOLD → IN_PROGRESS, CANCELLED
COMPLETED → (terminal)
CANCELLED → (terminal)
```

### Priority Handling

- Priority can be changed at any time
- Critical priority triggers notifications
- Priority affects scheduling

## Consequences

### Positive

1. **Complete maintenance tracking** - Full lifecycle visibility
2. **Asset-centric** - All work orders linked to assets
3. **Compliance ready** - Audit trail for regulations
4. **Event integration** - Timeline replay includes work orders
5. **Inspection support** - Checklists, findings, ratings

### Negative

1. **Additional complexity** - More entities to manage
2. **Data entry overhead** - Requires user input
3. **Integration points** - Users, notifications, etc.

### Neutral

1. **Database migration required** - New tables
2. **No external dependencies** - Pure Python
3. **Preserves architecture** - Follows existing patterns

## Acceptance Criteria

- [x] Work order creation and management
- [x] Status transitions
- [x] Priority handling
- [x] Asset linkage
- [x] Inspection tasks with checklists
- [x] Maintenance tasks with parts/labor
- [x] Validation rules
- [x] EventBus integration
- [x] Database migration
- [x] 30+ tests
- [x] ADR documentation
