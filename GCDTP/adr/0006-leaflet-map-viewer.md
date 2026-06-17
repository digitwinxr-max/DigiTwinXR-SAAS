# ADR-0006: Leaflet Map Viewer

## Status

Accepted

## Context

GCDTP assets contain geographic coordinates. The system needs a way to visualize assets on a map for operational awareness and spatial understanding.

## Decision

We will implement a simple Leaflet-based map viewer for asset visualization:

1. **Map Library**: Use React-Leaflet for React integration
2. **Base Map**: OpenStreetMap tiles (free, no API key required)
3. **Asset Display**: Circle markers with popups
4. **Data Source**: Load from `/assets/geojson` endpoint
5. **Default View**: Center on Botswana at zoom level 6

## Implementation

### Component Structure

```
frontend/src/
├── components/
│   └── MapView/
│       ├── MapView.jsx    # Main map component
│       └── index.js       # Export
└── pages/
    └── Map.jsx            # Map page wrapper
```

### MapView Component

```jsx
<MapContainer center={[-22.3285, 24.6849]} zoom={6}>
  <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
  {/* Circle markers from GeoJSON */}
</MapContainer>
```

### Popup Content

Each marker displays:
- Asset name
- Asset type
- Status
- Coordinates (latitude, longitude)

### Data Flow

```
/assets/geojson → MapView → CircleMarker + Popup
```

## Decision Made By

GCDTP Core Team

## Date

2026-06-16

## Consequences

### Positive
- Simple, lightweight map implementation
- No API keys required (OpenStreetMap)
- GeoJSON integration with existing API
- Popup provides all asset details
- Responsive map fills available space

### Negative
- Limited to point markers (no lines/polygons)
- No offline support
- Relies on OpenStreetMap availability

### Neutral
- Map is visualization-only (no editing)
- No clustering for dense areas
- Standard zoom/pan controls

## Future Considerations

- Clustering for dense asset areas
- Asset filtering by type/status
- Multiple basemap options
- Custom marker icons
- Heat map visualization
