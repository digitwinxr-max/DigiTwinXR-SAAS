# Database Report

**Date:** 2026-06-21
**Repository:** digitwinxr-max/DigiTwinXR-SAAS
**Branch:** feature/tasks-024-029-extensible-architecture

---

## Database Instances

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| PostgreSQL | postgis/postgis:15-3.4 | 5432 | Primary relational DB |
| TimescaleDB | timescale/timescaledb:latest-pg15 | 5433 | Time-series data |
| Neo4j | neo4j:5 | 7474/7687 | Graph database |
| Chroma | ghcr.io/chroma-core/chroma:0.5.0 | 8000 | Vector embeddings |
| Redis | redis:7-alpine | 6379 | Cache/sessions |

---

## Migration Files

**Location:** `GCDTP/database/migrations/`
**Count:** 36 SQL migration files

### Core Schema Migrations

| Migration | Purpose |
|-----------|---------|
| 001_create_asset_table.sql | Asset entities |
| 002_create_sensors_table.sql | Sensor registration |
| 003_create_measurements_table.sql | Time-series measurements |
| 004_timescale_hypertable_migration.sql.skip | TimescaleDB hypertable (skipped) |
| 005_create_threshold_rules.sql | Alert thresholds |
| 006_create_events.sql | Event logging |
| 007_create_asset_health.sql | Health metrics |

### Additional Migrations
- Asset relationships
- Propagation rules
- Network topology
- Resilience analysis
- Scenario simulations
- Recovery actions
- Knowledge graphs
- Semantic tags
- Timeline/events
- Work orders
- Documents
- Learning models
- Prescriptive models

---

## SQLAlchemy Models

**Location:** `GCDTP/backend/src/models/`
**Count:** 40 Python model files

### Core Models

| Model | Table | Relationships |
|-------|-------|---------------|
| Asset | assets | sensors, relationships, events, measurements |
| Sensor | sensors | measurements, thresholds |
| Measurement | measurements | sensor (FK) |
| ThresholdRule | threshold_rules | sensor (FK) |
| Event | events | asset (FK) |
| AssetRelationship | asset_relationships | from_asset, to_asset |

### Extension Models

| Model | Table | Purpose |
|-------|-------|---------|
| ResilienceAnalysis | resilience_analyses | What-if scenarios |
| ResilienceRecommendation | resilience_recommendations | Recommended actions |
| Scenario | scenarios | Simulation configs |
| RecoveryAction | recovery_actions | Recovery procedures |
| TimelineEvent | timeline_events | Audit trail |
| KnowledgeGraph | knowledge_graphs | Semantic knowledge |
| SemanticEntity | semantic_entities | Ontology entities |
| SemanticRelationship | semantic_relationships | Entity links |
| WorkOrder | work_orders | Maintenance tasks |
| Document | documents | Attachments |

---

## Table Relationships

### Asset → Sensor → Measurement
```
assets.id (PK)
    ↓
sensors.asset_id (FK)
    ↓
measurements.sensor_id (FK)  ← ForeignKey("sensors.id")
```

### Asset → Event
```
assets.id (PK)
    ↓
events.asset_id (FK)
```

### Asset → ThresholdRule
```
assets.id (PK)
    ↓
sensors.asset_id (FK)
    ↓
threshold_rules.sensor_id (FK)
```

---

## PostGIS Extensions

**Extension:** PostGIS enabled on PostgreSQL

**Geometry Types:**
- Asset geometry (Point, LineString, Polygon)
- GeoJSON support
- Coordinate transformations via pyproj

---

## TimescaleDB Configuration

**Hypertable:** measurements
**Chunk Interval:** Configured via migration
**Compression:** Enabled for older chunks

---

## Neo4j Graph Schema

**Node Types:**
- Asset
- Sensor
- Component
- System

**Relationship Types:**
- CONTAINS
- CONNECTS_TO
- DEPENDS_ON
- IMPACTS
- PROPAGATES_TO

---

## Redis Usage

**Purpose:** Session storage, caching, pub/sub

**Keys:**
- `session:{user_id}` - User sessions
- `cache:{endpoint}` - API response cache
- `lock:{resource}` - Distributed locks

---

## Status

| Component | Status |
|-----------|--------|
| PostgreSQL + PostGIS | ✅ Running |
| TimescaleDB | ✅ Running |
| Neo4j | ✅ Running |
| Chroma | ✅ Running |
| Redis | ✅ Running |
| Migrations | ✅ Applied |
| Models | ✅ 40 models defined |
| Relationships | ✅ FK constraints defined |
