"""
Graph Validator

Validates graph projections, nodes, and relationships.
"""

from typing import Dict, List, Set, Optional
from backend.src.integrations.neo4j.graph_types import (
    GraphNode,
    GraphRelationship,
    EntityType,
    ProjectionJob,
    ProjectionStatus,
)


class GraphValidator:
    """
    Validates graph-related entities.
    
    Checks:
    - Orphan nodes
    - Duplicate projections
    - Relationship consistency
    - Sync conflicts
    - Projection integrity
    """
    
    def __init__(self):
        self.issues: List[str] = []
    
    def validate_graph_node(self, node: GraphNode) -> List[str]:
        """
        Validate a graph node.
        
        Args:
            node: Node to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not node.id:
            issues.append("Node ID is required")
        
        if not node.entity_type:
            issues.append("Entity type is required")
        
        if not node.entity_id:
            issues.append("Entity ID is required")
        
        if not node.label:
            issues.append("Node label is required")
        
        return issues
    
    def validate_relationship(
        self,
        relationship: GraphRelationship,
        existing_nodes: Set[str]
    ) -> List[str]:
        """
        Validate a relationship.
        
        Args:
            relationship: Relationship to validate
            existing_nodes: Set of existing node IDs
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not relationship.id:
            issues.append("Relationship ID is required")
        
        if not relationship.source_id:
            issues.append("Source ID is required")
        
        if not relationship.target_id:
            issues.append("Target ID is required")
        
        if not relationship.relationship_type:
            issues.append("Relationship type is required")
        
        # Check node existence
        if relationship.source_id not in existing_nodes:
            issues.append(f"Source node {relationship.source_id} does not exist")
        
        if relationship.target_id not in existing_nodes:
            issues.append(f"Target node {relationship.target_id} does not exist")
        
        # Self-loop check
        if relationship.source_id == relationship.target_id:
            issues.append("Self-loop relationships are not allowed")
        
        return issues
    
    def check_orphan_nodes(
        self,
        nodes: List[GraphNode],
        relationships: List[GraphRelationship]
    ) -> List[str]:
        """
        Check for orphan nodes (nodes without relationships).
        
        Args:
            nodes: List of nodes
            relationships: List of relationships
            
        Returns:
            List of orphan node IDs
        """
        issues = []
        
        # Build set of connected nodes
        connected = set()
        for rel in relationships:
            connected.add(rel.source_id)
            connected.add(rel.target_id)
        
        # Find orphan nodes
        for node in nodes:
            if node.id not in connected:
                issues.append(f"Orphan node: {node.id} ({node.label})")
        
        return issues
    
    def check_duplicate_projections(
        self,
        entity_type: EntityType,
        filters: Dict,
        existing_jobs: List[ProjectionJob]
    ) -> bool:
        """
        Check for duplicate projection jobs.
        
        Args:
            entity_type: Entity type
            filters: Job filters
            existing_jobs: Existing jobs
            
        Returns:
            True if duplicate exists
        """
        for job in existing_jobs:
            if job.entity_type == entity_type and job.filters == filters:
                if job.status in [ProjectionStatus.PENDING, ProjectionStatus.RUNNING]:
                    return True
        return False
    
    def check_relationship_consistency(
        self,
        relationships: List[GraphRelationship]
    ) -> List[str]:
        """
        Check relationship consistency.
        
        Args:
            relationships: List of relationships
            
        Returns:
            List of consistency issues
        """
        issues = []
        
        # Check for duplicate relationships
        seen = set()
        for rel in relationships:
            key = f"{rel.source_id}|{rel.relationship_type}|{rel.target_id}"
            if key in seen:
                issues.append(f"Duplicate relationship: {key}")
            seen.add(key)
        
        return issues
    
    def check_sync_conflicts(
        self,
        pending_syncs: List[Dict],
        existing_syncs: List[Dict]
    ) -> List[str]:
        """
        Check for sync conflicts.
        
        Args:
            pending_syncs: Pending sync operations
            existing_syncs: Existing sync operations
            
        Returns:
            List of conflict descriptions
        """
        issues = []
        
        # Build map of existing syncs
        existing_map: Dict[str, Dict] = {}
        for sync in existing_syncs:
            key = f"{sync.get('entity_type')}|{sync.get('entity_id')}"
            existing_map[key] = sync
        
        # Check pending syncs
        for pending in pending_syncs:
            key = f"{pending.get('entity_type')}|{pending.get('entity_id')}"
            
            if key in existing_map:
                existing = existing_map[key]
                if existing.get("operation") == "delete" and pending.get("operation") != "delete":
                    issues.append(f"Conflict: Cannot update {key} after delete")
                elif pending.get("operation") == "delete" and existing.get("operation") != "delete":
                    issues.append(f"Conflict: Cannot delete {key} while update is pending")
        
        return issues
    
    def validate_projection_job(self, job: ProjectionJob) -> List[str]:
        """
        Validate a projection job.
        
        Args:
            job: Job to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not job.id:
            issues.append("Job ID is required")
        
        if not job.name:
            issues.append("Job name is required")
        
        if not job.entity_type:
            issues.append("Entity type is required")
        
        return issues
    
    def validate_cypher_query(self, query: str) -> List[str]:
        """
        Validate a Cypher query.
        
        Args:
            query: Cypher query
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not query or not query.strip():
            issues.append("Query is empty")
            return issues
        
        # Check for dangerous operations
        dangerous = ["DROP", "DELETE", "REMOVE"]
        query_upper = query.upper()
        
        for op in dangerous:
            if f" {op} " in query_upper or query_upper.startswith(op):
                issues.append(f"Query contains potentially dangerous operation: {op}")
        
        # Check for balanced parentheses
        if query.count("(") != query.count(")"):
            issues.append("Unbalanced parentheses")
        
        return issues
    
    def get_validation_summary(self) -> Dict:
        """
        Get validation summary.
        
        Returns:
            Summary dictionary
        """
        return {
            "issues": self.issues,
            "issue_count": len(self.issues),
            "has_critical": any("required" in i.lower() for i in self.issues),
        }
