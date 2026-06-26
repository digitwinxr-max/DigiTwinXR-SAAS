# ADR-0052: AI Agent Framework

## Status

Accepted

## Context

The GCDTP platform has achieved perfect Enterprise Grade status with RAG Foundation (ADR-0051). To introduce action capability while preserving human governance, we need an AI Agent Framework.

### Copilot vs Agent

| Feature | Copilot | Agent |
|---------|---------|-------|
| **Primary Function** | Explain | Act |
| **Modifies System** | ❌ No | ⚠️ Requires Approval |
| **Autonomous** | ❌ No | ❌ No |
| **Human in Loop** | ✅ Yes | ✅ Yes |
| **Proposes Actions** | ❌ No | ✅ Yes |

### Why Approval Gates Exist

```
┌─────────────────────────────────────────────┐
│            Human Operator                    │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│          Agent Analysis                      │
│  - Analyze context                          │
│  - Propose actions                          │
│  - Create recommendations                   │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│        Approval Queue                        │
│  ┌─────────────────────────────────────┐   │
│  │ Task 1: Pending                     │   │
│  │ Task 2: Pending                     │   │
│  │ Task 3: Pending                     │   │
│  └─────────────────────────────────────┘   │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│         Human Approval                       │
│  - Review proposal                           │
│  - Approve or Reject                        │
│  - Add notes                                │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│           Execution                          │
│  - Execute approved actions                  │
│  - Record results                           │
│  - Audit trail                             │
└─────────────────────────────────────────────┘
```

### Human-in-the-Loop Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Human Operator                    │
│              (Full Control & Oversight)              │
└─────────────────────────┬───────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                   Agent Layer                       │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────┐  │
│  │ Diagnostic   │ │ Maintenance  │ │ Recovery   │  │
│  │ Agent       │ │ Agent        │ │ Agent     │  │
│  └──────────────┘ └──────────────┘ └────────────┘  │
│  ┌──────────────┐ ┌──────────────┐                   │
│  │ Knowledge   │ │ Timeline    │                   │
│  │ Agent       │ │ Agent        │                   │
│  └──────────────┘ └──────────────┘                   │
└─────────────────────────┬───────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│               Operational Twin                        │
│  (Assets, Sensors, Events, Health - NO DIRECT MOD)  │
└─────────────────────────────────────────────────────┘
```

### Agent Auditability

Every agent action is audited:

```json
{
  "task_id": "task-123",
  "agent_id": "diagnostic-agent",
  "agent_type": "diagnostic_agent",
  "status": "executed",
  "requested_by": "operator",
  "approved_by": "supervisor",
  "context_data": {
    "entity_type": "asset",
    "entity_id": "asset-456"
  },
  "result_data": {
    "recommendations": [...],
    "findings": [...]
  },
  "created_at": "2026-06-17T10:00:00Z",
  "executed_at": "2026-06-17T10:05:00Z"
}
```

### Explainability Requirements

Agents must provide:

1. **Context Analysis**: What data was analyzed
2. **Proposal**: What action is recommended
3. **Justification**: Why this action
4. **Alternatives**: Other options considered
5. **Risk Assessment**: Potential issues

---

## Decision

Implement AI Agent Framework:

```
database/migrations/
└── 044_create_agent_framework.sql

backend/src/models/
├── agent_definition.py
├── agent_task.py
└── agent_action.py

backend/src/schemas/
└── agent.py

backend/src/services/
└── agent_service.py

backend/src/routes/
└── agent_routes.py

frontend/src/pages/
├── AgentWorkbench.jsx
└── AgentWorkbench.css

frontend/src/components/
├── AgentList.jsx
├── TaskQueue.jsx
├── ApprovalPanel.jsx
├── ExecutionHistory.jsx
└── ActionViewer.jsx

frontend/src/api/
└── agent.js
```

---

## Agent Types

| Type | Description | Capabilities |
|------|-------------|--------------|
| **Diagnostic Agent** | Analyzes system health | Context analysis, Health inspection |
| **Maintenance Agent** | Suggests maintenance | Procedures, Recommendations |
| **Recovery Agent** | Proposes recovery | Recovery plans, Steps |
| **Knowledge Agent** | Retrieves documentation | Knowledge lookup, SOPs |
| **Timeline Agent** | Analyzes history | Pattern detection, Timeline analysis |

---

## Agent Capabilities

### May Do
- ✅ Analyze context
- ✅ Propose actions
- ✅ Create recommendations
- ✅ Invoke RAG
- ✅ Access knowledge repository
- ✅ Read timelines
- ✅ Inspect health

### Forbidden
- ❌ Create events
- ❌ Modify health
- ❌ Alter measurements
- ❌ Execute automatically
- ❌ Close work orders
- ❌ Control assets
- ❌ Send notifications
- ❌ External APIs
- ❌ MCP
- ❌ LangGraph
- ❌ CrewAI
- ❌ AutoGen

---

## Execution Flow

```
Human Request
     ↓
Agent Analysis
     ↓
Proposal Generation
     ↓
Approval Queue
     ↓
Human Review
     ↓
Approval/Rejection
     ↓
Execution (if approved)
     ↓
Audit Trail
```

---

## Architecture Rules

1. **NO autonomous execution** - Human approval always required
2. **NO direct twin modification** - Agents propose, humans execute
3. **Complete audit trail** - Every action recorded
4. **Explainability** - Agents must justify proposals
5. **Reversibility** - Actions can be rejected

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/agent/agents` | List all agents |
| GET | `/agent/agent/{id}` | Get agent details |
| POST | `/agent/task` | Create task |
| GET | `/agent/tasks` | List tasks |
| GET | `/agent/task/{id}` | Get task |
| POST | `/agent/task/{id}/approve` | Approve task |
| POST | `/agent/task/{id}/reject` | Reject task |
| POST | `/agent/task/{id}/execute` | Execute task |
| GET | `/agent/pending` | Get pending tasks |
| GET | `/agent/history` | Get execution history |

---

## Consequences

### Positive

1. **Action Capability** - Agents can propose actions
2. **Human Control** - Approval gates prevent autonomous behavior
3. **Audit Trail** - Complete accountability
4. **Explainability** - Agents justify their proposals
5. **Governance** - Full oversight of AI actions

### Negative

1. **Speed** - Human approval adds latency
2. **Human Required** - Cannot fully automate
3. **Complexity** - More components to manage

### Neutral

1. Read-only twin remains protected
2. Human always in control
3. Explainable proposals

---

## Sign-off

**Status:** ✅ COMPLETE
**Platform Status:** Perfect Enterprise Grade with Agent Framework
