# Viewer Dependency Graph

**Generated:** 2026-06-21
**Repository:** DigiTwinXR-SAAS
**Branch:** feature/tasks-024-029-extensible-architecture
**Phase:** 4 - Component Dependency Graph

---

## Executive Summary

This document shows the dependency graph between viewers, pages, components, and API modules. Evidence is derived from filesystem inspection only. **No code modifications were made.**

---

## Phase 1: High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND APPLICATION                              │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         PAGE LAYER (38 pages)                            │
│                                                                          │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│   │    Map      │ │   GeoPortal │ │  Analytics  │ │ DigitalTwin │      │
│   │  (MapLibre) │ │ (TerriaJS)  │ │  (Kepler)  │ │  (Cesium)   │      │
│   └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘      │
└──────────┼───────────────┼───────────────┼───────────────┼──────────────┘
           │               │               │               │
           ▼               ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     VIEWER COMPONENT LAYER                                │
│                                                                          │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│   │  MapLibre   │ │  TerriaJS  │ │   Kepler   │ │   Cesium    │      │
│   │   Viewer    │ │   Viewer   │ │   Viewer   │ │   Viewer    │      │
│   │   (12)      │ │   (11)     │ │   (14)     │ │   (9)       │      │
│   └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘      │
└──────────┼───────────────┼───────────────┼───────────────┼──────────────┘
           │               │               │               │
           │               │               │               │
           └───────────────┼───────────────┼───────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         API MODULE LAYER                                 │
│                                                                          │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│   │ assets  │ │ sensors │ │ events  │ │measure- │ │knowledge│          │
│   │   .js   │ │   .js   │ │   .js   │ │ments.js │ │   .js   │          │
│   └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘          │
└────────┼───────────┼───────────┼───────────┼───────────┼─────────────────┘
         │           │           │           │           │
         └───────────┴───────────┴───────────┴───────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      BACKEND API (178 routes)                            │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 2: Page Dependencies

### Map Page Dependencies

```
Map.jsx
├── Viewers
│   └── MapLibreViewer
│       ├── MapLibreContext
│       ├── LayerManager
│       ├── CameraController
│       └── SynchronizationManager
└── API Modules
    ├── assets.js
    ├── sensors.js
    └── events.js
```

### GeoPortal Page Dependencies

```
GeoPortal.jsx
├── Viewers
│   ├── MapLibreViewer
│   │   ├── MapLibreContext
│   │   └── LayerManager
│   └── TerriaViewer
│       ├── TerriaContext
│       ├── CatalogManager
│       └── FederationManager
└── API Modules
    ├── assets.js
    ├── sensors.js
    ├── knowledge.js
    └── semantic.js
```

### AnalyticsMapPage Dependencies

```
AnalyticsMapPage.tsx
├── Viewers
│   └── KeplerViewer
│       ├── KeplerContext
│       ├── DatasetManager
│       ├── AggregationManager
│       ├── FilterManager
│       ├── HeatmapManager
│       └── SynchronizationManager ⚠️ DUPLICATE
└── API Modules
    ├── measurements.js
    ├── sensors.js
    └── events.js
```

### DigitalTwin3DPage Dependencies

```
DigitalTwin3DPage.tsx
├── Viewers
│   └── GlobeViewer (Cesium)
│       ├── CesiumContext
│       ├── TilesetLoader
│       ├── TerrainManager
│       ├── CameraController
│       ├── Asset3DLayer
│       ├── SceneController
│       └── TimelineController
└── API Modules
    ├── assets.js
    ├── sensors.js
    └── timeline.js
```

---

## Phase 3: Viewer Component Dependencies

### MapLibre Dependencies

```
MapLibreViewer
├── MapLibreContext (provider)
├── LayerManager
├── CameraController
├── OfflineMapManager
├── TileCacheManager
├── PMTilesManager
├── VectorTileManager
├── StyleManager
└── SynchronizationManager
    └── MapLibreContext
```

### Cesium Dependencies

```
GlobeViewer
├── CesiumContext (provider)
├── TilesetLoader
├── TerrainManager
├── CameraController
├── Asset3DLayer
├── SceneController
└── TimelineController
```

### TerriaJS Dependencies

```
TerriaViewer
├── TerriaContext (provider)
├── CatalogManager
├── FederationManager
├── LayerCatalog
├── MetadataExplorer
├── ShareManager
├── StoryMapManager
└── TimelineLayerManager
```

### Kepler Dependencies

```
KeplerViewer
├── KeplerContext (provider)
├── DatasetManager
├── AggregationManager
├── AnalyticsLayerManager
├── ClusterManager
├── FilterManager
├── FlowMapManager
├── HeatmapManager
├── SynchronizationManager ⚠️ DUPLICATE
├── TemporalDatasetManager
└── TrajectoryManager
```

---

## Phase 4: API Module Dependencies

### assets.js

```
assets.js
├── Used by
│   ├── Map.jsx
│   ├── GeoPortal.jsx
│   ├── AnalyticsMapPage.tsx
│   ├── DigitalTwin3DPage.tsx
│   └── ... (all pages)
└── Backend API
    └── /assets/* (8 routes)
```

### sensors.js

```
sensors.js
├── Used by
│   ├── Map.jsx
│   ├── GeoPortal.jsx
│   ├── AnalyticsMapPage.tsx
│   ├── DigitalTwin3DPage.tsx
│   └── ... (all pages)
└── Backend API
    └── /sensors/* (10 routes)
```

### events.js

```
events.js
├── Used by
│   ├── Map.jsx
│   └── AnalyticsMapPage.tsx
└── Backend API
    └── /events/* (10 routes)
```

### measurements.js

```
measurements.js
├── Used by
│   └── AnalyticsMapPage.tsx
└── Backend API
    └── /measurements/* (6 routes)
```

---

## Phase 5: Cross-Dependencies

### Shared Dependencies

| Component | MapLibre | Kepler | Shared |
|-----------|----------|--------|--------|
| SynchronizationManager | ✅ | ✅ | ⚠️ DUPLICATE |

### Shared API Modules

| Module | MapLibre | Cesium | TerriaJS | Kepler | Shared |
|--------|----------|--------|----------|--------|--------|
| assets.js | ✅ | ✅ | ✅ | ✅ | 4 |
| sensors.js | ✅ | ✅ | ✅ | ✅ | 4 |
| events.js | ✅ | ❌ | ❌ | ✅ | 2 |
| timeline.js | ❌ | ✅ | ❌ | ❌ | 1 |
| knowledge.js | ❌ | ❌ | ✅ | ❌ | 1 |
| semantic.js | ❌ | ❌ | ✅ | ❌ | 1 |
| measurements.js | ❌ | ❌ | ❌ | ✅ | 1 |
| health.js | ✅ | ❌ | ❌ | ❌ | 1 |

---

## Phase 6: Dependency Diagram

```
                           ┌──────────────┐
                           │  Page Layer  │
                           │  (38 pages)  │
                           └──────┬───────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
          ▼                       ▼                       ▼
   ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
   │   MapLibre   │       │   TerriaJS   │       │   Kepler    │
   │   (12)       │       │   (11)       │       │   (14)      │
   └──────┬───────┘       └──────┬───────┘       └──────┬───────┘
          │                       │                       │
          │    ┌──────────────────┴──────────────────┐    │
          │    │         Shared API Modules           │    │
          │    │   assets.js  sensors.js  events.js  │    │
          │    └────────────────────────────────────┘    │
          │                       │                       │
          └───────────────────────┼───────────────────────┘
                                  │
                                  ▼
                           ┌──────────────┐
                           │ Backend API  │
                           │ (178 routes) │
                           └──────────────┘
```

---

## Phase 7: Critical Path Analysis

### Critical Path 1: Asset Visualization

```
assets.js → Page → Viewer → Cesium/MapLibre
           │
           └── Required by: All pages
           └── Bottleneck: Single API module
```

### Critical Path 2: Sensor Data

```
sensors.js → Page → Viewer → All Viewers
             │
             └── Required by: All pages
             └── Bottleneck: Single API module
```

### Critical Path 3: Temporal Data

```
measurements.js → Page → KeplerViewer → Analytics
                 │
                 └── Required by: AnalyticsMapPage only
                 └── Bottleneck: Single viewer
```

---

## Phase 8: Dependency Summary

### Viewer Dependencies

| Viewer | Page Count | API Modules | Components | Critical |
|--------|-----------|-------------|------------|----------|
| MapLibre | 3 | 3 | 12 | YES |
| Cesium | 2 | 3 | 9 | YES |
| TerriaJS | 2 | 4 | 11 | MEDIUM |
| Kepler | 1 | 3 | 14 | MEDIUM |

### Bottleneck Analysis

| Bottleneck | Type | Risk |
|------------|------|------|
| assets.js | API Module | HIGH |
| sensors.js | API Module | HIGH |
| Cesium | Viewer | HIGH |
| SynchronizationManager | Component | MEDIUM |

---

## No Code Modifications Made

Per Task 080G constraints, **no code modifications were made**. This is an observation report only.

---

## Next Steps

- Proceed to Phase 5: Convergence Options
