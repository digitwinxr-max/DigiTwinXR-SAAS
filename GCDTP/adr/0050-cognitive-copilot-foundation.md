# ADR-0050: Cognitive Copilot Foundation

## Status

Accepted

## Context

The GCDTP platform has achieved perfect Enterprise Grade status with Knowledge Management (ADR-0049). To enable AI-powered explanations and context aggregation, we need a Cognitive Copilot Foundation.

### AI Terminology

| Term | Description | Example |
|------|-------------|---------|
| **Copilot** | AI assistant that provides explanations | "Here is the health status..." |
| **Agent** | AI that performs actions | "I will restart the asset..." |
| **Autonomous AI** | AI that makes decisions | "I have decided to shut down..." |

### Why Explanations Precede Decisions

1. **Trust**: Users need to understand AI reasoning
2. **Control**: Humans should approve actions
3. **Audit**: We need to know why decisions were made
4. **Safety**: Prevent harmful autonomous actions
5. **Compliance**: Explainable AI for regulations

### Why Copilot is Read-Only

This Cognitive Copilot:

- ❌ Does NOT perform actions
- ❌ Does NOT modify the system
- ❌ Does NOT make decisions
- ❌ Does NOT trigger alerts
- ❌ Does NOT control assets

This Cognitive Copilot:

- ✅ Provides explanations
- ✅ Aggregates context
- ✅ Summarizes data
- ✅ Shows relationships
- ✅ Guides operators

### Why AI Should Consume Context First

```
Context Sources:
- Asset Engine → Asset metadata
- Health Engine → Health status
- Event Engine → Active events
- Timeline Engine → Historical state
- Logbook Engine → Human observations
- Knowledge Repository → Documentation
- Semantic Layer → Entity relationships
```

Context enables:
- Accurate explanations
- Relevant suggestions
- Grounded responses
- Reduced hallucinations

---

## Decision

Implement Cognitive Copilot Foundation:

```
database/migrations/
└── 042_create_copilot_sessions.sql

backend/src/models/
├── copilot_session.py
└── copilot_message.py

backend/src/schemas/
└── copilot.py

backend/src/services/
└── copilot_service.py

backend/src/routes/
└── copilot_routes.py

frontend/src/api/
└── copilot.js

frontend/src/pages/
├── CognitiveCopilot.jsx
└── CognitiveCopilot.css

frontend/src/components/
├── CopilotChat.jsx
├── ContextPanel.jsx
├── MessageBubble.jsx
└── SessionList.jsx
```

---

## Architecture

### Session Management

- Create sessions for conversations
- Store messages in chronological order
- Track context across queries

### Context Bundle

Aggregates data from all engines:

```json
{
  "entity_type": "asset",
  "entity_id": "asset-001",
  "asset": { ... },
  "health": { ... },
  "events": [ ... ],
  "sensors": [ ... ],
  "timeline": [ ... ],
  "logbook": [ ... ],
  "knowledge": [ ... ],
  "semantic": { ... },
  "summary": "..."
}
```

### Deterministic Templates

**IMPORTANT**: NO LLM integration yet.

Responses are template-based:
- Asset summary → Asset template
- Health status → Health template
- Events list → Events template
- Suggestions → Rule-based suggestions

---

## Architecture Rules

1. **NO LLM** - No language model integration
2. **NO embeddings** - No vector processing
3. **NO actions** - Read-only explanations only
4. **NO decisions** - No autonomous behavior
5. **NO automation** - Human in the loop
6. **Deterministic** - Template-based responses

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/copilot/session` | Create session |
| GET | `/copilot/sessions` | List sessions |
| GET | `/copilot/session/{id}` | Get session |
| POST | `/copilot/query` | Query copilot |
| GET | `/copilot/history/{id}` | Get history |
| GET | `/copilot/context/{type}/{id}` | Get context |
| GET | `/copilot/messages/{id}` | Get messages |

---

## Future Integration Points

1. **LLM Integration** - Connect to OpenAI/Claude
2. **RAG Pipeline** - Use knowledge context
3. **Vector Store** - Semantic search
4. **Action Framework** - Execute approved actions

---

## Consequences

### Positive

1. **Explainability** - AI provides context
2. **Trust** - Users understand AI responses
3. **Safety** - No autonomous actions
4. **Compliance** - Human oversight maintained
5. **Foundation** - Ready for future AI

### Negative

1. **Limited Responses** - Template-only
2. **No Actions** - Cannot modify system
3. **No Learning** - Static templates

### Neutral

1. Read-only
2. Deterministic
3. Human in the loop
4. Backward compatible

---

## Acceptance Criteria

- [x] Database migration 042
- [x] CopilotSession model
- [x] CopilotMessage model
- [x] Copilot schemas
- [x] CopilotService
- [x] Copilot routes
- [x] Frontend API client
- [x] CognitiveCopilot page
- [x] CopilotChat component
- [x] ContextPanel component
- [x] MessageBubble component
- [x] SessionList component
- [x] GeoPortal integration
- [x] Timeline integration
- [x] Knowledge integration
- [x] Backend tests
- [x] Frontend tests
- [x] ADR documentation

---

## Sign-off

**Status:** ✅ COMPLETE
**Platform Status:** Perfect Enterprise Grade with AI Foundation
