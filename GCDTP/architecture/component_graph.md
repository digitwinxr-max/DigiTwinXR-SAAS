# DigiTwinXR-SAAS Component Graph

**Version:** 1.0.0
**Generated:** 2026-06-21

---

## React Application Structure

```
GCDTP-Frontend
├── App.jsx (Root Component)
├── main.jsx (Entry Point)
├── pages/ (Route Pages)
├── components/ (Shared Components)
├── contexts/ (React Contexts)
├── hooks/ (Custom Hooks)
├── services/ (API Services)
├── utils/ (Utilities)
├── maplibre/ (MapLibre Components)
├── cesium/ (Cesium Components)
├── terria/ (TerriaJS Components)
└── kepler/ (Kepler.gl Components)
```

---

## Root Component Hierarchy

```
App.jsx
└── React Router
    ├── Layout (Sidebar, Header, Footer)
    │   ├── Sidebar Navigation
    │   │   ├── Asset Management
    │   │   ├── Sensors
    │   │   ├── Events
    │   │   ├── Health
    │   │   ├── Simulations
    │   │   ├── Operations
    │   │   ├── AI & Knowledge
    │   │   └── Maps & Visualization
    │   └── Main Content Area
    └── Route Pages
```

---

## Page Hierarchy

```
Pages
├── Asset Management
│   ├── AssetList
│   ├── AssetDetails
│   ├── AssetHierarchy
│   └── CreateAsset
│
├── Sensor Management
│   ├── SensorList
│   ├── SensorDetails
│   ├── SensorMeasurements
│   ├── SensorThresholds
│   ├── CreateSensor
│   ├── Measurements
│   └── MeasurementDetails
│
├── Event Management
│   ├── EventList
│   ├── EventDetails
│   └── ActiveEvents
│
├── Threshold Management
│   ├── ThresholdList
│   └── CreateThreshold
│
├── Health & Analytics
│   ├── HealthDashboard
│   ├── NetworkHealth
│   ├── ResilienceDashboard
│   ├── RootCauseAnalysis
│   ├── ImpactChain
│   └── PredictiveMaintenance
│
├── Simulations
│   ├── ScenarioStudio
│   └── RecoveryStudio
│
├── Operations
│   ├── DigitalLogbook
│   └── TimelineReplay
│
├── AI & Knowledge
│   ├── SemanticExplorer
│   ├── KnowledgeRepository
│   ├── RAGWorkbench
│   ├── CognitiveTwin
│   ├── CognitiveCopilot
│   └── AgentWorkbench
│
└── Maps & Visualization
    ├── Map
    ├── GeoPortal
    ├── DigitalTwin3DPage
    ├── TerriaPortalPage
    ├── VectorMapPage
    └── AnalyticsMapPage
```

---

## Shared Components Structure

### Layout Components

```
Layout
├── Header
│   ├── Logo
│   ├── SearchBar
│   ├── Notifications
│   └── UserMenu
├── Sidebar
│   ├── NavigationMenu
│   ├── QuickLinks
│   └── CollapseToggle
└── MainContent
```

### Common UI Components

```
Common Components
├── Button
│   ├── PrimaryButton
│   ├── SecondaryButton
│   ├── IconButton
│   └── ButtonGroup
├── Form
│   ├── Input
│   ├── Select
│   ├── Checkbox
│   ├── Radio
│   ├── DatePicker
│   └── TextArea
├── Table
│   ├── DataTable
│   ├── SortableTable
│   └── Pagination
├── Card
│   ├── StatCard
│   ├── InfoCard
│   └── ActionCard
├── Modal
│   ├── ConfirmModal
│   └── FormModal
├── Alert
│   ├── SuccessAlert
│   ├── ErrorAlert
│   ├── WarningAlert
│   └── InfoAlert
└── Loading
    ├── Spinner
    ├── Skeleton
    └── ProgressBar
```

### Chart Components

```
Charts
├── LineChart
├── BarChart
├── PieChart
├── AreaChart
├── ScatterPlot
├── Heatmap
├── NetworkGraph
└── TimelineChart
```

---

## MapLibre Components

**Location:** `src/maplibre/`

```
MapLibre Module
├── MapLibreViewer (Main)
│   └── MapLibreContext (Provider)
│
├── Layer Management
│   ├── LayerManager
│   ├── VectorTileManager
│   ├── StyleManager
│   └── TileCacheManager
│
├── Map Controls
│   ├── CameraController
│   ├── SynchronizationManager
│   └── OfflineMapManager
│
└── Specialized Managers
    └── PMTilesManager
```

### MapLibre Component Details

| Component | Purpose | Dependencies |
|-----------|---------|--------------|
| MapLibreViewer | Main map container | MapLibre GL JS |
| MapLibreContext | State management | React Context |
| LayerManager | Layer lifecycle | MapLibreContext |
| VectorTileManager | Vector tile handling | LayerManager |
| StyleManager | Map styling | MapLibreContext |
| TileCacheManager | Offline tile cache | LayerManager |
| CameraController | View controls | MapLibreContext |
| SynchronizationManager | Cross-viewer sync | MapLibreContext |
| OfflineMapManager | Offline functionality | TileCacheManager |
| PMTilesManager | PMTiles support | LayerManager |

### MapLibre Data Flow

```
┌─────────────────┐
│   Data Source   │
│ (API, GeoJSON)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LayerManager   │
│  - Add layers   │
│  - Update styles│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ VectorTileManager│
│ - Fetch tiles   │
│ - Parse MVT     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  StyleManager   │
│ - Apply styles  │
│ - Update colors │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ MapLibreViewer  │
│ - Render map    │
│ - Handle events │
└─────────────────┘
```

---

## Cesium Components

**Location:** `src/cesium/`

```
Cesium Module
├── GlobeViewer (Main)
│   └── CesiumContext (Provider)
│
├── 3D Data Loading
│   ├── TilesetLoader
│   ├── TerrainManager
│   └── Asset3DLayer
│
├── Map Controls
│   ├── CameraController
│   ├── SceneController
│   └── TimelineController
│
└── Context Management
    └── CesiumContext
```

### Cesium Component Details

| Component | Purpose | Dependencies |
|-----------|---------|--------------|
| GlobeViewer | Main 3D globe | Cesium JS |
| CesiumContext | State management | React Context |
| TilesetLoader | Load 3D tiles | CesiumContext |
| TerrainManager | Terrain data | CesiumContext |
| Asset3DLayer | 3D asset overlay | TilesetLoader |
| CameraController | 3D camera | CesiumContext |
| SceneController | Scene settings | CesiumContext |
| TimelineController | Timeline sync | CesiumContext |

### Cesium Data Flow

```
┌─────────────────┐
│   3D Tileset    │
│   (GLB, GLTF)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  TilesetLoader  │
│ - Load tileset  │
│ - Handle errors │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Asset3DLayer   │
│ - Position      │
│ - Style         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GlobeViewer    │
│ - 3D rendering  │
│ - Picking       │
└─────────────────┘
```

---

## TerriaJS Components

**Location:** `src/terria/`

```
TerriaJS Module
├── TerriaViewer (Main)
│   └── TerriaContext (Provider)
│
├── Catalog Management
│   ├── CatalogManager
│   ├── LayerCatalog
│   └── MetadataExplorer
│
├── Federation
│   └── FederationManager
│
├── Sharing
│   └── ShareManager
│
├── Storytelling
│   └── StoryMapManager
│
└── Timeline
    └── TimelineLayerManager
```

### TerriaJS Component Details

| Component | Purpose | Dependencies |
|-----------|---------|--------------|
| TerriaViewer | Main viewer | Terria JS |
| TerriaContext | State management | React Context |
| CatalogManager | Data catalog | TerriaContext |
| FederationManager | Service federation | CatalogManager |
| LayerCatalog | Layer browser | CatalogManager |
| MetadataExplorer | Metadata display | CatalogManager |
| ShareManager | Share functionality | TerriaContext |
| StoryMapManager | Story maps | TerriaContext |
| TimelineLayerManager | Timeline sync | TerriaContext |

---

## Kepler.gl Components

**Location:** `src/kepler/`

```
Kepler.gl Module
├── KeplerViewer (Main)
│   └── KeplerContext (Provider)
│
├── Data Management
│   ├── DatasetManager
│   ├── TemporalDatasetManager
│   └── FilterManager
│
├── Visualization
│   ├── AggregationManager
│   ├── AnalyticsLayerManager
│   ├── ClusterManager
│   ├── FlowMapManager
│   ├── HeatmapManager
│   └── TrajectoryManager
│
├── Sync
│   └── SynchronizationManager
│
└── Context
    └── KeplerContext
```

### Kepler.gl Component Details

| Component | Purpose | Dependencies |
|-----------|---------|--------------|
| KeplerViewer | Main viewer | Kepler.gl |
| KeplerContext | State management | React Context |
| DatasetManager | Dataset loading | KeplerContext |
| TemporalDatasetManager | Time-based data | DatasetManager |
| FilterManager | Data filtering | KeplerContext |
| AggregationManager | Aggregations | KeplerContext |
| AnalyticsLayerManager | Analytics layers | KeplerContext |
| ClusterManager | Clustering | KeplerContext |
| FlowMapManager | Flow visualization | KeplerContext |
| HeatmapManager | Heatmaps | KeplerContext |
| TrajectoryManager | Trajectories | KeplerContext |
| SynchronizationManager | Cross-sync | KeplerContext |

---

## Context Providers

```
Context Providers
├── MapLibreContext
│   └── Provides map instance and state
│
├── CesiumContext
│   └── Provides globe instance and state
│
├── TerriaContext
│   └── Provides Terria instance and catalog
│
├── KeplerContext
│   └── Provides Kepler instance and datasets
│
├── AuthContext
│   └── User authentication state
│
└── ThemeContext
    └── UI theme (light/dark mode)
```

---

## Custom Hooks

### Map Hooks

```
useMapLibre()
├── Returns map instance
├── Controls camera
└── Manages layers

useCesium()
├── Returns globe instance
├── Controls camera
└── Manages entities

useKepler()
├── Returns Kepler instance
├── Manages datasets
└── Controls visualization
```

### Data Hooks

```
useAssets()
├── Fetches asset list
├── Provides CRUD operations
└── Caches results

useSensors()
├── Fetches sensor data
├── Manages sensor state
└── Handles thresholds

useEvents()
├── Subscribes to events
├── Filters by type
└── Manages event state

useHealth()
├── Fetches health metrics
├── Calculates scores
└── Provides history

useTimeline()
├── Fetches snapshots
├── Manages playback
└── Handles range queries
```

### AI Hooks

```
useRAG()
├── Queries RAG engine
├── Manages context
└── Handles sources

useCognitive()
├── Manages sessions
├── Sends queries
└── Handles responses

useCopilot()
├── Manages sessions
├── Streams responses
└── Handles history
```

---

## API Services

```
services/
├── api.js (Base API client)
├── assets.js
├── sensors.js
├── events.js
├── measurements.js
├── health.js
├── timeline.js
├── logbook.js
├── semantic.js
├── rag.js
├── cognitive.js
├── copilot.js
├── agents.js
└── simulations.js
```

### Service Layer Architecture

```
Component
    │
    ▼ (Hook)
Service
    │
    ▼ (HTTP)
API Gateway
    │
    ▼
Backend Routes
    │
    ▼
Services
    │
    ▼
Models
    │
    ▼
Database
```

---

## Cross-Component Communication

### Viewer Synchronization

```
┌────────────────┐     ┌────────────────┐
│  MapLibreViewer │◄───►│  CesiumViewer   │
│  (2D map)      │     │  (3D globe)    │
└───────┬────────┘     └───────┬────────┘
        │                      │
        │   Synchronization    │
        │        Manager        │
        │                      │
        └──────────┬───────────┘
                   │
                   ▼
         ┌──────────────────┐
         │   KeplerViewer   │
         │  (Analytics)     │
         └──────────────────┘
```

### State Management Pattern

```
Component A ──► Context Provider ──► Component B
                 │
                 ▼
           ┌─────────┐
           │  Store  │
           └─────────┘
                 │
                 ▼
           Component C
```

---

## Page-to-Component Mapping

### Asset Hierarchy Page

```
AssetHierarchy.jsx
├── AssetTree
│   ├── TreeNode
│   └── TreeControls
├── AssetDetailsPanel
│   ├── AssetInfo
│   ├── SensorSummary
│   └── HealthIndicator
└── AssetMap (optional)
    └── MapLibreViewer
```

### Health Dashboard

```
HealthDashboard.jsx
├── HealthSummary
│   ├── OverallHealthScore
│   ├── HealthTrend
│   └── CriticalAssets
├── HealthMap
│   └── MapLibreViewer / CesiumViewer
├── AssetHealthTable
│   ├── HealthCell
│   └── HealthChart
└── HealthTimeline
    └── TimelineChart
```

### Scenario Studio

```
ScenarioStudio.jsx
├── ScenarioList
│   ├── ScenarioCard
│   └── ScenarioFilters
├── ScenarioEditor
│   ├── ScenarioForm
│   ├── EventSelector
│   └── ConditionBuilder
├── ScenarioMap
│   ├── MapLibreViewer
│   └── CesiumViewer
└── ScenarioResults
    ├── ResultsChart
    └── ComparisonTable
```

### Cognitive Copilot

```
CognitiveCopilot.jsx
├── ChatInterface
│   ├── MessageList
│   │   ├── UserMessage
│   │   └── AIResponse
│   └── ChatInput
├── ContextPanel
│   ├── EntityInfo
│   ├── RelatedAssets
│   └── KnowledgeSources
└── ActionPanel
    ├── SuggestedActions
    └── QuickCommands
```

---

## Component Dependency Tree

```
App
├── Layout
│   ├── Header
│   │   ├── SearchBar
│   │   ├── Notifications
│   │   └── UserMenu
│   └── Sidebar
│       └── NavigationMenu
├── Pages
│   ├── AssetHierarchy
│   │   ├── AssetTree
│   │   ├── AssetDetailsPanel
│   │   └── AssetMap (MapLibreViewer)
│   ├── HealthDashboard
│   │   ├── HealthSummary
│   │   ├── HealthMap
│   │   │   └── MapLibreViewer
│   │   ├── AssetHealthTable
│   │   └── HealthTimeline
│   ├── DigitalTwin3DPage
│   │   └── CesiumViewer
│   │       ├── TilesetLoader
│   │       ├── TerrainManager
│   │       └── CameraController
│   ├── ScenarioStudio
│   │   ├── ScenarioList
│   │   ├── ScenarioEditor
│   │   ├── ScenarioMap
│   │   │   └── CesiumViewer
│   │   └── ScenarioResults
│   ├── RAGWorkbench
│   │   ├── QueryInput
│   │   ├── ContextViewer
│   │   └── SourcesList
│   └── CognitiveCopilot
│       ├── ChatInterface
│       ├── ContextPanel
│       └── ActionPanel
└── Modals
    ├── CreateAssetModal
    ├── CreateSensorModal
    └── ConfirmModal
```

---

## Performance Considerations

### Code Splitting

```
Routes with Lazy Loading
├── HealthDashboard (lazy)
├── ScenarioStudio (lazy)
├── DigitalTwin3DPage (lazy)
│   └── Cesium (heavy)
├── TerriaPortalPage (lazy)
│   └── TerriaJS (heavy)
└── AnalyticsMapPage (lazy)
    └── Kepler.gl (heavy)
```

### State Management

```
Local State (useState)
├── Form inputs
├── UI toggles
└── Simple flags

Context State
├── User session
├── Theme
├── Map instances
└── Selected entities

Server State (React Query/SWR)
├── Asset lists
├── Sensor data
├── Health metrics
└── Event streams
```

---

## Testing Strategy

### Component Tests

```
Unit Tests
├── Button.test.jsx
├── Input.test.jsx
├── Table.test.jsx
└── Modal.test.jsx

Integration Tests
├── AssetHierarchy.test.jsx
├── HealthDashboard.test.jsx
└── CognitiveCopilot.test.jsx

E2E Tests (Playwright)
├── AssetCreation.flow.js
├── HealthVisualization.flow.js
└── AIQuery.flow.js
```
