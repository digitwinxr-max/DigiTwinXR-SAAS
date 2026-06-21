# Route Ownership Matrix

**Generated:** 2026-06-21
**Repository:** DigiTwinXR-SAAS
**Branch:** feature/tasks-024-029-extensible-architecture
**Phase:** 3 - Canonical Domain Ownership

---

## Executive Summary

This document assigns canonical ownership domains for all API routes. Evidence is derived from filesystem inspection only. **No code modifications were made.**

---

## Ownership Classification

| Role | Description |
|------|-------------|
| OWNER | Primary service responsible for route |
| CONSUMER | Service that calls this route |
| DEPENDENCY | Service that this route depends on |
| CROSS_DOMAIN | Access across domain boundaries |

---

## Phase 1: Domain Ownership Assignment

### Domain: Agent Framework

**Owner:** Agent Service
**Prefix:** `/agent`
**Route File:** `agent_routes.py`

| Route | Ownership | Consumers |
|-------|-----------|-----------|
| `GET /agents` | OWNER | Frontend, Copilot |
| `GET /agents/{id}` | OWNER | Frontend |
| `POST /tasks` | OWNER | Copilot, Cognitive |
| `POST /task/{id}/approve` | OWNER | Frontend |
| `POST /task/{id}/execute` | OWNER | Frontend |
| `POST /task/{id}/reject` | OWNER | Frontend |

**Dependencies:** Asset Service, Sensor Service
**Cross-domain access:** Yes (Cognitive, Copilot)

---

### Domain: Asset Management

**Owner:** Asset Service
**Prefix:** `/assets`
**Route File:** `asset_routes.py`

| Route | Ownership | Consumers |
|-------|-----------|-----------|
| `GET /assets` | OWNER | Frontend, Health, Events |
| `POST /assets` | OWNER | Frontend |
| `GET /assets/{id}` | OWNER | All domains |
| `PUT /assets/{id}` | OWNER | Frontend |
| `DELETE /assets/{id}` | OWNER | Frontend |
| `GET /assets/{id}/sensors` | OWNER | Frontend |
| `GET /assets/{id}/events` | OWNER | Events |
| `GET /assets/{id}/timeline` | OWNER | Timeline |
| `GET /assets/{id}/health` | OWNER | Health |

**Dependencies:** Sensor Service, Event Service, Health Service
**Cross-domain access:** Yes (Health, Events, Timeline)

---

### Domain: Asset Relationships

**Owner:** Asset Relationship Service
**Prefix:** `/relationships`
**Route File:** `asset_relationship_routes.py`

| Route | Ownership | Consumers |
|-------|-----------|-----------|
| `GET /relationships` | OWNER | Frontend, Resilience |
| `POST /relationships` | OWNER | Frontend |
| `GET /relationships/{id}` | OWNER | Frontend |
| `DELETE /relationships/{id}` | OWNER | Frontend |
| `GET /relationships/graph/{id}` | OWNER | Frontend, Resilience |
| `GET /relationships/tree/{id}` | OWNER | Frontend |

**Dependencies:** Asset Service
**Cross-domain access:** Yes (Resilience)

---

### Domain: Cognitive Twin

**Owner:** Cognitive Twin Service
**Prefix:** `/cognitive`
**Route File:** `cognitive_routes.py`

| Route | Ownership | Consumers |
|-------|-----------|-----------|
| `GET /sessions` | OWNER | Frontend |
| `POST /sessions` | OWNER | Frontend |
| `GET /sessions/{id}` | OWNER | Frontend |
| `POST /query` | OWNER | Frontend, Copilot |
| `GET /context/{id}` | OWNER | RAG |
| `GET /context/{type}/{id}` | OWNER | RAG, Semantic |
| `GET /confidence/{id}` | OWNER | RAG |

**Dependencies:** RAG Service, Semantic Service, Agent Service
**Cross-domain access:** Yes (RAG, Semantic)

---

### Domain: Copilot

**Owner:** Copilot Service
**Prefix:** `/copilot`
**Route File:** `copilot_routes.py`

| Route | Ownership | Consumers |
|-------|-----------|-----------|
| `GET /sessions` | OWNER | Frontend |
| `POST /sessions` | OWNER | Frontend |
| `GET /sessions/{id}` | OWNER | Frontend |
| `GET /sessions/{id}/messages` | OWNER | Frontend |
| `POST /query` | OWNER | Frontend, Cognitive |

**Dependencies:** Cognitive Service, Agent Service
**Cross-domain access:** Yes (Cognitive)

---

### Domain: Events

**Owner:** Event Service
**Prefix:** `/events`
**Route File:** `event_routes.py`

| Route | Ownership | Consumers |
|-------|-----------|-----------|
| `GET /events` | OWNER | Frontend, Health |
| `POST /events` | OWNER | Sensors, Propagation |
| `GET /events/{id}` | OWNER | Frontend |
| `PATCH /events/{id}/resolve` | OWNER | Frontend |
| `GET /events/active` | OWNER | Frontend |
| `POST /events/manual` | OWNER | Frontend |

**Dependencies:** Asset Service, Propagation Service
**Cross-domain access:** Yes (Propagation, Health)

---

### Domain: Health Engine

**Owner:** Health Service
**Prefix:** `/health` ⚠️ **COLLISION**
**Route File:** `health_routes.py`

| Route | Ownership | Consumers |
|-------|-----------|-----------|
| `GET /health/assets` | OWNER | Frontend |
| `GET /health/assets/{id}` | OWNER | Frontend, Asset |
| `GET /health/assets/{id}/summary` | OWNER | Frontend |
| `GET /health/assets/{id}/contributors` | OWNER | Frontend |
| `GET /health/assets/high-risk` | OWNER | Frontend |
| `POST /health/recalculate/{id}` | OWNER | Frontend |
| `POST /health/recalculate-all` | OWNER | Frontend |

**Dependencies:** Asset Service, Sensor Service
**Cross-domain access:** Yes (Network Health)

---

### Domain: Knowledge Repository

**Owner:** Knowledge Service
**Prefix:** `/knowledge`
**Route File:** `knowledge_routes.py`

| Route | Ownership | Consumers |
|-------|-----------|-----------|
| `GET /documents` | OWNER | Frontend, RAG |
| `POST /documents` | OWNER | Frontend |
| `GET /documents/{id}` | OWNER | Frontend, RAG |
| `GET /documents/{id}/references` | OWNER | Frontend |
| `GET /search` | OWNER | Frontend, RAG |

**Dependencies:** Semantic Service, RAG Service
**Cross-domain access:** Yes (RAG)

---

### Domain: Digital Logbook

**Owner:** Logbook Service
**Prefix:** `/logbook`
**Route File:** `logbook_routes.py`

| Route | Ownership | Consumers |
|-------|-----------|-----------|
| `GET /logbook` | OWNER | Frontend |
| `POST /logbook` | OWNER | Frontend, Events |
| `GET /logbook/{id}` | OWNER | Frontend |
| `GET /logbook/search` | OWNER | Frontend |
| `GET /logbook/summary` | OWNER | Frontend |
| `POST /logbook/snapshot` | OWNER | Timeline |

**Dependencies:** Timeline Service
**Cross-domain access:** Yes (Timeline)

---

### Domain: Measurements

**Owner:** Measurement Service
**Prefix:** `/measurements`
**Route File:** `measurement_routes.py`

| Route | Ownership | Consumers |
|-------|-----------|-----------|
| `GET /measurements` | OWNER | Frontend, Sensors |
| `POST /measurements` | OWNER | Sensors |
| `GET /measurements/{id}` | OWNER | Frontend |
| `GET /measurements/sensor/{id}` | OWNER | Frontend |

**Dependencies:** Sensor Service
**Cross-domain access:** No

---

### Domain: Network Health ⚠️ **COLLISION**

**Owner:** Network Health Service
**Prefix:** `/health` ⚠️ **COLLISION**
**Route File:** `network_health_routes.py`

| Route | Ownership | Consumers |
|-------|-----------|-----------|
| `GET /health/network` | OWNER | Frontend |
| `POST /health/analyze-network` | OWNER | Frontend |
| `POST /health/recalculate-network` | OWNER | Frontend |

**Recommended Prefix:** `/network`
**Dependencies:** Health Service, Topology Service
**Cross-domain access:** Yes (Health)

---

### Domain: Predictive Maintenance

**Owner:** Predictive Maintenance Service
**Prefix:** `/predictive`
**Route File:** `predictive_routes.py`

| Route | Ownership | Consumers |
|-------|-----------|-----------|
| `GET /{id}` | OWNER | Frontend |
| `POST /{id}/run` | OWNER | Frontend |
| `GET /{id}/history` | OWNER | Frontend |
| `GET /{id}/probability` | OWNER | Frontend |

**Dependencies:** Asset Service, Health Service
**Cross-domain access:** No

---

### Domain: Failure Propagation

**Owner:** Failure Propagation Service
**Prefix:** `/propagation`
**Route File:** `propagation_routes.py`

| Route | Ownership | Consumers |
|-------|-----------|-----------|
| `POST /{event_id}` | OWNER | Event Service |
| `GET /{event_id}/impacts` | OWNER | Frontend, Resilience |
| `GET /asset/{id}` | OWNER | Resilience |
| `GET /chain/{id}` | OWNER | Frontend |

**Dependencies:** Event Service, Asset Service, Resilience Service
**Cross-domain access:** Yes (Resilience, Event)

---

### Domain: RAG Engine

**Owner:** RAG Service
**Prefix:** `/rag`
**Route File:** `rag_routes.py`

| Route | Ownership | Consumers |
|-------|-----------|-----------|
| `POST /query` | OWNER | Frontend, Copilot, Cognitive |
| `GET /models` | OWNER | Frontend |
| `GET /history/{id}` | OWNER | Frontend |
| `GET /sources/{id}` | OWNER | Frontend |
| `GET /retrieve` | OWNER | Cognitive |

**Dependencies:** Knowledge Service, Semantic Service
**Cross-domain access:** Yes (Cognitive, Copilot)

---

### Domain: Recovery Simulations

**Owner:** Recovery Simulation Service
**Prefix:** `/recovery`
**Route File:** `recovery_routes.py`

| Route | Ownership | Consumers |
|-------|-----------|-----------|
| `GET /recovery` | OWNER | Frontend |
| `POST /recovery` | OWNER | Frontend |
| `GET /recovery/{id}` | OWNER | Frontend |
| `POST /recovery/{id}/run` | OWNER | Frontend |
| `GET /recovery/{id}/results` | OWNER | Frontend |

**Dependencies:** Asset Service
**Cross-domain access:** No

---

### Domain: Resilience Analysis

**Owner:** Resilience Service
**Prefix:** `/resilience`
**Route File:** `resilience_routes.py`

| Route | Ownership | Consumers |
|-------|-----------|-----------|
| `GET /{id}` | OWNER | Frontend |
| `POST /{id}/analyze` | OWNER | Frontend |
| `GET /{id}/recommendations` | OWNER | Frontend |
| `GET /impacts` | OWNER | Frontend, Propagation |

**Dependencies:** Asset Service, Propagation Service
**Cross-domain access:** Yes (Propagation)

---

### Domain: Root Cause Analysis

**Owner:** Root Cause Service
**Prefix:** `/root-cause`
**Route File:** `root_cause_routes.py`

| Route | Ownership | Consumers |
|-------|-----------|-----------|
| `GET /{event_id}` | OWNER | Frontend |
| `POST /{event_id}/analyze` | OWNER | Frontend |
| `GET /{id}/factors` | OWNER | Frontend |
| `GET /{id}/chains` | OWNER | Frontend |

**Dependencies:** Event Service, Propagation Service
**Cross-domain access:** Yes (Propagation)

---

### Domain: Scenario Simulations

**Owner:** Simulation Service
**Prefix:** `/scenarios`
**Route File:** `scenario_routes.py`

| Route | Ownership | Consumers |
|-------|-----------|-----------|
| `GET /scenarios` | OWNER | Frontend |
| `POST /scenarios` | OWNER | Frontend |
| `GET /scenarios/{id}` | OWNER | Frontend |
| `POST /scenarios/{id}/run` | OWNER | Frontend |
| `GET /scenarios/{id}/results` | OWNER | Frontend |

**Dependencies:** Asset Service
**Cross-domain access:** No

---

### Domain: Semantic Layer

**Owner:** Semantic Service
**Prefix:** `/semantic`
**Route File:** `semantic_routes.py`

| Route | Ownership | Consumers |
|-------|-----------|-----------|
| `GET /entities` | OWNER | Frontend, RAG |
| `POST /entities` | OWNER | Frontend |
| `GET /entity/{id}` | OWNER | Frontend, RAG, Cognitive |
| `POST /relationships` | OWNER | Frontend |
| `GET /relationships/{id}` | OWNER | Frontend |
| `POST /tags` | OWNER | Frontend |
| `GET /graph` | OWNER | Frontend, RAG |
| `GET /search` | OWNER | Frontend |

**Dependencies:** RAG Service, Cognitive Service
**Cross-domain access:** Yes (RAG, Cognitive)

---

### Domain: Sensors

**Owner:** Sensor Service
**Prefix:** `/sensors`
**Route File:** `sensor_routes.py`

| Route | Ownership | Consumers |
|-------|-----------|-----------|
| `GET /sensors` | OWNER | Frontend, Asset |
| `POST /sensors` | OWNER | Frontend |
| `GET /sensors/{id}` | OWNER | Frontend |
| `PUT /sensors/{id}` | OWNER | Frontend |
| `GET /sensors/{id}/measurements` | OWNER | Frontend |
| `GET /sensors/{id}/events` | OWNER | Frontend |
| `GET /sensors/{id}/thresholds` | OWNER | Frontend |

**Dependencies:** Asset Service, Measurement Service
**Cross-domain access:** No

---

### Domain: Threshold Rules

**Owner:** Threshold Service
**Prefix:** `/thresholds`
**Route File:** `threshold_routes.py`

| Route | Ownership | Consumers |
|-------|-----------|-----------|
| `GET /thresholds` | OWNER | Frontend, Sensors |
| `POST /thresholds` | OWNER | Frontend |
| `GET /thresholds/{id}` | OWNER | Frontend, Sensors |
| `PUT /thresholds/{id}` | OWNER | Frontend |
| `DELETE /thresholds/{id}` | OWNER | Frontend |

**Dependencies:** Sensor Service
**Cross-domain access:** No

---

### Domain: Timeline

**Owner:** Timeline Service
**Prefix:** `/timeline`
**Route File:** `timeline_routes.py`

| Route | Ownership | Consumers |
|-------|-----------|-----------|
| `GET /timeline/assets/{id}` | OWNER | Frontend |
| `GET /timeline/system` | OWNER | Frontend |
| `POST /timeline/snapshot` | OWNER | Logbook |
| `GET /timeline/playback` | OWNER | Frontend |
| `GET /timeline/range` | OWNER | Frontend |

**Dependencies:** Asset Service, Logbook Service
**Cross-domain access:** Yes (Logbook)

---

## Phase 2: Cross-Domain Dependencies

### Cross-Domain Map

```
┌─────────────────────────────────────────────────────────────────┐
│                      CROSS-DOMAIN DEPENDENCIES                    │
└─────────────────────────────────────────────────────────────────┘

Agent ──────┬──────► Cognitive ──────► Semantic
            │              │
            │              ▼
            └──────► Copilot ◄─────► RAG ──────► Knowledge
                         │
                         ▼
                      Frontend
                         │
     ┌─────────┬─────────┼─────────┬─────────┬─────────┐
     ▼         ▼         ▼         ▼         ▼         ▼
  Asset    Events    Sensors    Health   Timeline   Recovery
     │         │         │         │         │         │
     ▼         ▼         ▼         ▼         ▼         ▼
Relationships Propagation Predic- Resilience Timeline  Scenarios
     │         │         tive
     ▼         ▼         ▼
  Resilience  Root Cause
```

---

## Phase 3: Dependency Summary

| Domain | Owns | Consumes From | Cross-Domain |
|--------|------|---------------|--------------|
| Agent | /agent | Asset, Sensor | Yes |
| Asset | /assets | Sensor, Event | Yes |
| Cognitive | /cognitive | RAG, Semantic, Agent | Yes |
| Copilot | /copilot | Cognitive, Agent | Yes |
| Events | /events | Asset, Propagation | Yes |
| Health | /health | Asset, Sensor | Yes |
| Knowledge | /knowledge | Semantic, RAG | Yes |
| Logbook | /logbook | Timeline | Yes |
| Network Health | /health ⚠️ | Health, Topology | Yes |
| Predictive | /predictive | Asset, Health | Yes |
| Propagation | /propagation | Event, Asset, Resilience | Yes |
| RAG | /rag | Knowledge, Semantic | Yes |
| Recovery | /recovery | Asset | No |
| Resilience | /resilience | Asset, Propagation | Yes |
| Root Cause | /root-cause | Event, Propagation | Yes |
| Scenarios | /scenarios | Asset | No |
| Semantic | /semantic | RAG, Cognitive | Yes |
| Sensors | /sensors | Asset, Measurement | No |
| Threshold | /thresholds | Sensor | No |
| Timeline | /timeline | Asset, Logbook | Yes |

---

## Phase 4: Ownership Conflicts

### Conflict 1: /health Prefix

| File | Current Prefix | Recommended Prefix | Status |
|------|---------------|-------------------|--------|
| health_routes.py | `/health` | `/health` | OK |
| network_health_routes.py | `/health` | `/network` | ⚠️ COLLISION |

**Resolution:** Rename `network_health_routes.py` to `/network`

---

## No Code Modifications Made

Per Task 080E constraints, **no code modifications were made**. This is an observation report only.

---

## Next Steps

- Proceed to Phase 4: API Topology
