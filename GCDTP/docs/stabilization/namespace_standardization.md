# Namespace Standardization

**Generated:** 2026-06-21
**Repository:** DigiTwinXR-SAAS
**Branch:** feature/tasks-024-029-extensible-architecture
**Phase:** 5 - Namespace Standardization

---

## Executive Summary

This document recommends API namespace standardization for version control and collision prevention. Evidence is derived from filesystem inspection only. **No code modifications were made.**

---

## Current State Analysis

### Current Prefixes (21 unique)

```
/agent
/assets
/cognitive
/copilot
/events
/health         ⚠️ COLLISION
/knowledge
/logbook
/measurements
/predictive
/propagation
/rag
/recovery
/resilience
/root-cause
/scenarios
/semantic
/sensors
/thresholds
/timeline
```

**⚠️ ISSUE:** `/health` is used by both `health_routes.py` and `network_health_routes.py`

---

## Recommended Standardization

### Pattern: `/api/v1/{domain}`

This follows industry best practices:
- `/api` - API indicator
- `/v1` - Version prefix
- `/{domain}` - Domain-specific namespace

---

## Phase 1: Current vs Recommended Namespaces

### Domain Routes

| Current Prefix | Recommended Prefix | Route File | Status |
|--------------|-------------------|------------|--------|
| `/agent` | `/api/v1/agent` | agent_routes.py | ✅ |
| `/assets` | `/api/v1/assets` | asset_routes.py | ✅ |
| `/cognitive` | `/api/v1/cognitive` | cognitive_routes.py | ✅ |
| `/copilot` | `/api/v1/copilot` | copilot_routes.py | ✅ |
| `/events` | `/api/v1/events` | event_routes.py | ✅ |
| `/knowledge` | `/api/v1/knowledge` | knowledge_routes.py | ✅ |
| `/logbook` | `/api/v1/logbook` | logbook_routes.py | ✅ |
| `/measurements` | `/api/v1/measurements` | measurement_routes.py | ✅ |
| `/predictive` | `/api/v1/predictive` | predictive_routes.py | ✅ |
| `/propagation` | `/api/v1/propagation` | propagation_routes.py | ✅ |
| `/rag` | `/api/v1/rag` | rag_routes.py | ✅ |
| `/recovery` | `/api/v1/recovery` | recovery_routes.py | ✅ |
| `/resilience` | `/api/v1/resilience` | resilience_routes.py | ✅ |
| `/root-cause` | `/api/v1/root-cause` | root_cause_routes.py | ✅ |
| `/scenarios` | `/api/v1/scenarios` | scenario_routes.py | ✅ |
| `/semantic` | `/api/v1/semantic` | semantic_routes.py | ✅ |
| `/sensors` | `/api/v1/sensors` | sensor_routes.py | ✅ |
| `/thresholds` | `/api/v1/thresholds` | threshold_routes.py | ✅ |
| `/timeline` | `/api/v1/timeline` | timeline_routes.py | ✅ |
| `/health` | `/api/v1/health` | health_routes.py | ⚠️ COLLISION |

### Health Collision Resolution

| Current Prefix | Issue | Recommended Prefix | Route File |
|--------------|-------|-------------------|------------|
| `/health` | COLLISION | `/api/v1/health` | health_routes.py |
| `/health` | COLLISION | `/api/v1/network` | network_health_routes.py |

**Recommended Action:** Rename `network_health_routes.py` prefix to `/api/v1/network`

---

## Phase 2: Namespace Structure

### Proposed Namespace Hierarchy

```
/api
├── /v1                    (Current version)
│   ├── /core              (Core domain)
│   │   ├── /assets
│   │   ├── /sensors
│   │   ├── /events
│   │   ├── /measurements
│   │   └── /thresholds
│   │
│   ├── /analytics         (Analytics domain)
│   │   ├── /health
│   │   ├── /network
│   │   ├── /resilience
│   │   ├── /predictive
│   │   ├── /propagation
│   │   └── /root-cause
│   │
│   ├── /ai                (AI domain)
│   │   ├── /rag
│   │   ├── /cognitive
│   │   ├── /copilot
│   │   └── /agent
│   │
│   ├── /knowledge         (Knowledge domain)
│   │   ├── /semantic
│   │   ├── /knowledge
│   │   ├── /logbook
│   │   └── /timeline
│   │
│   └── /simulation        (Simulation domain)
│       ├── /scenarios
│       └── /recovery
│
└── /v2                    (Future version)
```

---

## Phase 3: Collision Resolution

### Collision 1: /health Prefix

**Current State:**
```
health_routes.py         → /health/*
network_health_routes.py → /health/*  ← COLLISION!
```

**Recommended Resolution:**

```
Option A: Rename network_health prefix
  health_routes.py         → /api/v1/health/*
  network_health_routes.py → /api/v1/network/*

Option B: Merge routes
  health_routes.py         → /api/v1/health/*  (include network)
  network_health_routes.py → (DELETE - merge into health)
```

**Recommended:** Option A (maintain separation)

### Option A Details

```python
# health_routes.py
router = APIRouter(prefix="/api/v1/health", tags=["health"])

# network_health_routes.py  
router = APIRouter(prefix="/api/v1/network", tags=["network"])
```

**Affected Routes:**

| Before | After |
|--------|-------|
| GET /health/assets | GET /api/v1/health/assets |
| GET /health/network | GET /api/v1/network |
| POST /health/recalculate-all | POST /api/v1/health/recalculate-all |
| POST /health/analyze-network | POST /api/v1/network/analyze-network |

---

## Phase 4: Migration Path

### Phase 4.1: Dual Support (Version 1.0 → 1.1)

Maintain both old and new prefixes during transition:

```python
# main.py
app.include_router(health_routes.router, prefix="/health")      # Legacy
app.include_router(health_routes.router, prefix="/api/v1/health") # New
```

### Phase 4.2: New Version Only (Version 2.0)

After deprecation period, remove legacy:

```python
# main.py (v2.0)
app.include_router(health_routes.router, prefix="/api/v2/health")
```

---

## Phase 5: Versioning Strategy

### Version Lifecycle

```
v1 (Current)
├── /api/v1/assets
├── /api/v1/sensors
├── /api/v1/health
└── /api/v1/...

    ↓ (Deprecation period: 6 months)

v2 (Future)
├── /api/v2/assets (breaking changes)
├── /api/v2/sensors (breaking changes)
├── /api/v2/health (breaking changes)
└── /api/v2/...
```

### Deprecation Headers

```python
# When serving v1
response.headers["X-API-Deprecation"] = "true"
response.headers["X-API-Removal-Date"] = "2026-12-31"
```

---

## Phase 6: Implementation Plan

### Step 1: Prefix Updates

Update each route file's APIRouter prefix:

```python
# Before
router = APIRouter(prefix="/assets", tags=["assets"])

# After
router = APIRouter(prefix="/api/v1/assets", tags=["assets"])
```

### Step 2: Collision Resolution

Rename `network_health_routes.py`:

```python
# Before
router = APIRouter(prefix="/health", tags=["network-health"])

# After
router = APIRouter(prefix="/api/v1/network", tags=["network"])
```

### Step 3: Main.py Update

Update route registration:

```python
# main.py
app.include_router(asset_routes.router)           # Uses /api/v1/assets
app.include_router(health_routes.router)           # Uses /api/v1/health
app.include_router(network_health_routes.router)   # Uses /api/v1/network
```

---

## Phase 7: Consumer Updates

### Frontend Updates

```javascript
// Before
GET /assets/123

// After
GET /api/v1/assets/123
```

### Service Updates

```python
# Before
async def get_asset(asset_id):
    return await client.get("/assets/{asset_id}")

# After
async def get_asset(asset_id):
    return await client.get("/api/v1/assets/{asset_id}")
```

---

## Phase 8: Namespace Standardization Summary

| Namespace | Current | Recommended | Action |
|----------|---------|-------------|--------|
| Core | /assets | /api/v1/assets | Rename |
| Core | /sensors | /api/v1/sensors | Rename |
| Core | /events | /api/v1/events | Rename |
| Core | /measurements | /api/v1/measurements | Rename |
| Core | /thresholds | /api/v1/thresholds | Rename |
| Analytics | /health | /api/v1/health | Rename |
| Analytics | /health | /api/v1/network | **RENAME + MOVE** |
| Analytics | /resilience | /api/v1/resilience | Rename |
| Analytics | /predictive | /api/v1/predictive | Rename |
| Analytics | /propagation | /api/v1/propagation | Rename |
| Analytics | /root-cause | /api/v1/root-cause | Rename |
| AI | /rag | /api/v1/rag | Rename |
| AI | /cognitive | /api/v1/cognitive | Rename |
| AI | /copilot | /api/v1/copilot | Rename |
| AI | /agent | /api/v1/agent | Rename |
| Knowledge | /semantic | /api/v1/semantic | Rename |
| Knowledge | /knowledge | /api/v1/knowledge | Rename |
| Knowledge | /logbook | /api/v1/logbook | Rename |
| Knowledge | /timeline | /api/v1/timeline | Rename |
| Simulation | /scenarios | /api/v1/scenarios | Rename |
| Simulation | /recovery | /api/v1/recovery | Rename |

---

## No Code Modifications Made

Per Task 080E constraints, **no code modifications were made**. This is an observation report only.

---

## Next Steps

- Proceed to Phase 6: Refactor Readiness
