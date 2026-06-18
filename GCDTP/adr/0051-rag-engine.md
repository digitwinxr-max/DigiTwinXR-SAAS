# ADR-0051: RAG Engine (Retrieval-Augmented Generation)

## Status

Accepted

## Context

The GCDTP platform has achieved perfect Enterprise Grade status with Cognitive Copilot Foundation (ADR-0050). To transform the copilot into a true context-aware AI assistant, we need a RAG Engine.

### Evolution of AI Twin

```
Data Twin
    ↓
Knowledge Twin
    ↓
Contextual AI Twin
```

### Why RAG Follows Semantics

```
Semantic Layer
    ↓
Timeline Replay
    ↓
Digital Logbook
    ↓
Knowledge Repository
    ↓
RAG Engine
```

The Semantic Layer provides entity relationships. RAG retrieves based on these relationships.

### Difference Between Retrieval and Reasoning

| Phase | Description | Example |
|-------|-------------|---------|
| **Retrieval** | Finding relevant context | "Find health data for asset-123" |
| **Reasoning** | Drawing conclusions | "Health is degraded because..." |

RAG handles retrieval. Reasoning is deferred to future LLM integration.

### Explainability via Source Attribution

Every RAG response includes:

- **Sources**: Which chunks were used
- **Relevance**: How relevant each chunk is (0-1)
- **Confidence**: Overall confidence in the answer
- **Traceability**: Query ID for audit

```
Query: "Why is Substation Alpha degraded?"
├─ Health Engine (0.9) → "Health score: 75/100"
├─ Event Engine (0.8) → "2 warnings in past hour"
└─ Timeline Engine (0.6) → "Degradation started 2h ago"
```

### Human-in-the-Loop Philosophy

```
┌─────────────────────────────────────────────┐
│              Human Operator                  │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│          RAG Engine (Explain)               │
│  - Retrieves context                        │
│  - Generates explanations                   │
│  - NO actions                               │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│           All Platform Engines              │
│  - Semantic Layer                           │
│  - Health Engine                            │
│  - Event Engine                             │
│  - Timeline Engine                          │
│  - Logbook Engine                           │
│  - Knowledge Repository                     │
└─────────────────────────────────────────────┘
```

### Why RAG Remains Read-Only

RAG provides **explanations**, not **actions**:

- ✅ Answers questions
- ✅ Explains health status
- ✅ Describes event relationships
- ✅ Shows historical context
- ❌ Creates work orders
- ❌ Modifies assets
- ❌ Triggers alerts
- ❌ Makes decisions

---

## Decision

Implement RAG Engine:

```
database/migrations/
└── 043_create_rag_cache.sql

backend/src/models/
├── rag_query.py
├── rag_context_chunk.py
└── rag_answer.py

backend/src/schemas/
└── rag.py

backend/src/services/
└── rag_service.py

backend/src/ai/
├── llm_provider.py
└── template_provider.py

backend/src/routes/
└── rag_routes.py

frontend/src/api/
└── rag.js

frontend/src/pages/
├── RAGWorkbench.jsx
└── RAGWorkbench.css

frontend/src/components/
├── RAGChat.jsx
├── RAGSources.jsx
├── RAGContextPanel.jsx
└── ConfidenceBadge.jsx
```

---

## Architecture

### RAG Query Flow

```
User Query
    ↓
Context Retrieval
├─ Semantic Layer
├─ Health Engine
├─ Event Engine
├─ Timeline Engine
├─ Logbook Engine
└─ Knowledge Repository
    ↓
Context Chunks with Relevance Scores
    ↓
LLM Provider (Template for now)
    ↓
Answer with Sources
    ↓
Audit Storage
```

### LLM Provider Abstraction

```python
class LLMProvider(ABC):
    @abstractmethod
    def generate(context, query) -> Dict:
        pass

# Implementations:
class TemplateProvider(LLMProvider):
    """Current - deterministic templates"""

class OpenAIProvider(LLMProvider):
    """Future - OpenAI GPT"""

class ClaudeProvider(LLMProvider):
    """Future - Anthropic Claude"""
```

---

## Architecture Rules

1. **NO AI agents** - Explanations only
2. **NO autonomous decisions** - Human approval required
3. **NO work orders** - No operational writes
4. **NO event modification** - Read-only
5. **NO health modification** - Read-only
6. **NO automation** - Manual approval
7. **NO notifications** - No alerts
8. **NO predictions** - Current state only
9. **NO embeddings** - Metadata-based retrieval
10. **NO vector databases** - Structured storage only
11. **NO LangGraph** - No workflow orchestration
12. **NO CrewAI** - No agent teams
13. **NO AutoGen** - No multi-agent
14. **NO MCP** - No model context protocol

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/rag/query` | Query RAG engine |
| GET | `/rag/history/{session_id}` | Query history |
| GET | `/rag/sources/{query_id}` | Sources used |
| GET | `/rag/context/{query_id}` | Full context |
| GET | `/rag/models` | Available models |
| GET | `/rag/retrieve` | Retrieve context only |

---

## Questions RAG Can Answer

| Question | Context Sources |
|----------|----------------|
| "Why is this asset degraded?" | Health, Events, Timeline |
| "What events affected this?" | Event Engine |
| "What happened before?" | Timeline Engine |
| "Which SOP addresses this?" | Knowledge Repository |
| "Has this happened before?" | Logbook, Knowledge |
| "What is the health status?" | Health Engine |
| "Who observed this?" | Digital Logbook |

---

## Consequences

### Positive

1. **Context-aware AI** - Explanations grounded in data
2. **Explainability** - Source attribution for every answer
3. **Audit trail** - All queries stored for compliance
4. **Extensibility** - Easy to add new LLM providers
5. **Safety** - Read-only prevents accidents

### Negative

1. **No actions** - Cannot modify system
2. **Template responses** - Limited intelligence
3. **No real LLM** - Placeholder until OpenAI/Claude

### Neutral

1. Read-only
2. Deterministic (for now)
3. Human in the loop
4. Backward compatible

---

## Future Integration Points

1. **TASK 052** - AI Agent Framework
   - Introduces action capability
   - Human-supervised agents
   - Maintains governance

---

## Acceptance Criteria

- [x] Database migration 043
- [x] RAG models
- [x] RAG schemas
- [x] LLM Provider interface
- [x] Template Provider
- [x] RAGService
- [x] RAG routes
- [x] Frontend API client
- [x] RAGWorkbench page
- [x] RAGChat component
- [x] RAGSources component
- [x] RAGContextPanel component
- [x] ConfidenceBadge component
- [x] Backend tests
- [x] Frontend tests
- [x] ADR documentation

---

## Sign-off

**Status:** ✅ COMPLETE
**Platform Status:** Perfect Enterprise Grade with RAG Foundation
**Next:** TASK 052 - AI Agent Framework
