# DigiTwinXR-SAAS Master Inventory

**Version:** 1.0.0
**Generated:** 2026-06-21
**Repository:** DigiTwinXR-SAAS

---

## Table of Contents

1. [Migrations](#1-migrations)
2. [Architecture Decision Records (ADRs)](#2-architecture-decision-records-adrs)
3. [Backend Models](#3-backend-models)
4. [Backend Services](#4-backend-services)
5. [API Routes](#5-api-routes)
6. [Request/Response Schemas](#6-requestresponse-schemas)
7. [Frontend Pages](#7-frontend-pages)
8. [Frontend Components](#8-frontend-components)
9. [API Endpoints Summary](#9-api-endpoints-summary)
10. [Test Suite](#10-test-suite)
11. [Dependencies](#11-dependencies)

---

## 1. Migrations

**Location:** `GCDTP/database/migrations/`
**Total:** 47 migration files

| # | Migration File | Purpose |
|---|---------------|---------|
| 001 | `001_create_asset_table.sql` | Core asset table |
| 002 | `002_create_sensors_table.sql` | Sensor definitions |
| 003 | `003_create_measurements_table.sql` | Time-series measurements |
| 004 | `004_timescale_hypertable_migration.sql` | TimescaleDB hypertable |
| 005 | `005_create_threshold_rules.sql` | Alert thresholds |
| 006 | `006_create_events.sql` | Event logging |
| 007 | `007_create_asset_health.sql` | Health scoring |
| 008 | `008_create_asset_relationships.sql` | Asset relationships |
| 009 | `009_create_propagated_events.sql` | Cascading failures |
| 010 | `010_create_asset_health_dependencies.sql` | Health dependencies |
| 011 | `011_create_simulation_tables.sql` | Scenario simulations |
| 012 | `012_create_recovery_simulations.sql` | Recovery planning |
| 013 | `013_create_resilience_analysis.sql` | Resilience metrics |
| 014 | `014_create_work_orders.sql` | Work order management |
| 015 | `015_create_documents.sql` | Document storage |
| 016 | `016_create_identity_tables.sql` | User identities |
| 017 | `017_create_workflow_tables.sql` | Workflow definitions |
| 018 | `018_create_mqtt_tables.sql` | MQTT message logging |
| 019 | `019_create_geoserver_tables.sql` | GeoServer integration |
| 020 | `020_create_graph_projection_tables.sql` | Graph projections |
| 021 | `021_create_ontology_tables.sql` | Semantic ontology |
| 022 | `022_create_observability_tables.sql` | Observability data |
| 023 | `023_create_performance_tables.sql` | Performance metrics |
| 024 | `024_create_devops_tables.sql` | DevOps tracking |
| 025 | `025_create_platform_tables.sql` | Platform configuration |
| 026 | `026_create_storage_tables.sql` | Object storage metadata |
| 027 | `027_create_geospatial_tables.sql` | Geospatial data |
| 038 | `038_create_semantic_layer.sql` | Semantic entities |
| 039 | `039_create_timeline_snapshots.sql` | Timeline snapshots |
| 040 | `040_create_logbook_tables.sql` | Digital logbook |
| 041 | `041_create_knowledge_repository.sql` | Knowledge base |
| 042 | `042_create_copilot_sessions.sql` | Copilot sessions |
| 043 | `043_create_rag_cache.sql` | RAG context cache |
| 044 | `044_create_agent_framework.sql` | Agent definitions |
| 045 | `045_create_predictive_maintenance.sql` | Predictive models |
| 046 | `046_create_root_cause_analysis.sql` | Root cause tracking |
| 047 | `047_create_cognitive_twin.sql` | Cognitive twin data |

---

## 2. Architecture Decision Records (ADRs)

**Location:** `GCDTP/adr/`
**Total:** 55 ADR files

| ID | Title | Domain |
|----|-------|--------|
| 0001 | Use Architecture Decision Records | Meta |
| 0002 | Use Service-Oriented Folder Structure | Architecture |
| 0003 | Use Docker for Development Environment | DevOps |
| 0004 | Asset-Centric Architecture | Core |
| 0005 | PostGIS Spatial Assets | Geospatial |
| 0006 | Leaflet Map Viewer | Visualization |
| 0007 | Sensor Engine | IoT |
| 0008 | Measurement Engine | IoT |
| 0009 | Timescale Hypertable Foundation | Database |
| 0010 | Threshold Engine | Alerting |
| 0011 | Event Engine | Events |
| 0013 | Health Engine | Health |
| 0014 | GeoPortal Operational Intelligence | Visualization |
| 0015 | System-Wide Event Propagation Hardening | Resilience |
| 0016 | Asset Relationship Graph Engine | Graph |
| 0017 | Cascading Failure Engine | Resilience |
| 0018 | Dependency-Aware Health | Health |
| 0019 | Scenario Simulation Engine | Simulation |
| 0020 | Recovery Simulation Engine | Simulation |
| 0021 | Resilience Analysis Engine | Resilience |
| 0022 | Network Topology Engine | Topology |
| 0023 | Routing Flow Resilience Engines | Routing |
| 0024 | Extensible Simulation Architecture | Simulation |
| 0025 | Operational Timeline Engine | Timeline |
| 0026 | Work Order Engine | Operations |
| 0027 | Document Management Engine | Documents |
| 0028 | Identity Access Management | Security |
| 0029 | Cesium 3D Visualization | Visualization |
| 0030 | Node-RED Integration | Integration |
| 0031 | EMQX MQTT Integration | IoT |
| 0032 | GeoServer Integration | Geospatial |
| 0033 | Graph Intelligence Layer | Graph |
| 0034 | Semantic Ontology Layer | Semantic |
| 0035 | Architecture Review and Hardening | Architecture |
| 0036 | Observability and Diagnostics Layer | Observability |
| 0037 | Performance and Scaling Layer | Performance |
| 0038 | Deployment and DevOps Layer | DevOps |
| 0039 | Enterprise Packaging Layer | Packaging |
| 0040 | Production Readiness Audit | Operations |
| 0041 | Object Storage Layer | Storage |
| 0042 | Advanced Geospatial Analytics Layer | Geospatial |
| 0043 | TerriaJS Federation Layer | Visualization |
| 0044 | MapLibre Vector Tile Layer | Visualization |
| 0045 | Kepler Analytics Layer | Visualization |
| 0046 | Unified Semantic Layer | Semantic |
| 0047 | Timeline Replay Engine | Timeline |
| 0048 | Digital Logbook Engine | Operations |
| 0049 | Knowledge Repository Engine | Knowledge |
| 0050 | Cognitive Copilot Foundation | AI |
| 0051 | RAG Engine | AI |
| 0052 | Agent Framework | AI |
| 0053 | Predictive Maintenance | AI |
| 0054 | Root Cause Analysis Engine | Analysis |
| 0055 | Cognitive Twin Engine | AI |

---

## 3. Backend Models

**Location:** `GCDTP/backend/src/models/`
**Total:** 39 model files

### Core Domain Models

| Model | File | Description |
|-------|------|-------------|
| Asset | `asset.py` | Core asset representation |
| Sensor | `sensor.py` | Sensor definitions |
| Measurement | `measurement.py` | Time-series data points |
| Event | `event.py` | System events |
| Threshold | `threshold.py` | Alert threshold rules |
| Health | `health.py` | Health scoring data |
| AssetRelationship | `asset_relationship.py` | Asset connections |
| AssetHealthDependency | `asset_health_dependency.py` | Health dependencies |

### Simulation Models

| Model | File | Description |
|-------|------|-------------|
| Scenario | `scenario.py` | What-if scenarios |
| ScenarioResult | `scenario_result.py` | Simulation outcomes |
| RecoverySimulation | `recovery_simulation.py` | Recovery planning |
| RecoveryResult | `recovery_result.py` | Recovery outcomes |

### Analysis Models

| Model | File | Description |
|-------|------|-------------|
| ResilienceAnalysis | `resilience_analysis.py` | Resilience metrics |
| ResilienceRecommendation | `resilience_recommendation.py` | Improvement suggestions |
| RootCauseAnalysis | `root_cause_analysis.py` | RCA results |
| CauseChain | `cause_chain.py` | Failure chain |
| CauseFactor | `cause_factor.py` | Contributing factors |

### Semantic & Knowledge Models

| Model | File | Description |
|-------|------|-------------|
| SemanticEntity | `semantic_entity.py` | Semantic entities |
| SemanticRelationship | `semantic_relationship.py` | Entity relationships |
| SemanticTag | `semantic_tag.py` | Entity tags |
| KnowledgeDocument | `knowledge_document.py` | Knowledge base docs |
| KnowledgeReference | `knowledge_reference.py` | Document references |

### Timeline & Operations Models

| Model | File | Description |
|-------|------|-------------|
| TimelineSnapshot | `timeline_snapshot.py` | Point-in-time state |
| LogbookEntry | `logbook_entry.py` | Operator notes |
| MaintenanceHistory | `maintenance_history.py` | Maintenance records |
| MaintenancePrediction | `maintenance_prediction.py` | Predicted failures |
| PropagatedEvent | `propagated_event.py` | Cascading events |

### AI & Copilot Models

| Model | File | Description |
|-------|------|-------------|
| CognitiveSession | `cognitive_session.py` | AI conversation session |
| CognitiveQuery | `cognitive_query.py` | AI query data |
| CognitiveContext | `cognitive_context.py` | Context for AI |
| CopilotSession | `copilot_session.py` | Copilot session |
| CopilotMessage | `copilot_message.py` | Copilot messages |
| RAGQuery | `rag_query.py` | RAG query log |
| RAGContextChunk | `rag_context_chunk.py` | Retrieved context |
| RAGAnswer | `rag_answer.py` | Generated answers |

### Agent Models

| Model | File | Description |
|-------|------|-------------|
| AgentDefinition | `agent_definition.py` | Agent type definitions |
| AgentAction | `agent_action.py` | Agent actions |
| AgentTask | `agent_task.py` | Agent tasks |

---

## 4. Backend Services

**Location:** `GCDTP/backend/src/services/`
**Total:** 47 service files

### Core Services

| Service | File | Domain |
|---------|------|--------|
| AssetService | `asset_service.py` | Assets |
| SensorService | `sensor_service.py` | Sensors |
| MeasurementService | `measurement_service.py` | Measurements |
| EventService | `event_service.py` | Events |
| ThresholdService | `threshold_service.py` | Thresholds |
| HealthService | `health_service.py` | Health |

### Relationship & Topology Services

| Service | File | Domain |
|---------|------|--------|
| AssetRelationshipService | `asset_relationship_service.py` | Relationships |
| TopologyEngine | `topology_engine.py` | Network topology |
| TopologyTypes | `topology_types.py` | Topology models |
| TopologyValidator | `topology_validator.py` | Topology validation |
| GraphBuilder | `graph_builder.py` | Graph construction |

### Simulation Services

| Service | File | Domain |
|---------|------|--------|
| SimulationService | `simulation_service.py` | Scenario simulation |
| RecoverySimulationService | `recovery_simulation_service.py` | Recovery planning |
| RoutingEngine | `routing_engine.py` | Routing flow |
| RoutingTypes | `routing_types.py` | Routing models |
| FlowEngine | `flow_engine.py` | Flow analysis |
| FlowModels | `flow_models.py` | Flow models |

### Resilience & Analysis Services

| Service | File | Domain |
|---------|------|--------|
| ResilienceService | `resilience_service.py` | Resilience metrics |
| ResilienceEngine | `resilience_engine.py` | Resilience analysis |
| FailurePropagationService | `failure_propagation_service.py` | Failure cascade |
| RootCauseService | `root_cause_service.py` | RCA |
| DependencyHealthService | `dependency_health_service.py` | Health dependencies |

### Timeline & Document Services

| Service | File | Domain |
|---------|------|--------|
| TimelineService | `timeline_service.py` | Timeline ops |
| TimelineEngine | `timeline_engine.py` | Timeline core |
| TimelineQueryEngine | `timeline_query_engine.py` | Timeline queries |
| TimelineValidator | `timeline_validator.py` | Timeline validation |
| TimelineTypes | `timeline_types.py` | Timeline models |
| SnapshotManager | `snapshot_manager.py` | Snapshot management |
| ReplayEngine | `replay_engine.py` | Timeline replay |
| DiffEngine | `diff_engine.py` | State diffs |
| EventRecorder | `event_recorder.py` | Event recording |

### Document Services

| Service | File | Domain |
|---------|------|--------|
| DocumentEngine | `document_engine.py` | Document management |
| DocumentIndexer | `document_indexer.py` | Document indexing |
| DocumentValidator | `document_validator.py` | Document validation |
| DocumentTypes | `document_types.py` | Document models |
| AttachmentManager | `attachment_manager.py` | File attachments |

### Knowledge & Semantic Services

| Service | File | Domain |
|---------|------|--------|
| KnowledgeService | `knowledge_service.py` | Knowledge base |
| SemanticService | `semantic_service.py` | Semantic layer |
| LogbookService | `logbook_service.py` | Digital logbook |

### Work Order Services

| Service | File | Domain |
|---------|------|--------|
| WorkOrderEngine | `work_order_engine.py` | Work order management |
| WorkOrderValidator | `work_order_validator.py` | Validation |
| WorkOrderTypes | `work_order_types.py` | Work order models |
| MaintenanceEngine | `maintenance_engine.py` | Maintenance planning |
| InspectionEngine | `inspection_engine.py` | Inspections |

### AI & Copilot Services

| Service | File | Domain |
|---------|------|--------|
| RAGService | `rag_service.py` | RAG operations |
| CognitiveTwinService | `cognitive_twin_service.py` | Cognitive twin |
| CopilotService | `copilot_service.py` | Copilot interface |
| AgentService | `agent_service.py` | Agent execution |
| PredictiveMaintenanceService | `predictive_maintenance_service.py` | Predictions |

### Cost Models

| Service | File | Domain |
|---------|------|--------|
| CostModels | `cost_models.py` | Cost calculations |

---

## 5. API Routes

**Location:** `GCDTP/backend/src/routes/`
**Total:** 22 route files

| Route File | Router Prefix | Description |
|------------|---------------|-------------|
| `agent_routes.py` | `/agents` | Agent framework endpoints |
| `asset_routes.py` | `/assets` | Asset CRUD operations |
| `asset_relationship_routes.py` | `/relationships` | Asset relationships |
| `cognitive_routes.py` | `/cognitive` | Cognitive twin AI |
| `copilot_routes.py` | `/copilot` | Copilot sessions |
| `event_routes.py` | `/events` | Event management |
| `health_routes.py` | `/health` | Health metrics |
| `knowledge_routes.py` | `/knowledge` | Knowledge repository |
| `logbook_routes.py` | `/logbook` | Digital logbook |
| `measurement_routes.py` | `/measurements` | Sensor measurements |
| `network_health_routes.py` | `/network` | Network health |
| `predictive_routes.py` | `/predictive` | Predictive maintenance |
| `propagation_routes.py` | `/propagation` | Failure propagation |
| `rag_routes.py` | `/rag` | RAG engine |
| `recovery_routes.py` | `/recovery` | Recovery simulations |
| `resilience_routes.py` | `/resilience` | Resilience analysis |
| `root_cause_routes.py` | `/root-cause` | Root cause analysis |
| `scenario_routes.py` | `/scenarios` | Scenario simulations |
| `semantic_routes.py` | `/semantic` | Semantic layer |
| `sensor_routes.py` | `/sensors` | Sensor management |
| `threshold_routes.py` | `/thresholds` | Threshold rules |
| `timeline_routes.py` | `/timeline` | Timeline operations |

---

## 6. Request/Response Schemas

**Location:** `GCDTP/backend/src/schemas/`
**Total:** 22 schema files

| Schema | File | Description |
|--------|------|-------------|
| Asset | `asset.py` | Asset request/response |
| Sensor | `sensor.py` | Sensor schemas |
| Measurement | `measurement.py` | Measurement schemas |
| Event | `event.py` | Event schemas |
| Threshold | `threshold.py` | Threshold schemas |
| Health | `health.py` | Health schemas |
| AssetHealthDependency | `asset_health_dependency.py` | Dependency schemas |
| AssetRelationship | `asset_relationship.py` | Relationship schemas |
| PropagatedEvent | `propagated_event.py` | Cascading event schemas |
| Scenario | `scenario.py` | Scenario schemas |
| Recovery | `recovery.py` | Recovery schemas |
| Resilience | `resilience.py` | Resilience schemas |
| RootCause | `root_cause.py` | RCA schemas |
| Semantic | `semantic.py` | Semantic layer schemas |
| Knowledge | `knowledge.py` | Knowledge schemas |
| Logbook | `logbook.py` | Logbook schemas |
| Timeline | `timeline.py` | Timeline schemas |
| RAG | `rag.py` | RAG schemas |
| Cognitive | `cognitive.py` | Cognitive schemas |
| Copilot | `copilot.py` | Copilot schemas |
| Agent | `agent.py` | Agent schemas |
| PredictiveMaintenance | `predictive_maintenance.py` | Prediction schemas |

---

## 7. Frontend Pages

**Location:** `GCDTP/frontend/src/pages/`
**Total:** 43 page files

### Asset Management Pages

| Page | File | Test |
|------|------|------|
| AssetList | `AssetList.jsx` | ❌ |
| AssetDetails | `AssetDetails.jsx` | ❌ |
| AssetHierarchy | `AssetHierarchy.jsx` | ✅ |
| CreateAsset | `CreateAsset.jsx` | ❌ |

### Sensor Pages

| Page | File | Test |
|------|------|------|
| SensorList | `SensorList.jsx` | ❌ |
| SensorDetails | `SensorDetails.jsx` | ❌ |
| SensorMeasurements | `SensorMeasurements.jsx` | ❌ |
| SensorThresholds | `SensorThresholds.jsx` | ❌ |
| CreateSensor | `CreateSensor.jsx` | ❌ |
| Measurements | `Measurements.jsx` | ❌ |
| MeasurementDetails | `MeasurementDetails.jsx` | ❌ |

### Event Pages

| Page | File | Test |
|------|------|------|
| EventList | `EventList.jsx` | ❌ |
| EventDetails | `EventDetails.jsx` | ❌ |
| ActiveEvents | `ActiveEvents.jsx` | ❌ |

### Threshold Pages

| Page | File | Test |
|------|------|------|
| ThresholdList | `ThresholdList.jsx` | ❌ |
| CreateThreshold | `CreateThreshold.jsx` | ❌ |

### Health & Analytics Pages

| Page | File | Test |
|------|------|------|
| HealthDashboard | `HealthDashboard.jsx` | ❌ |
| NetworkHealth | `NetworkHealth.jsx` | ✅ |
| ResilienceDashboard | `ResilienceDashboard.jsx` | ❌ |
| RootCauseAnalysis | `RootCauseAnalysis.jsx` | ❌ |
| ImpactChain | `ImpactChain.jsx` | ✅ |
| PredictiveMaintenance | `PredictiveMaintenance.jsx` | ❌ |

### Simulation Pages

| Page | File | Test |
|------|------|------|
| ScenarioStudio | `ScenarioStudio.jsx` | ✅ |
| RecoveryStudio | `RecoveryStudio.jsx` | ✅ |

### Operations Pages

| Page | File | Test |
|------|------|------|
| DigitalLogbook | `DigitalLogbook.jsx` | ❌ |
| TimelineReplay | `TimelineReplay.jsx` | ❌ |

### Knowledge & AI Pages

| Page | File | Test |
|------|------|------|
| SemanticExplorer | `SemanticExplorer.jsx` | ❌ |
| KnowledgeRepository | `KnowledgeRepository.jsx` | ❌ |
| RAGWorkbench | `RAGWorkbench.jsx` | ❌ |
| CognitiveTwin | `CognitiveTwin.jsx` | ❌ |
| CognitiveCopilot | `CognitiveCopilot.jsx` | ❌ |
| AgentWorkbench | `AgentWorkbench.jsx` | ❌ |

### Map & Visualization Pages

| Page | File | Test |
|------|------|------|
| Map | `Map.jsx` | ❌ |
| GeoPortal | `GeoPortal.jsx` | ❌ |
| DigitalTwin3DPage | `DigitalTwin3DPage.tsx` | ❌ |
| TerriaPortalPage | `TerriaPortalPage.tsx` | ❌ |
| VectorMapPage | `VectorMapPage.tsx` | ❌ |
| AnalyticsMapPage | `AnalyticsMapPage.tsx` | ❌ |

---

## 8. Frontend Components

### MapLibre Components
**Location:** `GCDTP/frontend/src/maplibre/`
**Count:** 10

| Component | File | Purpose |
|-----------|------|---------|
| MapLibreViewer | `MapLibreViewer.tsx` | Main map viewer |
| MapLibreContext | `MapLibreContext.tsx` | React context |
| LayerManager | `LayerManager.tsx` | Layer operations |
| CameraController | `CameraController.tsx` | Camera control |
| OfflineMapManager | `OfflineMapManager.tsx` | Offline support |
| TileCacheManager | `TileCacheManager.tsx` | Tile caching |
| PMTilesManager | `PMTilesManager.tsx` | PMTiles support |
| VectorTileManager | `VectorTileManager.tsx` | Vector tiles |
| StyleManager | `StyleManager.tsx` | Map styling |
| SynchronizationManager | `SynchronizationManager.tsx` | Sync with other viewers |

### Cesium Components
**Location:** `GCDTP/frontend/src/cesium/`
**Count:** 8

| Component | File | Purpose |
|-----------|------|---------|
| GlobeViewer | `GlobeViewer.tsx` | 3D globe viewer |
| CesiumContext | `CesiumContext.tsx` | React context |
| TilesetLoader | `TilesetLoader.tsx` | 3D tiles loading |
| TerrainManager | `TerrainManager.tsx` | Terrain data |
| CameraController | `CameraController.tsx` | 3D camera control |
| Asset3DLayer | `Asset3DLayer.tsx` | 3D asset layers |
| SceneController | `SceneController.tsx` | Scene management |
| TimelineController | `TimelineController.tsx` | Timeline sync |

### TerriaJS Components
**Location:** `GCDTP/frontend/src/terria/`
**Count:** 9

| Component | File | Purpose |
|-----------|------|---------|
| TerriaViewer | `TerriaViewer.tsx` | Main viewer |
| TerriaContext | `TerriaContext.tsx` | React context |
| CatalogManager | `CatalogManager.tsx` | Data catalog |
| FederationManager | `FederationManager.tsx` | Service federation |
| LayerCatalog | `LayerCatalog.tsx` | Layer management |
| MetadataExplorer | `MetadataExplorer.tsx` | Metadata display |
| ShareManager | `ShareManager.tsx` | Share functionality |
| StoryMapManager | `StoryMapManager.tsx` | Story maps |
| TimelineLayerManager | `TimelineLayerManager.tsx` | Timeline sync |

### Kepler.gl Components
**Location:** `GCDTP/frontend/src/kepler/`
**Count:** 13

| Component | File | Purpose |
|-----------|------|---------|
| KeplerViewer | `KeplerViewer.tsx` | Main viewer |
| KeplerContext | `KeplerContext.tsx` | React context |
| DatasetManager | `DatasetManager.tsx` | Data management |
| AggregationManager | `AggregationManager.tsx` | Aggregation |
| AnalyticsLayerManager | `AnalyticsLayerManager.tsx` | Analytics layers |
| ClusterManager | `ClusterManager.tsx` | Clustering |
| FilterManager | `FilterManager.tsx` | Data filtering |
| FlowMapManager | `FlowMapManager.tsx` | Flow visualization |
| HeatmapManager | `HeatmapManager.tsx` | Heatmaps |
| SynchronizationManager | `SynchronizationManager.tsx` | Sync |
| TemporalDatasetManager | `TemporalDatasetManager.tsx` | Temporal data |
| TrajectoryManager | `TrajectoryManager.tsx` | Trajectories |

---

## 9. API Endpoints Summary

### Endpoint Statistics

| Method | Count |
|--------|-------|
| GET | ~100 |
| POST | ~60 |
| PUT | ~10 |
| PATCH | ~2 |
| DELETE | ~15 |

### Key API Groups

| Group | Base Path | Operations |
|-------|-----------|------------|
| Assets | `/assets` | CRUD, relationships, health |
| Sensors | `/sensors` | CRUD, measurements, thresholds |
| Measurements | `/measurements` | CRUD, history |
| Events | `/events` | CRUD, propagation, root cause |
| Thresholds | `/thresholds` | CRUD |
| Health | `/health` | Health scores, contributors |
| Network | `/network` | Network health, topology |
| Resilience | `/resilience` | Analysis, recommendations |
| Scenarios | `/scenarios` | CRUD, simulation |
| Recovery | `/recovery` | CRUD, simulation |
| Timeline | `/timeline` | Snapshots, playback, range |
| Logbook | `/logbook` | CRUD, search, summaries |
| Semantic | `/semantic` | Entities, relationships, tags |
| Knowledge | `/knowledge` | Documents, search |
| RAG | `/rag` | Query, history, sources |
| Cognitive | `/cognitive` | Query, context |
| Copilot | `/copilot` | Sessions, messages |
| Agents | `/agents` | Definitions, tasks, actions |

---

## 10. Test Suite

### Backend Tests
**Location:** `GCDTP/backend/tests/`
**Count:** 38 test files

| Test File | Domain |
|-----------|--------|
| `test_assets.py` | Asset management |
| `test_sensors.py` | Sensor operations |
| `test_measurements.py` | Time-series data |
| `test_events.py` | Event handling |
| `test_thresholds.py` | Alerting |
| `test_health.py` | Health engine |
| `test_asset_relationships.py` | Relationships |
| `test_topology.py` | Network topology |
| `test_simulation_engine.py` | Scenarios |
| `test_recovery_simulation.py` | Recovery |
| `test_resilience.py` | Resilience |
| `test_failure_propagation.py` | Cascading failures |
| `test_timeline.py` | Timeline |
| `test_timeline_engine.py` | Timeline engine |
| `test_logbook_engine.py` | Digital logbook |
| `test_documents.py` | Document management |
| `test_knowledge_repository.py` | Knowledge base |
| `test_semantic_layer.py` | Semantic layer |
| `test_ontology.py` | Ontology |
| `test_rag_engine.py` | RAG |
| `test_copilot_foundation.py` | Copilot |
| `test_agent_framework.py` | Agent framework |
| `test_cognitive_twin.py` | Cognitive twin |
| `test_predictive_maintenance.py` | Predictions |
| `test_root_cause_analysis.py` | RCA |
| `test_routing.py` | Routing |
| `test_platform.py` | Platform |
| `test_storage.py` | Storage |
| `test_geoserver.py` | GeoServer |
| `test_geospatial.py` | Geospatial |
| `test_node_red.py` | Node-RED |
| `test_emqx.py` | EMQX/MQTT |
| `test_event_system.py` | Events |
| `test_security.py` | Security |
| `test_observability.py` | Observability |
| `test_performance.py` | Performance |
| `test_timescale_performance.py` | TimescaleDB |
| `test_dependency_health.py` | Health deps |
| `test_devops.py` | DevOps |
| `test_recovery_simulation.py` | Recovery |

### Frontend Tests
**Location:** `GCDTP/frontend/tests/`
**Count:** 6 test files

| Test | Location |
|------|----------|
| `MapLibre.test.tsx` | `test_maplibre/` |
| `AssetHierarchy.test.jsx` | `pages/` |
| `NetworkHealth.test.jsx` | `pages/` |
| `ImpactChain.test.jsx` | `pages/` |
| `RecoveryStudio.test.jsx` | `pages/` |
| `ScenarioStudio.test.jsx` | `pages/` |

### Integration Tests
**Location:** `GCDTP/tests/integration/`
- `placeholder.test.js` (placeholder file)

### E2E Tests
**Location:** `GCDTP/tests/e2e/`
- `placeholder.test.js` (placeholder file)

### Test Fixtures
**Location:** `GCDTP/backend/tests/`
- `conftest.py` - Shared pytest fixtures

---

## 11. Dependencies

### Backend Dependencies
**File:** `GCDTP/backend/requirements.txt`

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.109.0 | Web framework |
| uvicorn[standard] | 0.27.0 | ASGI server |
| sqlalchemy | 2.0.25 | ORM |
| psycopg2-binary | 2.9.9 | PostgreSQL driver |
| geoalchemy2 | 0.14.3 | GeoAlchemy |
| pydantic | 2.5.3 | Data validation |
| python-dotenv | 1.0.0 | Environment vars |
| pytest | 7.4.4 | Testing |
| pytest-asyncio | 0.23.3 | Async testing |
| httpx | 0.26.0 | HTTP client |

### Frontend Dependencies
**File:** `GCDTP/frontend/package.json`

| Package | Version | Purpose |
|---------|---------|---------|
| react | ^18.2.0 | UI framework |
| react-dom | ^18.2.0 | DOM rendering |
| react-router-dom | ^6.21.0 | Routing |
| leaflet | ^1.9.4 | 2D maps |
| react-leaflet | ^4.2.1 | Leaflet React |
| recharts | ^2.10.0 | Charts |

### Frontend Dev Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| @vitejs/plugin-react | ^4.2.1 | Vite React |
| vite | ^5.0.10 | Build tool |
| vitest | ^1.2.0 | Testing |
| @testing-library/react | ^14.1.0 | React testing |

---

## Document Index

| Document | Location |
|----------|-----------|
| Master Inventory | `GCDTP/architecture/master_inventory.md` |
| Dependency Graph | `GCDTP/architecture/dependency_graph.md` |
| Route Graph | `GCDTP/architecture/route_graph.md` |
| Component Graph | `GCDTP/architecture/component_graph.md` |
| Integration Graph | `GCDTP/architecture/integration_graph.md` |
| Sanitation Report | `REPOSITORY_SANITATION_REPORT.md` |
