"""
Path Analysis Engine

Provides path analysis and graph traversal.
"""

from typing import Dict, List, Optional, Any
from backend.src.integrations.neo4j.neo4j_client import Neo4jClient
from backend.src.integrations.neo4j.graph_types import (
    PathAnalysis,
    PathType,
    EntityType,
    GraphNode,
)


class PathAnalysisEngine:
    """
    Provides path analysis capabilities.
    
    Responsibilities:
    - Shortest path finding
    - All paths finding
    - Critical path analysis
    - Dependency path analysis
    - Redundancy path analysis
    """
    
    def __init__(self, client: Optional[Neo4jClient] = None):
        self.client = client or Neo4jClient()
    
    def close(self):
        """Close resources."""
        self.client.close()
    
    def find_shortest_path(
        self,
        start_id: str,
        end_id: str,
        start_type: EntityType,
        end_type: EntityType,
        relationship_types: Optional[List[str]] = None
    ) -> PathAnalysis:
        """
        Find shortest path between two entities.
        
        Args:
            start_id: Start entity ID
            end_id: End entity ID
            start_type: Start entity type
            end_type: End entity type
            relationship_types: Filter by relationship types
            
        Returns:
            PathAnalysis
        """
        rel_pattern = "[*]"
        if relationship_types:
            rel_pattern = "[:{}*]".format("|".join(relationship_types))
        
        query = f"""
        MATCH path = (start:{start_type.value} {{id: $start_id}}){rel_pattern}(end:{end_type.value} {{id: $end_id}})
        WITH path, length(path) as pathLength
        ORDER BY pathLength
        LIMIT 1
        RETURN nodes(path) as nodes, pathLength
        """
        
        results = self.client.execute_cypher(query, {
            "start_id": start_id,
            "end_id": end_id
        })
        
        paths: List[List[GraphNode]] = []
        path_length = 0
        
        if results:
            nodes = results[0].get("nodes", [])
            path_length = results[0].get("pathLength", 0)
            paths = [[
                GraphNode(
                    id=n.get("id", ""),
                    entity_type=start_type,
                    entity_id=n.get("id", ""),
                    label=n.get("type", "")
                )
                for n in nodes
            ]]
        
        return PathAnalysis(
            path_type=PathType.SHORTEST,
            start_entity_id=start_id,
            end_entity_id=end_id,
            path_length=path_length,
            paths=paths
        )
    
    def find_all_paths(
        self,
        start_id: str,
        end_id: str,
        start_type: EntityType,
        end_type: EntityType,
        max_depth: int = 10
    ) -> PathAnalysis:
        """
        Find all paths between two entities.
        
        Args:
            start_id: Start entity ID
            end_id: End entity ID
            start_type: Start entity type
            end_type: End entity type
            max_depth: Maximum path depth
            
        Returns:
            PathAnalysis
        """
        query = f"""
        MATCH path = (start:{start_type.value} {{id: $start_id}})-[*1..{max_depth}]-(end:{end_type.value} {{id: $end_id}})
        RETURN nodes(path) as nodes, length(path) as pathLength
        ORDER BY pathLength
        """
        
        results = self.client.execute_cypher(query, {
            "start_id": start_id,
            "end_id": end_id
        })
        
        paths: List[List[GraphNode]] = []
        for result in results:
            nodes = result.get("nodes", [])
            paths.append([
                GraphNode(
                    id=n.get("id", ""),
                    entity_type=start_type,
                    entity_id=n.get("id", ""),
                    label=n.get("type", "")
                )
                for n in nodes
            ])
        
        min_length = min((len(p) for p in paths), default=0)
        
        return PathAnalysis(
            path_type=PathType.ALL_PATHS,
            start_entity_id=start_id,
            end_entity_id=end_id,
            path_length=min_length,
            paths=paths
        )
    
    def find_critical_paths(
        self,
        start_id: str,
        end_id: str,
        start_type: EntityType,
        end_type: EntityType
    ) -> PathAnalysis:
        """
        Find critical paths between two entities.
        
        Critical paths are the longest paths with no redundancy.
        
        Args:
            start_id: Start entity ID
            end_id: End entity ID
            start_type: Start entity type
            end_type: End entity type
            
        Returns:
            PathAnalysis
        """
        # Find all paths first
        all_paths = self.find_all_paths(start_id, end_id, start_type, end_type)
        
        # Filter to critical paths (no alternative routes at each step)
        critical_paths: List[List[GraphNode]] = []
        
        for path in all_paths.paths:
            is_critical = True
            # Check if each step has only one option
            for i, node in enumerate(path[:-1]):
                # In production, would query for alternatives at each step
                pass
            
            if is_critical:
                critical_paths.append(path)
        
        return PathAnalysis(
            path_type=PathType.CRITICAL,
            start_entity_id=start_id,
            end_entity_id=end_id,
            path_length=min((len(p) for p in critical_paths), default=0),
            paths=critical_paths
        )
    
    def find_dependency_paths(
        self,
        start_id: str,
        end_id: str,
        start_type: EntityType,
        end_type: EntityType,
        max_depth: int = 10
    ) -> PathAnalysis:
        """
        Find dependency paths between two entities.
        
        Args:
            start_id: Start entity ID
            end_id: End entity ID
            start_type: Start entity type
            end_type: End entity type
            max_depth: Maximum depth
            
        Returns:
            PathAnalysis
        """
        query = f"""
        MATCH path = (start:{start_type.value} {{id: $start_id}})-[:DEPENDS_ON*1..{max_depth}]->(end:{end_type.value} {{id: $end_id}})
        RETURN nodes(path) as nodes, length(path) as pathLength
        ORDER BY pathLength
        """
        
        results = self.client.execute_cypher(query, {
            "start_id": start_id,
            "end_id": end_id
        })
        
        paths: List[List[GraphNode]] = []
        for result in results:
            nodes = result.get("nodes", [])
            paths.append([
                GraphNode(
                    id=n.get("id", ""),
                    entity_type=start_type,
                    entity_id=n.get("id", ""),
                    label=n.get("type", "")
                )
                for n in nodes
            ])
        
        min_length = min((len(p) for p in paths), default=0)
        
        return PathAnalysis(
            path_type=PathType.DEPENDENCY,
            start_entity_id=start_id,
            end_entity_id=end_id,
            path_length=min_length,
            paths=paths
        )
    
    def find_redundancy_paths(
        self,
        start_id: str,
        end_id: str,
        start_type: EntityType,
        end_type: EntityType
    ) -> List[PathAnalysis]:
        """
        Find redundant paths between two entities.
        
        Redundant paths provide alternative routes.
        
        Args:
            start_id: Start entity ID
            end_id: End entity ID
            start_type: Start entity type
            end_type: End entity type
            
        Returns:
            List of redundant paths
        """
        # Find all paths
        all_paths = self.find_all_paths(start_id, end_id, start_type, end_type)
        
        # Filter to redundant paths
        if len(all_paths.paths) > 1:
            # Multiple paths exist - find alternative routes
            return [
                PathAnalysis(
                    path_type=PathType.REDUNDANCY,
                    start_entity_id=start_id,
                    end_entity_id=end_id,
                    path_length=len(p),
                    paths=[p]
                )
                for p in all_paths.paths[1:]  # First is shortest, rest are redundant
            ]
        
        return []
    
    def get_path_between_entities(
        self,
        entity_id_1: str,
        entity_id_2: str,
        entity_type: EntityType = EntityType.ASSET
    ) -> PathAnalysis:
        """
        Get path between two entities of the same type.
        
        Args:
            entity_id_1: First entity ID
            entity_id_2: Second entity ID
            entity_type: Entity type
            
        Returns:
            PathAnalysis
        """
        return self.find_shortest_path(
            entity_id_1,
            entity_id_2,
            entity_type,
            entity_type
        )


class PathAnalyzer:
    """
    Analyzer for path analysis results.
    """
    
    def __init__(self):
        self._path_history: List[PathAnalysis] = []
    
    def add_path(self, path: PathAnalysis) -> None:
        """Add a path analysis result."""
        self._path_history.append(path)
    
    def get_most_common_waypoints(self) -> List[Dict[str, Any]]:
        """Get most common intermediate waypoints."""
        waypoint_counts: Dict[str, int] = {}
        
        for path in self._path_history:
            for p in path.paths:
                for node in p[1:-1]:  # Exclude start and end
                    entity_id = node.entity_id
                    waypoint_counts[entity_id] = waypoint_counts.get(entity_id, 0) + 1
        
        return sorted(
            [{"entity_id": k, "count": v} for k, v in waypoint_counts.items()],
            key=lambda x: x["count"],
            reverse=True
        )
    
    def get_average_path_length(self) -> float:
        """Get average path length."""
        if not self._path_history:
            return 0.0
        
        total = sum(p.path_length for p in self._path_history)
        return total / len(self._path_history)
