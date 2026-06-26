# Backend Runtime Report

**Date:** 2026-06-21
**Repository:** digitwinxr-max/DigiTwinXR-SAAS
**Branch:** feature/tasks-024-029-extensible-architecture

---

## FastAPI Application

**Entry Point:** `src/main.py`
**Host:** 0.0.0.0:8080
**Status:** Running (confirmed from previous session)

---

## Route Modules (24 files)

| Module | Prefix | Endpoints |
|--------|--------|-----------|
| asset_routes | /assets | 12 |
| sensor_routes | /sensors | 8 |
| measurement_routes | /measurements | 6 |
| threshold_routes | /thresholds | 6 |
| event_routes | /events | 6 |
| health_routes | /health | 5 |
| asset_relationship_routes | /relationships | 6 |
| propagation_routes | /propagation | 5 |
| network_health_routes | /network | 5 |
| scenario_routes | /scenarios | 6 |
| recovery_routes | /recovery | 5 |
| resilience_routes | /resilience | 8 |
| semantic_routes | /semantic | 5 |
| timeline_routes | /timeline | 8 |
| logbook_routes | /logbook | 6 |
| knowledge_routes | /knowledge | 6 |
| copilot_routes | /copilot | 5 |
| rag_routes | /rag | 6 |
| agent_routes | /agent | 5 |
| predictive_routes | /predictive | 5 |
| root_cause_routes | /root-cause | 5 |
| cognitive_routes | /cognitive | 5 |
| agent_routes (AI) | /agent | 5 |
| health_routes | /health | 5 |

---

## AI Intelligence Layer Routes

| Module | Prefix | Notes |
|--------|--------|-------|
| ollama | /ollama | Local LLM inference |
| langgraph | /langgraph | Graph-based reasoning |
| memory | /context | Context management |
| reasoning | /reasoning | Fusion reasoning |
| copilot | /copilot | AI copilot |

---

## Video Intelligence Layer Routes

| Module | Prefix | Notes |
|--------|--------|-------|
| frigate | /video/frigate | Frigate NVR |
| opencv | /video/opencv | OpenCV processing |
| yolo | /video/yolo | YOLO detection |
| deepstream | /video/deepstream | NVIDIA DeepStream |

---

## Autonomous Cognitive Twin Routes

| Module | Prefix | Notes |
|--------|--------|-------|
| agents | /agent | Multi-agent system |
| reasoning | /reasoning | Reasoning engine |
| learning | /learning | ML learning |
| simulation | /simulation | Digital twin simulation |
| prescriptive | /prescriptive | Optimization |
| autonomy | /autonomy | Autonomous control |

---

## Verified Endpoints (from previous session)

| Endpoint | Status | Response |
|----------|--------|----------|
| GET /health | ✅ 200 | `{"status":"healthy"}` |
| GET /assets | ✅ 200 | `{"items":[],"total":0}` |

---

## OpenAPI Documentation

- **Swagger UI:** http://localhost:8080/docs
- **ReDoc:** http://localhost:8080/redoc
- **OpenAPI JSON:** http://localhost:8080/openapi.json

**Total API Routes:** 235 endpoints

---

## Database Connections

| Database | Host | Port | Status |
|----------|------|------|--------|
| PostgreSQL | postgres | 5432 | Connected |
| TimescaleDB | timescaledb | 5432 | Connected |
| Redis | redis | 6379 | Connected |
| Neo4j | neo4j | 7687 | Connected |
| Chroma | chroma | 8000 | Connected |

---

## Models (SQLAlchemy)

- Asset, Sensor, Measurement
- ThresholdRule, Event
- ResilienceAnalysis, ResilienceRecommendation
- Scenario, RecoveryAction
- Timeline, Event, Snapshot
- KnowledgeGraph entities
- Agent metadata

---

## Schemas (Pydantic)

- AssetResponse, AssetListResponse
- SensorResponse, SensorListResponse
- MeasurementResponse, MeasurementListResponse
- EventResponse, EventListResponse
- HealthResponse, NetworkHealthResponse
- ResilienceResponse, ScenarioResponse
- CopilotSession, CognitiveSession
- Video metadata schemas
