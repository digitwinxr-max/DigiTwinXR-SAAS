# ADR-0049: Knowledge Repository Engine

## Status

Accepted

## Context

The GCDTP platform has achieved perfect Enterprise Grade status with operational memory (Digital Logbook, ADR-0048). To enable structured documentation, organizational knowledge, and future AI readiness, we need a Knowledge Repository Engine.

### Data vs Information vs Knowledge

| Layer | Description | Example |
|-------|-------------|---------|
| **Data** | Raw facts | Sensor reading: 400V |
| **Information** | Processed data | Voltage above threshold |
| **Knowledge** | Contextualized information | This indicates normal operation |
| **Wisdom** | Applied knowledge | React based on patterns |

### Why Knowledge Precedes RAG

1. **Structure**: Well-organized documents improve retrieval
2. **Metadata**: Categories, tags, and relationships enable filtering
3. **Quality**: Human-curated knowledge is high-quality
4. **Trust**: Verifiable sources build confidence
5. **Context**: Relationships provide context for AI

### Why Repository is NOT AI

This Knowledge Repository:

- ❌ Does NOT generate summaries
- ❌ Does NOT create embeddings
- ❌ Does NOT perform vector search
- ❌ Does NOT reason about content
- ❌ Does NOT answer questions

This Knowledge Repository:

- ✅ Stores document metadata
- ✅ Organizes by category and tags
- ✅ Links related documents
- ✅ Enables filtering and search
- ✅ Builds knowledge graph

### Why Relationships Matter

```
ADR-001 → extends → ADR-002
SOP-101 → references → Manual-201
Incident Report → related_to → Lesson Learned 42
```

Relationships enable:
- Navigation between documents
- Understanding document dependencies
- Building knowledge graphs
- AI grounding in document networks

### How Documents Support Digital Twins

| Document Type | Digital Twin Support |
|--------------|---------------------|
| Manuals | Asset configuration knowledge |
| SOPs | Operational procedures |
| ADRs | Architecture decisions |
| Reports | Historical analysis |
| Lessons Learned | Failure prevention |
| Troubleshooting | Problem resolution |

---

## Decision

Implement Knowledge Repository Engine:

```
database/migrations/
└── 040_create_knowledge_repository.sql

backend/src/models/
├── knowledge_document.py
└── knowledge_reference.py

backend/src/schemas/
└── knowledge.py

backend/src/services/
└── knowledge_service.py

backend/src/routes/
└── knowledge_routes.py

frontend/src/api/
└── knowledge.js

frontend/src/pages/
├── KnowledgeRepository.jsx
└── KnowledgeRepository.css

frontend/src/components/
└── KnowledgeGraph.jsx
```

---

## Data Model

### Document Types

| Type | Description |
|------|-------------|
| `manual` | Equipment and system manuals |
| `sop` | Standard operating procedures |
| `troubleshooting` | Problem resolution guides |
| `adr` | Architecture decision records |
| `report` | Analysis and summary reports |
| `lesson_learned` | Post-incident learnings |
| `reference` | Reference documentation |
| `external` | External documentation links |

### Relationship Types

| Type | Description |
|------|-------------|
| `references` | Document A references B |
| `extends` | Document A extends B |
| `supersedes` | Document A supersedes B |
| `related_to` | General relationship |

---

## Architecture Rules

1. **NO AI** - Pure metadata storage
2. **NO embeddings** - No vector processing
3. **NO vector database** - No specialized storage
4. **NO LLM** - No language model integration
5. **NO inference** - No AI reasoning
6. **NO automatic summarization** - Manual curation only
7. **Relationships are read-only** - After creation, no edits

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/knowledge/documents` | Create document |
| GET | `/knowledge/documents` | List documents |
| GET | `/knowledge/document/{id}` | Get document |
| DELETE | `/knowledge/document/{id}` | Delete document |
| POST | `/knowledge/references` | Create reference |
| GET | `/knowledge/references/{id}` | Get references |
| GET | `/knowledge/search` | Search documents |
| GET | `/knowledge/categories` | Category summary |
| GET | `/knowledge/graph` | Knowledge graph |
| GET | `/knowledge/related/{id}` | Related documents |

---

## Semantic Layer Integration

Knowledge documents can be linked to semantic entities:

```json
{
  "entity_type": "document",
  "entity_id": "doc-123",
  "tags": ["infrastructure", "power", "safety"]
}
```

This enables:
- Cross-referencing documents with assets
- Linking procedures to sensors
- Connecting reports to events

---

## Timeline Integration

Documents can reference timeline frames:

- Troubleshooting guides linked to incident times
- Reports linked to specific analysis periods
- Lessons learned linked to event timelines

---

## Consequences

### Positive

1. **Organization** - Structured documentation
2. **Discoverability** - Easy to find relevant docs
3. **Relationships** - Understanding connections
4. **AI Readiness** - Clean metadata for future AI
5. **Compliance** - Documented procedures

### Negative

1. **Curation** - Manual document entry required
2. **Maintenance** - Keep documents updated
3. **Quality** - Depends on content quality

### Neutral

1. No AI processing
2. No automatic summaries
3. Pure metadata storage
4. Backward compatible

---

## Acceptance Criteria

- [x] Database migration 040
- [x] KnowledgeDocument model
- [x] KnowledgeReference model
- [x] Knowledge schemas
- [x] KnowledgeService
- [x] Knowledge routes
- [x] Frontend API client
- [x] KnowledgeRepository page
- [x] KnowledgeGraph component
- [x] Semantic layer integration
- [x] Timeline integration
- [x] Digital logbook integration
- [x] GeoPortal integration
- [x] Backend tests
- [x] Frontend tests
- [x] ADR documentation

---

## Future Integration Points

1. **RAG Pipeline** - Use metadata for retrieval
2. **Vector Store** - Index document summaries
3. **AI Assistant** - Ground responses in docs
4. **Compliance** - Generate reports

---

## Sign-off

**Status:** ✅ COMPLETE
**Platform Status:** Perfect Enterprise Grade with Knowledge Management
