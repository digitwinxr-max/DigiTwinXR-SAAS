# Viewer Role Analysis

**Generated:** 2026-06-21
**Repository:** DigiTwinXR-SAAS
**Branch:** feature/tasks-024-029-extensible-architecture
**Phase:** 2 - Role Analysis

---

## Executive Summary

This document determines the responsibilities for each map viewer library. Evidence is derived from filesystem inspection only. **No code modifications were made.**

---

## Classification System

| Role | Description |
|------|-------------|
| **base_map** | Basic map display and navigation |
| **catalog** | Data source management |
| **analytics** | Data visualization and analysis |
| **timeline** | Time-based data navigation |
| **3D** | 3D globe and terrain |
| **federation** | Multi-source data integration |
| **storytelling** | Narrative map presentations |

---

## Phase 1: MapLibre Role Analysis

### Primary Role: Base Map (2D)

**Rationale:**
- MapLibre is designed for 2D vector maps
- Primary use case is operational map display
- Optimized for performance on 2D data

### Secondary Roles

| Role | Priority | Evidence |
|------|----------|----------|
| base_map | PRIMARY | 2D vector tile rendering |
| analytics | SECONDARY | Limited by design |
| timeline | SUPPORT | Camera sync only |
| catalog | NO | No catalog features |
| 3D | NO | 2D only |
| federation | NO | Single source only |
| storytelling | NO | No story features |

### MapLibre Components and Roles

| Component | Primary Role | Secondary Role |
|-----------|-------------|----------------|
| MapLibreViewer | base_map | - |
| LayerManager | analytics | catalog |
| CameraController | base_map | timeline |
| OfflineMapManager | base_map | - |
| TileCacheManager | base_map | - |
| PMTilesManager | base_map | analytics |
| VectorTileManager | base_map | analytics |
| StyleManager | base_map | - |
| SynchronizationManager | timeline | - |

### Recommended Use Cases

| Use Case | Fit | Notes |
|----------|-----|-------|
| Asset location map | ✅ PERFECT | 2D base map |
| Sensor network visualization | ✅ PERFECT | Layer support |
| Real-time monitoring | ✅ PERFECT | Performance |
| Event tracking | ✅ GOOD | Limited analytics |
| 3D visualization | ❌ NO | 2D only |
| Multi-source federation | ❌ NO | Not supported |
| Data analytics | ⚠️ LIMITED | Basic layers |

---

## Phase 2: Cesium Role Analysis

### Primary Role: 3D Globe

**Rationale:**
- Cesium is designed for 3D globe visualization
- Industry standard for terrain and 3D tiles
- Built-in 3D asset support

### Secondary Roles

| Role | Priority | Evidence |
|------|----------|----------|
| 3D | PRIMARY | Globe, terrain, 3D tiles |
| timeline | SECONDARY | TimelineController |
| analytics | SUPPORT | 3D visualization |
| base_map | SUPPORT | 2D fallback available |
| catalog | NO | No catalog features |
| federation | NO | Single source only |
| storytelling | NO | No story features |

### Cesium Components and Roles

| Component | Primary Role | Secondary Role |
|-----------|-------------|----------------|
| GlobeViewer | 3D | base_map |
| CesiumContext | 3D | - |
| TilesetLoader | 3D | catalog |
| TerrainManager | 3D | base_map |
| CameraController | 3D | timeline |
| Asset3DLayer | 3D | analytics |
| SceneController | 3D | base_map |
| TimelineController | timeline | analytics |

### Recommended Use Cases

| Use Case | Fit | Notes |
|----------|-----|-------|
| Digital twin 3D view | ✅ PERFECT | Globe + assets |
| Terrain visualization | ✅ PERFECT | Cesium World Terrain |
| 3D asset overlay | ✅ PERFECT | 3D tiles |
| Infrastructure planning | ✅ PERFECT | 3D analysis |
| Historical timeline | ✅ GOOD | Timeline sync |
| Operational 2D map | ⚠️ LIMITED | 2D fallback only |
| Multi-source federation | ❌ NO | Not supported |
| Data analytics | ⚠️ LIMITED | Basic 3D viz |

---

## Phase 3: TerriaJS Role Analysis

### Primary Role: Data Federation

**Rationale:**
- TerriaJS is designed for multi-source data integration
- Built-in catalog management
- Supports multiple map engines (Leaflet, Cesium, MapLibre)

### Secondary Roles

| Role | Priority | Evidence |
|------|----------|----------|
| federation | PRIMARY | Multi-source support |
| catalog | PRIMARY | CatalogManager |
| base_map | SECONDARY | Leaflet/Cesium |
| 3D | SECONDARY | Via Cesium |
| storytelling | SECONDARY | StoryMapManager |
| analytics | NO | No analytics features |
| timeline | SUPPORT | TimelineLayerManager |

### TerriaJS Components and Roles

| Component | Primary Role | Secondary Role |
|-----------|-------------|----------------|
| TerriaViewer | federation | catalog |
| TerriaContext | federation | - |
| CatalogManager | catalog | federation |
| FederationManager | federation | catalog |
| LayerCatalog | catalog | federation |
| MetadataExplorer | catalog | - |
| ShareManager | storytelling | federation |
| StoryMapManager | storytelling | federation |
| TimelineLayerManager | timeline | federation |

### Recommended Use Cases

| Use Case | Fit | Notes |
|----------|-----|-------|
| Data portal | ✅ PERFECT | Federation + catalog |
| Sensor network portal | ✅ PERFECT | Multiple sources |
| Geospatial catalog | ✅ PERFECT | Layer catalog |
| Storytelling | ✅ GOOD | StoryMapManager |
| Multi-source analytics | ⚠️ LIMITED | No built-in analytics |
| Real-time monitoring | ⚠️ LIMITED | Static catalogs |
| Complex 3D | ⚠️ LIMITED | Via Cesium |
| Performance-critical | ⚠️ LIMITED | Heavy framework |

---

## Phase 4: Kepler.gl Role Analysis

### Primary Role: Data Analytics

**Rationale:**
- Kepler.gl is designed for data visualization and analytics
- Built-in layer types for visualization
- Optimized for large dataset rendering

### Secondary Roles

| Role | Priority | Evidence |
|------|----------|----------|
| analytics | PRIMARY | Multiple layer types |
| timeline | SECONDARY | TemporalDatasetManager |
| base_map | SUPPORT | Background map only |
| catalog | NO | No catalog features |
| 3D | NO | 2D only |
| federation | NO | Single dataset |
| storytelling | NO | Limited to trips |

### Kepler.gl Components and Roles

| Component | Primary Role | Secondary Role |
|-----------|-------------|----------------|
| KeplerViewer | analytics | - |
| KeplerContext | analytics | - |
| DatasetManager | analytics | timeline |
| AggregationManager | analytics | - |
| AnalyticsLayerManager | analytics | - |
| ClusterManager | analytics | - |
| FilterManager | analytics | - |
| FlowMapManager | analytics | timeline |
| HeatmapManager | analytics | - |
| SynchronizationManager | timeline | - |
| TemporalDatasetManager | timeline | analytics |
| TrajectoryManager | analytics | timeline |

### Recommended Use Cases

| Use Case | Fit | Notes |
|----------|-----|-------|
| Sensor analytics | ✅ PERFECT | Temporal + spatial |
| Movement analysis | ✅ PERFECT | TrajectoryManager |
| Density visualization | ✅ PERFECT | HeatmapManager |
| Cluster analysis | ✅ PERFECT | ClusterManager |
| Event correlation | ✅ PERFECT | FlowMapManager |
| Multi-source federation | ❌ NO | Single dataset |
| 3D visualization | ❌ NO | 2D only |
| Complex catalog | ❌ NO | No catalog |

---

## Phase 5: Role Matrix

### Viewer x Role Matrix

| Viewer | base_map | catalog | analytics | timeline | 3D | federation | storytelling |
|--------|----------|---------|-----------|----------|-----|-----------|--------------|
| **MapLibre** | ✅ PRIMARY | ⚠️ LIMITED | ⚠️ LIMITED | ⚠️ LIMITED | ❌ NO | ❌ NO | ❌ NO |
| **Cesium** | ⚠️ LIMITED | ❌ NO | ⚠️ LIMITED | ✅ SECONDARY | ✅ PRIMARY | ❌ NO | ❌ NO |
| **TerriaJS** | ✅ SECONDARY | ✅ PRIMARY | ❌ NO | ⚠️ LIMITED | ✅ SECONDARY | ✅ PRIMARY | ✅ SECONDARY |
| **Kepler.gl** | ⚠️ LIMITED | ❌ NO | ✅ PRIMARY | ✅ SECONDARY | ❌ NO | ❌ NO | ❌ NO |

### Best Fit Summary

| Role | Best Viewer | Alternative |
|------|-------------|-------------|
| base_map | MapLibre | Cesium (limited) |
| catalog | TerriaJS | MapLibre (limited) |
| analytics | Kepler.gl | MapLibre (limited) |
| timeline | Cesium | Kepler.gl |
| 3D | Cesium | TerriaJS (via Cesium) |
| federation | TerriaJS | None |
| storytelling | TerriaJS | None |

---

## Phase 6: Architectural Recommendations

### Current State Problem

```
CURRENT:
┌─────────────────────────────────────────────────────────────────┐
│  MapLibre ──► 2D Base Map (placeholder)                         │
│  Cesium   ──► 3D Globe (implemented)                            │
│  TerriaJS ──► Federation (placeholder)                          │
│  Kepler   ──► Analytics (placeholder)                           │
└─────────────────────────────────────────────────────────────────┘
```

### Recommended State

```
RECOMMENDED:
┌─────────────────────────────────────────────────────────────────┐
│  MapLibre ──► Primary 2D Base Map (IMPLEMENT)                   │
│  Cesium   ──► Primary 3D Globe (KEEP)                           │
│  TerriaJS ──► Federation Layer (IMPLEMENT or DEPRECATE)         │
│  Kepler   ──► Analytics View (IMPLEMENT)                         │
└─────────────────────────────────────────────────────────────────┘
```

### Rationale

| Decision | Reason |
|----------|--------|
| Keep Cesium | Already implemented, industry standard |
| Implement MapLibre | Missing base map functionality |
| Implement Kepler | Dedicated analytics (not in others) |
| Decide TerriaJS | Federation is unique but complex |

---

## Phase 7: Role Conflicts

### Overlap Analysis

| Role | Viewers | Conflict Level |
|------|---------|---------------|
| base_map | MapLibre, Cesium, TerriaJS | MEDIUM |
| timeline | Cesium, Kepler | LOW |
| 3D | Cesium, TerriaJS | LOW |
| analytics | MapLibre, Kepler | HIGH |
| catalog | TerriaJS, MapLibre | MEDIUM |
| federation | TerriaJS only | NONE |

### Conflict Resolution

| Conflict | Resolution |
|----------|-----------|
| MapLibre vs Kepler (analytics) | MapLibre = base, Kepler = analytics |
| MapLibre vs TerriaJS (catalog) | TerriaJS = catalog, MapLibre = base |
| Cesium vs TerriaJS (3D) | Cesium = 3D, TerriaJS = federation |

---

## No Code Modifications Made

Per Task 080G constraints, **no code modifications were made**. This is an observation report only.

---

## Next Steps

- Proceed to Phase 3: Duplication Analysis
