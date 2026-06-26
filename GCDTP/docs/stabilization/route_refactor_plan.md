# Route Refactor Plan

**Generated:** 2026-06-21
**Repository:** DigiTwinXR-SAAS
**Branch:** feature/tasks-024-029-extensible-architecture
**Phase:** 6 - Refactor Readiness

---

## Executive Summary

This document estimates the effort, risk, and impact of the required route refactoring. Evidence is derived from filesystem inspection only. **No code modifications were made.**

---

## Classification System

| Level | Description |
|-------|-------------|
| **LOW** | < 1 day effort, minimal risk |
| **MEDIUM** | 1-5 days effort, moderate risk |
| **HIGH** | 5+ days effort, significant risk |

---

## Phase 1: Collision Fix - /health Prefix

### Issue
Both `health_routes.py` and `network_health_routes.py` use `/health` prefix.

### Refactor Actions

1. Rename `network_health_routes.py` prefix to `/network`

### Effort Estimate

| Task | Effort | Risk |
|------|--------|------|
| Update router prefix | 0.5 hours | LOW |
| Update main.py registration | 0.5 hours | LOW |
| Update tests | 2 hours | MEDIUM |
| Update frontend imports | 4 hours | MEDIUM |
| Update documentation | 1 hour | LOW |

**Total:** ~8 hours (1 day)

### Affected Components

| Component | Count | Update Required |
|-----------|-------|----------------|
| Route files | 1 | Prefix change |
| Test files | 2 | Endpoint updates |
| Frontend pages | 12 | Import updates |
| Services | 1 | NetworkHealthService |

### Risk Assessment

| Risk | Level | Mitigation |
|------|-------|-----------|
| Breaking frontend | MEDIUM | Test all pages |
| Breaking tests | MEDIUM | Update test endpoints |
| Missing routes | LOW | Verify registration order |

---

## Phase 2: Namespace Standardization - /api/v1

### Issue
Routes lack versioned namespaces for future-proofing.

### Refactor Actions

1. Add `/api/v1/` prefix to all route files
2. Update main.py registration
3. Update frontend imports
4. Update service imports
5. Update documentation

### Effort Estimate (Per Route File)

| Task | Effort | Files | Total |
|------|--------|-------|-------|
| Update prefix | 0.25 hours | 22 | 5.5 hours |
| Update main.py | 0.5 hours | 1 | 0.5 hours |
| Update tests | 1 hour | 38 | 38 hours |
| Update frontend | 0.5 hours | 40 | 20 hours |
| Update services | 0.5 hours | 50 | 25 hours |

**Total:** ~89 hours (~11 days)

### Affected Components

| Component | Count | Update Required |
|-----------|-------|----------------|
| Route files | 22 | Prefix change |
| Test files | 38 | Endpoint updates |
| Frontend pages | 40 | Import updates |
| Services | 50 | Import updates |

### Risk Assessment

| Risk | Level | Mitigation |
|------|-------|-----------|
| Breaking all consumers | HIGH | Phased rollout |
| Missing routes | HIGH | Comprehensive testing |
| Version conflicts | MEDIUM | Clear deprecation path |

---

## Phase 3: Route Consolidation - Semantic Routes

### Issue
Semantic routes have 19 routes, most overlap with other domains.

### Refactor Actions

1. Move `/semantic/context` to `/rag/context`
2. Move `/semantic/graph` to `/rag/graph`
3. Consolidate entity routes

### Effort Estimate

| Task | Effort | Risk |
|------|--------|------|
| Analyze overlaps | 4 hours | LOW |
| Plan consolidation | 8 hours | MEDIUM |
| Implement changes | 16 hours | HIGH |
| Test changes | 8 hours | MEDIUM |
| Update consumers | 8 hours | HIGH |

**Total:** ~44 hours (~5.5 days)

### Affected Components

| Component | Count | Update Required |
|-----------|-------|----------------|
| Route files | 3 | Route merging |
| Test files | 6 | Endpoint updates |
| Frontend pages | 8 | Import updates |

### Risk Assessment

| Risk | Level | Mitigation |
|------|-------|-----------|
| Breaking RAG integration | HIGH | Test thoroughly |
| Breaking Cognitive | HIGH | Update all consumers |
| Missing functionality | MEDIUM | Comprehensive review |

---

## Phase 4: Route Grouping - Analytics

### Issue
Analytics routes are scattered across multiple files.

### Refactor Actions

1. Group health, network, resilience under `/analytics`
2. Consolidate `/propagation`, `/root-cause` under `/analytics`

### Effort Estimate

| Task | Effort | Risk |
|------|--------|------|
| Create /analytics prefix | 2 hours | LOW |
| Move routes | 4 hours | MEDIUM |
| Update tests | 8 hours | MEDIUM |
| Update consumers | 8 hours | MEDIUM |

**Total:** ~22 hours (~3 days)

### Affected Components

| Component | Count | Update Required |
|-----------|-------|----------------|
| Route files | 5 | Route grouping |
| Test files | 10 | Endpoint updates |
| Frontend pages | 15 | Import updates |

### Risk Assessment

| Risk | Level | Mitigation |
|------|-------|-----------|
| Breaking health dashboard | MEDIUM | Test all charts |
| Breaking analytics | MEDIUM | Verify calculations |

---

## Phase 5: Complete Refactor Summary

### Overall Effort

| Phase | Effort | Duration |
|-------|--------|----------|
| Phase 1: /health Fix | 8 hours | 1 day |
| Phase 2: Namespace Standardization | 89 hours | 11 days |
| Phase 3: Semantic Consolidation | 44 hours | 5.5 days |
| Phase 4: Analytics Grouping | 22 hours | 3 days |

**Total:** ~163 hours (~20 days)

### Risk Matrix

| Phase | Effort | Risk | Impact |
|-------|--------|------|--------|
| Phase 1 | LOW | LOW | MEDIUM |
| Phase 2 | HIGH | HIGH | HIGH |
| Phase 3 | MEDIUM | HIGH | HIGH |
| Phase 4 | MEDIUM | MEDIUM | MEDIUM |

---

## Phase 6: Recommended Approach

### Recommended: Phased Approach

```
Month 1: Phase 1 (/health fix)
  ├── Day 1: Update network_health prefix
  ├── Day 2-3: Update tests
  └── Day 4-5: Update frontend

Month 2-3: Phase 2 (Namespace) - Part 1
  ├── Week 1: Core routes (/assets, /sensors, /events)
  ├── Week 2: Analytics routes
  └── Week 3: AI routes

Month 3-4: Phase 2 (Namespace) - Part 2
  ├── Week 4: Knowledge routes
  └── Week 5: Simulation routes

Month 4-5: Phase 3 (Semantic Consolidation)
  ├── Week 6-7: Plan consolidation
  └── Week 8-9: Implement

Month 5-6: Phase 4 (Analytics Grouping)
  ├── Week 10: Create /analytics prefix
  └── Week 11-12: Consolidate
```

### Alternative: Big Bang

Update all routes at once with a breaking change version bump.

**Pros:**
- Single migration
- Clean namespace

**Cons:**
- High risk
- All consumers must update simultaneously
- No rollback

**Not recommended.**

---

## Phase 7: Affected Components Summary

### Frontend Pages (40)

| Page | Uses /health | Uses /health/network | Uses Other |
|------|--------------|---------------------|------------|
| HealthDashboard.jsx | ✅ | ❌ | ✅ |
| NetworkHealth.jsx | ❌ | ✅ | ✅ |
| ResilienceDashboard.jsx | ❌ | ❌ | ✅ |
| AssetDetails.jsx | ✅ | ❌ | ✅ |
| SensorDetails.jsx | ❌ | ❌ | ✅ |
| (35 more) | Various | Various | Various |

### Services (50)

| Service | Depends on Routes | Affected |
|--------|------------------|---------|
| HealthService | /health/* | Yes |
| NetworkHealthService | /health/* | Yes |
| AssetService | /assets/* | Yes |
| (47 more) | Various | Yes |

### Tests (38)

| Test File | Tests Routes | Affected |
|-----------|-------------|---------|
| test_health.py | /health/* | Yes |
| test_network_health.py | /health/* | Yes |
| test_assets.py | /assets/* | Yes |
| (35 more) | Various | Yes |

---

## Phase 8: Rollback Plan

### Rollback Strategy

1. **Database backup** before refactor
2. **Feature flag** for new routes
3. **Dual support** during transition
4. **Gradual migration** of consumers

### Rollback Steps

1. Disable new routes
2. Re-enable old routes
3. Deploy previous version
4. Restore database if needed

---

## No Code Modifications Made

Per Task 080E constraints, **no code modifications were made**. This is an observation report only.

---

## Next Steps

- Proceed to Phase 7: Release Impact
