# ADR-0025: Operational Timeline Engine

## Status

Accepted

## Context

GCDTP has implemented:

```
TASK 021: Simulation Engine
TASK 022: Topology Engine
TASK 023: Routing / Flow / Resilience Engines
TASK 024: Extensible Architecture
```

Now we need to answer:

```
┌─────────────────────────────────────────────────────────────────┐
│                    OPERATIONAL QUESTIONS                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  What happened?     ──► Event recording                          │
│  What changed?     ──► Snapshot comparison                      │
│  What was the sequence? ──► Timeline ordering                   │
│  How did failures propagate? ──► Causal chains                 │
│  What if alternate response? ──► Branch replay                  │
│  Can we replay?   ──► Replay engine                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

This becomes the foundation for:

- Incident investigation
- Root-cause analysis
- Timeline playback
- Forensic simulation
- Training scenarios
- Time-travel digital twin capabilities

## Decision

Create the Operational Timeline Engine:

```
backend/src/services/timeline/
├── timeline_types.py          # TimelineEvent, Snapshot, Segment
├── timeline_engine.py         # Main coordinator
├── event_recorder.py          # EventBus subscription
├── snapshot_manager.py        # State capture/restore
├── replay_engine.py           # Time-travel playback
├── timeline_query_engine.py   # Query capabilities
├── diff_engine.py            # Snapshot comparison
├── timeline_validator.py      # Validation
└── __init__.py
```

## Core Components

### 1. Timeline Types

```python
@dataclass
class TimelineEvent:
    event_id: str
    timestamp: datetime
    event_type: TimelineEventType
    source_engine: str
    entity_id: str
    payload: Dict
    severity: Severity
    metadata: Dict

@dataclass
class TimelineSnapshot:
    snapshot_id: str
    timestamp: datetime
    graph_snapshot: Dict
    asset_states: Dict
    flow_states: List
    resilience_state: ResilienceState

@dataclass
class ReplaySession:
    session_id: str
    speed: float
    current_index: int
    state: ReplayState
    is_branch: bool
```

### 2. Event Recorder

Black box recorder for the system:

```python
class EventRecorder:
    def start_recording(self):
        # Subscribe to EventBus
        
    def stop_recording(self):
        # Return recorded events
        
    def record_event(self, event_type, source_engine, entity_id):
        # Manually record event
```

**Recorded Events:**
- NODE_FAILED, NODE_RECOVERED, NODE_DEGRADED
- EDGE_FAILED, EDGE_RECOVERED, EDGE_OVERLOADED
- FLOW_CHANGED, LOAD_INCREASED, LOAD_DECREASED
- ROUTE_CHANGED, ROUTE_FOUND, ROUTE_FAILED
- BOTTLENECK_DETECTED
- RECOVERY_STARTED, RECOVERY_COMPLETED

### 3. Snapshot Manager

State capture and restore:

```python
class SnapshotManager:
    def capture_snapshot(self, graph, asset_states, flow_states):
        # Capture current state
        
    def restore_snapshot(self, snapshot_id):
        # Restore to saved state
        
    def compare_snapshots(self, id_a, id_b):
        # Compare two snapshots
        
    def prune_snapshots(self, keep_count=10):
        # Clean up old snapshots
```

### 4. Replay Engine

Digital Twin Time Machine:

```python
class ReplayEngine:
    def play(self): ...
    def pause(self): ...
    def resume(self): ...
    def stop(self): ...
    
    def seek(self, timestamp): ...
    def step_forward(self): ...
    def step_backward(self): ...
    
    def change_speed(self, speed):
        # 0.25x, 0.5x, 1x, 2x, 10x, 100x
        
    def create_branch(self, branch_name):
        # Alternative history support
```

### 5. Timeline Query Engine

Query capabilities:

```python
class TimelineQueryEngine:
    def get_events_between(start_time, end_time)
    def get_events_by_type(event_types)
    def get_events_by_asset(asset_id)
    def get_failures()
    def get_recoveries()
    def get_route_changes()
    def get_flow_anomalies()
    def search(text)
```

### 6. Diff Engine

Snapshot comparison:

```python
class DiffEngine:
    def diff_snapshots(snapshot_a, snapshot_b) -> DiffResult:
        # Nodes added/removed/changed
        # Edges added/removed
        # Asset states changed
        # Flow states changed
        
    def generate_change_report(diff_result) -> str:
        # Human-readable report
```

## Architecture Integration

```
┌─────────────────────────────────────────────────────────────────┐
│                    EVENTBUS INTEGRATION                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  RoutingEngine ──────────────┐                                  │
│  FlowEngine ─────────────────┼──► EventBus ──► EventRecorder     │
│  ResilienceEngine ───────────┘              │                   │
│                                              ▼                   │
│                                    ┌───────────────────┐         │
│                                    │  TimelineEngine   │         │
│                                    └─────────┬─────────┘         │
│                                              │                    │
│                              ┌───────────────┼───────────────┐  │
│                              ▼               ▼               ▼   │
│                        Snapshot      TimelineSegment    Replay   │
│                        Manager         QueryEngine       Engine   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Timeline Event Types

| Category | Event Types |
|----------|-------------|
| Node | NODE_FAILED, NODE_RECOVERED, NODE_DEGRADED |
| Edge | EDGE_FAILED, EDGE_RECOVERED, EDGE_OVERLOADED |
| Flow | FLOW_CHANGED, LOAD_INCREASED, LOAD_DECREASED, BOTTLENECK_DETECTED |
| Route | ROUTE_CHANGED, ROUTE_FOUND, ROUTE_FAILED |
| Analysis | RESILIENCE_UPDATED, CRITICAL_NODE_IDENTIFIED |
| Recovery | RECOVERY_STARTED, RECOVERY_COMPLETED |
| Timeline | SNAPSHOT_CREATED, TIMELINE_STARTED, TIMELINE_STOPPED |

## Replay Capabilities

### Speed Control

| Speed | Use Case |
|-------|----------|
| 0.25x | Detailed analysis |
| 0.5x | Slow review |
| 1x | Real-time playback |
| 2x | Fast forward |
| 10x | Quick overview |
| 100x | Summary mode |

### Branching

```
Timeline
    │
    ├── Branch A (alternate response)
    │     └── What if we chose option B?
    │
    └── Branch B (alternate scenario)
          └── What if the failure was worse?
```

## Use Cases

### Use Case 1: Incident Investigation

```python
# Get timeline for incident
timeline = timeline_engine.get_timeline("incident-123")

# Query for failures
query = TimelineQueryEngine(timeline)
failures = query.get_failures()

# Get causal chain
chain = query.get_causal_chain(failures[0])
```

### Use Case 2: Forensic Analysis

```python
# Compare before and after snapshots
diff = diff_engine.diff_snapshots(snapshot_before, snapshot_after)

# Generate report
report = diff_engine.generate_change_report(diff)
```

### Use Case 3: Training Replay

```python
# Create replay session
session = replay_engine.create_session(incident_segment)

# Set slow speed for training
replay_engine.change_speed(0.5)

# Step through events
while not session.is_complete:
    event = replay_engine.step_forward()
    # Discuss each event
```

### Use Case 4: What-If Analysis

```python
# Create branch at failure point
branch = replay_engine.create_branch("alternate-response")

# Simulate different response
branch_events = simulate_alternate_response(branch)

# Compare outcomes
original = get_final_state(replay_engine.current_session)
alternate = get_final_state(branch)
```

## Consequences

### Positive

1. **Incident investigation** - Full historical replay
2. **Root cause analysis** - Event chains and causation
3. **Training scenarios** - Replay past incidents
4. **What-if analysis** - Branch and compare
5. **Forensic simulation** - SCADA-like capabilities
6. **Compliance** - Audit trail

### Negative

1. **Storage requirements** - Snapshots take space
2. **Performance overhead** - Recording adds latency
3. **Complexity** - More moving parts

### Neutral

1. **Extends existing EventBus** - Reuses TASK 024 infrastructure
2. **No new databases** - In-memory with optional persistence
3. **Deterministic** - Same input = same output

## Platform Evolution

After TASK 025, GCDTP evolves from:

```
┌─────────────────────────────────────────────────────────────────┐
│                    BEFORE: TASK 024                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Operational Intelligence Platform                               │
│  - Real-time analysis                                           │
│  - Event processing                                              │
│  - Topology management                                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

                        ↓

┌─────────────────────────────────────────────────────────────────┐
│                    AFTER: TASK 025                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Temporal Operational Intelligence Platform                     │
│  - Real-time analysis                                           │
│  - Historical replay                                            │
│  - Forensic simulation                                          │
│  - What-if analysis                                             │
│  - Training capabilities                                        │
│                                                                  │
│  Approaching capabilities of:                                    │
│  - Bentley iTwin (historical replay)                            │
│  - Palantir Foundry (event timelines)                           │
│  - Utility command centers (incident reconstruction)           │
│  - SCADA historians (time-series forensic analysis)             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Acceptance Criteria

- [x] Event recording from EventBus
- [x] Snapshot capture and restore
- [x] Timeline query engine
- [x] Replay engine with speed control
- [x] Snapshot diff and change reports
- [x] Timeline validation
- [x] EventBus integration
- [x] Deterministic replay
- [x] No external dependencies
- [x] Pure Python implementation
- [x] 50+ tests
- [x] ADR documentation
