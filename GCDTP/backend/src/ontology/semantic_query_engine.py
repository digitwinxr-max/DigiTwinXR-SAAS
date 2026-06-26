"""
Semantic Query Engine

Provides semantic query capabilities.
"""

from typing import Dict, List, Optional, Set
from backend.src.ontology.ontology_registry import OntologyRegistry
from backend.src.ontology.ontology_types import (
    OntologyClass,
    SemanticQueryResult,
)


class SemanticQueryEngine:
    """
    Provides semantic query capabilities.
    
    Responsibilities:
    - Find by class
    - Find by capability
    - Find related classes
    - Taxonomy traversal
    - Ancestor lookup
    - Descendant lookup
    """
    
    def __init__(self, registry: Optional[OntologyRegistry] = None):
        self.registry = registry or OntologyRegistry()
    
    def find_by_class(
        self,
        class_name: str,
        domain_name: Optional[str] = None
    ) -> SemanticQueryResult:
        """
        Find classes by name.
        
        Args:
            class_name: Class name to search
            domain_name: Optional domain filter
            
        Returns:
            SemanticQueryResult
        """
        results = []
        
        for ontology_class in self.registry.get_all_classes():
            if class_name.lower() in ontology_class.name.lower():
                if domain_name:
                    domain = self.registry.get_domain(ontology_class.domain_id)
                    if domain and domain.name != domain_name:
                        continue
                results.append(ontology_class)
        
        return SemanticQueryResult(
            classes=results,
            result_count=len(results),
            query_type="find_by_class"
        )
    
    def find_by_capability(
        self,
        capability_name: str
    ) -> SemanticQueryResult:
        """
        Find classes with a specific capability.
        
        Args:
            capability_name: Capability name
            
        Returns:
            SemanticQueryResult
        """
        from backend.src.ontology.capability_engine import CapabilityEngine
        
        cap_engine = CapabilityEngine(self.registry)
        class_ids = cap_engine.find_classes_with_capability(capability_name)
        
        classes = [self.registry.get_class(cid) for cid in class_ids]
        classes = [c for c in classes if c]
        
        return SemanticQueryResult(
            classes=classes,
            result_count=len(classes),
            query_type="find_by_capability"
        )
    
    def find_related_classes(
        self,
        class_id: str,
        relationship_type: Optional[str] = None
    ) -> SemanticQueryResult:
        """
        Find classes related to a given class.
        
        Args:
            class_id: Class ID
            relationship_type: Optional relationship type filter
            
        Returns:
            SemanticQueryResult
        """
        relationships = self.registry.get_relationships_for_class(class_id)
        
        related_ids: Set[str] = set()
        for rel in relationships:
            if relationship_type and rel.relationship_type != relationship_type:
                continue
            if rel.source_class_id == class_id:
                related_ids.add(rel.target_class_id)
            if rel.target_class_id == class_id:
                related_ids.add(rel.source_class_id)
        
        classes = [self.registry.get_class(cid) for cid in related_ids]
        classes = [c for c in classes if c]
        
        return SemanticQueryResult(
            classes=classes,
            result_count=len(classes),
            query_type="find_related"
        )
    
    def find_ancestors(self, class_id: str) -> SemanticQueryResult:
        """
        Find ancestor classes.
        
        Args:
            class_id: Class ID
            
        Returns:
            SemanticQueryResult
        """
        from backend.src.ontology.taxonomy_engine import TaxonomyEngine
        
        taxonomy = TaxonomyEngine(self.registry)
        parents = taxonomy.get_parent_classes(class_id)
        
        return SemanticQueryResult(
            classes=parents,
            result_count=len(parents),
            query_type="find_ancestors"
        )
    
    def find_descendants(self, class_id: str) -> SemanticQueryResult:
        """
        Find descendant classes.
        
        Args:
            class_id: Class ID
            
        Returns:
            SemanticQueryResult
        """
        from backend.src.ontology.taxonomy_engine import TaxonomyEngine
        
        taxonomy = TaxonomyEngine(self.registry)
        subclasses = taxonomy.get_subclasses(class_id)
        
        return SemanticQueryResult(
            classes=subclasses,
            result_count=len(subclasses),
            query_type="find_descendants"
        )
    
    def find_by_domain(self, domain_name: str) -> SemanticQueryResult:
        """
        Find all classes in a domain.
        
        Args:
            domain_name: Domain name
            
        Returns:
            SemanticQueryResult
        """
        domain = self.registry.get_domain_by_name(domain_name)
        if not domain:
            return SemanticQueryResult(
                classes=[],
                result_count=0,
                query_type="find_by_domain"
            )
        
        classes = self.registry.get_classes_for_domain(domain.id)
        
        return SemanticQueryResult(
            classes=classes,
            result_count=len(classes),
            query_type="find_by_domain"
        )
    
    def find_at_level(
        self,
        domain_name: str,
        level: int
    ) -> SemanticQueryResult:
        """
        Find classes at a specific hierarchy level.
        
        Args:
            domain_name: Domain name
            level: Hierarchy level
            
        Returns:
            SemanticQueryResult
        """
        from backend.src.ontology.taxonomy_engine import TaxonomyEngine
        
        domain = self.registry.get_domain_by_name(domain_name)
        if not domain:
            return SemanticQueryResult(
                classes=[],
                result_count=0,
                query_type="find_at_level"
            )
        
        taxonomy = TaxonomyEngine(self.registry)
        classes = taxonomy.get_level_classes(domain.id, level)
        
        return SemanticQueryResult(
            classes=classes,
            result_count=len(classes),
            query_type="find_at_level"
        )
    
    def find_root_classes(self, domain_name: str) -> SemanticQueryResult:
        """
        Find root classes in a domain.
        
        Args:
            domain_name: Domain name
            
        Returns:
            SemanticQueryResult
        """
        from backend.src.ontology.taxonomy_engine import TaxonomyEngine
        
        domain = self.registry.get_domain_by_name(domain_name)
        if not domain:
            return SemanticQueryResult(
                classes=[],
                result_count=0,
                query_type="find_root"
            )
        
        taxonomy = TaxonomyEngine(self.registry)
        classes = taxonomy.get_root_classes(domain.id)
        
        return SemanticQueryResult(
            classes=classes,
            result_count=len(classes),
            query_type="find_root"
        )
    
    def search(self, query: str) -> SemanticQueryResult:
        """
        Search for classes by name or description.
        
        Args:
            query: Search query
            
        Returns:
            SemanticQueryResult
        """
        query_lower = query.lower()
        results = []
        
        for ontology_class in self.registry.get_all_classes():
            if (query_lower in ontology_class.name.lower() or
                query_lower in ontology_class.display_name.lower() or
                query_lower in ontology_class.description.lower()):
                results.append(ontology_class)
        
        return SemanticQueryResult(
            classes=results,
            result_count=len(results),
            query_type="search"
        )
