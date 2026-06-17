"""
Ontology Types

Core data types for semantic ontology.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from enum import Enum


class OntologyDomain(str, Enum):
    """Ontology domain."""
    ELECTRICAL = "electrical"
    WATER = "water"
    TRANSPORT = "transport"
    BUILDINGS = "buildings"
    TELECOMMUNICATIONS = "telecommunications"
    ENVIRONMENT = "environment"
    ENERGY = "energy"
    INDUSTRIAL = "industrial"
    CUSTOM = "custom"


class SyncStatus(str, Enum):
    """Sync status."""
    PENDING = "pending"
    SYNCING = "syncing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class OntologyDomain:
    """Ontology domain representation."""
    id: str
    name: str
    display_name: str
    domain_type: OntologyDomain
    description: str = ""
    parent_domain_id: Optional[str] = None
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "domain_type": self.domain_type.value,
            "description": self.description,
            "is_active": self.is_active,
        }


@dataclass
class OntologyClass:
    """Ontology class representation."""
    id: str
    domain_id: str
    name: str
    display_name: str
    description: str = ""
    parent_class_id: Optional[str] = None
    level: int = 0
    path: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    capabilities: Dict[str, Any] = field(default_factory=dict)
    is_abstract: bool = False
    is_system: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "domain_id": self.domain_id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "parent_class_id": self.parent_class_id,
            "level": self.level,
            "path": self.path,
            "is_abstract": self.is_abstract,
        }


@dataclass
class OntologyRelationship:
    """Ontology relationship representation."""
    id: str
    source_class_id: str
    target_class_id: str
    relationship_type: str
    description: str = ""
    cardinality: str = "many-to-many"
    is_directional: bool = True
    inverse_relationship: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "source_class_id": self.source_class_id,
            "target_class_id": self.target_class_id,
            "relationship_type": self.relationship_type,
            "cardinality": self.cardinality,
            "is_directional": self.is_directional,
        }


@dataclass
class Taxonomy:
    """Taxonomy representation."""
    id: str
    domain_id: str
    name: str
    display_name: str
    description: str = ""
    root_class_id: Optional[str] = None
    is_primary: bool = False
    version: str = "1.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "domain_id": self.domain_id,
            "name": self.name,
            "display_name": self.display_name,
            "is_primary": self.is_primary,
        }


@dataclass
class Capability:
    """Capability representation."""
    id: str
    class_id: str
    name: str
    display_name: str
    description: str = ""
    capability_type: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    requirements: List[str] = field(default_factory=list)
    inherited: bool = False
    parent_capability_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "class_id": self.class_id,
            "name": self.name,
            "display_name": self.display_name,
            "capability_type": self.capability_type,
            "inherited": self.inherited,
        }


@dataclass
class SemanticTag:
    """Semantic tag representation."""
    id: str
    entity_type: str
    entity_id: str
    class_id: str
    confidence: float = 1.0
    source: str = ""
    assigned_by: str = ""
    assigned_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "class_id": self.class_id,
            "confidence": self.confidence,
            "source": self.source,
        }


@dataclass
class Classification:
    """Classification representation."""
    entity_type: str
    entity_id: str
    class_id: str
    class_name: str = ""
    domain_name: str = ""
    confidence: float = 1.0
    source: str = ""
    assigned_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "class_id": self.class_id,
            "class_name": self.class_name,
            "confidence": self.confidence,
        }


@dataclass
class ClassHierarchy:
    """Class hierarchy result."""
    ontology_class: OntologyClass
    subclasses: List[OntologyClass] = field(default_factory=list)
    parent_classes: List[OntologyClass] = field(default_factory=list)
    depth: int = 0
    ancestors: List[str] = field(default_factory=list)
    descendants: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "class_id": self.ontology_class.id,
            "class_name": self.ontology_class.name,
            "subclass_count": len(self.subclasses),
            "depth": self.depth,
            "ancestor_count": len(self.ancestors),
            "descendant_count": len(self.descendants),
        }


@dataclass
class CapabilitySet:
    """Set of capabilities for a class."""
    own_capabilities: List[Capability] = field(default_factory=list)
    inherited_capabilities: List[Capability] = field(default_factory=list)
    direct_count: int = 0
    total_count: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "direct_count": self.direct_count,
            "total_count": self.total_count,
            "capabilities": [c.name for c in self.inherited_capabilities],
        }


@dataclass
class SemanticQueryResult:
    """Semantic query result."""
    classes: List[OntologyClass] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    result_count: int = 0
    query_type: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "class_count": len(self.classes),
            "entity_count": len(self.entities),
            "result_count": self.result_count,
            "query_type": self.query_type,
        }


@dataclass
class SyncRecord:
    """Ontology sync record."""
    id: str
    entity_type: str
    entity_id: str
    operation: str
    status: SyncStatus
    class_id: Optional[str] = None
    error_message: str = ""
    synced_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "operation": self.operation,
            "status": self.status.value,
        }
