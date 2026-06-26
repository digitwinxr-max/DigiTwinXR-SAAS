"""
Topology Types

Core data types for infrastructure network topology representation.
Supports electrical grids, water distribution, and transport systems.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class NodeType(str, Enum):
    """Types of nodes in the topology."""
    ASSET = "asset"
    SUBSTATION = "substation"
    PUMP = "pump"
    JUNCTION = "junction"
    STATION = "station"
    GENERATOR = "generator"
    CONSUMER = "consumer"
    RESERVOIR = "reservoir"
    VALVE = "valve"
    CROSSING = "crossing"


class Layer(str, Enum):
    """Infrastructure layers (domains)."""
    ELECTRICAL = "electrical"
    WATER = "water"
    TRANSPORT = "transport"
    GENERIC = "generic"


class Direction(str, Enum):
    """Edge direction types."""
    UNIDIRECTIONAL = "unidirectional"
    BIDIRECTIONAL = "bidirectional"


class FlowType(str, Enum):
    """Flow types by domain."""
    POWER = "power"
    WATER = "water"
    TRAFFIC = "traffic"
    GENERIC = "generic"


class FlowStatus(str, Enum):
    """Flow calculation status."""
    STABLE = "stable"
    OVERLOADED = "overloaded"
    DEGRADED = "degraded"
    BLOCKED = "blocked"


@dataclass
class TopologyNode:
    """
    Represents a node in the infrastructure topology.
    
    A node can be:
    - A physical asset (transformer, pump, intersection)
    - A logical point (junction, substation)
    - A source or sink (generator, reservoir, consumer)
    """
    id: str
    type: str = NodeType.ASSET.value
    layer: str = Layer.GENERIC.value
    metadata: Dict = field(default_factory=dict)
    
    # Optional properties
    capacity: Optional[float] = None
    load: Optional[float] = None
    position: Optional[Dict[str, float]] = None  # x, y coordinates
    
    def __post_init__(self):
        """Validate node properties."""
        if self.type not in [t.value for t in NodeType]:
            self.type = NodeType.ASSET.value
        if self.layer not in [l.value for l in Layer]:
            self.layer = Layer.GENERIC.value
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "layer": self.layer,
            "metadata": self.metadata,
            "capacity": self.capacity,
            "load": self.load,
            "position": self.position,
        }


@dataclass
class TopologyEdge:
    """
    Represents a connection between two nodes in the topology.
    
    Edges have:
    - Directionality (unidirectional or bidirectional)
    - Capacity (max flow)
    - Resistance (flow loss)
    - Flow type (power, water, traffic)
    """
    from_node: str
    to_node: str
    direction: str = Direction.UNIDIRECTIONAL.value
    capacity: float = 1.0
    flow_type: str = FlowType.GENERIC.value
    resistance: float = 0.1
    
    # Optional properties
    length: Optional[float] = None
    current_flow: Optional[float] = None
    utilization: Optional[float] = None
    status: Optional[str] = None
    
    def __post_init__(self):
        """Validate edge properties."""
        if self.direction not in [d.value for d in Direction]:
            self.direction = Direction.UNIDIRECTIONAL.value
        if self.flow_type not in [f.value for f in FlowType]:
            self.flow_type = FlowType.GENERIC.value
    
    @property
    def is_bidirectional(self) -> bool:
        """Check if edge is bidirectional."""
        return self.direction == Direction.BIDIRECTIONAL.value
    
    def effective_capacity(self) -> float:
        """Calculate effective capacity after resistance."""
        return max(0, self.capacity - self.resistance)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "from_node": self.from_node,
            "to_node": self.to_node,
            "direction": self.direction,
            "capacity": self.capacity,
            "flow_type": self.flow_type,
            "resistance": self.resistance,
            "length": self.length,
            "current_flow": self.current_flow,
            "utilization": self.utilization,
            "status": self.status,
        }


@dataclass
class TopologyGraph:
    """
    Represents a complete infrastructure topology.
    
    Contains:
    - nodes: Dictionary of node_id -> TopologyNode
    - edges: List of TopologyEdge connections
    """
    nodes: Dict[str, TopologyNode] = field(default_factory=dict)
    edges: List[TopologyEdge] = field(default_factory=list)
    
    def add_node(self, node: TopologyNode) -> None:
        """Add a node to the graph."""
        self.nodes[node.id] = node
    
    def add_edge(self, edge: TopologyEdge) -> None:
        """Add an edge to the graph."""
        self.edges.append(edge)
    
    def get_node(self, node_id: str) -> Optional[TopologyNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)
    
    def get_edges_from(self, node_id: str) -> List[TopologyEdge]:
        """Get all edges originating from a node."""
        return [e for e in self.edges if e.from_node == node_id]
    
    def get_edges_to(self, node_id: str) -> List[TopologyEdge]:
        """Get all edges targeting a node."""
        return [e for e in self.edges if e.to_node == node_id]
    
    def get_neighbors(self, node_id: str) -> List[str]:
        """Get all neighboring node IDs."""
        neighbors = set()
        for edge in self.edges:
            if edge.from_node == node_id:
                neighbors.add(edge.to_node)
            if edge.to_node == node_id:
                neighbors.add(edge.from_node)
        return list(neighbors)
    
    def node_count(self) -> int:
        """Get number of nodes."""
        return len(self.nodes)
    
    def edge_count(self) -> int:
        """Get number of edges."""
        return len(self.edges)
    
    def get_layer_nodes(self, layer: str) -> List[TopologyNode]:
        """Get all nodes for a specific layer."""
        return [n for n in self.nodes.values() if n.layer == layer]
    
    def get_type_nodes(self, node_type: str) -> List[TopologyNode]:
        """Get all nodes of a specific type."""
        return [n for n in self.nodes.values() if n.type == node_type]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "edges": [e.to_dict() for e in self.edges],
            "node_count": self.node_count(),
            "edge_count": self.edge_count(),
        }


@dataclass
class Path:
    """Represents a path through the topology."""
    nodes: List[str]
    edges: List[TopologyEdge]
    total_capacity: float
    total_resistance: float
    length: float
    
    def to_dict(self) -> Dict:
        return {
            "nodes": self.nodes,
            "edge_count": len(self.edges),
            "total_capacity": self.total_capacity,
            "total_resistance": self.total_resistance,
            "length": self.length,
        }


@dataclass
class FlowResult:
    """Result of flow calculation."""
    status: FlowStatus
    node_loads: Dict[str, float]
    edge_flows: Dict[str, float]
    overloaded_edges: List[str]
    utilization: Dict[str, float]
    total_flow: float
    
    def to_dict(self) -> Dict:
        return {
            "status": self.status.value,
            "node_loads": self.node_loads,
            "edge_flows": self.edge_flows,
            "overloaded_edges": self.overloaded_edges,
            "utilization": self.utilization,
            "total_flow": self.total_flow,
        }
