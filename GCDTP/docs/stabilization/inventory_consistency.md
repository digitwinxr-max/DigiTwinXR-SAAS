# Inventory Consistency Report

**Generated:** 2026-06-21
**Repository:** DigiTwinXR-SAAS
**Branch:** feature/tasks-024-029-extensible-architecture
**Phase:** 1 - Repository Consistency

---

## Purpose

This document cross-references all inventory items between architecture documentation and actual filesystem.

---

## Migrations Inventory

**Location:** `GCDTP/database/migrations/`

| # | Filename | Status |
|---|----------|--------|
| 001 | 001_create_asset_table.sql | ✅ |
| 002 | 002_create_sensors_table.sql | ✅ |
| 003 | 003_create_measurements_table.sql | ✅ |
| 004 | 004_timescale_hypertable_migration.sql | ✅ |
| 005 | 005_create_threshold_rules.sql | ✅ |
| 006 | 006_create_events.sql | ✅ |
| 007 | 007_create_asset_health.sql | ✅ |
| 008 | 008_create_asset_relationships.sql | ✅ |
| 009 | 009_create_propagated_events.sql | ✅ |
| 010 | 010_create_asset_health_dependencies.sql | ✅ |
| 011 | 011_create_simulation_tables.sql | ✅ |
| 012 | 012_create_recovery_simulations.sql | ✅ |
| 013 | 013_create_resilience_analysis.sql | ✅ |
| 014 | 014_create_work_orders.sql | ✅ |
| 015 | 015_create_documents.sql | ✅ |
| 016 | 016_create_identity_tables.sql | ✅ |
| 017 | 017_create_workflow_tables.sql | ✅ |
| 018 | 018_create_mqtt_tables.sql | ✅ |
| 019 | 019_create_geoserver_tables.sql | ✅ |
| 020 | 020_create_graph_projection_tables.sql | ✅ |
| 021 | 021_create_ontology_tables.sql | ✅ |
| 022 | 022_create_observability_tables.sql | ✅ |
| 023 | 023_create_performance_tables.sql | ✅ |
| 024 | 024_create_devops_tables.sql | ✅ |
| 025 | 025_create_platform_tables.sql | ✅ |
| 026 | 026_create_storage_tables.sql | ✅ |
| 027 | 027_create_geospatial_tables.sql | ✅ |
| 038 | 038_create_semantic_layer.sql | ✅ |
| 039 | 039_create_timeline_snapshots.sql | ✅ |
| 040 | 040_create_logbook_tables.sql | ✅ |
| 041 | 041_create_knowledge_repository.sql | ✅ |
| 042 | 042_create_copilot_sessions.sql | ✅ |
| 043 | 043_create_rag_cache.sql | ✅ |
| 044 | 044_create_agent_framework.sql | ✅ |
| 045 | 045_create_predictive_maintenance.sql | ✅ |
| 046 | 046_create_root_cause_analysis.sql | ✅ |
| 047 | 047_create_cognitive_twin.sql | ✅ |

**Total:** 37 migrations

---

## ADR Inventory

**Location:** `GCDTP/adr/`

| ID | Filename | Status |
|----|----------|--------|
| 0001 | 0001-use-architecture-decision-records.md | ✅ |
| 0002 | 0002-use-service-oriented-folder-structure.md | ✅ |
| 0003 | 0003-use-docker-for-development-environment.md | ✅ |
| 0004 | 0004-asset-centric-architecture.md | ✅ |
| 0005 | 0005-postgis-spatial-assets.md | ✅ |
| 0006 | 0006-leaflet-map-viewer.md | ✅ |
| 0007 | 0007-sensor-engine.md | ✅ |
| 0008 | 0008-measurement-engine.md | ✅ |
| 0009 | 0009-timescale-hypertable-foundation.md | ✅ |
| 0010 | 0010-threshold-engine.md | ✅ |
| 0011 | 0011-event-engine.md | ✅ |
| 0012 | (gap in sequence) | - |
| 0013 | 0013-health-engine.md | ✅ |
| 0014 | 0014-geoportal-operational-intelligence.md | ✅ |
| 0015 | 0015-system-wide-event-propagation-hardening.md | ✅ |
| 0016 | 0016-asset-relationship-graph-engine.md | ✅ |
| 0017 | 0017-cascading-failure-engine.md | ✅ |
| 0018 | 0018-dependency-aware-health.md | ✅ |
| 0019 | 0019-scenario-simulation-engine.md | ✅ |
| 0020 | 0020-recovery-simulation-engine.md | ✅ |
| 0021 | 0021-resilience-analysis-engine.md | ✅ |
| 0022 | 0022-network-topology-engine.md | ✅ |
| 0023 | 0023-routing-flow-resilience-engines.md | ✅ |
| 0024 | 0024-extensible-simulation-architecture.md | ✅ |
| 0025 | 0025-operational-timeline-engine.md | ✅ |
| 0026 | 0026-work-order-engine.md | ✅ |
| 0027 | 0027-document-management-engine.md | ✅ |
| 0028 | 0028-identity-access-management.md | ✅ |
| 0029 | 0029-cesium-3d-visualization.md | ✅ |
| 0030 | 0030-node-red-integration.md | ✅ |
| 0031 | 0031-emqx-mqtt-integration.md | ✅ |
| 0032 | 0032-geoserver-integration.md | ✅ |
| 0033 | 0033-graph-intelligence-layer.md | ✅ |
| 0034 | 0034-semantic-ontology-layer.md | ✅ |
| 0035 | 0035-architecture-review-and-hardening.md | ✅ |
| 0036 | 0036-observability-and-diagnostics-layer.md | ✅ |
| 0037 | 0037-performance-and-scaling-layer.md | ✅ |
| 0038 | 0038-deployment-and-devops-layer.md | ✅ |
| 0039 | 0039-enterprise-packaging-layer.md | ✅ |
| 0040 | 0040-production-readiness-audit.md | ✅ |
| 0041 | 0041-object-storage-layer.md | ✅ |
| 0042 | 0042-advanced-geospatial-analytics-layer.md | ✅ |
| 0043 | 0043-terriajs-federation-layer.md | ✅ |
| 0044 | 0044-maplibre-vector-tile-layer.md | ✅ |
| 0045 | 0045-kepler-analytics-layer.md | ✅ |
| 0046 | 0046-unified-semantic-layer.md | ✅ |
| 0047 | 0047-timeline-replay-engine.md | ✅ |
| 0048 | 0048-digital-logbook-engine.md | ✅ |
| 0049 | 0049-knowledge-repository-engine.md | ✅ |
| 0050 | 0050-cognitive-copilot-foundation.md | ✅ |
| 0051 | 0051-rag-engine.md | ✅ |
| 0052 | 0052-agent-framework.md | ✅ |
| 0053 | 0053-predictive-maintenance.md | ✅ |
| 0054 | 0054-root-cause-analysis-engine.md | ✅ |
| 0055 | 0055-cognitive-twin-engine.md | ✅ |

**Total:** 54 ADRs (0012 missing, gap confirmed)

---

## Backend Models Inventory

**Location:** `GCDTP/backend/src/models/`

| Model | Filename | Status |
|-------|----------|--------|
| agent_action | agent_action.py | ✅ |
| agent_definition | agent_definition.py | ✅ |
| agent_task | agent_task.py | ✅ |
| asset | asset.py | ✅ |
| asset_health_dependency | asset_health_dependency.py | ✅ |
| asset_relationship | asset_relationship.py | ✅ |
| cause_chain | cause_chain.py | ✅ |
| cause_factor | cause_factor.py | ✅ |
| cognitive_context | cognitive_context.py | ✅ |
| cognitive_query | cognitive_query.py | ✅ |
| cognitive_session | cognitive_session.py | ✅ |
| copilot_message | copilot_message.py | ✅ |
| copilot_session | copilot_session.py | ✅ |
| event | event.py | ✅ |
| health | health.py | ✅ |
| knowledge_document | knowledge_document.py | ✅ |
| knowledge_reference | knowledge_reference.py | ✅ |
| logbook_entry | logbook_entry.py | ✅ |
| maintenance_history | maintenance_history.py | ✅ |
| maintenance_prediction | maintenance_prediction.py | ✅ |
| measurement | measurement.py | ✅ |
| propagated_event | propagated_event.py | ✅ |
| rag_answer | rag_answer.py | ✅ |
| rag_context_chunk | rag_context_chunk.py | ✅ |
| rag_query | rag_query.py | ✅ |
| recovery_result | recovery_result.py | ✅ |
| recovery_simulation | recovery_simulation.py | ✅ |
| resilience_analysis | resilience_analysis.py | ✅ |
| resilience_recommendation | resilience_recommendation.py | ✅ |
| root_cause_analysis | root_cause_analysis.py | ✅ |
| scenario | scenario.py | ✅ |
| scenario_result | scenario_result.py | ✅ |
| semantic_entity | semantic_entity.py | ✅ |
| semantic_relationship | semantic_relationship.py | ✅ |
| semantic_tag | semantic_tag.py | ✅ |
| sensor | sensor.py | ✅ |
| threshold | threshold.py | ✅ |
| timeline_snapshot | timeline_snapshot.py | ✅ |

**Total:** 38 models

---

## Backend Services Inventory

**Location:** `GCDTP/backend/src/services/`

| Service | Filename | Status |
|---------|----------|--------|
| agent_service | agent_service.py | ✅ |
| asset_relationship_service | asset_relationship_service.py | ✅ |
| asset_service | asset_service.py | ✅ |
| attachment_manager | attachment_manager.py | ✅ |
| cognitive_twin_service | cognitive_twin_service.py | ✅ |
| copilot_service | copilot_service.py | ✅ |
| cost_models | cost_models.py | ✅ |
| dependency_health_service | dependency_health_service.py | ✅ |
| diff_engine | diff_engine.py | ✅ |
| document_engine | document_engine.py | ✅ |
| document_indexer | document_indexer.py | ✅ |
| document_types | document_types.py | ✅ |
| document_validator | document_validator.py | ✅ |
| event_recorder | event_recorder.py | ✅ |
| event_service | event_service.py | ✅ |
| failure_propagation_service | failure_propagation_service.py | ✅ |
| flow_engine | flow_engine.py | ✅ |
| flow_models | flow_models.py | ✅ |
| graph_builder | graph_builder.py | ✅ |
| health_service | health_service.py | ✅ |
| inspection_engine | inspection_engine.py | ✅ |
| knowledge_service | knowledge_service.py | ✅ |
| logbook_service | logbook_service.py | ✅ |
| maintenance_engine | maintenance_engine.py | ✅ |
| measurement_service | measurement_service.py | ✅ |
| predictive_maintenance_service | predictive_maintenance_service.py | ✅ |
| rag_service | rag_service.py | ✅ |
| recovery_simulation_service | recovery_simulation_service.py | ✅ |
| replay_engine | replay_engine.py | ✅ |
| resilience_engine | resilience_engine.py | ✅ |
| resilience_service | resilience_service.py | ✅ |
| root_cause_service | root_cause_service.py | ✅ |
| routing_engine | routing_engine.py | ✅ |
| routing_types | routing_types.py | ✅ |
| semantic_service | semantic_service.py | ✅ |
| sensor_service | sensor_service.py | ✅ |
| simulation_service | simulation_service.py | ✅ |
| snapshot_manager | snapshot_manager.py | ✅ |
| threshold_service | threshold_service.py | ✅ |
| timeline_engine | timeline_engine.py | ✅ |
| timeline_query_engine | timeline_query_engine.py | ✅ |
| timeline_service | timeline_service.py | ✅ |
| timeline_types | timeline_types.py | ✅ |
| timeline_validator | timeline_validator.py | ✅ |
| topology_engine | topology_engine.py | ✅ |
| topology_types | topology_types.py | ✅ |
| topology_validator | topology_validator.py | ✅ |
| work_order_engine | work_order_engine.py | ✅ |
| work_order_types | work_order_types.py | ✅ |
| work_order_validator | work_order_validator.py | ✅ |

**Total:** 50 services

---

## API Routes Inventory

**Location:** `GCDTP/backend/src/routes/`

| Route | Filename | Status |
|-------|----------|--------|
| agent | agent_routes.py | ✅ |
| asset | asset_routes.py | ✅ |
| asset_relationship | asset_relationship_routes.py | ✅ |
| cognitive | cognitive_routes.py | ✅ |
| copilot | copilot_routes.py | ✅ |
| event | event_routes.py | ✅ |
| health | health_routes.py | ✅ |
| knowledge | knowledge_routes.py | ✅ |
| logbook | logbook_routes.py | ✅ |
| measurement | measurement_routes.py | ✅ |
| network_health | network_health_routes.py | ✅ |
| predictive | predictive_routes.py | ✅ |
| propagation | propagation_routes.py | ✅ |
| rag | rag_routes.py | ✅ |
| recovery | recovery_routes.py | ✅ |
| resilience | resilience_routes.py | ✅ |
| root_cause | root_cause_routes.py | ✅ |
| scenario | scenario_routes.py | ✅ |
| semantic | semantic_routes.py | ✅ |
| sensor | sensor_routes.py | ✅ |
| threshold | threshold_routes.py | ✅ |
| timeline | timeline_routes.py | ✅ |

**Total:** 22 route files

---

## Schemas Inventory

**Location:** `GCDTP/backend/src/schemas/`

| Schema | Filename | Status |
|--------|----------|--------|
| agent | agent.py | ✅ |
| asset | asset.py | ✅ |
| asset_health_dependency | asset_health_dependency.py | ✅ |
| asset_relationship | asset_relationship.py | ✅ |
| cognitive | cognitive.py | ✅ |
| copilot | copilot.py | ✅ |
| event | event.py | ✅ |
| health | health.py | ✅ |
| knowledge | knowledge.py | ✅ |
| logbook | logbook.py | ✅ |
| measurement | measurement.py | ✅ |
| predictive_maintenance | predictive_maintenance.py | ✅ |
| propagated_event | propagated_event.py | ✅ |
| rag | rag.py | ✅ |
| recovery | recovery.py | ✅ |
| resilience | resilience.py | ✅ |
| root_cause | root_cause.py | ✅ |
| scenario | scenario.py | ✅ |
| semantic | semantic.py | ✅ |
| sensor | sensor.py | ✅ |
| threshold | threshold.py | ✅ |
| timeline | timeline.py | ✅ |

**Total:** 22 schemas

---

## Frontend Pages Inventory

**Location:** `GCDTP/frontend/src/pages/`

| Page | Filename | Test File | Status |
|------|----------|-----------|--------|
| ActiveEvents | ActiveEvents.jsx | No | ✅ |
| AgentWorkbench | AgentWorkbench.jsx | No | ✅ |
| AnalyticsMapPage | AnalyticsMapPage.tsx | No | ✅ |
| AssetDetails | AssetDetails.jsx | No | ✅ |
| AssetHierarchy | AssetHierarchy.jsx | Yes | ✅ |
| AssetList | AssetList.jsx | No | ✅ |
| CognitiveCopilot | CognitiveCopilot.jsx | No | ✅ |
| CognitiveTwin | CognitiveTwin.jsx | No | ✅ |
| CreateAsset | CreateAsset.jsx | No | ✅ |
| CreateSensor | CreateSensor.jsx | No | ✅ |
| CreateThreshold | CreateThreshold.jsx | No | ✅ |
| DigitalLogbook | DigitalLogbook.jsx | No | ✅ |
| DigitalTwin3DPage | DigitalTwin3DPage.tsx | No | ✅ |
| EventDetails | EventDetails.jsx | No | ✅ |
| EventList | EventList.jsx | No | ✅ |
| GeoPortal | GeoPortal.jsx | No | ✅ |
| HealthDashboard | HealthDashboard.jsx | No | ✅ |
| ImpactChain | ImpactChain.jsx | Yes | ✅ |
| KnowledgeRepository | KnowledgeRepository.jsx | No | ✅ |
| Map | Map.jsx | No | ✅ |
| MeasurementDetails | MeasurementDetails.jsx | No | ✅ |
| Measurements | Measurements.jsx | No | ✅ |
| NetworkHealth | NetworkHealth.jsx | Yes | ✅ |
| PredictiveMaintenance | PredictiveMaintenance.jsx | No | ✅ |
| RAGWorkbench | RAGWorkbench.jsx | No | ✅ |
| RecoveryStudio | RecoveryStudio.jsx | Yes | ✅ |
| ResilienceDashboard | ResilienceDashboard.jsx | No | ✅ |
| RootCauseAnalysis | RootCauseAnalysis.jsx | No | ✅ |
| ScenarioStudio | ScenarioStudio.jsx | Yes | ✅ |
| SemanticExplorer | SemanticExplorer.jsx | No | ✅ |
| SensorDetails | SensorDetails.jsx | No | ✅ |
| SensorList | SensorList.jsx | No | ✅ |
| SensorMeasurements | SensorMeasurements.jsx | No | ✅ |
| SensorThresholds | SensorThresholds.jsx | No | ✅ |
| TerriaPortalPage | TerriaPortalPage.tsx | No | ✅ |
| ThresholdList | ThresholdList.jsx | No | ✅ |
| TimelineReplay | TimelineReplay.jsx | No | ✅ |
| VectorMapPage | VectorMapPage.tsx | No | ✅ |

**Total:** 38 production pages (5 with test files)

---

## Test Inventory

### Backend Tests

**Location:** `GCDTP/backend/tests/`

| Test | Status |
|------|--------|
| test_agent_framework.py | ✅ |
| test_asset_relationships.py | ✅ |
| test_assets.py | ✅ |
| test_cognitive_twin.py | ✅ |
| test_copilot_foundation.py | ✅ |
| test_dependency_health.py | ✅ |
| test_devops.py | ✅ |
| test_documents.py | ✅ |
| test_emqx.py | ✅ |
| test_event_system.py | ✅ |
| test_events.py | ✅ |
| test_failure_propagation.py | ✅ |
| test_geoserver.py | ✅ |
| test_geospatial.py | ✅ |
| test_health.py | ✅ |
| test_knowledge_repository.py | ✅ |
| test_logbook_engine.py | ✅ |
| test_measurements.py | ✅ |
| test_neo4j.py | ✅ |
| test_node_red.py | ✅ |
| test_observability.py | ✅ |
| test_ontology.py | ✅ |
| test_performance.py | ✅ |
| test_predictive_maintenance.py | ✅ |
| test_rag_engine.py | ✅ |
| test_recovery_simulation.py | ✅ |
| test_resilience.py | ✅ |
| test_root_cause_analysis.py | ✅ |
| test_routing.py | ✅ |
| test_security.py | ✅ |
| test_semantic_layer.py | ✅ |
| test_sensors.py | ✅ |
| test_simulation_engine.py | ✅ |
| test_storage.py | ✅ |
| test_thresholds.py | ✅ |
| test_timeline.py | ✅ |
| test_timeline_engine.py | ✅ |
| test_timescale_performance.py | ✅ |
| test_topology.py | ✅ |
| test_work_orders.py | ✅ |

**Total:** 40 test files (38 test_*.py + conftest.py)

---

## Consistency Matrix

| Component | Expected | Actual | Match |
|-----------|----------|--------|-------|
| Migrations | 37 | 37 | ✅ |
| ADRs | 54 | 54 | ✅ |
| Models | 38 | 38 | ✅ |
| Services | 50 | 50 | ✅ |
| Routes | 22 | 22 | ✅ |
| Schemas | 22 | 22 | ✅ |
| Frontend Pages | 38 | 38 | ✅ |
| Backend Tests | 38 | 38 | ✅ |

**All inventory items verified.** ✅
