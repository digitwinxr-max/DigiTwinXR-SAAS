# Frontend Consolidation Report

**Generated:** 2026-06-21
**Repository:** DigiTwinXR-SAAS
**Branch:** feature/tasks-024-029-extensible-architecture
**Phase:** 5 - Frontend Consolidation

---

## Executive Summary

This document inventories the three map visualization libraries in the frontend and recommends a convergence strategy. Evidence is derived from filesystem inspection only. **No UI modifications were made.**

---

## Map Visualization Libraries Inventory

### 1. MapLibre GL

**Location:** `frontend/src/maplibre/`
**ADR Reference:** ADR-0044 (MapLibre Vector Tile Layer)
**Component Count:** 10

| Component | File | Purpose |
|-----------|------|---------|
| MapLibreViewer | `MapLibreViewer.tsx` | Main 2D map viewer |
| MapLibreContext | `MapLibreContext.tsx` | React context provider |
| LayerManager | `LayerManager.tsx` | Layer lifecycle management |
| CameraController | `CameraController.tsx` | Camera/view controls |
| OfflineMapManager | `OfflineMapManager.tsx` | Offline map support |
| TileCacheManager | `TileCacheManager.tsx` | Tile caching |
| PMTilesManager | `PMTilesManager.tsx` | PMTiles format support |
| VectorTileManager | `VectorTileManager.tsx` | Vector tile handling |
| StyleManager | `StyleManager.tsx` | Map styling |
| SynchronizationManager | `SynchronizationManager.tsx` | Cross-viewer sync |

**Current Status:** ⚠️ Placeholder div at line 80

---

### 2. CesiumJS

**Location:** `frontend/src/cesium/`
**ADR Reference:** ADR-0029 (Cesium 3D Visualization)
**Component Count:** 8

| Component | File | Purpose |
|-----------|------|---------|
| GlobeViewer | `GlobeViewer.tsx` | Main 3D globe viewer |
| CesiumContext | `CesiumContext.tsx` | React context provider |
| TilesetLoader | `TilesetLoader.tsx` | 3D tileset loading |
| TerrainManager | `TerrainManager.tsx` | Terrain data management |
| CameraController | `CameraController.tsx` | 3D camera controls |
| Asset3DLayer | `Asset3DLayer.tsx` | 3D asset overlay |
| SceneController | `SceneController.tsx` | Scene settings |
| TimelineController | `TimelineController.tsx` | Timeline synchronization |

**Current Status:** ✅ Full implementation

---

### 3. TerriaJS

**Location:** `frontend/src/terria/`
**ADR Reference:** ADR-0043 (TerriaJS Federation Layer)
**Component Count:** 9

| Component | File | Purpose |
|-----------|------|---------|
| TerriaViewer | `TerriaViewer.tsx` | Main TerriaJS viewer |
| TerriaContext | `TerriaContext.tsx` | React context provider |
| CatalogManager | `CatalogManager.tsx` | Data catalog management |
| FederationManager | `FederationManager.tsx` | Service federation |
| LayerCatalog | `LayerCatalog.tsx` | Layer browser |
| MetadataExplorer | `MetadataExplorer.tsx` | Metadata display |
| ShareManager | `ShareManager.tsx` | Share functionality |
| StoryMapManager | `StoryMapManager.tsx` | Story map creation |
| TimelineLayerManager | `TimelineLayerManager.tsx` | Timeline sync |

**Current Status:** ⚠️ Placeholder divs for Leaflet/Cesium/Terria at lines 39, 47, 55

---

### 4. Kepler.gl

**Location:** `frontend/src/kepler/`
**ADR Reference:** ADR-0045 (Kepler Analytics Layer)
**Component Count:** 12

| Component | File | Purpose |
|-----------|------|---------|
| KeplerViewer | `KeplerViewer.tsx` | Main Kepler viewer |
| KeplerContext | `KeplerContext.tsx` | React context provider |
| DatasetManager | `DatasetManager.tsx` | Dataset management |
| AggregationManager | `AggregationManager.tsx` | Data aggregation |
| AnalyticsLayerManager | `AnalyticsLayerManager.tsx` | Analytics layers |
| ClusterManager | `ClusterManager.tsx` | Clustering |
| FilterManager | `FilterManager.tsx` | Data filtering |
| FlowMapManager | `FlowMapManager.tsx` | Flow visualization |
| HeatmapManager | `HeatmapManager.tsx` | Heatmap rendering |
| SynchronizationManager | `SynchronizationManager.tsx` | Cross-sync |
| TemporalDatasetManager | `TemporalDatasetManager.tsx` | Temporal data |
| TrajectoryManager | `TrajectoryManager.tsx` | Trajectory display |

**Current Status:** ⚠️ Placeholder div at line 75

---

## Component Comparison

| Feature | MapLibre | Cesium | TerriaJS | Kepler.gl |
|---------|----------|--------|----------|-----------|
| 2D Maps | ✅ | ❌ | ✅ | ❌ |
| 3D Globe | ❌ | ✅ | ✅ | ❌ |
| Data Federation | ❌ | ❌ | ✅ | ❌ |
| Analytics | ❌ | ❌ | ❌ | ✅ |
| Vector Tiles | ✅ | ❌ | ✅ | ❌ |
| Raster Tiles | ✅ | ✅ | ✅ | ✅ |
| Timeline Sync | ⚠️ | ✅ | ✅ | ⚠️ |
| Offline Support | ✅ | ✅ | ❌ | ❌ |

---

## Shared Components Analysis

### Cross-Library Components

| Component | MapLibre | Cesium | TerriaJS | Kepler |
|-----------|----------|--------|----------|---------|
| CameraController | ✅ | ✅ | ❌ | ❌ |
| SynchronizationManager | ✅ | ❌ | ❌ | ✅ |
| LayerManager | ✅ | ❌ | ❌ | ❌ |

### Potential Shared Components

1. **CameraController** - Exists in MapLibre and Cesium, could be unified
2. **SynchronizationManager** - Exists in MapLibre and Kepler, could be unified
3. **TimelineController** - Similar functionality across libraries

---

## Page-to-Viewer Mapping

| Page | Primary Viewer | Secondary Viewer |
|------|---------------|------------------|
| Map | MapLibre | - |
| GeoPortal | MapLibre | TerriaJS |
| DigitalTwin3DPage | Cesium | - |
| TerriaPortalPage | TerriaJS | - |
| VectorMapPage | MapLibre | - |
| AnalyticsMapPage | Kepler | - |

---

## Duplicate Viewer Analysis

### 3D Viewer Duplicates

| Feature | Cesium | TerriaJS |
|---------|--------|----------|
| 3D Globe | ✅ Native | ✅ Via Cesium |
| Terrain | ✅ Native | ✅ Via Cesium |
| 3D Tiles | ✅ Native | ✅ Via Cesium |

**Finding:** TerriaJS wraps Cesium for 3D functionality.

---

### 2D Viewer Duplicates

| Feature | MapLibre | TerriaJS (Leaflet) |
|---------|----------|---------------------|
| 2D Maps | ✅ Native | ✅ Via Leaflet |
| Vector Tiles | ✅ Native | ✅ Via CARTO |
| Raster Tiles | ✅ Native | ✅ Native |

**Finding:** TerriaJS wraps Leaflet for 2D functionality.

---

## Convergence Recommendations

### Option A: Single Viewer Architecture (Recommended)

| Viewer | Primary Use Case | Retire |
|--------|-----------------|--------|
| **MapLibre** | 2D operational maps | TerriaJS 2D |
| **Cesium** | 3D digital twin | TerriaJS 3D |
| **Kepler** | Analytics dashboards | None |

**Rationale:**
- MapLibre: Lightweight, modern, active development
- Cesium: Industry standard for 3D globe visualization
- Kepler: Purpose-built for data analytics

### Option B: TerriaJS as Unified Layer

| Viewer | Status |
|--------|--------|
| **TerriaJS** | Unified viewer |
| MapLibre | Deprecated |
| Cesium | Deprecated |
| Kepler | Independent (different purpose) |

**Rationale:**
- TerriaJS already wraps Leaflet, Cesium, MapLibre
- Federation built-in
- Larger bundle size

### Option C: Keep All Three

| Viewer | Status |
|--------|--------|
| MapLibre | Keep - 2D maps |
| Cesium | Keep - 3D globe |
| TerriaJS | Keep - Data federation |
| Kepler | Keep - Analytics |

**Rationale:**
- Each has unique strengths
- No convergence needed
- Larger bundle size

---

## Recommended Architecture

Based on the codebase analysis, **Option A (Single Viewer per Purpose)** is recommended:

```
┌─────────────────────────────────────────────────────────────┐
│                    Recommended Architecture                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   2D Operational Maps                                       │
│   └── MapLibre GL (primary)                                │
│                                                             │
│   3D Digital Twin                                           │
│   └── CesiumJS (primary)                                   │
│                                                             │
│   Data Federation                                           │
│   └── TerriaJS OR direct MapLibre/Cesium integration       │
│                                                             │
│   Analytics & Visualization                                  │
│   └── Kepler.gl (independent)                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Roadmap (Future)

| Phase | Action | Viewer |
|-------|--------|--------|
| 1 | Deprecate TerriaJS Leaflet wrapper | TerriaJS |
| 2 | Deprecate TerriaJS Cesium wrapper | TerriaJS |
| 3 | Keep TerriaJS for federation only | TerriaJS |
| 4 | Or: Deprecate TerriaJS entirely | TerriaJS |
| 5 | Consolidate camera controllers | MapLibre/Cesium |

---

## No UI Changes Made

Per Task 080D constraints, **no UI modifications were made**. This is a strategic recommendation document only.

---

## Next Steps

- Proceed to Phase 6: Integration Chain Validation
