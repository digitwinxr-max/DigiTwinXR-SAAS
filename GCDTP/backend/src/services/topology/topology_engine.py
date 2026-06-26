"""
Topology Engine

Main system for infrastructure topology analysis and simulation.
Provides path tracing, flow simulation, and topology queries.
"""

from collections import deque
from typing import Dict, List, Set, Optional, Tuple
from .graph_builder import GraphBuilder
from .flow_models import FlowModels
from .topology_types import (
    TopologyGraph,
    TopologyNode,
    TopologyEdge,
    Path,
    FlowResult as TopologyFlowResult,
    FlowStatus,
)


class TopologyEngine:
    """
    Main engine for infrastructure topology operations.
    
    Capabilities:
    - Build topology from raw assets
    - Path tracing (BFS/DFS)
    - Flow simulation
    - Network analysis
    - Multi-domain support
    """
    
    def __init__(self):
        self.builder = GraphBuilder()
        self.flow = FlowModels()
        self._graph: Optional[TopologyGraph] = None
    
    def build_topology(self, raw_assets: Dict) -> TopologyGraph:
        """
        Build topology graph from raw asset data.
        
        Args:
            raw_assets: Dictionary mapping asset_id -> asset properties
            
        Returns:
            TopologyGraph instance
        """
        self._graph = self.builder.build(raw_assets)
        return self._graph
    
    def build_from_relationships(
        self,
        assets: List[Dict],
        relationships: List[Dict]
    ) -> TopologyGraph:
        """
        Build topology from separate asset and relationship lists.
        
        Args:
            assets: List of asset dictionaries
            relationships: List of relationship dictionaries
            
        Returns:
            TopologyGraph instance
        """
        self._graph = self.builder.build_from_relationships(assets, relationships)
        return self._graph
    
    @property
    def graph(self) -> Optional[TopologyGraph]:
        """Get the current topology graph."""
        return self._graph
    
    # =========================================================================
    # Path Tracing
    # =========================================================================
    
    def trace_path(
        self,
        graph: TopologyGraph,
        start_node: str,
        goal_node: Optional[str] = None,
        max_depth: int = 100
    ) -> List[str]:
        """
        Trace all reachable nodes from start using BFS.
        
        Args:
            graph: The topology graph
            start_node: Starting node ID
            goal_node: Optional target node (stops when found)
            max_depth: Maximum traversal depth
            
        Returns:
            List of visited node IDs
        """
        visited = set()
        queue = deque([(start_node, 0)])
        path = []
        
        while queue:
            node, depth = queue.popleft()
            
            if node in visited:
                continue
            
            if depth > max_depth:
                continue
            
            visited.add(node)
            path.append(node)
            
            # Stop if we reached goal
            if goal_node and node == goal_node:
                break
            
            # Add neighbors
            for edge in graph.get_edges_from(node):
                if edge.to_node not in visited:
                    queue.append((edge.to_node, depth + 1))
        
        return path
    
    def find_path(
        self,
        graph: TopologyGraph,
        start: str,
        end: str
    ) -> Optional[Path]:
        """
        Find shortest path between two nodes using BFS.
        
        Args:
            graph: The topology graph
            start: Starting node ID
            end: Target node ID
            
        Returns:
            Path object or None if no path exists
        """
        if start not in graph.nodes or end not in graph.nodes:
            return None
        
        # BFS for shortest path
        queue = deque([(start, [start], [])])
        visited = {start}
        
        while queue:
            node, path_nodes, path_edges = queue.popleft()
            
            if node == end:
                total_capacity = self._calculate_path_capacity(path_edges)
                total_resistance = self._calculate_path_resistance(path_edges)
                length = self._calculate_path_length(path_edges)
                return Path(
                    nodes=path_nodes,
                    edges=path_edges,
                    total_capacity=total_capacity,
                    total_resistance=total_resistance,
                    length=length
                )
            
            for edge in graph.get_edges_from(node):
                if edge.to_node not in visited:
                    visited.add(edge.to_node)
                    new_nodes = path_nodes + [edge.to_node]
                    new_edges = path_edges + [edge]
                    queue.append((edge.to_node, new_nodes, new_edges))
        
        return None
    
    def find_all_paths(
        self,
        graph: TopologyGraph,
        start: str,
        end: str,
        max_paths: int = 10
    ) -> List[Path]:
        """
        Find all paths between two nodes.
        
        Args:
            graph: The topology graph
            start: Starting node ID
            end: Target node ID
            max_paths: Maximum number of paths to return
            
        Returns:
            List of Path objects
        """
        paths = []
        
        def dfs(node: str, current_path: List[str], current_edges: List[TopologyEdge]):
            if len(paths) >= max_paths:
                return
            
            if node == end:
                total_capacity = self._calculate_path_capacity(current_edges)
                total_resistance = self._calculate_path_resistance(current_edges)
                length = self._calculate_path_length(current_edges)
                paths.append(Path(
                    nodes=current_path.copy(),
                    edges=current_edges.copy(),
                    total_capacity=total_capacity,
                    total_resistance=total_resistance,
                    length=length
                ))
                return
            
            for edge in graph.get_edges_from(node):
                if edge.to_node not in current_path:
                    dfs(
                        edge.to_node,
                        current_path + [edge.to_node],
                        current_edges + [edge]
                    )
        
        dfs(start, [start], [])
        return paths
    
    def get_reachable_nodes(
        self,
        graph: TopologyGraph,
        start: str
    ) -> Set[str]:
        """
        Get all nodes reachable from start node.
        
        Args:
            graph: The topology graph
            start: Starting node ID
            
        Returns:
            Set of reachable node IDs
        """
        visited = set()
        queue = deque([start])
        
        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            
            for edge in graph.get_edges_from(node):
                if edge.to_node not in visited:
                    queue.append(edge.to_node)
        
        return visited
    
    def get_upstream_nodes(
        self,
        graph: TopologyGraph,
        node: str
    ) -> Set[str]:
        """
        Get all nodes upstream (that feed into) the given node.
        
        Args:
            graph: The topology graph
            node: Target node ID
            
        Returns:
            Set of upstream node IDs
        """
        visited = set()
        queue = deque([node])
        
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            
            # Find nodes that point to this node
            for edge in graph.get_edges_to(current):
                upstream = edge.from_node
                if upstream not in visited:
                    queue.append(upstream)
        
        visited.discard(node)  # Remove the target node itself
        return visited
    
    def get_downstream_nodes(
        self,
        graph: TopologyGraph,
        node: str
    ) -> Set[str]:
        """
        Get all nodes downstream (that depend on) the given node.
        
        Args:
            graph: The topology graph
            node: Source node ID
            
        Returns:
            Set of downstream node IDs
        """
        return self.get_reachable_nodes(graph, node) - {node}
    
    # =========================================================================
    # Flow Simulation
    # =========================================================================
    
    def simulate_flow(
        self,
        graph: TopologyGraph,
        start_node: str,
        initial_load: float = 1.0
    ) -> TopologyFlowResult:
        """
        Simulate flow propagation from a starting node.
        
        Args:
            graph: The topology graph
            start_node: Source node ID
            initial_load: Initial load at source
            
        Returns:
            FlowResult with node loads, edge flows, and status
        """
        node_loads = {start_node: initial_load}
        edge_flows = {}
        edge_utilization = {}
        overloaded_edges = []
        queue = deque([(start_node, initial_load)])
        
        while queue:
            node, load = queue.popleft()
            node_loads[node] = load
            
            for edge in graph.get_edges_from(node):
                edge_key = f"{edge.from_node}->{edge.to_node}"
                
                flow_result = self.flow.calculate_flow(edge, load)
                
                edge_flows[edge_key] = load
                edge_utilization[edge_key] = flow_result.utilization
                
                if flow_result.status == FlowStatus.OVERLOADED:
                    if edge_key not in overloaded_edges:
                        overloaded_edges.append(edge_key)
                
                # Propagate to next node if stable or degraded
                if flow_result.status in [FlowStatus.STABLE, FlowStatus.DEGRADED]:
                    next_load = flow_result.utilization * load
                    if edge.to_node not in node_loads:
                        node_loads[edge.to_node] = next_load
                        queue.append((edge.to_node, next_load))
                    else:
                        node_loads[edge.to_node] += next_load
        
        # Determine overall status
        if overloaded_edges:
            overall_status = FlowStatus.OVERLOADED
        elif any(u > 0.8 for u in edge_utilization.values()):
            overall_status = FlowStatus.DEGRADED
        else:
            overall_status = FlowStatus.STABLE
        
        total_flow = sum(edge_flows.values())
        
        return TopologyFlowResult(
            status=overall_status,
            node_loads=node_loads,
            edge_flows=edge_flows,
            overloaded_edges=overloaded_edges,
            utilization=edge_utilization,
            total_flow=total_flow
        )
    
    def simulate_multi_source_flow(
        self,
        graph: TopologyGraph,
        sources: Dict[str, float]
    ) -> TopologyFlowResult:
        """
        Simulate flow from multiple source nodes.
        
        Args:
            graph: The topology graph
            sources: Dictionary mapping source node IDs to initial loads
            
        Returns:
            FlowResult with aggregated results
        """
        all_node_loads = {}
        all_edge_flows = {}
        all_edge_utilization = {}
        all_overloaded = []
        
        for source, load in sources.items():
            result = self.simulate_flow(graph, source, load)
            
            # Merge results
            for node, node_load in result.node_loads.items():
                all_node_loads[node] = all_node_loads.get(node, 0) + node_load
            
            for edge_key, flow in result.edge_flows.items():
                if edge_key in all_edge_flows:
                    all_edge_flows[edge_key] += flow
                    # Take max utilization
                    all_edge_utilization[edge_key] = max(
                        all_edge_utilization.get(edge_key, 0),
                        result.utilization.get(edge_key, 0)
                    )
                else:
                    all_edge_flows[edge_key] = flow
                    all_edge_utilization[edge_key] = result.utilization.get(edge_key, 0)
            
            for edge_key in result.overloaded_edges:
                if edge_key not in all_overloaded:
                    all_overloaded.append(edge_key)
        
        # Determine overall status
        if all_overloaded:
            overall_status = FlowStatus.OVERLOADED
        elif any(u > 0.8 for u in all_edge_utilization.values()):
            overall_status = FlowStatus.DEGRADED
        else:
            overall_status = FlowStatus.STABLE
        
        total_flow = sum(all_edge_flows.values())
        
        return TopologyFlowResult(
            status=overall_status,
            node_loads=all_node_loads,
            edge_flows=all_edge_flows,
            overloaded_edges=all_overloaded,
            utilization=all_edge_utilization,
            total_flow=total_flow
        )
    
    # =========================================================================
    # Network Analysis
    # =========================================================================
    
    def get_bridge_edges(
        self,
        graph: TopologyGraph,
        node: str
    ) -> List[TopologyEdge]:
        """
        Get edges that, if removed, would disconnect the network.
        
        Args:
            graph: The topology graph
            node: Node to check
            
        Returns:
            List of bridge edges
        """
        bridges = []
        
        for edge in graph.get_edges_from(node):
            # Try removing this edge
            test_graph = TopologyGraph(
                nodes=graph.nodes.copy(),
                edges=[e for e in graph.edges if e != edge]
            )
            
            # Check if target is still reachable
            reachable = self.get_reachable_nodes(test_graph, node)
            if edge.to_node not in reachable:
                bridges.append(edge)
        
        return bridges
    
    def get_critical_nodes(
        self,
        graph: TopologyGraph
    ) -> List[Tuple[str, int]]:
        """
        Get nodes sorted by their importance (degree centrality).
        
        Args:
            graph: The topology graph
            
        Returns:
            List of (node_id, connection_count) tuples, sorted descending
        """
        degrees = {}
        
        for node_id in graph.nodes:
            count = len(graph.get_edges_from(node_id)) + len(graph.get_edges_to(node_id))
            degrees[node_id] = count
        
        return sorted(degrees.items(), key=lambda x: x[1], reverse=True)
    
    # =========================================================================
    # Helper Methods
    # =========================================================================
    
    def _calculate_path_capacity(self, edges: List[TopologyEdge]) -> float:
        """Calculate minimum capacity along a path (bottleneck)."""
        if not edges:
            return 0
        return min(e.capacity for e in edges)
    
    def _calculate_path_resistance(self, edges: List[TopologyEdge]) -> float:
        """Calculate total resistance along a path."""
        return sum(e.resistance for e in edges)
    
    def _calculate_path_length(self, edges: List[TopologyEdge]) -> float:
        """Calculate total length of a path."""
        return sum(e.length or 0 for e in edges)
