# ADR-0054: Root Cause Analysis Engine

**Date:** 2026-06-16  
**Status:** Accepted  
**Author:** GCDTP Platform Team

---

## Context

The GCDTP platform has evolved through multiple stages:

1. **Operational Twin** - Basic asset management
2. **Contextual Twin** - Semantic layer, timeline, logbook
3. **Agent Twin** - AI agents with human approval
4. **Predictive Twin** - Failure prediction (what may happen)
5. **Root Cause Twin** - Root cause analysis (why did it happen)

This ADR defines the Root Cause Analysis (RCA) Engine, which explains WHY failures, health degradation, and propagated impacts occurred.

## Decision

### The Fundamental Question

Every cognitive twin must answer two questions:

| Question | Answered By | Example |
|----------|-------------|---------|
| **What may happen?** | Predictive Engine | "This transformer may fail in 30 days" |
| **Why did it happen?** | Root Cause Analysis | "The transformer failed due to oil degradation" |

### Separation of Concerns

**Predictive Maintenance** → What might fail?  
**Root Cause Analysis** → Why did it fail?

These are complementary but fundamentally different operations:

1. **Prediction is forward-looking** - estimates future states
2. **RCA is backward-looking** - explains past events

### Actions Belong Elsewhere

RCA is **READ ONLY**. It explains WHY, not WHAT TO DO.

| RCA Does | RCA Does NOT |
|----------|--------------|
| ✅ Explains causation | ❌ Modify events |
| ✅ Ranks contributing factors | ❌ Create work orders |
| ✅ Builds causal chains | ❌ Execute agents |
| ✅ Calculates confidence | ❌ Perform automation |
| ✅ References timeline | ❌ Send notifications |
| ✅ Analyzes dependency chains | ❌ Trigger healing |

**Actions are human decisions, not RCA outputs.**

## Technical Implementation

### Database Schema

```sql
-- root_cause_analysis: Analysis records
-- cause_factor: Contributing factors
-- cause_chain: Causal chain links
```

### Analysis Types

| Type | Description |
|------|-------------|
| `failure` | General failure analysis |
| `health_degradation` | Health score decline |
| `dependency_chain` | Dependency-based propagation |
| `event_sequence` | Sequential event analysis |

### Factor Types

| Type | Description | Weight Range |
|------|-------------|--------------|
| `measurement` | Measurement anomalies | 0-1 |
| `event` | Related events | 0-1 |
| `health` | Health history patterns | 0-1 |
| `relationship` | Dependency relationships | 0-1 |
| `timeline` | Timeline patterns | 0-1 |
| `logbook` | Logbook entries | 0-1 |
| `knowledge` | Knowledge base references | 0-1 |

### Confidence Calculation

```
Total = Factor_Score + Chain_Score + Evidence_Score

Where:
- Factor_Score: up to 40% (based on factor count × average weight)
- Chain_Score: up to 30% (based on chain depth)
- Evidence_Score: up to 30% (based on evidence count)
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/root-cause/analyze/{asset_id}` | POST | Run analysis |
| `/root-cause/{id}` | GET | Get analysis |
| `/root-cause/asset/{asset_id}` | GET | Asset history |
| `/root-cause/event/{event_id}` | GET | Event analysis |
| `/root-cause/factors/{id}` | GET | Factor details |
| `/root-cause/chains/{id}` | GET | Chain details |
| `/root-cause/high-confidence` | GET | High confidence |
| `/root-cause/history` | GET | Analysis history |

## Why Explanation Over Automation

### The Trust Problem

Automated root cause can lead to:
- **False confidence** in incorrect causes
- **Over-reliance** on automated systems
- **Loss of domain expertise**

### The Human Factor

Human operators bring:
- **Context** - Understanding of operational history
- **Judgment** - Ability to weigh competing factors
- **Experience** - Recognition of patterns machines miss
- **Accountability** - Responsibility for decisions

### Explanation > Action

RCA provides:
1. **Evidence** - What data supports the cause
2. **Confidence** - How certain is the analysis
3. **Factors** - Ranked list of contributing elements
4. **Chain** - How the cause propagated

Human decides what to do with this information.

## Constraints

### STRICTLY FORBIDDEN

- ❌ Modify events
- ❌ Create work orders
- ❌ Execute agents
- ❌ Perform automation
- ❌ Send notifications
- ❌ Trigger healing
- ❌ ML/LLM reasoning
- ❌ External APIs

### MUST REMAIN

- ✅ Read-only analysis
- ✅ Deterministic calculations
- ✅ Factor ranking
- ✅ Chain reconstruction
- ✅ Confidence scoring
- ✅ Timeline references

## Consequences

### Positive

- Clear separation of analysis vs action
- Full auditability of causes
- Human oversight maintained
- No accidental automation
- Explainable results

### Negative

- Slower response to failures
- Requires human judgment
- May need multiple analyses

## Metrics

1. **Analysis Accuracy** - How often causes are correct
2. **Confidence Calibration** - Are confidence scores accurate?
3. **Factor Relevance** - Are top factors actually relevant?
4. **Chain Completeness** - Are chains fully reconstructed?
5. **Time to Analysis** - How fast is analysis delivered?

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-06-16 | 1.0 | Initial version |

---

**End of ADR-0054**
