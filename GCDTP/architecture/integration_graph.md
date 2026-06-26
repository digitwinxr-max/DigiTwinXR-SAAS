# DigiTwinXR-SAAS Integration Graph

**Version:** 1.0.0
**Generated:** 2026-06-21

---

## Integration Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INTEGRATION LAYER                                  │
│                                                                             │
│   GeoServer ──► GDAL ──► RasterIO ──► GeoPandas ──► Kafka ──► NiFi ──► Camunda   │
│                                            │                                │
│                                            ▼                                │
│                                    ┌─────────────────┐                     │
│                                    │  Video Found.    │                     │
│                                    └─────────────────┘                     │
│                                            │                                │
│                                            ▼                                │
│                                    ┌─────────────────┐                     │
│                                    │   Frigate       │                     │
│                                    │   OpenCV        │                     │
│                                    │   YOLO          │                     │
│                                    │   DeepStream    │                     │
│                                    └─────────────────┘                     │
│                                            │                                │
│                                            ▼                                │
│                                    ┌─────────────────┐                     │
│                                    │   Ollama        │                     │
│                                    │   Qwen3         │                     │
│                                    │   LangGraph     │                     │
│                                    └─────────────────┘                     │
│                                            │                                │
│                                            ▼                                │
│                                    ┌─────────────────┐                     │
│                                    │  Cognitive Twin  │                     │
│                                    └─────────────────┘                     │
│                                            │                                │
│                                            ▼                                │
│                                    ┌─────────────────┐                     │
│                                    │  Decision Twin   │                     │
│                                    └─────────────────┘                     │
│                                            │                                │
│                                            ▼                                │
│                                    ┌─────────────────┐                     │
│                                    │   Workflow      │                     │
│                                    └─────────────────┘                     │
│                                            │                                │
│                                            ▼                                │
│                                    ┌─────────────────┐                     │
│                                    │  Work Orders    │                     │
│                                    └─────────────────┘                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Geospatial Foundation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GEOSPATIAL FOUNDATION                                │
│                              ADR-0005, ADR-0032                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  GeoServer                                   │
│                                                                             │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────────────────┐   │
│   │   WMS   │    │   WFS   │    │   WCS   │    │   GeoWebCache       │   │
│   │ Web Map │    │ Web     │    │ Web     │    │   Tile Caching      │   │
│   │ Service │    │ Feature │    │ Coverage│    │                     │   │
│   │         │    │ Service │    │ Service │    │                     │   │
│   └─────────┘    └─────────┘    └─────────┘    └─────────────────────┘   │
│                                                                             │
│   Responsibilities:                                                          │
│   - Serve spatial data as standard OGC services                            │
│   - Cache tiles for performance                                            │
│   - Manage spatial data publishing                                         │
│                                                                             │
│   Connected to:                                                             │
│   - GDAL (data ingestion)                                                  │
│   - Frontend Map viewers                                                   │
│   - PostGIS (data storage)                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                    GDAL                                      │
│                        Geospatial Data Abstraction                           │
│                                                                             │
│   Responsibilities:                                                          │
│   - Translate between raster/vector formats                                 │
│   - Handle projections and coordinate systems                              │
│   - Process spatial data transformations                                   │
│   - Support 100+ formats (GeoTIFF, Shapefile, etc.)                         │
│                                                                             │
│   Key Operations:                                                            │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐     │
│   │  Raster Ops     │    │  Vector Ops      │    │  Transformation │     │
│   │  - Resample     │    │  - Buffer       │    │  - Project      │     │
│   │  - Reproject    │───►│  - Intersect    │───►│  - Convert      │     │
│   │  - Composite    │    │  - Union         │    │  - Translate    │     │
│   └─────────────────┘    └─────────────────┘    └─────────────────┘     │
│                                                                             │
│   Connected to:                                                             │
│   - GeoServer (output)                                                      │
│   - RasterIO (raster handling)                                             │
│   - GeoPandas (vector handling)                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  RasterIO                                    │
│                         High-Performance Raster I/O                          │
│                              ADR-0042 (Stubs)                               │
│                                                                             │
│   Responsibilities:                                                          │
│   - Fast raster reading/writing                                             │
│   - Band manipulation                                                       │
│   - Georeference handling                                                   │
│   - Memory-efficient processing                                            │
│                                                                             │
│   Key Classes:                                                              │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐     │
│   │  Dataset        │    │  Profile        │    │  Window         │     │
│   │  - open()      │    │  - width        │    │  - read()       │     │
│   │  - write()     │    │  - height       │    │  - write()      │     │
│   │  - close()     │    │  - crs          │    │  - sliced       │     │
│   └─────────────────┘    └─────────────────┘    └─────────────────┘     │
│                                                                             │
│   Connected to:                                                             │
│   - GDAL (low-level driver)                                                 │
│   - GeoPandas (data frames)                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                 GeoPandas                                    │
│                      Pandas-Like Spatial Operations                           │
│                              ADR-0042 (Stubs)                               │
│                                                                             │
│   Responsibilities:                                                          │
│   - DataFrame-like API for spatial data                                    │
│   - Spatial joins and operations                                            │
│   - Coordinate system transformations                                       │
│   - Visualization integration                                               │
│                                                                             │
│   Key Classes:                                                              │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐     │
│   │  GeoDataFrame   │    │  GeoSeries      │    │  GeoData        │     │
│   │  - spatial join │    │  - buffer       │    │  - shapely     │     │
│   │  - overlay      │    │  - overlay      │    │  - transform   │     │
│   └─────────────────┘    └─────────────────┘    └─────────────────┘     │
│                                                                             │
│   Connected to:                                                             │
│   - RasterIO (array data)                                                  │
│   - Kafka (data streaming)                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Layer 2: Data Integration

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA INTEGRATION LAYER                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                    Kafka                                    │
│                           Event Streaming Platform                            │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                           Topics                                      │  │
│   │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐ │  │
│   │  │  sensor-   │  │   events   │  │  health-   │  │  alerts    │ │  │
│   │  │  data      │  │            │  │  metrics   │  │            │ │  │
│   │  └────────────┘  └────────────┘  └────────────┘  └────────────┘ │  │
│   │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐ │  │
│   │  │  geospatial│  │  video-     │  │  workflow  │  │  work-     │ │  │
│   │  │  updates   │  │  analytics  │  │  events    │  │  orders    │ │  │
│   │  └────────────┘  └────────────┘  └────────────┘  └────────────┘ │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   Responsibilities:                                                          │
│   - Real-time data streaming                                                │
│   - Event sourcing                                                          │
│   - Data pipeline backbone                                                  │
│   - Decoupling microservices                                               │
│                                                                             │
│   Producers:                                                                │
│   - IoT Gateway (sensor data)                                              │
│   - Event Engine (system events)                                            │
│   - Video Analytics (Frigate/OpenCV)                                       │
│   - GeoServer (spatial updates)                                            │
│                                                                             │
│   Consumers:                                                               │
│   - NiFi (data processing)                                                 │
│   - Health Engine (metrics)                                                 │
│   - RAG Engine (context)                                                   │
│   - Cognitive Twin (insights)                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                   Apache NiFi                               │
│                           Data Flow & Ingestion                              │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                          Processors                                  │  │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │  │
│   │  │ Consume  │  │  Route   │  │  Enrich  │  │  Publish  │            │  │
│   │  │  Kafka   │──►│  Flow    │──►│  Data    │──►│  to       │            │  │
│   │  │          │  │          │  │          │  │  Camunda  │            │  │
│   │  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │  │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │  │
│   │  │ Fetch    │  │  Split   │  │  Validate│  │  Store   │            │  │
│   │  │ GeoJSON  │──►│  JSON    │──►│  Schema  │──►│  S3/HDFS  │            │  │
│   │  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   Responsibilities:                                                          │
│   - Data ingestion from multiple sources                                    │
│   - Data transformation and enrichment                                      │
│   - Flow-based programming                                                  │
│   - Data provenance tracking                                                │
│                                                                             │
│   Connected to:                                                             │
│   - Kafka (consume/produce)                                                │
│   - Camunda (workflow triggers)                                            │
│   - Object Storage (data archival)                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  Camunda                                     │
│                          BPMN Workflow Engine                                │
│                              ADR-0026 (Work Orders)                          │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                       Workflow Definitions                            │  │
│   │  ┌────────────────────────────────────────────────────────────────┐│  │
│   │  │                                                                 ││  │
│   │  │    ┌──────┐     ┌──────┐     ┌──────┐     ┌──────┐            ││  │
│   │  │    │Start │────►│ Task │────►│Review│────►│ End  │            ││  │
│   │  │    └──────┘     └──────┘     └──────┘     └──────┘            ││  │
│   │  │                                                                 ││  │
│   │  └────────────────────────────────────────────────────────────────┘│  │
│   │                                                                     │  │
│   │  Workflow Types:                                                    │  │
│   │  - Maintenance Workflow                                             │  │
│   │  - Inspection Workflow                                              │  │
│   │  - Incident Response                                                │  │
│   │  - Equipment Changeover                                             │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   Responsibilities:                                                          │
│   - Workflow orchestration                                                  │
│   - Task assignment and tracking                                            │
│   - Process automation                                                     │
│   - Business rule execution                                                 │
│                                                                             │
│   Connected to:                                                            │
│   - NiFi (workflow triggers)                                               │
│   - Work Order Engine (backend)                                            │
│   - External Systems (email, Slack)                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Layer 3: Video Foundation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            VIDEO FOUNDATION LAYER                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  Frigate                                    │
│                        Network Video Recorder (NVR)                          │
│                                                                             │
│   Responsibilities:                                                          │
│   - Real-time video stream management                                       │
│   - Object detection (persons, vehicles, etc.)                              │
│   - Motion detection                                                        │
│   - RTSP/RTMP stream handling                                               │
│   - Event recording and playback                                            │
│                                                                             │
│   Key Features:                                                             │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐     │
│   │  Stream Mgmt    │    │  Detection      │    │  Event Gen      │     │
│   │  - Add cameras  │    │  - Objects      │───►│  - MQTT topics  │     │
│   │  - Multi-stream │    │  - Motion       │    │  - Webhooks     │     │
│   │  - TLS          │    │  - Zones        │    │  - REST         │     │
│   └─────────────────┘    └─────────────────┘    └─────────────────┘     │
│                                                                             │
│   Connected to:                                                             │
│   - OpenCV (frame processing)                                              │
│   - Kafka (event streaming)                                                │
│   - Backend (event API)                                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                   OpenCV                                    │
│                          Computer Vision Library                             │
│                                                                             │
│   Responsibilities:                                                          │
│   - Image processing                                                        │
│   - Video frame analysis                                                    │
│   - Feature detection (edges, corners, etc.)                                │
│   - Image transformations                                                  │
│   - Color space conversions                                                 │
│                                                                             │
│   Key Modules:                                                              │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐     │
│   │  imgproc        │    │  videoio        │    │  dnn            │     │
│   │  - resize       │    │  - VideoCapture │    │  - Neural Nets  │     │
│   │  - blur         │    │  - VideoWriter  │    │  - Pre-trained  │     │
│   │  - threshold    │    │                 │    │                 │     │
│   └─────────────────┘    └─────────────────┘    └─────────────────┘     │
│                                                                             │
│   Connected to:                                                             │
│   - Frigate (frame source)                                                 │
│   - YOLO (object detection)                                               │
│   - DeepStream (GPU pipeline)                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                    YOLO                                     │
│                        You Only Look Once (Detection)                        │
│                                                                             │
│   Responsibilities:                                                          │
│   - Real-time object detection                                             │
│   - Multi-class classification                                              │
│   - Bounding box generation                                                 │
│   - Confidence scoring                                                      │
│                                                                             │
│   Supported Classes:                                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  Industrial Equipment    │  Safety Gear    │  Anomalies          │  │
│   │  ───────────────────────  │  ───────────    │  ──────────         │  │
│   │  • Transformers          │  • Hard hats    │  • Equipment fail   │  │
│   │  • Circuit breakers      │  • Safety vests │  • Oil leaks       │  │
│   │  • Valves                │  • Safety glasses│  • Smoke/Fire     │  │
│   │  • Motors                │  • Gloves        │  • Unauthorized    │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   Model Variants:                                                          │
│   - YOLOv5 (production)                                                    │
│   - YOLOv8 (latest)                                                        │
│   - YOLOv8-Seg (segmentation)                                              │
│                                                                             │
│   Connected to:                                                            │
│   - OpenCV (frame preprocessing)                                          │
│   - DeepStream (GPU acceleration)                                          │
│   - Backend (detection events)                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                NVIDIA DeepStream                             │
│                         GPU-Accelerated Video Pipeline                       │
│                                                                             │
│   Responsibilities:                                                          │
│   - Hardware-accelerated video decode/encode                               │
│   - TensorRT inference integration                                          │
│   - Multi-stream processing (100+ cameras)                                 │
│   - Real-time analytics pipeline                                            │
│                                                                             │
│   Pipeline Architecture:                                                    │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                                                                     │  │
│   │  ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐ │  │
│   │  │ Source │──►│ Decode │──►│ Pre-   │──►│ Inference│──►│  Sink  │ │  │
│   │  │        │   │        │   │process │   │ (TensorRT)│  │        │ │  │
│   │  │ RTSP   │   │ NVDEC  │   │        │   │  + YOLO │   │ MQTT/  │ │  │
│   │  │ USB    │   │        │   │        │   │         │   │ Kafka  │ │  │
│   │  └────────┘   └────────┘   └────────┘   └────────┘   └────────┘ │  │
│   │                                                                     │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   Connected to:                                                             │
│   - YOLO (inference)                                                       │
│   - Kafka (event streaming)                                               │
│   - Ollama (context analysis)                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Layer 4: AI Foundation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AI FOUNDATION LAYER                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                   Ollama                                     │
│                           Local LLM Runtime                                  │
│                                                                             │
│   Responsibilities:                                                          │
│   - Local model management                                                  │
│   - Inference server                                                        │
│   - Model quantization (Q4, Q5, Q8)                                        │
│   - GPU memory management                                                   │
│                                                                             │
│   Key Features:                                                             │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐     │
│   │  Model Registry │    │  API Server     │    │  Inference      │     │
│   │  - pull()       │    │  - /api/generate│    │  - streaming    │     │
│   │  - list()       │    │  - /api/chat    │    │  - batched      │     │
│   │  - show()       │    │                 │    │                 │     │
│   └─────────────────┘    └─────────────────┘    └─────────────────┘     │
│                                                                             │
│   Supported Models:                                                         │
│   - Llama3 (various sizes)                                                 │
│   - Qwen2.5/Qwen3                                                           │
│   - Mistral                                                                 │
│   - Custom GGUF models                                                      │
│                                                                             │
│   Connected to:                                                             │
│   - Qwen3 (primary model)                                                  │
│   - LangGraph (agent framework)                                            │
│   - Backend API (RAG, Cognitive)                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  Qwen3                                       │
│                            Large Language Model                               │
│                                                                             │
│   Responsibilities:                                                          │
│   - Natural language understanding                                          │
│   - Text generation                                                         │
│   - Code generation                                                          │
│   - Reasoning and analysis                                                  │
│                                                                             │
│   Capabilities:                                                             │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐     │
│   │  NLU            │    │  Generation     │    │  Tool Use       │     │
│   │  - Intent       │    │  - Summarize    │───►│  - Function     │     │
│   │  - Extraction   │    │  - Answer       │    │    calling      │     │
│   │  - Classification│   │  - Compose      │    │  - Reasoning    │     │
│   └─────────────────┘    └─────────────────┘    └─────────────────┘     │
│                                                                             │
│   Integration:                                                              │
│   - Ollama (runtime)                                                        │
│   - LangGraph (agentic workflows)                                           │
│   - RAG Engine (context retrieval)                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                 LangGraph                                   │
│                         Graph-Based Agent Framework                          │
│                              ADR-0052 (Agent)                               │
│                                                                             │
│   Responsibilities:                                                          │
│   - Orchestrating multi-step workflows                                      │
│   - Managing agent state                                                    │
│   - Tool integration                                                        │
│   - Conditional branching                                                   │
│                                                                             │
│   Architecture:                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                                                                     │  │
│   │          ┌──────────┐                                              │  │
│   │          │  State   │◄─────────────────────────────────┐            │  │
│   │          └────┬─────┘                                  │            │  │
│   │               │                                        │            │  │
│   │          ┌────▼─────┐     ┌──────────┐     ┌──────────┐│            │  │
│   │          │  Nodes   │────►│ Check    │────►│  End     ││            │  │
│   │          │ - LLM    │     │ Condition│     │          ││            │  │
│   │          │ - Tool   │     └──────────┘     └──────────┘│            │  │
│   │          │ - Branch │                                  │            │  │
│   │          └──────────┘                                  │            │  │
│   │                                                             │            │  │
│   │          ┌──────────────────────────────────────────────┐ │            │  │
│   │          │                     Edges                    │◄┘            │  │
│   │          │   ┌───────┐    ┌───────┐    ┌───────┐       │            │  │
│   │          │   │ Node1 │───►│ Node2 │───►│ Node3 │── ...  │            │  │
│   │          │   └───────┘    └───────┘    └───────┘       │            │  │
│   │          └──────────────────────────────────────────────┘            │  │
│   │                                                                     │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   Agent Types:                                                              │
│   - Diagnostic Agent (root cause)                                          │
│   - Recommendation Agent (resilience)                                       │
│   - Maintenance Agent (work orders)                                        │
│   - Copilot Agent (Q&A)                                                    │
│                                                                             │
│   Connected to:                                                             │
│   - Ollama/Qwen3 (LLM)                                                    │
│   - Backend Services (API calls)                                           │
│   - Cognitive Twin (reasoning)                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Layer 5: Digital Twin Intelligence

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COGNITIVE TWIN ENGINE                                │
│                              ADR-0055                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                               Cognitive Twin                                 │
│                      Reasoning & Understanding Layer                          │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                        Cognitive Services                            │  │
│   │                                                                     │  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐│  │
│   │  │  Context    │  │  Semantic   │  │   RAG       │  │  Temporal   ││  │
│   │  │  Engine     │◄─┤  Layer      │◄─┤  Engine     │◄─┤  Reasoning  ││  │
│   │  │             │  │             │  │             │  │             ││  │
│   │  │ - Session   │  │ - Entities  │  │ - Retrieve  │  │ - Patterns  ││  │
│   │  │   mgmt      │  │ - Relations │  │ - Generate  │  │ - Sequences ││  │
│   │  │ - History   │  │ - Tags      │  │ - Sources   │  │ - Anomalies ││  │
│   │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘│  │
│   │                                                                     │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   Responsibilities:                                                          │
│   - Maintain conversation context                                           │
│   - Reason about asset relationships                                        │
│   - Generate insights from context                                          │
│   - Learn from historical patterns                                          │
│                                                                             │
│   Connected to:                                                            │
│   - LangGraph (agent reasoning)                                            │
│   - Semantic Layer (knowledge graph)                                       │
│   - RAG Engine (retrieval)                                                 │
│   - Decision Twin (recommendations)                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                               Decision Twin                                  │
│                      Analytics & Recommendation Layer                         │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                      Decision Services                               │  │
│   │                                                                     │  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐│  │
│   │  │  Health     │  │  Resilience │  │  Predictive  │  │  Root Cause ││  │
│   │  │  Engine     │◄─┤  Analysis   │◄─┤  Maintenance │◄─┤  Analysis   ││  │
│   │  │             │  │             │  │              │  │             ││  │
│   │  │ - Scoring   │  │ - Criticality│ │ - Failure    │  │ - Chain     ││  │
│   │  │ - Decay     │  │ - Impact    │  │   prediction │  │   detection ││  │
│   │  │ - Deps      │  │ - Recommend │  │ - Maintenance│  │ - Factors   ││  │
│   │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘│  │
│   │                                                                     │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   Responsibilities:                                                          │
│   - Calculate health scores                                                 │
│   - Identify critical assets                                                │
│   - Predict failures                                                        │
│   - Recommend actions                                                       │
│   - Analyze root causes                                                     │
│                                                                             │
│   Connected to:                                                            │
│   - Cognitive Twin (reasoning)                                             │
│   - Workflow Engine (triggers)                                              │
│   - Work Orders (maintenance)                                               │
│   - Frontend (dashboards)                                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                Workflow                                      │
│                          Orchestration Layer                                 │
│                              ADR-0026                                       │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                     Workflow Types                                   │  │
│   │                                                                     │  │
│   │  ┌─────────────────────────────────────────────────────────────┐  │  │
│   │  │                                                              │  │  │
│   │  │   Incident Response                                          │  │  │
│   │  │   ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐         │  │  │
│   │  │   │Detect │──►│Assess  │──►│Contain │──►│Recover │         │  │  │
│   │  │   │Event  │   │Impact  │   │Issue   │   │Service │         │  │  │
│   │  │   └────────┘   └────────┘   └────────┘   └────────┘         │  │  │
│   │  │                                                              │  │  │
│   │  │   Predictive Maintenance                                      │  │  │
│   │  │   ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐         │  │  │
│   │  │   │Predict │──►│Schedule│──►│Dispatch│──►│Complete│         │  │  │
│   │  │   │Failure │   │Work    │   │Tech    │   │& Record│         │  │  │
│   │  │   └────────┘   └────────┘   └────────┘   └────────┘         │  │  │
│   │  │                                                              │  │  │
│   │  │   Scenario Simulation                                        │  │  │
│   │  │   ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐         │  │  │
│   │  │   │Define  │──►│Execute │──►│Analyze │──►│Compare │         │  │  │
│   │  │   │Scenario│   │Sim     │   │Results │   │Outcomes│         │  │  │
│   │  │   └────────┘   └────────┘   └────────┘   └────────┘         │  │  │
│   │  │                                                              │  │  │
│   │  └─────────────────────────────────────────────────────────────┘  │  │
│   │                                                                     │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   Responsibilities:                                                          │
│   - Orchestrate multi-step processes                                        │
│   - Manage state across steps                                               │
│   - Handle exceptions                                                       │
│   - Track process metrics                                                    │
│                                                                             │
│   Connected to:                                                            │
│   - Decision Twin (triggers)                                               │
│   - Work Orders (task management)                                          │
│   - Camunda (external workflows)                                           │
│   - Event Engine (process events)                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                               Work Orders                                   │
│                        Maintenance Management                                │
│                              ADR-0026                                       │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                       Work Order Lifecycle                            │  │
│   │                                                                     │  │
│   │         ┌─────────────────────────────────────────────────────┐   │  │
│   │         │                                                     │   │  │
│   │    ┌────▼────┐    ┌────────┐    ┌────────┐    ┌────────┐      │   │  │
│   │    │ Created │───►│ Planned│───►│Assigned│───►│ In     │      │   │  │
│   │    │         │    │        │    │        │    │Progress│      │   │  │
│   │    └─────────┘    └────────┘    └────────┘    └───┬────┘      │   │  │
│   │         ▲                                           │         │   │  │
│   │         │                                    ┌──────▼──────┐   │   │  │
│   │         │         ┌────────┐    ┌────────┐   │  Completed │   │   │  │
│   │         └─────────│Pending │◄───│Paused  │◄──┤            │   │   │  │
│   │                   │Approval│    │        │   └────────────┘   │   │  │
│   │                   └────────┘    └────────┘                   │   │  │
│   │                                                             │   │  │
│   │         ┌─────────────────────────────────────────────────────┘   │  │
│   │         │                                                       │   │  │
│   │    ┌────▼────┐    ┌────────┐                                    │   │  │
│   │    │Cancelled│    │ On Hold│                                    │   │  │
│   │    └─────────┘    └────────┘                                    │   │  │
│   │                                                                     │  │
│   │         Work Order Types:                                         │  │  │
│   │         - Preventive Maintenance                                   │  │  │
│   │         - Corrective Maintenance                                  │  │  │
│   │         - Predictive Maintenance                                   │  │  │
│   │         - Emergency Repair                                        │  │  │
│   │         - Inspection                                              │  │  │
│   │                                                                     │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   Responsibilities:                                                          │
│   - Create and manage work orders                                           │
│   - Assign technicians                                                      │
│   - Track progress                                                          │
│   - Record completion                                                       │
│   - Generate reports                                                        │
│                                                                             │
│   Connected to:                                                            │
│   - Decision Twin (recommendations)                                         │
│   - Workflow (process)                                                      │
│   - Asset Service (asset info)                                             │
│   - Sensor Service (meter readings)                                         │
│   - Document Service (attachments)                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Complete Integration Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                          COMPLETE DATA FLOW                                  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ GEOSPATIAL FOUNDATION                                                  │ │
│  │                                                                       │ │
│  │  GeoServer ◄────────┐                                                 │ │
│  │       │             │                                                 │ │
│  │       ▼             │                                                 │ │
│  │  GDAL ◄─────────────┼──────────────────────────────┐                  │ │
│  │       │             │                              │                  │ │
│  │       ▼             │                              │                  │ │
│  │  RasterIO ◄─────────┼──────┐                        │                  │ │
│  │       │             │      │                        │                  │ │
│  │       └──────┬──────┘      │                        │                  │ │
│  │              │             │                        │                  │ │
│  │              ▼             │                        │                  │ │
│  │  GeoPandas ◄──┴─────────────┼────────────────────────┘                  │ │
│  │       │                      │                                          │ │
│  └───────┼──────────────────────┼──────────────────────────────────────────┘ │
│          │                      │                                          │
│          │                      ▼                                          │
│          │              ┌──────────────┐                                   │
│          │              │    Kafka     │                                   │
│          │              │   (Events)   │                                   │
│          │              └──────┬───────┘                                   │
│          │                     │                                           │
│          │     ┌───────────────┼───────────────┐                          │
│          │     │               │               │                          │
│          │     ▼               ▼               ▼                          │
│          │  ┌────────┐   ┌──────────┐   ┌──────────┐                      │
│          │  │  NiFi  │──►│ Camunda  │   │  Video   │                      │
│          │  │        │   │          │   │ Pipeline │                      │
│          │  └────────┘   └────┬─────┘   └────┬─────┘                      │
│          │                   │               │                              │
│          │                   │               │                              │
│          │                   │               ▼                              │
│          │                   │        ┌──────────┐                          │
│          │                   │        │ Frigate  │                          │
│          │                   │        │ OpenCV   │                          │
│          │                   │        │ YOLO     │                          │
│          │                   │        │DeepStream│                          │
│          │                   │        └────┬─────┘                          │
│          │                   │             │                                │
│          └───────────────────┴─────────────┼───────────────────────────────┤
│                                              │                               │
│                                              ▼                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ AI FOUNDATION                                                            ││
│  │                                                                          ││
│  │  ┌──────────────────────────────────────────────────────────────────┐   ││
│  │  │                        Ollama (LLM Runtime)                       │   ││
│  │  │                              │                                   │   ││
│  │  │          ┌───────────────────┼───────────────────┐               │   ││
│  │  │          │                   │                   │               │   ││
│  │  │          ▼                   ▼                   ▼               │   ││
│  │  │    ┌──────────┐        ┌──────────┐        ┌──────────┐         │   ││
│  │  │    │  Qwen3   │◄──────►│ LangGraph │◄──────►│ RAG Eng. │         │   ││
│  │  │    │  (LLM)   │        │ (Agents)  │        │(Context) │         │   ││
│  │  │    └──────────┘        └───────────┘        └──────────┘         │   ││
│  │  └──────────────────────────────────────────────────────────────────┘   ││
│  │                                                                          ││
│  └──────────────────────────────────────────────────────────────────────────┘│
│                                              │                               │
│                                              ▼                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ DIGITAL TWIN INTELLIGENCE                                                ││
│  │                                                                          ││
│  │    ┌─────────────────────┐         ┌─────────────────────┐              ││
│  │    │   Cognitive Twin    │◄───────►│   Decision Twin     │              ││
│  │    │                     │         │                     │              ││
│  │    │  - Context          │         │  - Health Engine    │              ││
│  │    │  - Semantics        │         │  - Resilience       │              ││
│  │    │  - RAG              │         │  - Predictive       │              ││
│  │    │  - Temporal         │         │  - Root Cause       │              ││
│  │    └──────────┬──────────┘         └──────────┬──────────┘              ││
│  │               │                               │                         ││
│  │               │                               │                         ││
│  │               │              ┌────────────────┘                         ││
│  │               │              │                                          ││
│  │               │              ▼                                          ││
│  │               │        ┌──────────────┐                                  ││
│  │               │        │  Workflow    │                                  ││
│  │               │        │  Engine      │                                  ││
│  │               │        └──────┬───────┘                                  ││
│  │               │               │                                          ││
│  │               │               ▼                                          ││
│  │               │        ┌──────────────┐                                  ││
│  │               └───────►│ Work Orders  │                                  ││
│  │                        │              │                                  ││
│  │                        │ - Preventive│                                  ││
│  │                        │ - Predictive│                                  ││
│  │                        │ - Corrective│                                  ││
│  │                        │ - Emergency │                                  ││
│  │                        └──────────────┘                                  ││
│  │                                                                          ││
│  └──────────────────────────────────────────────────────────────────────────┘│
│                                              │                               │
│                                              ▼                               │
│                           ┌────────────────────────────────┐               │
│                           │      FRONTEND DASHBOARDS       │               │
│                           │                                │               │
│                           │  ┌─────────┐  ┌─────────────┐ │               │
│                           │  │  Asset  │  │   Health    │ │               │
│                           │  │  Mgmt   │  │  Dashboard  │ │               │
│                           │  └─────────┘  └─────────────┘ │               │
│                           │  ┌─────────┐  ┌─────────────┐ │               │
│                           │  │ Cognitive│  │   Scenario  │ │               │
│                           │  │ Copilot │  │   Studio    │ │               │
│                           │  └─────────┘  └─────────────┘ │               │
│                           │  ┌─────────┐  ┌─────────────┐ │               │
│                           │  │   Map   │  │  Work Order │ │               │
│                           │  │ Views   │  │  Manager    │ │               │
│                           │  └─────────┘  └─────────────┘ │               │
│                           └────────────────────────────────┘               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Integration Dependencies Summary

| From | To | Protocol | Data | Frequency |
|------|-----|---------|------|-----------|
| GeoServer | GDAL | File/Network | Raster/Vector | On-demand |
| GDAL | RasterIO | In-memory | Arrays | Batch |
| GDAL | GeoPandas | In-memory | GeoDataFrame | Batch |
| GeoServer | Frontend | WMS/WFS | Tiles/Features | Interactive |
| GeoPandas | Kafka | TCP | Events | Real-time |
| NiFi | Kafka | TCP | Flows | Real-time |
| Camunda | NiFi | HTTP | Commands | On-demand |
| Frigate | Kafka | MQTT/TCP | Events | Real-time |
| OpenCV | YOLO | In-memory | Frames | Streaming |
| YOLO | DeepStream | CUDA/GPU | Detections | Streaming |
| Ollama | Backend | HTTP | LLM requests | Interactive |
| Qwen3 | Ollama | Internal | Inference | Interactive |
| LangGraph | Ollama | HTTP | LLM calls | Per step |
| LangGraph | Backend | HTTP | Tool calls | Per step |
| Cognitive Twin | LangGraph | Internal | Reasoning | Interactive |
| Decision Twin | Cognitive Twin | Internal | Context | Periodic |
| Workflow | Decision Twin | HTTP | Triggers | Event-driven |
| Work Orders | Workflow | HTTP | Tasks | Transactional |
| Work Orders | Backend | HTTP | CRUD | Transactional |
| Backend | Frontend | REST/WebSocket | JSON | Interactive |
