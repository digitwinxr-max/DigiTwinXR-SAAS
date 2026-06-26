# ADR-0046: Unified Semantic Layer

## Status

Accepted

## Context

The GCDTP platform has achieved perfect Enterprise Grade status (10.0/10) with Kepler.gl Analytics (ADR-0045). To enable advanced AI capabilities and prepare for Cognitive Twin (ADR-00XX), we need a unified semantic metadata layer.

### Why Semantics Precede AI

1. **Foundation**: AI requires structured, meaningful data
2. **Quality**: Semantic metadata improves data quality
3. **Interoperability**: Common ontology enables cross-domain AI
4. **Explainability**: Semantic context makes AI decisions interpretable

### Data vs Relationships vs Knowledge

| Layer | Description | Example |
|-------|-------------|---------|
| **Data** | Raw facts | Sensor reading: 400V |
| **Relationships** | Connections | Asset → Sensor (observed_by) |
| **Knowledge** | Meaning + Context | This 400V reading indicates normal operation at a power substation |
| **Wisdom** | Applied knowledge | React to prevent failure based on patterns |

### Why RAG Requires Semantics

1. **Retrieval**: Semantics improve document/vector retrieval
2. **Context**: Semantic relationships provide relevant context
3. ** grounding**: Semantic layer grounds AI to real entities
4. **Accuracy**: Reduces hallucinations by providing factual context

### Why Cognitive Twin Requires Context

1. **Digital Twin Integration**: Links physical assets to AI understanding
2. **Cross-domain Context**: Connects assets, sensors, events, documents
3. **Temporal Awareness**: Timeline entries provide historical context
4. **Actionable Intelligence**: Work orders and health records inform AI

### This Layer Performs No Reasoning

**IMPORTANT**: The semantic layer is metadata only:
- ❌ NO AI inference
- ❌ NO embeddings
- ❌ NO vector search
- ❌ NO LLM integration
- ❌ NO Neo4j/graph database queries

This layer ONLY provides:
- ✅ Entity metadata
- ✅ Tag assignments
- ✅ Relationship definitions
- ✅ Context aggregation
- ✅ Search capabilities

---

## Decision

Implement Unified Semantic Layer:

```
backend/src/models/
├── semantic_entity.py          # Entity metadata
├── semantic_tag.py             # Tag definitions
├── semantic_relationship.py    # Relationship types

backend/src/schemas/
└── semantic.py                 # API schemas

backend/src/services/
└── semantic_service.py         # Pure aggregation service

backend/src/routes/
└── semantic_routes.py          # API endpoints

database/migrations/
└── 038_create_semantic_layer.sql

frontend/src/api/
└── semantic.js                 # Frontend API client

frontend/src/pages/
├── SemanticExplorer.jsx        # Explorer page
└── SemanticExplorer.css       # Styles

frontend/src/components/
└── SemanticGraph.jsx           # Graph visualization
```

---

## Data Model

### Entity Types

| Type | Description |
|------|-------------|
| `asset` | Infrastructure assets |
| `sensor` | Sensor devices |
| `measurement` | Measurement data |
| `event` | System events |
| `health` | Health records |
| `relationship` | Relationship definitions |
| `scenario` | Scenario definitions |
| `recovery` | Recovery procedures |
| `timeline` | Timeline entries |
| `work_order` | Work orders |
| `document` | Documentation |

### Semantic Tags

Common tag categories:
- `voltage`, `temperature`, `criticality`
- `location`, `utility`, `substation`
- `transformer`, `water`, `power`

### Relationship Types

| Type | Description |
|------|-------------|
| `related_to` | General relationship |
| `caused_by` | Causal relationship |
| `depends_on` | Dependency |
| `documented_by` | Documentation |
| `observed_by` | Observation |
| `generated_by` | Generation |

---

## Context Output

```json
{
  "entity": { ... },
  "asset": { ... },
  "sensors": { "entities": [], "count": 0 },
  "events": { "entities": [], "count": 0 },
  "health": { "entities": [], "count": 0 },
  "documents": { "entities": [], "count": 0 },
  "timeline_entries": { "entities": [], "count": 0 },
  "work_orders": { "entities": [], "count": 0 },
  "relationships": []
}
```

---

## Architecture Rules

1. **NO microservices** - Single backend
2. **NO Kafka** - No event streaming
3. **NO AI inference** - Pure metadata
4. **NO Camunda** - No workflow engine
5. **Backward compatibility** - No existing engine changes
6. **Loose coupling** - Standalone module
7. **Timeline integration** - Sync with Timeline Engine

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/semantic/entities` | Create entity |
| GET | `/semantic/entities` | List entities |
| GET | `/semantic/entity/{id}` | Get entity |
| PUT | `/semantic/entity/{id}` | Update entity |
| DELETE | `/semantic/entity/{id}` | Delete entity |
| POST | `/semantic/tags` | Create tag |
| GET | `/semantic/tags/{entity_id}` | Get tags |
| DELETE | `/semantic/tag/{id}` | Delete tag |
| POST | `/semantic/relationships` | Create relationship |
| GET | `/semantic/relationships/{entity_id}` | Get relationships |
| DELETE | `/semantic/relationship/{id}` | Delete relationship |
| GET | `/semantic/search` | Search entities |
| GET | `/semantic/context/{type}/{id}` | Get context |
| GET | `/semantic/graph` | Get semantic graph |
| GET | `/semantic/tags/summary` | Tag summary |

---

## Consequences

### Positive

1. **AI Readiness** - Foundation for future AI/ML
2. **RAG Support** - Enables retrieval-augmented generation
3. **Cognitive Twin** - Prepares for cognitive digital twin
4. **Interoperability** - Common ontology across domains
5. **Explainability** - Semantic context for AI decisions

### Negative

1. **Additional Storage** - Metadata tables
2. **Maintenance** - Tag curation required
3. **Complexity** - Additional layer to manage

### Neutral

1. No existing engine changes
2. FastAPI remains authoritative
3. Backward compatible

---

## Acceptance Criteria

- [x] SemanticEntity model
- [x] SemanticTag model
- [x] SemanticRelationship model
- [x] Database migration 038
- [x] API schemas
- [x] SemanticService
- [x] Semantic routes
- [x] Frontend API client
- [x] SemanticExplorer page
- [x] SemanticGraph component
- [x] GeoPortal integration
- [x] Backend tests
- [x] Frontend tests
- [x] ADR documentation

---

## Future Integration Points

1. **RAG Pipeline** - Use semantic context for retrieval
2. **Vector Store** - Index semantic entities
3. **LLM Integration** - Ground AI responses
4. **Cognitive Twin** - Full entity context

---

## Sign-off

**Status:** ✅ COMPLETE
**Platform Status:** Perfect Enterprise Grade with AI Foundation
