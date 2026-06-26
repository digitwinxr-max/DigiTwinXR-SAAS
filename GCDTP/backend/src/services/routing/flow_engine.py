"""
Flow Engine

Handles load distribution across routes.
Manages flow allocation, overload detection, and load balancing.
"""

from typing import Dict, List, Optional
from backend.src.services.topology import TopologyGraph, TopologyEdge
from backend.src.services.routing.routing_types import (
    Route,
    FlowAllocation,
    FlowDistribution,
    RouteStatus,
)


class FlowEngine:
    """
    Engine for flow allocation and load distribution.
    
    Features:
    - Flow allocation across routes
    - Overload detection
    - Load balancing
    - Multi-path flow distribution
    """
    
    def __init__(self):
        self.overload_threshold = 1.0  # 100% utilization = overloaded
        self.degraded_threshold = 0.8  # 80% utilization = degraded
    
    def allocate_flow(
        self,
        route: Route,
        total_load: float
    ) -> FlowDistribution:
        """
        Allocate flow across a route.
        
        Distributes load evenly across edges in the route.
        
        Args:
            route: The route to allocate flow on
            total_load: Total load to route
            
        Returns:
            FlowDistribution with per-edge allocations
        """
        if not route or not route.path:
            return FlowDistribution(
                source="",
                destination="",
                allocations=[]
            )
        
        allocations = []
        num_edges = len(route.path) - 1
        
        if num_edges == 0:
            return FlowDistribution(
                source=route.path[0] if route.path else "",
                destination=route.path[-1] if route.path else "",
                allocations=[]
            )
        
        # Distribute load evenly
        base_load = total_load / num_edges
        
        for i in range(num_edges):
            from_node = route.path[i]
            to_node = route.path[i + 1]
            edge_id = f"{from_node}->{to_node}"
            
            # Find edge capacity
            capacity = self._find_edge_capacity(route.path, from_node, to_node)
            
            # Calculate utilization
            utilization = base_load / capacity if capacity > 0 else float('inf')
            
            allocation = FlowAllocation(
                edge_id=edge_id,
                from_node=from_node,
                to_node=to_node,
                load=base_load,
                utilization=utilization,
                capacity=capacity,
                status=self._get_status(utilization)
            )
            
            allocations.append(allocation)
        
        return FlowDistribution(
            source=route.path[0],
            destination=route.path[-1],
            allocations=allocations,
            total_load=total_load
        )
    
    def allocate_multi_path_flow(
        self,
        routes: List[Route],
        total_load: float,
        strategy: str = "equal"
    ) -> List[FlowDistribution]:
        """
        Allocate flow across multiple routes.
        
        Args:
            routes: List of routes to use
            total_load: Total load to distribute
            strategy: Distribution strategy ("equal", "capacity", "cost")
            
        Returns:
            List of FlowDistribution objects
        """
        if not routes:
            return []
        
        distributions = []
        
        # Calculate load distribution based on strategy
        if strategy == "equal":
            loads = self._equal_distribution(len(routes), total_load)
        elif strategy == "capacity":
            loads = self._capacity_distribution(routes, total_load)
        elif strategy == "cost":
            loads = self._cost_distribution(routes, total_load)
        else:
            loads = self._equal_distribution(len(routes), total_load)
        
        # Allocate flow to each route
        for route, load in zip(routes, loads):
            dist = self.allocate_flow(route, load)
            distributions.append(dist)
        
        return distributions
    
    def detect_overload(
        self,
        allocations: List[FlowAllocation]
    ) -> List[FlowAllocation]:
        """
        Detect overloaded edges in allocations.
        
        Args:
            allocations: List of flow allocations
            
        Returns:
            List of overloaded allocations
        """
        return [a for a in allocations if a.utilization > self.overload_threshold]
    
    def detect_degraded(
        self,
        allocations: List[FlowAllocation]
    ) -> List[FlowAllocation]:
        """
        Detect degraded edges in allocations.
        
        Args:
            allocations: List of flow allocations
            
        Returns:
            List of degraded allocations
        """
        return [
            a for a in allocations
            if self.degraded_threshold < a.utilization <= self.overload_threshold
        ]
    
    def balance_load(
        self,
        graph: TopologyGraph,
        routes: List[Route],
        total_load: float
    ) -> List[FlowDistribution]:
        """
        Balance load across routes to minimize max utilization.
        
        Args:
            graph: The topology graph
            routes: Available routes
            total_load: Total load to distribute
            
        Returns:
            Optimized flow distributions
        """
        if not routes or total_load <= 0:
            return []
        
        # Get edge capacities for each route
        route_capacities = []
        for route in routes:
            min_capacity = float('inf')
            for i in range(len(route.path) - 1):
                cap = self._find_edge_capacity(route.path, route.path[i], route.path[i + 1])
                min_capacity = min(min_capacity, cap)
            route_capacities.append(min_capacity if min_capacity != float('inf') else 0)
        
        # Calculate weights based on capacity
        total_capacity = sum(route_capacities)
        if total_capacity == 0:
            return self.allocate_multi_path_flow(routes, total_load, "equal")
        
        # Distribute based on capacity
        loads = [total_load * (cap / total_capacity) for cap in route_capacities]
        
        distributions = []
        for route, load in zip(routes, loads):
            dist = self.allocate_flow(route, load)
            distributions.append(dist)
        
        # Check if any edge is overloaded
        all_overloaded = []
        for dist in distributions:
            all_overloaded.extend(self.detect_overload(dist.allocations))
        
        # If overloaded, fall back to equal distribution
        if all_overloaded:
            return self.allocate_multi_path_flow(routes, total_load, "equal")
        
        return distributions
    
    def simulate_load(
        self,
        graph: TopologyGraph,
        source: str,
        destination: str,
        load: float,
        route: Route
    ) -> FlowDistribution:
        """
        Simulate load on a specific route.
        
        Args:
            graph: The topology graph
            source: Source node
            destination: Destination node
            load: Load to simulate
            route: Route to use
            
        Returns:
            FlowDistribution with simulation results
        """
        dist = self.allocate_flow(route, load)
        
        # Add current loads to utilization
        for allocation in dist.allocations:
            edge = self._find_edge(graph, allocation.from_node, allocation.to_node)
            if edge and edge.current_flow:
                current_util = (allocation.load + edge.current_flow) / allocation.capacity
                allocation.utilization = current_util
                allocation.status = self._get_status(current_util)
        
        return dist
    
    def get_edge_utilization(
        self,
        graph: TopologyGraph,
        allocations: List[FlowAllocation]
    ) -> Dict[str, float]:
        """
        Get utilization for all edges in allocations.
        
        Args:
            graph: The topology graph
            allocations: Flow allocations
            
        Returns:
            Dictionary mapping edge_id to utilization
        """
        utilization = {}
        
        for a in allocations:
            utilization[a.edge_id] = a.utilization
        
        return utilization
    
    # =========================================================================
    # Helper Methods
    # =========================================================================
    
    def _find_edge_capacity(
        self,
        path: List[str],
        from_node: str,
        to_node: str
    ) -> float:
        """Find capacity of edge between two nodes in a path."""
        # This is a simplified lookup - in real implementation,
        # this would query the graph or store edge data
        for i in range(len(path) - 1):
            if path[i] == from_node and path[i + 1] == to_node:
                # Return a default capacity - actual implementation
                # would look this up from the graph
                return 100.0  # Default capacity
        return 100.0
    
    def _find_edge(
        self,
        graph: TopologyGraph,
        from_node: str,
        to_node: str
    ) -> Optional[TopologyEdge]:
        """Find edge in graph between two nodes."""
        for edge in graph.edges:
            if edge.from_node == from_node and edge.to_node == to_node:
                return edge
        return None
    
    def _get_status(self, utilization: float) -> RouteStatus:
        """Get status based on utilization."""
        if utilization > self.overload_threshold:
            return RouteStatus.OVERLOADED
        elif utilization > self.degraded_threshold:
            return RouteStatus.DEGRADED
        else:
            return RouteStatus.VALID
    
    def _equal_distribution(
        self,
        count: int,
        total: float
    ) -> List[float]:
        """Distribute load equally."""
        if count <= 0:
            return []
        base = total / count
        result = [base] * count
        # Handle rounding
        result[0] += total - sum(result)
        return result
    
    def _capacity_distribution(
        self,
        routes: List[Route],
        total_load: float
    ) -> List[float]:
        """Distribute load proportional to route capacity."""
        total_capacity = sum(r.total_capacity for r in routes)
        if total_capacity == 0:
            return self._equal_distribution(len(routes), total_load)
        
        loads = []
        for route in routes:
            share = (route.total_capacity / total_capacity) * total_load
            loads.append(share)
        
        return loads
    
    def _cost_distribution(
        self,
        routes: List[Route],
        total_load: float
    ) -> List[float]:
        """Distribute load inversely proportional to cost."""
        # Lower cost routes get more load
        total_inverse_cost = sum(1.0 / max(r.total_cost, 0.01) for r in routes)
        
        loads = []
        for route in routes:
            share = ((1.0 / max(route.total_cost, 0.01)) / total_inverse_cost) * total_load
            loads.append(share)
        
        return loads
