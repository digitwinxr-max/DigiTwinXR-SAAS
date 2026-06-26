# Viewer Duplication Report

**Generated:** 2026-06-21
**Repository:** DigiTwinXR-SAAS
**Branch:** feature/tasks-024-029-extensible-architecture
**Phase:** 3 - Duplication Analysis

---

## Executive Summary

This document identifies overlapping capabilities and duplication across map viewers. Evidence is derived from filesystem inspection only. **No code modifications were made.**

---

## Classification System

| Level | Description | Action Required |
|-------|-------------|----------------|
| **LOW** | Minimal overlap, different implementations | Monitor |
| **MEDIUM** | Some overlap, potential consolidation | Consider |
| **HIGH** | Significant overlap, wasted effort | Consolidate |

---

## Phase 1: Page Duplication

### Map-Related Pages

| Page | File | Primary Viewer | Duplicates? |
|------|------|---------------|-------------|
| Map | `Map.jsx` | MapLibre | None |
| VectorMapPage | `VectorMapPage.tsx` | MapLibre | Similar to Map.jsx |
| GeoPortal | `GeoPortal.jsx` | MapLibre + TerriaJS | Combines 2 viewers |
| DigitalTwin3DPage | `DigitalTwin3DPage.tsx` | Cesium | None |
| TerriaPortalPage | `TerriaPortalPage.tsx` | TerriaJS | None |
| AnalyticsMapPage | `AnalyticsMapPage.tsx` | Kepler | None |

### Page Duplication Analysis

| Duplicate Type | Pages | Severity | Action |
|---------------|-------|----------|--------|
| Map vs VectorMapPage | 2 | LOW | Consolidate to single page |
| GeoPortal | 2 | MEDIUM | Consolidate viewers |
| Others | - | NONE | No duplication |

**Finding:** `Map.jsx` and `VectorMapPage.tsx` appear to serve similar purposes.

---

## Phase 2: Panel Duplication

### Control Panels

| Panel Type | MapLibre | Cesium | TerriaJS | Kepler | Severity |
|-----------|----------|--------|----------|--------|----------|
| Camera Controls | ✅ | ✅ | ❌ | ❌ | LOW |
| Layer Controls | ✅ | ✅ | ✅ | ✅ | HIGH |
| Legend | ✅ | ✅ | ✅ | ❌ | LOW |
| Timeline Controls | ❌ | ✅ | ✅ | ✅ | MEDIUM |
| Zoom Controls | ✅ | ✅ | ✅ | ✅ | HIGH |
| Scale Controls | ✅ | ✅ | ❌ | ❌ | LOW |

### Control Panel Analysis

| Duplicate Type | Count | Severity | Action |
|---------------|-------|----------|--------|
| Layer Controls | 4 | HIGH | Standardize |
| Timeline Controls | 3 | MEDIUM | Share implementation |
| Zoom Controls | 4 | HIGH | Standardize |
| Camera Controls | 2 | LOW | Keep separate |

**Finding:** Layer and zoom controls are duplicated across all 4 viewers.

---

## Phase 3: Placeholder Duplication

### Placeholder Status

| Viewer | Status | Placeholder Elements |
|--------|--------|---------------------|
| MapLibre | ⚠️ Placeholder | 1 div |
| Cesium | ✅ Implemented | 0 div |
| TerriaJS | ⚠️ Placeholder | 3 divs |
| Kepler | ⚠️ Placeholder | 1 div |

### Placeholder Element Analysis

| File | Element | Count | Severity |
|------|---------|-------|----------|
| MapLibreViewer.tsx | `map-placeholder` | 1 | LOW |
| TerriaViewer.tsx | `leaflet-placeholder` | 1 | MEDIUM |
| TerriaViewer.tsx | `cesium-placeholder` | 1 | MEDIUM |
| TerriaViewer.tsx | `terria-placeholder` | 1 | MEDIUM |
| KeplerViewer.tsx | `kepler-placeholder` | 1 | LOW |

**Finding:** TerriaJS has 3 placeholders (Leaflet, Cesium, Terria) because it supports all 3.

---

## Phase 4: Component Duplication

### Synchronization Components

| Component | MapLibre | Kepler | Severity |
|-----------|----------|--------|----------|
| SynchronizationManager | ✅ | ✅ | HIGH |

### Controller Components

| Component | MapLibre | Cesium | Severity |
|-----------|----------|--------|----------|
| CameraController | ✅ | ✅ | LOW |

### Manager Components

| Manager | Count | Duplicates | Severity |
|---------|-------|-----------|----------|
| LayerManager | 1 | MapLibre | NONE |
| LayerCatalog | 1 | TerriaJS | NONE |
| AnalyticsLayerManager | 1 | Kepler | NONE |
| TilesetLoader | 1 | Cesium | NONE |

### Component Duplication Summary

| Type | Count | Severity |
|------|-------|----------|
| SynchronizationManager | 2 | HIGH |
| CameraController | 2 | LOW |

**Finding:** `SynchronizationManager` is duplicated between MapLibre and Kepler.

---

## Phase 5: Context Provider Duplication

### Context Providers

| Context | MapLibre | Cesium | TerriaJS | Kepler |
|---------|----------|--------|----------|--------|
| Context Provider | ✅ | ✅ | ✅ | ✅ |
| Store Type | MapLibre | Cesium | Terria | Kepler |
| State Shape | Different | Different | Different | Different |

**Finding:** All viewers have unique context providers - no duplication.

---

## Phase 6: API Module Duplication

### API Module Usage by Viewer

| API Module | MapLibre | Cesium | TerriaJS | Kepler |
|-----------|----------|--------|----------|--------|
| assets.js | ✅ | ✅ | ✅ | ✅ |
| sensors.js | ✅ | ✅ | ✅ | ✅ |
| events.js | ✅ | ❌ | ❌ | ✅ |
| measurements.js | ❌ | ❌ | ❌ | ✅ |
| knowledge.js | ❌ | ❌ | ✅ | ❌ |
| semantic.js | ❌ | ❌ | ✅ | ❌ |
| timeline.js | ❌ | ✅ | ❌ | ❌ |
| health.js | ✅ | ❌ | ❌ | ❌ |

### API Overlap Analysis

| API Module | Viewers | Severity |
|-----------|---------|----------|
| assets.js | 4 | HIGH (shared) |
| sensors.js | 4 | HIGH (shared) |
| events.js | 2 | MEDIUM |
| measurements.js | 1 | NONE |
| knowledge.js | 1 | NONE |
| semantic.js | 1 | NONE |
| timeline.js | 1 | NONE |
| health.js | 1 | NONE |

**Finding:** `assets.js` and `sensors.js` are heavily shared - good.

---

## Phase 7: Feature Duplication

### Feature Matrix

| Feature | MapLibre | Cesium | TerriaJS | Kepler |
|---------|----------|--------|----------|--------|
| 2D Rendering | ✅ | ⚠️ Limited | ✅ | ⚠️ Limited |
| 3D Globe | ❌ | ✅ | ✅ (via Cesium) | ❌ |
| Vector Tiles | ✅ | ❌ | ✅ | ❌ |
| Raster Tiles | ✅ | ✅ | ✅ | ✅ |
| Terrain | ❌ | ✅ | ✅ (via Cesium) | ❌ |
| 3D Tiles | ❌ | ✅ | ✅ (via Cesium) | ❌ |
| Offline Maps | ✅ | ✅ | ❌ | ❌ |
| Layer Management | ✅ | ✅ | ✅ | ✅ |
| Time Animation | ⚠️ Limited | ✅ | ✅ | ✅ |
| Data Catalog | ❌ | ❌ | ✅ | ❌ |
| Multi-source | ❌ | ❌ | ✅ | ❌ |
| Heatmaps | ❌ | ❌ | ❌ | ✅ |
| Cluster Analysis | ❌ | ❌ | ❌ | ✅ |
| Flow Maps | ❌ | ❌ | ❌ | ✅ |
| Trajectory Viz | ❌ | ❌ | ❌ | ✅ |

### Feature Duplication Analysis

| Feature | Viewers | Severity | Action |
|---------|---------|----------|--------|
| 2D Rendering | 3 | MEDIUM | Keep separate |
| Raster Tiles | 4 | HIGH | Standardize |
| Layer Management | 4 | HIGH | Standardize |
| Time Animation | 3 | MEDIUM | Share timeline |

---

## Phase 8: Summary Matrix

### Duplication Summary by Type

| Type | Count | Severity | Action |
|------|-------|----------|--------|
| Pages | 2 | LOW | Consolidate |
| Panels | 2 | HIGH | Standardize |
| Placeholders | 4 | MEDIUM | Implement |
| Components | 1 | HIGH | Share |
| Context Providers | 0 | NONE | N/A |
| API Modules | 2 | HIGH | Standardize |
| Features | 3 | MEDIUM | Share |

### Overall Duplication Assessment

| Category | Duplication | Severity |
|----------|-------------|----------|
| Code | LOW | LOW |
| Features | MEDIUM | MEDIUM |
| Components | HIGH | HIGH |
| API Usage | HIGH | HIGH |

---

## Phase 9: Recommendations

### Immediate Actions

| Action | Priority | Reason |
|--------|----------|--------|
| Share SynchronizationManager | HIGH | Already duplicated |
| Standardize Layer controls | HIGH | All 4 viewers |
| Consolidate Map.jsx + VectorMapPage | MEDIUM | Similar purpose |

### Future Actions

| Action | Priority | Reason |
|--------|----------|--------|
| Implement MapLibre | HIGH | Placeholder only |
| Implement TerriaJS | MEDIUM | Federation unique |
| Implement Kepler | HIGH | Analytics unique |
| Share Timeline implementation | MEDIUM | In 3 viewers |

---

## No Code Modifications Made

Per Task 080G constraints, **no code modifications were made**. This is an observation report only.

---

## Next Steps

- Proceed to Phase 4: Component Dependency Graph
