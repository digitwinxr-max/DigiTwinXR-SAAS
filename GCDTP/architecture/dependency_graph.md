# DigiTwinXR-SAAS Dependency Graph

**Version:** 1.0.0
**Generated:** 2026-06-21

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DigiTwinXR-SAAS Stack                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
        ▼                            ▼                            ▼
┌───────────────┐          ┌─────────────────┐          ┌─────────────────┐
│   Frontend    │          │     Backend     │          │    Database     │
│   (React)     │◄────────►│    (FastAPI)    │◄────────►│   (PostgreSQL)  │
└───────────────┘          └─────────────────┘          └─────────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │   Integration Layer     │
                        │   (GeoServer, Kafka,   │
                        │    NiFi, Camunda)      │
                        └─────────────────────────┘
```

---

## Layer 1: Frontend Dependencies

```
Frontend (React 18)
├── react-router-dom (6.21.0)
│   └── Client-side routing
├── leaflet (1.9.4)
│   └── 2D Map visualization
├── react-leaflet (4.2.1)
│   └── Leaflet React bindings
└── recharts (2.10.0)
    └── Data visualization charts
```

### Frontend Dev Dependencies

```
├── vite (5.0.10)
│   └── Build tool & dev server
├── @vitejs/plugin-react (4.2.1)
│   └── Vite React plugin
├── vitest (1.2.0)
│   └── Unit testing framework
└── @testing-library/react (14.1.0)
    └── React component testing
```

---

## Layer 2: Backend Dependencies

```
Backend (Python 3.11+)
├── FastAPI (0.109.0)
│   └── Web framework & API
├── Uvicorn (0.27.0)
│   └── ASGI server
├── SQLAlchemy (2.0.25)
│   └── ORM framework
├── GeoAlchemy2 (0.14.3)
│   └── PostGIS integration
├── Pydantic (2.5.3)
│   └── Data validation
└── python-dotenv (1.0.0)
    └── Environment configuration
```

### Backend Testing Dependencies

```
├── pytest (7.4.4)
│   └── Unit testing framework
├── pytest-asyncio (0.23.3)
│   └── Async test support
└── httpx (0.26.0)
    └── HTTP client for tests
```

---

## Layer 3: Database Stack

```
PostgreSQL (Primary Database)
├── PostGIS Extension
│   └── Spatial data support
└── TimescaleDB Extension
    └── Time-series optimization
    └── Hypertable for measurements
```

### Database Migrations

```
Migrations (47 files)
├── Core Tables
│   ├── 001-007: Assets, Sensors, Measurements, Events
│   └── 008-013: Relationships, Simulations, Recovery
├── Domain Tables
│   ├── 014-017: Work Orders, Documents, Identity, Workflow
│   └── 018-023: MQTT, GeoServer, Graph, Ontology
├── Platform Tables
│   ├── 024-027: DevOps, Platform, Storage, Geospatial
│   └── 038-047: Semantic, Timeline, Logbook, Knowledge
└── AI Tables
    └── RAG, Agents, Cognitive Twin
```

---

## Layer 4: Geospatial Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                      GEOSPATIAL LAYER                           │
└─────────────────────────────────────────────────────────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
        ▼                            ▼                            ▼
┌───────────────┐          ┌─────────────────┐          ┌─────────────────┐
│   GeoServer   │──────────►│      GDAL       │──────────►│    RasterIO     │
│  (Web Map     │          │  (Raster/Vector  │          │  (Raster I/O)   │
│   Service)    │          │   Translation)   │          │                 │
└───────────────┘          └─────────────────┘          └─────────────────┘
                                     │                            │
                                     │                            │
                                     └──────────┬─────────────────┘
                                                │
                                                ▼
                                    ┌─────────────────────┐
                                    │     GeoPandas       │
                                    │  (GeoDataFrame)     │
                                    └─────────────────────┘
```

### GeoServer Integration (ADR-0032)

```
GeoServer Service
├── WMS (Web Map Service)
├── WFS (Web Feature Service)
├── WCS (Web Coverage Service)
└── Tile Caching (GeoWebCache)
```

### GDAL Operations

```
GDAL Adapter
├── Raster Translation
├── Vector Transformation
├── Projection Conversion
└── Format Translation
```

### RasterIO Integration

```
RasterIO Adapter
├── Raster Reading
├── Raster Writing
├── Band Operations
└── Georeferencing
```

---

## Layer 5: Integration Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTEGRATION LAYER                             │
└─────────────────────────────────────────────────────────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
        ▼                            ▼                            ▼
┌───────────────┐          ┌─────────────────┐          ┌─────────────────┐
│     Kafka     │          │      NiFi       │          │    Camunda      │
│  (Event       │──────────►│  (Data Flow &   │──────────►│  (Workflow      │
│   Streaming)  │          │   Ingestion)    │          │   Engine)       │
└───────────────┘          └─────────────────┘          └─────────────────┘
        │                            │                            │
        └────────────────────────────┼────────────────────────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │   Event System  │
                            │   (FastAPI)     │
                            └─────────────────┘
```

### Kafka Integration

```
Kafka Event Streaming
├── Event Publishing
├── Event Consumption
├── Topic Management
└── Consumer Groups
```

### NiFi Data Flow

```
Apache NiFi
├── Data Ingestion
├── Data Transformation
├── Route &分流
└── Data Provenance
```

### Camunda Workflow

```
Camunda BPMN Engine
├── Workflow Execution
├── Process Monitoring
├── Task Management
└── BPMN 2.0 Support
```

---

## Layer 6: Video & AI Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                      VIDEO FOUNDATION                           │
└─────────────────────────────────────────────────────────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
        ▼                            ▼                            ▼
┌───────────────┐          ┌─────────────────┐          ┌─────────────────┐
│    Frigate    │──────────►│     OpenCV      │──────────►│      YOLO       │
│  (Video       │          │  (Computer      │          │  (Object        │
│   Analytics)  │          │   Vision)       │          │   Detection)    │
└───────────────┘          └─────────────────┘          └─────────────────┘
        │                            │                            │
        └────────────────────────────┼────────────────────────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │   DeepStream    │
                            │ (NVIDIA Video   │
                            │   Pipeline)     │
                            └─────────────────┘
```

### Frigate NVR

```
Frigate Video Analytics
├── Real-time Detection
├── Object Tracking
├── Motion Detection
└── RTSP/RTMP Support
```

### Computer Vision

```
OpenCV
├── Image Processing
├── Video Analysis
├── Feature Detection
└── Image Transformation

YOLO (You Only Look Once)
├── Real-time Detection
├── Multi-class Detection
├── Bounding Boxes
└── Confidence Scores

NVIDIA DeepStream
├── GPU-accelerated Pipeline
├── Video Decode/Encode
├── TensorRT Integration
└── Multi-stream Processing
```

---

## Layer 7: AI & LLM Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                          AI LAYER                               │
└─────────────────────────────────────────────────────────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
        ▼                            ▼                            ▼
┌───────────────┐          ┌─────────────────┐          ┌─────────────────┐
│    Ollama     │──────────►│     Qwen3        │──────────►│   LangGraph     │
│  (Local LLM   │          │  (LLM Model)     │          │  (Agent         │
│   Runtime)    │          │                  │          │   Framework)    │
└───────────────┘          └─────────────────┘          └─────────────────┘
        │                            │                            │
        └────────────────────────────┼────────────────────────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │   RAG Engine    │
                            │  (Retrieval +   │
                            │   Generation)   │
                            └─────────────────┘
```

### Local LLM Runtime

```
Ollama
├── Model Management
├── Inference Server
├── Model Quantization
└── GPU Support
```

### Language Models

```
Qwen3 (LLM)
├── Natural Language Understanding
├── Text Generation
├── Code Completion
└── Reasoning

Supported Models
├── Qwen2.5
├── Llama3
├── Mistral
└── Custom Models
```

### Agent Framework

```
LangGraph
├── Graph-based Workflows
├── State Management
├── Tool Integration
└── Multi-agent Support
```

---

## Layer 8: Cognitive Twin Engine

```
┌─────────────────────────────────────────────────────────────────┐
│                    COGNITIVE TWIN ENGINE                        │
│                         (ADR-0055)                              │
└─────────────────────────────────────────────────────────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
        ▼                            ▼                            ▼
┌───────────────┐          ┌─────────────────┐          ┌─────────────────┐
│   Semantic    │          │     RAG         │          │    Cognitive    │
│   Layer       │◄────────►│   Engine        │◄────────►│    Sessions     │
│               │          │                 │          │                 │
└───────────────┘          └─────────────────┘          └─────────────────┘
        │                            │                            │
        └────────────────────────────┼────────────────────────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │  Knowledge      │
                            │  Repository     │
                            └─────────────────┘
```

### Semantic Layer (ADR-0046)

```
Semantic Services
├── Entity Management
├── Relationship Tracking
├── Tag System
└── Ontology Support
```

### RAG Engine (ADR-0051)

```
RAG Service
├── Context Retrieval
├── Vector Search
├── Answer Generation
└── Source Attribution

Supported Providers
├── Template (Current)
├── OpenAI (Future)
├── Claude (Future)
└── Local LLM (Future)
```

---

## Layer 9: Digital Twin Analytics

```
┌─────────────────────────────────────────────────────────────────┐
│                     DECISION TWIN                                │
└─────────────────────────────────────────────────────────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
        ▼                            ▼                            ▼
┌───────────────┐          ┌─────────────────┐          ┌─────────────────┐
│    Health     │          │    Resilience   │          │   Predictive     │
│   Engine      │──────────►│    Analysis     │──────────►│   Maintenance   │
│               │          │                 │          │                 │
└───────────────┘          └─────────────────┘          └─────────────────┘
        │                            │                            │
        └────────────────────────────┼────────────────────────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │  Root Cause     │
                            │  Analysis       │
                            └─────────────────┘
```

### Health Engine (ADR-0013)

```
Health Services
├── Health Scoring
├── Dependency Awareness
├── Decay Calculation
└── Contributors Analysis
```

### Resilience Analysis (ADR-0021)

```
Resilience Engine
├── Criticality Analysis
├── Vulnerability Assessment
├── Recommendations
└── Impact Modeling
```

### Predictive Maintenance (ADR-0053)

```
Predictive Services
├── Failure Prediction
├── Maintenance Scheduling
├── History Tracking
└── Probability Estimation
```

---

## Layer 10: Workflow & Operations

```
┌─────────────────────────────────────────────────────────────────┐
│                      WORKFLOW LAYER                              │
└─────────────────────────────────────────────────────────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
        ▼                            ▼                            ▼
┌───────────────┐          ┌─────────────────┐          ┌─────────────────┐
│    Work       │          │     Event       │          │    Timeline     │
│   Orders      │──────────►│    Propagation  │──────────►│    Engine       │
│               │          │                 │          │                 │
└───────────────┘          └─────────────────┘          └─────────────────┘
        │                            │                            │
        └────────────────────────────┼────────────────────────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │   Scenario      │
                            │   Simulation    │
                            └─────────────────┘
```

### Work Order Engine (ADR-0026)

```
Work Order Services
├── Order Management
├── Maintenance Planning
├── Inspection Tracking
└── Validation Rules
```

### Event Propagation (ADR-0015)

```
Failure Propagation
├── Cascade Detection
├── Impact Chain
├── Network Propagation
└── Severity Calculation
```

### Timeline Engine (ADR-0025, ADR-0047)

```
Timeline Services
├── Snapshot Management
├── State Replay
├── Diff Computation
└── Range Queries
```

### Scenario Simulation (ADR-0019)

```
Simulation Engine
├── What-if Analysis
├── Impact Assessment
├── Scenario Execution
└── Result Comparison
```

---

## Complete Integration Flow

```
GeoServer ──► GDAL ──► RasterIO ──► GeoPandas ──► Kafka ──► NiFi ──► Camunda
                                        │                         │
                                        │                         │
                                        ▼                         ▼
                               ┌────────────────┐         ┌────────────────┐
                               │  Video Found.  │         │   Workflow     │
                               └────────────────┘         └────────────────┘
                                        │                         │
                    ┌───────────────────┼───────────────────────┘
                    │                   │
                    ▼                   ▼
           ┌────────────────┐   ┌────────────────┐
           │    Frigate     │   │  Work Orders   │
           │    OpenCV      │   │  Events        │
           │    YOLO        │   │  Timeline      │
           │   DeepStream   │   │  Scenarios     │
           └────────────────┘   └────────────────┘
                    │                   │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────┐
                    │  AI Layer      │
                    │  Ollama        │
                    │  Qwen3         │
                    │  LangGraph     │
                    └────────────────┘
                              │
                              ▼
                    ┌────────────────┐
                    │Cognitive Twin  │
                    │    +           │
                    │Decision Twin   │
                    │    +           │
                    │   Workflow     │
                    │    +           │
                    │  Work Orders   │
                    └────────────────┘
```

---

## Service Dependencies Matrix

| Service | GeoServer | GDAL | RasterIO | GeoPandas | Kafka | NiFi | Camunda | Frigate | OpenCV | YOLO | DeepStream | Ollama | Qwen3 | LangGraph |
|---------|-----------|------|----------|-----------|-------|------|---------|---------|--------|------|-----------|--------|-------|----------|
| **Backend API** | ✓ | | | | | | | | | | | | | |
| **Geospatial** | ✓ | ✓ | ✓ | ✓ | | | | | | | | | | |
| **Event System** | | | | | ✓ | | | | | | | | | |
| **Data Flow** | | | | | ✓ | ✓ | | | | | | | | |
| **Workflow** | | | | | | ✓ | ✓ | | | | | | | |
| **Video Analytics** | | | | | | | | ✓ | ✓ | ✓ | ✓ | | | |
| **AI/LLM** | | | | | | | | | | | | ✓ | ✓ | ✓ |
| **Cognitive Twin** | | | | | | | | | | | | ✓ | ✓ | ✓ |
| **Decision Twin** | | | | | ✓ | | | | | | | ✓ | ✓ | ✓ |
| **Work Orders** | | | | | | ✓ | ✓ | | | | | | | |

---

## External Service Dependencies

| External Service | Purpose | Status | ADR |
|-----------------|---------|--------|-----|
| GeoServer | Spatial data serving | ✓ | 0032 |
| PostGIS | Spatial database | ✓ | 0005 |
| TimescaleDB | Time-series data | ✓ | 0009 |
| EMQX | MQTT broker | Planned | 0031 |
| Node-RED | Flow-based programming | Planned | 0030 |
| Kafka | Event streaming | Planned | - |
| NiFi | Data flow | Planned | - |
| Camunda | BPMN workflow | Planned | - |
| Frigate | Video NVR | Planned | - |
| OpenCV | Computer vision | Planned | - |
| YOLO | Object detection | Planned | - |
| DeepStream | GPU video pipeline | Planned | - |
| Ollama | Local LLM runtime | Planned | - |
| Qwen3 | LLM model | Planned | - |
| LangGraph | Agent framework | Planned | - |
