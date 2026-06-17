# ADR-0022: Network Topology Engine

## Status

Accepted

## Context

After implementing the Resilience Analysis Engine (ADR-0021), the platform has a good understanding of asset criticality and network fragility. However, we need a unified representation of the **physical infrastructure** to support:

1. **Path tracing** - How does flow travel through the network?
2. **Flow simulation** - What happens when load increases?
3. **Multi-domain support** - How do electrical, water, and transport systems differ?

### The Gap

Current architecture is asset-centric:

```
Asset A --depends-on--> Asset B --feeds--> Asset C
```

What we need is topology-centric:

```
Generator --> Substation --> Transformer --> Distribution --> Consumer
    |              |              |              |
  Power         Power          Power          Power
```

### The Transition

```
┌─────────────────────────────────────────────────────────────────┐
│              FROM: Asset Dependency Graph                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Asset-centric view                                             │
│   - Focus on what assets depend on                              │
│   - Logical relationships                                        │
│   - Health propagation                                           │
│                                                                  │
│   Example:                                                       │
│   Transformer A depends on: [Substation X, Power Grid Y]         │
│   Assets affected if A fails: [Building 1, Building 2]            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

                            ↓

┌─────────────────────────────────────────────────────────────────┐
│              TO: Infrastructure Topology Graph                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Infrastructure-centric view                                    │
│   - Focus on how networks are physically connected               │
│   - Directional flow paths                                       │
│   - Capacity and resistance                                       │
│   - Multi-domain support                                         │
│                                                                  │
│   Example:                                                       │
│   Electrical Grid:                                               │
│   Generator(100MW) --> Substation(500MW) --> Transformer(200MW)  │
│         |                  |                    |                │
│      power              power                power               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Decision

Create a Network Topology Engine that provides a unified graph model for infrastructure networks.

### Module Structure

```
backend/src/services/topology/
├── topology_types.py      # Core data types
├── graph_builder.py       # Build graphs from assets
├── flow_models.py         # Physics abstraction
├── topology_engine.py     # Main engine
└── topology_validator.py  # Validation
```

## Core Data Types

### TopologyNode

```python
@dataclass
class TopologyNode:
    id: str                    # Unique identifier
    type: str                 # asset, substation, pump, junction, station
    layer: str                # electrical, water, transport
    metadata: Dict            # Additional properties
    capacity: Optional[float] # Node capacity
    position: Optional[Dict]  # x, y coordinates
```

### TopologyEdge

```python
@dataclass
class TopologyEdge:
    from_node: str            # Source node
    to_node: str             # Target node
    direction: str           # unidirectional / bidirectional
    capacity: float          # Maximum flow
    flow_type: str           # power, water, traffic
    resistance: float        # Flow loss
```

### TopologyGraph

```python
@dataclass
class TopologyGraph:
    nodes: Dict[str, TopologyNode]
    edges: List[TopologyEdge]
```

## Infrastructure Layers

The engine supports multiple infrastructure domains:

### Electrical Layer

```
┌─────────────────────────────────────────────────────────────┐
│  ELECTRICAL GRID                                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Generator ──▶ Substation ──▶ Transformer ──▶ Distribution  │
│    │              │               │               │          │
│  Power          Power           Power           Power        │
│                                                              │
│  Flow type: power                                           │
│  Load metric: MW (megawatts)                                 │
│  Capacity: Thermal limits                                    │
│  Resistance: I²R losses                                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Water Layer

```
┌─────────────────────────────────────────────────────────────┐
│  WATER DISTRIBUTION                                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Reservoir ──▶ Pump Station ──▶ Junction ──▶ Consumers        │
│      │              │              │              │          │
│   Pressure        Pressure       Pressure       Pressure      │
│                                                              │
│  Flow type: water                                            │
│  Load metric: m³/h (cubic meters per hour)                   │
│  Capacity: Pipe diameter                                    │
│  Resistance: Friction loss (Darcy-Weisbach)                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Transport Layer

```
┌─────────────────────────────────────────────────────────────┐
│  TRANSPORT NETWORK                                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Station A ──▶ Junction ──▶ Station B ──▶ Crossing          │
│      │              │              │              │          │
│   Vehicles       Vehicles       Vehicles       Vehicles       │
│                                                              │
│  Flow type: traffic                                          │
│  Load metric: vehicles/hour                                  │
│  Capacity: Lanes × speed limit                               │
│  Resistance: Congestion factor                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Flow Models

### Generic Flow

```python
effective_capacity = capacity - resistance
utilization = load / effective_capacity

# Status thresholds:
# STABLE:    utilization < 0.8
# DEGRADED:  0.8 <= utilization < 1.0
# OVERLOADED: utilization >= 1.0
```

### Electrical Flow

- Tighter margins (0.85 threshold for degradation)
- Power loss modeled as I²R

### Water Flow

- Higher utilization tolerance (0.75 threshold)
- Pressure drop along pipes

### Traffic Flow

- Capacity decreases at high densities
- Congestion factor applied

## Key Capabilities

### Path Tracing

```python
# Find shortest path
path = engine.find_path(graph, "substation-1", "consumer-5")

# Find all paths
paths = engine.find_all_paths(graph, "source", "sink", max_paths=10)

# Get reachable nodes
reachable = engine.get_reachable_nodes(graph, "node-a")

# Get upstream nodes
upstream = engine.get_upstream_nodes(graph, "node-x")

# Get downstream nodes
downstream = engine.get_downstream_nodes(graph, "node-x")
```

### Flow Simulation

```python
# Single source simulation
result = engine.simulate_flow(graph, "generator-1", initial_load=100.0)

# Multi-source simulation
result = engine.simulate_multi_source_flow(
    graph,
    sources={"gen-1": 100.0, "gen-2": 50.0}
)

# Results include:
# - node_loads: Load at each node
# - edge_flows: Flow through each edge
# - overloaded_edges: List of overloaded edges
# - utilization: Per-edge utilization
# - status: STABLE, DEGRADED, or OVERLOADED
```

### Graph Building

```python
# From raw assets
graph = builder.build(raw_assets)

# From separate assets and relationships
graph = builder.build_from_relationships(assets, relationships)

# Merge multiple graphs
merged = builder.merge_graphs([electrical_graph, water_graph])
```

## Validation

```python
validator = TopologyValidator()
result = validator.validate(graph)

# Checks:
# - Empty topology
# - No connectivity
# - Orphan nodes
# - Invalid references
# - Self-loops
# - Duplicate edges
# - Negative capacity
# - High resistance

if not result.valid:
    for issue in result.issues:
        print(f"ERROR: {issue}")
```

## What This Engine Provides

### Foundation for Tasks 23-25

```
TASK 022: Topology Engine (THIS)
    │
    ├── TASK 023: Critical Infrastructure Engine
    │   └── Uses topology for cascading failure analysis
    │
    ├── TASK 024: Network Optimization Engine
    │   └── Uses topology for path optimization
    │
    └── TASK 025: Infrastructure Planning Engine
        └── Uses topology for capacity planning
```

### Multi-Domain Readiness

The same engine supports:

| Domain | Flow Type | Load Metric | Capacity | Resistance |
|--------|-----------|-------------|----------|------------|
| Electrical | power | MW | Thermal limit | I²R loss |
| Water | water | m³/h | Pipe diameter | Friction |
| Transport | traffic | vehicles/h | Lanes × speed | Congestion |

## Consequences

### Positive

1. **Unified representation** - Single model for all infrastructure
2. **Physical accuracy** - Directional, capacity-constrained flows
3. **Multi-domain** - Supports electrical, water, transport
4. **Simulation-ready** - Built for flow analysis
5. **Validation** - Ensures graph correctness

### Negative

1. **Complexity** - More complex than simple dependency graphs
2. **Data requirements** - Needs connection topology data
3. **Coordinate systems** - May need position data for visualization

### Neutral

1. **No database changes** - Pure Python implementation
2. **In-memory graphs** - No persistence layer (yet)
3. **Foundation only** - Doesn't do analysis itself

## Constraints Enforced

- **NO AI/ML/LLMs** - Rule-based algorithms only
- **NO external graph libraries** - Custom BFS/DFS
- **NO Neo4j/Redis** - Standard Python only
- **NO database writes** - Read-only from operational state

## Implementation Checklist

- [x] topology_types.py
- [x] graph_builder.py
- [x] flow_models.py
- [x] topology_engine.py
- [x] topology_validator.py
- [x] Tests
- [x] ADR documentation
