"""
Graph Query Engine

Provides graph query capabilities.
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from backend.src.integrations.neo4j.neo4j_client import Neo4jClient, CypherBuilder
from backend.src.integrations.neo4j.graph_types import (
    QueryResult,
    GraphNode,
    GraphRelationship,
    NeighborhoodResult,
    SubgraphResult,
    EntityType,
)


class GraphQueryEngine:
    """
    Provides graph query capabilities.
    
    Responsibilities:
    - Neighbor search
    - Dependency traversal
    - Impact traversal
    - Ancestor/descendant search
    - Subgraph extraction
    """
    
    def __init__(self, client: Optional[Neo4jClient] = None):
        self.client = client or Neo4jClient()
        
        # Query history
        self._query_history: List[Dict] = []
        self._cache: Dict[str, QueryResult] = {}
    
    def close(self):
        """Close resources."""
        self.client.close()
    
    # =========================================================================
    # Neighbor Search
    # =========================================================================
    
    def get_neighbors(
        self,
        entity_id: str,
        entity_type: EntityType,
        depth: int = 1,
        relationship_types: Optional[List[str]] = None
    ) -> NeighborhoodResult:
        """
        Get neighbors of a node.
        
        Args:
            entity_id: Entity ID
            entity_type: Entity type
            depth: Search depth
            relationship_types: Filter by relationship types
            
        Returns:
            NeighborhoodResult
        """
        node_id = f"{entity_type.value}_{entity_id}"
        
        # Build Cypher query
        rel_pattern = "[*" + str(depth) + "]"
        if relationship_types:
            rel_pattern = "[:" + "|".join(relationship_types) + rel_pattern
        
        query = f"""
        MATCH (center:{entity_type.value} {{id: $entity_id}})
        MATCH (center){rel_pattern}-(neighbor)
        RETURN center, neighbor
        """
        
        # Execute query
        results = self.client.execute_cypher(query, {"entity_id": entity_id})
        
        # Build result
        center_node = GraphNode(
            id=node_id,
            entity_type=entity_type,
            entity_id=entity_id,
            label=entity_type.value
        )
        
        neighbors = []
        for result in results:
            if "neighbor" in result:
                n = result["neighbor"]
                neighbors.append(GraphNode(
                    id=n.get("id", ""),
                    entity_type=entity_type,
                    entity_id=n.get("id", ""),
                    label=n.get("type", ""),
                    properties=n
                ))
        
        return NeighborhoodResult(
            center_node=center_node,
            neighbors=neighbors,
            depth=depth
        )
    
    # =========================================================================
    # Traversal Queries
    # =========================================================================
    
    def get_upstream(
        self,
        entity_id: str,
        entity_type: EntityType,
        max_depth: int = 10
    ) -> List[GraphNode]:
        """
        Get upstream dependencies.
        
        Args:
            entity_id: Entity ID
            entity_type: Entity type
            max_depth: Maximum traversal depth
            
        Returns:
            List of upstream nodes
        """
        node_id = f"{entity_type.value}_{entity_id}"
        
        query = f"""
        MATCH path = (upstream)-[*1..{max_depth}]->(target:{entity_type.value} {{id: $entity_id}})
        WITH nodes(path) as ns
        UNWIND ns as n
        WITH DISTINCT n
        WHERE n.id <> $entity_id
        RETURN n
        """
        
        results = self.client.execute_cypher(query, {"entity_id": entity_id})
        
        nodes = []
        for result in results:
            if "n" in result:
                n = result["n"]
                nodes.append(GraphNode(
                    id=n.get("id", ""),
                    entity_type=entity_type,
                    entity_id=n.get("id", ""),
                    label=n.get("type", ""),
                    properties=n
                ))
        
        return nodes
    
    def get_downstream(
        self,
        entity_id: str,
        entity_type: EntityType,
        max_depth: int = 10
    ) -> List[GraphNode]:
        """
        Get downstream dependencies.
        
        Args:
            entity_id: Entity ID
            entity_type: Entity type
            max_depth: Maximum traversal depth
            
        Returns:
            List of downstream nodes
        """
        node_id = f"{entity_type.value}_{entity_id}"
        
        query = f"""
        MATCH path = (target:{entity_type.value} {{id: $entity_id}})-[*1..{max_depth}]->(downstream)
        WITH nodes(path) as ns
        UNWIND ns as n
        WITH DISTINCT n
        WHERE n.id <> $entity_id
        RETURN n
        """
        
        results = self.client.execute_cypher(query, {"entity_id": entity_id})
        
        nodes = []
        for result in results:
            if "n" in result:
                n = result["n"]
                nodes.append(GraphNode(
                    id=n.get("id", ""),
                    entity_type=entity_type,
                    entity_id=n.get("id", ""),
                    label=n.get("type", ""),
                    properties=n
                ))
        
        return nodes
    
    # =========================================================================
    # Ancestor/Descendant Search
    # =========================================================================
    
    def get_ancestors(
        self,
        entity_id: str,
        entity_type: EntityType
    ) -> List[GraphNode]:
        """Get all ancestors of a node."""
        return self.get_upstream(entity_id, entity_type)
    
    def get_descendants(
        self,
        entity_id: str,
        entity_type: EntityType
    ) -> List[GraphNode]:
        """Get all descendants of a node."""
        return self.get_downstream(entity_id, entity_type)
    
    # =========================================================================
    # Subgraph Extraction
    # =========================================================================
    
    def extract_subgraph(
        self,
        entity_ids: List[str],
        entity_type: EntityType,
        include_relationships: bool = True
    ) -> SubgraphResult:
        """
        Extract a subgraph containing specified entities.
        
        Args:
            entity_ids: List of entity IDs
            entity_type: Entity type
            include_relationships: Include relationships
            
        Returns:
            SubgraphResult
        """
        query = f"""
        MATCH (n:{entity_type.value})
        WHERE n.id IN $entity_ids
        WITH collect(n) as nodes
        MATCH (n1)-[r]-(n2)
        WHERE n1 IN nodes AND n2 IN nodes
        RETURN nodes, collect(r) as relationships
        """
        
        results = self.client.execute_cypher(query, {"entity_ids": entity_ids})
        
        nodes = []
        relationships = []
        boundary_nodes = []
        
        for result in results:
            if "nodes" in result:
                for n in result["nodes"]:
                    nodes.append(GraphNode(
                        id=n.get("id", ""),
                        entity_type=entity_type,
                        entity_id=n.get("id", ""),
                        label=n.get("type", ""),
                        properties=n
                    ))
            
            if "relationships" in result and include_relationships:
                for r in result["relationships"]:
                    relationships.append(GraphRelationship(
                        id=r.get("id", ""),
                        source_id=r.get("source", ""),
                        target_id=r.get("target", ""),
                        relationship_type=r.get("type", ""),
                        properties=r
                    ))
        
        # Boundary nodes are in subgraph but not in entity_ids
        boundary_ids = set(n.entity_id for n in nodes) - set(entity_ids)
        boundary_nodes = [n for n in nodes if n.entity_id in boundary_ids]
        
        return SubgraphResult(
            nodes=nodes,
            relationships=relationships,
            boundary_nodes=boundary_nodes
        )
    
    # =========================================================================
    # Query Execution
    # =========================================================================
    
    def execute_query(
        self,
        query_type: str,
        cypher_query: str,
        parameters: Optional[Dict] = None,
        use_cache: bool = True
    ) -> QueryResult:
        """
        Execute a Cypher query.
        
        Args:
            query_type: Type of query
            cypher_query: Cypher query
            parameters: Query parameters
            use_cache: Use cached results
            
        Returns:
            QueryResult
        """
        # Check cache
        cache_key = f"{query_type}:{cypher_query}"
        if use_cache and cache_key in self._cache:
            cached_result = self._cache[cache_key]
            cached_result.cached = True
            return cached_result
        
        # Execute query
        start_time = datetime.utcnow()
        raw_results = self.client.execute_cypher(cypher_query, parameters or {})
        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        # Parse results
        nodes = []
        relationships = []
        for result in raw_results:
            for key, value in result.items():
                if isinstance(value, dict):
                    if "type" in value or "source" in value:
                        relationships.append(GraphRelationship(
                            id=value.get("id", ""),
                            source_id=value.get("source", ""),
                            target_id=value.get("target", ""),
                            relationship_type=value.get("type", ""),
                            properties=value
                        ))
                    else:
                        nodes.append(GraphNode(
                            id=value.get("id", ""),
                            entity_type=entity_type,
                            entity_id=value.get("id", ""),
                            label=value.get("type", ""),
                            properties=value
                        ))
        
        query_result = QueryResult(
            query_type=query_type,
            nodes=nodes,
            relationships=relationships,
            execution_time_ms=execution_time,
            result_count=len(nodes) + len(relationships),
            cached=False
        )
        
        # Cache result
        if use_cache:
            self._cache[cache_key] = query_result
        
        # Record in history
        self._query_history.append({
            "query_type": query_type,
            "cypher_query": cypher_query,
            "execution_time_ms": execution_time,
            "result_count": query_result.result_count
        })
        
        return query_result
    
    # =========================================================================
    # Query History
    # =========================================================================
    
    def get_query_history(self, limit: int = 50) -> List[Dict]:
        """Get query history."""
        return sorted(
            self._query_history,
            key=lambda x: x.get("execution_time_ms", 0),
            reverse=True
        )[:limit]
    
    def clear_cache(self) -> None:
        """Clear query cache."""
        self._cache.clear()
