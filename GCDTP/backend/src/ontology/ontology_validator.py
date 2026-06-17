"""
Ontology Validator

Validates ontology classes, taxonomies, and capabilities.
"""

from typing import Dict, List, Set, Optional
from backend.src.ontology.ontology_types import (
    OntologyClass,
    OntologyRelationship,
    Capability,
)


class OntologyValidator:
    """
    Validates ontology entities.
    
    Checks:
    - Duplicate classes
    - Cyclic taxonomies
    - Inheritance conflicts
    - Capability conflicts
    - Semantic consistency
    """
    
    def __init__(self):
        self.issues: List[str] = []
    
    def validate_class(self, ontology_class: OntologyClass) -> List[str]:
        """
        Validate an ontology class.
        
        Args:
            ontology_class: Class to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not ontology_class.id:
            issues.append("Class ID is required")
        
        if not ontology_class.name or not ontology_class.name.strip():
            issues.append("Class name is required")
        
        if not ontology_class.display_name or not ontology_class.display_name.strip():
            issues.append("Class display name is required")
        
        if ontology_class.name:
            if len(ontology_class.name) > 255:
                issues.append("Class name must be 255 characters or less")
            
            # Check for invalid characters
            if not ontology_class.name.replace("_", "").isalnum():
                issues.append("Class name must be alphanumeric with underscores")
        
        return issues
    
    def validate_relationship(
        self,
        relationship: OntologyRelationship,
        existing_class_ids: Set[str]
    ) -> List[str]:
        """
        Validate an ontology relationship.
        
        Args:
            relationship: Relationship to validate
            existing_class_ids: Set of existing class IDs
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not relationship.id:
            issues.append("Relationship ID is required")
        
        if not relationship.source_class_id:
            issues.append("Source class ID is required")
        
        if not relationship.target_class_id:
            issues.append("Target class ID is required")
        
        if not relationship.relationship_type:
            issues.append("Relationship type is required")
        
        if relationship.source_class_id not in existing_class_ids:
            issues.append("Source class does not exist")
        
        if relationship.target_class_id not in existing_class_ids:
            issues.append("Target class does not exist")
        
        if relationship.source_class_id == relationship.target_class_id:
            issues.append("Self-referencing relationships not allowed")
        
        return issues
    
    def validate_capability(self, capability: Capability) -> List[str]:
        """
        Validate a capability.
        
        Args:
            capability: Capability to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not capability.id:
            issues.append("Capability ID is required")
        
        if not capability.name or not capability.name.strip():
            issues.append("Capability name is required")
        
        if not capability.display_name or not capability.display_name.strip():
            issues.append("Capability display name is required")
        
        return issues
    
    def check_cyclic_taxonomy(
        self,
        class_id: str,
        parent_class_id: str,
        existing_classes: Dict[str, OntologyClass]
    ) -> bool:
        """
        Check for cyclic taxonomy.
        
        Args:
            class_id: Class ID
            parent_class_id: Proposed parent class ID
            existing_classes: Map of existing classes
            
        Returns:
            True if cyclic
        """
        visited: Set[str] = set()
        current_id = parent_class_id
        
        while current_id:
            if current_id in visited:
                return True
            
            if current_id == class_id:
                return True
            
            visited.add(current_id)
            
            if current_id in existing_classes:
                current_id = existing_classes[current_id].parent_class_id
            else:
                break
        
        return False
    
    def check_duplicate_class(
        self,
        name: str,
        domain_id: str,
        existing_classes: Dict[str, OntologyClass]
    ) -> bool:
        """
        Check for duplicate class.
        
        Args:
            name: Class name
            domain_id: Domain ID
            existing_classes: Map of existing classes
            
        Returns:
            True if duplicate
        """
        for ontology_class in existing_classes.values():
            if (ontology_class.name == name and 
                ontology_class.domain_id == domain_id):
                return True
        return False
    
    def check_inheritance_conflicts(
        self,
        class_id: str,
        parent_class_id: str,
        existing_classes: Dict[str, OntologyClass]
    ) -> List[str]:
        """
        Check for inheritance conflicts.
        
        Args:
            class_id: Class ID
            parent_class_id: Parent class ID
            existing_classes: Map of existing classes
            
        Returns:
            List of conflicts
        """
        conflicts = []
        
        if parent_class_id not in existing_classes:
            return conflicts
        
        parent = existing_classes[parent_class_id]
        
        # Check domain conflict
        if class_id in existing_classes:
            child = existing_classes[class_id]
            if child.domain_id != parent.domain_id:
                conflicts.append("Cannot inherit from class in different domain")
        
        # Check abstract conflict
        if parent.is_abstract:
            conflicts.append("Cannot inherit from abstract class")
        
        return conflicts
    
    def check_capability_conflicts(
        self,
        capability: Capability,
        existing_capabilities: List[Capability]
    ) -> List[str]:
        """
        Check for capability conflicts.
        
        Args:
            capability: Capability to check
            existing_capabilities: List of existing capabilities
            
        Returns:
            List of conflicts
        """
        conflicts = []
        
        for existing in existing_capabilities:
            if (existing.class_id == capability.class_id and
                existing.name == capability.name):
                conflicts.append(f"Duplicate capability: {capability.name}")
        
        return conflicts
    
    def validate_taxonomy_path(
        self,
        path: str,
        class_ids: List[str]
    ) -> List[str]:
        """
        Validate taxonomy path.
        
        Args:
            path: Slash-separated path
            class_ids: List of class IDs in path
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not path:
            issues.append("Taxonomy path is required")
            return issues
        
        # Check path structure
        parts = path.split("/")
        if len(parts) != len(class_ids):
            issues.append("Path and class IDs mismatch")
        
        # Check for empty parts
        for part in parts:
            if not part.strip():
                issues.append("Empty path segment not allowed")
        
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
