# Viewer Future Compatibility

**Generated:** 2026-06-21
**Repository:** DigiTwinXR-SAAS
**Branch:** feature/tasks-024-029-extensible-architecture
**Phase:** 6 - Future Compatibility

---

## Executive Summary

This document evaluates viewer compatibility with future technologies including video, AI, and timeline features. Evidence is derived from filesystem inspection only. **No code modifications were made.**

---

## Assessment Criteria

| Level | Description |
|-------|-------------|
| 🟢 GREEN | Native support or easy integration |
| 🟡 YELLOW | Possible with moderate effort |
| 🔴 RED | Difficult or not supported |

---

## Phase 1: Video Integration Compatibility

### 1.1 Frigate NVR

| Viewer | Compatibility | Integration Effort | Notes |
|--------|--------------|-------------------|-------|
| MapLibre | 🟡 YELLOW | MEDIUM | Custom overlay layer |
| Cesium | 🟡 YELLOW | MEDIUM | 3D overlay support |
| TerriaJS | 🟢 GREEN | LOW | Video extension exists |
| Kepler | 🔴 RED | HIGH | No video support |

**Analysis:**
- TerriaJS has video extension support
- MapLibre can add video overlay layer
- Cesium supports video as imagery provider
- Kepler has no video support

### 1.2 OpenCV Video Processing

| Viewer | Compatibility | Integration Effort | Notes |
|--------|--------------|-------------------|-------|
| MapLibre | 🟡 YELLOW | MEDIUM | Canvas overlay |
| Cesium | 🟡 YELLOW | MEDIUM | Imagery provider |
| TerriaJS | 🟡 YELLOW | MEDIUM | Custom catalog item |
| Kepler | 🔴 RED | HIGH | No canvas access |

**Analysis:**
- All viewers can display processed video frames
- Requires custom overlay implementation
- Real-time processing challenging

### 1.3 YOLO Object Detection

| Viewer | Compatibility | Integration Effort | Notes |
|--------|--------------|-------------------|-------|
| MapLibre | 🟡 YELLOW | MEDIUM | Marker/image overlay |
| Cesium | 🟡 YELLOW | MEDIUM | Billboard/entity overlay |
| TerriaJS | 🟡 YELLOW | MEDIUM | Custom catalog item |
| Kepler | 🟡 YELLOW | MEDIUM | Icon layer |

**Analysis:**
- All viewers can display detection results
- Bounding boxes can be rendered as overlays
- Real-time updates possible

### 1.4 DeepStream Pipeline

| Viewer | Compatibility | Integration Effort | Notes |
|--------|--------------|-------------------|-------|
| MapLibre | 🟡 YELLOW | MEDIUM | WebSocket + overlay |
| Cesium | 🟡 YELLOW | MEDIUM | WebSocket + overlay |
| TerriaJS | 🟡 YELLOW | MEDIUM | WebSocket + custom item |
| Kepler | 🟡 YELLOW | MEDIUM | WebSocket + layer |

**Analysis:**
- All viewers support WebSocket data
- Real-time overlays require custom implementation
- Stream processing on backend required

---

## Phase 2: AI Feature Compatibility

### 2.1 Cognitive Graph

| Viewer | Compatibility | Integration Effort | Notes |
|--------|--------------|-------------------|-------|
| MapLibre | 🟡 YELLOW | MEDIUM | GeoJSON layer |
| Cesium | 🟡 YELLOW | MEDIUM | Entity layer |
| TerriaJS | 🟢 GREEN | LOW | Catalog item support |
| Kepler | 🟡 YELLOW | MEDIUM | Arc layer |

**Analysis:**
- Graph visualization is possible on all viewers
- TerriaJS has best support for graph-like data
- Requires custom rendering for complex graphs

### 2.2 RAG Context Display

| Viewer | Compatibility | Integration Effort | Notes |
|--------|--------------|-------------------|-------|
| MapLibre | 🟡 YELLOW | MEDIUM | Popup/info panel |
| Cesium | 🟡 YELLOW | MEDIUM | Info box/popup |
| TerriaJS | 🟡 YELLOW | MEDIUM | Feature info panel |
| Kepler | 🟡 YELLOW | MEDIUM | Tooltip support |

**Analysis:**
- All viewers can display context information
- Requires integration with RAG service
- Popup/panel implementation needed

### 2.3 Ollama Local LLM

| Viewer | Compatibility | Integration Effort | Notes |
|--------|--------------|-------------------|-------|
| MapLibre | 🟡 YELLOW | MEDIUM | Backend integration |
| Cesium | 🟡 YELLOW | MEDIUM | Backend integration |
| TerriaJS | 🟡 YELLOW | MEDIUM | Backend integration |
| Kepler | 🟡 YELLOW | MEDIUM | Backend integration |

**Analysis:**
- All viewers are display-only
- AI processing happens in backend
- Frontend integration is API-based

---

## Phase 3: Timeline Feature Compatibility

### 3.1 Timeline Replay

| Viewer | Compatibility | Integration Effort | Notes |
|--------|--------------|-------------------|-------|
| MapLibre | 🟡 YELLOW | MEDIUM | Custom playback control |
| Cesium | 🟢 GREEN | LOW | TimelineController exists |
| TerriaJS | 🟢 GREEN | LOW | TimelineLayerManager exists |
| Kepler | 🟢 GREEN | LOW | TemporalDatasetManager exists |

**Analysis:**
- Cesium, TerriaJS, and Kepler have built-in timeline
- MapLibre requires custom timeline implementation
- All can support historical playback

### 3.2 Digital Logbook Integration

| Viewer | Compatibility | Integration Effort | Notes |
|--------|--------------|-------------------|-------|
| MapLibre | 🟡 YELLOW | MEDIUM | Event markers |
| Cesium | 🟡 YELLOW | MEDIUM | Entity/timeline |
| TerriaJS | 🟢 GREEN | LOW | TimelineLayerManager |
| Kepler | 🟡 YELLOW | MEDIUM | Layer filter |

**Analysis:**
- TerriaJS has best logbook integration
- All viewers can display logbook events
- Requires timeline sync

### 3.3 Historical Playback

| Viewer | Compatibility | Integration Effort | Notes |
|--------|--------------|-------------------|-------|
| MapLibre | 🟡 YELLOW | HIGH | Custom implementation |
| Cesium | 🟢 GREEN | LOW | Built-in clock |
| TerriaJS | 🟢 GREEN | LOW | Time-series support |
| Kepler | 🟢 GREEN | LOW | Temporal layer |

**Analysis:**
- Cesium has best historical playback
- Kepler supports time-based filtering
- MapLibre requires significant custom work

---

## Phase 4: Video Overlay Analysis

### 4.1 Video Overlay Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      VIDEO OVERLAY PIPELINE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Video Source                                                    │
│  ├── Frigate NVR                                               │
│  ├── RTSP Stream                                                │
│  └── File Upload                                                │
│       │                                                          │
│       ▼                                                          │
│  ┌─────────────┐                                                 │
│  │   Backend   │                                                 │
│  │  Processing │                                                 │
│  │ ├── OpenCV  │                                                 │
│  │ ├── YOLO    │                                                 │
│  │ └──DeepStream│                                                │
│  └──────┬──────┘                                                 │
│         │                                                         │
│         ▼                                                         │
│  ┌─────────────┐                                                 │
│  │   WebSocket │                                                 │
│  │   / Streaming│                                                │
│  └──────┬──────┘                                                 │
│         │                                                         │
│         ▼                                                         │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    VIEWER LAYER                            │    │
│  │                                                          │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │    │
│  │  │ MapLibre │ │  Cesium  │ │ TerriaJS │ │  Kepler  │    │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │    │
│  │                                                          │    │
│  │  Video Overlay ──► Canvas/DOM Layer                       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Video Overlay Support by Viewer

| Viewer | Canvas Support | DOM Support | Overlay Complexity |
|--------|---------------|-------------|-------------------|
| MapLibre | ✅ Native | ✅ Native | LOW |
| Cesium | ⚠️ Limited | ✅ Entity | MEDIUM |
| TerriaJS | ⚠️ Via adapter | ✅ Catalog item | MEDIUM |
| Kepler | ❌ Limited | ❌ No | HIGH |

**Analysis:**
- MapLibre has best canvas overlay support
- Cesium supports video as imagery
- TerriaJS can wrap other viewers
- Kepler has limited overlay support

---

## Phase 5: AI Overlay Analysis

### 5.1 AI Detection Overlay

| Viewer | Bounding Box | Heatmap | Trajectory | Point Cloud |
|--------|-------------|---------|------------|------------|
| MapLibre | 🟢 GREEN | 🟢 GREEN | 🟢 GREEN | 🔴 RED |
| Cesium | 🟢 GREEN | 🟢 GREEN | 🟢 GREEN | 🟢 GREEN |
| TerriaJS | 🟡 YELLOW | 🟡 YELLOW | 🟡 YELLOW | 🔴 RED |
| Kepler | 🟢 GREEN | 🟢 GREEN | 🟢 GREEN | 🔴 RED |

**Analysis:**
- All viewers except TerriaJS support AI overlays natively
- Cesium has best 3D point cloud support
- Kepler is optimized for trajectory visualization
- MapLibre has good 2D overlay support

### 5.2 AI Context Overlay

| Viewer | Semantic Graph | RAG Context | Recommendation |
|--------|---------------|-------------|----------------|
| MapLibre | 🟡 YELLOW | 🟡 YELLOW | 🟡 YELLOW |
| Cesium | 🟡 YELLOW | 🟡 YELLOW | 🟡 YELLOW |
| TerriaJS | 🟢 GREEN | 🟡 YELLOW | 🟡 YELLOW |
| Kepler | 🟡 YELLOW | 🟡 YELLOW | 🟡 YELLOW |

**Analysis:**
- All viewers can display AI context via popups/panels
- TerriaJS has best support for semantic data
- Custom implementation required for all

---

## Phase 6: Summary Matrix

### Future Compatibility Summary

| Technology | MapLibre | Cesium | TerriaJS | Kepler |
|-----------|----------|--------|----------|--------|
| **Video** | 🟡 MEDIUM | 🟡 MEDIUM | 🟢 HIGH | 🟡 MEDIUM |
| Frigate | 🟡 MEDIUM | 🟡 MEDIUM | 🟢 HIGH | 🔴 LOW |
| OpenCV | 🟡 MEDIUM | 🟡 MEDIUM | 🟡 MEDIUM | 🔴 LOW |
| YOLO | 🟡 MEDIUM | 🟡 MEDIUM | 🟡 MEDIUM | 🟡 MEDIUM |
| DeepStream | 🟡 MEDIUM | 🟡 MEDIUM | 🟡 MEDIUM | 🟡 MEDIUM |
| **AI** | 🟡 MEDIUM | 🟡 MEDIUM | 🟡 MEDIUM | 🟡 MEDIUM |
| Cognitive | 🟡 MEDIUM | 🟡 MEDIUM | 🟢 HIGH | 🟡 MEDIUM |
| RAG | 🟡 MEDIUM | 🟡 MEDIUM | 🟡 MEDIUM | 🟡 MEDIUM |
| Ollama | 🟡 MEDIUM | 🟡 MEDIUM | 🟡 MEDIUM | 🟡 MEDIUM |
| **Timeline** | 🟡 MEDIUM | 🟢 HIGH | 🟢 HIGH | 🟢 HIGH |
| Replay | 🔴 LOW | 🟢 HIGH | 🟢 HIGH | 🟢 HIGH |
| Logbook | 🟡 MEDIUM | 🟡 MEDIUM | 🟢 HIGH | 🟡 MEDIUM |
| Playback | 🔴 LOW | 🟢 HIGH | 🟢 HIGH | 🟢 HIGH |
| **3D** | 🔴 LOW | 🟢 HIGH | 🟢 HIGH | 🔴 LOW |
| Globe | 🔴 LOW | 🟢 HIGH | 🟢 HIGH | 🔴 LOW |
| Terrain | 🔴 LOW | 🟢 HIGH | 🟢 HIGH | 🔴 LOW |
| 3D Tiles | 🔴 LOW | 🟢 HIGH | 🟢 HIGH | 🔴 LOW |

### Overall Scores

| Viewer | Video | AI | Timeline | 3D | Overall |
|--------|-------|-----|----------|-----|---------|
| MapLibre | 🟡 MEDIUM | 🟡 MEDIUM | 🟡 MEDIUM | 🔴 LOW | 🟡 MEDIUM |
| Cesium | 🟡 MEDIUM | 🟡 MEDIUM | 🟢 HIGH | 🟢 HIGH | 🟢 HIGH |
| TerriaJS | 🟢 HIGH | 🟡 MEDIUM | 🟢 HIGH | 🟢 HIGH | 🟢 HIGH |
| Kepler | 🔴 LOW | 🟡 MEDIUM | 🟢 HIGH | 🔴 LOW | 🟡 MEDIUM |

---

## Phase 7: Recommendations by Use Case

### Video-Heavy Use Case

| Priority | Viewer | Rationale |
|----------|--------|-----------|
| 1 | TerriaJS | Built-in video support |
| 2 | MapLibre | Good canvas overlay |
| 3 | Cesium | Good 3D video |
| 4 | Kepler | No video support |

### AI-Heavy Use Case

| Priority | Viewer | Rationale |
|----------|--------|-----------|
| 1 | Cesium | Best AI overlay support |
| 2 | MapLibre | Good 2D overlay |
| 3 | TerriaJS | Semantic integration |
| 4 | Kepler | Limited AI support |

### Timeline-Heavy Use Case

| Priority | Viewer | Rationale |
|----------|--------|-----------|
| 1 | Cesium | Built-in timeline |
| 2 | TerriaJS | TimelineLayerManager |
| 3 | Kepler | TemporalDatasetManager |
| 4 | MapLibre | Custom timeline needed |

### 3D-Heavy Use Case

| Priority | Viewer | Rationale |
|----------|--------|-----------|
| 1 | Cesium | Industry standard 3D |
| 2 | TerriaJS | Via Cesium adapter |
| 3 | MapLibre | No 3D support |
| 4 | Kepler | No 3D support |

---

## No Code Modifications Made

Per Task 080G constraints, **no code modifications were made**. This is an observation report only.

---

## Next Steps

- Proceed to Phase 7: Recommended Target Architecture
