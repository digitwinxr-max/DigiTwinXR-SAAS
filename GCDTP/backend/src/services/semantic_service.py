"""
Semantic Service

Provides semantic metadata layer operations.
This layer ONLY adds semantic descriptions and cross-domain references.
It does NOT change existing engines.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from ..models.semantic_entity import SemanticEntity, EntityType
from ..models.semantic_tag import SemanticTag
from ..models.semantic_relationship import SemanticRelationship, RelationshipType
from ..schemas.semantic import (
    SemanticEntityCreate,
    SemanticEntityUpdate,
    SemanticTagCreate,
    SemanticRelationshipCreate,
    SemanticSearchQuery,
    SemanticContextResponse,
    SemanticGraphResponse,
    GraphNode,
    GraphEdge,
)


class SemanticService:
    """
    Service for semantic metadata operations.
    
    This service provides:
    - Entity management
    - Tag management
    - Relationship management
    - Search functionality
    - Context aggregation
    - Graph building
    
    NO AI, NO inference, NO embeddings.
    Pure aggregation only.
    """
    
    def __init__(self):
        # In-memory storage for semantic entities
        self._entities: Dict[str, SemanticEntity] = {}
        self._tags: Dict[str, SemanticTag] = {}
        self._relationships: Dict[str, SemanticRelationship] = {}
        # Index by entity_type
        self._entities_by_type: Dict[str, List[str]] = {}
        # Index by ontology_class
        self._entities_by_class: Dict[str, List[str]] = {}
        # Index tags by entity_id
        self._tags_by_entity: Dict[str, List[str]] = {}
        # Index relationships by entity
        self._rels_by_source: Dict[str, List[str]] = {}
        self._rels_by_target: Dict[str, List[str]] = {}
    
    def create_entity(self, data: SemanticEntityCreate) -> SemanticEntity:
        """Create a new semantic entity."""
        # Check for duplicate
        for entity in self._entities.values():
            if entity.entity_type.value == data.entity_type and entity.entity_id == data.entity_id:
                return entity
        
        entity = SemanticEntity(
            entity_type=EntityType(data.entity_type),
            entity_id=data.entity_id,
            name=data.name,
            description=data.description,
            category=data.category,
            ontology_class=data.ontology_class
        )
        
        self._entities[entity.id] = entity
        
        # Update indexes
        entity_type = data.entity_type
        if entity_type not in self._entities_by_type:
            self._entities_by_type[entity_type] = []
        self._entities_by_type[entity_type].append(entity.id)
        
        if data.ontology_class:
            if data.ontology_class not in self._entities_by_class:
                self._entities_by_class[data.ontology_class] = []
            self._entities_by_class[data.ontology_class].append(entity.id)
        
        return entity
    
    def get_entity(self, entity_id: str) -> Optional[SemanticEntity]:
        """Get entity by ID."""
        return self._entities.get(entity_id)
    
    def update_entity(self, entity_id: str, data: SemanticEntityUpdate) -> Optional[SemanticEntity]:
        """Update an entity."""
        entity = self._entities.get(entity_id)
        if not entity:
            return None
        
        if data.name is not None:
            entity.name = data.name
        if data.description is not None:
            entity.description = data.description
        if data.category is not None:
            entity.category = data.category
        if data.ontology_class is not None:
            entity.ontology_class = data.ontology_class
        
        entity.updated_at = datetime.utcnow()
        return entity
    
    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity and its related tags and relationships."""
        entity = self._entities.pop(entity_id, None)
        if not entity:
            return False
        
        # Remove from type index
        entity_type = entity.entity_type.value
        if entity_type in self._entities_by_type:
            self._entities_by_type[entity_type] = [
                eid for eid in self._entities_by_type[entity_type] if eid != entity_id
            ]
        
        # Remove from class index
        if entity.ontology_class and entity.ontology_class in self._entities_by_class:
            self._entities_by_class[entity.ontology_class] = [
                eid for eid in self._entities_by_class[entity.ontology_class] if eid != entity_id
            ]
        
        # Remove related tags
        tag_ids = self._tags_by_entity.pop(entity_id, [])
        for tag_id in tag_ids:
            self._tags.pop(tag_id, None)
        
        # Remove related relationships
        rel_ids = self._rels_by_source.pop(entity_id, [])
        rel_ids.extend(self._rels_by_target.pop(entity_id, []))
        for rel_id in set(rel_ids):
            rel = self._relationships.pop(rel_id, None)
            if rel:
                source_id = rel.source_entity_id
                target_id = rel.target_entity_id
                if source_id in self._rels_by_source:
                    self._rels_by_source[source_id] = [
                        rid for rid in self._rels_by_source[source_id] if rid != rel_id
                    ]
                if target_id in self._rels_by_target:
                    self._rels_by_target[target_id] = [
                        rid for rid in self._rels_by_target[target_id] if rid != rel_id
                    ]
        
        return True
    
    def list_entities(
        self,
        entity_type: Optional[str] = None,
        category: Optional[str] = None,
        ontology_class: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[SemanticEntity]:
        """List entities with optional filters."""
        results = list(self._entities.values())
        
        if entity_type:
            results = [e for e in results if e.entity_type.value == entity_type]
        
        if category:
            results = [e for e in results if e.category == category]
        
        if ontology_class:
            results = [e for e in results if e.ontology_class == ontology_class]
        
        # Sort by created_at descending
        results.sort(key=lambda e: e.created_at, reverse=True)
        
        return results[offset:offset + limit]
    
    def create_tag(self, data: SemanticTagCreate) -> Optional[SemanticTag]:
        """Create a new semantic tag."""
        # Verify entity exists
        entity = self._entities.get(data.entity_id)
        if not entity:
            return None
        
        # Check for duplicate tag on entity
        if data.entity_id in self._tags_by_entity:
            for tag_id in self._tags_by_entity[data.entity_id]:
                tag = self._tags.get(tag_id)
                if tag and tag.tag_name == data.tag_name:
                    return tag
        
        tag = SemanticTag(
            entity_id=data.entity_id,
            tag_name=data.tag_name,
            tag_value=data.tag_value
        )
        
        self._tags[tag.id] = tag
        
        # Update index
        if data.entity_id not in self._tags_by_entity:
            self._tags_by_entity[data.entity_id] = []
        self._tags_by_entity[data.entity_id].append(tag.id)
        
        return tag
    
    def get_tags(self, entity_id: str) -> List[SemanticTag]:
        """Get all tags for an entity."""
        tag_ids = self._tags_by_entity.get(entity_id, [])
        return [self._tags[tag_id] for tag_id in tag_ids if tag_id in self._tags]
    
    def get_tags_by_name(self, tag_name: str) -> List[SemanticTag]:
        """Get all tags with a specific name."""
        return [tag for tag in self._tags.values() if tag.tag_name == tag_name]
    
    def delete_tag(self, tag_id: str) -> bool:
        """Delete a tag."""
        tag = self._tags.pop(tag_id, None)
        if not tag:
            return False
        
        entity_id = tag.entity_id
        if entity_id in self._tags_by_entity:
            self._tags_by_entity[entity_id] = [
                tid for tid in self._tags_by_entity[entity_id] if tid != tag_id
            ]
        
        return True
    
    def create_relationship(self, data: SemanticRelationshipCreate) -> Optional[SemanticRelationship]:
        """Create a new semantic relationship."""
        # Verify both entities exist
        source = self._entities.get(data.source_entity_id)
        target = self._entities.get(data.target_entity_id)
        if not source or not target:
            return None
        
        # Check for duplicate
        for rel in self._relationships.values():
            if (rel.source_entity_id == data.source_entity_id and
                rel.target_entity_id == data.target_entity_id and
                rel.relationship_type.value == data.relationship_type):
                return rel
        
        relationship = SemanticRelationship(
            source_entity_id=data.source_entity_id,
            target_entity_id=data.target_entity_id,
            relationship_type=RelationshipType(data.relationship_type)
        )
        
        self._relationships[relationship.id] = relationship
        
        # Update indexes
        if data.source_entity_id not in self._rels_by_source:
            self._rels_by_source[data.source_entity_id] = []
        self._rels_by_source[data.source_entity_id].append(relationship.id)
        
        if data.target_entity_id not in self._rels_by_target:
            self._rels_by_target[data.target_entity_id] = []
        self._rels_by_target[data.target_entity_id].append(relationship.id)
        
        return relationship
    
    def get_relationships(self, entity_id: str) -> List[SemanticRelationship]:
        """Get all relationships for an entity (both source and target)."""
        rel_ids = set()
        rel_ids.update(self._rels_by_source.get(entity_id, []))
        rel_ids.update(self._rels_by_target.get(entity_id, []))
        return [self._relationships[rid] for rid in rel_ids if rid in self._relationships]
    
    def get_relationships_by_type(self, relationship_type: str) -> List[SemanticRelationship]:
        """Get all relationships of a specific type."""
        return [
            rel for rel in self._relationships.values()
            if rel.relationship_type.value == relationship_type
        ]
    
    def delete_relationship(self, relationship_id: str) -> bool:
        """Delete a relationship."""
        rel = self._relationships.pop(relationship_id, None)
        if not rel:
            return False
        
        source_id = rel.source_entity_id
        target_id = rel.target_entity_id
        
        if source_id in self._rels_by_source:
            self._rels_by_source[source_id] = [
                rid for rid in self._rels_by_source[source_id] if rid != relationship_id
            ]
        
        if target_id in self._rels_by_target:
            self._rels_by_target[target_id] = [
                rid for rid in self._rels_by_target[target_id] if rid != relationship_id
            ]
        
        return True
    
    def search(
        self,
        query: Optional[SemanticSearchQuery] = None
    ) -> List[SemanticEntity]:
        """
        Search semantic entities.
        
        NO AI, NO embeddings, NO vector search.
        Pure filter-based search only.
        """
        if query is None:
            query = SemanticSearchQuery()
        
        results = list(self._entities.values())
        
        # Filter by entity_type
        if query.entity_type:
            results = [e for e in results if e.entity_type.value == query.entity_type]
        
        # Filter by category
        if query.category:
            results = [e for e in results if e.category == query.category]
        
        # Filter by ontology_class
        if query.ontology_class:
            results = [e for e in results if e.ontology_class == query.ontology_class]
        
        # Filter by tag_name
        if query.tag_name:
            entity_ids = set()
            for tag in self._tags.values():
                if tag.tag_name == query.tag_name:
                    entity_ids.add(tag.entity_id)
            results = [e for e in results if e.id in entity_ids]
        
        # Filter by tag_value
        if query.tag_value:
            entity_ids = set()
            for tag in self._tags.values():
                if tag.tag_value == query.tag_value:
                    entity_ids.add(tag.entity_id)
            results = [e for e in results if e.id in entity_ids]
        
        # Text search on name/description
        if query.query:
            query_lower = query.query.lower()
            results = [
                e for e in results
                if query_lower in e.name.lower() or
                   (e.description and query_lower in e.description.lower())
            ]
        
        # Sort by created_at descending
        results.sort(key=lambda e: e.created_at, reverse=True)
        
        # Apply pagination
        return results[query.offset:query.offset + query.limit]
    
    def build_context(
        self,
        entity_type: str,
        entity_id: str
    ) -> Optional[SemanticContextResponse]:
        """
        Build semantic context for an entity.
        
        Returns aggregated information about related entities:
        - Asset
        - Sensors
        - Events
        - Health
        - Documents
        - Timeline entries
        - Work orders
        
        NO AI, NO inference. Pure aggregation only.
        """
        # Find the entity by type and entity_id
        entity = None
        for e in self._entities.values():
            if e.entity_type.value == entity_type and e.entity_id == entity_id:
                entity = e
                break
        
        if not entity:
            return None
        
        # Get tags for this entity
        tags = self.get_tags(entity.id)
        tags_dict = [{"tag_name": t.tag_name, "tag_value": t.tag_value} for t in tags]
        
        # Get relationships
        relationships = self.get_relationships(entity.id)
        
        # Build context
        context = SemanticContextResponse(
            entity={
                "id": entity.id,
                "entity_type": entity.entity_type.value,
                "entity_id": entity.entity_id,
                "name": entity.name,
                "description": entity.description,
                "category": entity.category,
                "ontology_class": entity.ontology_class,
                "created_at": entity.created_at,
                "updated_at": entity.updated_at,
                "tags": tags_dict
            }
        )
        
        # Aggregate related entities by type
        for rel in relationships:
            # Get the related entity
            related_id = rel.target_entity_id if rel.source_entity_id == entity.id else rel.source_entity_id
            related = self._entities.get(related_id)
            if not related:
                continue
            
            related_tags = self.get_tags(related.id)
            related_tags_dict = [{"tag_name": t.tag_name, "tag_value": t.tag_value} for t in related_tags]
            related_with_tags = {
                "id": related.id,
                "entity_type": related.entity_type.value,
                "entity_id": related.entity_id,
                "name": related.name,
                "description": related.description,
                "category": related.category,
                "ontology_class": related.ontology_class,
                "created_at": related.created_at,
                "updated_at": related.updated_at,
                "tags": related_tags_dict
            }
            
            # Categorize by type
            entity_type_val = related.entity_type.value
            if entity_type_val == EntityType.ASSET.value:
                context.asset = {
                    "id": related.id,
                    "name": related.name,
                    "category": related.category,
                    "ontology_class": related.ontology_class,
                    "tags": related_tags_dict
                }
            elif entity_type_val == EntityType.SENSOR.value:
                context.sensors.entities.append(related_with_tags)
                context.sensors.count += 1
            elif entity_type_val == EntityType.EVENT.value:
                context.events.entities.append(related_with_tags)
                context.events.count += 1
            elif entity_type_val == EntityType.HEALTH.value:
                context.health.entities.append(related_with_tags)
                context.health.count += 1
            elif entity_type_val == EntityType.DOCUMENT.value:
                context.documents.entities.append(related_with_tags)
                context.documents.count += 1
            elif entity_type_val == EntityType.TIMELINE.value:
                context.timeline_entries.entities.append(related_with_tags)
                context.timeline_entries.count += 1
            elif entity_type_val == EntityType.WORK_ORDER.value:
                context.work_orders.entities.append(related_with_tags)
                context.work_orders.count += 1
        
        # Add relationships
        context.relationships = [
            {
                "id": r.id,
                "source_entity_id": r.source_entity_id,
                "target_entity_id": r.target_entity_id,
                "relationship_type": r.relationship_type.value,
                "created_at": r.created_at
            }
            for r in relationships
        ]
        
        return context
    
    def build_graph(self, limit: int = 500) -> SemanticGraphResponse:
        """
        Build semantic graph.
        
        Returns nodes and edges for graph visualization.
        NO AI, NO inference. Pure aggregation only.
        """
        nodes = []
        edges = []
        
        # Get all entities (with limit)
        entities = list(self._entities.values())[:limit]
        
        for entity in entities:
            tags = self.get_tags(entity.id)
            tags_dict = [{"tag_name": t.tag_name, "tag_value": t.tag_value} for t in tags]
            
            nodes.append(GraphNode(
                id=entity.id,
                name=entity.name,
                entity_type=entity.entity_type.value,
                category=entity.category,
                ontology_class=entity.ontology_class,
                tags=tags_dict
            ))
        
        # Get all relationships (with limit)
        relationships = list(self._relationships.values())[:limit]
        
        for rel in relationships:
            edges.append(GraphEdge(
                source=rel.source_entity_id,
                target=rel.target_entity_id,
                relationship_type=rel.relationship_type.value
            ))
        
        return SemanticGraphResponse(
            nodes=nodes,
            edges=edges,
            total_nodes=len(nodes),
            total_edges=len(edges)
        )


# Global instance
semantic_service = SemanticService()
