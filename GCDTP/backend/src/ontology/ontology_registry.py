"""
Ontology Registry

Registry for managing ontology domains, classes, and taxonomies.
"""

import uuid
from typing import Dict, List, Optional, Set
from datetime import datetime
from backend.src.ontology.ontology_types import (
    OntologyDomain,
    OntologyClass,
    OntologyRelationship,
    Taxonomy,
    Capability,
    SemanticTag,
    OntologyDomain as DomainType,
)


class OntologyRegistry:
    """
    Registry for ontology management.
    
    Responsibilities:
    - Register domains
    - Register classes
    - Register taxonomies
    - Register capabilities
    - Register semantic tags
    """
    
    def __init__(self):
        # Domain storage
        self._domains: Dict[str, OntologyDomain] = {}
        self._domains_by_name: Dict[str, str] = {}  # name -> id
        
        # Class storage
        self._classes: Dict[str, OntologyClass] = {}
        self._classes_by_name: Dict[str, str] = {}  # name -> id
        self._domain_classes: Dict[str, List[str]] = {}  # domain_id -> [class_ids]
        
        # Relationship storage
        self._relationships: Dict[str, OntologyRelationship] = {}
        
        # Taxonomy storage
        self._taxonomies: Dict[str, Taxonomy] = {}
        
        # Capability storage
        self._capabilities: Dict[str, Capability] = {}
        self._class_capabilities: Dict[str, List[str]] = {}  # class_id -> [capability_ids]
        
        # Semantic tag storage
        self._tags: Dict[str, SemanticTag] = {}
        self._entity_tags: Dict[str, List[str]] = {}  # entity_key -> [tag_ids]
        
        # Initialize default domains
        self._initialize_default_domains()
    
    def _initialize_default_domains(self):
        """Initialize default domains."""
        defaults = [
            (DomainType.ELECTRICAL, "Electrical", "Electrical infrastructure"),
            (DomainType.WATER, "Water", "Water distribution systems"),
            (DomainType.TRANSPORT, "Transport", "Transportation networks"),
            (DomainType.BUILDINGS, "Buildings", "Building systems"),
            (DomainType.TELECOMMUNICATIONS, "Telecommunications", "Communication networks"),
            (DomainType.ENVIRONMENT, "Environment", "Environmental monitoring"),
            (DomainType.ENERGY, "Energy", "Energy systems"),
            (DomainType.INDUSTRIAL, "Industrial", "Industrial processes"),
        ]
        
        for domain_type, name, desc in defaults:
            domain = OntologyDomain(
                id=str(uuid.uuid4()),
                name=domain_type.value,
                display_name=name,
                domain_type=domain_type,
                description=desc
            )
            self._domains[domain.id] = domain
            self._domains_by_name[domain.name] = domain.id
    
    # =========================================================================
    # Domain Operations
    # =========================================================================
    
    def register_domain(
        self,
        name: str,
        display_name: str,
        domain_type: DomainType,
        description: str = "",
        parent_domain_id: Optional[str] = None
    ) -> OntologyDomain:
        """Register a new domain."""
        domain = OntologyDomain(
            id=str(uuid.uuid4()),
            name=name,
            display_name=display_name,
            domain_type=domain_type,
            description=description,
            parent_domain_id=parent_domain_id
        )
        
        self._domains[domain.id] = domain
        self._domains_by_name[domain.name] = domain.id
        
        return domain
    
    def get_domain(self, domain_id: str) -> Optional[OntologyDomain]:
        """Get domain by ID."""
        return self._domains.get(domain_id)
    
    def get_domain_by_name(self, name: str) -> Optional[OntologyDomain]:
        """Get domain by name."""
        domain_id = self._domains_by_name.get(name)
        if domain_id:
            return self._domains.get(domain_id)
        return None
    
    def get_all_domains(self) -> List[OntologyDomain]:
        """Get all domains."""
        return list(self._domains.values())
    
    # =========================================================================
    # Class Operations
    # =========================================================================
    
    def register_class(
        self,
        domain_id: str,
        name: str,
        display_name: str,
        parent_class_id: Optional[str] = None,
        description: str = "",
        is_abstract: bool = False,
        is_system: bool = False
    ) -> OntologyClass:
        """Register a new class."""
        # Calculate level and path
        level = 0
        path_parts = [name]
        
        if parent_class_id:
            parent = self._classes.get(parent_class_id)
            if parent:
                level = parent.level + 1
                path_parts = parent.path.split("/") + [name]
        
        path = "/".join(path_parts)
        
        ontology_class = OntologyClass(
            id=str(uuid.uuid4()),
            domain_id=domain_id,
            name=name,
            display_name=display_name,
            description=description,
            parent_class_id=parent_class_id,
            level=level,
            path=path,
            is_abstract=is_abstract,
            is_system=is_system
        )
        
        self._classes[ontology_class.id] = ontology_class
        self._classes_by_name[ontology_class.name] = ontology_class.id
        
        if domain_id not in self._domain_classes:
            self._domain_classes[domain_id] = []
        self._domain_classes[domain_id].append(ontology_class.id)
        
        return ontology_class
    
    def get_class(self, class_id: str) -> Optional[OntologyClass]:
        """Get class by ID."""
        return self._classes.get(class_id)
    
    def get_class_by_name(self, name: str) -> Optional[OntologyClass]:
        """Get class by name."""
        class_id = self._classes_by_name.get(name)
        if class_id:
            return self._classes.get(class_id)
        return None
    
    def get_classes_for_domain(self, domain_id: str) -> List[OntologyClass]:
        """Get all classes in a domain."""
        class_ids = self._domain_classes.get(domain_id, [])
        return [self._classes[cid] for cid in class_ids if cid in self._classes]
    
    def get_all_classes(self) -> List[OntologyClass]:
        """Get all classes."""
        return list(self._classes.values())
    
    # =========================================================================
    # Relationship Operations
    # =========================================================================
    
    def register_relationship(
        self,
        source_class_id: str,
        target_class_id: str,
        relationship_type: str,
        cardinality: str = "many-to-many",
        is_directional: bool = True,
        inverse_relationship: str = ""
    ) -> OntologyRelationship:
        """Register a relationship between classes."""
        relationship = OntologyRelationship(
            id=str(uuid.uuid4()),
            source_class_id=source_class_id,
            target_class_id=target_class_id,
            relationship_type=relationship_type,
            cardinality=cardinality,
            is_directional=is_directional,
            inverse_relationship=inverse_relationship
        )
        
        self._relationships[relationship.id] = relationship
        return relationship
    
    def get_relationships_for_class(self, class_id: str) -> List[OntologyRelationship]:
        """Get relationships for a class."""
        return [
            r for r in self._relationships.values()
            if r.source_class_id == class_id or r.target_class_id == class_id
        ]
    
    # =========================================================================
    # Taxonomy Operations
    # =========================================================================
    
    def register_taxonomy(
        self,
        domain_id: str,
        name: str,
        display_name: str,
        root_class_id: Optional[str] = None,
        description: str = "",
        is_primary: bool = False
    ) -> Taxonomy:
        """Register a taxonomy."""
        taxonomy = Taxonomy(
            id=str(uuid.uuid4()),
            domain_id=domain_id,
            name=name,
            display_name=display_name,
            description=description,
            root_class_id=root_class_id,
            is_primary=is_primary
        )
        
        self._taxonomies[taxonomy.id] = taxonomy
        return taxonomy
    
    def get_taxonomy(self, taxonomy_id: str) -> Optional[Taxonomy]:
        """Get taxonomy by ID."""
        return self._taxonomies.get(taxonomy_id)
    
    def get_taxonomies_for_domain(self, domain_id: str) -> List[Taxonomy]:
        """Get taxonomies for a domain."""
        return [t for t in self._taxonomies.values() if t.domain_id == domain_id]
    
    # =========================================================================
    # Capability Operations
    # =========================================================================
    
    def register_capability(
        self,
        class_id: str,
        name: str,
        display_name: str,
        capability_type: str = "",
        description: str = "",
        parameters: Optional[Dict] = None,
        parent_capability_id: Optional[str] = None
    ) -> Capability:
        """Register a capability for a class."""
        capability = Capability(
            id=str(uuid.uuid4()),
            class_id=class_id,
            name=name,
            display_name=display_name,
            description=description,
            capability_type=capability_type,
            parameters=parameters or {},
            parent_capability_id=parent_capability_id
        )
        
        self._capabilities[capability.id] = capability
        
        if class_id not in self._class_capabilities:
            self._class_capabilities[class_id] = []
        self._class_capabilities[class_id].append(capability.id)
        
        return capability
    
    def get_capabilities_for_class(self, class_id: str) -> List[Capability]:
        """Get capabilities for a class."""
        cap_ids = self._class_capabilities.get(class_id, [])
        return [self._capabilities[cid] for cid in cap_ids if cid in self._capabilities]
    
    # =========================================================================
    # Semantic Tag Operations
    # =========================================================================
    
    def assign_tag(
        self,
        entity_type: str,
        entity_id: str,
        class_id: str,
        confidence: float = 1.0,
        source: str = "",
        assigned_by: str = ""
    ) -> SemanticTag:
        """Assign a semantic tag to an entity."""
        tag = SemanticTag(
            id=str(uuid.uuid4()),
            entity_type=entity_type,
            entity_id=entity_id,
            class_id=class_id,
            confidence=confidence,
            source=source,
            assigned_by=assigned_by
        )
        
        self._tags[tag.id] = tag
        
        entity_key = f"{entity_type}:{entity_id}"
        if entity_key not in self._entity_tags:
            self._entity_tags[entity_key] = []
        self._entity_tags[entity_key].append(tag.id)
        
        return tag
    
    def get_tags_for_entity(self, entity_type: str, entity_id: str) -> List[SemanticTag]:
        """Get tags for an entity."""
        entity_key = f"{entity_type}:{entity_id}"
        tag_ids = self._entity_tags.get(entity_key, [])
        return [self._tags[tid] for tid in tag_ids if tid in self._tags]
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def get_class_count(self) -> int:
        """Get total class count."""
        return len(self._classes)
    
    def get_domain_count(self) -> int:
        """Get total domain count."""
        return len(self._domains)
    
    def get_taxonomy_count(self) -> int:
        """Get total taxonomy count."""
        return len(self._taxonomies)
    
    def get_capability_count(self) -> int:
        """Get total capability count."""
        return len(self._capabilities)
