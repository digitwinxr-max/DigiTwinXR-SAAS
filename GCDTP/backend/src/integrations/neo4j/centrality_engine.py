"""
Centrality Engine

Calculates graph centrality metrics.
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from backend.src.integrations.neo4j.neo4j_client import Neo4jClient
from backend.src.integrations.neo4j.graph_types import (
    CentralityScore,
    CentralityType,
    EntityType,
    GraphSnapshot,
)


class CentralityEngine:
    """
    Calculates centrality metrics.
    
    Responsibilities:
    - Degree centrality
    - Betweenness centrality
    - Closeness centrality
    - Eigenvector centrality
    - Criticality ranking
    """
    
    def __init__(self, client: Optional[Neo4jClient] = None):
        self.client = client or Neo4jClient()
    
    def close(self):
        """Close resources."""
        self.client.close()
    
    def compute_degree_centrality(
        self,
        entity_type: EntityType,
        snapshot_id: Optional[str] = None
    ) -> List[CentralityScore]:
        """
        Compute degree centrality.
        
        Degree centrality counts the number of connections for each node.
        
        Args:
            entity_type: Entity type to analyze
            snapshot_id: Optional snapshot ID
            
        Returns:
            List of centrality scores
        """
        # In production, would use Neo4j Graph Data Science library:
        # result = gds.degree(mutation)
        
        # Mock implementation
        return []
    
    def compute_betweenness_centrality(
        self,
        entity_type: EntityType,
        snapshot_id: Optional[str] = None
    ) -> List[CentralityScore]:
        """
        Compute betweenness centrality.
        
        Betweenness centrality measures how often a node lies on the shortest path
        between other nodes.
        
        Args:
            entity_type: Entity type to analyze
            snapshot_id: Optional snapshot ID
            
        Returns:
            List of centrality scores
        """
        return []
    
    def compute_closeness_centrality(
        self,
        entity_type: EntityType,
        snapshot_id: Optional[str] = None
    ) -> List[CentralityScore]:
        """
        Compute closeness centrality.
        
        Closeness centrality measures how close a node is to all other nodes.
        
        Args:
            entity_type: Entity type to analyze
            snapshot_id: Optional snapshot ID
            
        Returns:
            List of centrality scores
        """
        return []
    
    def compute_eigenvector_centrality(
        self,
        entity_type: EntityType,
        snapshot_id: Optional[str] = None
    ) -> List[CentralityScore]:
        """
        Compute eigenvector centrality.
        
        Eigenvector centrality measures the influence of a node based on
        the centrality of its neighbors.
        
        Args:
            entity_type: Entity type to analyze
            snapshot_id: Optional snapshot ID
            
        Returns:
            List of centrality scores
        """
        return []
    
    def compute_pagerank(
        self,
        entity_type: EntityType,
        damping_factor: float = 0.85,
        max_iterations: int = 100,
        snapshot_id: Optional[str] = None
    ) -> List[CentralityScore]:
        """
        Compute PageRank scores.
        
        PageRank measures the importance of nodes based on incoming links.
        
        Args:
            entity_type: Entity type to analyze
            damping_factor: Damping factor (default 0.85)
            max_iterations: Maximum iterations
            snapshot_id: Optional snapshot ID
            
        Returns:
            List of centrality scores
        """
        return []
    
    def compute_criticality_ranking(
        self,
        entity_type: EntityType,
        weights: Optional[Dict[str, float]] = None,
        snapshot_id: Optional[str] = None
    ) -> List[CentralityScore]:
        """
        Compute criticality ranking.
        
        Combines multiple centrality metrics with weights.
        
        Args:
            entity_type: Entity type to analyze
            weights: Weights for each centrality type
            snapshot_id: Optional snapshot ID
            
        Returns:
            List of centrality scores
        """
        # Default weights
        if weights is None:
            weights = {
                "degree": 0.3,
                "betweenness": 0.3,
                "closeness": 0.2,
                "pagerank": 0.2
            }
        
        # Get individual scores
        degree_scores = {
            s.entity_id: s.score for s in self.compute_degree_centrality(entity_type, snapshot_id)
        }
        betweenness_scores = {
            s.entity_id: s.score for s in self.compute_betweenness_centrality(entity_type, snapshot_id)
        }
        closeness_scores = {
            s.entity_id: s.score for s in self.compute_closeness_centrality(entity_type, snapshot_id)
        }
        pagerank_scores = {
            s.entity_id: s.score for s in self.compute_pagerank(entity_type, snapshot_id=snapshot_id)
        }
        
        # Combine scores
        all_entity_ids = set(degree_scores.keys()) | set(betweenness_scores.keys())
        
        combined_scores: List[CentralityScore] = []
        for i, entity_id in enumerate(sorted(all_entity_ids)):
            score = (
                weights.get("degree", 0) * degree_scores.get(entity_id, 0) +
                weights.get("betweenness", 0) * betweenness_scores.get(entity_id, 0) +
                weights.get("closeness", 0) * closeness_scores.get(entity_id, 0) +
                weights.get("pagerank", 0) * pagerank_scores.get(entity_id, 0)
            )
            
            combined_scores.append(CentralityScore(
                id=str(uuid.uuid4()),
                entity_type=entity_type,
                entity_id=entity_id,
                centrality_type=CentralityType.PAGERANK,  # Using pagerank as representative
                score=score,
                rank=i + 1,
                snapshot_id=snapshot_id
            ))
        
        # Sort by score and assign ranks
        combined_scores.sort(key=lambda x: x.score, reverse=True)
        for i, cs in enumerate(combined_scores):
            cs.rank = i + 1
        
        return combined_scores
    
    def rank_assets_by_centrality(
        self,
        snapshot_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Rank assets by criticality.
        
        Args:
            snapshot_id: Optional snapshot ID
            
        Returns:
            List of ranked assets with scores
        """
        scores = self.compute_criticality_ranking(EntityType.ASSET, snapshot_id=snapshot_id)
        
        ranked = []
        for score in scores:
            ranked.append({
                "entity_id": score.entity_id,
                "rank": score.rank,
                "score": score.score,
                "centrality_type": score.centrality_type.value
            })
        
        return ranked


class CentralityAnalyzer:
    """
    Analyzer for centrality results.
    """
    
    def __init__(self):
        self._scores: Dict[str, List[CentralityScore]] = {}
    
    def add_scores(
        self,
        entity_type: EntityType,
        scores: List[CentralityScore]
    ) -> None:
        """Add centrality scores."""
        key = entity_type.value
        self._scores[key] = scores
    
    def get_top_entities(
        self,
        entity_type: EntityType,
        limit: int = 10
    ) -> List[CentralityScore]:
        """Get top entities by centrality."""
        key = entity_type.value
        scores = self._scores.get(key, [])
        return sorted(scores, key=lambda x: x.rank)[:limit]
    
    def get_entity_rank(
        self,
        entity_id: str,
        entity_type: EntityType
    ) -> Optional[int]:
        """Get rank of a specific entity."""
        key = entity_type.value
        scores = self._scores.get(key, [])
        for score in scores:
            if score.entity_id == entity_id:
                return score.rank
        return None
