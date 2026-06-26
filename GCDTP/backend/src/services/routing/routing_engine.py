"""
Routing Engine

Dijkstra-based path discovery for infrastructure networks.
Finds optimal routes based on cost models.
Now uses Strategy pattern for pluggable algorithms.
"""

import heapq
from typing import Dict, List, Optional, Set, Tuple, Any
from backend.src.services.topology import TopologyGraph, TopologyEdge
from backend.src.services.routing.cost_models import CostModels, get_cost_model
from backend.src.services.routing.routing_types import (
    Route,
    RoutingResult,
    RouteStatus,
)
from backend.src.core.interfaces.routing import IRoutingEngine
from backend.src.core.interfaces.base import EngineMetadata
from backend.src.core.strategies.routing_strategies import (
    DijkstraStrategy,
    BaseRoutingStrategy,
)
from backend.src.core.events import get_event_bus, EventType


class RoutingEngine(IRoutingEngine):
    """
    Dijkstra-based routing engine for finding optimal paths.
    
    Features:
    - Multiple path discovery
    - Domain-specific cost models
    - Capacity-aware routing
    - Alternative route finding
    - Strategy pattern for pluggable algorithms
    """
    
    def __init__(self, strategy: Optional[BaseRoutingStrategy] = None):
        self.cost_model = CostModels()
        self.strategy = strategy or DijkstraStrategy(cost_model=self.cost_model)
    
    # =========================================================================
    # IEngine Implementation
    # =========================================================================
    
    def get_metadata(self) -> EngineMetadata:
        """Get engine metadata."""
        return EngineMetadata(
            name="RoutingEngine",
            version="1.0.0",
            description="Dijkstra-based routing with pluggable strategies",
            capabilities=[
                "find_route",
                "find_all_routes",
                "find_route_with_constraints",
                "get_reachable_nodes"
            ]
        )
    
    def validate_input(self, **kwargs) -> bool:
        """Validate engine input parameters."""
        required = ["graph", "start", "end"]
        return all(k in kwargs for k in required)
    
    def reset(self) -> None:
        """Reset engine state."""
        pass  # Stateless operation
    
    # =========================================================================
    # IRoutingEngine Implementation
    # =========================================================================
    
    def find_route(
        self,
        graph: Any,
        start: str,
        end: str,
        **kwargs
    ) -> Optional[Route]:
        """Find a route from start to end (IRoutingEngine interface)."""
        return self.find_shortest_path(graph, start, end, **kwargs)
    
    def find_all_routes(
        self,
        graph: Any,
        start: str,
        end: str,
        max_routes: int = 10,
        **kwargs
    ) -> List[Route]:
        """Find multiple routes (IRoutingEngine interface)."""
        return self.find_all_paths(graph, start, end, max_paths=max_routes, **kwargs)
    
    def find_route_with_constraints(
        self,
        graph: Any,
        start: str,
        end: str,
        constraints: Dict[str, Any],
        **kwargs
    ) -> Optional[Route]:
        """Find route with constraints (IRoutingEngine interface)."""
        max_hops = constraints.get("max_hops", 100)
        return self.find_path_with_max_hops(graph, start, end, max_hops=max_hops, **kwargs)
    
    def get_reachable_nodes(
        self,
        graph: Any,
        start: str,
        **kwargs
    ) -> List[str]:
        """Get reachable nodes (IRoutingEngine interface)."""
        from backend.src.services.topology import TopologyEngine
        engine = TopologyEngine()
        return list(engine.get_reachable_nodes(graph, start))
    
    # =========================================================================
    # Strategy Management
    # =========================================================================
    
    def set_strategy(self, strategy: BaseRoutingStrategy) -> None:
        """
        Set a new routing strategy at runtime.
        
        Args:
            strategy: New routing strategy
        """
        self.strategy = strategy
        if not strategy.cost_model:
            strategy.cost_model = self.cost_model
    
    def get_strategy_name(self) -> str:
        """Get current strategy name."""
        return self.strategy.get_name()
    
    def find_shortest_path(
        self,
        graph: TopologyGraph,
        start: str,
        end: str,
        domain: str = "generic"
    ) -> Optional[Route]:
        """
        Find the shortest (minimum cost) path between two nodes.
        
        Uses Dijkstra's algorithm with domain-specific costs.
        
        Args:
            graph: The topology graph
            start: Source node ID
            end: Target node ID
            domain: Infrastructure domain
            
        Returns:
            Route object or None if no path exists
        """
        if start not in graph.nodes or end not in graph.nodes:
            return None
        
        # Priority queue: (cost, node, path)
        queue = [(0.0, start, [start])]
        visited: Set[str] = set()
        
        # Edge lookup for fast access
        edge_map = self._build_edge_map(graph)
        
        while queue:
            current_cost, current_node, path = heapq.heappop(queue)
            
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            # Found destination
            if current_node == end:
                edges = self._path_to_edges(graph, path)
                total_capacity = self._compute_path_capacity(graph, path)
                total_resistance = sum(e.resistance for e in edges)
                
                return Route(
                    path=path,
                    total_cost=current_cost,
                    total_capacity=total_capacity,
                    total_resistance=total_resistance,
                    is_valid=True,
                    status=RouteStatus.VALID
                )
            
            # Explore neighbors
            if current_node in edge_map:
                for edge in edge_map[current_node]:
                    neighbor = edge.to_node
                    
                    if neighbor in visited:
                        continue
                    
                    edge_cost = self.cost_model.compute_cost(edge, domain)
                    new_cost = current_cost + edge_cost
                    new_path = path + [neighbor]
                    
                    heapq.heappush(queue, (new_cost, neighbor, new_path))
        
        # No path found
        return None
    
    def find_all_paths(
        self,
        graph: TopologyGraph,
        start: str,
        end: str,
        domain: str = "generic",
        max_paths: int = 10,
        max_cost_ratio: float = 2.0
    ) -> List[Route]:
        """
        Find multiple paths between two nodes.
        
        Args:
            graph: The topology graph
            start: Source node ID
            end: Target node ID
            domain: Infrastructure domain
            max_paths: Maximum number of paths to return
            max_cost_ratio: Maximum ratio of path cost to shortest path
            
        Returns:
            List of Route objects
        """
        shortest = self.find_shortest_path(graph, start, end, domain)
        if not shortest:
            return []
        
        max_cost = shortest.total_cost * max_cost_ratio
        
        # Yen's algorithm for k-shortest paths
        routes = []
        candidates: List[Tuple[float, Route]] = []
        
        # Add shortest path
        routes.append(shortest)
        
        # Build edge map
        edge_map = self._build_edge_map(graph)
        
        for k in range(1, max_paths):
            prev_route = routes[k - 1].path
            
            # For each node in the previous path (except last)
            for i in range(len(prev_route) - 1):
                spur_node = prev_route[i]
                root_path = prev_route[:i + 1]
                
                # Get edges to remove
                removed_edges: Set[Tuple[str, str]] = set()
                for route in routes:
                    if route.path[:i + 1] == root_path:
                        removed_edges.add((route.path[i], route.path[i + 1]))
                
                # Remove edges from root path
                spur_path = self._dijkstra_with_exclusions(
                    graph, edge_map, spur_node, end, domain,
                    excluded_edges=removed_edges
                )
                
                if spur_path:
                    total_path = root_path[:-1] + spur_path.path
                    edges = self._path_to_edges(graph, total_path)
                    capacity = self._compute_path_capacity(graph, total_path)
                    resistance = sum(e.resistance for e in edges)
                    
                    if spur_path.total_cost <= max_cost:
                        candidate = Route(
                            path=total_path,
                            total_cost=spur_path.total_cost,
                            total_capacity=capacity,
                            total_resistance=resistance,
                            is_valid=True,
                            status=RouteStatus.VALID
                        )
                        candidates.append((candidate.total_cost, candidate))
            
            if not candidates:
                break
            
            # Get cheapest candidate
            candidates.sort(key=lambda x: x[0])
            cheapest_cost, cheapest = candidates.pop(0)
            
            if cheapest not in routes:
                routes.append(cheapest)
        
        return routes
    
    def find_path_with_max_hops(
        self,
        graph: TopologyGraph,
        start: str,
        end: str,
        max_hops: int = 20,
        domain: str = "generic"
    ) -> Optional[Route]:
        """
        Find shortest path with hop limit.
        
        Args:
            graph: The topology graph
            start: Source node ID
            end: Target node ID
            max_hops: Maximum number of hops
            domain: Infrastructure domain
            
        Returns:
            Route object or None
        """
        if start not in graph.nodes or end not in graph.nodes:
            return None
        
        queue = [(0.0, 0, start, [start])]  # (cost, hops, node, path)
        visited: Dict[str, float] = {}  # node -> best cost
        edge_map = self._build_edge_map(graph)
        
        while queue:
            current_cost, hops, current_node, path = heapq.heappop(queue)
            
            if hops > max_hops:
                continue
            
            if current_node in visited and visited[current_node] <= current_cost:
                continue
            
            visited[current_node] = current_cost
            
            if current_node == end:
                edges = self._path_to_edges(graph, path)
                capacity = self._compute_path_capacity(graph, path)
                resistance = sum(e.resistance for e in edges)
                
                return Route(
                    path=path,
                    total_cost=current_cost,
                    total_capacity=capacity,
                    total_resistance=resistance,
                    is_valid=True,
                    status=RouteStatus.VALID
                )
            
            if current_node in edge_map:
                for edge in edge_map[current_node]:
                    neighbor = edge.to_node
                    edge_cost = self.cost_model.compute_cost(edge, domain)
                    
                    if neighbor not in visited or visited[neighbor] > current_cost + edge_cost:
                        new_cost = current_cost + edge_cost
                        new_path = path + [neighbor]
                        heapq.heappush(queue, (new_cost, hops + 1, neighbor, new_path))
        
        return None
    
    def route(
        self,
        graph: TopologyGraph,
        source: str,
        destination: str,
        domain: str = "generic"
    ) -> RoutingResult:
        """
        Perform full routing analysis between two nodes.
        
        Args:
            graph: The topology graph
            source: Source node ID
            destination: Target node ID
            domain: Infrastructure domain
            
        Returns:
            RoutingResult with best route and alternatives
        """
        # Find shortest path
        shortest = self.find_shortest_path(graph, source, destination, domain)
        
        if not shortest:
            return RoutingResult(
                source=source,
                destination=destination,
                routes=[],
                best_route=None,
                total_routes_found=0,
                has_valid_route=False
            )
        
        # Find alternatives
        all_routes = self.find_all_paths(graph, source, destination, domain)
        
        return RoutingResult(
            source=source,
            destination=destination,
            routes=all_routes,
            best_route=shortest,
            total_routes_found=len(all_routes),
            has_valid_route=True
        )
    
    # =========================================================================
    # Helper Methods
    # =========================================================================
    
    def _build_edge_map(self, graph: TopologyGraph) -> Dict[str, List[TopologyEdge]]:
        """Build adjacency map for fast edge lookup."""
        edge_map: Dict[str, List[TopologyEdge]] = {}
        
        for edge in graph.edges:
            if edge.from_node not in edge_map:
                edge_map[edge.from_node] = []
            edge_map[edge.from_node].append(edge)
        
        return edge_map
    
    def _path_to_edges(self, graph: TopologyGraph, path: List[str]) -> List[TopologyEdge]:
        """Convert node path to edge list."""
        edges = []
        
        for i in range(len(path) - 1):
            for edge in graph.edges:
                if edge.from_node == path[i] and edge.to_node == path[i + 1]:
                    edges.append(edge)
                    break
        
        return edges
    
    def _compute_path_capacity(self, graph: TopologyGraph, path: List[str]) -> float:
        """Compute minimum capacity along a path (bottleneck)."""
        edges = self._path_to_edges(graph, path)
        
        if not edges:
            return 0.0
        
        return min(e.capacity for e in edges)
    
    def _dijkstra_with_exclusions(
        self,
        graph: TopologyGraph,
        edge_map: Dict[str, List[TopologyEdge]],
        start: str,
        end: str,
        domain: str,
        excluded_edges: Set[Tuple[str, str]]
    ) -> Optional[Route]:
        """Run Dijkstra with excluded edges."""
        queue = [(0.0, start, [start])]
        visited: Set[str] = set()
        
        while queue:
            current_cost, current_node, path = heapq.heappop(queue)
            
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            if current_node == end:
                edges = self._path_to_edges(graph, path)
                capacity = self._compute_path_capacity(graph, path)
                resistance = sum(e.resistance for e in edges)
                
                return Route(
                    path=path,
                    total_cost=current_cost,
                    total_capacity=capacity,
                    total_resistance=resistance,
                    is_valid=True,
                    status=RouteStatus.VALID
                )
            
            if current_node in edge_map:
                for edge in edge_map[current_node]:
                    neighbor = edge.to_node
                    edge_key = (edge.from_node, edge.to_node)
                    
                    if neighbor in visited or edge_key in excluded_edges:
                        continue
                    
                    edge_cost = self.cost_model.compute_cost(edge, domain)
                    new_cost = current_cost + edge_cost
                    new_path = path + [neighbor]
                    
                    heapq.heappush(queue, (new_cost, neighbor, new_path))
        
        return None
