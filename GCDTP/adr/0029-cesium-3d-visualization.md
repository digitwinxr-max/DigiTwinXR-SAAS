# ADR-0029: Cesium 3D Visualization Layer

## Status

Accepted

## Context

GCDTP currently uses Leaflet for 2D map visualization. We need to add 3D capabilities for:

- Asset visualization in 3D space
- Terrain visualization
- Simulation overlays
- Timeline replay in 3D
- Route and topology visualization

### The Decision

Introduce Cesium as a **second** visualization layer while **preserving** Leaflet 2D.

```
┌─────────────────────────────────────────────────────────────────┐
│                     DUAL-VIEW ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐          ┌─────────────────┐              │
│  │   LEAFLET 2D    │   ←→     │    CESIUM 3D    │              │
│  │                 │  SWITCH  │                 │              │
│  │   - 2D Maps     │          │   - 3D Globe    │              │
│  │   - Overlays    │          │   - Terrain     │              │
│  │   - Markers     │          │   - Entities    │              │
│  │   - Polylines   │          │   - 3D Models   │              │
│  └─────────────────┘          └─────────────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Decision

Create Cesium 3D Visualization Layer:

```
frontend/src/cesium/
├── CesiumContext.tsx         # React context for viewer management
├── GlobeViewer.tsx           # Main 3D globe component
├── Asset3DLayer.tsx          # 3D asset visualization
├── TilesetLoader.tsx         # 3D tiles loading
├── TerrainManager.tsx        # Terrain management
├── SceneController.tsx       # Scene state management
├── CameraController.tsx      # Camera controls
├── TimelineController.tsx    # Timeline integration
└── __init__.ts               # Module exports
```

## Architecture

### Dual-View Pattern

Both views share the same backend data:

```typescript
// Common data interface
interface DigitalTwinData {
  assets: Asset[];
  sensors: Sensor[];
  topology: Topology;
  routes: Route[];
  events: TimelineEvent[];
}
```

### Cesium Context

Manages Cesium viewer lifecycle:

```typescript
interface CesiumState {
  viewer: CesiumViewer | null;
  isInitialized: boolean;
  timeline: TimelineState;
  selectedEntity: CesiumEntity | null;
}
```

## Supported Layers

### Layer Types

| Layer | Description | Status |
|-------|-------------|--------|
| Assets | Point/billboard/model assets | ✅ |
| Sensors | Sensor readings overlay | ✅ |
| Events | Event visualization | ✅ |
| Health | Health indicator bars | ✅ |
| Work Orders | Work order locations | ✅ |
| Documents | Document markers | ✅ |
| Topology | Network connections | ✅ |
| Routes | Route paths | ✅ |
| Simulation | Simulation overlays | ✅ |
| Timeline | Replay path | ✅ |

## Capabilities

### 3D Globe

- Cesium World Terrain
- Ellipsoid (flat mode)
- Custom terrain providers
- Atmospheric rendering
- Fog effects

### Asset Visualization

- Point markers with status colors
- Billboard labels
- Health bars (3D extrusion)
- Model loading (GLB/B3DM)
- Selection highlighting

### Camera Controls

- Zoom in/out
- Fly-to animations
- Focus on asset
- Follow route
- Preset positions (NA, EU, AS, AU)
- Keyboard navigation

### Timeline Integration (ADR-0025)

- Play/pause
- Seek to time
- Speed control (0.25x - 100x)
- Event markers
- Step forward/backward

## Future-Ready

### Prepared But Not Implemented

| Feature | Purpose | Implementation |
|---------|---------|----------------|
| 3D Tiles | Streaming large models | Cesium.create3DTileset() |
| BIM/IFC | Building models | GLB format |
| Photogrammetry | Reality capture | 3D Tiles |
| Point Clouds | LiDAR data | PNTS format |
| CZML | Temporal animation | Cesium.CzmlDataSource |

## Database Schema

No database changes required. Cesium visualization is purely frontend.

## EventBus Integration

Timeline events (ADR-0025) are visualized on 3D globe:

- Asset status changes
- Route changes
- Simulation snapshots
- Replay positions

## Consequences

### Positive

1. **Enhanced visualization** - 3D assets and terrain
2. **Dual-view** - Users choose 2D or 3D
3. **Timeline replay** - Visualize history in 3D
4. **Simulation** - Overlay results on globe
5. **Future-ready** - Prepared for BIM/point clouds

### Negative

1. **Dependency** - Cesium library added
2. **Performance** - 3D rendering more intensive
3. **Complexity** - Two visualization systems

### Neutral

1. **Leaflet preserved** - Existing 2D view unchanged
2. **Additive only** - No existing features removed
3. **Backend unchanged** - No backend modifications

## Acceptance Criteria

- [x] CesiumContext for viewer management
- [x] GlobeViewer component
- [x] Asset3DLayer with status colors
- [x] TilesetLoader for 3D models
- [x] TerrainManager with terrain options
- [x] SceneController for layer management
- [x] CameraController with presets
- [x] TimelineController (ADR-0025 integration)
- [x] DigitalTwin3DPage
- [x] ViewSwitcher (2D/3D toggle)
- [x] 40+ tests
- [x] ADR documentation
