# Stub Completion Roadmap

**Generated:** 2026-06-21
**Repository:** DigiTwinXR-SAAS
**Branch:** feature/tasks-024-029-extensible-architecture
**Phase:** 6 - Execution Roadmap

---

## Executive Summary

This document provides a prioritized roadmap for implementing the geospatial stubs. Work is ordered by foundation first, lowest risk first, and dependency sequence. Evidence is derived from filesystem inspection only. **No code modifications were made.**

---

## Roadmap Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     STUB COMPLETION ROADMAP                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  PHASE 1: Foundation (Week 1-2)                                   │
│  ├── Add Python dependencies                                     │
│  ├── Add system dependencies                                     │
│  └── Create schema files                                        │
│                                                                  │
│  PHASE 2: Core Implementations (Week 3-6)                        │
│  ├── Trivial calculations (area, length)                         │
│  ├── Format utilities (supported_formats)                        │
│  └── Geometry operations (centroid, boundary)                    │
│                                                                  │
│  PHASE 3: Intermediate Implementations (Week 7-10)                │
│  ├── Buffer operations                                           │
│  ├── Overlay operations                                          │
│  └── Spatial joins                                              │
│                                                                  │
│  PHASE 4: Advanced Implementations (Week 11-14)                   │
│  ├── Raster I/O                                                 │
│  ├── GDAL operations                                            │
│  └── Coordinate transforms                                        │
│                                                                  │
│  PHASE 5: Integration & Testing (Week 15-16)                     │
│  ├── Add routes                                                 │
│  ├── Add tests                                                  │
│  └── Add frontend integration                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Foundation (Week 1-2)

**Objective:** Set up infrastructure for implementation

### 1.1 Add Python Dependencies

**File:** `backend/requirements.txt`

```diff
+ shapely>=2.0.0
+ geopandas>=0.13.0
+ rasterio>=1.3.0
+ fiona>=1.9.0
+ pyproj>=3.5.0
+ rtree>=1.0.0
+ numpy>=1.24.0
```

### 1.2 Add System Dependencies

```bash
# Ubuntu/Debian
apt-get update
apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    libspatialindex-dev \
    libshp-dev
```

### 1.3 Create Schema Files

```
backend/src/schemas/geospatial/
├── __init__.py
├── spatial_analysis.py
│   ├── BufferRequest
│   ├── BufferResponse
│   ├── IntersectionRequest
│   ├── IntersectionResponse
│   ├── SpatialJoinRequest
│   └── SpatialJoinResponse
├── raster.py
│   ├── RasterReadRequest
│   ├── RasterReadResponse
│   └── RasterStatsResponse
└── vector.py
    ├── VectorReadRequest
    └── VectorReadResponse
```

### Phase 1 Deliverables

| Task | Status | Notes |
|------|--------|-------|
| Add Python deps | ⏳ Pending | |
| Install system deps | ⏳ Pending | |
| Create schema directory | ⏳ Pending | |
| Define request schemas | ⏳ Pending | |
| Define response schemas | ⏳ Pending | |

---

## Phase 2: Core Implementations (Week 3-6)

**Objective:** Implement trivial, low-risk operations first

### 2.1 Trivial Calculations

| Method | File | Complexity | Risk | Week |
|--------|------|------------|------|------|
| `calculate_area()` | SpatialAnalysisEngine | Trivial | LOW | 3 |
| `calculate_length()` | SpatialAnalysisEngine | Trivial | LOW | 3 |
| `calculate_area()` | GeoPandasAdapter | Trivial | LOW | 3 |
| `calculate_length()` | GeoPandasAdapter | Trivial | LOW | 3 |
| `get_centroid()` | GeoPandasAdapter | Trivial | LOW | 4 |
| `get_boundary()` | GeoPandasAdapter | Trivial | LOW | 4 |
| `get_convex_hull()` | GeoPandasAdapter | Trivial | LOW | 4 |

**Implementation Example:**

```python
def calculate_area(self, layer_path: str) -> List[float]:
    """Calculate areas of geometries."""
    gdf = geopandas.read_file(layer_path)
    return gdf.geometry.area.tolist()
```

### 2.2 Format Utilities

| Method | File | Complexity | Risk | Week |
|--------|------|------------|------|------|
| `get_supported_formats()` | GeoPandasAdapter | Static | NONE | 5 |
| `get_supported_formats()` | GDALAdapter | Static | NONE | 5 |

**Implementation:** Already functional - return format lists.

### 2.3 Geometry Operations

| Method | File | Complexity | Risk | Week |
|--------|------|------------|------|------|
| `calculate_centroid()` | SpatialAnalysisEngine | Trivial | LOW | 6 |
| `calculate_boundary()` | SpatialAnalysisEngine | Trivial | LOW | 6 |

### Phase 2 Deliverables

| Task | Status | Methods |
|------|--------|---------|
| Implement area calculations | ⏳ Pending | 4 |
| Implement length calculations | ⏳ Pending | 4 |
| Implement geometry operations | ⏳ Pending | 5 |
| Add unit tests | ⏳ Pending | - |

---

## Phase 3: Intermediate Implementations (Week 7-10)

**Objective:** Implement core GIS operations

### 3.1 Buffer Operations

| Method | File | Complexity | Risk | Week |
|--------|------|------------|------|------|
| `buffer()` | SpatialAnalysisEngine | Medium | MEDIUM | 7 |
| `buffer()` | GeoPandasAdapter | Medium | MEDIUM | 7 |

**Implementation Example:**

```python
def buffer(
    self,
    layer_path: str,
    distance: float,
    resolution: int = 16
) -> Optional[GeoDataFrame]:
    """Create buffer around geometries."""
    gdf = geopandas.read_file(layer_path)
    buffered = gdf.geometry.buffer(distance, resolution=resolution)
    return geopandas.GeoDataFrame(geometry=buffered, crs=gdf.crs)
```

### 3.2 Overlay Operations

| Method | File | Complexity | Risk | Week |
|--------|------|------------|------|------|
| `intersection()` | SpatialAnalysisEngine | Medium | MEDIUM | 8 |
| `union()` | SpatialAnalysisEngine | Medium | MEDIUM | 8 |
| `difference()` | SpatialAnalysisEngine | Medium | MEDIUM | 8 |
| `symmetric_difference()` | SpatialAnalysisEngine | Medium | MEDIUM | 8 |
| `overlay()` | GeoPandasAdapter | Medium | MEDIUM | 8 |

### 3.3 Spatial Joins

| Method | File | Complexity | Risk | Week |
|--------|------|------------|------|------|
| `spatial_join()` | SpatialAnalysisEngine | Medium | MEDIUM | 9 |
| `spatial_join()` | GeoPandasAdapter | Medium | MEDIUM | 9 |

### 3.4 Additional Operations

| Method | File | Complexity | Risk | Week |
|--------|------|------------|------|------|
| `clip()` | SpatialAnalysisEngine | Medium | MEDIUM | 10 |
| `clip()` | GeoPandasAdapter | Medium | MEDIUM | 10 |
| `dissolve()` | GeoPandasAdapter | Medium | MEDIUM | 10 |
| `simplify()` | GeoPandasAdapter | Medium | MEDIUM | 10 |
| `erase()` | SpatialAnalysisEngine | Medium | MEDIUM | 10 |
| `update()` | SpatialAnalysisEngine | Medium | MEDIUM | 10 |

### Phase 3 Deliverables

| Task | Status | Methods |
|------|--------|---------|
| Implement buffer | ⏳ Pending | 2 |
| Implement overlay | ⏳ Pending | 5 |
| Implement spatial join | ⏳ Pending | 2 |
| Implement additional ops | ⏳ Pending | 5 |
| Add unit tests | ⏳ Pending | - |

---

## Phase 4: Advanced Implementations (Week 11-14)

**Objective:** Implement complex operations

### 4.1 Raster Operations

| Method | File | Complexity | Risk | Week |
|--------|------|------------|------|------|
| `read_band()` | RasterioAdapter | High | MEDIUM | 11 |
| `read_multi_band()` | RasterioAdapter | High | MEDIUM | 11 |
| `write()` | RasterioAdapter | High | MEDIUM | 12 |

**Implementation Example:**

```python
def read_band(
    self,
    file_path: str,
    band_index: int = 1,
    window: Optional[RasterWindow] = None
) -> Optional[np.ndarray]:
    """Read raster band data."""
    with rasterio.open(file_path) as dataset:
        if window:
            return dataset.read(band_index, window=window)
        return dataset.read(band_index)
```

### 4.2 GDAL Operations

| Method | File | Complexity | Risk | Week |
|--------|------|------------|------|------|
| `open_dataset()` | GDALAdapter | High | MEDIUM | 13 |
| `read_band()` | GDALAdapter | High | MEDIUM | 13 |
| `convert_format()` | GDALAdapter | High | MEDIUM | 13 |
| `build_overviews()` | GDALAdapter | High | MEDIUM | 14 |

### 4.3 Coordinate Transforms

| Method | File | Complexity | Risk | Week |
|--------|------|------------|------|------|
| `transform()` | CoordinateTransformEngine | High | MEDIUM | 14 |

### Phase 4 Deliverables

| Task | Status | Methods |
|------|--------|---------|
| Implement raster I/O | ⏳ Pending | 3 |
| Implement GDAL ops | ⏳ Pending | 4 |
| Implement transforms | ⏳ Pending | 1 |
| Add unit tests | ⏳ Pending | - |

---

## Phase 5: Integration & Testing (Week 15-16)

**Objective:** Connect stubs to routes and add tests

### 5.1 Add Routes

```
backend/src/routes/geospatial_routes.py

POST   /geospatial/buffer
POST   /geospatial/intersection
POST   /geospatial/union
POST   /geospatial/overlay
POST   /geospatial/spatial-join
GET    /geospatial/calculate-area
GET    /geospatial/calculate-length
POST   /raster/read-band
POST   /raster/write
POST   /raster/reproject
```

### 5.2 Add Tests

```python
backend/tests/test_spatial_analysis.py
backend/tests/test_raster_operations.py
backend/tests/test_geospatial_routes.py
```

### 5.3 Frontend Integration

| Page | Uses Stubs | Integration |
|------|-----------|-------------|
| VectorMapPage | SpatialAnalysisEngine | Load map with vector analysis |
| GeoPortal | RasterioAdapter | Load raster tiles |

### Phase 5 Deliverables

| Task | Status | Notes |
|------|--------|-------|
| Add geospatial routes | ⏳ Pending | 10 routes |
| Add integration tests | ⏳ Pending | 3 test files |
| Add frontend integration | ⏳ Pending | 2 pages |

---

## Implementation Priority Matrix

### By Foundation Dependency

| Priority | Adapter | Dependencies | Order |
|----------|---------|-------------|-------|
| 1 | GeoPandasAdapter.calculate_area | geopandas | First |
| 2 | GeoPandasAdapter.calculate_length | geopandas | First |
| 3 | SpatialAnalysisEngine.calculate_area | shapely | First |
| 4 | SpatialAnalysisEngine.calculate_length | shapely | First |
| 5 | GeoPandasAdapter.buffer | geopandas, shapely | Second |
| 6 | SpatialAnalysisEngine.buffer | shapely | Second |
| 7 | GeoPandasAdapter.overlay | geopandas | Third |
| 8 | SpatialAnalysisEngine.intersection | shapely | Third |
| 9 | RasterioAdapter.read_band | rasterio, numpy | Fourth |
| 10 | GDALAdapter | gdal | Fifth |

### By Risk Level

| Risk | Methods | Approach |
|------|---------|----------|
| LOW | 7 | Implement first, minimal testing |
| MEDIUM | 28 | Implement with full testing |
| HIGH | 12 | Implement with integration tests |

---

## Summary Timeline

| Phase | Duration | Methods | Stub Methods |
|-------|----------|---------|-------------|
| 1: Foundation | 2 weeks | Infrastructure | 0 |
| 2: Core | 4 weeks | 14 | 14 |
| 3: Intermediate | 4 weeks | 14 | 14 |
| 4: Advanced | 4 weeks | 8 | 8 |
| 5: Integration | 2 weeks | Routes + Tests | 0 |
| **Total** | **16 weeks** | **44** | **36** |

---

## Quick Start Guide

### Day 1 Actions

1. **Add dependencies to requirements.txt**
2. **Install system libraries**
3. **Create schema directory structure**
4. **Define first request/response schemas**

### Week 1 Goal

Implement `calculate_area()` and `calculate_length()` in both SpatialAnalysisEngine and GeoPandasAdapter.

### Success Criteria

- [ ] Dependencies installed
- [ ] Schema files created
- [ ] Unit tests passing for trivial methods
- [ ] No regressions in existing code

---

## No Code Modifications Made

Per Task 080F constraints, **no code modifications were made**. This is an observation report only.

---

## Document Index

All stub elimination reports are located in `GCDTP/docs/stabilization/`:

| Document | Phase |
|----------|-------|
| stub_inventory_detailed.md | 1 |
| stub_dependency_graph.md | 2 |
| implementation_readiness.md | 3 |
| adapter_architecture.md | 4 |
| stub_risk_matrix.md | 5 |
| stub_completion_roadmap.md | 6 |
