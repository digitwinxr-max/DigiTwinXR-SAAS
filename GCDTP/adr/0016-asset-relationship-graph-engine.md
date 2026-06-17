# ADR-0016: Asset Relationship Graph Engine

## Status

Accepted

## Context

GCDTP manages assets (sites, buildings, equipment, sensors) that exist in physical and logical relationships:

- **Hierarchical containment**: Site → Building → Equipment → Sensor
- **Dependency relationships**: PowerGrid feeds Facility, Controller controls Motor
- **Monitoring relationships**: Sensor monitors Equipment
- **Connection relationships**: Equipment connected_to Equipment

The current system stores assets as flat entities with no relationships. This limits:

1. **Context awareness** - No understanding of asset dependencies
2. **Cascading impact analysis** - Can't determine what fails when something breaks
3. **System-level reasoning** - Can't understand parent-child asset hierarchies

## Decision

Implement a graph-based relationship system for assets.

### Database Layer

Create `asset_relationships` table:

```sql
CREATE TABLE asset_relationships (
    id UUID PRIMARY KEY,
    parent_asset_id UUID REFERENCES assets(id),
    child_asset_id UUID REFERENCES assets(id),
    relationship_type ENUM('contains', 'connected_to', 'feeds', 'monitors', 'controls'),
    created_at TIMESTAMP,
    
    -- Constraints
    CONSTRAINT no_self_reference CHECK (parent_asset_id != child_asset_id),
    CONSTRAINT unique_relationship UNIQUE (parent_asset_id, child_asset_id, relationship_type)
);
```

### Why Flat Asset Models Are Insufficient

A flat model stores only asset attributes:

```
┌─────────────┐
│   Asset     │
├─────────────┤
│ id          │
│ name        │
│ type        │
│ location    │
└─────────────┘
     │
     │ No relationships
     ▼
┌─────────────┐
│   Asset     │
├─────────────┤
│ id          │
│ name        │
│ type        │
│ location    │
└─────────────┘
```

**Problems with flat model:**

1. **No dependency tracking**: If a sensor fails, what equipment does it affect?
2. **No hierarchy**: What's the parent building of this sensor?
3. **No impact analysis**: If power fails at Site A, what goes down?
4. **Manual correlation**: Users must mentally trace relationships

### Why Graph Structure Is Required for Digital Twins

A digital twin requires understanding **relationships** between assets:

```
                    ┌──────────────┐
                    │  Site Alpha  │
                    └──────┬───────┘
                           │ contains
                    ┌──────▼───────┐
                    │  Building A  │
                    └──────┬───────┘
                           │ contains
              ┌────────────┼────────────┐
              │ contains   │            │ feeds
       ┌──────▼──────┐ ┌──▼───────┐ ┌──▼──────────┐
       │  Equipment   │ │ Controller│ │ PowerGrid   │
       └──────┬──────┘ └──────────┘ └──────┬──────┘
              │ controls                    │
              ▼                            ▼
       ┌──────────────┐            ┌──────────────┐
       │   Motor A    │            │   Facility   │
       └──────────────┘            └──────────────┘
              │ monitors
       ┌──────▼──────┐
       │  Sensor X   │
       └──────────────┘
```

### Relational DB vs Graph Logical Structure

**Relational Database (Physical Storage):**

```
┌─────────────────────────────────────────────────────┐
│              Relational Tables                        │
├─────────────────────────────────────────────────────┤
│  assets          │  asset_relationships            │
│  ─────           │  ──────────────────              │
│  id              │  id                             │
│  name            │  parent_asset_id ─────────┐      │
│  type            │  child_asset_id  ────────┼──┐    │
│  location        │  relationship_type       │  │    │
│                  │  created_at               │  │    │
└──────────────────┘                           │  │    │
                                              │  │    │
          References ─────────────────────────┘  │    │
          Foreign keys ──────────────────────────-┘    │
                                                     │
                                                     ▼
                                          Foreign keys create
                                          relationships in rows
```

**Graph Logical Structure (How We Query):**

```
┌─────────────────────────────────────────────────────┐
│              Graph Traversal                         │
├─────────────────────────────────────────────────────┤
│                                                      │
│   START WITH asset = "Sensor X"                      │
│                                                      │
│   OUT parents() → Building A, Equipment              │
│   OUT parents() OUT parents() → Site Alpha           │
│                                                      │
│   OUT children() → (none - leaf node)               │
│                                                      │
│   IN parents() → Equipment (monitors)               │
│   IN parents() IN parents() → Building A (contains) │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Difference Between Relational and Graph

| Aspect | Relational Model | Graph Model |
|--------|-----------------|-------------|
| **Storage** | Tables with foreign keys | Edge list with node IDs |
| **Query pattern** | JOINs with conditions | Graph traversal |
| **Depth queries** | Expensive with multiple JOINs | Efficient traversal |
| **Cyclic queries** | Complex SQL | Natural for graphs |
| **Path finding** | Recursive CTEs | Simple traversal |

### Why Relationships Unlock New Capabilities

#### 1. Cascading Failures

```
When Sensor X fails:
  
  1. Find parent: Equipment (monitors)
  2. Find parent: Building A (contains)
  3. Find parent: Site Alpha (contains)
  
  → Sensor X monitors Equipment
  → Equipment is in Building A
  → Building A is at Site Alpha
  
  Impact: Limited to Equipment level
  (unless Equipment has no redundancy)
```

#### 2. Dependency-Aware Health

```python
def calculate_aggregate_health(asset_id):
    # Start with direct health
    health = get_direct_health(asset_id)
    
    # Factor in children's health
    children = get_children(asset_id)
    for child in children:
        child_health = calculate_aggregate_health(child)
        # Downstream failures affect upstream
        if child_health == "CRITICAL":
            health *= 0.8
    
    return health
```

#### 3. System-Level Reasoning

```
Question: "What will fail if PowerGrid goes down?"

Query:
  1. Find all assets fed by PowerGrid
  2. Find all assets dependent on those
  3. Recursively find all downstream impacts

Answer:
  - Facility (directly fed)
  - Building A (contains Facility equipment)
  - All Equipment in Building A
  - All Sensors monitoring that Equipment
```

## Relationship Types

### contains

**Description**: Parent contains the child (hierarchical ownership)

**Examples**:
- Site contains Building
- Building contains Equipment
- Equipment contains Sensor

**Inverse**: Implicit (child is contained by parent)

### connected_to

**Description**: Assets are physically or logically connected

**Examples**:
- Network switch connected_to Server
- Pipeline connected_to Valve

**Inverse**: Symmetric (bidirectional)

### feeds

**Description**: Parent provides input/material/energy to child

**Examples**:
- PowerGrid feeds Facility
- Generator feeds Building
- UPS feeds Server

**Inverse**: Could be "receives_from" but we store one direction

### monitors

**Description**: Parent monitors or measures child

**Examples**:
- Sensor monitors Motor
- Camera monitors Area
- FlowMeter monitors Pipeline

**Inverse**: "monitored_by" (not stored separately)

### controls

**Description**: Parent controls or commands child

**Examples**:
- Controller controls Motor
- PLC controls Valve
- Dashboard controls System

**Inverse**: "controlled_by" (not stored separately)

## Graph Output Format

### Hierarchical Structure

```json
{
  "asset_id": "site-alpha-uuid",
  "asset_name": "Site Alpha",
  "asset_type": "site",
  "health_status": "HEALTHY",
  "health_score": 95,
  "children": [
    {
      "asset_id": "building-a-uuid",
      "asset_name": "Building A",
      "asset_type": "building",
      "relationship_type": "contains",
      "health_status": "DEGRADED",
      "health_score": 65,
      "children": [
        {
          "asset_id": "motor-1-uuid",
          "asset_name": "Motor 1",
          "asset_type": "motor",
          "relationship_type": "contains",
          "children": []
        }
      ]
    }
  ],
  "parents": [],
  "depth": 2
}
```

### Why This Format?

1. **Hierarchical**: Natural for "contains" relationships
2. **Recursive**: Children can have their own children
3. **Flat-friendly**: Works for connected_to graphs too
4. **Health-aware**: Each node includes health status

## API Design

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /relationships | Create relationship |
| GET | /relationships | List relationships |
| GET | /relationships/{id} | Get single relationship |
| DELETE | /relationships/{id} | Delete relationship |
| GET | /relationships/graph/{asset_id} | Get full graph |
| GET | /relationships/children/{asset_id} | Get direct children |
| GET | /relationships/parents/{asset_id} | Get direct parents |
| GET | /relationships/types | List available types |

### Query Parameters

```
GET /relationships?parent_asset_id=xxx&relationship_type=contains
GET /relationships/graph/{id}?direction=down&max_depth=10
```

## Consequences

### Positive

1. **Dependency tracking**: Know what affects what
2. **Impact analysis**: Predict cascade effects
3. **Hierarchy navigation**: Understand asset structure
4. **Aggregate health**: Roll up health from children
5. **No external dependencies**: PostgreSQL only

### Negative

1. **Additional complexity**: More tables and code
2. **Cycle prevention**: Must handle/prevent cyclic graphs
3. **Performance**: Deep graph queries can be expensive
4. **Maintenance**: Keep relationships synchronized

### Neutral

1. **Storage overhead**: One row per relationship
2. **Validation**: Must validate asset existence
3. **No graph DB**: Can't do complex graph algorithms

## Why Not External Graph Database?

### Constraints

- No Neo4j or external dependencies
- Must remain PostgreSQL-based

### Rationale

1. **Simplicity**: One database to manage
2. **Consistency**: ACID transactions across all data
3. **Sufficiency**: Most queries work with simple traversal
4. **Cost**: No additional infrastructure

### Future Consideration

If complex graph algorithms are needed later:
```python
# Future: Add graph DB adapter
class GraphDatabaseAdapter:
    def find_shortest_path(self, source, target):
        # Delegate to Neo4j
        pass
```

## Implementation Notes

### Cycle Prevention

```python
def _build_graph_node(self, asset_id, visited, max_depth):
    if asset_id in visited:
        return None  # Prevent cycles
    visited.add(asset_id)
    # ... recurse with visited set
```

### Self-Reference Prevention

```python
# Database constraint
CONSTRAINT no_self_reference CHECK (parent_asset_id != child_asset_id)

# Application validation
if parent_asset_id == child_asset_id:
    raise ValueError("Cannot create self-referencing relationship")
```

### Depth Limiting

```python
def get_graph(self, asset_id, max_depth=10):
    if current_depth >= max_depth:
        return None
    # ... recursive traversal
```

## No AI, No Alerts, No Automation

This ADR creates the **structure** for relationship-based reasoning. It does not:

- Predict failures (requires ML)
- Generate alerts (requires notification system)
- Automate responses (requires workflow engine)
- Analyze patterns (requires analytics)

These capabilities can build on this foundation.

## Implementation Checklist

- [x] Database migration (008_create_asset_relationships.sql)
- [x] AssetRelationship model
- [x] Relationship schemas
- [x] AssetRelationshipService
- [x] Relationship routes
- [x] Frontend API client
- [x] AssetHierarchy page
- [x] Backend tests
- [x] Frontend tests

## Future Considerations

1. **Aggregate health calculation**: Roll up health from children
2. **Impact analysis API**: "What fails if X fails?"
3. **Cycle detection**: Warn when creating cyclic relationships
4. **Bulk relationship creation**: Import from CSV
5. **Relationship templates**: Common patterns (site→building→equipment→sensor)