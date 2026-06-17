"""Failure Propagation Service for cascading failure analysis."""
from typing import Optional, List, Dict, Any, Set, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..models.asset_relationship import AssetRelationship, RelationshipType
from ..models.propagated_event import PropagatedEvent, PropagationType
from ..models.asset import Asset
from ..models.event import Event
from ..models.health import AssetHealth
from ..schemas.propagated_event import ImpactChainNode, ImpactChainResponse


# Default maximum propagation depth
DEFAULT_MAX_DEPTH = 3

# Relationship propagation rules
PROPAGATION_RULES = {
    # contains → propagate upward (child affects parent)
    RelationshipType.CONTAINS: {
        'direction': 'up',
        'propagation_type': PropagationType.CHILD_FAILURE,
    },
    # feeds → propagate downstream (source affects destination)
    RelationshipType.FEEDS: {
        'direction': 'down',
        'propagation_type': PropagationType.DOWNSTREAM_FAILURE,
    },
    # controls → propagate downstream (controller affects controlled)
    RelationshipType.CONTROLS: {
        'direction': 'down',
        'propagation_type': PropagationType.DEPENDENCY_IMPACT,
    },
    # connected_to → propagate bidirectionally
    RelationshipType.CONNECTED_TO: {
        'direction': 'both',
        'propagation_type': PropagationType.DEPENDENCY_IMPACT,
    },
    # monitors → informational only (no health impact)
    RelationshipType.MONITORS: {
        'direction': 'none',
        'propagation_type': None,
    },
}


class FailurePropagationService:
    """Service class for failure propagation operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_upstream_assets(
        self,
        asset_id: UUID,
        visited: Optional[Set[UUID]] = None,
        depth: int = 0,
        max_depth: int = DEFAULT_MAX_DEPTH,
    ) -> List[Dict[str, Any]]:
        """Get all upstream (parent) assets through contains relationships.
        
        Args:
            asset_id: Starting asset ID
            visited: Set of already visited asset IDs
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            
        Returns:
            List of upstream assets with relationship info
        """
        if visited is None:
            visited = set()
        
        if depth >= max_depth or asset_id in visited:
            return []
        
        visited.add(asset_id)
        results = []
        
        # Find parent relationships (where this asset is the child)
        parent_rels = self.db.query(AssetRelationship).filter(
            AssetRelationship.child_asset_id == asset_id,
            AssetRelationship.relationship_type == RelationshipType.CONTAINS.value,
        ).all()
        
        for rel in parent_rels:
            parent_asset = self.db.query(Asset).filter(
                Asset.id == rel.parent_asset_id
            ).first()
            
            if parent_asset and parent_asset.id not in visited:
                results.append({
                    'asset_id': parent_asset.id,
                    'asset_name': parent_asset.name,
                    'asset_type': parent_asset.asset_type,
                    'relationship_type': rel.relationship_type,
                    'depth': depth + 1,
                })
                
                # Recursively get upstream
                upstream = self.get_upstream_assets(
                    parent_asset.id,
                    visited,
                    depth + 1,
                    max_depth,
                )
                results.extend(upstream)
        
        return results
    
    def get_downstream_assets(
        self,
        asset_id: UUID,
        visited: Optional[Set[UUID]] = None,
        depth: int = 0,
        max_depth: int = DEFAULT_MAX_DEPTH,
        include_connected: bool = True,
    ) -> List[Dict[str, Any]]:
        """Get all downstream assets through feeds/controls/connected relationships.
        
        Args:
            asset_id: Starting asset ID
            visited: Set of already visited asset IDs
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            include_connected: Whether to follow connected_to relationships
            
        Returns:
            List of downstream assets with relationship info
        """
        if visited is None:
            visited = set()
        
        if depth >= max_depth or asset_id in visited:
            return []
        
        visited.add(asset_id)
        results = []
        
        # Get relationships where this asset is the parent
        child_rels = self.db.query(AssetRelationship).filter(
            AssetRelationship.parent_asset_id == asset_id,
        ).all()
        
        for rel in child_rels:
            rel_type = RelationshipType(rel.relationship_type)
            rule = PROPAGATION_RULES.get(rel_type, {})
            
            # Skip if direction is 'none' (monitors) or 'up' only
            direction = rule.get('direction', 'none')
            if direction in ('none', 'up'):
                continue
            
            # Skip connected_to if not included
            if rel_type == RelationshipType.CONNECTED_TO and not include_connected:
                continue
            
            child_asset = self.db.query(Asset).filter(
                Asset.id == rel.child_asset_id
            ).first()
            
            if child_asset and child_asset.id not in visited:
                results.append({
                    'asset_id': child_asset.id,
                    'asset_name': child_asset.name,
                    'asset_type': child_asset.asset_type,
                    'relationship_type': rel.relationship_type,
                    'propagation_type': rule.get('propagation_type'),
                    'depth': depth + 1,
                })
                
                # Recursively get downstream
                downstream = self.get_downstream_assets(
                    child_asset.id,
                    visited,
                    depth + 1,
                    max_depth,
                    include_connected,
                )
                results.extend(downstream)
        
        return results
    
    def detect_cycles(
        self,
        asset_id: UUID,
        visited: Optional[Set[UUID]] = None,
        recursion_stack: Optional[Set[UUID]] = None,
    ) -> bool:
        """Detect if there's a cycle in the asset relationship graph.
        
        Args:
            asset_id: Asset to check
            visited: Set of all visited assets
            recursion_stack: Set of assets in current path
            
        Returns:
            True if cycle detected, False otherwise
        """
        if visited is None:
            visited = set()
        if recursion_stack is None:
            recursion_stack = set()
        
        if asset_id in recursion_stack:
            return True
        
        if asset_id in visited:
            return False
        
        visited.add(asset_id)
        recursion_stack.add(asset_id)
        
        # Check relationships
        rels = self.db.query(AssetRelationship).filter(
            (AssetRelationship.parent_asset_id == asset_id) |
            (AssetRelationship.child_asset_id == asset_id)
        ).all()
        
        for rel in rels:
            next_id = (
                rel.child_asset_id 
                if rel.parent_asset_id == asset_id 
                else rel.parent_asset_id
            )
            
            if self.detect_cycles(next_id, visited, recursion_stack):
                return True
        
        recursion_stack.remove(asset_id)
        return False
    
    def propagate_event(
        self,
        event_id: UUID,
        max_depth: int = DEFAULT_MAX_DEPTH,
    ) -> Tuple[int, List[UUID]]:
        """Propagate an event through the asset relationship graph.
        
        Args:
            event_id: The source event ID
            max_depth: Maximum propagation depth
            
        Returns:
            Tuple of (propagated_count, list of affected asset IDs)
        """
        # Get source event
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise ValueError(f"Event not found: {event_id}")
        
        # Only propagate WARNING and CRITICAL events
        if event.severity not in ('WARNING', 'CRITICAL'):
            return 0, []
        
        source_asset_id = event.asset_id
        if not source_asset_id:
            return 0, []
        
        affected_assets = []
        visited = set([source_asset_id])
        
        # Propagate upstream (through contains relationships)
        upstream = self.get_upstream_assets(
            source_asset_id,
            visited.copy(),
            0,
            max_depth,
        )
        
        for item in upstream:
            if item['asset_id'] not in visited:
                visited.add(item['asset_id'])
                affected_assets.append(item)
        
        # Propagate downstream (through feeds/controls/connected relationships)
        downstream = self.get_downstream_assets(
            source_asset_id,
            visited.copy(),
            0,
            max_depth,
        )
        
        for item in downstream:
            if item['asset_id'] not in visited:
                visited.add(item['asset_id'])
                affected_assets.append(item)
        
        # Store propagation records
        propagated_count = 0
        stored_assets = []
        
        for item in affected_assets:
            try:
                # Determine propagation type
                if item.get('propagation_type'):
                    prop_type = item['propagation_type']
                elif item['relationship_type'] == RelationshipType.CONTAINS.value:
                    prop_type = PropagationType.CHILD_FAILURE
                else:
                    prop_type = PropagationType.DEPENDENCY_IMPACT
                
                propagated = PropagatedEvent(
                    source_event_id=event_id,
                    source_asset_id=source_asset_id,
                    affected_asset_id=item['asset_id'],
                    propagation_type=prop_type.value,
                    severity=event.severity,
                    depth=item['depth'],
                )
                
                self.db.add(propagated)
                self.db.commit()
                propagated_count += 1
                stored_assets.append(item['asset_id'])
                
            except IntegrityError:
                self.db.rollback()
                # Skip duplicates
        
        return propagated_count, stored_assets
    
    def get_event_propagation(
        self,
        event_id: UUID,
    ) -> List[PropagatedEvent]:
        """Get all propagation records for an event.
        
        Args:
            event_id: Source event ID
            
        Returns:
            List of PropagatedEvent records
        """
        return self.db.query(PropagatedEvent).filter(
            PropagatedEvent.source_event_id == event_id
        ).order_by(PropagatedEvent.depth).all()
    
    def get_asset_impacts(
        self,
        asset_id: UUID,
    ) -> List[Dict[str, Any]]:
        """Get all propagation impacts on an asset.
        
        Args:
            asset_id: The affected asset ID
            
        Returns:
            List of impacts with source event and asset info
        """
        propagations = self.db.query(PropagatedEvent).filter(
            PropagatedEvent.affected_asset_id == asset_id
        ).order_by(PropagatedEvent.depth).all()
        
        results = []
        for prop in propagations:
            source_event = self.db.query(Event).filter(
                Event.id == prop.source_event_id
            ).first()
            source_asset = self.db.query(Asset).filter(
                Asset.id == prop.source_asset_id
            ).first()
            
            results.append({
                'id': prop.id,
                'source_event_id': prop.source_event_id,
                'source_asset_id': prop.source_asset_id,
                'source_asset_name': source_asset.name if source_asset else None,
                'event_message': source_event.message if source_event else None,
                'propagation_type': prop.propagation_type.value if isinstance(prop.propagation_type, PropagationType) else prop.propagation_type,
                'severity': prop.severity,
                'depth': prop.depth,
                'created_at': prop.created_at,
            })
        
        return results
    
    def build_impact_chain(
        self,
        event_id: UUID,
        max_depth: int = DEFAULT_MAX_DEPTH,
    ) -> ImpactChainResponse:
        """Build a hierarchical impact chain from a source event.
        
        Args:
            event_id: Source event ID
            max_depth: Maximum depth to traverse
            
        Returns:
            ImpactChainResponse with hierarchical structure
        """
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise ValueError(f"Event not found: {event_id}")
        
        source_asset = self.db.query(Asset).filter(
            Asset.id == event.asset_id
        ).first()
        
        source_health = None
        if source_asset:
            source_health = self.db.query(AssetHealth).filter(
                AssetHealth.asset_id == source_asset.id
            ).first()
        
        visited = set([event.asset_id] if event.asset_id else [])
        
        def build_node(
            asset_id: UUID,
            parent_rel_type: str,
            prop_type: PropagationType,
            current_depth: int,
        ) -> Optional[ImpactChainNode]:
            if current_depth >= max_depth or asset_id in visited:
                return None
            
            visited.add(asset_id)
            
            asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
            if not asset:
                return None
            
            health = self.db.query(AssetHealth).filter(
                AssetHealth.asset_id == asset_id
            ).first()
            
            node = ImpactChainNode(
                asset_id=asset_id,
                asset_name=asset.name,
                asset_type=asset.asset_type,
                severity=event.severity,
                depth=current_depth,
                relationship_type=parent_rel_type,
                propagation_type=prop_type,
                health_status=health.health_status if health else None,
                health_score=health.health_score if health else None,
                children=[],
            )
            
            # Get downstream children
            downstream = self.get_downstream_assets(
                asset_id,
                visited.copy(),
                current_depth,
                max_depth,
            )
            
            for item in downstream:
                if item['asset_id'] not in visited:
                    child_node = build_node(
                        item['asset_id'],
                        item['relationship_type'],
                        item.get('propagation_type', PropagationType.DEPENDENCY_IMPACT),
                        current_depth + 1,
                    )
                    if child_node:
                        node.children.append(child_node)
            
            return node
        
        chain = []
        max_actual_depth = [0]
        
        # Build chain for downstream propagation
        downstream = self.get_downstream_assets(
            event.asset_id if event.asset_id else UUID('00000000-0000-0000-0000-000000000000'),
            visited.copy(),
            0,
            max_depth,
        )
        
        for item in downstream:
            if item['asset_id'] not in visited:
                node = build_node(
                    item['asset_id'],
                    item['relationship_type'],
                    item.get('propagation_type', PropagationType.DEPENDENCY_IMPACT),
                    item['depth'],
                )
                if node:
                    chain.append(node)
                    max_actual_depth[0] = max(max_actual_depth[0], item['depth'])
        
        # Get total affected count
        total_affected = self.db.query(PropagatedEvent).filter(
            PropagatedEvent.source_event_id == event_id
        ).count()
        
        return ImpactChainResponse(
            source_event_id=event_id,
            source_asset_id=event.asset_id,
            source_asset_name=source_asset.name if source_asset else "Unknown",
            source_severity=event.severity,
            root_event_message=event.message,
            chain=chain,
            max_depth=max_actual_depth[0],
            total_affected=total_affected,
        )
    
    def get_all_impacts(
        self,
        skip: int = 0,
        limit: int = 100,
        min_depth: Optional[int] = None,
        severity: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get all propagation impacts.
        
        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            min_depth: Minimum depth filter
            severity: Severity filter
            
        Returns:
            Tuple of (list, total count)
        """
        query = self.db.query(PropagatedEvent)
        
        if min_depth is not None:
            query = query.filter(PropagatedEvent.depth >= min_depth)
        if severity:
            query = query.filter(PropagatedEvent.severity == severity)
        
        total = query.count()
        propagations = query.order_by(
            PropagatedEvent.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        results = []
        for prop in propagations:
            source_event = self.db.query(Event).filter(
                Event.id == prop.source_event_id
            ).first()
            source_asset = self.db.query(Asset).filter(
                Asset.id == prop.source_asset_id
            ).first()
            affected_asset = self.db.query(Asset).filter(
                Asset.id == prop.affected_asset_id
            ).first()
            
            results.append({
                'id': prop.id,
                'source_event_id': prop.source_event_id,
                'source_asset_id': prop.source_asset_id,
                'source_asset_name': source_asset.name if source_asset else None,
                'affected_asset_id': prop.affected_asset_id,
                'affected_asset_name': affected_asset.name if affected_asset else None,
                'propagation_type': prop.propagation_type.value if isinstance(prop.propagation_type, PropagationType) else prop.propagation_type,
                'severity': prop.severity,
                'depth': prop.depth,
                'created_at': prop.created_at,
                'event_message': source_event.message if source_event else None,
            })
        
        return results, total