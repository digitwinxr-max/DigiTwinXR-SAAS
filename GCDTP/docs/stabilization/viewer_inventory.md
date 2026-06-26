# Viewer Inventory

**Generated:** 2026-06-21
**Repository:** DigiTwinXR-SAAS
**Branch:** feature/tasks-024-029-extensible-architecture
**Phase:** 1 - Viewer Inventory

---

## Executive Summary

This document provides a complete inventory of all map viewers and map-related components in the frontend. Evidence is derived from filesystem inspection only. **No code modifications were made.**

---

## Viewer Summary

| Viewer | Location | Status | Components |
|--------|----------|--------|------------|
| MapLibre | `frontend/src/maplibre/` | ⚠️ Placeholder | 12 |
| Cesium | `frontend/src/cesium/` | ✅ Implemented | 9 |
| TerriaJS | `frontend/src/terria/` | ⚠️ Placeholder | 11 |
| Kepler.gl | `frontend/src/kepler/` | ⚠️ Placeholder | 14 |

---

## Phase 1: MapLibre Viewer

**Location:** `frontend/src/maplibre/`
**Status:** ⚠️ Placeholder
**Component Count:** 12
**Package:** Not in package.json (placeholder only)

### Components

| Component | File | Purpose |
|-----------|------|---------|
| MapLibreViewer | `MapLibreViewer.tsx` | Main 2D map viewer |
| MapLibreContext | `MapLibreContext.tsx` | React context provider |
| CameraController | `CameraController.tsx` | Camera/view controls |
| LayerManager | `LayerManager.tsx` | Layer lifecycle management |
| OfflineMapManager | `OfflineMapManager.tsx` | Offline map support |
| TileCacheManager | `TileCacheManager.tsx` | Tile caching |
| PMTilesManager | `PMTilesManager.tsx` | PMTiles format support |
| VectorTileManager | `VectorTileManager.tsx` | Vector tile handling |
| StyleManager | `StyleManager.tsx` | Map styling |
| SynchronizationManager | `SynchronizationManager.tsx` | Cross-viewer sync |
| Types | `maplibre_types.ts` | TypeScript definitions |
| Index | `index.ts` | Module exports |

### Pages Using MapLibre

| Page | File | Viewer Usage |
|------|------|-------------|
| Map | `Map.jsx` | MapLibreViewer |
| VectorMapPage | `VectorMapPage.tsx` | MapLibreViewer |
| GeoPortal | `GeoPortal.jsx` | MapLibreViewer + TerriaJS |

### API Dependencies

```
Frontend API modules used:
- assets.js (asset data)
- sensors.js (sensor data)
- events.js (event overlay)
```

### Placeholder Evidence

```typescript
// MapLibreViewer.tsx line 35
// Placeholder - actual implementation would use maplibre-gl
setIsReady(true);
onMapReady?.({});
```

---

## Phase 2: Cesium Viewer

**Location:** `frontend/src/cesium/`
**Status:** ✅ Implemented
**Component Count:** 9
**Package:** Not in package.json (may be external)

### Components

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
| __init__ | `__init__.ts` | Module exports |

### Pages Using Cesium

| Page | File | Viewer Usage |
|------|------|-------------|
| DigitalTwin3DPage | `DigitalTwin3DPage.tsx` | GlobeViewer |
| TerriaPortalPage | `TerriaPortalPage.tsx` | GlobeViewer (via TerriaJS) |

### API Dependencies

```
Frontend API modules used:
- assets.js (3D asset loading)
- sensors.js (sensor data)
- timeline.js (timeline sync)
```

### Implementation Evidence

```typescript
// GlobeViewer.tsx line 45
const {
  initializeViewer,
  destroyViewer,
  isInitialized,
  isLoading,
  error,
  viewer,
} = useCesium();

// Full implementation with CesiumContext
```

---

## Phase 3: TerriaJS Viewer

**Location:** `frontend/src/terria/`
**Status:** ⚠️ Placeholder
**Component Count:** 11
**Package:** Not in package.json (placeholder only)

### Components

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
| Types | `terria_types.ts` | TypeScript definitions |
| Index | `index.ts` | Module exports |

### Pages Using TerriaJS

| Page | File | Viewer Usage |
|------|------|-------------|
| GeoPortal | `GeoPortal.jsx` | TerriaViewer + MapLibreViewer |
| TerriaPortalPage | `TerriaPortalPage.tsx` | TerriaViewer |

### API Dependencies

```
Frontend API modules used:
- knowledge.js (catalog data)
- sensors.js (sensor catalog)
- semantic.js (semantic catalog)
```

### Placeholder Evidence

```typescript
// TerriaViewer.tsx line 39
<div className="leaflet-placeholder">
  Leaflet 2D View
</div>

// TerriaViewer.tsx line 47
<div className="cesium-placeholder">
  Cesium 3D View
</div>

// TerriaViewer.tsx line 55
<div className="terria-placeholder">
  Terria View
</div>
```

---

## Phase 4: Kepler.gl Viewer

**Location:** `frontend/src/kepler/`
**Status:** ⚠️ Placeholder
**Component Count:** 14
**Package:** Not in package.json (placeholder only)

### Components

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
| Types | `kepler_types.ts` | TypeScript definitions |
| Index | `index.ts` | Module exports |

### Pages Using Kepler

| Page | File | Viewer Usage |
|------|------|-------------|
| AnalyticsMapPage | `AnalyticsMapPage.tsx` | KeplerViewer |

### API Dependencies

```
Frontend API modules used:
- measurements.js (temporal data)
- sensors.js (sensor data)
- events.js (event analytics)
```

### Placeholder Evidence

```typescript
// KeplerViewer.tsx line 75
<div className="kepler-placeholder">
  Kepler.gl Analytics View
</div>
```

---

## Phase 5: Shared Components

### Cross-Viewer Components

| Component | Location | Shared By |
|-----------|----------|-----------|
| SynchronizationManager | `maplibre/SynchronizationManager.tsx` | MapLibre, Kepler |
| CameraController | `maplibre/CameraController.tsx` | MapLibre |
| CameraController | `cesium/CameraController.tsx` | Cesium |
| TimelineController | `cesium/TimelineController.tsx` | Cesium |
| TimelineLayerManager | `terria/TimelineLayerManager.tsx` | TerriaJS |

### Common Patterns

```
Context Providers:
├── MapLibreContext
├── CesiumContext
├── TerriaContext
└── KeplerContext
```

---

## Phase 6: API Module Usage

### Frontend API Modules (22 total)

| Module | Used by Viewers | Notes |
|--------|----------------|-------|
| assets.js | MapLibre, Cesium, Terria, Kepler | Asset data |
| sensors.js | MapLibre, Cesium, Terria, Kepler | Sensor catalog |
| events.js | MapLibre, Kepler | Event overlay |
| measurements.js | Kepler | Temporal data |
| knowledge.js | Terria | Catalog data |
| semantic.js | Terria | Semantic catalog |
| timeline.js | Cesium | Timeline sync |
| health.js | MapLibre | Health overlay |

---

## Phase 7: Component Count Summary

| Viewer | Components | Functional | Placeholder |
|--------|-----------|------------|-------------|
| MapLibre | 12 | 0 | 12 |
| Cesium | 9 | 9 | 0 |
| TerriaJS | 11 | 0 | 11 |
| Kepler.gl | 14 | 0 | 14 |
| **Total** | **46** | **9** | **37** |

---

## Phase 8: Dependency Summary

### Missing Packages

Based on package.json inspection:

| Package | Used By | Status |
|---------|---------|--------|
| maplibre-gl | MapLibre | ❌ Not in dependencies |
| cesium | Cesium | ❌ Not in dependencies |
| terriajs | TerriaJS | ❌ Not in dependencies |
| kepler.gl | Kepler | ❌ Not in dependencies |

**Note:** Only leaflet and react-leaflet are in package.json.

---

## No Code Modifications Made

Per Task 080G constraints, **no code modifications were made**. This is an observation report only.

---

## Next Steps

- Proceed to Phase 2: Role Analysis
