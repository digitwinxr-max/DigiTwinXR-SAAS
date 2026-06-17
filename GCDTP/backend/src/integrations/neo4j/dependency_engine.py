"""
Dependency Engine

Analyzes dependency chains and impact analysis.
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from backend.src.integrations.neo4j.neo4j_client import Neo4jClient
from backend.src.integrations.neo4j.graph_types import (
    DependencyChain,
    ChainType,
    EntityType,
    GraphNode,
    PathAnalysis,
    PathType,
)


class DependencyEngine:
    """
    Analyzes dependency chains.
    
    Responsibilities:
    - Dependency chain analysis
    - Failure impact chains
    - Cascade chain analysis
    - Upstream/downstream traversal
    """
    
    def __init__(self, client: Optional[Neo4jClient] = None):
        self.client = client or Neo4jClient()
    
    def close(self):
        """Close resources."""
        self.client.close()
    
    def get_dependency_chain(
        self,
        entity_id: str,
        entity_type: EntityType,
        chain_type: ChainType = ChainType.DEPENDENCY,
        max_depth: int = 10
    ) -> DependencyChain:
        """
        Get dependency chain for an entity.
        
        Args:
            entity_id: Entity ID
            entity_type: Entity type
            chain_type: Type of chain
            max_depth: Maximum chain depth
            
        Returns:
            DependencyChain
        """
        if chain_type == ChainType.FAILURE_IMPACT:
            return self._get_failure_impact_chain(entity_id, entity_type, max_depth)
        elif chain_type == ChainType.CASCADE:
            return self._get_cascade_chain(entity_id, entity_type, max_depth)
        else:
            return self._get_basic_dependency_chain(entity_id, entity_type, max_depth)
    
    def _get_basic_dependency_chain(
        self,
        entity_id: str,
        entity_type: EntityType,
        max_depth: int
    ) -> DependencyChain:
        """Get basic dependency chain."""
        query = f"""
        MATCH path = (start:{entity_type.value} {{id: $entity_id}})-[*1..{max_depth}]->(end)
        WITH path, length(path) as pathLength
        ORDER BY pathLength
        LIMIT 1
        RETURN nodes(path) as chain, pathLength
        """
        
        results = self.client.execute_cypher(query, {"entity_id": entity_id})
        
        chain_data = []
        if results:
            nodes = results[0].get("chain", [])
            chain_data = [
                {"entity_id": n.get("id"), "entity_type": entity_type.value, "depth": i}
                for i, n in enumerate(nodes)
            ]
        
        return DependencyChain(
            id=str(uuid.uuid4()),
            chain_type=ChainType.DEPENDENCY,
            start_entity_id=entity_id,
            chain_data=chain_data,
            chain_length=len(chain_data)
        )
    
    def _get_failure_impact_chain(
        self,
        entity_id: str,
        entity_type: EntityType,
        max_depth: int
    ) -> DependencyChain:
        """
        Get failure impact chain.
        
        Shows what would be affected if this entity fails.
        """
        query = f"""
        MATCH path = (start:{entity_type.value} {{id: $entity_id}})-[:DEPENDS_ON|FEEDS_INTO*1..{max_depth}]->(impacted)
        RETURN start, impacted, length(path) as depth
        ORDER BY depth
        """
        
        results = self.client.execute_cypher(query, {"entity_id": entity_id})
        
        chain_data = []
        if results:
            impacted = results[0].get("impacted", [])
            chain_data = [
                {"entity_id": impacted.get("id"), "entity_type": impacted.get("type"), "depth": i}
                for i, node in enumerate(impacted) if isinstance(node, dict)
            ]
        
        return DependencyChain(
            id=str(uuid.uuid4()),
            chain_type=ChainType.FAILURE_IMPACT,
            start_entity_id=entity_id,
            chain_data=chain_data,
            chain_length=len(chain_data)
        )
    
    def _get_cascade_chain(
        self,
        entity_id: str,
        entity_type: EntityType,
        max_depth: int
    ) -> DependencyChain:
        """
        Get cascade chain.
        
        Shows the cascade effect of failures.
        """
        query = f"""
        MATCH path = (start:{entity_type.value} {{id: $entity_id}})-[*1..{max_depth}]->(cascade)
        WITH path
        WHERE all(r IN relationships(path) WHERE r.critical = true)
        RETURN nodes(path) as chain, length(path) as depth
        """
        
        results = self.client.execute_cypher(query, {"entity_id": entity_id})
        
        chain_data = []
        if results:
            nodes = results[0].get("chain", [])
            chain_data = [
                {"entity_id": n.get("id"), "entity_type": entity_type.value, "depth": i}
                for i, n in enumerate(nodes)
            ]
        
        return DependencyChain(
            id=str(uuid.uuid4()),
            chain_type=ChainType.CASCADE,
            start_entity_id=entity_id,
            chain_data=chain_data,
            chain_length=len(chain_data)
        )
    
    # =========================================================================
    # Traversal Methods
    # =========================================================================
    
    def get_upstream_dependencies(
        self,
        entity_id: str,
        entity_type: EntityType,
        max_depth: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get upstream dependencies.
        
        Args:
            entity_id: Entity ID
            entity_type: Entity type
            max_depth: Maximum depth
            
        Returns:
            List of upstream entities with depth
        """
        query = f"""
        MATCH path = (upstream)-[*1..{max_depth}]->(target:{entity_type.value} {{id: $entity_id}})
        WITH upstream, min(length(path)) as minDepth
        RETURN upstream, minDepth as depth
        ORDER BY depth
        """
        
        results = self.client.execute_cypher(query, {"entity_id": entity_id})
        
        upstream = []
        for result in results:
            if "upstream" in result:
                node = result["upstream"]
                upstream.append({
                    "entity_id": node.get("id"),
                    "entity_type": entity_type.value,
                    "depth": result.get("depth", 0)
                })
        
        return upstream
    
    def get_downstream_dependencies(
        self,
        entity_id: str,
        entity_type: EntityType,
        max_depth: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get downstream dependencies.
        
        Args:
            entity_id: Entity ID
            entity_type: Entity type
            max_depth: Maximum depth
            
        Returns:
            List of downstream entities with depth
        """
        query = f"""
        MATCH path = (target:{entity_type.value} {{id: $entity_id}})-[*1..{max_depth}]->(downstream)
        WITH downstream, min(length(path)) as minDepth
        RETURN downstream, minDepth as depth
        ORDER BY depth
        """
        
        results = self.client.execute_cypher(query, {"entity_id": entity_id})
        
        downstream = []
        for result in results:
            if "downstream" in result:
                node = result["downstream"]
                downstream.append({
                    "entity_id": node.get("id"),
                    "entity_type": entity_type.value,
                    "depth": result.get("depth", 0)
                })
        
        return downstream
    
    def get_all_dependencies(
        self,
        entity_id: str,
        entity_type: EntityType,
        max_depth: int = 10
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all dependencies (upstream and downstream).
        
        Args:
            entity_id: Entity ID
            entity_type: Entity type
            max_depth: Maximum depth
            
        Returns:
            Dictionary with upstream and downstream
        """
        return {
            "upstream": self.get_upstream_dependencies(entity_id, entity_type, max_depth),
            "downstream": self.get_downstream_dependencies(entity_id, entity_type, max_depth)
        }
    
    # =========================================================================
    # Impact Analysis
    # =========================================================================
    
    def analyze_failure_impact(
        self,
        entity_id: str,
        entity_type: EntityType,
        max_depth: int = 10
    ) -> Dict[str, Any]:
        """
        Analyze impact of entity failure.
        
        Args:
            entity_id: Entity ID
            entity_type: Entity type
            max_depth: Maximum impact depth
            
        Returns:
            Impact analysis results
        """
        chain = self.get_dependency_chain(
            entity_id, entity_type, ChainType.FAILURE_IMPACT, max_depth
        )
        
        # Group by entity type
        impact_by_type: Dict[str, int] = {}
        for item in chain.chain_data:
            etype = item.get("entity_type", "unknown")
            impact_by_type[etype] = impact_by_type.get(etype, 0) + 1
        
        return {
            "entity_id": entity_id,
            "entity_type": entity_type.value,
            "impacted_count": len(chain.chain_data),
            "impact_by_type": impact_by_type,
            "max_depth": max_depth,
            "chain": chain.chain_data
        }
    
    def analyze_cascade_effects(
        self,
        entity_id: str,
        entity_type: EntityType,
        max_depth: int = 10
    ) -> Dict[str, Any]:
        """
        Analyze cascade effects.
        
        Args:
            entity_id: Entity ID
            entity_type: Entity type
            max_depth: Maximum cascade depth
            
        Returns:
            Cascade analysis results
        """
        chain = self.get_dependency_chain(
            entity_id, entity_type, ChainType.CASCADE, max_depth
        )
        
        # Find cascade points
        cascade_points = [
            item for item in chain.chain_data
            if item.get("critical", False)
        ]
        
        return {
            "entity_id": entity_id,
            "entity_type": entity_type.value,
            "cascade_points": cascade_points,
            "total_cascade": len(chain.chain_data),
            "chain": chain.chain_data
        }
