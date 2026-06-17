# ADR-0021: Resilience Analysis Engine

## Status

Accepted

## Context

After implementing the Scenario Simulation Engine (ADR-0019) and Recovery Simulation Engine (ADR-0020), the platform can simulate both failure impacts and recovery strategies. However, operators also need to understand **which assets are most critical** and **which pose the greatest risk** to the network.

### The Problem

**Without resilience analysis:**

```
1. Asset fails
2. Network impacted
3. Response is reactive
4. No understanding of criticality
5. No prioritization
```

**With resilience analysis:**

```
1. Identify critical assets
2. Detect single points of failure
3. Generate recommendations
4. Proactive mitigation
5. Network-wide risk understanding
```

### Health vs Resilience

These are two distinct concepts:

```
┌─────────────────────────────────────────────────────────────┐
│                    HEALTH vs RESILIENCE                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   HEALTH          RESILIENCE                                │
│   Current state   Ability to withstand failures             │
│   0-100 scale     0-100 scale                               │
│   NOW             FUTURE                                    │
│                                                             │
│   Example:         Example:                                  │
│   "Transformer A   "Transformer A has 5 downstream assets   │
│   health is 65"    and no backup - SPOF"                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Health** tells you the current condition.
**Resilience** tells you how well the network can handle failures.

## Decision

Create a Resilience Analysis Engine that evaluates asset importance and network fragility.

### Database Layer

**resilience_analyses** table:

```sql
CREATE TABLE resilience_analyses (
    id UUID PRIMARY KEY,
    asset_id UUID,
    criticality_score FLOAT,      -- 0-100, higher = more critical
    resilience_score FLOAT,       -- 0-100, higher = more resilient
    dependency_count INTEGER,
    upstream_count INTEGER,
    downstream_count INTEGER,
    single_point_of_failure BOOLEAN,
    created_at TIMESTAMP
);
```

**resilience_recommendations** table:

```sql
CREATE TABLE resilience_recommendations (
    id UUID PRIMARY KEY,
    analysis_id UUID,
    recommendation_type VARCHAR,
    priority VARCHAR,
    description TEXT,
    created_at TIMESTAMP
);
```

## Criticality Score

### Formula

```
criticality_score = (upstream × 0.3) + (downstream × 0.4) + 
                    (dependency × 0.2) + (active_events × 0.1)
```

### Weights

| Factor | Weight | Reasoning |
|--------|--------|-----------|
| Downstream | 0.4 | What depends on this matters most |
| Upstream | 0.3 | What this depends on |
| Dependencies | 0.2 | Total complexity |
| Active Events | 0.1 | Current stress factor |

### Levels

| Score Range | Level | Color |
|-------------|-------|-------|
| 0-39 | LOW | Green (#22c55e) |
| 40-69 | MEDIUM | Orange (#f97316) |
| 70-100 | HIGH | Red (#ef4444) |

## Resilience Score

### Formula

```
resilience_score = 100 - dependency_penalty - propagation_penalty - event_penalty
```

### Penalties

| Penalty | Weight | Condition |
|---------|--------|-----------|
| Dependency | 0-40 | Based on dependency count |
| Propagation | 0 or 50 | If SPOF, full penalty |
| Event | 0-25 | Based on active events |

### Levels

| Score Range | Level | Color |
|-------------|-------|-------|
| 70-100 | GOOD | Green (#22c55e) |
| 40-69 | MODERATE | Yellow (#eab308) |
| 0-39 | POOR | Red (#ef4444) |

## Single Point of Failure (SPOF)

### Definition

An asset is a **Single Point of Failure** if removing it would disconnect more than one downstream branch.

### Detection Algorithm

```
1. Get all downstream assets
2. For each immediate downstream:
   - Check if it has other upstream paths
   - If no alternatives, count as unique branch
3. If unique branches > 1, mark as SPOF
```

### Example

```
     Transformer A
          │
    ┌─────┴─────┐
    │           │
  Line 1     Line 2        <- Transformer A is SPOF
    │           │             (2 unique branches)
    │           │
 Building A  Building B
```

```
     Transformer A
          │
    ┌─────┴─────┐
    │           │
  Line 1     Line 2        <- Transformer A is NOT SPOF
    │           │             (redundant paths exist)
    │           │
  Building A  Building B
    │           │
    └─────┬─────┘
          │
      Backup Line
```

## Recommendations

### Types

| Type | Description |
|------|-------------|
| redundancy | Add backup assets/paths |
| monitoring | Increase monitoring frequency |
| backup | Ensure backup systems exist |
| failover | Implement automatic failover |
| maintenance | Schedule preventive maintenance |
| diversification | Diversify suppliers/dependencies |
| reconfiguration | Balance load across assets |
| early_warning | Set up early warning alerts |

### Priorities

| Priority | Trigger |
|----------|---------|
| CRITICAL | SPOF identified |
| HIGH | Criticality ≥ 70 |
| MEDIUM | Resilience < 60 |
| LOW | Informational |

## API Design

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /resilience/analyze/{id} | Analyze single asset |
| POST | /resilience/analyze-network | Analyze all assets |
| GET | /resilience/asset/{id} | Get existing analysis |
| GET | /resilience/top-critical | Get top critical assets |
| GET | /resilience/network | Get network metrics |
| GET | /resilience/recommendations/{id} | Get recommendations |

### Network Response

```json
{
  "total_assets": 50,
  "analyzed_assets": 50,
  "avg_criticality": 45.5,
  "avg_resilience": 72.3,
  "single_points_of_failure": 3,
  "high_criticality_count": 8,
  "medium_criticality_count": 15,
  "low_criticality_count": 27,
  "critical_assets": [...],
  "recommendations_by_priority": {
    "CRITICAL": [...],
    "HIGH": [...],
    "MEDIUM": [...],
    "LOW": [...]
  }
}
```

## Why This Engine Never Modifies Operational State

### Read-Only Analysis

The Resilience Analysis Engine is **read-only** with respect to operational systems:

```
┌─────────────────────────────────────────────────────────────┐
│                 RESILIENCE ENGINE (READ-ONLY)                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   READS FROM:                                               │
│   ✓ assets (metadata only)                                  │
│   ✓ asset_relationships (structure)                         │
│   ✓ asset_health_dependencies (dependencies)                │
│   ✓ events (active event counts)                           │
│                                                             │
│   WRITES TO:                                                │
│   ✓ resilience_analyses (new table)                         │
│   ✓ resilience_recommendations (new table)                 │
│                                                             │
│   NEVER TOUCHES:                                            │
│   ✗ events (live events)                                   │
│   ✗ propagated_events (propagation history)                 │
│   ✗ asset_health (live health state)                        │
│   ✗ scenarios (scenario simulations)                        │
│   ✗ recovery_simulations (recovery simulations)              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Reasons for Isolation

1. **Analysis must not affect reality**: We can't create failures by analyzing them
2. **Separation of concerns**: Analysis is different from operational state
3. **Reproducibility**: Same analysis should produce same results
4. **Auditability**: Know exactly what was analyzed vs what happened
5. **Performance**: No blocking on operational writes

## Digital Twin Architecture

The three simulation/analysis engines form a complete digital twin:

```
┌─────────────────────────────────────────────────────────────┐
│                      DIGITAL TWIN                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Scenario    │  │  Recovery    │  │  Resilience  │       │
│  │  Simulation  │  │  Simulation  │  │  Analysis    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│        │                │                 │                   │
│        ▼                ▼                 ▼                   │
│   "What if?"        "How to fix?"     "What's at risk?"      │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              OPERATIONAL STATE (LIVE)               │    │
│  │                                                     │    │
│  │   assets | health | events | relationships         │    │
│  │                                                     │    │
│  │   (Never modified by simulation/analysis engines)   │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Consequences

### Positive

1. **Prioritization**: Know which assets need most attention
2. **Proactive Mitigation**: Address SPOFs before failures
3. **Risk Visibility**: Network-wide risk understanding
4. **Recommendations**: Actionable improvement suggestions
5. **Historical Tracking**: Track resilience over time

### Negative

1. **Analysis Overhead**: Computation for large networks
2. **Recommendation Quality**: Rule-based, may miss nuanced situations
3. **Static Thresholds**: May not fit all asset types

### Neutral

1. **New Tables**: Added to database schema
2. **Scheduled Analysis**: May need periodic refresh
3. **Separation**: Analysis isolated from operations

## Constraints Enforced

- **NO AI/ML/LLMs**: Rule-based analysis only
- **NO operational writes**: Never touches events, health, scenarios
- **NO external dependencies**: PostgreSQL only
- **NO graph libraries**: Custom BFS/DFS algorithms
- **NO Neo4j/Redis/Kafka**: Standard stack only

## Implementation Checklist

- [x] Database migration (013_create_resilience_analysis.sql)
- [x] ResilienceAnalysis model
- [x] ResilienceRecommendation model
- [x] Resilience schemas
- [x] ResilienceService with calculations
- [x] Resilience routes
- [x] Frontend API client
- [x] ResilienceDashboard page
- [x] CriticalAssetTable component
- [x] ResilienceRadar component
- [x] NetworkRiskSummary component
- [x] Backend tests
- [x] ADR documentation
