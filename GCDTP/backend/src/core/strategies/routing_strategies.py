"""
Routing Strategies

Pluggable routing algorithms following the Strategy pattern.
"""

import heapq
from abc import abstractmethod
from typing import List, Optional, Dict, Any, Set, Tuple
from backend.src.core.interfaces.base import IStrategy


class BaseRoutingStrategy(IStrategy):
    """Base class for routing strategies."""
    
    def __init__(self, cost_model=None):
        self.cost_model = cost_model
    
    @abstractmethod
    def find_path(
        self,
        graph: Any,
        start: str,
        end: str,
        domain: str = "generic",
        **kwargs
    ) -> Optional[List[str]]:
        """Find a path from start to end."""
        pass
    
    def execute(self, **kwargs) -> Any:
        """Execute the strategy."""
        return self.find_path(**kwargs)
    
    def get_name(self) -> str:
        """Get strategy name."""
        return self.__class__.__name__
    
    def _build_edge_map(self, graph: Any) -> Dict[str, List[Any]]:
        """Build adjacency map for fast edge lookup."""
        edge_map: Dict[str, List[Any]] = {}
        for edge in graph.edges:
            if edge.from_node not in edge_map:
                edge_map[edge.from_node] = []
            edge_map[edge.from_node].append(edge)
        return edge_map
    
    def _compute_edge_cost(self, edge: Any, domain: str) -> float:
        """Compute cost of traversing an edge."""
        if self.cost_model:
            return self.cost_model.compute_cost(edge, domain)
        return 1.0 + edge.resistance


class DijkstraStrategy(BaseRoutingStrategy):
    """Dijkstra's shortest path algorithm."""
    
    def find_path(
        self,
        graph: Any,
        start: str,
        end: str,
        domain: str = "generic",
        **kwargs
    ) -> Optional[List[str]]:
        """Find shortest path using Dijkstra's algorithm."""
        if start not in graph.nodes or end not in graph.nodes:
            return None
        
        edge_map = self._build_edge_map(graph)
        queue = [(0.0, start, [start])]
        visited: Set[str] = set()
        
        while queue:
            current_cost, current_node, path = heapq.heappop(queue)
            
            if current_node in visited:
                continue
            visited.add(current_node)
            
            if current_node == end:
                return path
            
            if current_node in edge_map:
                for edge in edge_map[current_node]:
                    neighbor = edge.to_node
                    if neighbor not in visited:
                        edge_cost = self._compute_edge_cost(edge, domain)
                        heapq.heappush(queue, (current_cost + edge_cost, neighbor, path + [neighbor]))
        
        return None


class AStarStrategy(BaseRoutingStrategy):
    """A* search algorithm with heuristics."""
    
    def __init__(self, cost_model=None, heuristic=None):
        super().__init__(cost_model)
        self.heuristic = heuristic or self._default_heuristic
    
    def find_path(
        self,
        graph: Any,
        start: str,
        end: str,
        domain: str = "generic",
        **kwargs
    ) -> Optional[List[str]]:
        """Find shortest path using A* algorithm."""
        if start not in graph.nodes or end not in graph.nodes:
            return None
        
        edge_map = self._build_edge_map(graph)
        node_positions = self._get_node_positions(graph)
        
        h_end = self.heuristic(start, end, node_positions)
        queue = [(h_end, 0.0, start, [start])]
        visited: Set[str] = set()
        g_scores: Dict[str, float] = {start: 0.0}
        
        while queue:
            f_score, g_score, current_node, path = heapq.heappop(queue)
            
            if current_node in visited:
                continue
            visited.add(current_node)
            
            if current_node == end:
                return path
            
            if current_node in edge_map:
                for edge in edge_map[current_node]:
                    neighbor = edge.to_node
                    if neighbor not in visited:
                        edge_cost = self._compute_edge_cost(edge, domain)
                        tentative_g = g_score + edge_cost
                        
                        if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                            g_scores[neighbor] = tentative_g
                            h_score = self.heuristic(neighbor, end, node_positions)
                            heapq.heappush(queue, (tentative_g + h_score, tentative_g, neighbor, path + [neighbor]))
        
        return None
    
    def _get_node_positions(self, graph: Any) -> Dict[str, Tuple[float, float]]:
        """Get node positions for heuristic calculation."""
        positions = {}
        for node_id, node in graph.nodes.items():
            if node.position:
                positions[node_id] = (node.position.get('x', 0), node.position.get('y', 0))
            else:
                positions[node_id] = (0, 0)
        return positions
    
    def _default_heuristic(
        self,
        node: str,
        end: str,
        positions: Dict[str, Tuple[float, float]]
    ) -> float:
        """Default Euclidean distance heuristic."""
        if node not in positions or end not in positions:
            return 0.0
        x1, y1 = positions[node]
        x2, y2 = positions[end]
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


class BFSRoutingStrategy(BaseRoutingStrategy):
    """Breadth-First Search for unweighted graphs."""
    
    def find_path(
        self,
        graph: Any,
        start: str,
        end: str,
        domain: str = "generic",
        max_depth: int = 100,
        **kwargs
    ) -> Optional[List[str]]:
        """Find shortest path using BFS."""
        if start not in graph.nodes or end not in graph.nodes:
            return None
        
        edge_map = self._build_edge_map(graph)
        from collections import deque
        queue = deque([(start, [start])])
        visited: Set[str] = {start}
        
        while queue:
            current_node, path = queue.popleft()
            
            if len(path) > max_depth:
                continue
            
            if current_node == end:
                return path
            
            if current_node in edge_map:
                for edge in edge_map[current_node]:
                    neighbor = edge.to_node
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, path + [neighbor]))
        
        return None


class RiskAwareRoutingStrategy(BaseRoutingStrategy):
    """Risk-aware routing considering failure probabilities."""
    
    def __init__(self, cost_model=None, risk_weights: Dict[str, float] = None):
        super().__init__(cost_model)
        self.risk_weights = risk_weights or {
            "failure_probability": 0.3,
            "resilience": 0.3,
            "capacity": 0.2,
            "cost": 0.2
        }
    
    def find_path(
        self,
        graph: Any,
        start: str,
        end: str,
        domain: str = "generic",
        **kwargs
    ) -> Optional[List[str]]:
        """Find path considering risk factors."""
        if start not in graph.nodes or end not in graph.nodes:
            return None
        
        edge_map = self._build_edge_map(graph)
        queue = [(0.0, 0.0, start, [start])]
        visited: Set[str] = set()
        
        while queue:
            risk_score, cost, current_node, path = heapq.heappop(queue)
            
            if current_node in visited:
                continue
            visited.add(current_node)
            
            if current_node == end:
                return path
            
            if current_node in edge_map:
                for edge in edge_map[current_node]:
                    neighbor = edge.to_node
                    if neighbor not in visited:
                        edge_cost = self._compute_edge_cost(edge, domain)
                        edge_risk = self._calculate_edge_risk(edge)
                        new_path = path + [neighbor]
                        priority = (risk_score + edge_risk) + (cost + edge_cost) * 0.1
                        heapq.heappush(queue, (risk_score + edge_risk, cost + edge_cost, neighbor, new_path))
        
        return None
    
    def _calculate_edge_risk(self, edge: Any) -> float:
        """Calculate risk score for an edge."""
        risk = 0.0
        if edge.capacity < 50:
            risk += self.risk_weights.get("capacity", 0.2) * (50 - edge.capacity) / 50
        risk += self.risk_weights.get("failure_probability", 0.3) * edge.resistance
        return risk


class CostAdaptiveRoutingStrategy(BaseRoutingStrategy):
    """Cost-adaptive routing with dynamic load."""
    
    def __init__(self, cost_model=None):
        super().__init__(cost_model)
        self.network_state: Dict[str, float] = {}
    
    def update_network_state(self, edge_states: Dict[str, float]) -> None:
        """Update current network load states."""
        self.network_state = edge_states
    
    def find_path(
        self,
        graph: Any,
        start: str,
        end: str,
        domain: str = "generic",
        **kwargs
    ) -> Optional[List[str]]:
        """Find path with adaptive cost model."""
        if start not in graph.nodes or end not in graph.nodes:
            return None
        
        edge_map = self._build_edge_map(graph)
        queue = [(0.0, start, [start])]
        visited: Set[str] = set()
        
        while queue:
            current_cost, current_node, path = heapq.heappop(queue)
            
            if current_node in visited:
                continue
            visited.add(current_node)
            
            if current_node == end:
                return path
            
            if current_node in edge_map:
                for edge in edge_map[current_node]:
                    neighbor = edge.to_node
                    if neighbor not in visited:
                        edge_cost = self._compute_adaptive_cost(edge, domain)
                        heapq.heappush(queue, (current_cost + edge_cost, neighbor, path + [neighbor]))
        
        return None
    
    def _compute_adaptive_cost(self, edge: Any, domain: str) -> float:
        """Compute cost with adaptive load factor."""
        base_cost = self._compute_edge_cost(edge, domain)
        edge_key = f"{edge.from_node}->{edge.to_node}"
        current_load = self.network_state.get(edge_key, 0)
        
        if current_load > 0:
            load_factor = 1.0 + (current_load / edge.capacity) ** 2
            return base_cost * load_factor
        return base_cost
