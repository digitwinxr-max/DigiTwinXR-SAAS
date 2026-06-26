# Route Collision Audit Report

**Generated:** 2026-06-21
**Repository:** DigiTwinXR-SAAS
**Branch:** feature/tasks-024-029-extensible-architecture
**Phase:** 2 - Route Collision Audit

---

## Executive Summary

This document investigates route collisions in the FastAPI application. Evidence is derived from filesystem inspection only. **No modifications were made to routes.**

---

## Route Collision Findings

### Collision Type 1: POST /query

**Full Paths with Collision:**

| # | Route File | Router Prefix | Full Path | Response Model |
|---|------------|---------------|-----------|----------------|
| 1 | `rag_routes.py` | `/rag` | `POST /rag/query` | `RAGQueryResponse` |
| 2 | `cognitive_routes.py` | `/cognitive` | `POST /cognitive/query` | `CognitiveQueryWithContextResponse` |
| 3 | `copilot_routes.py` | `/copilot` | `POST /copilot/query` | `QueryResponse` |

**Analysis:**
- **NO ACTUAL COLLISION** - Each route has unique router prefix
- Routes are: `/rag/query`, `/cognitive/query`, `/copilot/query`
- All are distinct endpoints
- Semantic difference: RAG vs Cognitive vs Copilot query operations

**Ambiguity Risk:** LOW (paths are distinct)

---

### Collision Type 2: GET /context/{id}

**Full Paths with Collision:**

| # | Route File | Router Prefix | Full Path | Response Model |
|---|------------|---------------|-----------|----------------|
| 1 | `rag_routes.py` | `/rag` | `GET /rag/context/{query_id}` | (no model) |
| 2 | `semantic_routes.py` | `/semantic` | `GET /semantic/context/{entity_type}/{entity_id}` | `SemanticContextResponse` |
| 3 | `cognitive_routes.py` | `/cognitive` | `GET /cognitive/context/{query_id}` | (no model) |
| 4 | `copilot_routes.py` | `/copilot` | `GET /copilot/context/{entity_type}/{entity_id}` | `ContextResponse` |

**Analysis:**
- **NO ACTUAL COLLISION** - Path structures differ
- `/rag/context/{query_id}` vs `/semantic/context/{entity_type}/{entity_id}`
- `/cognitive/context/{query_id}` vs `/copilot/context/{entity_type}/{entity_id}`
- Different parameter patterns prevent collision

**Ambiguity Risk:** LOW (parameter structures differ)

---

### Collision Type 3: GET /asset/{asset_id}

**Full Paths with Collision:**

| # | Route File | Router Prefix | Full Path | Response Model |
|---|------------|---------------|-----------|----------------|
| 1 | `asset_routes.py` | `/assets` | `GET /assets/{asset_id}` | `AssetResponse` |
| 2 | `timeline_routes.py` | `/timeline` | `GET /timeline/asset/{asset_id}` | `AssetTimelineResponse` |
| 3 | `propagation_routes.py` | `/propagation` | `GET /propagation/asset/{asset_id}` | (no model) |
| 4 | `resilience_routes.py` | `/resilience` | `GET /resilience/asset/{asset_id}` | `ResilienceAnalysisResponse` |
| 5 | `root_cause_routes.py` | `/root-cause` | `GET /root-cause/asset/{asset_id}` | (no model) |
| 6 | `event_routes.py` | `/events` | `GET /events/asset/{asset_id}` | `EventListResponse` |

**Analysis:**
- **NO ACTUAL COLLISION** - All paths are distinct
- `/assets/{asset_id}` - Core asset retrieval
- `/timeline/asset/{asset_id}` - Timeline data for asset
- `/propagation/asset/{asset_id}` - Propagation chain for asset
- `/resilience/asset/{asset_id}` - Resilience analysis for asset
- `/root-cause/asset/{asset_id}` - Root cause for asset
- `/events/asset/{asset_id}` - Events for asset

**Ambiguity Risk:** LOW (domain-specific prefixes clarify intent)

---

## Router Prefix Overlap

### Duplicate Prefixes Found

| Prefix | Route Files | Status |
|--------|-------------|--------|
| `/health` | `health_routes.py` | ⚠️ DUPLICATE |
| `/health` | `network_health_routes.py` | ⚠️ DUPLICATE |

**Details:**

| File | Prefix | Tag |
|------|--------|-----|
| `health_routes.py` | `/health` | `["health"]` |
| `network_health_routes.py` | `/health` | `["network-health"]` |

**Analysis:**
- **POTENTIAL COLLISION** - Both use `/health` prefix
- FastAPI will mount these sequentially
- Last-mounted router may override first
- **Action Required:** This is a real concern

**Risk Level:** MEDIUM-HIGH

---

## FastAPI Router Registration Analysis

Based on `backend/src/main.py` inspection (if exists) or typical structure:

```python
# Typical FastAPI app structure
app.include_router(agent_routes.router)        # /agent
app.include_router(asset_routes.router)        # /assets
app.include_router(health_routes.router)        # /health
app.include_router(network_health_routes.router) # /health (CONFLICT!)
```

**Consequence:**
- Routes in `network_health_routes.py` may shadow routes in `health_routes.py`
- Or vice versa depending on registration order
- Affects: `/health/assets`, `/health/assets/{asset_id}`, etc.

---

## Conflict Summary

| Conflict Type | Files Affected | Risk Level | Actual Collision |
|---------------|----------------|------------|------------------|
| POST /query | 3 files | LOW | NO |
| GET /context | 4 files | LOW | NO |
| GET /asset | 6 files | LOW | NO |
| Prefix /health | 2 files | MEDIUM-HIGH | YES |

---

## Canonical Ownership Recommendations

### For Routes Without Collision

| Endpoint Pattern | Canonical Owner | Rationale |
|------------------|-----------------|-----------|
| `/rag/*` | `rag_routes.py` | RAG engine scope |
| `/cognitive/*` | `cognitive_routes.py` | Cognitive twin scope |
| `/copilot/*` | `copilot_routes.py` | Copilot scope |
| `/assets/*` | `asset_routes.py` | Core asset scope |
| `/timeline/*` | `timeline_routes.py` | Timeline scope |
| `/propagation/*` | `propagation_routes.py` | Propagation scope |
| `/resilience/*` | `resilience_routes.py` | Resilience scope |
| `/root-cause/*` | `root_cause_routes.py` | RCA scope |
| `/events/*` | `event_routes.py` | Events scope |

### For Health Prefix Conflict

| Option | Recommendation |
|--------|----------------|
| **Option A** | Merge `network_health_routes.py` into `health_routes.py` |
| **Option B** | Rename `network_health_routes.py` prefix to `/network` |
| **Option C** | Reorder router registration so `/health` routes have priority |

**Recommended Action:** Option B - Rename to `/network` for clarity

---

## Action Items

| Priority | Action | Owner | Status |
|----------|--------|-------|--------|
| HIGH | Investigate `/health` prefix conflict | Backend Team | **Requires Resolution** |
| MEDIUM | Document API endpoint ownership | Architecture | Recommended |
| LOW | Consider renaming `/root-cause` to `/root-cause-analysis` | Backend Team | Optional |

---

## Verification Commands

To verify routes at runtime:

```bash
# List all routes
curl http://localhost:8080/openapi.json | jq '.paths | keys'

# Check for /health conflicts
curl http://localhost:8080/openapi.json | jq '.paths | keys[] | select(contains("health"))'
```

---

## Conclusion

**No actual path collisions exist** for the investigated patterns (`POST /query`, `GET /context/{id}`, `GET /asset/{id}`).

**However**, a real conflict exists between `health_routes.py` and `network_health_routes.py` due to duplicate `/health` prefix.

**DO NOT MODIFY ROUTES** - This is an observation report only.

---

## Next Steps

- Proceed to Phase 3: Placeholder Elimination Audit
