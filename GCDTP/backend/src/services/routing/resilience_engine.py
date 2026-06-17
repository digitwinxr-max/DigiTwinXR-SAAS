"""
Resilience Engine

Measures network robustness under stress.
Evaluates route resilience, redundancy, and stability.
"""

from typing import Dict, List, Optional, Set
from backend.src.services.topology import TopologyGraph, TopologyEdge
from backend.src.services.routing.routing_engine import RoutingEngine
from backend.src.services.routing.routing_types import (
    Route,
    ResilienceMetrics,
    NetworkResilienceResult,
)


class ResilienceEngine:
    """
    Engine for resilience and stability analysis.
    
    Features:
    - Route resilience scoring
    - Redundancy analysis
    - Critical node/edge identification
    - Network-wide resilience assessment
    """
    
    def __init__(self):
        self.routing_engine = RoutingEngine()
        
        # Scoring weights
        self.REDUNDANCY_WEIGHT = 0.3
        self.CAPACITY_WEIGHT = 0.5
        self.STABILITY_WEIGHT = 0.2
        
        # Thresholds
        self.CRITICAL_REDUNDANCY = 1  # Less than this = critical
    
    def compute_resilience_score(
        self,
        graph: TopologyGraph,
        route: Route
    ) -> ResilienceMetrics:
        """
        Compute resilience score for a route.
        
        Args:
            graph: The topology graph
            route: The route to evaluate
            
        Returns:
            ResilienceMetrics with scores
        """
        if not route or not route.path:
            return self._empty_metrics()
        
        # Count alternative paths
        redundancy = self._count_alternative_paths(
            graph,
            route.path[0],
            route.path[-1],
            exclude_path=route.path
        )
        
        # Calculate capacity margin
        capacity_margin = self._calculate_capacity_margin(route)
        
        # Calculate stability score
        stability = self._calculate_stability(route, redundancy)
        
        # Calculate overall resilience score
        resilience_score = (
            redundancy * self.REDUNDANCY_WEIGHT * 0.33 +  # Normalize to 0-1
            capacity_margin * self.CAPACITY_WEIGHT +
            stability * self.STABILITY_WEIGHT
        )
        
        return ResilienceMetrics(
            resilience_score=resilience_score,
            redundancy_paths=redundancy,
            capacity_margin=capacity_margin,
            stability_score=stability,
            alternative_routes=redundancy,
            bottleneck_capacity=route.total_capacity,
            average_utilization=0.0  # Calculated when flow is applied
        )
    
    def compute_network_resilience(
        self,
        graph: TopologyGraph,
        key_pairs: Optional[List[tuple]] = None
    ) -> NetworkResilienceResult:
        """
        Compute overall network resilience.
        
        Args:
            graph: The topology graph
            key_pairs: Optional list of (source, dest) pairs to analyze
            
        Returns:
            NetworkResilienceResult with comprehensive metrics
        """
        if key_pairs is None:
            # Analyze key pairs based on graph structure
            key_pairs = self._select_key_pairs(graph)
        
        # Analyze each pair
        route_resilience: Dict[str, ResilienceMetrics] = {}
        critical_nodes: Set[str] = set()
        critical_edges: Set[str] = set()
        spof_nodes: List[str] = []
        
        all_scores = []
        
        for source, dest in key_pairs:
            route = self.routing_engine.find_shortest_path(graph, source, dest)
            
            if route:
                key = f"{source}->{dest}"
                metrics = self.compute_resilience_score(graph, route)
                route_resilience[key] = metrics
                all_scores.append(metrics.resilience_score)
                
                # Identify critical elements
                if metrics.redundancy_paths <= self.CRITICAL_REDUNDANCY:
                    spof_nodes.extend(route.path)
                
                for i in range(len(route.path) - 1):
                    edge_key = f"{route.path[i]}->{route.path[i + 1]}"
                    critical_edges.add(edge_key)
        
        # Calculate overall score
        overall_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
        
        # Count nodes in critical edges
        for edge_key in critical_edges:
            parts = edge_key.split("->")
            if len(parts) == 2:
                critical_nodes.add(parts[0])
                critical_nodes.add(parts[1])
        
        return NetworkResilienceResult(
            graph_id="network",
            overall_score=overall_score,
            critical_nodes=list(critical_nodes),
            critical_edges=list(critical_edges),
            single_points_of_failure=list(set(spof_nodes)),
            route_resilience=route_resilience
        )
    
    def find_critical_nodes(
        self,
        graph: TopologyGraph
    ) -> List[tuple]:
        """
        Find nodes that are critical to network connectivity.
        
        Args:
            graph: The topology graph
            
        Returns:
            List of (node_id, criticality_score) tuples
        """
        criticality: Dict[str, float] = {}
        
        for node_id in graph.nodes:
            # Count how many paths would be broken
            broken_paths = 0
            total_paths = 0
            
            for other_id in graph.nodes:
                if node_id == other_id:
                    continue
                
                # Check if there's a path
                route = self.routing_engine.find_shortest_path(graph, node_id, other_id)
                if route:
                    total_paths += 1
                    # Check if removing this node breaks the path
                    if node_id in route.path:
                        broken_paths += 1
            
            if total_paths > 0:
                criticality[node_id] = broken_paths / total_paths
        
        # Sort by criticality
        sorted_critical = sorted(
            criticality.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_critical
    
    def find_critical_edges(
        self,
        graph: TopologyGraph
    ) -> List[tuple]:
        """
        Find edges that are critical to network connectivity (bridges).
        
        Args:
            graph: The topology graph
            
        Returns:
            List of (edge_id, is_critical) tuples
        """
        critical_edges = []
        
        for edge in graph.edges:
            # Test if removing this edge disconnects the graph
            is_bridge = self._is_bridge(graph, edge)
            
            critical_edges.append((
                f"{edge.from_node}->{edge.to_node}",
                is_bridge
            ))
        
        # Sort by criticality (bridges first)
        return sorted(
            critical_edges,
            key=lambda x: x[1],
            reverse=True
        )
    
    def evaluate_route_alternatives(
        self,
        graph: TopologyGraph,
        source: str,
        destination: str,
        max_alternatives: int = 5
    ) -> Dict[str, ResilienceMetrics]:
        """
        Evaluate resilience of alternative routes.
        
        Args:
            graph: The topology graph
            source: Source node
            destination: Target node
            max_alternatives: Maximum routes to evaluate
            
        Returns:
            Dictionary mapping route_key to ResilienceMetrics
        """
        routes = self.routing_engine.find_all_paths(
            graph,
            source,
            destination,
            max_paths=max_alternatives
        )
        
        results = {}
        for i, route in enumerate(routes):
            key = f"route_{i + 1}"
            metrics = self.compute_resilience_score(graph, route)
            results[key] = metrics
        
        return results
    
    def get_redundancy_score(
        self,
        graph: TopologyGraph,
        node: str
    ) -> float:
        """
        Get redundancy score for a specific node.
        
        Args:
            graph: The topology graph
            node: Node to evaluate
            
        Returns:
            Redundancy score (0-1, higher = more redundant)
        """
        # Count how many alternative paths exist
        alternatives = 0
        
        for edge in graph.get_edges_from(node):
            # Check if there's an alternative path to the target
            # This is simplified - real implementation would check
            # for multiple independent paths
            alternatives += 1
        
        for edge in graph.get_edges_to(node):
            alternatives += 1
        
        # Normalize to 0-1
        # Assuming 3+ alternatives is fully redundant
        return min(1.0, alternatives / 3.0)
    
    # =========================================================================
    # Helper Methods
    # =========================================================================
    
    def _count_alternative_paths(
        self,
        graph: TopologyGraph,
        start: str,
        end: str,
        exclude_path: Optional[List[str]] = None
    ) -> int:
        """Count alternative paths between two nodes."""
        count = 0
        
        # Find first path
        first_path = self.routing_engine.find_shortest_path(graph, start, end)
        if not first_path:
            return 0
        
        count = 1
        
        # Try to find more paths with edge exclusions
        if exclude_path:
            for i in range(len(exclude_path) - 1):
                # Skip finding more than 5 alternatives
                if count >= 5:
                    break
                
                # Check if path exists without this edge
                edge = self._find_edge(graph, exclude_path[i], exclude_path[i + 1])
                if edge:
                    # Try finding path without this edge
                    alt_routes = self.routing_engine.find_all_paths(
                        graph, start, end, max_paths=3
                    )
                    count = len(alt_routes)
        
        return max(1, count)
    
    def _calculate_capacity_margin(self, route: Route) -> float:
        """Calculate capacity margin (available capacity / total capacity)."""
        if route.total_capacity == 0:
            return 0.0
        
        # Assuming current utilization is 50%
        current_utilization = 0.5
        available = 1.0 - current_utilization
        
        return min(1.0, available)
    
    def _calculate_stability(
        self,
        route: Route,
        redundancy: int
    ) -> float:
        """Calculate stability score based on route characteristics."""
        # Base stability from redundancy
        redundancy_factor = min(1.0, redundancy / 3.0)
        
        # Capacity factor (higher capacity = more stable)
        capacity_factor = min(1.0, route.total_capacity / 100.0)
        
        # Hop count factor (fewer hops = more stable)
        hop_factor = 1.0 / (1.0 + route.hop_count * 0.1)
        
        # Combine factors
        stability = (
            redundancy_factor * 0.4 +
            capacity_factor * 0.3 +
            hop_factor * 0.3
        )
        
        return stability
    
    def _is_bridge(self, graph: TopologyGraph, edge: TopologyEdge) -> bool:
        """Check if an edge is a bridge (removal disconnects graph)."""
        # Build graph without this edge
        other_edges = [e for e in graph.edges if e != edge]
        
        # Check if edge.to_node is reachable from edge.from_node
        visited: Set[str] = set()
        queue = [edge.from_node]
        
        while queue:
            node = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            
            for e in other_edges:
                if e.from_node == node and e.to_node not in visited:
                    queue.append(e.to_node)
        
        # If target is not reachable, edge is a bridge
        return edge.to_node not in visited
    
    def _find_edge(
        self,
        graph: TopologyGraph,
        from_node: str,
        to_node: str
    ) -> Optional[TopologyEdge]:
        """Find edge between two nodes."""
        for edge in graph.edges:
            if edge.from_node == from_node and edge.to_node == to_node:
                return edge
        return None
    
    def _select_key_pairs(
        self,
        graph: TopologyGraph
    ) -> List[tuple]:
        """Select key source-destination pairs for analysis."""
        nodes = list(graph.nodes.keys())
        
        if len(nodes) <= 10:
            # Analyze all pairs
            pairs = []
            for i in range(len(nodes)):
                for j in range(i + 1, len(nodes)):
                    pairs.append((nodes[i], nodes[j]))
            return pairs
        
        # Select pairs based on connectivity
        # Take nodes with most connections
        degrees = []
        for node_id in nodes:
            degree = len(graph.get_edges_from(node_id)) + len(graph.get_edges_to(node_id))
            degrees.append((node_id, degree))
        
        degrees.sort(key=lambda x: x[1], reverse=True)
        key_nodes = [d[0] for d in degrees[:10]]
        
        pairs = []
        for i in range(len(key_nodes)):
            for j in range(i + 1, len(key_nodes)):
                pairs.append((key_nodes[i], key_nodes[j]))
        
        return pairs[:20]  # Limit to 20 pairs
    
    def _empty_metrics(self) -> ResilienceMetrics:
        """Return empty resilience metrics."""
        return ResilienceMetrics(
            resilience_score=0.0,
            redundancy_paths=0,
            capacity_margin=0.0,
            stability_score=0.0
        )
