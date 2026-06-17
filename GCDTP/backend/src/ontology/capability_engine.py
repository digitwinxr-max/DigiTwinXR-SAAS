"""
Capability Engine

Manages capabilities and cross-domain capability analysis.
"""

from typing import Dict, List, Optional, Set
from backend.src.ontology.ontology_registry import OntologyRegistry
from backend.src.ontology.ontology_types import (
    Capability,
    CapabilitySet,
)


class CapabilityEngine:
    """
    Manages capabilities.
    
    Responsibilities:
    - Capability lookup
    - Shared capabilities
    - Cross-domain capabilities
    - Dependency capabilities
    """
    
    def __init__(self, registry: Optional[OntologyRegistry] = None):
        self.registry = registry or OntologyRegistry()
    
    def get_class_capabilities(
        self,
        class_id: str,
        include_inherited: bool = True
    ) -> List[Capability]:
        """
        Get capabilities for a class.
        
        Args:
            class_id: Class ID
            include_inherited: Include inherited capabilities
            
        Returns:
            List of Capabilities
        """
        if include_inherited:
            from backend.src.ontology.inheritance_engine import InheritanceEngine
            engine = InheritanceEngine(self.registry)
            cap_set = engine.get_inherited_capabilities(class_id)
            return cap_set.own_capabilities + cap_set.inherited_capabilities
        
        return self.registry.get_capabilities_for_class(class_id)
    
    def find_shared_capabilities(
        self,
        class_id1: str,
        class_id2: str
    ) -> List[Capability]:
        """
        Find capabilities shared between two classes.
        
        Args:
            class_id1: First class ID
            class_id2: Second class ID
            
        Returns:
            List of shared Capabilities
        """
        caps1 = set(c.name for c in self.get_class_capabilities(class_id1))
        caps2 = set(c.name for c in self.get_class_capabilities(class_id2))
        
        shared_names = caps1 & caps2
        
        all_caps = {c.name: c for c in self.get_class_capabilities(class_id1)}
        all_caps.update({c.name: c for c in self.get_class_capabilities(class_id2)})
        
        return [all_caps[name] for name in shared_names if name in all_caps]
    
    def find_cross_domain_capabilities(
        self,
        domain1_id: str,
        domain2_id: str
    ) -> Dict[str, List[str]]:
        """
        Find capabilities that exist in both domains.
        
        Args:
            domain1_id: First domain ID
            domain2_id: Second domain ID
            
        Returns:
            Dictionary of capability_name -> [class_names]
        """
        # Get classes in each domain
        classes1 = self.registry.get_classes_for_domain(domain1_id)
        classes2 = self.registry.get_classes_for_domain(domain2_id)
        
        # Get capabilities for each domain
        caps1: Set[str] = set()
        caps2: Set[str] = set()
        
        for c in classes1:
            for cap in self.get_class_capabilities(c.id):
                caps1.add(cap.name)
        
        for c in classes2:
            for cap in self.get_class_capabilities(c.id):
                caps2.add(cap.name)
        
        # Find shared
        shared = caps1 & caps2
        
        result: Dict[str, List[str]] = {}
        for cap_name in shared:
            classes_with_cap = []
            for c in classes1 + classes2:
                for cap in self.get_class_capabilities(c.id):
                    if cap.name == cap_name:
                        classes_with_cap.append(c.name)
            result[cap_name] = classes_with_cap
        
        return result
    
    def find_capability_dependencies(
        self,
        class_id: str,
        capability_name: str
    ) -> List[str]:
        """
        Find capabilities that depend on a specific capability.
        
        Args:
            class_id: Class ID
            capability_name: Capability name
            
        Returns:
            List of dependent capability names
        """
        dependencies: List[str] = []
        
        # Get all capabilities for the class
        caps = self.get_class_capabilities(class_id)
        
        for cap in caps:
            if cap.requirements:
                if capability_name in cap.requirements:
                    dependencies.append(cap.name)
        
        return dependencies
    
    def get_capability_requirement_chain(
        self,
        class_id: str,
        capability_name: str
    ) -> List[str]:
        """
        Get the full requirement chain for a capability.
        
        Args:
            class_id: Class ID
            capability_name: Capability name
            
        Returns:
            Ordered list of requirements
        """
        chain: List[str] = []
        visited: Set[str] = set()
        
        caps = {c.name: c for c in self.get_class_capabilities(class_id)}
        
        def collect_requirements(name: str):
            if name in visited or name not in caps:
                return
            
            visited.add(name)
            cap = caps[name]
            
            if cap.requirements:
                for req in cap.requirements:
                    collect_requirements(req)
                    chain.append(req)
        
        collect_requirements(capability_name)
        return chain
    
    def find_classes_with_capability(
        self,
        capability_name: str
    ) -> List[str]:
        """
        Find all classes with a specific capability.
        
        Args:
            capability_name: Capability name
            
        Returns:
            List of class IDs
        """
        class_ids = []
        
        for ontology_class in self.registry.get_all_classes():
            for cap in self.get_class_capabilities(ontology_class.id):
                if cap.name == capability_name:
                    class_ids.append(ontology_class.id)
                    break
        
        return class_ids
    
    def get_capability_usage_stats(self) -> Dict[str, int]:
        """
        Get usage statistics for all capabilities.
        
        Returns:
            Dictionary of capability_name -> usage_count
        """
        stats: Dict[str, int] = {}
        
        for ontology_class in self.registry.get_all_classes():
            for cap in self.get_class_capabilities(ontology_class.id):
                stats[cap.name] = stats.get(cap.name, 0) + 1
        
        return stats
