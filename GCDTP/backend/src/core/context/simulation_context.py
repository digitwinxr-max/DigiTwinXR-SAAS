"""
Simulation Context

Global state contract for simulation engines.
Contains graph snapshot, domain config, parameters, constraints, and runtime flags.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from enum import Enum
from copy import deepcopy


class SimulationMode(str, Enum):
    """Simulation execution modes."""
    NORMAL = "normal"
    STRESS_TEST = "stress_test"
    WHAT_IF = "what_if"
    RECOVERY = "recovery"


class SimulationState(str, Enum):
    """Simulation state."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class DomainConfig:
    """Configuration for an infrastructure domain."""
    name: str
    cost_multiplier: float = 1.0
    flow_unit: str = "generic"
    capacity_threshold: float = 0.8
    degradation_threshold: float = 0.8
    overload_threshold: float = 1.0
    custom_params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "cost_multiplier": self.cost_multiplier,
            "flow_unit": self.flow_unit,
            "capacity_threshold": self.capacity_threshold,
            "degradation_threshold": self.degradation_threshold,
            "overload_threshold": self.overload_threshold,
            "custom_params": self.custom_params,
        }


@dataclass
class SimulationConstraints:
    """Constraints for simulation execution."""
    max_hops: int = 100
    max_paths: int = 10
    max_iterations: int = 1000
    timeout_seconds: float = 30.0
    max_load: float = 10000.0
    forbidden_nodes: Set[str] = field(default_factory=set)
    required_nodes: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> Dict:
        return {
            "max_hops": self.max_hops,
            "max_paths": self.max_paths,
            "max_iterations": self.max_iterations,
            "timeout_seconds": self.timeout_seconds,
            "max_load": self.max_load,
            "forbidden_nodes": list(self.forbidden_nodes),
            "required_nodes": list(self.required_nodes),
        }


@dataclass
class RuntimeFlags:
    """Runtime flags for simulation control."""
    debug_mode: bool = False
    validate_inputs: bool = True
    enable_caching: bool = True
    enable_event_bus: bool = True
    strict_mode: bool = False
    trace_enabled: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "debug_mode": self.debug_mode,
            "validate_inputs": self.validate_inputs,
            "enable_caching": self.enable_caching,
            "enable_event_bus": self.enable_event_bus,
            "strict_mode": self.strict_mode,
            "trace_enabled": self.trace_enabled,
        }


@dataclass
class GraphSnapshot:
    """Immutable snapshot of the topology graph."""
    nodes: Dict[str, Any]
    edges: List[Any]
    timestamp: datetime
    checksum: str = ""
    
    @classmethod
    def from_graph(cls, graph: Any) -> "GraphSnapshot":
        """Create snapshot from a topology graph."""
        import hashlib
        import json
        
        nodes_data = {k: v.to_dict() for k, v in graph.nodes.items()}
        edges_data = [e.to_dict() for e in graph.edges]
        
        # Calculate checksum
        content = json.dumps({"nodes": nodes_data, "edges": edges_data}, sort_keys=True)
        checksum = hashlib.md5(content.encode()).hexdigest()
        
        return cls(
            nodes=deepcopy(nodes_data),
            edges=deepcopy(edges_data),
            timestamp=datetime.utcnow(),
            checksum=checksum,
        )
    
    def to_dict(self) -> Dict:
        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "timestamp": self.timestamp.isoformat(),
            "checksum": self.checksum,
        }


class SimulationContext:
    """
    Global state contract for simulation engines.
    
    Provides a consistent interface for all engines to access
    graph state, configuration, and runtime parameters.
    """
    
    def __init__(self):
        # Graph state
        self._graph_snapshot: Optional[GraphSnapshot] = None
        self._original_graph: Any = None
        
        # Configuration
        self.domain: str = "generic"
        self.domain_configs: Dict[str, DomainConfig] = self._default_domain_configs()
        
        # Simulation parameters
        self.mode: SimulationMode = SimulationMode.NORMAL
        self.state: SimulationState = SimulationState.IDLE
        self.iteration: int = 0
        
        # Constraints
        self.constraints = SimulationConstraints()
        
        # Runtime flags
        self.flags = RuntimeFlags()
        
        # Time tracking
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        
        # Results storage
        self._results: Dict[str, Any] = {}
        self._event_log: List[Dict[str, Any]] = []
    
    def set_graph(self, graph: Any) -> None:
        """Set the current topology graph."""
        self._original_graph = graph
        self._graph_snapshot = GraphSnapshot.from_graph(graph)
    
    def get_graph(self) -> Optional[Any]:
        """Get the original graph."""
        return self._original_graph
    
    def get_graph_snapshot(self) -> Optional[GraphSnapshot]:
        """Get the current graph snapshot."""
        return self._graph_snapshot
    
    def set_domain(self, domain: str) -> None:
        """Set the current domain."""
        self.domain = domain
    
    def get_domain_config(self) -> DomainConfig:
        """Get configuration for current domain."""
        return self.domain_configs.get(
            self.domain,
            self.domain_configs["generic"]
        )
    
    def add_domain_config(self, config: DomainConfig) -> None:
        """Add or update a domain configuration."""
        self.domain_configs[config.name] = config
    
    def start(self) -> None:
        """Start simulation."""
        self.state = SimulationState.RUNNING
        self.start_time = datetime.utcnow()
        self.iteration = 0
    
    def pause(self) -> None:
        """Pause simulation."""
        self.state = SimulationState.PAUSED
    
    def resume(self) -> None:
        """Resume simulation."""
        if self.state == SimulationState.PAUSED:
            self.state = SimulationState.RUNNING
    
    def complete(self) -> None:
        """Complete simulation."""
        self.state = SimulationState.COMPLETED
        self.end_time = datetime.utcnow()
    
    def fail(self, error: str) -> None:
        """Mark simulation as failed."""
        self.state = SimulationState.FAILED
        self.end_time = datetime.utcnow()
        self._results["error"] = error
    
    def increment_iteration(self) -> None:
        """Increment simulation iteration."""
        self.iteration += 1
    
    def set_result(self, key: str, value: Any) -> None:
        """Store a simulation result."""
        self._results[key] = value
    
    def get_result(self, key: str, default: Any = None) -> Any:
        """Retrieve a simulation result."""
        return self._results.get(key, default)
    
    def log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log an event to the event log."""
        self._event_log.append({
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "iteration": self.iteration,
        })
    
    def get_event_log(self) -> List[Dict[str, Any]]:
        """Get the event log."""
        return self._event_log.copy()
    
    def get_elapsed_time(self) -> float:
        """Get elapsed simulation time in seconds."""
        if not self.start_time:
            return 0.0
        
        end = self.end_time or datetime.utcnow()
        return (end - self.start_time).total_seconds()
    
    def validate(self) -> List[str]:
        """Validate the simulation context."""
        issues = []
        
        if not self._graph_snapshot:
            issues.append("No graph has been set")
        
        if not self.domain:
            issues.append("No domain has been set")
        
        if self.constraints.max_hops <= 0:
            issues.append("max_hops must be positive")
        
        if self.constraints.max_paths <= 0:
            issues.append("max_paths must be positive")
        
        return issues
    
    def reset(self) -> None:
        """Reset the simulation context."""
        self._graph_snapshot = None
        self._original_graph = None
        self.state = SimulationState.IDLE
        self.iteration = 0
        self.start_time = None
        self.end_time = None
        self._results = {}
        self._event_log = []
    
    @staticmethod
    def _default_domain_configs() -> Dict[str, DomainConfig]:
        """Get default domain configurations."""
        return {
            "generic": DomainConfig(name="generic", flow_unit="units"),
            "electrical": DomainConfig(
                name="electrical",
                cost_multiplier=1.2,
                flow_unit="MW",
                capacity_threshold=0.85,
            ),
            "water": DomainConfig(
                name="water",
                cost_multiplier=1.0,
                flow_unit="m3/h",
                capacity_threshold=0.75,
            ),
            "transport": DomainConfig(
                name="transport",
                cost_multiplier=0.8,
                flow_unit="vehicles/h",
                capacity_threshold=0.70,
            ),
        }
    
    def to_dict(self) -> Dict:
        """Convert context to dictionary."""
        return {
            "domain": self.domain,
            "mode": self.mode.value,
            "state": self.state.value,
            "iteration": self.iteration,
            "constraints": self.constraints.to_dict(),
            "flags": self.flags.to_dict(),
            "graph_snapshot": self._graph_snapshot.to_dict() if self._graph_snapshot else None,
            "elapsed_time": self.get_elapsed_time(),
            "results": self._results,
            "event_count": len(self._event_log),
        }
