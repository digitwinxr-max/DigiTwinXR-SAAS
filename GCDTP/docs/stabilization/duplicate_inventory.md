# Duplicate Inventory Report

**Generated:** 2026-06-21
**Repository:** DigiTwinXR-SAAS
**Branch:** feature/tasks-024-029-extensible-architecture
**Phase:** 4 - Import and Duplicate Validation

---

## Executive Summary

This document catalogs all duplicate files, models, services, schemas, and routes found in the repository. Evidence is derived from filesystem inspection only.

---

## Duplicate Search Results

### Backend Models

| Model Name | File Location | Duplicate? |
|------------|--------------|------------|
| agent | `backend/src/models/agent.py` | ✅ Unique |
| asset | `backend/src/models/asset.py` | ✅ Unique |
| sensor | `backend/src/models/sensor.py` | ✅ Unique |
| event | `backend/src/models/event.py` | ✅ Unique |
| measurement | `backend/src/models/measurement.py` | ✅ Unique |
| health | `backend/src/models/health.py` | ✅ Unique |
| threshold | `backend/src/models/threshold.py` | ✅ Unique |
| scenario | `backend/src/models/scenario.py` | ✅ Unique |
| semantic_entity | `backend/src/models/semantic_entity.py` | ✅ Unique |
| rag_query | `backend/src/models/rag_query.py` | ✅ Unique |
| cognitive_session | `backend/src/models/cognitive_session.py` | ✅ Unique |

**Duplicates Found:** 0

---

### Backend Services

| Service Name | File Location | Duplicate? |
|--------------|--------------|------------|
| asset_service | `backend/src/services/asset_service.py` | ✅ Unique |
| sensor_service | `backend/src/services/sensor_service.py` | ✅ Unique |
| event_service | `backend/src/services/event_service.py` | ✅ Unique |
| health_service | `backend/src/services/health_service.py` | ✅ Unique |
| rag_service | `backend/src/services/rag_service.py` | ✅ Unique |
| semantic_service | `backend/src/services/semantic_service.py` | ✅ Unique |
| timeline_service | `backend/src/services/timeline_service.py` | ✅ Unique |
| topology_engine | `backend/src/services/topology_engine.py` | ✅ Unique |
| resilience_engine | `backend/src/services/resilience_engine.py` | ✅ Unique |
| work_order_engine | `backend/src/services/work_order_engine.py` | ✅ Unique |

**Duplicates Found:** 0

---

### Backend Schemas

| Schema Name | File Location | Duplicate? |
|------------|--------------|------------|
| asset | `backend/src/schemas/asset.py` | ✅ Unique |
| sensor | `backend/src/schemas/sensor.py` | ✅ Unique |
| event | `backend/src/schemas/event.py` | ✅ Unique |
| health | `backend/src/schemas/health.py` | ✅ Unique |
| rag | `backend/src/schemas/rag.py` | ✅ Unique |
| cognitive | `backend/src/schemas/cognitive.py` | ✅ Unique |
| timeline | `backend/src/schemas/timeline.py` | ✅ Unique |
| resilience | `backend/src/schemas/resilience.py` | ✅ Unique |
| work_order | `backend/src/schemas/work_order.py` | ✅ Unique |

**Duplicates Found:** 0

---

### API Route Files

| Route File | Router Prefix | Duplicate? |
|------------|---------------|------------|
| agent_routes.py | `/agent` | ✅ Unique |
| asset_routes.py | `/assets` | ✅ Unique |
| sensor_routes.py | `/sensors` | ✅ Unique |
| event_routes.py | `/events` | ✅ Unique |
| health_routes.py | `/health` | ⚠️ See Note |
| rag_routes.py | `/rag` | ✅ Unique |
| cognitive_routes.py | `/cognitive` | ✅ Unique |
| copilot_routes.py | `/copilot` | ✅ Unique |
| timeline_routes.py | `/timeline` | ✅ Unique |
| work_order_routes.py | `/work-orders` | ✅ Unique |

**Route Prefix Duplicates Found:** 1 (`/health`)

**Note:** `health_routes.py` and `network_health_routes.py` both use prefix `/health`. See route_collision_report.md for details.

---

### Frontend Pages

| Page Name | File Location | Duplicate? |
|-----------|--------------|------------|
| AssetList | `frontend/src/pages/AssetList.jsx` | ✅ Unique |
| AssetDetails | `frontend/src/pages/AssetDetails.jsx` | ✅ Unique |
| SensorList | `frontend/src/pages/SensorList.jsx` | ✅ Unique |
| EventList | `frontend/src/pages/EventList.jsx` | ✅ Unique |
| HealthDashboard | `frontend/src/pages/HealthDashboard.jsx` | ✅ Unique |
| CognitiveCopilot | `frontend/src/pages/CognitiveCopilot.jsx` | ✅ Unique |
| RAGWorkbench | `frontend/src/pages/RAGWorkbench.jsx` | ✅ Unique |

**Duplicates Found:** 0

---

### Frontend Components

| Component Category | Count | Duplicates? |
|-------------------|-------|-------------|
| MapLibre | 10 | ✅ Unique |
| Cesium | 8 | ✅ Unique |
| TerriaJS | 9 | ✅ Unique |
| Kepler.gl | 12 | ✅ Unique |

**Duplicates Found:** 0

---

## Duplicate Service Names (Subdirectories)

Some services exist in subdirectories with same base names:

| Base Name | Locations |
|-----------|-----------|
| document_engine | `backend/src/services/documents/document_engine.py` |
| timeline_engine | `backend/src/services/timeline/timeline_engine.py` |
| work_order_engine | `backend/src/services/work_orders/work_order_engine.py` |

**Note:** These are not duplicates - they are namespaced by subdirectory.

---

## Duplicate Patterns Summary

| Category | Total Items | Duplicates | Unique |
|----------|-------------|------------|--------|
| Backend Models | 38 | 0 | 38 |
| Backend Services | 50 | 0 | 50 |
| Backend Schemas | 22 | 0 | 22 |
| Route Files | 22 | 0 | 22 |
| Route Prefixes | 22 | 1 | 21 |
| Frontend Pages | 38 | 0 | 38 |
| Frontend Components | 39 | 0 | 39 |

**Overall Duplicate Rate:** < 1% (only route prefix collision)

---

## Findings

1. **No file-level duplicates** - All models, services, schemas are unique
2. **No page-level duplicates** - All frontend pages are unique
3. **No component-level duplicates** - All map components are unique
4. **One route prefix collision** - `/health` prefix used by 2 route files

---

## No Action Required for Duplicates

The repository is well-organized with no significant duplicate issues.

---

## Next Steps

- Proceed to import_validation.md
- Proceed to dead_code_report.md
