"""
Cognitive Graph Foundation

Knowledge graph infrastructure for entity relationships.
Deterministic - NO AI execution.
"""

from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class EntityType(str, Enum):
    """Entity types in the cognitive graph."""
    ASSET = "asset"
    SENSOR = "sensor"
    EVENT = "event"
    LOCATION = "location"
    PERSON = "person"
    SYSTEM = "system"
    CONCEPT = "concept"
    DOCUMENT = "document"


class RelationshipType(str, Enum):
    """Relationship types between entities."""
    CONTAINS = "contains"
    MONITORS = "monitors"
    CAUSES = "causes"
    DEPENDS_ON = "depends_on"
    SIMILAR_TO = "similar_to"
    PART_OF = "part_of"
    LOCATED_AT = "located_at"
    TRIGGERS = "triggers"
    AFFECTS = "affects"
    RELATED_TO = "related_to"


@dataclass
class Entity:
    """Entity in the cognitive graph."""
    id: str
    type: EntityType
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Relationship:
    """Relationship between entities."""
    id: str
    source_id: str
    target_id: str
    type: RelationshipType
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class GraphQuery:
    """Query for graph traversal."""
    start_id: str
    relation_types: List[RelationshipType] = field(default_factory=list)
    max_depth: int = 3
    entity_types: List[EntityType] = field(default_factory=list)
    direction: str = "both"  # "outgoing", "incoming", "both"


@dataclass
class GraphResult:
    """Result from graph query."""
    entities: List[Entity]
    relationships: List[Relationship]
    paths: List[List[str]]  # List of entity ID paths
    depth: int


@dataclass
class InferenceResult:
    """Inference result from graph traversal."""
    entity: Entity
    inferred_from: List[str]  # Entity IDs
    confidence: float
    explanation: str


class CognitiveGraph:
    """
    Cognitive graph for entity relationships.
    
    Deterministic graph operations - no AI inference.
    """
    
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.relationships: Dict[str, Relationship] = {}
        
        # Indexes for fast lookup
        self._entity_by_type: Dict[EntityType, Set[str]] = {}
        self._outgoing: Dict[str, Set[str]] = {}  # entity_id -> set of relationship IDs
        self._incoming: Dict[str, Set[str]] = {}  # entity_id -> set of relationship IDs
    
    def add_entity(
        self,
        entity_id: str,
        entity_type: EntityType,
        name: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> Entity:
        """Add an entity to the graph."""
        entity = Entity(
            id=entity_id,
            type=entity_type,
            name=name,
            properties=properties or {}
        )
        
        self.entities[entity_id] = entity
        
        # Update type index
        if entity_type not in self._entity_by_type:
            self._entity_by_type[entity_type] = set()
        self._entity_by_type[entity_type].add(entity_id)
        
        return entity
    
    def add_relationship(
        self,
        relationship_id: str,
        source_id: str,
        target_id: str,
        relationship_type: RelationshipType,
        weight: float = 1.0,
        properties: Optional[Dict[str, Any]] = None
    ) -> Optional[Relationship]:
        """Add a relationship between entities."""
        # Verify entities exist
        if source_id not in self.entities or target_id not in self.entities:
            return None
        
        relationship = Relationship(
            id=relationship_id,
            source_id=source_id,
            target_id=target_id,
            type=relationship_type,
            weight=weight,
            properties=properties or {}
        )
        
        self.relationships[relationship_id] = relationship
        
        # Update indexes
        if source_id not in self._outgoing:
            self._outgoing[source_id] = set()
        self._outgoing[source_id].add(relationship_id)
        
        if target_id not in self._incoming:
            self._incoming[target_id] = set()
        self._incoming[target_id].add(relationship_id)
        
        return relationship
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get an entity by ID."""
        return self.entities.get(entity_id)
    
    def get_entities_by_type(self, entity_type: EntityType) -> List[Entity]:
        """Get all entities of a type."""
        entity_ids = self._entity_by_type.get(entity_type, set())
        return [self.entities[eid] for eid in entity_ids if eid in self.entities]
    
    def get_relationship(self, relationship_id: str) -> Optional[Relationship]:
        """Get a relationship by ID."""
        return self.relationships.get(relationship_id)
    
    def get_outgoing(self, entity_id: str) -> List[Relationship]:
        """Get all outgoing relationships from an entity."""
        relationship_ids = self._outgoing.get(entity_id, set())
        return [
            self.relationships[rid]
            for rid in relationship_ids
            if rid in self.relationships
        ]
    
    def get_incoming(self, entity_id: str) -> List[Relationship]:
        """Get all incoming relationships to an entity."""
        relationship_ids = self._incoming.get(entity_id, set())
        return [
            self.relationships[rid]
            for rid in relationship_ids
            if rid in self.relationships
        ]
    
    def traverse(self, query: GraphQuery) -> GraphResult:
        """
        Traverse the graph based on query.
        
        Deterministic traversal - no AI inference.
        """
        visited: Set[str] = set()
        paths: List[List[str]] = []
        current_path: List[str] = []
        
        def _traverse(
            current_id: str,
            depth: int,
            path: List[str]
        ):
            if depth > query.max_depth:
                return
            
            if current_id in visited:
                return
            
            visited.add(current_id)
            path.append(current_id)
            
            # Check if this is an end point
            if depth > 0:
                paths.append(path.copy())
            
            # Get neighbors based on direction
            neighbors: List[Tuple[str, Relationship]] = []
            
            if query.direction in ("outgoing", "both"):
                for rel in self.get_outgoing(current_id):
                    if not query.relation_types or rel.type in query.relation_types:
                        neighbors.append((rel.target_id, rel))
            
            if query.direction in ("incoming", "both"):
                for rel in self.get_incoming(current_id):
                    if not query.relation_types or rel.type in query.relation_types:
                        neighbors.append((rel.source_id, rel))
            
            # Continue traversal
            for neighbor_id, _ in neighbors:
                _traverse(neighbor_id, depth + 1, path.copy())
        
        _traverse(query.start_id, 0, current_path)
        
        # Collect entities and relationships from paths
        entity_ids: Set[str] = set()
        relationship_ids: Set[str] = set()
        
        for path in paths:
            for i, entity_id in enumerate(path):
                entity_ids.add(entity_id)
                
                if i < len(path) - 1:
                    # Find relationship between consecutive entities
                    for rel in self.get_outgoing(entity_id):
                        if rel.target_id == path[i + 1]:
                            relationship_ids.add(rel.id)
        
        entities = [self.entities[eid] for eid in entity_ids if eid in self.entities]
        relationships = [self.relationships[rid] for rid in relationship_ids if rid in self.relationships]
        
        return GraphResult(
            entities=entities,
            relationships=relationships,
            paths=paths,
            depth=len(paths)
        )
    
    def find_paths(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 5
    ) -> List[List[str]]:
        """
        Find all paths between two entities.
        
        Deterministic path finding.
        """
        paths: List[List[str]] = []
        
        def _find_paths(
            current_id: str,
            target_id: str,
            visited: Set[str],
            path: List[str],
            depth: int
        ):
            if depth > max_depth:
                return
            
            if current_id == target_id:
                paths.append(path.copy())
                return
            
            if current_id in visited:
                return
            
            visited.add(current_id)
            path.append(current_id)
            
            # Explore outgoing relationships
            for rel in self.get_outgoing(current_id):
                _find_paths(
                    rel.target_id,
                    target_id,
                    visited.copy(),
                    path.copy(),
                    depth + 1
                )
            
            # Explore incoming relationships
            for rel in self.get_incoming(current_id):
                _find_paths(
                    rel.source_id,
                    target_id,
                    visited.copy(),
                    path.copy(),
                    depth + 1
                )
        
        _find_paths(source_id, target_id, set(), [], 0)
        
        return paths
    
    def get_neighbors(
        self,
        entity_id: str,
        depth: int = 1,
        relationship_types: Optional[List[RelationshipType]] = None
    ) -> List[Entity]:
        """
        Get neighboring entities.
        
        Deterministic neighbor lookup.
        """
        neighbors: Set[str] = set()
        current_level: Set[str] = {entity_id}
        visited: Set[str] = {entity_id}
        
        for _ in range(depth):
            next_level: Set[str] = set()
            
            for eid in current_level:
                # Get outgoing neighbors
                for rel in self.get_outgoing(eid):
                    if not relationship_types or rel.type in relationship_types:
                        if rel.target_id not in visited:
                            neighbors.add(rel.target_id)
                            next_level.add(rel.target_id)
                
                # Get incoming neighbors
                for rel in self.get_incoming(eid):
                    if not relationship_types or rel.type in relationship_types:
                        if rel.source_id not in visited:
                            neighbors.add(rel.source_id)
                            next_level.add(rel.source_id)
            
            visited.update(next_level)
            current_level = next_level
        
        return [self.entities[nid] for nid in neighbors if nid in self.entities]
    
    def infer_relationships(
        self,
        entity_id: str,
        relationship_type: RelationshipType
    ) -> List[InferenceResult]:
        """
        Infer potential relationships based on graph structure.
        
        Deterministic inference based on existing relationships.
        """
        results: List[InferenceResult] = []
        entity = self.entities.get(entity_id)
        
        if not entity:
            return results
        
        # Find similar entities (same type, shared neighbors)
        neighbors = self.get_neighbors(entity_id, depth=1)
        
        for neighbor in neighbors:
            if neighbor.type == entity.type and neighbor.id != entity_id:
                # Check for common neighbors
                neighbor_neighbors = set(n.id for n in self.get_neighbors(neighbor.id, depth=1))
                entity_neighbors = set(n.id for n in neighbors)
                common = neighbor_neighbors.intersection(entity_neighbors)
                
                if common:
                    # Calculate confidence based on shared neighbors
                    confidence = len(common) / (len(neighbor_neighbors) + len(entity_neighbors))
                    
                    results.append(InferenceResult(
                        entity=neighbor,
                        inferred_from=list(common),
                        confidence=confidence,
                        explanation=f"Entities share {len(common)} common neighbor(s)"
                    ))
        
        return results
    
    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity and its relationships."""
        if entity_id not in self.entities:
            return False
        
        # Remove from type index
        entity_type = self.entities[entity_id].type
        if entity_type in self._entity_by_type:
            self._entity_by_type[entity_type].discard(entity_id)
        
        # Remove outgoing relationships
        for rel in list(self.get_outgoing(entity_id)):
            self.delete_relationship(rel.id)
        
        # Remove incoming relationships
        for rel in list(self.get_incoming(entity_id)):
            self.delete_relationship(rel.id)
        
        # Remove entity
        del self.entities[entity_id]
        
        return True
    
    def delete_relationship(self, relationship_id: str) -> bool:
        """Delete a relationship."""
        if relationship_id not in self.relationships:
            return False
        
        rel = self.relationships[relationship_id]
        
        # Remove from indexes
        if rel.source_id in self._outgoing:
            self._outgoing[rel.source_id].discard(relationship_id)
        if rel.target_id in self._incoming:
            self._incoming[rel.target_id].discard(relationship_id)
        
        del self.relationships[relationship_id]
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Export graph to dictionary."""
        return {
            "entities": [
                {
                    "id": e.id,
                    "type": e.type.value,
                    "name": e.name,
                    "properties": e.properties
                }
                for e in self.entities.values()
            ],
            "relationships": [
                {
                    "id": r.id,
                    "source_id": r.source_id,
                    "target_id": r.target_id,
                    "type": r.type.value,
                    "weight": r.weight,
                    "properties": r.properties
                }
                for r in self.relationships.values()
            ]
        }
    
    def to_json(self) -> str:
        """Export graph to JSON."""
        return json.dumps(self.to_dict(), indent=2)


# Singleton instance
_graph: Optional[CognitiveGraph] = None


def get_cognitive_graph() -> CognitiveGraph:
    """Get or create cognitive graph singleton."""
    global _graph
    if _graph is None:
        _graph = CognitiveGraph()
    return _graph
