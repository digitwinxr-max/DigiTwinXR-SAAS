# Stub Dependency Graph Report

**Generated:** 2026-06-21
**Repository:** DigiTwinXR-SAAS
**Branch:** feature/tasks-024-029-extensible-architecture
**Phase:** 2 - Method Dependency Analysis

---

## Executive Summary

This document traces dependencies for all stub methods to determine what would break if they were implemented. Evidence is derived from filesystem inspection only. **No code modifications were made.**

---

## Dependency Analysis Methodology

1. Search for imports of geospatial modules in services/routes
2. Search for direct usage in other files
3. Trace through __init__.py exports
4. Check test files for expected usage

---

## Phase 1: Import Chain Analysis

### geospatial/__init__.py Exports

```python
from .rasterio_adapter import RasterioAdapter, RasterWindow, RasterProfile
from .gdal_adapter import GDALAdapter, GDALDatasetInfo, GDALBandInfo
from .geopandas_adapter import GeoPandasAdapter, VectorDatasetInfo
from .spatial_analysis_engine import SpatialAnalysisEngine, NearestNeighborResult, BufferResult
```

### External Import Search Results

| Module | Imported By | Status |
|--------|-------------|--------|
| `SpatialAnalysisEngine` | None found | ⚠️ No external callers |
| `RasterioAdapter` | None found | ⚠️ No external callers |
| `GeoPandasAdapter` | None found | ⚠️ No external callers |
| `GDALAdapter` | None found | ⚠️ No external callers |

**Finding:** All geospatial adapters are **not imported** by any external service or route.

---

## Phase 2: Call Graph by Module

### 1. SpatialAnalysisEngine Dependencies

```
SpatialAnalysisEngine (stub)
├── buffer()
├── intersection()
├── union()
├── difference()
├── symmetric_difference()
├── clip()
├── erase()
├── update()
├── identify()
├── nearest_neighbor()
├── calculate_distance()
├── calculate_centroid()
├── calculate_boundary()
├── calculate_area()
├── calculate_length()
├── spatial_join()
└── aggregate_polygons()
```

**Who Calls This Module:**
- ❌ No services import this module
- ❌ No routes import this module
- ❌ No tests call these methods
- ❌ No frontend components use this

**Impact:** Zero current dependencies

---

### 2. RasterioAdapter Dependencies

```
RasterioAdapter (partial stub)
├── open() → PARTIAL (returns mock)
├── read_band() → CRITICAL (returns None)
├── read_multi_band() → CRITICAL (returns None)
├── write() → PARTIAL (returns True)
├── get_window() → SAFE (deterministic)
├── get_band_statistics() → PARTIAL (returns mock)
├── get_histogram() → PARTIAL (returns mock)
├── compute_checksum() → PARTIAL (hardcoded)
├── get_geotransform() → PARTIAL (returns mock)
└── reproject() → PARTIAL (returns True)
```

**Who Calls This Module:**
- ❌ No services import this module
- ❌ No routes import this module
- ❌ No tests call these methods

**Impact:** Zero current dependencies

---

### 3. GeoPandasAdapter Dependencies

```
GeoPandasAdapter (stub)
├── read_vector() → PARTIAL (returns mock)
├── spatial_join() → CRITICAL
├── buffer() → CRITICAL
├── dissolve() → CRITICAL
├── overlay() → CRITICAL
├── simplify() → CRITICAL
├── clip() → CRITICAL
├── get_centroid() → CRITICAL
├── get_boundary() → CRITICAL
├── get_convex_hull() → CRITICAL
├── calculate_area() → CRITICAL
├── calculate_length() → CRITICAL
└── get_supported_formats() → SAFE
```

**Who Calls This Module:**
- ❌ No services import this module
- ❌ No routes import this module
- ❌ No tests call these methods

**Impact:** Zero current dependencies

---

### 4. GDALAdapter Dependencies

```
GDALAdapter (partial stub)
├── open_dataset() → PARTIAL
├── get_band_info() → PARTIAL
├── read_band() → CRITICAL
├── convert_format() → PARTIAL
├── extract_metadata() → PARTIAL
├── build_overviews() → PARTIAL
└── get_supported_formats() → SAFE
```

**Who Calls This Module:**
- ❌ No services import this module
- ❌ No routes import this module
- ❌ No tests call these methods

**Impact:** Zero current dependencies

---

## Phase 3: Route Dependencies

### Search: Routes Using Geospatial

```bash
grep -rn "geospatial\|spatial_analysis\|rasterio\|geopandas\|gdal" backend/src/routes/
```

**Result:** No routes import or use geospatial modules

### Route Chain for Geospatial Operations

```
┌─────────────────────────────────────────────────────────────┐
│                        ROUTES                               │
│                     (178 routes)                             │
└───────────────────────┬───────────────────────────────────┘
                        │
                        │ No geospatial imports
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                     SERVICES                                 │
│                      (50 services)                          │
└───────────────────────┬───────────────────────────────────┘
                        │
                        │ No geospatial imports
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   GEOSPATIAL MODULES                        │
│  SpatialAnalysisEngine  │  RasterioAdapter  │  GeoPandas  │
│         ❌              │        ❌         │      ❌      │
│     No callers          │     No callers    │   No callers │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 4: Frontend Dependencies

### Search: Frontend Using Geospatial

```bash
grep -rn "spatial_analysis\|rasterio\|geopandas\|gdal" frontend/src/
```

**Result:** No frontend components import geospatial modules

### Frontend Map Viewers Status

| Viewer | Status | Backend Dependency |
|--------|--------|-------------------|
| MapLibreViewer | ⚠️ Placeholder | None |
| GlobeViewer (Cesium) | ✅ Implemented | None |
| TerriaViewer | ⚠️ Placeholder | None |
| KeplerViewer | ⚠️ Placeholder | None |

---

## Phase 5: Test Dependencies

### Search: Tests Using Geospatial

```bash
grep -rn "SpatialAnalysisEngine\|RasterioAdapter\|GeoPandasAdapter\|GDALAdapter" backend/tests/
```

**Result:** No test files call these adapters

### Geospatial Test Coverage

| Test File | Tests Adapter? |
|-----------|----------------|
| test_geospatial.py | ❌ No calls to stubs |

---

## Phase 6: Integration Dependencies

### GeoServer Integration

| Component | Status | Dependency |
|-----------|--------|------------|
| GeoServer tables | ✅ Migration exists | None |
| GeoServer service | ❌ Missing | None |
| GeoServer routes | ❌ Missing | None |

### Database Integration

| Component | Status | Dependency |
|-----------|--------|------------|
| geospatial_tables migration | ✅ Exists | None |
| GeoServer tables | ✅ Exists | None |

---

## Dependency Graph Summary

### Current State

```
┌─────────────────────────────────────────────────────────────────┐
│                     DEPENDENCY GRAPH                              │
│                                                                 │
│   ROUTES ──X──► SERVICES ──X──► GEOSPATIAL ADAPTERS             │
│                  (178)          │                               │
│                                   │                               │
│                    ┌──────────────┼──────────────┐               │
│                    │              │              │               │
│                    ▼              ▼              ▼               │
│           SpatialAnalysis    RasterioAdapter  GeoPandas          │
│                 17               11              13               │
│               STUBS             PARTIAL         STUBS             │
│                                                                 │
│   LEGEND: ──X── = No import path found                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Why No Dependencies?

1. **Adapters are isolated** - No services import them
2. **No routes expose geospatial** - No endpoints use the adapters
3. **No tests exercise them** - test_geospatial.py doesn't call stubs
4. **Frontend is independent** - Map viewers don't call backend adapters

---

## Risk Assessment

### Current Risk: ZERO (No Dependencies)

| Stub Group | Current Risk | Reason |
|------------|--------------|--------|
| SpatialAnalysisEngine | 🟢 ZERO | No callers |
| RasterioAdapter | 🟢 ZERO | No callers |
| GeoPandasAdapter | 🟢 ZERO | No callers |
| GDALAdapter | 🟢 ZERO | No callers |

### Future Risk: HIGH (If Implemented Without Architecture)

| Scenario | Risk | Mitigation |
|----------|------|-----------|
| Implement then discover circular deps | HIGH | Design first |
| Implement with wrong interface | HIGH | Define schemas first |
| Implement without migration | HIGH | Add migrations first |

---

## Implementation Considerations

### Safe to Implement Because:

1. ✅ No existing callers to break
2. ✅ No route dependencies
3. ✅ No service dependencies
4. ✅ No test dependencies
5. ✅ Clean slate for design

### Considerations Before Implementation:

1. **Define API contract first** - What should these adapters return?
2. **Add schemas** - Define response models
3. **Add migrations** - If database tables needed
4. **Add tests** - Before implementation
5. **Plan integration points** - Which routes will call these?

---

## Recommendations

### Immediate Actions (After Decision)

1. **If implementing:** Start with clean architecture design
2. **If abstracting:** Document the abstraction layer interface
3. **If deprecating:** Mark for removal in future version

### Long-term Architecture

```
RECOMMENDED DEPENDENCY STRUCTURE:

routes/ ──► services/ ──► geospatial/
                          ├── adapters/  (interfaces)
                          ├── implementations/
                          │   ├── rasterio_impl.py
                          │   ├── geopandas_impl.py
                          │   └── gdal_impl.py
                          └── spatial_engine/
```

---

## No Code Modifications Made

Per Task 080F constraints, **no code modifications were made**. This is an observation report only.

---

## Next Steps

- Proceed to Phase 3: Implementation Readiness
