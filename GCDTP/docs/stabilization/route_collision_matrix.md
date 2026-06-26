# Route Collision Matrix

**Generated:** 2026-06-21
**Repository:** DigiTwinXR-SAAS
**Branch:** feature/tasks-024-029-extensible-architecture
**Phase:** 2 - Collision Analysis

---

## Executive Summary

This document analyzes all route collisions, overlaps, and ambiguities. Evidence is derived from filesystem inspection only. **No code modifications were made.**

---

## Classification System

| Level | Description | Action Required |
|-------|-------------|----------------|
| **CRITICAL** | Direct path + method collision | Immediate fix |
| **HIGH** | Prefix collision causing shadowing | Urgent fix |
| **MEDIUM** | Semantic overlap | Monitor |
| **LOW** | Possible future conflict | Document |

---

## Phase 1: Prefix Collision Analysis

### Critical Finding: /health Prefix Collision

| Route File | Prefix | Status |
|------------|--------|--------|
| `health_routes.py` | `/health` | ⚠️ |
| `network_health_routes.py` | `/health` | ⚠️ ⚠️ |

**Collision Type:** HIGH (prefix shadowing)

**Evidence:**
```
health_routes.py:
  router = APIRouter(prefix="/health", tags=["health"])

network_health_routes.py:
  router = APIRouter(prefix="/health", tags=["network-health"])
```

**Impact:** FastAPI router registration order determines which routes are accessible.

---

## Phase 2: Path + Method Collision Analysis

### 2.1 /query POST Collision

| Route File | Full Path | Method | Response Model |
|------------|-----------|--------|---------------|
| `rag_routes.py` | `/rag/query` | POST | RAGQueryResponse |
| `cognitive_routes.py` | `/cognitive/query` | POST | CognitiveQueryWithContextResponse |
| `copilot_routes.py` | `/copilot/query` | POST | QueryResponse |

**Classification:** LOW (different full paths)

**Explanation:** These routes have the same path pattern `/query` but different router prefixes, so they resolve to different full paths:
- `/rag/query`
- `/cognitive/query`
- `/copilot/query`

**Risk:** None (FastAPI routes by full path)

---

### 2.2 /context/{id} GET Collision

| Route File | Full Path | Method | Response Model |
|------------|-----------|--------|---------------|
| `rag_routes.py` | `/rag/context/{query_id}` | GET | - |
| `cognitive_routes.py` | `/cognitive/context/{query_id}` | GET | - |
| `semantic_routes.py` | `/semantic/context/{entity_type}/{entity_id}` | GET | SemanticContextResponse |
| `copilot_routes.py` | `/copilot/context/{entity_type}/{entity_id}` | GET | ContextResponse |

**Classification:** LOW (different full paths)

**Explanation:** Routes use different parameter structures:
- `{query_id}` vs `{entity_type}/{entity_id}`

**Risk:** None

---

### 2.3 /asset/{asset_id} GET Collision

| Route File | Full Path | Response Model |
|------------|-----------|---------------|
| `asset_routes.py` | `/assets/{asset_id}` | AssetResponse |
| `timeline_routes.py` | `/timeline/asset/{asset_id}` | AssetTimelineResponse |
| `propagation_routes.py` | `/propagation/asset/{asset_id}` | - |
| `resilience_routes.py` | `/resilience/asset/{asset_id}` | ResilienceAnalysisResponse |
| `root_cause_routes.py` | `/root-cause/asset/{asset_id}` | - |
| `event_routes.py` | `/events/asset/{asset_id}` | EventListResponse |

**Classification:** LOW (different full paths)

**Explanation:** Routes are domain-scoped:
- `/assets/` - Core asset
- `/timeline/asset/` - Timeline for asset
- `/propagation/asset/` - Propagation for asset
- etc.

**Risk:** None

---

### 2.4 /history Collision

| Route File | Full Path | Response Model |
|------------|-----------|---------------|
| `agent_routes.py` | `/agent/history` | TaskHistoryResponse |
| `cognitive_routes.py` | `/cognitive/sessions/{session_id}/history` | HistoryResponse |
| `rag_routes.py` | `/rag/history/{session_id}` | RAGHistoryResponse |
| `copilot_routes.py` | `/copilot/sessions/{session_id}/history` | SessionHistory |

**Classification:** LOW (different full paths)

**Risk:** None

---

### 2.5 /stats Collision

| Route File | Full Path | Response Model |
|------------|-----------|---------------|
| `agent_routes.py` | `/agent/stats` | TaskStatsResponse |

**Classification:** LOW (unique)

**Risk:** None

---

### 2.6 /search Collision

| Route File | Full Path | Response Model |
|------------|-----------|---------------|
| `knowledge_routes.py` | `/knowledge/search` | KnowledgeSearchResponse |
| `logbook_routes.py` | `/logbook/search` | LogbookListResponse |
| `semantic_routes.py` | `/semantic/search` | SemanticSearchResponse |

**Classification:** LOW (different full paths)

**Risk:** None

---

## Phase 3: Shadowing Analysis

### 3.1 /health Prefix Shadowing

**Critical Issue:** Both `health_routes.py` and `network_health_routes.py` use `/health` prefix.

**Scenario A: health_routes registered first**
```
GET /health/assets → health_routes ✓
GET /health/network → health_routes ✗ (404 or wrong handler)
```

**Scenario B: network_health_routes registered first**
```
GET /health/assets → network_health_routes ✗ (404 or wrong handler)
GET /health/network → network_health_routes ✓
```

**Risk Level:** HIGH

**Recommendation:** Rename one prefix to avoid collision.

---

## Phase 4: Ambiguous Ownership Analysis

### 4.1 /asset Ownership

Multiple domains claim `/asset` ownership:

| Domain | Routes | Context |
|--------|--------|---------|
| Asset | `/assets/{asset_id}` | Core asset |
| Timeline | `/timeline/asset/{asset_id}` | Timeline view |
| Propagation | `/propagation/asset/{asset_id}` | Propagation view |
| Resilience | `/resilience/asset/{asset_id}` | Resilience view |
| Events | `/events/asset/{asset_id}` | Events view |

**Classification:** MEDIUM (semantic overlap)

**Recommendation:** Document ownership clearly.

---

### 4.2 /history Ownership

Multiple domains have `/history` routes:

| Domain | Routes | Context |
|--------|--------|---------|
| Agent | `/agent/history` | Task history |
| Cognitive | `/cognitive/sessions/{id}/history` | Session history |
| RAG | `/rag/history/{id}` | Query history |
| Copilot | `/copilot/sessions/{id}/history` | Message history |

**Classification:** LOW (different entities)

**Recommendation:** None required.

---

## Phase 5: Collision Summary Matrix

| Collision Type | Files Affected | Severity | Action Required |
|---------------|---------------|----------|-----------------|
| `/health` prefix | 2 files | HIGH | Rename prefix |
| `/rag/query` vs others | 3 files | LOW | None |
| `/cognitive/query` vs others | 3 files | LOW | None |
| `/copilot/query` vs others | 3 files | LOW | None |
| `/asset/{id}` | 6 files | LOW | None |
| `/context/{id}` | 4 files | LOW | None |
| `/history` | 4 files | LOW | None |
| `/search` | 3 files | LOW | None |

---

## Phase 6: Detailed Collision Records

### COLLISION-001: Health Prefix Collision

| Field | Value |
|-------|-------|
| ID | COLLISION-001 |
| Type | PREFIX_SHADOWING |
| Severity | HIGH |
| Files | `health_routes.py`, `network_health_routes.py` |
| Affected Routes | All `/health/*` routes |
| FastAPI Impact | Registration order determines accessibility |
| Resolution | Rename `network_health_routes.py` prefix to `/network` |

**Affected Routes:**

| File | Routes |
|------|--------|
| health_routes.py | `/health/assets`, `/health/assets/{id}`, etc. |
| network_health_routes.py | `/health/network`, `/health/analyze-network`, etc. |

---

### COLLISION-002: Query Route Pattern

| Field | Value |
|-------|-------|
| ID | COLLISION-002 |
| Type | PATTERN_MATCH |
| Severity | LOW |
| Files | `rag_routes.py`, `cognitive_routes.py`, `copilot_routes.py` |
| Affected Routes | 3 POST `/query` routes |
| FastAPI Impact | None (different full paths) |
| Resolution | None required |

**Routes:**
```
POST /rag/query      → RAGQueryResponse
POST /cognitive/query → CognitiveQueryWithContextResponse
POST /copilot/query  → QueryResponse
```

---

### COLLISION-003: Asset Route Pattern

| Field | Value |
|-------|-------|
| ID | COLLISION-003 |
| Type | SEMANTIC_OVERLAP |
| Severity | LOW |
| Files | 6 route files |
| Affected Routes | 6 `/asset/{id}` routes |
| FastAPI Impact | None (different full paths) |
| Resolution | Document ownership |

**Routes:**
```
GET /assets/{asset_id}                    → Core asset
GET /timeline/asset/{asset_id}            → Timeline
GET /propagation/asset/{asset_id}         → Propagation
GET /resilience/asset/{asset_id}         → Resilience
GET /events/asset/{asset_id}             → Events
GET /root-cause/asset/{asset_id}         → Root cause
```

---

## Phase 7: FastAPI Router Registration Impact

### Current Registration Order (Assumed)

```python
# main.py (typical pattern)
app.include_router(health_routes.router)          # /health
app.include_router(network_health_routes.router)    # /health (SHADOWS!)
```

### Impact Analysis

| If health_routes first | If network_health first |
|----------------------|------------------------|
| `/health/assets` works | `/health/assets` → 404 |
| `/health/network` → 404 | `/health/network` works |
| `/health/recalculate-all` works | `/health/recalculate-all` → 404 |

---

## Phase 8: Recommendations

### Immediate Actions

1. **Rename network_health prefix** from `/health` to `/network`
   - Affects: `network_health_routes.py`
   - Routes become: `/network/assets`, `/network/analyze-network`

2. **Update imports in main.py** to reflect new prefix

### Future Considerations

1. **Add API versioning** to prevent future collisions
   - `/api/v1/health`
   - `/api/v1/network`

2. **Document ownership** for ambiguous routes

---

## No Code Modifications Made

Per Task 080E constraints, **no code modifications were made**. This is an observation report only.

---

## Next Steps

- Proceed to Phase 3: Canonical Domain Ownership
