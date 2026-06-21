# API Topology

**Generated:** 2026-06-21
**Repository:** DigiTwinXR-SAAS
**Branch:** feature/tasks-024-029-extensible-architecture
**Phase:** 4 - API Topology

---

## Executive Summary

This document shows the API topology including layers, routes, dependencies, shared endpoints, and potential bottlenecks. Evidence is derived from filesystem inspection only. **No code modifications were made.**

---

## API Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        API LAYER (FastAPI)                        │
│                        178 Routes, 22 Route Files                  │
└─────────────────────────────────────────────────────────────────┘
                                     │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
        ▼                             ▼                             ▼
┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│  DOMAIN ROUTES    │     │  ANALYTICS ROUTES │     │  AI ROUTES        │
│                   │     │                   │     │                   │
│ /assets           │     │ /health           │     │ /rag              │
│ /sensors          │     │ /resilience       │     │ /cognitive        │
│ /events           │     │ /predictive       │     │ /copilot          │
│ /measurements     │     │ /propagation      │     │ /agent            │
│ /thresholds       │     │ /root-cause       │     │                   │
└───────────────────┘     └───────────────────┘     └───────────────────┘
        │                             │                             │
        └─────────────────────────────┼─────────────────────────────┘
                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER (50 Services)                  │
│                                                                 │
│  AssetService         HealthService        RAGService             │
│  SensorService       ResilienceService    CognitiveService         │
│  EventService       PropagationService    AgentService            │
│  MeasurementService RootCauseService     CopilotService          │
└─────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                       MODEL LAYER (38 Models)                    │
│                                                                 │
│  Asset, Sensor, Event, Measurement, Threshold, Health              │
│  Scenario, Recovery, Resilience, RAG*, Cognitive*                │
└─────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER (PostgreSQL)                   │
│                                                                 │
│  TimescaleDB (hypertable)    PostGIS (spatial)                  │
│  37 migrations               54 ADRs                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Route Layer Details

### Layer 1: Core Domain Routes

| Prefix | Routes | Services | Bottleneck Risk |
|--------|--------|----------|----------------|
| `/assets` | 8 | AssetService | LOW |
| `/sensors` | 10 | SensorService | LOW |
| `/events` | 10 | EventService | MEDIUM |
| `/measurements` | 6 | MeasurementService | MEDIUM |
| `/thresholds` | 7 | ThresholdService | LOW |
| `/relationships` | 8 | AssetRelationshipService | LOW |

### Layer 2: Analytics Routes

| Prefix | Routes | Services | Bottleneck Risk |
|--------|--------|----------|----------------|
| `/health` ⚠️ | 9 | HealthService | HIGH |
| `/network` ⚠️ | 4 | NetworkHealthService | HIGH |
| `/resilience` | 6 | ResilienceService | MEDIUM |
| `/predictive` | 8 | PredictiveService | MEDIUM |
| `/propagation` | 5 | PropagationService | HIGH |
| `/root-cause` | 6 | RootCauseService | MEDIUM |

### Layer 3: AI Routes

| Prefix | Routes | Services | Bottleneck Risk |
|--------|--------|----------|----------------|
| `/rag` | 7 | RAGService | HIGH |
| `/cognitive` | 9 | CognitiveService | HIGH |
| `/copilot` | 6 | CopilotService | HIGH |
| `/agent` | 13 | AgentService | HIGH |

### Layer 4: Knowledge Routes

| Prefix | Routes | Services | Bottleneck Risk |
|--------|--------|----------|----------------|
| `/semantic` | 19 | SemanticService | MEDIUM |
| `/knowledge` | 8 | KnowledgeService | LOW |
| `/logbook` | 12 | LogbookService | MEDIUM |
| `/timeline` | 6 | TimelineService | MEDIUM |

### Layer 5: Simulation Routes

| Prefix | Routes | Services | Bottleneck Risk |
|--------|--------|----------|----------------|
| `/scenarios` | 10 | SimulationService | HIGH |
| `/recovery` | 8 | RecoveryService | HIGH |

---

## Dependencies Map

### Asset Service Dependencies

```
AssetService
├── Asset Relationship Service (for relationships)
├── Sensor Service (for sensors)
├── Event Service (for events)
├── Health Service (for health)
├── Timeline Service (for snapshots)
└── Knowledge Service (for documents)
```

### Health Service Dependencies

```
HealthService
├── Asset Service (for asset data)
├── Sensor Service (for sensor data)
├── Threshold Service (for thresholds)
└── Network Health Service (for network topology)
```

### RAG Service Dependencies

```
RAGService
├── Knowledge Service (for documents)
├── Semantic Service (for entities)
├── Cognitive Service (for context)
└── Timeline Service (for historical)
```

### Propagation Service Dependencies

```
PropagationService
├── Event Service (for events)
├── Asset Service (for relationships)
├── Resilience Service (for impacts)
└── Root Cause Service (for analysis)
```

---

## Shared Endpoints Analysis

### Shared /asset Endpoints

| Route | Owner | Shared By |
|-------|-------|-----------|
| `/assets/{id}` | AssetService | All domains |
| `/assets/{id}/sensors` | AssetService | SensorService |
| `/assets/{id}/events` | AssetService | EventService |
| `/assets/{id}/timeline` | AssetService | TimelineService |
| `/assets/{id}/health` | AssetService | HealthService |

**Impact:** AssetService is a critical bottleneck

### Shared /context Endpoints

| Route | Owner | Shared By |
|-------|-------|-----------|
| `/rag/context/{id}` | RAGService | CognitiveService |
| `/cognitive/context/{id}` | CognitiveService | RAGService |
| `/semantic/context/{id}` | SemanticService | RAG, Cognitive |

**Impact:** SemanticService provides shared context

---

## Potential Bottlenecks

### High-Traffic Endpoints

| Endpoint | Traffic | Bottleneck Type |
|----------|---------|----------------|
| `/assets` | HIGH | Database query |
| `/health/assets` | HIGH | Health calculation |
| `/rag/query` | HIGH | LLM inference |
| `/cognitive/query` | HIGH | LLM inference |
| `/measurements` | HIGH | Time-series data |
| `/events` | MEDIUM | Event stream |

### Critical Path Analysis

```
HIGH TRAFFIC CRITICAL PATH:

/measurements ──► /sensors ──► /assets ──► /health
    │               │            │           │
    ▼               ▼            ▼           ▼
TimescaleDB    PostgreSQL   PostgreSQL   Health Calc
(Write)        (Read)       (Read)       (Compute)
```

---

## Service Layer Topology

### Core Services (50 total)

| Category | Services | Count |
|----------|---------|-------|
| Domain | Asset, Sensor, Event, Measurement, Threshold | 5 |
| Analytics | Health, Resilience, Propagation, RootCause | 4 |
| AI | RAG, Cognitive, Copilot, Agent | 4 |
| Simulation | Scenario, Recovery | 2 |
| Knowledge | Semantic, Knowledge, Logbook, Timeline | 4 |
| Integration | GeoServer, NodeRED, EMQX | 3 |
| Support | Topology, Routing, Flow | 3 |
| Document | Document, Attachment | 2 |
| WorkOrder | WorkOrder, Maintenance, Inspection | 3 |
| Other | 20+ | 20 |

---

## Database Topology

### TimescaleDB Hypertable

```
measurements
├── time (time column)
├── sensor_id (partition key)
├── value
├── quality
└── INDEX on (sensor_id, time)
```

### PostGIS Tables

```
spatial_assets
├── geometry (PostGIS geometry)
├── crs
├── asset_id
└── spatial_index (GiST)
```

### Key Tables

| Table | Type | Routes |
|-------|------|--------|
| assets | Standard | All routes |
| sensors | Standard | /sensors, /assets |
| measurements | TimescaleDB | /measurements |
| events | Standard | /events |
| health_scores | Standard | /health |
| semantic_entities | Standard | /semantic |

---

## API Topology Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND CLIENTS                                  │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        FASTAPI GATEWAY                                    │
│                      (178 Routes, 22 Routers)                           │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│ CORE DOMAIN   │         │   ANALYTICS   │         │     AI        │
│               │         │               │         │               │
│ /assets      │         │ /health       │         │ /rag          │
│ /sensors     │         │ /resilience   │         │ /cognitive    │
│ /events      │         │ /predictive   │         │ /copilot      │
│ /measurements │         │ /propagation  │         │ /agent        │
│ /thresholds  │         │ /root-cause   │         │               │
└───────┬───────┘         └───────┬───────┘         └───────┬───────┘
        │                         │                         │
        └─────────────────────────┼─────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          SERVICE LAYER                                   │
│                          (50 Services)                                   │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           MODEL LAYER                                    │
│                          (38 Models)                                     │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATABASE LAYER                                   │
│                                                                          │
│   PostgreSQL + TimescaleDB + PostGIS                                      │
│                                                                          │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│   │  Assets  │  │ Sensors  │  │Measure- │  │ Health   │              │
│   │          │  │          │  │ments    │  │ Scores   │              │
│   │  (std)   │  │  (std)   │  │(hypertable)│ │  (std)   │              │
│   └──────────┘  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Bottleneck Summary

| Component | Risk Level | Reason |
|-----------|------------|--------|
| AssetService | 🟡 MEDIUM | Central hub for all domains |
| HealthService | 🔴 HIGH | Expensive calculations |
| RAGService | 🔴 HIGH | LLM inference latency |
| CognitiveService | 🔴 HIGH | LLM inference latency |
| CopilotService | 🔴 HIGH | LLM inference latency |
| MeasurementService | 🟡 MEDIUM | Time-series writes |
| EventService | 🟡 MEDIUM | Event stream processing |
| PropagationService | 🔴 HIGH | Cascade analysis |
| SemanticService | 🟡 MEDIUM | Graph traversal |

---

## No Code Modifications Made

Per Task 080E constraints, **no code modifications were made**. This is an observation report only.

---

## Next Steps

- Proceed to Phase 5: Namespace Standardization
