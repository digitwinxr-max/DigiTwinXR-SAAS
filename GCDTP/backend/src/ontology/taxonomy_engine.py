"""
Taxonomy Engine

Manages class hierarchies and taxonomy traversal.
"""

from typing import Dict, List, Optional, Set
from backend.src.ontology.ontology_registry import OntologyRegistry
from backend.src.ontology.ontology_types import (
    OntologyClass,
    ClassHierarchy,
)


class TaxonomyEngine:
    """
    Manages class hierarchies and taxonomy operations.
    
    Responsibilities:
    - Class hierarchy management
    - Subclass traversal
    - Parent class lookup
    - Taxonomy traversal
    - Classification lookup
    """
    
    def __init__(self, registry: Optional[OntologyRegistry] = None):
        self.registry = registry or OntologyRegistry()
    
    def get_class_hierarchy(self, class_id: str) -> ClassHierarchy:
        """
        Get the full hierarchy for a class.
        
        Args:
            class_id: Class ID
            
        Returns:
            ClassHierarchy
        """
        ontology_class = self.registry.get_class(class_id)
        if not ontology_class:
            return ClassHierarchy(ontology_class=OntologyClass(
                id="",
                domain_id="",
                name="",
                display_name=""
            ))
        
        subclasses = self.get_subclasses(class_id)
        parent_classes = self.get_parent_classes(class_id)
        
        # Get ancestors
        ancestors = []
        current = ontology_class.parent_class_id
        while current:
            parent = self.registry.get_class(current)
            if parent:
                ancestors.append(parent.name)
                current = parent.parent_class_id
            else:
                break
        
        # Get descendants
        descendants = self._collect_descendants(class_id)
        
        return ClassHierarchy(
            ontology_class=ontology_class,
            subclasses=subclasses,
            parent_classes=parent_classes,
            depth=ontology_class.level,
            ancestors=ancestors,
            descendants=descendants
        )
    
    def get_subclasses(self, class_id: str, direct_only: bool = False) -> List[OntologyClass]:
        """
        Get subclasses of a class.
        
        Args:
            class_id: Class ID
            direct_only: Only direct subclasses
            
        Returns:
            List of OntologyClass
        """
        subclasses = []
        
        for ontology_class in self.registry.get_all_classes():
            if ontology_class.parent_class_id == class_id:
                subclasses.append(ontology_class)
                
                if not direct_only:
                    # Recursively get subclasses
                    nested = self.get_subclasses(ontology_class.id)
                    subclasses.extend(nested)
        
        return subclasses
    
    def get_parent_classes(self, class_id: str) -> List[OntologyClass]:
        """
        Get parent classes of a class.
        
        Args:
            class_id: Class ID
            
        Returns:
            List of OntologyClass (from direct parent to root)
        """
        parents = []
        current_id = class_id
        
        while True:
            ontology_class = self.registry.get_class(current_id)
            if not ontology_class or not ontology_class.parent_class_id:
                break
            
            parent = self.registry.get_class(ontology_class.parent_class_id)
            if parent:
                parents.append(parent)
                current_id = parent.id
            else:
                break
        
        return parents
    
    def get_root_classes(self, domain_id: str) -> List[OntologyClass]:
        """
        Get root classes (classes with no parent) in a domain.
        
        Args:
            domain_id: Domain ID
            
        Returns:
            List of root classes
        """
        return [
            c for c in self.registry.get_classes_for_domain(domain_id)
            if c.parent_class_id is None
        ]
    
    def get_level_classes(self, domain_id: str, level: int) -> List[OntologyClass]:
        """
        Get all classes at a specific level in a domain.
        
        Args:
            domain_id: Domain ID
            level: Hierarchy level
            
        Returns:
            List of classes at that level
        """
        return [
            c for c in self.registry.get_classes_for_domain(domain_id)
            if c.level == level
        ]
    
    def get_class_depth(self, class_id: str) -> int:
        """
        Get the depth of a class in its hierarchy.
        
        Args:
            class_id: Class ID
            
        Returns:
            Depth (root = 0)
        """
        ontology_class = self.registry.get_class(class_id)
        if not ontology_class:
            return -1
        
        depth = 0
        current_id = ontology_class.parent_class_id
        
        while current_id:
            depth += 1
            parent = self.registry.get_class(current_id)
            if parent:
                current_id = parent.parent_class_id
            else:
                break
        
        return depth
    
    def get_path(self, class_id: str) -> str:
        """
        Get the path from root to this class.
        
        Args:
            class_id: Class ID
            
        Returns:
            Slash-separated path
        """
        ontology_class = self.registry.get_class(class_id)
        if not ontology_class:
            return ""
        
        return ontology_class.path
    
    def get_children_at_level(
        self,
        class_id: str,
        target_level: int
    ) -> List[OntologyClass]:
        """
        Get all descendants of a class at a specific level.
        
        Args:
            class_id: Class ID
            target_level: Target hierarchy level
            
        Returns:
            List of classes at target level
        """
        descendants = self._collect_descendants(class_id)
        return [d for d in descendants if d.level == target_level]
    
    def _collect_descendants(self, class_id: str) -> List[OntologyClass]:
        """Recursively collect all descendants."""
        descendants = []
        subclasses = self.get_subclasses(class_id, direct_only=True)
        
        for subclass in subclasses:
            descendants.append(subclass)
            nested = self._collect_descendants(subclass.id)
            descendants.extend(nested)
        
        return descendants
    
    def get_siblings(self, class_id: str) -> List[OntologyClass]:
        """
        Get sibling classes (classes with the same parent).
        
        Args:
            class_id: Class ID
            
        Returns:
            List of sibling classes
        """
        ontology_class = self.registry.get_class(class_id)
        if not ontology_class or not ontology_class.parent_class_id:
            return []
        
        return [
            c for c in self.registry.get_all_classes()
            if c.parent_class_id == ontology_class.parent_class_id
            and c.id != class_id
        ]
    
    def is_ancestor_of(self, ancestor_id: str, descendant_id: str) -> bool:
        """
        Check if one class is an ancestor of another.
        
        Args:
            ancestor_id: Potential ancestor class ID
            descendant_id: Potential descendant class ID
            
        Returns:
            True if ancestor_id is an ancestor of descendant_id
        """
        current_id = descendant_id
        
        while True:
            ontology_class = self.registry.get_class(current_id)
            if not ontology_class or not ontology_class.parent_class_id:
                return False
            
            if ontology_class.parent_class_id == ancestor_id:
                return True
            
            current_id = ontology_class.parent_class_id
    
    def is_descendant_of(self, descendant_id: str, ancestor_id: str) -> bool:
        """Check if one class is a descendant of another."""
        return self.is_ancestor_of(ancestor_id, descendant_id)
    
    def get_common_ancestor(self, class_id1: str, class_id2: str) -> Optional[OntologyClass]:
        """
        Find the common ancestor of two classes.
        
        Args:
            class_id1: First class ID
            class_id2: Second class ID
            
        Returns:
            Common ancestor or None
        """
        # Get ancestors of first class
        ancestors1 = set()
        current_id = class_id1
        while True:
            ontology_class = self.registry.get_class(current_id)
            if not ontology_class:
                break
            ancestors1.add(ontology_class.id)
            if ontology_class.parent_class_id:
                current_id = ontology_class.parent_class_id
            else:
                break
        
        # Check ancestors of second class
        current_id = class_id2
        while True:
            ontology_class = self.registry.get_class(current_id)
            if not ontology_class:
                return None
            
            if ontology_class.id in ancestors1:
                return ontology_class
            
            if ontology_class.parent_class_id:
                current_id = ontology_class.parent_class_id
            else:
                break
        
        return None
