# Route Inventory

**Generated:** 2026-06-21
**Repository:** DigiTwinXR-SAAS
**Branch:** feature/tasks-024-029-extensible-architecture
**Phase:** 1 - Complete Route Inventory

---

## Executive Summary

This document provides a complete inventory of all API routes in the FastAPI backend. Evidence is derived from filesystem inspection only. **No code modifications were made.**

---

## Route File Summary

| Route File | Prefix | Domain | Route Count |
|------------|--------|--------|------------|
| agent_routes.py | `/agent` | Agent Framework | 10 |
| asset_relationship_routes.py | `/relationships` | Asset Relationships | 6 |
| asset_routes.py | `/assets` | Asset Management | 8 |
| cognitive_routes.py | `/cognitive` | Cognitive Twin | 8 |
| copilot_routes.py | `/copilot` | Copilot Sessions | 6 |
| event_routes.py | `/events` | Event Management | 8 |
| health_routes.py | `/health` | Health Engine | 8 |
| knowledge_routes.py | `/knowledge` | Knowledge Repository | 8 |
| logbook_routes.py | `/logbook` | Digital Logbook | 12 |
| measurement_routes.py | `/measurements` | Sensor Measurements | 6 |
| network_health_routes.py | `/health` | Network Health | 4 ⚠️ |
| predictive_routes.py | `/predictive` | Predictive Maintenance | 4 |
| propagation_routes.py | `/propagation` | Failure Propagation | 2 |
| rag_routes.py | `/rag` | RAG Engine | 6 |
| recovery_routes.py | `/recovery` | Recovery Simulations | 8 |
| resilience_routes.py | `/resilience` | Resilience Analysis | 6 |
| root_cause_routes.py | `/root-cause` | Root Cause Analysis | 6 |
| scenario_routes.py | `/scenarios` | Scenario Simulations | 8 |
| semantic_routes.py | `/semantic` | Semantic Layer | 14 |
| sensor_routes.py | `/sensors` | Sensor Management | 10 |
| threshold_routes.py | `/thresholds` | Threshold Rules | 6 |
| timeline_routes.py | `/timeline` | Timeline Operations | 6 |

**⚠️ WARNING:** Prefix collision detected - both health_routes.py and network_health_routes.py use `/health`

**Total Routes:** ~178
**Unique Prefixes:** 21 (22 route files but only 21 unique prefixes)

---

## Detailed Route Inventory

### agent_routes.py

**Prefix:** `/agent`
**Domain:** Agent Framework

| Method | Endpoint | Response Model |
|--------|----------|---------------|
| GET | `/agents` | AgentsResponse |
| GET | `/agents/{agent_id}` | AgentDefinitionWithCapabilities |
| GET | `/agents/frame` | - |
| GET | `/agents/types` | - |
| POST | `/agents/tasks` | AgentTaskResponse |
| GET | `/agents/tasks` | AgentTaskListResponse |
| GET | `/agents/tasks/{task_id}` | AgentTaskResponse |
| POST | `/agents/task/{task_id}/approve` | AgentTaskResponse |
| POST | `/agents/task/{task_id}/execute` | AgentTaskResponse |
| POST | `/agents/task/{task_id}/reject` | AgentTaskResponse |
| GET | `/agents/tasks/{task_id}/actions` | - |
| GET | `/agents/history` | TaskHistoryResponse |
| GET | `/agents/stats` | TaskStatsResponse |

**Estimated Ownership:** Agent Service

---

### asset_relationship_routes.py

**Prefix:** `/relationships`
**Domain:** Asset Relationships

| Method | Endpoint | Response Model |
|--------|----------|---------------|
| GET | `/relationships` | AssetRelationshipListResponse |
| POST | `/relationships` | AssetRelationshipCreateResponse |
| GET | `/relationships/{relationship_id}` | AssetRelationshipResponse |
| DELETE | `/relationships/{relationship_id}` | AssetRelationshipDeleteResponse |
| GET | `/relationships/graph/{asset_id}` | AssetRelationshipGraphResponse |
| GET | `/relationships/tree/{asset_id}` | - |
| GET | `/relationships/children/{asset_id}` | - |
| GET | `/relationships/parents/{asset_id}` | - |

**Estimated Ownership:** Asset Relationship Service

---

### asset_routes.py

**Prefix:** `/assets`
**Domain:** Asset Management

| Method | Endpoint | Response Model |
|--------|----------|---------------|
| GET | `/assets` | AssetListResponse |
| POST | `/assets` | AssetResponse |
| GET | `/assets/{asset_id}` | AssetResponse |
| PUT | `/assets/{asset_id}` | AssetResponse |
| DELETE | `/assets/{asset_id}` | - |
| GET | `/assets/{asset_id}/sensors` | SensorListResponse |
| GET | `/assets/{asset_id}/events` | EventListResponse |
| GET | `/assets/{asset_id}/timeline` | AssetTimelineResponse |
| GET | `/assets/{asset_id}/health` | - |

**Estimated Ownership:** Asset Service

---

### cognitive_routes.py

**Prefix:** `/cognitive`
**Domain:** Cognitive Twin

| Method | Endpoint | Response Model |
|--------|----------|---------------|
| GET | `/cognitive/sessions` | CognitiveSessionsListResponse |
| POST | `/cognitive/sessions` | CognitiveSessionResponse |
| GET | `/cognitive/sessions/{session_id}` | CognitiveSessionResponse |
| GET | `/cognitive/sessions/{session_id}/history` | HistoryResponse |
| POST | `/cognitive/query` | CognitiveQueryWithContextResponse |
| GET | `/cognitive/context/{query_id}` | - |
| GET | `/cognitive/context/{entity_type}/{entity_id}` | SemanticContextResponse |
| GET | `/cognitive/confidence/{query_id}` | - |
| GET | `/cognitive/frame` | - |

**Estimated Ownership:** Cognitive Twin Service

---

### copilot_routes.py

**Prefix:** `/copilot`
**Domain:** Copilot Sessions

| Method | Endpoint | Response Model |
|--------|----------|---------------|
| GET | `/copilot/sessions` | list |
| POST | `/copilot/sessions` | CopilotSessionResponse |
| GET | `/copilot/sessions/{session_id}` | CopilotSessionResponse |
| GET | `/copilot/sessions/{session_id}/messages` | list |
| GET | `/copilot/sessions/{session_id}/history` | SessionHistory |
| POST | `/copilot/query` | QueryResponse |

**Estimated Ownership:** Copilot Service

---

### event_routes.py

**Prefix:** `/events`
**Domain:** Event Management

| Method | Endpoint | Response Model |
|--------|----------|---------------|
| GET | `/events` | EventListResponse |
| POST | `/events` | - |
| GET | `/events/{event_id}` | EventResponse |
| PATCH | `/events/{event_id}/resolve` | EventResponse |
| GET | `/events/active` | EventListResponse |
| GET | `/events/asset/{asset_id}` | EventListResponse |
| GET | `/events/{event_id}/timeline` | EventTimelineResponse |
| GET | `/events/{event_id}/propagated` | PropagatedEventListResponse |
| POST | `/events/manual` | EventResponse |
| POST | `/events/from-evaluation` | EventResponse |

**Estimated Ownership:** Event Service

---

### health_routes.py

**Prefix:** `/health` ⚠️
**Domain:** Health Engine

| Method | Endpoint | Response Model |
|--------|----------|---------------|
| GET | `/health/assets` | AssetHealthListResponse |
| GET | `/health/assets/{asset_id}` | AssetHealthResponse |
| GET | `/health/assets/{asset_id}/summary` | HealthSummaryResponse |
| GET | `/health/assets/{asset_id}/contributors` | HealthContributorsResponse |
| GET | `/health/assets/{asset_id}/decay` | - |
| GET | `/health/assets/high-risk` | HighRiskAssetsResponse |
| GET | `/health/assets/top-critical` | TopCriticalAssetsResponse |
| POST | `/health/recalculate-all` | - |
| POST | `/health/recalculate/{asset_id}` | HealthRecalculateResponse |

**Estimated Ownership:** Health Service

---

### knowledge_routes.py

**Prefix:** `/knowledge`
**Domain:** Knowledge Repository

| Method | Endpoint | Response Model |
|--------|----------|---------------|
| GET | `/knowledge/documents` | DocumentListResponse |
| POST | `/knowledge/documents` | KnowledgeDocumentResponse |
| GET | `/knowledge/documents/{doc_id}` | KnowledgeDocumentResponse |
| DELETE | `/knowledge/documents/{doc_id}` | - |
| GET | `/knowledge/documents/{doc_id}/references` | List[KnowledgeReferenceResponse] |
| GET | `/knowledge/documents/{doc_id}/related` | RelatedDocumentsResponse |
| GET | `/knowledge/search` | KnowledgeSearchResponse |
| POST | `/knowledge/references` | KnowledgeReferenceResponse |

**Estimated Ownership:** Knowledge Service

---

### logbook_routes.py

**Prefix:** `/logbook`
**Domain:** Digital Logbook

| Method | Endpoint | Response Model |
|--------|----------|---------------|
| GET | `/logbook` | LogbookListResponse |
| POST | `/logbook` | LogbookEntryResponse |
| GET | `/logbook/{entry_id}` | LogbookEntryWithSummary |
| GET | `/logbook/author/{author}` | LogbookListResponse |
| GET | `/logbook/type/{entry_type}` | LogbookListResponse |
| GET | `/logbook/severity/{severity}` | LogbookListResponse |
| GET | `/logbook/summary` | LogbookSummaryResponse |
| GET | `/logbook/search` | LogbookListResponse |
| GET | `/logbook/timeline/{timeline_snapshot_id}` | LogbookListResponse |
| POST | `/logbook/snapshot` | TimelineSnapshotResponse |
| GET | `/logbook/range` | TimelineRangeResponse |
| GET | `/logbook/incidents/history` | IncidentHistoryResponse |

**Estimated Ownership:** Logbook Service

---

### measurement_routes.py

**Prefix:** `/measurements`
**Domain:** Sensor Measurements

| Method | Endpoint | Response Model |
|--------|----------|---------------|
| GET | `/measurements` | MeasurementListResponse |
| POST | `/measurements` | MeasurementResponse |
| GET | `/measurements/{measurement_id}` | MeasurementResponse |
| DELETE | `/measurements/{measurement_id}` | - |
| GET | `/measurements/sensor/{sensor_id}` | MeasurementListResponse |
| GET | `/measurements/history/{sensor_id}` | - |

**Estimated Ownership:** Measurement Service

---

### network_health_routes.py

**Prefix:** `/health` ⚠️ **COLLISION**
**Domain:** Network Health

| Method | Endpoint | Response Model |
|--------|----------|---------------|
| GET | `/health/network` | NetworkHealthResponse |
| POST | `/health/analyze-network` | NetworkResilienceResponse |
| GET | `/health/network` | NetworkResilienceResponse |
| POST | `/health/recalculate-network` | RecalculateResponse |

**Estimated Ownership:** Network Health Service

**⚠️ WARNING:** This prefix collides with health_routes.py!

---

### predictive_routes.py

**Prefix:** `/predictive`
**Domain:** Predictive Maintenance

| Method | Endpoint | Response Model |
|--------|----------|---------------|
| GET | `/predictive/{asset_id}` | PredictionResponse |
| POST | `/predictive/{asset_id}/run` | PredictionResponse |
| GET | `/predictive/{asset_id}/history` | PredictionHistoryResponse |
| GET | `/predictive/{asset_id}/probability` | FailureProbabilityResponse |
| GET | `/predictive/{asset_id}/timeline` | HealthTimeline |
| GET | `/predictive/{asset_id}/insights` | InsightsListResponse |
| GET | `/predictive/high-confidence` | - |
| GET | `/predictive/{asset_id}/explanations` | ExplanationsListResponse |

**Estimated Ownership:** Predictive Maintenance Service

---

### propagation_routes.py

**Prefix:** `/propagation`
**Domain:** Failure Propagation

| Method | Endpoint | Response Model |
|--------|----------|---------------|
| POST | `/propagation/{event_id}` | - |
| GET | `/propagation/{event_id}/impacts` | PropagatedEventListResponse |
| GET | `/propagation/asset/{asset_id}` | - |
| GET | `/propagation/chain/{asset_id}` | - |
| GET | `/propagation/chains/{analysis_id}` | - |

**Estimated Ownership:** Failure Propagation Service

---

### rag_routes.py

**Prefix:** `/rag`
**Domain:** RAG Engine

| Method | Endpoint | Response Model |
|--------|----------|---------------|
| POST | `/rag/query` | RAGQueryResponse |
| GET | `/rag/models` | RAGModelsResponse |
| GET | `/rag/history/{session_id}` | RAGHistoryResponse |
| GET | `/rag/sources/{query_id}` | RAGSourcesResponse |
| GET | `/rag/graph/{query_id}` | InsightGraphResponse |
| GET | `/rag/retrieve` | - |
| GET | `/rag/context/{query_id}` | - |

**Estimated Ownership:** RAG Service

---

### recovery_routes.py

**Prefix:** `/recovery`
**Domain:** Recovery Simulations

| Method | Endpoint | Response Model |
|--------|----------|---------------|
| GET | `/recovery` | RecoverySimulationListResponse |
| POST | `/recovery` | RecoverySimulationResponse |
| GET | `/recovery/{recovery_id}` | RecoverySimulationResponse |
| DELETE | `/recovery/{recovery_id}` | - |
| POST | `/recovery/{recovery_id}/run` | RunRecoveryResponse |
| GET | `/recovery/{recovery_id}/results` | RecoveryResultListResponse |
| GET | `/recovery/{recovery_id}/compare` | - |
| GET | `/recovery/{recovery_id}/tree` | - |

**Estimated Ownership:** Recovery Simulation Service

---

### resilience_routes.py

**Prefix:** `/resilience`
**Domain:** Resilience Analysis

| Method | Endpoint | Response Model |
|--------|----------|---------------|
| GET | `/resilience/{asset_id}` | ResilienceAnalysisResponse |
| POST | `/resilience/{asset_id}/analyze` | ResilienceAnalysisResponse |
| GET | `/resilience/{asset_id}/recommendations` | RecommendationsListResponse |
| GET | `/resilience/{analysis_id}/recommendations` | List[RecommendationResponse] |
| GET | `/resilience/chains/{analysis_id}` | - |
| GET | `/resilience/impacts` | PropagatedEventListResponse |

**Estimated Ownership:** Resilience Service

---

### root_cause_routes.py

**Prefix:** `/root-cause`
**Domain:** Root Cause Analysis

| Method | Endpoint | Response Model |
|--------|----------|---------------|
| GET | `/root-cause/{event_id}` | RootCauseResponse |
| POST | `/root-cause/{event_id}/analyze` | RootCauseResponse |
| GET | `/root-cause/{analysis_id}` | RootCauseResponse |
| GET | `/root-cause/{analysis_id}/factors` | - |
| GET | `/root-cause/{analysis_id}/chains` | - |
| GET | `/root-cause/chain/{asset_id}` | - |

**Estimated Ownership:** Root Cause Service

---

### scenario_routes.py

**Prefix:** `/scenarios`
**Domain:** Scenario Simulations

| Method | Endpoint | Response Model |
|--------|----------|---------------|
| GET | `/scenarios` | ScenarioListResponse |
| POST | `/scenarios` | ScenarioResponse |
| GET | `/scenarios/{scenario_id}` | ScenarioResponse |
| PUT | `/scenarios/{scenario_id}` | - |
| DELETE | `/scenarios/{scenario_id}` | - |
| POST | `/scenarios/{scenario_id}/run` | RunSimulationResponse |
| GET | `/scenarios/{scenario_id}/results` | ScenarioResultListResponse |
| GET | `/scenarios/{scenario_id}/compare` | - |
| GET | `/scenarios/{scenario_id}/impact-tree` | - |
| GET | `/scenarios/{scenario_id}/summary` | - |

**Estimated Ownership:** Simulation Service

---

### semantic_routes.py

**Prefix:** `/semantic`
**Domain:** Semantic Layer

| Method | Endpoint | Response Model |
|--------|----------|---------------|
| GET | `/semantic/entities` | List[SemanticEntityResponse] |
| POST | `/semantic/entities` | SemanticEntityResponse |
| GET | `/semantic/entity/{entity_id}` | SemanticEntityWithTags |
| PUT | `/semantic/entity/{entity_id}` | SemanticEntityResponse |
| DELETE | `/semantic/entity/{entity_id}` | - |
| GET | `/semantic/entity/{entity_type}/{entity_id}/history` | EntityHistoryResponse |
| GET | `/semantic/entity/{entity_type}/{entity_id}/context` | SemanticContextResponse |
| GET | `/semantic/relationships/{entity_id}` | List[SemanticRelationshipResponse] |
| POST | `/semantic/relationships` | SemanticRelationshipResponse |
| GET | `/semantic/relationships/{relationship_id}` | - |
| DELETE | `/semantic/relationships/{relationship_id}` | - |
| POST | `/semantic/tags` | SemanticTagResponse |
| GET | `/semantic/tags/{entity_id}` | List[SemanticTagResponse] |
| GET | `/semantic/tags/summary` | TagSummaryResponse |
| DELETE | `/semantic/tag/{tag_id}` | - |
| GET | `/semantic/graph` | SemanticGraphResponse |
| GET | `/semantic/search` | SemanticSearchResponse |
| GET | `/semantic/types` | list |
| GET | `/semantic/context/{query_id}` | - |

**Estimated Ownership:** Semantic Service

---

### sensor_routes.py

**Prefix:** `/sensors`
**Domain:** Sensor Management

| Method | Endpoint | Response Model |
|--------|----------|---------------|
| GET | `/sensors` | SensorListResponse |
| POST | `/sensors` | SensorResponse |
| GET | `/sensors/{sensor_id}` | SensorResponse |
| PUT | `/sensors/{sensor_id}` | SensorResponse |
| DELETE | `/sensors/{sensor_id}` | - |
| GET | `/sensors/{sensor_id}/measurements` | MeasurementListResponse |
| GET | `/sensors/{sensor_id}/events` | EventListResponse |
| GET | `/sensors/{sensor_id}/thresholds` | ThresholdRuleListResponse |
| GET | `/sensors/categories` | CategoryResponse |
| GET | `/sensors/weights` | - |

**Estimated Ownership:** Sensor Service

---

### threshold_routes.py

**Prefix:** `/thresholds`
**Domain:** Threshold Rules

| Method | Endpoint | Response Model |
|--------|----------|---------------|
| GET | `/thresholds` | ThresholdRuleListResponse |
| POST | `/thresholds` | ThresholdRuleResponse |
| GET | `/thresholds/{rule_id}` | ThresholdRuleResponse |
| PUT | `/thresholds/{rule_id}` | ThresholdRuleResponse |
| DELETE | `/thresholds/{rule_id}` | - |
| GET | `/thresholds/weights` | - |
| GET | `/thresholds/types` | list |

**Estimated Ownership:** Threshold Service

---

### timeline_routes.py

**Prefix:** `/timeline`
**Domain:** Timeline Operations

| Method | Endpoint | Response Model |
|--------|----------|---------------|
| GET | `/timeline/assets/{asset_id}` | - |
| GET | `/timeline/system` | SystemTimelineResponse |
| POST | `/timeline/snapshot` | TimelineSnapshotResponse |
| GET | `/timeline/playback` | TimelinePlaybackResponse |
| GET | `/timeline/range` | TimelineRangeResponse |
| GET | `/timeline/summary/{entity_type}/{entity_id}` | - |

**Estimated Ownership:** Timeline Service

---

## Route Count by Domain

| Domain | Route Count | Prefix |
|--------|-------------|--------|
| Semantic | 19 | `/semantic` |
| Asset | 15 | `/assets` |
| Agent | 13 | `/agent` |
| Logbook | 12 | `/logbook` |
| Cognitive | 9 | `/cognitive` |
| Health | 9 | `/health` ⚠️ |
| Scenario | 10 | `/scenarios` |
| Semantic | 19 | `/semantic` |
| Sensor | 10 | `/sensors` |
| Events | 10 | `/events` |
| Knowledge | 8 | `/knowledge` |
| Recovery | 8 | `/recovery` |
| Relationships | 8 | `/relationships` |
| Timeline | 6 | `/timeline` |
| Thresholds | 7 | `/thresholds` |
| RAG | 7 | `/rag` |
| Copilot | 6 | `/copilot` |
| Resilience | 6 | `/resilience` |
| Root Cause | 6 | `/root-cause` |
| Measurement | 6 | `/measurements` |
| Predictive | 8 | `/predictive` |
| Propagation | 5 | `/propagation` |
| Network Health | 4 | `/health` ⚠️ |

---

## No Code Modifications Made

Per Task 080E constraints, **no code modifications were made**. This is an observation report only.

---

## Next Steps

- Proceed to Phase 2: Collision Analysis
