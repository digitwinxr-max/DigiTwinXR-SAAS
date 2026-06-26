# ADR-0055: Cognitive Twin Engine

**Date:** 2026-06-16  
**Status:** Accepted  
**Author:** GCDTP Platform Team

---

## Context

The GCDTP platform has evolved through multiple stages:

1. **Operational Twin** - Basic asset management
2. **Contextual Twin** - Semantic layer, timeline, logbook, knowledge
3. **Agent Twin** - AI agents with human approval
4. **Predictive Twin** - Failure prediction
5. **Root Cause Twin** - Failure explanation
6. **Cognitive Twin** - Convergence layer

This ADR defines the Cognitive Twin Engine, which serves as the convergence layer that aggregates context from all platform engines.

## Decision

### The Convergence Pattern

The Cognitive Twin is not another engine with new capabilities. It is a **convergence layer** that:

1. **Aggregates** context from all existing engines
2. **Synthesizes** information across sources
3. **Explains** complex relationships
4. **Provides** unified intelligence view

### Platform Engines

The Cognitive Twin integrates with:

| Engine | Purpose | Integration |
|--------|---------|-------------|
| Semantic Layer | Entity relationships | Context retrieval |
| Timeline Replay | Historical events | Time-series context |
| Digital Logbook | Operational notes | Historical context |
| Knowledge Repository | Documented info | Reference context |
| RAG Engine | Similar queries | Query context |
| Predictive Maintenance | Failure prediction | Future context |
| Root Cause Analysis | Failure explanation | Causal context |
| Agent Framework | AI analysis | Agent insights |
| Health Engine | Current health | Status context |
| Event Engine | Active events | Event context |

### Copilot vs Agent vs RAG vs Cognitive Twin

| Feature | Copilot | Agent | RAG | Cognitive Twin |
|---------|---------|-------|-----|---------------|
| **Primary Function** | Explain | Act (approved) | Retrieve | Synthesize |
| **Modifies System** | ❌ No | ⚠️ No | ❌ No | ❌ No |
| **Autonomous** | ❌ No | ❌ No | ❌ No | ❌ No |
| **Human Control** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Data Sources** | Single | Single | Single | All |
| **Synthesis** | ❌ No | ❌ No | ❌ No | ✅ Yes |
| **Confidence** | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes |

### Why Explainability is Mandatory

The Cognitive Twin provides **explainable intelligence**:

1. **Source Attribution** - Every insight traces to specific engines
2. **Confidence Scoring** - Indicates reliability of explanation
3. **Context Weighting** - Shows which sources matter most
4. **Reasoning Chain** - Displays how conclusion was reached

### Why Humans Remain in Control

The Cognitive Twin is **ADVISORY ONLY**:

1. **No Actions** - Cannot modify assets, events, or health
2. **No Automation** - Cannot execute agents automatically
3. **No Work Orders** - Cannot create maintenance tasks
4. **No Notifications** - Cannot send alerts
5. **No Autonomous Decisions** - Always requires human review

Humans remain responsible for all decisions.

## Technical Implementation

### Database Schema

```sql
-- cognitive_sessions: User sessions
-- cognitive_queries: Questions and answers
-- cognitive_context: Aggregated context from all engines
```

### Confidence Calculation

```
Total = Coverage + Weight + Diversity + Relevance

Where:
- Coverage: up to 40% (more context = higher)
- Weight: up to 30% (higher weights = higher)
- Diversity: up to 15% (more source types = higher)
- Relevance: up to 15% (higher relevance = higher)
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/cognitive/session` | POST | Create session |
| `/cognitive/sessions` | GET | List sessions |
| `/cognitive/session/{id}` | GET | Get session |
| `/cognitive/query` | POST | Ask question |
| `/cognitive/history/{id}` | GET | Query history |
| `/cognitive/context/{id}` | GET | Get context |
| `/cognitive/insights` | GET | Recent insights |
| `/cognitive/explanations` | GET | Recent explanations |
| `/cognitive/confidence/{id}` | GET | Confidence score |
| `/cognitive/graph/{id}` | GET | Insight graph |

## Constraints

### STRICTLY FORBIDDEN

- ❌ Modify assets
- ❌ Modify events
- ❌ Modify health
- ❌ Execute agents
- ❌ Create work orders
- ❌ Trigger automation
- ❌ Send notifications
- ❌ Perform autonomous actions
- ❌ LangChain/LangGraph
- ❌ CrewAI/AutoGen
- ❌ External LLM APIs
- ❌ Autonomous reasoning

### MUST REMAIN

- ✅ Read-only explanation
- ✅ Context aggregation
- ✅ Source attribution
- ✅ Confidence scoring
- ✅ Human oversight

## Consequences

### Positive

- Unified intelligence view
- Cross-engine context
- Explainable recommendations
- Confidence transparency
- Human control maintained

### Negative

- No real-time actions
- Depends on other engines
- May have latency
- Complexity in integration

## Metrics

1. **Query Satisfaction** - Are answers helpful?
2. **Confidence Accuracy** - Are confidence scores correct?
3. **Context Coverage** - Are all relevant sources included?
4. **Explanation Quality** - Can users understand explanations?

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-06-16 | 1.0 | Initial version |

---

**End of ADR-0055**
