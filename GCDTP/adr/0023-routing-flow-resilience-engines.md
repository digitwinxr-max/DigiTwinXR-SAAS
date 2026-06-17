# ADR-0023: Routing, Flow, and Resilience Engines

## Status

Accepted

## Context

The Network Topology Engine (ADR-0022) provides the foundation for representing infrastructure networks. However, it lacks:

1. **Routing** - How do we find optimal paths through the network?
2. **Flow Allocation** - How do we distribute load across paths?
3. **Resilience Measurement** - How do we measure network robustness?

These three capabilities are **independent** but work together:

```
┌─────────────────────────────────────────────────────────────────┐
│                 THREE INDEPENDENT ENGINES                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Routing    │  │   Flow      │  │  Resilience │             │
│  │  Engine     │  │   Engine    │  │  Engine     │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│        │                │                │                      │
│        ▼                ▼                ▼                      │
│   "Which path?"    "How much on      "How stable?"             │
│                    each edge?"                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### The Problem

Without routing capability:

```
User: "Find the best route from A to B"
System: "I don't know how to route"

User: "What's the fastest path?"
System: "I only have the graph structure"

User: "Can traffic go through C?"
System: "I have edges but no routing logic"
```

With routing capability:

```
User: "Find the best route from A to B"
System: "Route found: A → X → Y → B (cost: 5.2)"

User: "What's the fastest path?"
System: "Route found: A → Z → B (cost: 3.1) - 2 hops"

User: "Can traffic go through C?"
System: "Yes, there are 3 paths through C"
```

## Decision

Create three separate, independent engines:

```
backend/src/services/routing/
├── routing_types.py      # Route, FlowAllocation, RoutingResult
├── cost_models.py        # Domain-specific cost calculations
├── routing_engine.py     # Dijkstra-based path discovery
├── flow_engine.py        # Load distribution across routes
└── resilience_engine.py  # Network robustness measurement
```

## Module 1: Cost Models

Defines how "distance" behaves across infrastructure types.

### Cost Formula

```
edge_cost = base + resistance_factor + capacity_penalty × domain_factor + load_factor
```

### Domain Multipliers

| Domain | Factor | Reasoning |
|--------|--------|----------|
| Electrical | 1.2 | Power transmission is expensive |
| Water | 1.0 | Baseline |
| Transport | 0.8 | Traffic flows more freely |

### Capacity Penalty

```
High capacity (≥100): 0.1 penalty
Low capacity (≤10): 10.0 penalty
```

## Module 2: Routing Engine

Dijkstra-based path discovery with domain awareness.

### Key Methods

```python
# Find shortest (minimum cost) path
route = routing_engine.find_shortest_path(graph, "source", "dest", domain="electrical")

# Find multiple alternative paths
routes = routing_engine.find_all_paths(graph, "source", "dest", max_paths=10)

# Full routing analysis
result = routing_engine.route(graph, "source", "dest")
```

### Path Selection Criteria

1. **Cost** - Lower cost = better
2. **Capacity** - Higher capacity = better (bottleneck)
3. **Redundancy** - More alternatives = more resilient

## Module 3: Flow Engine

Handles load distribution across routes.

### Allocation Strategies

| Strategy | Description |
|----------|-------------|
| equal | Distribute load equally across routes |
| capacity | Proportional to route capacity |
| cost | Inverse proportional to route cost |

### Overload Detection

```
OVERLOADED: utilization > 100%
DEGRADED: 80% < utilization ≤ 100%
VALID: utilization ≤ 80%
```

## Module 4: Resilience Engine

Measures network robustness under stress.

### Resilience Score

```python
resilience = (
    redundancy × 0.3 +
    capacity_margin × 0.5 +
    stability × 0.2
)
```

### What It Measures

1. **Redundancy** - Number of alternative paths
2. **Capacity Margin** - Available headroom
3. **Stability** - Route characteristics (hops, capacity)

### Critical Element Detection

```python
# Find critical nodes
critical_nodes = resilience_engine.find_critical_nodes(graph)

# Find critical edges (bridges)
critical_edges = resilience_engine.find_critical_edges(graph)
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    TOPOLOGY GRAPH                                  │
│                                                                  │
│    Nodes: [substation, transformer, distribution, consumer]       │
│    Edges: [capacity, resistance, direction, flow_type]            │
│                                                                  │
└────────────────────────────┬────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│   Routing     │  │     Flow      │  │   Resilience  │
│   Engine      │  │    Engine     │  │    Engine     │
├───────────────┤  ├───────────────┤  ├───────────────┤
│ Dijkstra      │  │ Allocation    │  │ Score calc    │
│ K-shortest    │  │ Balancing     │  │ Criticality   │
│ Domain costs   │  │ Overload      │  │ Redundancy    │
└───────────────┘  └───────────────┘  └───────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ROUTING RESULT                                 │
│                                                                  │
│  {                                                              │
│    "source": "substation-1",                                     │
│    "destination": "consumer-5",                                 │
│    "best_route": {                                               │
│      "path": ["substation-1", "dist-1", "consumer-5"],          │
│      "total_cost": 3.2,                                          │
│      "total_capacity": 100                                       │
│    },                                                            │
│    "total_routes_found": 3,                                      │
│    "has_valid_route": true                                        │
│  }                                                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
1. BUILD TOPOLOGY
   Assets + Relationships → TopologyGraph

2. FIND ROUTES
   TopologyGraph + CostModel → Routes

3. ALLOCATE FLOW
   Routes + Load → FlowDistribution

4. MEASURE RESILIENCE
   TopologyGraph + Routes → ResilienceMetrics
```

## Use Cases

### Use Case 1: Power Grid Routing

```python
# Build electrical topology
graph = graph_builder.build(electrical_assets)

# Find best power route
route = routing_engine.find_shortest_path(
    graph,
    "generator-1",
    "substation-5",
    domain="electrical"
)

# Allocate power flow
load = 50.0  # MW
distribution = flow_engine.allocate_flow(route, load)

# Check resilience
metrics = resilience_engine.compute_resilience_score(graph, route)
```

### Use Case 2: Water Distribution

```python
# Find optimal water path
route = routing_engine.find_shortest_path(
    graph,
    "reservoir-1",
    "pump-station-3",
    domain="water"
)

# Allocate flow
distribution = flow_engine.allocate_flow(route, total_flow=1000)  # m³/h
```

### Use Case 3: Traffic Routing

```python
# Find fastest route
route = routing_engine.find_shortest_path(
    graph,
    "station-a",
    "station-b",
    domain="transport"
)

# Distribute traffic across alternatives
routes = routing_engine.find_all_paths(graph, "a", "b", max_paths=5)
distributions = flow_engine.allocate_multi_path_flow(routes, 5000, "capacity")
```

## Consequences

### Positive

1. **Separation of concerns** - Each engine does one thing well
2. **Testability** - Independent engines are easier to test
3. **Flexibility** - Can use engines independently or together
4. **Domain awareness** - Different costs for electrical, water, transport

### Negative

1. **Integration complexity** - Engines must be wired together
2. **Data consistency** - Must ensure flow and resilience use same graph
3. **Performance** - Multiple engines may be slower than combined

### Neutral

1. **No database changes** - Pure Python implementation
2. **In-memory only** - No persistence layer
3. **Ready for extension** - Can add new cost models, allocation strategies

## Independence

These engines are intentionally **NOT merged**:

```
┌─────────────────────────────────────────────────────────────────┐
│                    WHY SEPARATION MATTERS                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   RoutingEngine  ──── Can work alone ──── Just finding paths     │
│   FlowEngine     ──── Can work alone ──── Just allocating load   │
│   ResilienceEngine ── Can work alone ──── Just measuring scores  │
│                                                                  │
│   Combined use is OPTIONAL, not mandatory.                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

This allows:
- Simple routing without flow analysis
- Flow analysis on pre-computed routes
- Resilience scoring without routing

## Constraints Enforced

- **NO AI/ML/LLMs** - Dijkstra algorithm only
- **NO external graph libraries** - Custom implementation
- **NO database writes** - Read-only from operational state
- **NO stateful engines** - Each operation is stateless

## Implementation Checklist

- [x] routing_types.py
- [x] cost_models.py
- [x] routing_engine.py
- [x] flow_engine.py
- [x] resilience_engine.py
- [x] Tests
- [x] ADR documentation
