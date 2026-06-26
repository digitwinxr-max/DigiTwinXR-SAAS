"""
Topology Validator

Validates topology graphs for correctness and consistency.
"""

from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from .topology_types import TopologyGraph, TopologyNode, TopologyEdge


@dataclass
class ValidationResult:
    """Result of topology validation."""
    valid: bool
    issues: List[str]
    warnings: List[str]
    stats: Dict
    
    def to_dict(self) -> Dict:
        return {
            "valid": self.valid,
            "issues": self.issues,
            "warnings": self.warnings,
            "stats": self.stats,
        }


class TopologyValidator:
    """
    Validates topology graphs for correctness.
    
    Checks:
    - Empty topology
    - No connectivity
    - Orphan nodes
    - Duplicate edges
    - Invalid references
    - Self-loops
    - Consistent layers
    """
    
    def validate(self, graph: TopologyGraph) -> ValidationResult:
        """
        Perform full validation of a topology graph.
        
        Args:
            graph: The topology graph to validate
            
        Returns:
            ValidationResult with issues and warnings
        """
        issues = []
        warnings = []
        stats = {}
        
        # Basic structure checks
        self._check_basic_structure(graph, issues, warnings)
        
        # Connectivity checks
        self._check_connectivity(graph, issues, warnings)
        
        # Node reference checks
        self._check_node_references(graph, issues)
        
        # Edge validity checks
        self._check_edge_validity(graph, issues, warnings)
        
        # Layer consistency
        self._check_layer_consistency(graph, warnings)
        
        # Collect statistics
        stats = self._collect_stats(graph)
        
        return ValidationResult(
            valid=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            stats=stats
        )
    
    def _check_basic_structure(
        self,
        graph: TopologyGraph,
        issues: List[str],
        warnings: List[str]
    ) -> None:
        """Check basic graph structure."""
        if not graph.nodes:
            issues.append("Empty topology: no nodes defined")
            return
        
        if len(graph.nodes) == 0:
            issues.append("No nodes in topology")
        
        if not graph.edges:
            warnings.append("No edges defined - topology has no connectivity")
    
    def _check_connectivity(
        self,
        graph: TopologyGraph,
        issues: List[str],
        warnings: List[str]
    ) -> None:
        """Check graph connectivity and detect orphans."""
        connected_nodes = self._get_connected_nodes(graph)
        
        # Check for orphan nodes
        orphan_nodes = set(graph.nodes.keys()) - connected_nodes
        
        if orphan_nodes:
            issue = f"Orphan nodes detected: {len(orphan_nodes)}"
            if len(orphan_nodes) <= 5:
                issue += f" ({', '.join(list(orphan_nodes)[:5])})"
            else:
                issue += f" (showing first 5: {', '.join(list(orphan_nodes)[:5])})"
            
            if len(orphan_nodes) == len(graph.nodes):
                issues.append(f"No connectivity: all {len(orphan_nodes)} nodes are orphans")
            else:
                warnings.append(issue)
        
        # Check for disconnected components
        components = self._find_components(graph)
        
        if len(components) > 1:
            warnings.append(
                f"Graph has {len(components)} disconnected components"
            )
            
            # List component sizes
            component_sizes = [len(c) for c in components]
            warnings.append(
                f"Component sizes: {component_sizes}"
            )
    
    def _check_node_references(
        self,
        graph: TopologyGraph,
        issues: List[str]
    ) -> None:
        """Check that all edge references point to valid nodes."""
        invalid_edges = []
        
        for edge in graph.edges:
            if edge.from_node not in graph.nodes:
                invalid_edges.append(
                    f"Edge from '{edge.from_node}' references non-existent node"
                )
            if edge.to_node not in graph.nodes:
                invalid_edges.append(
                    f"Edge to '{edge.to_node}' references non-existent node"
                )
        
        if invalid_edges:
            issues.extend(invalid_edges[:10])  # Limit to first 10
            if len(invalid_edges) > 10:
                issues.append(
                    f"... and {len(invalid_edges) - 10} more invalid edge references"
                )
    
    def _check_edge_validity(
        self,
        graph: TopologyGraph,
        issues: List[str],
        warnings: List[str]
    ) -> None:
        """Check edge properties for validity."""
        # Check for self-loops
        self_loops = []
        for edge in graph.edges:
            if edge.from_node == edge.to_node:
                self_loops.append(edge.from_node)
        
        if self_loops:
            warnings.append(
                f"Self-loops detected on nodes: {', '.join(self_loops)}"
            )
        
        # Check for duplicate edges
        seen_edges = set()
        duplicates = []
        for edge in graph.edges:
            edge_key = (edge.from_node, edge.to_node)
            if edge_key in seen_edges:
                duplicates.append(f"{edge.from_node} -> {edge.to_node}")
            else:
                seen_edges.add(edge_key)
        
        if duplicates:
            warnings.append(
                f"Duplicate edges detected: {len(duplicates)} edges"
            )
        
        # Check for negative/invalid capacity
        invalid_capacity = []
        for edge in graph.edges:
            if edge.capacity < 0:
                invalid_capacity.append(edge.from_node)
        
        if invalid_capacity:
            issues.append(
                f"Edges with negative capacity: {', '.join(invalid_capacity)}"
            )
        
        # Check for excessive resistance
        high_resistance = []
        for edge in graph.edges:
            if edge.resistance > 0.9:
                high_resistance.append(f"{edge.from_node}->{edge.to_node}")
        
        if high_resistance:
            warnings.append(
                f"Edges with high resistance (>0.9): {len(high_resistance)}"
            )
    
    def _check_layer_consistency(
        self,
        graph: TopologyGraph,
        warnings: List[str]
    ) -> None:
        """Check for consistent layer usage in edges."""
        layer_connections = {}
        
        for edge in graph.edges:
            from_node = graph.get_node(edge.from_node)
            to_node = graph.get_node(edge.to_node)
            
            if from_node and to_node:
                from_layer = from_node.layer
                to_layer = to_node.layer
                
                if from_layer != to_layer:
                    key = f"{from_layer}->{to_layer}"
                    layer_connections[key] = layer_connections.get(key, 0) + 1
        
        # Cross-layer connections are informational
        if layer_connections:
            warnings.append(
                f"Cross-layer connections found: {len(layer_connections)} types"
            )
    
    def _collect_stats(self, graph: TopologyGraph) -> Dict:
        """Collect topology statistics."""
        # Node type distribution
        node_types = {}
        for node in graph.nodes.values():
            node_types[node.type] = node_types.get(node.type, 0) + 1
        
        # Layer distribution
        layers = {}
        for node in graph.nodes.values():
            layers[node.layer] = layers.get(node.layer, 0) + 1
        
        # Edge type distribution
        edge_directions = {"unidirectional": 0, "bidirectional": 0}
        for edge in graph.edges:
            edge_directions[edge.direction] = edge_directions.get(edge.direction, 0) + 1
        
        # Connectivity stats
        connected = len(self._get_connected_nodes(graph))
        
        # Average degree
        total_degree = sum(
            len(graph.get_edges_from(n)) + len(graph.get_edges_to(n))
            for n in graph.nodes
        )
        avg_degree = total_degree / len(graph.nodes) if graph.nodes else 0
        
        return {
            "node_count": graph.node_count(),
            "edge_count": graph.edge_count(),
            "connected_nodes": connected,
            "orphan_nodes": graph.node_count() - connected,
            "node_types": node_types,
            "layers": layers,
            "edge_directions": edge_directions,
            "avg_degree": round(avg_degree, 2),
            "density": round(
                graph.edge_count() / (graph.node_count() * (graph.node_count() - 1))
                if graph.node_count() > 1 else 0,
                4
            ),
        }
    
    def _get_connected_nodes(self, graph: TopologyGraph) -> Set[str]:
        """Get set of nodes that are part of edges."""
        connected = set()
        for edge in graph.edges:
            connected.add(edge.from_node)
            connected.add(edge.to_node)
        return connected
    
    def _find_components(self, graph: TopologyGraph) -> List[Set[str]]:
        """Find disconnected components using BFS."""
        visited = set()
        components = []
        
        for node_id in graph.nodes:
            if node_id not in visited:
                component = set()
                queue = [node_id]
                
                while queue:
                    current = queue.pop(0)
                    if current in visited:
                        continue
                    visited.add(current)
                    component.add(current)
                    
                    # Add neighbors
                    for edge in graph.get_edges_from(current):
                        if edge.to_node not in visited:
                            queue.append(edge.to_node)
                    for edge in graph.get_edges_to(current):
                        if edge.from_node not in visited:
                            queue.append(edge.from_node)
                
                components.append(component)
        
        return components
    
    def validate_node(
        self,
        graph: TopologyGraph,
        node_id: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate a single node.
        
        Args:
            graph: The topology graph
            node_id: Node to validate
            
        Returns:
            Tuple of (is_valid, issues)
        """
        issues = []
        
        if node_id not in graph.nodes:
            issues.append(f"Node '{node_id}' does not exist")
            return False, issues
        
        node = graph.get_node(node_id)
        
        if not node.type:
            issues.append("Node has no type defined")
        
        if not node.layer:
            issues.append("Node has no layer defined")
        
        # Check connectivity
        edges_from = graph.get_edges_from(node_id)
        edges_to = graph.get_edges_to(node_id)
        
        if not edges_from and not edges_to:
            issues.append("Node has no connections")
        
        return len(issues) == 0, issues
    
    def validate_edge(
        self,
        graph: TopologyGraph,
        from_node: str,
        to_node: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate a single edge.
        
        Args:
            graph: The topology graph
            from_node: Source node ID
            to_node: Target node ID
            
        Returns:
            Tuple of (is_valid, issues)
        """
        issues = []
        
        if from_node not in graph.nodes:
            issues.append(f"Source node '{from_node}' does not exist")
        
        if to_node not in graph.nodes:
            issues.append(f"Target node '{to_node}' does not exist")
        
        if from_node == to_node:
            issues.append("Edge is a self-loop")
        
        # Check if edge exists
        edge_exists = any(
            e.from_node == from_node and e.to_node == to_node
            for e in graph.edges
        )
        
        if not edge_exists:
            issues.append("Edge does not exist in graph")
        
        return len(issues) == 0, issues
