# DigiTwinXR-SAAS Route Graph

**Version:** 1.0.0
**Generated:** 2026-06-21

---

## API Topology Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API GATEWAY                                     │
│                              (FastAPI)                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
        ▼                             ▼                             ▼
┌───────────────┐           ┌─────────────────┐           ┌─────────────────┐
│  /assets     │           │   /sensors      │           │  /measurements  │
│  /events     │           │   /thresholds   │           │  /health        │
│  /scenarios  │           │   /recovery     │           │  /network       │
└───────────────┘           └─────────────────┘           └─────────────────┘
        │                             │                             │
        ▼                             ▼                             ▼
┌───────────────┐           ┌─────────────────┐           ┌─────────────────┐
│  /timeline    │           │   /logbook      │           │  /semantic      │
│  /knowledge   │           │   /rag          │           │  /cognitive     │
│  /resilience  │           │   /copilot      │           │  /agents        │
└───────────────┘           └─────────────────┘           └─────────────────┘
```

---

## Route Groups Summary

| Router | Prefix | Route Count | Description |
|--------|--------|-------------|-------------|
| agent_routes | `/agents` | 8 | Agent framework |
| asset_routes | `/assets` | 12 | Asset management |
| asset_relationship_routes | `/relationships` | 6 | Asset relationships |
| cognitive_routes | `/cognitive` | 8 | Cognitive twin AI |
| copilot_routes | `/copilot` | 6 | Copilot sessions |
| event_routes | `/events` | 8 | Event management |
| health_routes | `/health` | 8 | Health metrics |
| knowledge_routes | `/knowledge` | 8 | Knowledge repository |
| logbook_routes | `/logbook` | 12 | Digital logbook |
| measurement_routes | `/measurements` | 6 | Sensor measurements |
| network_health_routes | `/network` | 4 | Network health |
| predictive_routes | `/predictive` | 4 | Predictive maintenance |
| propagation_routes | `/propagation` | 2 | Failure propagation |
| rag_routes | `/rag` | 6 | RAG engine |
| recovery_routes | `/recovery` | 8 | Recovery simulations |
| resilience_routes | `/resilience` | 6 | Resilience analysis |
| root_cause_routes | `/root-cause` | 6 | Root cause analysis |
| scenario_routes | `/scenarios` | 8 | Scenario simulations |
| semantic_routes | `/semantic` | 14 | Semantic layer |
| sensor_routes | `/sensors` | 10 | Sensor management |
| threshold_routes | `/thresholds` | 6 | Threshold rules |
| timeline_routes | `/timeline` | 6 | Timeline operations |

**Total Routes:** ~178

---

## Detailed Route Maps

### Agent Routes (`/agents`)

```
/agents
├── GET    /agents                          → List agents
├── GET    /agents/{agent_id}               → Get agent details
├── GET    /agents/frame                    → Get agent frame
├── GET    /agents/types                    → Get agent types
├── POST   /agents/tasks                    → Create task
├── GET    /agents/tasks                    → List tasks
├── GET    /agents/tasks/{task_id}          → Get task
├── POST   /agents/task/{task_id}/approve   → Approve task
├── POST   /agents/task/{task_id}/execute   → Execute task
├── POST   /agents/task/{task_id}/reject    → Reject task
├── GET    /agents/tasks/{task_id}/actions  → Get actions
├── GET    /agents/history                  → Get history
└── GET    /agents/stats                    → Get stats
```

### Asset Routes (`/assets`)

```
/assets
├── GET    /assets                          → List assets
├── POST   /assets                          → Create asset
├── GET    /assets/{asset_id}               → Get asset
├── PUT    /assets/{asset_id}               → Update asset
├── DELETE /assets/{asset_id}               → Delete asset
├── GET    /assets/{asset_id}/sensors       → Get sensors
├── GET    /assets/{asset_id}/events       → Get events
├── GET    /assets/{asset_id}/timeline     → Get timeline
├── GET    /assets/{asset_id}/health        → Get health
├── GET    /assets/{asset_id}/children     → Get children
├── GET    /assets/{asset_id}/parents      → Get parents
├── GET    /assets/{asset_id}/relationships → Get relationships
└── POST   /assets/{asset_id}/recalculate  → Recalculate health
```

### Asset Relationship Routes (`/relationships`)

```
/relationships
├── GET    /relationships                   → List relationships
├── POST   /relationships                   → Create relationship
├── GET    /relationships/{relationship_id} → Get relationship
├── DELETE /relationships/{relationship_id}  → Delete relationship
├── GET    /relationships/graph/{asset_id}  → Get asset graph
└── GET    /relationships/tree/{asset_id}   → Get asset tree
```

### Cognitive Routes (`/cognitive`)

```
/cognitive
├── GET    /cognitive/sessions              → List sessions
├── POST   /cognitive/sessions              → Create session
├── GET    /cognitive/sessions/{session_id} → Get session
├── GET    /cognitive/sessions/{session_id}/history → Get history
├── POST   /cognitive/query                 → Query with context
├── GET    /cognitive/context/{entity_type}/{entity_id} → Get context
├── GET    /ognitive/confidence/{query_id}  → Get confidence
└── GET    /cognitive/frame                 → Get cognitive frame
```

### Copilot Routes (`/copilot`)

```
/copilot
├── GET    /copilot/sessions               → List sessions
├── POST   /copilot/sessions               → Create session
├── GET    /copilot/sessions/{session_id}  → Get session
├── GET    /copilot/sessions/{session_id}/messages → Get messages
├── GET    /copilot/sessions/{session_id}/history  → Get history
└── POST   /copilot/query                  → Query copilot
```

### Event Routes (`/events`)

```
/events
├── GET    /events                          → List events
├── POST   /events                          → Create event
├── GET    /events/{event_id}               → Get event
├── PATCH  /events/{event_id}/resolve      → Resolve event
├── GET    /events/active                   → Get active events
├── GET    /events/{event_id}/timeline      → Get event timeline
├── GET    /events/{event_id}/propagated   → Get propagated events
└── POST   /events/manual                   → Create manual event
```

### Health Routes (`/health`)

```
/health
├── GET    /health/assets                   → List asset health
├── GET    /health/assets/{asset_id}        → Get asset health
├── GET    /health/assets/{asset_id}/summary     → Get summary
├── GET    /health/assets/{asset_id}/contributors → Get contributors
├── GET    /health/assets/{asset_id}/decay       → Get decay
├── GET    /health/assets/high-risk         → Get high risk
├── GET    /health/assets/top-critical      → Get top critical
└── POST   /health/recalculate-all         → Recalculate all
```

### Knowledge Routes (`/knowledge`)

```
/knowledge
├── GET    /knowledge/documents            → List documents
├── POST   /knowledge/documents            → Create document
├── GET    /knowledge/documents/{doc_id}    → Get document
├── DELETE /knowledge/documents/{doc_id}   → Delete document
├── GET    /knowledge/documents/{doc_id}/references → Get references
├── GET    /knowledge/documents/{doc_id}/related    → Get related
├── GET    /knowledge/search                → Search knowledge
└── POST   /knowledge/references           → Create reference
```

### Logbook Routes (`/logbook`)

```
/logbook
├── GET    /logbook                        → List entries
├── POST   /logbook                        → Create entry
├── GET    /logbook/{entry_id}             → Get entry
├── GET    /logbook/author/{author}        → Get by author
├── GET    /logbook/type/{entry_type}      → Get by type
├── GET    /logbook/severity/{severity}    → Get by severity
├── GET    /logbook/summary                → Get summary
├── GET    /logbook/timeline/{timeline_snapshot_id} → Get timeline
├── POST   /logbook/snapshot               → Create snapshot
├── GET    /logbook/range                  → Get range
└── GET    /logbook/search                 → Search
```

### Measurement Routes (`/measurements`)

```
/measurements
├── GET    /measurements                   → List measurements
├── POST   /measurements                   → Create measurement
├── GET    /measurements/{measurement_id}  → Get measurement
├── DELETE /measurements/{measurement_id}  → Delete measurement
├── GET    /measurements/sensor/{sensor_id} → Get by sensor
└── GET    /measurements/history/{sensor_id} → Get history
```

### Network Health Routes (`/network`)

```
/network
├── GET    /network                        → Get network health
├── POST   /network/analyze               → Analyze network
├── GET    /network/resilience             → Get resilience
└── POST   /network/recalculate            → Recalculate network
```

### Predictive Routes (`/predictive`)

```
/predictive
├── GET    /predictive/{asset_id}         → Get prediction
├── POST   /predictive/{asset_id}/run     → Run prediction
├── GET    /predictive/{asset_id}/history → Get history
└── GET    /predictive/probability/{asset_id} → Get probability
```

### Propagation Routes (`/propagation`)

```
/propagation
├── POST   /propagation/{event_id}        → Propagate event
└── GET    /propagation/{event_id}/impacts → Get impacts
```

### RAG Routes (`/rag`)

```
/rag
├── POST   /rag/query                     → Query RAG
├── GET    /rag/models                    → List models
├── GET    /rag/history/{session_id}      → Get history
├── GET    /rag/sources/{query_id}        → Get sources
├── GET    /rag/graph/{query_id}          → Get insight graph
└── GET    /rag/retrieve                  → Retrieve context
```

### Recovery Routes (`/recovery`)

```
/recovery
├── GET    /recovery                       → List simulations
├── POST   /recovery                       → Create simulation
├── GET    /recovery/{recovery_id}         → Get simulation
├── DELETE /recovery/{recovery_id}         → Delete simulation
├── POST   /recovery/{recovery_id}/run     → Run simulation
├── GET    /recovery/{recovery_id}/results → Get results
├── GET    /recovery/{recovery_id}/compare → Compare results
└── GET    /recovery/{recovery_id}/tree    → Get tree
```

### Resilience Routes (`/resilience`)

```
/resilience
├── GET    /resilience/{asset_id}         → Get analysis
├── POST   /resilience/{asset_id}/analyze → Analyze
├── GET    /resilience/{asset_id}/recommendations → Get recommendations
├── GET    /resilience/{analysis_id}/recommendations → Get recommendations
└── GET    /resilience/chains/{analysis_id} → Get chains
```

### Root Cause Routes (`/root-cause`)

```
/root-cause
├── GET    /root-cause/{event_id}         → Get analysis
├── POST   /root-cause/{event_id}/analyze → Analyze
├── GET    /root-cause/{analysis_id}      → Get analysis
├── GET    /root-cause/{analysis_id}/factors → Get factors
├── GET    /root-cause/{analysis_id}/chains   → Get chains
└── GET    /root-cause/chain/{asset_id}      → Get chain
```

### Scenario Routes (`/scenarios`)

```
/scenarios
├── GET    /scenarios                      → List scenarios
├── POST   /scenarios                      → Create scenario
├── GET    /scenarios/{scenario_id}        → Get scenario
├── PUT    /scenarios/{scenario_id}       → Update scenario
├── DELETE /scenarios/{scenario_id}       → Delete scenario
├── POST   /scenarios/{scenario_id}/run   → Run scenario
├── GET    /scenarios/{scenario_id}/results → Get results
├── GET    /scenarios/{scenario_id}/compare → Compare
└── GET    /scenarios/{scenario_id}/impact-tree → Get impact tree
```

### Semantic Routes (`/semantic`)

```
/semantic
├── GET    /semantic/entities             → List entities
├── POST   /semantic/entities             → Create entity
├── GET    /semantic/entity/{entity_id}   → Get entity
├── PUT    /semantic/entity/{entity_id}   → Update entity
├── DELETE /semantic/entity/{entity_id}  → Delete entity
├── GET    /semantic/entity/{entity_type}/{entity_id}/history → Get history
├── GET    /semantic/entity/{entity_type}/{entity_id}/context → Get context
├── GET    /semantic/relationships/{entity_id} → Get relationships
├── POST   /semantic/relationships        → Create relationship
├── GET    /semantic/relationships/{relationship_id} → Get relationship
├── DELETE /semantic/relationships/{relationship_id} → Delete
├── POST   /semantic/tags                 → Create tag
├── GET    /semantic/tags/{entity_id}    → Get tags
├── GET    /semantic/tags/summary         → Get summary
├── GET    /semantic/graph               → Get graph
├── GET    /semantic/search               → Search
└── GET    /semantic/types                → Get types
```

### Sensor Routes (`/sensors`)

```
/sensors
├── GET    /sensors                       → List sensors
├── POST   /sensors                       → Create sensor
├── GET    /sensors/{sensor_id}           → Get sensor
├── PUT    /sensors/{sensor_id}           → Update sensor
├── DELETE /sensors/{sensor_id}           → Delete sensor
├── GET    /sensors/{sensor_id}/measurements → Get measurements
├── GET    /sensors/{sensor_id}/events    → Get events
├── GET    /sensors/{sensor_id}/thresholds → Get thresholds
└── GET    /sensors/categories            → Get categories
```

### Threshold Routes (`/thresholds`)

```
/thresholds
├── GET    /thresholds                    → List rules
├── POST   /thresholds                    → Create rule
├── GET    /thresholds/{rule_id}          → Get rule
├── PUT    /thresholds/{rule_id}          → Update rule
├── DELETE /thresholds/{rule_id}          → Delete rule
└── GET    /thresholds/weights            → Get weights
```

### Timeline Routes (`/timeline`)

```
/timeline
├── GET    /timeline/assets/{asset_id}   → Get asset timeline
├── POST   /timeline/snapshot            → Create snapshot
├── GET    /timeline/playback            → Get playback
├── GET    /timeline/system              → Get system timeline
├── GET    /timeline/range               → Get range
└── GET    /timeline/summary/{entity_type}/{entity_id} → Get summary
```

---

## Route Conflicts (Potential Issues)

### Duplicate Path + Method Combinations

| Path | Method | Files | Risk Level |
|------|--------|-------|------------|
| `/query` | POST | rag_routes, cognitive_routes, copilot_routes | HIGH |
| `/context/{query_id}` | GET | semantic_routes, cognitive_routes | MEDIUM |
| `/asset/{asset_id}` | GET | asset_routes, semantic_routes | MEDIUM |
| `/asset/{asset_id}` | GET | asset_routes, resilience_routes | MEDIUM |
| `/event/{event_id}` | GET | event_routes, root_cause_routes | MEDIUM |

### Note on Route Conflicts

These routes exist on different routers (e.g., `/rag/query` vs `/cognitive/query`), so FastAPI will correctly route based on the mounted router prefix. However, if routers are mounted incorrectly, conflicts may occur.

---

## API Request/Response Flow

```
Client Request
      │
      ▼
┌─────────────┐
│   Router    │ ← Matches prefix (/agents, /assets, etc.)
└─────────────┘
      │
      ▼
┌─────────────┐
│   Route     │ ← Matches path + method
└─────────────┘
      │
      ▼
┌─────────────┐
│   Schema    │ ← Request validation (Pydantic)
└─────────────┘
      │
      ▼
┌─────────────┐
│  Service    │ ← Business logic
└─────────────┘
      │
      ▼
┌─────────────┐
│   Model     │ ← Database operations
└─────────────┘
      │
      ▼
┌─────────────┐
│   Schema    │ ← Response validation (Pydantic)
└─────────────┘
      │
      ▼
   Client Response
```

---

## Route Security Matrix

| Route Group | Authentication | Authorization | Rate Limiting |
|-------------|----------------|---------------|---------------|
| Agents | ✓ | Role-based | Default |
| Assets | ✓ | Asset-based | Default |
| Cognitive | ✓ | Session-based | Default |
| Copilot | ✓ | Session-based | Default |
| Events | ✓ | Event-based | Default |
| Health | ✓ | Asset-based | Default |
| Knowledge | ✓ | Document-based | Default |
| Logbook | ✓ | Entry-based | Default |
| Measurements | ✓ | Sensor-based | Default |
| Network | ✓ | Network-based | Default |
| Predictive | ✓ | Asset-based | Default |
| Propagation | ✓ | Event-based | Default |
| RAG | ✓ | Session-based | Default |
| Recovery | ✓ | Scenario-based | Default |
| Resilience | ✓ | Asset-based | Default |
| Root Cause | ✓ | Event-based | Default |
| Scenarios | ✓ | Scenario-based | Default |
| Semantic | ✓ | Entity-based | Default |
| Sensors | ✓ | Sensor-based | Default |
| Thresholds | ✓ | Rule-based | Default |
| Timeline | ✓ | Asset-based | Default |

---

## Response Time SLAs

| Route Group | Typical Latency | P99 Target |
|-------------|-----------------|------------|
| Agents | < 200ms | < 500ms |
| Assets | < 100ms | < 300ms |
| Cognitive | < 2s | < 5s |
| Copilot | < 2s | < 5s |
| Events | < 100ms | < 300ms |
| Health | < 500ms | < 1s |
| Knowledge | < 500ms | < 1s |
| Logbook | < 200ms | < 500ms |
| Measurements | < 100ms | < 300ms |
| Network | < 1s | < 2s |
| Predictive | < 2s | < 5s |
| Propagation | < 500ms | < 1s |
| RAG | < 2s | < 5s |
| Recovery | < 5s | < 10s |
| Resilience | < 2s | < 5s |
| Root Cause | < 2s | < 5s |
| Scenarios | < 5s | < 10s |
| Semantic | < 500ms | < 1s |
| Sensors | < 100ms | < 300ms |
| Thresholds | < 100ms | < 300ms |
| Timeline | < 500ms | < 1s |
