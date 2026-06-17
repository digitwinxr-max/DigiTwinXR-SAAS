# ADR-0024: Extensible Simulation Architecture

## Status

Accepted

## Context

The current architecture has simulation engines directly implemented:

```python
class RoutingEngine:
    def find_shortest_path(self, graph, start, end):
        # Hardcoded Dijkstra implementation
        ...
```

This creates several problems:

1. **Tight coupling** - Engines are tightly coupled to their implementations
2. **No pluggability** - Can't swap algorithms without modifying engine code
3. **No shared state** - Engines have no context about simulation parameters
4. **Hard-coded domains** - Domain logic is scattered with if statements
5. **Direct coupling** - Engines call each other directly, no event system
6. **Static imports** - Can't hot-swap implementations

## Decision

Introduce a layered, extensible architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXTENSIBLE ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      CORE LAYER                           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │   │
│  │  │ Interfaces  │  │  Strategies │  │   Registry  │      │   │
│  │  │ (Contracts) │  │ (Algorithms)│  │ (Plugins)   │      │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │   │
│  │  ┌─────────────┐  ┌─────────────┐                       │   │
│  │  │   Context   │  │ Event Bus   │                       │   │
│  │  │  (State)    │  │ (Comms)     │                       │   │
│  │  └─────────────┘  └─────────────┘                       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                     DOMAIN LAYER                           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │   │
│  │  │ Electrical  │  │    Water    │  │  Transport  │      │   │
│  │  │   Domain    │  │   Domain    │  │   Domain    │      │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    ENGINE LAYER                           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │   │
│  │  │   Routing   │  │    Flow     │  │  Resilience │      │   │
│  │  │   Engine    │  │   Engine    │  │   Engine    │      │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 1. Core Interfaces (Contracts)

Define "what" engines do, not "how":

```python
class IRoutingEngine(IEngine):
    @abstractmethod
    def find_route(self, graph, start, end, **kwargs) -> Optional[Route]:
        pass

class IFlowEngine(IEngine):
    @abstractmethod
    def simulate_flow(self, graph, route, load, **kwargs) -> FlowResult:
        pass

class IResilienceEngine(IEngine):
    @abstractmethod
    def compute_resilience_score(self, graph, route, **kwargs) -> ResilienceMetrics:
        pass
```

**Why**: Engines can be swapped without changing client code.

## 2. Strategy Pattern (Algorithms)

```python
class RoutingEngine:
    def __init__(self, strategy=None):
        self.strategy = strategy or DijkstraStrategy()

# Pluggable strategies:
DijkstraStrategy()      # Standard shortest path
AStarStrategy()         # Heuristic-guided search
RiskAwareStrategy()     # Failure-aware routing
CostAdaptiveStrategy()  # Load-aware routing
```

**Why**: Swap algorithms without modifying engine code.

## 3. Simulation Context (State)

Global state contract:

```python
class SimulationContext:
    # Graph snapshot (immutable during simulation)
    graph_snapshot: GraphSnapshot
    
    # Domain configuration
    domain: str
    domain_configs: Dict[str, DomainConfig]
    
    # Simulation parameters
    mode: SimulationMode
    constraints: SimulationConstraints
    
    # Runtime flags
    flags: RuntimeFlags
    
    # Event log
    event_log: List[SimulationEvent]
```

**Why**: Engines are "context-aware" - they know simulation parameters.

## 4. Domain Plugins (Extensibility)

Instead of:
```python
if domain == "water":
    # water logic
elif domain == "electrical":
    # electrical logic
```

Use plugins:
```python
class DomainRegistry:
    def get(self, name: str) -> BaseDomainPlugin:
        return self._domains[name]()

# Register plugins
registry.register("electrical", ElectricalDomain)
registry.register("water", WaterDomain)
registry.register("transport", TransportDomain)

# Use
domain = registry.get("electrical")
cost = domain.compute_cost(edge)
```

**Why**: Add new domains without modifying existing code.

## 5. Event Bus (Communication)

Instead of direct calls:
```python
# Before: Direct coupling
routing_result = routing_engine.find_route(...)
flow_result = flow_engine.allocate_flow(routing_result, load)
resilience = resilience_engine.compute_score(...)
```

Use events:
```python
# After: Event-driven
event_bus.publish(
    EventType.ROUTE_FOUND,
    source="routing_engine",
    data={"route": route}
)

# Subscribe
event_bus.subscribe(
    [EventType.ROUTE_FOUND],
    callback=on_route_found
)
```

**Why**: Loose coupling, replay capability, SCADA-like debugging.

## 6. Engine Registry (Hot-Swapping)

```python
registry = get_registry()

# Register engines
registry.register(
    "routing",
    DijkstraRoutingEngine,
    name="dijkstra",
    default=True
)

registry.register(
    "routing", 
    AStarRoutingEngine,
    name="astar"
)

# Use default
engine = registry.create("routing")

# Use specific
engine = registry.create("routing", name="astar")
```

**Why**: A/B testing, multiple implementations, hot-swapping.

## Architecture Benefits

### Decoupling

```
┌─────────────────────────────────────────────────────────────────┐
│                       BEFORE vs AFTER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  BEFORE:                                                         │
│                                                                  │
│  RoutingEngine ──calls──> FlowEngine ──calls──> ResilienceEngine │
│       │                     │                      │             │
│   Hardcoded             Hardcoded              Hardcoded        │
│                                                                  │
│  AFTER:                                                           │
│                                                                  │
│  RoutingEngine ──publishes──> EventBus ──dispatches──> Subscribers │
│       │                                                         │
│   Strategy                                                       │
│   Pattern                                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Testability

- Mock interfaces instead of implementations
- Test strategies independently
- Test engines with mock contexts
- Event replay for debugging

### Extensibility

| Extension Point | How |
|---------------|-----|
| New routing algorithm | Implement `IStrategy` |
| New domain | Implement `BaseDomainPlugin` |
| New engine | Implement `IEngine` interface |
| New event type | Add to `EventType` enum |

## Consequences

### Positive

1. **Loose coupling** - Engines communicate via events/interfaces
2. **Testability** - Mock interfaces, isolated strategies
3. **Extensibility** - Plugins, hot-swapping
4. **Debugging** - Event replay, time-travel simulation
5. **Flexibility** - Multiple algorithm implementations

### Negative

1. **Complexity** - More indirection layers
2. **Performance** - Interface calls add overhead
3. **Learning curve** - More concepts to understand

### Neutral

1. **More files** - Architecture requires more structure
2. **More abstractions** - Need to balance granularity

## File Structure

```
backend/src/core/
├── interfaces/
│   ├── base.py          # IEngine, IStrategy
│   ├── routing.py       # IRoutingEngine
│   ├── flow.py          # IFlowEngine
│   └── resilience.py    # IResilienceEngine
├── strategies/
│   └── routing_strategies.py  # Dijkstra, A*, etc.
├── context/
│   └── simulation_context.py  # Global state
├── events/
│   └── event_bus.py          # Event system
├── registry/
│   └── engine_registry.py    # Hot-swapping

backend/src/domains/
├── base_domain.py         # BaseDomainPlugin
├── domain_registry.py     # Domain registry
├── electrical/
│   └── electrical_domain.py
├── water/
│   └── water_domain.py
└── transport/
    └── transport_domain.py
```

## Implementation Checklist

- [x] Core interfaces
- [x] Strategy implementations
- [x] Simulation context
- [x] Event bus
- [x] Engine registry
- [x] Domain plugins
- [x] Updated routing engine with strategy pattern
- [x] ADR documentation

## Future Extensions

### Planned

- [ ] Add more routing strategies (Bidirectional Dijkstra, Contraction Hierarchies)
- [ ] Add domain-specific validators
- [ ] Add persistence layer for contexts
- [ ] Add distributed simulation support

### Possible

- [ ] Graphical strategy configuration
- [ ] Strategy comparison benchmarking
- [ ] Automatic strategy selection based on graph characteristics
