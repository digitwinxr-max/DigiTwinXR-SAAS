# ADR-0032: GeoServer Integration Layer

## Status

Accepted

## Context

GCDTP needs spatial publishing capabilities for:
- Publishing map layers
- Serving geographic data
- OGC standard services
- Raster and vector data

### The Decision

Introduce GeoServer as a **spatial publishing layer** while **FastAPI remains authoritative** for business logic.

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTEGRATION ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  FastAPI              GeoServer              Clients               │
│  ┌─────────┐        ┌─────────┐        ┌─────────┐            │
│  │ Business │───────→│ Spatial │───────→│ Web Apps │            │
│  │ Logic    │        │ Publish │        │ GIS Tools│            │
│  └─────────┘        │ WMS/WFS │        └─────────┘            │
│                     │ WCS     │                                 │
│                     └─────────┘                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Decision

Create GeoServer Integration Layer:

```
backend/src/integrations/geoserver/
├── geoserver_client.py      # GeoServer REST API client
├── geoserver_types.py      # Core types
├── workspace_manager.py     # Workspace management
├── layer_manager.py        # Layer publishing
├── style_manager.py        # SLD style management
├── wms_adapter.py         # WMS adapter
├── wfs_adapter.py         # WFS adapter
├── wcs_adapter.py         # WCS adapter
├── geoserver_validator.py  # Validation
└── __init__.py
```

## Key Principle

**FastAPI remains authoritative for all business logic.**

GeoServer provides only:
- Layer publishing
- WMS/WFS/WCS services
- Style management
- Spatial interoperability

No business logic in GeoServer.

## Supported Services

| Service | Description | Status |
|---------|-------------|--------|
| WMS | Web Map Service | ✅ |
| WFS | Web Feature Service | ✅ |
| WCS | Web Coverage Service | ✅ |
| WMTS | Web Map Tile Service | ✅ |
| Layer Groups | Layer organization | ✅ |
| Raster Layers | GeoTIFF, etc. | ✅ |
| Vector Layers | Shapefile, PostGIS | ✅ |

## Database Schema

### geoserver_workspaces

```sql
CREATE TABLE geoserver_workspaces (
    id UUID PRIMARY KEY,
    name VARCHAR(100) UNIQUE,
    uri VARCHAR(500),
    is_default BOOLEAN
);
```

### published_layers

```sql
CREATE TABLE published_layers (
    id UUID PRIMARY KEY,
    workspace_id UUID,
    name VARCHAR(255),
    layer_type layer_type,
    title VARCHAR(255),
    srs VARCHAR(50),
    is_published BOOLEAN
);
```

## EventBus Integration

GeoServer events published to Timeline Engine:

- WORKSPACE_CREATED
- LAYER_PUBLISHED
- LAYER_UPDATED
- STYLE_ASSIGNED
- SERVICE_REGISTERED

## Consequences

### Positive

1. **Spatial publishing** - Publish map layers
2. **OGC standards** - WMS/WFS/WCS support
3. **Style management** - SLD styling
4. **Interoperability** - Standard protocols
5. **Scalable** - Tile caching

### Negative

1. **GeoServer dependency** - Requires deployment
2. **Data duplication** - Layers copied to GeoServer
3. **Complexity** - More infrastructure

### Neutral

1. **FastAPI authoritative** - No business logic changes
2. **Additive only** - Existing features unchanged
3. **Standard protocols** - Vendor-neutral

## Acceptance Criteria

- [x] GeoServer REST client
- [x] Workspace manager
- [x] Layer manager
- [x] Style manager
- [x] WMS adapter
- [x] WFS adapter
- [x] WCS adapter
- [x] Validator
- [x] All services supported
- [x] EventBus integration
- [x] Timeline integration
- [x] Database migration
- [x] 60+ tests
- [x] ADR documentation
