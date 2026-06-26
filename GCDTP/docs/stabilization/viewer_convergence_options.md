# Viewer Convergence Options

**Generated:** 2026-06-21
**Repository:** DigiTwinXR-SAAS
**Branch:** feature/tasks-024-029-extensible-architecture
**Phase:** 5 - Convergence Options

---

## Executive Summary

This document evaluates four convergence options for the map viewer architecture. Evidence is derived from filesystem inspection only. **No code modifications were made.**

---

## Assessment Criteria

| Criterion | Weight | Description |
|-----------|--------|-------------|
| complexity | HIGH | Implementation and maintenance complexity |
| maintainability | HIGH | Ease of future changes |
| extensibility | HIGH | Ability to add features |
| video_readiness | MEDIUM | Support for video overlays |
| ai_readiness | MEDIUM | Support for AI features |

---

## Option A: MapLibre Primary + Terria Catalog + Kepler Analytics

### Description

```
┌─────────────────────────────────────────────────────────────────┐
│                    OPTION A: Hybrid Architecture                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Primary 2D      ──► MapLibre GL (Vector Maps)                 │
│                                                                  │
│  Catalog          ──► TerriaJS (Data Federation)                │
│                                                                  │
│  Analytics        ──► Kepler.gl (Data Visualization)            │
│                                                                  │
│  3D               ──► Cesium (Digital Twin)                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Architecture

| Role | Viewer | Priority |
|------|-------|----------|
| 2D Base Map | MapLibre | PRIMARY |
| Data Catalog | TerriaJS | SECONDARY |
| Analytics | Kepler | PRIMARY |
| 3D | Cesium | PRIMARY |

### Pros

| Pros | Description |
|------|-------------|
| Best-in-class | Each viewer optimized for its role |
| Clear separation | Distinct responsibilities |
| Feature completeness | All requirements covered |
| Federation | TerriaJS handles multi-source |

### Cons

| Cons | Description |
|------|-------------|
| Multiple libraries | 4 different dependencies |
| Bundle size | Large JavaScript bundles |
| Learning curve | 4 different APIs |
| Integration | Cross-viewer sync complex |

### Complexity Assessment

| Criterion | Score | Notes |
|----------|-------|-------|
| complexity | 🟡 MEDIUM | 4 libraries to manage |
| maintainability | 🟢 HIGH | Clear separation |
| extensibility | 🟢 HIGH | Easy to add features |
| video_readiness | 🟡 MEDIUM | Requires integration |
| ai_readiness | 🟡 MEDIUM | Requires integration |

**Overall:** 🟢 **RECOMMENDED**

---

## Option B: TerriaJS-Centric

### Description

```
┌─────────────────────────────────────────────────────────────────┐
│                    OPTION B: TerriaJS-Centric                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  All Maps         ──► TerriaJS (wrapper)                         │
│                      │                                            │
│                      ├── 2D ──► Leaflet                         │
│                      ├── 3D ──► Cesium                          │
│                      └── Analytics ──► Kepler (via custom)      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Architecture

| Role | Viewer | Priority |
|------|-------|----------|
| 2D | Leaflet (via TerriaJS) | PRIMARY |
| 3D | Cesium (via TerriaJS) | PRIMARY |
| Analytics | Kepler (via custom) | SECONDARY |
| Federation | TerriaJS | PRIMARY |

### Pros

| Pros | Description |
|------|-------------|
| Single framework | One API to learn |
| Federation built-in | Multi-source support |
| 2D + 3D | Leaflet + Cesium |
| Catalog | Layer catalog built-in |

### Cons

| Cons | Description |
|------|-------------|
| TerriaJS complexity | Heavy framework |
| Kepler integration | Custom work required |
| Bundle size | Large (TerriaJS + all adapters) |
| Performance | Heavy for simple maps |
| Customization | Limited by TerriaJS |

### Complexity Assessment

| Criterion | Score | Notes |
|----------|-------|-------|
| complexity | 🔴 HIGH | Heavy framework |
| maintainability | 🟡 MEDIUM | Framework constraints |
| extensibility | 🟡 MEDIUM | Limited by TerriaJS |
| video_readiness | 🟡 MEDIUM | Via extensions |
| ai_readiness | 🟡 MEDIUM | Via extensions |

**Overall:** 🟡 **CONDITIONAL**

---

## Option C: MapLibre-Only

### Description

```
┌─────────────────────────────────────────────────────────────────┐
│                    OPTION C: MapLibre-Only                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  2D Maps         ──► MapLibre GL (primary)                      │
│                                                                  │
│  Analytics       ──► MapLibre (layers) + Charts                 │
│                                                                  │
│  3D              ──► MapLibre GL JS (limited)                  │
│                                                                  │
│  Federation      ──► Custom implementation                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Architecture

| Role | Viewer | Priority |
|------|-------|----------|
| 2D | MapLibre | PRIMARY |
| Analytics | MapLibre + Charts | PRIMARY |
| 3D | MapLibre (limited) | SECONDARY |
| Federation | Custom | SECONDARY |

### Pros

| Pros | Description |
|------|-------------|
| Single library | One dependency |
| Performance | Fast 2D rendering |
| Modern | Active development |
| Lightweight | Small bundle |
| Open source | Community support |

### Cons

| Cons | Description |
|------|-------------|
| No 3D | Limited globe support |
| No federation | Custom implementation needed |
| No analytics | Basic layer support only |
| Kepler lost | No dedicated analytics |

### Complexity Assessment

| Criterion | Score | Notes |
|----------|-------|-------|
| complexity | 🟢 LOW | Single library |
| maintainability | 🟢 HIGH | One codebase |
| extensibility | 🟡 MEDIUM | Limited by MapLibre |
| video_readiness | 🟡 MEDIUM | Via layers |
| ai_readiness | 🟡 MEDIUM | Via layers |

**Overall:** 🟡 **LIMITED**

---

## Option D: MapLibre + Cesium

### Description

```
┌─────────────────────────────────────────────────────────────────┐
│                    OPTION D: MapLibre + Cesium                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  2D Maps         ──► MapLibre GL (primary)                      │
│                                                                  │
│  3D Globe        ──► Cesium JS (primary)                         │
│                                                                  │
│  Analytics       ──► Recharts / D3 (separate panel)             │
│                                                                  │
│  Federation      ──► Custom implementation                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Architecture

| Role | Viewer | Priority |
|------|-------|----------|
| 2D | MapLibre | PRIMARY |
| 3D | Cesium | PRIMARY |
| Analytics | Recharts/D3 | PRIMARY |
| Federation | Custom | SECONDARY |

### Pros

| Pros | Description |
|------|-------------|
| Best 2D | MapLibre optimized |
| Best 3D | Cesium industry standard |
| Clean separation | 2D vs 3D clear |
| Performance | Both are performant |
| Lightweight | No TerriaJS overhead |

### Cons

| Cons | Description |
|------|-------------|
| No federation | Need custom implementation |
| No Kepler | Lose dedicated analytics |
| Two APIs | MapLibre + Cesium |
| TerriaJS lost | Lose multi-source support |

### Complexity Assessment

| Criterion | Score | Notes |
|----------|-------|-------|
| complexity | 🟡 MEDIUM | 2 libraries |
| maintainability | 🟢 HIGH | Clear separation |
| extensibility | 🟡 MEDIUM | Need custom for federation |
| video_readiness | 🟡 MEDIUM | Both support overlays |
| ai_readiness | 🟡 MEDIUM | Both support overlays |

**Overall:** 🟢 **RECOMMENDED**

---

## Option Comparison Matrix

| Criterion | Option A | Option B | Option C | Option D |
|-----------|----------|----------|----------|----------|
| complexity | 🟡 MEDIUM | 🔴 HIGH | 🟢 LOW | 🟡 MEDIUM |
| maintainability | 🟢 HIGH | 🟡 MEDIUM | 🟢 HIGH | 🟢 HIGH |
| extensibility | 🟢 HIGH | 🟡 MEDIUM | 🟡 MEDIUM | 🟡 MEDIUM |
| video_readiness | 🟡 MEDIUM | 🟡 MEDIUM | 🟡 MEDIUM | 🟡 MEDIUM |
| ai_readiness | 🟡 MEDIUM | 🟡 MEDIUM | 🟡 MEDIUM | 🟡 MEDIUM |
| 2D capability | 🟢 HIGH | 🟢 HIGH | 🟢 HIGH | 🟢 HIGH |
| 3D capability | 🟢 HIGH | 🟢 HIGH | ⚠️ LIMITED | 🟢 HIGH |
| analytics | 🟢 HIGH | 🟡 MEDIUM | ⚠️ LIMITED | 🟡 MEDIUM |
| federation | 🟢 HIGH | 🟢 HIGH | ❌ NONE | ⚠️ LIMITED |
| bundle size | 🔴 HIGH | 🔴 HIGH | 🟢 LOW | 🟡 MEDIUM |

---

## Decision Matrix

### Use Option A if:

- Federation is critical
- Best-in-class analytics needed
- Bundle size is not a concern
- Team can manage 4 libraries

### Use Option B if:

- Federation is the top priority
- Multi-source catalog is essential
- Willing to accept TerriaJS constraints
- Need built-in storytelling

### Use Option C if:

- Only need 2D maps
- Bundle size is critical
- Custom analytics acceptable
- Federation not needed

### Use Option D if:

- Need best 2D and 3D
- Federation not critical
- Custom analytics acceptable
- Simpler than Option A

---

## Recommendation

**Primary Recommendation:** Option A (Hybrid)

**Rationale:**
- Provides best-in-class for each role
- Clear separation of concerns
- Federation built-in (TerriaJS)
- Analytics built-in (Kepler)
- 3D industry standard (Cesium)

**Alternative:** Option D (MapLibre + Cesium)

**Alternative Rationale:**
- If federation is not critical
- Simpler architecture
- Smaller bundle
- Accept custom analytics

---

## No Code Modifications Made

Per Task 080G constraints, **no code modifications were made**. This is an observation report only.

---

## Next Steps

- Proceed to Phase 6: Future Compatibility
