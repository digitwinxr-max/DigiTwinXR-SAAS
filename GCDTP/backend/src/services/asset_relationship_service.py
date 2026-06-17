"""Asset Relationship Service for managing asset hierarchies."""
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError

from ..models.asset_relationship import AssetRelationship, RelationshipType as ModelRelationshipType
from ..models.asset import Asset
from ..models.health import AssetHealth
from ..schemas.asset_relationship import (
    AssetRelationshipCreate,
    AssetRelationshipGraphNode,
    AssetRelationshipGraphResponse,
)


class AssetRelationshipService:
    """Service class for asset relationship operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_relationship(
        self, 
        relationship_data: AssetRelationshipCreate
    ) -> AssetRelationship:
        """Create a new asset relationship.
        
        Args:
            relationship_data: Relationship creation data
            
        Returns:
            The created AssetRelationship
            
        Raises:
            ValueError: If validation fails
            IntegrityError: If relationship already exists
        """
        # Validate assets exist
        parent = self.db.query(Asset).filter(
            Asset.id == relationship_data.parent_asset_id
        ).first()
        if not parent:
            raise ValueError(f"Parent asset not found: {relationship_data.parent_asset_id}")
        
        child = self.db.query(Asset).filter(
            Asset.id == relationship_data.child_asset_id
        ).first()
        if not child:
            raise ValueError(f"Child asset not found: {relationship_data.child_asset_id}")
        
        # Check for self-reference
        if relationship_data.parent_asset_id == relationship_data.child_asset_id:
            raise ValueError("Cannot create self-referencing relationship")
        
        # Create relationship
        relationship = AssetRelationship(
            parent_asset_id=relationship_data.parent_asset_id,
            child_asset_id=relationship_data.child_asset_id,
            relationship_type=relationship_data.relationship_type.value,
        )
        
        try:
            self.db.add(relationship)
            self.db.commit()
            self.db.refresh(relationship)
            return relationship
        except IntegrityError as e:
            self.db.rollback()
            if "unique_relationship" in str(e).lower():
                raise ValueError("Relationship already exists")
            raise
    
    def delete_relationship(self, relationship_id: UUID) -> bool:
        """Delete an asset relationship.
        
        Args:
            relationship_id: ID of the relationship to delete
            
        Returns:
            True if deleted, False if not found
        """
        relationship = self.db.query(AssetRelationship).filter(
            AssetRelationship.id == relationship_id
        ).first()
        
        if not relationship:
            return False
        
        self.db.delete(relationship)
        self.db.commit()
        return True
    
    def get_relationship(self, relationship_id: UUID) -> Optional[AssetRelationship]:
        """Get a relationship by ID."""
        return self.db.query(AssetRelationship).filter(
            AssetRelationship.id == relationship_id
        ).first()
    
    def get_relationships(
        self,
        skip: int = 0,
        limit: int = 100,
        parent_asset_id: Optional[UUID] = None,
        child_asset_id: Optional[UUID] = None,
        relationship_type: Optional[str] = None,
    ) -> tuple[List[AssetRelationship], int]:
        """Get all relationships with optional filtering.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            parent_asset_id: Filter by parent asset
            child_asset_id: Filter by child asset
            relationship_type: Filter by relationship type
            
        Returns:
            Tuple of (relationships list, total count)
        """
        query = self.db.query(AssetRelationship)
        
        if parent_asset_id:
            query = query.filter(AssetRelationship.parent_asset_id == parent_asset_id)
        if child_asset_id:
            query = query.filter(AssetRelationship.child_asset_id == child_asset_id)
        if relationship_type:
            query = query.filter(AssetRelationship.relationship_type == relationship_type)
        
        total = query.count()
        relationships = query.offset(skip).limit(limit).all()
        
        return relationships, total
    
    def get_children(
        self, 
        asset_id: UUID,
        relationship_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get all children (direct descendants) of an asset.
        
        Args:
            asset_id: The parent asset ID
            relationship_type: Optional filter by relationship type
            
        Returns:
            List of child relationships with asset info
        """
        query = self.db.query(AssetRelationship).filter(
            AssetRelationship.parent_asset_id == asset_id
        )
        
        if relationship_type:
            query = query.filter(AssetRelationship.relationship_type == relationship_type)
        
        relationships = query.all()
        
        result = []
        for rel in relationships:
            child_asset = self.db.query(Asset).filter(Asset.id == rel.child_asset_id).first()
            health = self.db.query(AssetHealth).filter(AssetHealth.asset_id == rel.child_asset_id).first()
            
            result.append({
                "id": rel.id,
                "child_asset_id": rel.child_asset_id,
                "child_asset_name": child_asset.name if child_asset else None,
                "child_asset_type": child_asset.asset_type if child_asset else None,
                "relationship_type": rel.relationship_type,
                "health_status": health.health_status if health else None,
                "health_score": health.health_score if health else None,
                "created_at": rel.created_at,
            })
        
        return result
    
    def get_parents(
        self, 
        asset_id: UUID,
        relationship_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get all parents (direct ancestors) of an asset.
        
        Args:
            asset_id: The child asset ID
            relationship_type: Optional filter by relationship type
            
        Returns:
            List of parent relationships with asset info
        """
        query = self.db.query(AssetRelationship).filter(
            AssetRelationship.child_asset_id == asset_id
        )
        
        if relationship_type:
            query = query.filter(AssetRelationship.relationship_type == relationship_type)
        
        relationships = query.all()
        
        result = []
        for rel in relationships:
            parent_asset = self.db.query(Asset).filter(Asset.id == rel.parent_asset_id).first()
            health = self.db.query(AssetHealth).filter(AssetHealth.asset_id == rel.parent_asset_id).first()
            
            result.append({
                "id": rel.id,
                "parent_asset_id": rel.parent_asset_id,
                "parent_asset_name": parent_asset.name if parent_asset else None,
                "parent_asset_type": parent_asset.asset_type if parent_asset else None,
                "relationship_type": rel.relationship_type,
                "health_status": health.health_status if health else None,
                "health_score": health.health_score if health else None,
                "created_at": rel.created_at,
            })
        
        return result
    
    def _build_graph_node(
        self,
        asset_id: UUID,
        visited: set,
        max_depth: int = 10,
        current_depth: int = 0,
    ) -> Optional[AssetRelationshipGraphNode]:
        """Recursively build a graph node for an asset.
        
        Args:
            asset_id: The asset ID to build node for
            visited: Set of already visited asset IDs (for cycle prevention)
            max_depth: Maximum recursion depth
            current_depth: Current recursion depth
            
        Returns:
            GraphNode for the asset, or None if asset not found
        """
        if current_depth >= max_depth:
            return None
        
        if asset_id in visited:
            return None
        
        visited.add(asset_id)
        
        # Get asset info
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            return None
        
        # Get health info
        health = self.db.query(AssetHealth).filter(AssetHealth.asset_id == asset_id).first()
        
        node = AssetRelationshipGraphNode(
            asset_id=asset_id,
            asset_name=asset.name,
            asset_type=asset.asset_type,
            health_status=health.health_status if health else None,
            health_score=health.health_score if health else None,
            children=[],
        )
        
        # Recursively build children
        children_rels = self.db.query(AssetRelationship).filter(
            AssetRelationship.parent_asset_id == asset_id
        ).all()
        
        for rel in children_rels:
            child_node = self._build_graph_node(
                rel.child_asset_id,
                visited.copy(),  # Copy to allow branching
                max_depth,
                current_depth + 1,
            )
            if child_node:
                child_node.relationship_type = rel.relationship_type
                node.children.append(child_node)
        
        return node
    
    def get_graph(
        self,
        asset_id: UUID,
        direction: str = "down",
        max_depth: int = 10,
    ) -> AssetRelationshipGraphResponse:
        """Get the relationship graph for an asset.
        
        Args:
            asset_id: The root asset ID
            direction: "down" for children, "up" for parents, "both" for both
            max_depth: Maximum depth to traverse
            
        Returns:
            GraphResponse with hierarchical structure
        """
        # Get root asset info
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise ValueError(f"Asset not found: {asset_id}")
        
        health = self.db.query(AssetHealth).filter(AssetHealth.asset_id == asset_id).first()
        
        response = AssetRelationshipGraphResponse(
            asset_id=asset_id,
            asset_name=asset.name,
            asset_type=asset.asset_type,
            health_status=health.health_status if health else None,
            health_score=health.health_score if health else None,
            children=[],
            parents=[],
            depth=0,
        )
        
        visited = set()
        
        if direction in ("down", "both"):
            children = []
            max_actual_depth = [0]
            
            def build_children(parent_id: UUID, parent_visited: set, depth: int):
                if depth >= max_depth:
                    return None
                
                if parent_id in parent_visited:
                    return None
                
                parent_visited.add(parent_id)
                max_actual_depth[0] = max(max_actual_depth[0], depth)
                
                child_rels = self.db.query(AssetRelationship).filter(
                    AssetRelationship.parent_asset_id == parent_id
                ).all()
                
                result = []
                for rel in child_rels:
                    child_asset = self.db.query(Asset).filter(
                        Asset.id == rel.child_asset_id
                    ).first()
                    child_health = self.db.query(AssetHealth).filter(
                        AssetHealth.asset_id == rel.child_asset_id
                    ).first()
                    
                    node = AssetRelationshipGraphNode(
                        asset_id=rel.child_asset_id,
                        asset_name=child_asset.name if child_asset else "Unknown",
                        asset_type=child_asset.asset_type if child_asset else None,
                        health_status=child_health.health_status if child_health else None,
                        health_score=child_health.health_score if child_health else None,
                        relationship_type=rel.relationship_type,
                        children=[],
                    )
                    
                    node.children = build_children(
                        rel.child_asset_id,
                        parent_visited.copy(),
                        depth + 1,
                    ) or []
                    
                    result.append(node)
                
                return result
            
            response.children = build_children(asset_id, visited.copy(), 0) or []
            response.depth = max_actual_depth[0] + 1
        
        if direction in ("up", "both"):
            parents = []
            
            def build_parents(child_id: UUID, child_visited: set, depth: int):
                if depth >= max_depth:
                    return None
                
                if child_id in child_visited:
                    return None
                
                child_visited.add(child_id)
                
                parent_rels = self.db.query(AssetRelationship).filter(
                    AssetRelationship.child_asset_id == child_id
                ).all()
                
                result = []
                for rel in parent_rels:
                    parent_asset = self.db.query(Asset).filter(
                        Asset.id == rel.parent_asset_id
                    ).first()
                    parent_health = self.db.query(AssetHealth).filter(
                        AssetHealth.asset_id == rel.parent_asset_id
                    ).first()
                    
                    node = AssetRelationshipGraphNode(
                        asset_id=rel.parent_asset_id,
                        asset_name=parent_asset.name if parent_asset else "Unknown",
                        asset_type=parent_asset.asset_type if parent_asset else None,
                        health_status=parent_health.health_status if parent_health else None,
                        health_score=parent_health.health_score if parent_health else None,
                        relationship_type=rel.relationship_type,
                        children=[],
                    )
                    
                    node.children = build_parents(
                        rel.parent_asset_id,
                        child_visited.copy(),
                        depth + 1,
                    ) or []
                    
                    result.append(node)
                
                return result
            
            response.parents = build_parents(asset_id, set([asset_id]), 0) or []
        
        return response
    
    def check_relationship_exists(
        self,
        parent_asset_id: UUID,
        child_asset_id: UUID,
        relationship_type: Optional[str] = None,
    ) -> bool:
        """Check if a relationship already exists.
        
        Args:
            parent_asset_id: Parent asset ID
            child_asset_id: Child asset ID
            relationship_type: Optional relationship type filter
            
        Returns:
            True if exists, False otherwise
        """
        query = self.db.query(AssetRelationship).filter(
            and_(
                AssetRelationship.parent_asset_id == parent_asset_id,
                AssetRelationship.child_asset_id == child_asset_id,
            )
        )
        
        if relationship_type:
            query = query.filter(AssetRelationship.relationship_type == relationship_type)
        
        return query.first() is not None
    
    def get_all_relationship_types(self) -> List[str]:
        """Get all available relationship types.
        
        Returns:
            List of relationship type values
        """
        return [rt.value for rt in ModelRelationshipType]