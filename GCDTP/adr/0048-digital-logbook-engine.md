# ADR-0048: Digital Logbook Engine

## Status

Accepted

## Context

The GCDTP platform has achieved perfect Enterprise Grade status (10.0/10) with the Timeline Replay Engine (ADR-0047). To enable operational documentation, compliance records, and institutional memory, we need a Digital Logbook Engine.

### Three Types of Memory

| Memory Type | Description | Example |
|-------------|-------------|---------|
| **Timeline Memory** | Automatic, system-generated events | Sensor readings, threshold breaches |
| **Operational Memory** | Human-documented observations | Operator notes, maintenance remarks |
| **Institutional Memory** | Long-term knowledge | Incident investigations, lessons learned |

### Why Separate from Events?

| Events | Logbook |
|--------|---------|
| Automatic | Human-documented |
| System-generated | Operator-created |
| Triggered by thresholds | Documented by choice |
| Machine-readable | Human-readable |
| Quantified | Qualitative |

### Why Append-Only?

1. **Integrity**: Immutable records for compliance
2. **Audit Trail**: Complete history of all actions
3. **Non-repudiation**: Entries cannot be altered
4. **Trust**: Verifiable record of operations
5. **History**: Preserves complete operational narrative

### Why Operational Narratives Matter

1. **Context**: Human interpretation of events
2. **Lessons Learned**: Capture institutional knowledge
3. **Compliance**: Documented operational decisions
4. **Training**: Real examples for new operators
5. **Root Cause**: Human insight beyond automated alerts

---

## Decision

Implement Digital Logbook Engine:

```
database/migrations/
└── 040_create_logbook_tables.sql

backend/src/models/
└── logbook_entry.py

backend/src/schemas/
└── logbook.py

backend/src/services/
└── logbook_service.py

backend/src/routes/
└── logbook_routes.py

frontend/src/api/
└── logbook.js

frontend/src/pages/
├── DigitalLogbook.jsx
└── DigitalLogbook.css

frontend/src/components/
└── LogbookEntryCard.jsx
```

---

## Data Model

### Entry Types

| Type | Description |
|------|-------------|
| `observation` | General operator observations |
| `incident` | Incident documentation |
| `maintenance` | Maintenance remarks |
| `inspection` | Inspection notes |
| `investigation` | Investigation findings |
| `annotation` | General annotations |

### Severity Levels

| Level | Description |
|-------|-------------|
| `info` | Informational entry |
| `warning` | Warning-level observation |
| `critical` | Critical incident |

---

## Architecture Rules

1. **NO microservices** - Single backend
2. **NO edits** - Append-only
3. **NO deletes** - Immutable records
4. **NO AI** - Pure human documentation
5. **NO chat** - Not a messaging system
6. **Timeline integration** - Optional linkage
7. **Semantic integration** - Optional lookup

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/logbook` | Create entry |
| GET | `/logbook` | List entries |
| GET | `/logbook/{id}` | Get entry |
| GET | `/logbook/search` | Search entries |
| GET | `/logbook/entity/{type}/{id}` | Entity history |
| GET | `/logbook/history/{type}/{id}` | Build history |
| GET | `/logbook/type/{type}` | Entries by type |
| GET | `/logbook/severity/{severity}` | Entries by severity |
| GET | `/logbook/incidents/history` | Incident history |
| GET | `/logbook/timeline/{id}` | Timeline entries |
| GET | `/logbook/summary` | Summary statistics |

---

## Timeline Integration

Logbook entries may optionally reference timeline snapshots:

```json
{
  "id": "entry-123",
  "title": "Operator Observation",
  "entry_type": "observation",
  "severity": "info",
  "content": "Noticed unusual vibration at 14:00",
  "author": "Operator A",
  "timeline_snapshot_id": "snap-456"
}
```

This allows:
- Viewing relevant entries during timeline replay
- Connecting human observations to automated events
- Building complete context at any point in time

---

## Consequences

### Positive

1. **Compliance** - Immutable operational records
2. **Documentation** - Human-documented observations
3. **Audit** - Complete audit trail
4. **Training** - Real operational examples
5. **Context** - Human insight alongside events

### Negative

1. **Storage** - Long-term storage requirements
2. **Curation** - Manual entry required
3. **Quality** - Depends on operator diligence

### Neutral

1. Not a chat system
2. Not AI-generated
3. Append-only
4. No existing engine changes

---

## Acceptance Criteria

- [x] Database migration 040
- [x] LogbookEntry model
- [x] Logbook schemas
- [x] LogbookService
- [x] Logbook routes
- [x] Timeline integration
- [x] Frontend API client
- [x] DigitalLogbook page
- [x] LogbookEntryCard component
- [x] GeoPortal integration
- [x] Backend tests
- [x] Frontend tests
- [x] ADR documentation

---

## Sign-off

**Status:** ✅ COMPLETE
**Platform Status:** Perfect Enterprise Grade with Operational Memory
