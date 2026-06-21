# Viewer Target Architecture

**Generated:** 2026-06-21
**Repository:** DigiTwinXR-SAAS
**Branch:** feature/tasks-024-029-extensible-architecture
**Phase:** 7 - Recommended Target Architecture

---

## Executive Summary

This document provides the recommended target architecture for map viewers based on all previous analysis phases. Evidence is derived from filesystem inspection only. **No code modifications were made.**

---

## Status Legend

| Status | Description |
|--------|-------------|
| 🟢 GREEN | Ready for production |
| 🟡 YELLOW | Ready with caveats |
| 🔴 RED | Not ready / Deprecated |

---

## Recommended Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  RECOMMENDED TARGET ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  PRIMARY 2D BASE MAP                                                     │
│  └── MapLibre GL ─────────────────────────────────► PRIMARY            │
│                                                                          │
│  PRIMARY 3D VIEWER                                                      │
│  └── Cesium JS ────────────────────────────────────► PRIMARY            │
│                                                                          │
│  ANALYTICS VIEWER                                                        │
│  └── Kepler.gl ─────────────────────────────────────► PRIMARY          │
│                                                                          │
│  CATALOG / FEDERATION VIEWER                                             │
│  └── TerriaJS ──────────────────────────────────────► SECONDARY         │
│                                                                          │
│  VIDEO OVERLAY LAYER                                                   │
│  └── Custom Canvas ────────────────────────────────► INTEGRATED          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Primary 2D Base Map

### Recommendation: MapLibre GL

| Attribute | Status | Notes |
|-----------|--------|-------|
| **Status** | 🟡 YELLOW | Currently placeholder |
| **Implementation Priority** | HIGH | Core infrastructure |
| **Components** | 12 | All need implementation |

### Components to Implement

| Component | Priority | Status |
|-----------|----------|--------|
| MapLibreViewer | HIGH | ⚠️ Placeholder |
| MapLibreContext | HIGH | ⚠️ Placeholder |
| LayerManager | HIGH | ⚠️ Placeholder |
| CameraController | HIGH | ⚠️ Placeholder |
| TileCacheManager | MEDIUM | ⚠️ Placeholder |
| OfflineMapManager | MEDIUM | ⚠️ Placeholder |
| VectorTileManager | HIGH | ⚠️ Placeholder |
| StyleManager | MEDIUM | ⚠️ Placeholder |
| SynchronizationManager | MEDIUM | ⚠️ Placeholder |
| PMTilesManager | LOW | ⚠️ Placeholder |

### Implementation Status

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Implemented | 0 | 0% |
| ⚠️ Placeholder | 12 | 100% |
| ❌ Missing | 0 | 0% |

### Recommendation

**ACTION:** Implement MapLibre as primary 2D viewer

**RATIONALE:**
- Modern, actively developed
- Vector tile support
- Lightweight bundle
- Open source

---

## Phase 2: Primary 3D Viewer

### Recommendation: Cesium JS

| Attribute | Status | Notes |
|-----------|--------|-------|
| **Status** | 🟢 GREEN | Already implemented |
| **Components** | 9 | All functional |

### Components Status

| Component | Priority | Status |
|-----------|----------|--------|
| GlobeViewer | HIGH | ✅ Implemented |
| CesiumContext | HIGH | ✅ Implemented |
| TilesetLoader | HIGH | ✅ Implemented |
| TerrainManager | HIGH | ✅ Implemented |
| CameraController | HIGH | ✅ Implemented |
| Asset3DLayer | HIGH | ✅ Implemented |
| SceneController | MEDIUM | ✅ Implemented |
| TimelineController | MEDIUM | ✅ Implemented |

### Recommendation

**ACTION:** Keep Cesium as primary 3D viewer

**RATIONALE:**
- Already implemented
- Industry standard
- Full 3D support
- Timeline built-in

---

## Phase 3: Analytics Viewer

### Recommendation: Kepler.gl

| Attribute | Status | Notes |
|-----------|--------|-------|
| **Status** | 🟡 YELLOW | Currently placeholder |
| **Implementation Priority** | HIGH | Core analytics |

### Components to Implement

| Component | Priority | Status |
|-----------|----------|--------|
| KeplerViewer | HIGH | ⚠️ Placeholder |
| KeplerContext | HIGH | ⚠️ Placeholder |
| DatasetManager | HIGH | ⚠️ Placeholder |
| AggregationManager | HIGH | ⚠️ Placeholder |
| AnalyticsLayerManager | HIGH | ⚠️ Placeholder |
| ClusterManager | MEDIUM | ⚠️ Placeholder |
| FilterManager | MEDIUM | ⚠️ Placeholder |
| HeatmapManager | MEDIUM | ⚠️ Placeholder |
| FlowMapManager | MEDIUM | ⚠️ Placeholder |
| TemporalDatasetManager | HIGH | ⚠️ Placeholder |
| TrajectoryManager | MEDIUM | ⚠️ Placeholder |
| SynchronizationManager | MEDIUM | ⚠️ Placeholder |

### Recommendation

**ACTION:** Implement Kepler as analytics viewer

**RATIONALE:**
- Purpose-built for analytics
- Multiple layer types
- Temporal data support
- Optimized for large datasets

---

## Phase 4: Catalog/Federation Viewer

### Recommendation: TerriaJS (Optional)

| Attribute | Status | Notes |
|-----------|--------|-------|
| **Status** | 🟡 YELLOW | Currently placeholder |
| **Implementation Priority** | MEDIUM | If federation needed |

### Alternative: Custom Federation

If TerriaJS is too heavy, implement custom federation:

| Component | Description |
|-----------|-------------|
| CatalogManager | Custom data source management |
| LayerCatalog | Custom layer browser |
| FederationManager | Custom multi-source integration |

### Recommendation

**ACTION:** Decide based on federation requirements

**IF FEDERATION CRITICAL:**
- Implement TerriaJS
- Accept bundle size increase

**IF FEDERATION NOT CRITICAL:**
- Implement custom catalog
- Keep architecture simple

---

## Phase 5: Video Overlay Viewer

### Recommendation: Integrated Canvas Layer

| Attribute | Status | Notes |
|-----------|--------|-------|
| **Status** | 🔴 RED | Not implemented |
| **Implementation Priority** | MEDIUM | Future feature |

### Implementation Approach

| Layer | Viewer | Integration |
|-------|-------|------------|
| Video Overlay | MapLibre | Canvas layer |
| Video Overlay | Cesium | Imagery provider |
| Detection Overlay | Kepler | Custom layer |
| Annotation Layer | All | DOM overlay |

### Recommendation

**ACTION:** Implement video overlay as integrated layer

**RATIONALE:**
- Works across all viewers
- Centralized video processing
- Consistent UI

---

## Phase 6: Component Summary

### Recommended Architecture by Role

| Role | Viewer | Status | Priority |
|------|--------|--------|----------|
| **2D Base Map** | MapLibre GL | 🟡 YELLOW | HIGH |
| **3D Globe** | Cesium JS | 🟢 GREEN | HIGH |
| **Analytics** | Kepler.gl | 🟡 YELLOW | HIGH |
| **Catalog/Federation** | TerriaJS (or custom) | 🟡 YELLOW | MEDIUM |
| **Video Overlay** | Integrated Layer | 🔴 RED | MEDIUM |
| **Timeline** | Cesium Timeline | 🟢 GREEN | HIGH |

---

## Phase 7: Implementation Priority

### Priority 1: Critical Infrastructure

| Component | Viewer | Action |
|-----------|--------|--------|
| MapLibreViewer | MapLibre | Implement |
| Cesium GlobeViewer | Cesium | Keep |
| KeplerViewer | Kepler | Implement |

### Priority 2: Supporting Infrastructure

| Component | Viewer | Action |
|-----------|--------|--------|
| Layer management | All | Standardize |
| Camera sync | MapLibre/Cesium | Implement |
| Timeline sync | Cesium/Kepler | Keep |

### Priority 3: Advanced Features

| Component | Viewer | Action |
|-----------|--------|--------|
| TerriaJS | TerriaJS | Decide |
| Video overlay | All | Future |
| Custom federation | Custom | Future |

---

## Phase 8: Dependency Cleanup

### Components to Remove/Deprecate

| Component | Reason |
|-----------|--------|
| TerriaViewer (if not needed) | Heavy framework |
| Leaflet (via TerriaJS) | Redundant with MapLibre |
| Duplicate SynchronizationManager | Share between MapLibre/Kepler |

### Components to Keep

| Component | Reason |
|-----------|--------|
| Cesium GlobeViewer | 3D standard |
| MapLibreViewer | 2D standard |
| KeplerViewer | Analytics standard |

---

## Phase 9: Final Assessment

### Viewer Status Summary

| Viewer | Role | Status | Action |
|--------|------|--------|--------|
| **MapLibre** | 2D Base Map | 🟡 YELLOW | IMPLEMENT |
| **Cesium** | 3D Globe | 🟢 GREEN | KEEP |
| **Kepler** | Analytics | 🟡 YELLOW | IMPLEMENT |
| **TerriaJS** | Federation | 🟡 YELLOW | DECIDE |

### Overall Architecture Status

| Component | Status | Priority |
|-----------|--------|----------|
| 2D Viewer | 🟡 YELLOW | HIGH |
| 3D Viewer | 🟢 GREEN | HIGH |
| Analytics | 🟡 YELLOW | HIGH |
| Federation | 🟡 YELLOW | MEDIUM |
| Video | 🔴 RED | LOW |

---

## Phase 10: Action Items

### Immediate Actions

| # | Action | Priority | Owner |
|---|--------|----------|-------|
| 1 | Implement MapLibre base map | HIGH | Frontend |
| 2 | Keep Cesium as-is | HIGH | Frontend |
| 3 | Implement Kepler analytics | HIGH | Frontend |
| 4 | Share SynchronizationManager | MEDIUM | Frontend |

### Short-term Actions

| # | Action | Priority | Owner |
|---|--------|----------|-------|
| 5 | Decide on TerriaJS | MEDIUM | Architecture |
| 6 | Add video overlay layer | MEDIUM | Frontend |
| 7 | Implement timeline sync | MEDIUM | Frontend |

### Long-term Actions

| # | Action | Priority | Owner |
|---|--------|----------|-------|
| 8 | Custom federation (if needed) | LOW | Architecture |
| 9 | AI overlay integration | LOW | Frontend |
| 10 | Performance optimization | LOW | Frontend |

---

## No Code Modifications Made

Per Task 080G constraints, **no code modifications were made**. This is an observation report only.

---

## Document Index

All viewer architecture reports:

| Document | Phase |
|----------|-------|
| viewer_inventory.md | 1 |
| viewer_role_analysis.md | 2 |
| viewer_duplication_report.md | 3 |
| viewer_dependency_graph.md | 4 |
| viewer_convergence_options.md | 5 |
| viewer_future_compatibility.md | 6 |
| viewer_target_architecture.md | 7 |
