# ADR-0033: Graph Intelligence Layer (Neo4j)

## Status

Accepted

## Context

GCDTP has complex relationships between:
- Assets and their dependencies
- Work orders and assets
- Documents and work orders
- Devices and assets
- Organizations and users

We need graph analytics for:
- Impact analysis
- Dependency chains
- Centrality ranking
- Path analysis

### The Decision

Introduce Neo4j as a **graph analytics engine** while **PostgreSQL remains authoritative** for business logic.

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTEGRATION ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  PostgreSQL (Authoritative)    Neo4j (Analytics)                │
│  ┌─────────────────────┐      ┌─────────────────────┐        │
│  │                     │ Sync │                     │        │
│  │  Business Logic      │ ←──→ │  Graph Projection  │        │
│  │  Data Models        │      │  Analytics         │        │
│  │  Transactions       │      │  Traversal         │        │
│  │                     │      │                     │        │
│  └─────────────────────┘      └─────────────────────┘        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Decision

Create Neo4j Graph Intelligence Layer:

```
backend/src/integrations/neo4j/
├── neo4j_client.py              # Neo4j client
├── graph_types.py              # Core types
├── graph_projection_manager.py  # Projection management
├── graph_sync_engine.py         # PostgreSQL to Neo4j sync
├── graph_query_engine.py        # Query engine
├── centrality_engine.py          # Centrality calculations
├── dependency_engine.py         # Dependency analysis
├── path_analysis_engine.py      # Path analysis
├── graph_validator.py          # Validation
└── __init__.py
```

## Key Principle

**PostgreSQL remains authoritative for all business logic.**

Neo4j provides only:
- Graph projection
- Graph analytics
- Path traversal
- Centrality calculations

No business logic ownership.

## Supported Entity Projections

| Entity | Description |
|--------|-------------|
| Assets | Asset nodes with properties |
| Relationships | Asset connections |
| Work Orders | Work order nodes |
| Documents | Document nodes |
| Devices | Device nodes |
| Users | User nodes |
| Organizations | Organization nodes |
| Timeline Events | Timeline event nodes |

## Graph Query Capabilities

| Capability | Description |
|------------|-------------|
| Neighbor Search | Find connected nodes |
| Dependency Traversal | Trace dependencies |
| Impact Traversal | Find affected entities |
| Ancestor Search | Find upstream nodes |
| Descendant Search | Find downstream nodes |
| Subgraph Extraction | Extract specific subgraphs |

## Path Analysis

| Path Type | Description |
|-----------|-------------|
| Shortest Path | Minimum hops between entities |
| All Paths | All paths between entities |
| Critical Paths | Longest paths without redundancy |
| Dependency Paths | Dependency chains |
| Redundancy Paths | Alternative routes |

## Centrality Metrics

| Metric | Description |
|--------|-------------|
| Degree Centrality | Number of connections |
| Betweenness | Importance as bridge |
| Closeness | Average distance to others |
| Eigenvector | Influence based on neighbors |
| PageRank | Page importance |
| Criticality | Combined ranking |

## Dependency Analysis

| Chain Type | Description |
|------------|-------------|
| Failure Impact | What fails if this fails |
| Cascade | Cascade effects |
| Dependency | Direct dependencies |

## Database Schema

### graph_projection_jobs

```sql
CREATE TABLE graph_projection_jobs (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    entity_type graph_entity_type,
    status projection_status,
    node_count INTEGER,
    relationship_count INTEGER
);
```

## EventBus Integration

Graph events published to Timeline Engine:

- GRAPH_SYNC_STARTED
- GRAPH_SYNC_COMPLETED
- GRAPH_QUERY_EXECUTED
- GRAPH_SNAPSHOT_CREATED

## Consequences

### Positive

1. **Graph analytics** - Analyze complex relationships
2. **Impact analysis** - Find affected entities
3. **Path finding** - Trace connections
4. **Centrality** - Rank by importance
5. **No data ownership** - PostgreSQL remains authoritative

### Negative

1. **Neo4j dependency** - Requires Neo4j deployment
2. **Data duplication** - Data synced to Neo4j
3. **Sync complexity** - Keep graphs in sync

### Neutral

1. **PostgreSQL authoritative** - No business logic changes
2. **Additive only** - Existing features unchanged
3. **Async sync** - Background synchronization

## Acceptance Criteria

- [x] Neo4j client
- [x] Graph projection manager
- [x] Graph sync engine
- [x] Graph query engine
- [x] Centrality engine
- [x] Dependency engine
- [x] Path analysis engine
- [x] Graph validator
- [x] All entity projections
- [x] EventBus integration
- [x] Timeline integration
- [x] Database migration
- [x] 70+ tests
- [x] ADR documentation
