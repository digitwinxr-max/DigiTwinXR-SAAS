"""Dependency Health Service for calculating dependency-based health penalties."""
from typing import Optional, List, Dict, Any, Set, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..models.asset_relationship import AssetRelationship, RelationshipType
from ..models.health import AssetHealth
from ..models.asset_health_dependency import (
    AssetHealthDependency,
    RelationshipType as ModelRelationshipType,
    RELATIONSHIP_WEIGHTS,
    calculate_penalty,
)
from ..schemas.asset_health_dependency import (
    HealthContributorNode,
    HealthTreeNode,
    HealthTreeResponse,
    HealthContributorsResponse,
)


# Maximum propagation depth
MAX_DEPTH = 3

# Depth decay factors
DEPTH_DECAY = {
    1: 1.0,
    2: 0.5,
    3: 0.25,
}


class DependencyHealthService:
    """Service class for dependency-based health calculations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_dependency_penalty(
        self,
        source_health_score: float,
        relationship_type: str,
        depth: int,
    ) -> float:
        """Calculate the health penalty for a dependency.
        
        Formula:
            penalty = (100 - source_health_score) * weight * depth_decay
        
        Args:
            source_health_score: Health score of source asset (0-100)
            relationship_type: Type of relationship
            depth: Propagation depth (1, 2, or 3)
            
        Returns:
            Penalty amount (0-100)
        """
        try:
            rel_type = ModelRelationshipType(relationship_type)
        except ValueError:
            return 0.0
        
        weight = RELATIONSHIP_WEIGHTS.get(rel_type, 0.0)
        decay = DEPTH_DECAY.get(depth, DEPTH_DECAY[3])
        
        penalty = (100 - source_health_score) * weight * decay
        
        # Clamp to valid range
        return max(0.0, min(100.0, penalty))
    
    def get_related_assets_with_health(
        self,
        asset_id: UUID,
        visited: Optional[Set[UUID]] = None,
        depth: int = 0,
    ) -> List[Dict[str, Any]]:
        """Get all related assets with their health info.
        
        Args:
            asset_id: Starting asset ID
            visited: Set of visited asset IDs
            depth: Current recursion depth
            
        Returns:
            List of related assets with health info
        """
        if visited is None:
            visited = set()
        
        if depth >= MAX_DEPTH or asset_id in visited:
            return []
        
        visited.add(asset_id)
        results = []
        
        # Get relationships where this asset is the parent (downstream)
        child_rels = self.db.query(AssetRelationship).filter(
            AssetRelationship.parent_asset_id == asset_id
        ).all()
        
        for rel in child_rels:
            if rel.child_asset_id in visited:
                continue
            
            rel_type_str = rel.relationship_type.value if hasattr(rel.relationship_type, 'value') else rel.relationship_type
            
            try:
                rel_type = ModelRelationshipType(rel_type_str)
            except ValueError:
                continue
            
            # Skip monitors (no health impact)
            if rel_type == ModelRelationshipType.MONITORS:
                continue
            
            child_health = self.db.query(AssetHealth).filter(
                AssetHealth.asset_id == rel.child_asset_id
            ).first()
            
            results.append({
                'asset_id': rel.child_asset_id,
                'relationship_type': rel_type_str,
                'relationship_type_enum': rel_type,
                'depth': depth + 1,
                'health_score': child_health.health_score if child_health else 100.0,
                'health_status': child_health.health_status if child_health else 'HEALTHY',
            })
            
            # Recursively get downstream
            downstream = self.get_related_assets_with_health(
                rel.child_asset_id,
                visited.copy(),
                depth + 1,
            )
            results.extend(downstream)
        
        # Get relationships where this asset is the child (upstream)
        parent_rels = self.db.query(AssetRelationship).filter(
            AssetRelationship.child_asset_id == asset_id
        ).all()
        
        for rel in parent_rels:
            if rel.parent_asset_id in visited:
                continue
            
            rel_type_str = rel.relationship_type.value if hasattr(rel.relationship_type, 'value') else rel.relationship_type
            
            try:
                rel_type = ModelRelationshipType(rel_type_str)
            except ValueError:
                continue
            
            # Skip monitors (no health impact)
            if rel_type == ModelRelationshipType.MONITORS:
                continue
            
            parent_health = self.db.query(AssetHealth).filter(
                AssetHealth.asset_id == rel.parent_asset_id
            ).first()
            
            # For contains relationship, propagation goes UP (parent affected by child)
            # For other relationships, propagation goes BOTH
            if rel_type == ModelRelationshipType.CONTAINS:
                # Contains: propagate upward - parent is affected by child
                results.append({
                    'asset_id': rel.parent_asset_id,
                    'relationship_type': rel_type_str,
                    'relationship_type_enum': rel_type,
                    'depth': depth + 1,
                    'health_score': parent_health.health_score if parent_health else 100.0,
                    'health_status': parent_health.health_status if parent_health else 'HEALTHY',
                })
                
                # Recursively get upstream
                upstream = self.get_related_assets_with_health(
                    rel.parent_asset_id,
                    visited.copy(),
                    depth + 1,
                )
                results.extend(upstream)
            else:
                # Other relationships: propagate bidirectionally
                # Check connected_to
                if rel_type == ModelRelationshipType.CONNECTED_TO:
                    results.append({
                        'asset_id': rel.parent_asset_id,
                        'relationship_type': rel_type_str,
                        'relationship_type_enum': rel_type,
                        'depth': depth + 1,
                        'health_score': parent_health.health_score if parent_health else 100.0,
                        'health_status': parent_health.health_status if parent_health else 'HEALTHY',
                    })
                    
                    upstream = self.get_related_assets_with_health(
                        rel.parent_asset_id,
                        visited.copy(),
                        depth + 1,
                    )
                    results.extend(upstream)
        
        return results
    
    def recalculate_network_health(self) -> Tuple[int, int]:
        """Recalculate health for all assets based on dependencies.
        
        Returns:
            Tuple of (assets_recalculated, penalties_updated)
        """
        # Get all assets
        from ..models.asset import Asset
        all_assets = self.db.query(Asset).all()
        
        assets_recalculated = 0
        penalties_updated = 0
        
        # Clear existing dependencies
        self.db.query(AssetHealthDependency).delete()
        self.db.commit()
        
        # Recalculate for each asset
        for asset in all_assets:
            penalties = self._calculate_penalties_for_asset(asset.id)
            
            # Store penalties
            for penalty_data in penalties:
                dep = AssetHealthDependency(
                    asset_id=penalty_data['asset_id'],
                    source_asset_id=penalty_data['source_asset_id'],
                    relationship_type=penalty_data['relationship_type'],
                    impact_weight=penalty_data['weight'],
                    penalty=penalty_data['penalty'],
                    depth=penalty_data['depth'],
                )
                self.db.add(dep)
                penalties_updated += 1
            
            # Update asset health with dependency penalties
            self._update_asset_health(asset.id)
            assets_recalculated += 1
        
        self.db.commit()
        
        return assets_recalculated, penalties_updated
    
    def _calculate_penalties_for_asset(
        self,
        asset_id: UUID,
    ) -> List[Dict[str, Any]]:
        """Calculate all penalties that affect an asset.
        
        Args:
            asset_id: The asset to calculate penalties for
            
        Returns:
            List of penalty data dictionaries
        """
        penalties = []
        visited = set([asset_id])
        
        # Get source assets through relationships
        related = self.get_related_assets_with_health(asset_id, visited.copy(), 0)
        
        for rel in related:
            source_id = rel['asset_id']
            
            # Skip if already processed
            if (asset_id, source_id, rel['relationship_type']) in [
                (p['asset_id'], p['source_asset_id'], p['relationship_type']) 
                for p in penalties
            ]:
                continue
            
            penalty = self.calculate_dependency_penalty(
                rel['health_score'],
                rel['relationship_type'],
                rel['depth'],
            )
            
            if penalty > 0:
                penalties.append({
                    'asset_id': asset_id,
                    'source_asset_id': source_id,
                    'relationship_type': rel['relationship_type'],
                    'weight': RELATIONSHIP_WEIGHTS.get(rel['relationship_type_enum'], 0.0),
                    'penalty': penalty,
                    'depth': rel['depth'],
                })
        
        return penalties
    
    def _update_asset_health(self, asset_id: UUID) -> Optional[AssetHealth]:
        """Update an asset's health with dependency penalties.
        
        Args:
            asset_id: Asset to update
            
        Returns:
            Updated AssetHealth or None
        """
        # Get current health
        health = self.db.query(AssetHealth).filter(
            AssetHealth.asset_id == asset_id
        ).first()
        
        if not health:
            return None
        
        # Calculate total dependency penalty
        dependencies = self.db.query(AssetHealthDependency).filter(
            AssetHealthDependency.asset_id == asset_id
        ).all()
        
        total_dependency_penalty = sum(d.penalty for d in dependencies)
        
        # Calculate new health score
        # Health = base_health - local_penalty - dependency_penalty
        base_health = 100.0
        new_score = base_health - health.penalty + total_dependency_penalty
        
        # Clamp to valid range
        new_score = max(0.0, min(100.0, new_score))
        
        # Update health
        health.health_score = new_score
        
        # Update status
        if new_score >= 80:
            health.health_status = "HEALTHY"
        elif new_score >= 40:
            health.health_status = "DEGRADED"
        else:
            health.health_status = "CRITICAL"
        
        self.db.commit()
        self.db.refresh(health)
        
        return health
    
    def get_dependency_health(self, asset_id: UUID) -> List[Dict[str, Any]]:
        """Get all dependency penalties for an asset.
        
        Args:
            asset_id: Asset ID
            
        Returns:
            List of dependency penalty info
        """
        dependencies = self.db.query(AssetHealthDependency).filter(
            AssetHealthDependency.asset_id == asset_id
        ).all()
        
        results = []
        for dep in dependencies:
            from ..models.asset import Asset
            source_asset = self.db.query(Asset).filter(
                Asset.id == dep.source_asset_id
            ).first()
            
            results.append({
                'id': dep.id,
                'asset_id': dep.asset_id,
                'source_asset_id': dep.source_asset_id,
                'source_asset_name': source_asset.name if source_asset else None,
                'relationship_type': dep.relationship_type.value if hasattr(dep.relationship_type, 'value') else dep.relationship_type,
                'impact_weight': dep.impact_weight,
                'penalty': dep.penalty,
                'depth': dep.depth,
                'created_at': dep.created_at,
            })
        
        return results
    
    def build_health_tree(
        self,
        asset_id: UUID,
        max_depth: int = 3,
    ) -> Optional[HealthTreeResponse]:
        """Build a hierarchical health tree for an asset.
        
        Args:
            asset_id: Root asset ID
            max_depth: Maximum depth to traverse
            
        Returns:
            HealthTreeResponse with hierarchical structure
        """
        from ..models.asset import Asset
        
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            return None
        
        health = self.db.query(AssetHealth).filter(
            AssetHealth.asset_id == asset_id
        ).first()
        
        current_score = health.health_score if health else 100.0
        current_status = health.health_status if health else 'HEALTHY'
        local_penalty = health.penalty if health else 0.0
        
        # Get dependency penalties
        dependencies = self.get_dependency_health(asset_id)
        total_dependency_penalty = sum(d['penalty'] for d in dependencies)
        
        # Build contributors
        contributors = []
        for dep in dependencies:
            source_health = self.db.query(AssetHealth).filter(
                AssetHealth.asset_id == dep['source_asset_id']
            ).first()
            
            contributor = HealthContributorNode(
                asset_id=dep['source_asset_id'],
                asset_name=dep['source_asset_name'] or 'Unknown',
                health_score=source_health.health_score if source_health else 100.0,
                health_status=source_health.health_status if source_health else 'HEALTHY',
                penalty=dep['penalty'],
                depth=dep['depth'],
                relationship_type=dep['relationship_type'],
                is_source=True,
                children=[],
            )
            contributors.append(contributor)
        
        # Build children recursively
        children = self._build_health_children(
            asset_id, 
            visited=set([asset_id]),
            depth=0,
            max_depth=max_depth,
        )
        
        return HealthTreeResponse(
            asset_id=asset_id,
            asset_name=asset.name,
            asset_type=asset.asset_type,
            health_score=current_score,
            health_status=current_status,
            local_penalty=local_penalty,
            dependency_penalty=total_dependency_penalty,
            total_penalty=local_penalty + total_dependency_penalty,
            contributors=contributors,
            depth=0,
            max_depth=max_depth,
        )
    
    def _build_health_children(
        self,
        asset_id: UUID,
        visited: Set[UUID],
        depth: int,
        max_depth: int,
    ) -> List[HealthTreeNode]:
        """Recursively build health tree children.
        
        Args:
            asset_id: Parent asset ID
            visited: Set of visited asset IDs
            depth: Current depth
            max_depth: Maximum depth
            
        Returns:
            List of HealthTreeNode for children
        """
        if depth >= max_depth:
            return []
        
        visited.add(asset_id)
        children = []
        
        # Get child relationships
        rels = self.db.query(AssetRelationship).filter(
            AssetRelationship.parent_asset_id == asset_id
        ).all()
        
        from ..models.asset import Asset
        
        for rel in rels:
            if rel.child_asset_id in visited:
                continue
            
            child_asset = self.db.query(Asset).filter(
                Asset.id == rel.child_asset_id
            ).first()
            
            if not child_asset:
                continue
            
            child_health = self.db.query(AssetHealth).filter(
                AssetHealth.asset_id == rel.child_asset_id
            ).first()
            
            child_score = child_health.health_score if child_health else 100.0
            child_status = child_health.health_status if child_health else 'HEALTHY'
            child_local_penalty = child_health.penalty if child_health else 0.0
            
            # Get child's dependencies
            child_deps = self.get_dependency_health(rel.child_asset_id)
            child_dependency_penalty = sum(d['penalty'] for d in child_deps)
            
            node = HealthTreeNode(
                asset_id=rel.child_asset_id,
                asset_name=child_asset.name,
                asset_type=child_asset.asset_type,
                health_score=child_score,
                health_status=child_status,
                local_penalty=child_local_penalty,
                dependency_penalty=child_dependency_penalty,
                total_penalty=child_local_penalty + child_dependency_penalty,
                contributors=[],
                children=self._build_health_children(
                    rel.child_asset_id,
                    visited.copy(),
                    depth + 1,
                    max_depth,
                ),
            )
            children.append(node)
        
        return children
    
    def clear_dependency_penalties(self, asset_id: Optional[UUID] = None) -> int:
        """Clear dependency penalties.
        
        Args:
            asset_id: Optional specific asset to clear, or None for all
            
        Returns:
            Number of penalties cleared
        """
        if asset_id:
            count = self.db.query(AssetHealthDependency).filter(
                AssetHealthDependency.asset_id == asset_id
            ).delete()
        else:
            count = self.db.query(AssetHealthDependency).delete()
        
        self.db.commit()
        return count
    
    def get_contributors(self, asset_id: UUID) -> Optional[HealthContributorsResponse]:
        """Get health contributors for an asset.
        
        Args:
            asset_id: Asset ID
            
        Returns:
            HealthContributorsResponse or None
        """
        from ..models.asset import Asset
        
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            return None
        
        health = self.db.query(AssetHealth).filter(
            AssetHealth.asset_id == asset_id
        ).first()
        
        current_score = health.health_score if health else 100.0
        
        # Get contributors
        dependencies = self.get_dependency_health(asset_id)
        contributors = []
        
        for dep in dependencies:
            source_health = self.db.query(AssetHealth).filter(
                AssetHealth.asset_id == dep['source_asset_id']
            ).first()
            
            contributor = HealthContributorNode(
                asset_id=dep['source_asset_id'],
                asset_name=dep['source_asset_name'] or 'Unknown',
                health_score=source_health.health_score if source_health else 100.0,
                health_status=source_health.health_status if source_health else 'HEALTHY',
                penalty=dep['penalty'],
                depth=dep['depth'],
                relationship_type=dep['relationship_type'],
                is_source=True,
            )
            contributors.append(contributor)
        
        # Sort by penalty (highest first)
        contributors.sort(key=lambda x: x.penalty, reverse=True)
        
        total_penalty = sum(c.penalty for c in contributors)
        
        return HealthContributorsResponse(
            asset_id=asset_id,
            asset_name=asset.name,
            current_health_score=current_score,
            total_dependency_penalty=total_penalty,
            contributors=contributors,
            count=len(contributors),
        )