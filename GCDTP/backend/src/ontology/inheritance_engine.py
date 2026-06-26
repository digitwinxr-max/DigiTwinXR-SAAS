"""
Inheritance Engine

Manages property, capability, and taxonomy inheritance.
"""

from typing import Dict, List, Optional, Set
from backend.src.ontology.ontology_registry import OntologyRegistry
from backend.src.ontology.ontology_types import (
    OntologyClass,
    Capability,
    CapabilitySet,
)


class InheritanceEngine:
    """
    Manages inheritance across the ontology.
    
    Responsibilities:
    - Property inheritance
    - Capability inheritance
    - Taxonomy inheritance
    - Semantic propagation
    """
    
    def __init__(self, registry: Optional[OntologyRegistry] = None):
        self.registry = registry or OntologyRegistry()
    
    def get_inherited_properties(self, class_id: str) -> Dict[str, any]:
        """
        Get all inherited properties for a class.
        
        Args:
            class_id: Class ID
            
        Returns:
            Dictionary of property name -> value
        """
        properties: Dict[str, any] = {}
        
        # Collect properties from ancestors
        ancestors = self._get_ancestor_chain(class_id)
        ancestors.reverse()  # Start from root
        
        for ancestor in ancestors:
            if ancestor.properties:
                properties.update(ancestor.properties)
        
        # Add own properties
        ontology_class = self.registry.get_class(class_id)
        if ontology_class and ontology_class.properties:
            properties.update(ontology_class.properties)
        
        return properties
    
    def get_inherited_capabilities(self, class_id: str) -> CapabilitySet:
        """
        Get all inherited capabilities for a class.
        
        Args:
            class_id: Class ID
            
        Returns:
            CapabilitySet
        """
        capability_set = CapabilitySet()
        
        # Get own capabilities
        own_caps = self.registry.get_capabilities_for_class(class_id)
        capability_set.own_capabilities = own_caps
        capability_set.direct_count = len(own_caps)
        
        # Get inherited capabilities
        inherited: List[Capability] = []
        ancestors = self._get_ancestor_chain(class_id)
        
        for ancestor in ancestors:
            ancestor_caps = self.registry.get_capabilities_for_class(ancestor.id)
            for cap in ancestor_caps:
                cap.inherited = True
                inherited.append(cap)
        
        capability_set.inherited_capabilities = inherited
        capability_set.total_count = len(own_caps) + len(inherited)
        
        return capability_set
    
    def get_taxonomy_inheritance(self, class_id: str) -> List[str]:
        """
        Get taxonomy inheritance path for a class.
        
        Args:
            class_id: Class ID
            
        Returns:
            List of class IDs from root to this class
        """
        chain = self._get_ancestor_chain(class_id)
        chain.append(self.registry.get_class(class_id))
        return [c.id for c in chain if c]
    
    def propagate_semantic_tags(
        self,
        source_entity_type: str,
        source_entity_id: str,
        target_entity_type: str,
        target_entity_id: str
    ) -> List[str]:
        """
        Propagate semantic tags from one entity to another.
        
        Args:
            source_entity_type: Source entity type
            source_entity_id: Source entity ID
            target_entity_type: Target entity type
            target_entity_id: Target entity ID
            
        Returns:
            List of new tag IDs
        """
        # Get source tags
        source_tags = self.registry.get_tags_for_entity(source_entity_type, source_entity_id)
        
        new_tag_ids = []
        for tag in source_tags:
            new_tag = self.registry.assign_tag(
                entity_type=target_entity_type,
                entity_id=target_entity_id,
                class_id=tag.class_id,
                confidence=tag.confidence * 0.9,  # Reduce confidence for propagated
                source=f"propagated_from:{source_entity_id}"
            )
            new_tag_ids.append(new_tag.id)
        
        return new_tag_ids
    
    def get_property_value(self, class_id: str, property_name: str) -> Optional[any]:
        """
        Get a property value for a class, checking inheritance.
        
        Args:
            class_id: Class ID
            property_name: Property name
            
        Returns:
            Property value or None
        """
        properties = self.get_inherited_properties(class_id)
        return properties.get(property_name)
    
    def has_capability(self, class_id: str, capability_name: str) -> bool:
        """
        Check if a class has a capability (including inherited).
        
        Args:
            class_id: Class ID
            capability_name: Capability name
            
        Returns:
            True if class has the capability
        """
        caps = self.get_inherited_capabilities(class_id)
        all_caps = caps.own_capabilities + caps.inherited_capabilities
        
        return any(c.name == capability_name for c in all_caps)
    
    def _get_ancestor_chain(self, class_id: str) -> List[OntologyClass]:
        """Get the chain of ancestors from root to parent."""
        ancestors = []
        current_id = class_id
        
        while True:
            ontology_class = self.registry.get_class(current_id)
            if not ontology_class or not ontology_class.parent_class_id:
                break
            
            parent = self.registry.get_class(ontology_class.parent_class_id)
            if parent:
                ancestors.append(parent)
                current_id = parent.id
            else:
                break
        
        return ancestors
    
    def validate_inheritance(self, class_id: str) -> List[str]:
        """
        Validate inheritance for a class.
        
        Args:
            class_id: Class ID
            
        Returns:
            List of validation issues
        """
        issues = []
        
        ontology_class = self.registry.get_class(class_id)
        if not ontology_class:
            issues.append(f"Class {class_id} not found")
            return issues
        
        # Check for circular inheritance
        visited = set()
        current_id = class_id
        
        while ontology_class.parent_class_id:
            if ontology_class.parent_class_id in visited:
                issues.append("Circular inheritance detected")
                break
            
            visited.add(ontology_class.parent_class_id)
            ontology_class = self.registry.get_class(ontology_class.parent_class_id)
            if not ontology_class:
                break
        
        # Check for abstract class instantiation
        if ontology_class and ontology_class.is_abstract:
            issues.append("Cannot instantiate abstract class")
        
        return issues
