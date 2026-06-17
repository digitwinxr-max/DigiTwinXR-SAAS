"""
Routing Types

Core data types for routing, flow allocation, and resilience analysis.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class Domain(str, Enum):
    """Infrastructure domains for routing."""
    ELECTRICAL = "electrical"
    WATER = "water"
    TRANSPORT = "transport"
    GENERIC = "generic"


class RouteStatus(str, Enum):
    """Status of a route."""
    VALID = "valid"
    INVALID = "invalid"
    DEGRADED = "degraded"
    OVERLOADED = "overloaded"


@dataclass
class Route:
    """
    Represents a path through the network.
    
    A route is a sequence of nodes from source to destination
    with associated cost and capacity metrics.
    """
    path: List[str]
    total_cost: float
    total_capacity: float
    is_valid: bool = True
    
    # Optional metrics
    hop_count: int = 0
    total_resistance: float = 0.0
    status: RouteStatus = RouteStatus.VALID
    
    def __post_init__(self):
        """Calculate derived fields."""
        self.hop_count = len(self.path) - 1 if self.path else 0
    
    @property
    def average_capacity(self) -> float:
        """Average capacity along the route."""
        if self.hop_count == 0:
            return 0.0
        return self.total_capacity / self.hop_count
    
    @property
    def cost_per_hop(self) -> float:
        """Cost per hop."""
        if self.hop_count == 0:
            return 0.0
        return self.total_cost / self.hop_count
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "total_cost": round(self.total_cost, 4),
            "total_capacity": round(self.total_capacity, 4),
            "is_valid": self.is_valid,
            "hop_count": self.hop_count,
            "total_resistance": round(self.total_resistance, 4),
            "status": self.status.value,
            "average_capacity": round(self.average_capacity, 4),
            "cost_per_hop": round(self.cost_per_hop, 4),
        }


@dataclass
class FlowAllocation:
    """
    Represents flow allocation on an edge.
    
    Tracks load and utilization for a specific edge
    as part of a flow routing.
    """
    edge_id: str
    from_node: str
    to_node: str
    load: float
    utilization: float
    
    # Optional fields
    capacity: float = 0.0
    overflow: float = 0.0
    status: RouteStatus = RouteStatus.VALID
    
    def __post_init__(self):
        """Calculate overflow if overloaded."""
        if self.utilization > 1.0:
            self.status = RouteStatus.OVERLOADED
            self.overflow = (self.utilization - 1.0) * self.capacity if self.capacity > 0 else 0
        elif self.utilization > 0.8:
            self.status = RouteStatus.DEGRADED
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "edge_id": self.edge_id,
            "from_node": self.from_node,
            "to_node": self.to_node,
            "load": round(self.load, 4),
            "utilization": round(self.utilization, 4),
            "capacity": round(self.capacity, 4),
            "overflow": round(self.overflow, 4),
            "status": self.status.value,
        }


@dataclass
class RoutingResult:
    """
    Result of a routing operation.
    
    Contains the best route and all alternative routes
    found between source and destination.
    """
    source: str
    destination: str
    routes: List[Route] = field(default_factory=list)
    best_route: Optional[Route] = None
    
    # Summary metrics
    total_routes_found: int = 0
    has_valid_route: bool = False
    all_costs: List[float] = field(default_factory=list)
    
    def __post_init__(self):
        """Calculate summary metrics."""
        self.total_routes_found = len(self.routes)
        self.has_valid_route = any(r.is_valid for r in self.routes)
        self.all_costs = [r.total_cost for r in self.routes if r.is_valid]
        
        if not self.best_route and self.has_valid_route:
            # Find cheapest valid route
            valid_routes = [r for r in self.routes if r.is_valid]
            if valid_routes:
                self.best_route = min(valid_routes, key=lambda r: r.total_cost)
    
    def get_routes_by_cost(self, limit: int = 10) -> List[Route]:
        """Get routes sorted by cost."""
        return sorted(self.routes, key=lambda r: r.total_cost)[:limit]
    
    def get_routes_by_capacity(self, limit: int = 10) -> List[Route]:
        """Get routes sorted by capacity (descending)."""
        return sorted(self.routes, key=lambda r: r.total_capacity, reverse=True)[:limit]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "source": self.source,
            "destination": self.destination,
            "total_routes_found": self.total_routes_found,
            "has_valid_route": self.has_valid_route,
            "best_route": self.best_route.to_dict() if self.best_route else None,
            "routes": [r.to_dict() for r in self.routes[:10]],  # Limit for readability
            "all_costs": [round(c, 4) for c in self.all_costs],
        }


@dataclass
class FlowDistribution:
    """
    Represents flow distribution across multiple routes.
    
    Used when distributing load across alternative paths.
    """
    source: str
    destination: str
    allocations: List[FlowAllocation] = field(default_factory=list)
    
    # Summary metrics
    total_load: float = 0.0
    max_utilization: float = 0.0
    overloaded_edges: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Calculate summary metrics."""
        if self.allocations:
            self.total_load = sum(a.load for a in self.allocations)
            self.max_utilization = max(a.utilization for a in self.allocations)
            self.overloaded_edges = [a.edge_id for a in self.allocations if a.utilization > 1.0]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "source": self.source,
            "destination": self.destination,
            "total_load": round(self.total_load, 4),
            "max_utilization": round(self.max_utilization, 4),
            "overloaded_edges": self.overloaded_edges,
            "allocations": [a.to_dict() for a in self.allocations],
        }


@dataclass
class ResilienceMetrics:
    """
    Resilience metrics for a route or network.
    
    Measures network robustness under stress.
    """
    resilience_score: float
    redundancy_paths: int
    capacity_margin: float
    stability_score: float
    
    # Detailed metrics
    alternative_routes: int = 0
    bottleneck_capacity: float = 0.0
    average_utilization: float = 0.0
    
    def __post_init__(self):
        """Clamp scores to 0-1 range."""
        self.resilience_score = max(0.0, min(1.0, self.resilience_score))
        self.stability_score = max(0.0, min(1.0, self.stability_score))
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "resilience_score": round(self.resilience_score, 4),
            "redundancy_paths": self.redundancy_paths,
            "capacity_margin": round(self.capacity_margin, 4),
            "stability_score": round(self.stability_score, 4),
            "alternative_routes": self.alternative_routes,
            "bottleneck_capacity": round(self.bottleneck_capacity, 4),
            "average_utilization": round(self.average_utilization, 4),
        }


@dataclass
class NetworkResilienceResult:
    """
    Overall network resilience analysis result.
    """
    graph_id: str
    overall_score: float
    critical_nodes: List[str] = field(default_factory=list)
    critical_edges: List[str] = field(default_factory=list)
    single_points_of_failure: List[str] = field(default_factory=list)
    route_resilience: Dict[str, ResilienceMetrics] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "graph_id": self.graph_id,
            "overall_score": round(self.overall_score, 4),
            "critical_nodes": self.critical_nodes,
            "critical_edges": self.critical_edges,
            "single_points_of_failure": self.single_points_of_failure,
            "route_resilience": {k: v.to_dict() for k, v in self.route_resilience.items()},
        }
