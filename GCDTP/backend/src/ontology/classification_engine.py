"""
Classification Engine

Provides entity classification capabilities.
"""

from typing import Dict, List, Optional, Set
from datetime import datetime
from backend.src.ontology.ontology_registry import OntologyRegistry
from backend.src.ontology.ontology_types import (
    OntologyClass,
    Classification,
    SemanticTag,
)


class ClassificationEngine:
    """
    Provides entity classification.
    
    Responsibilities:
    - Asset classification
    - Document classification
    - Work order classification
    - Device classification
    - Organization classification
    """
    
    def __init__(self, registry: Optional[OntologyRegistry] = None):
        self.registry = registry or OntologyRegistry()
    
    def classify_asset(
        self,
        asset_id: str,
        class_id: str,
        confidence: float = 1.0,
        source: str = ""
    ) -> Classification:
        """Classify an asset."""
        return self._classify_entity("asset", asset_id, class_id, confidence, source)
    
    def classify_document(
        self,
        document_id: str,
        class_id: str,
        confidence: float = 1.0,
        source: str = ""
    ) -> Classification:
        """Classify a document."""
        return self._classify_entity("document", document_id, class_id, confidence, source)
    
    def classify_work_order(
        self,
        work_order_id: str,
        class_id: str,
        confidence: float = 1.0,
        source: str = ""
    ) -> Classification:
        """Classify a work order."""
        return self._classify_entity("work_order", work_order_id, class_id, confidence, source)
    
    def classify_device(
        self,
        device_id: str,
        class_id: str,
        confidence: float = 1.0,
        source: str = ""
    ) -> Classification:
        """Classify a device."""
        return self._classify_entity("device", device_id, class_id, confidence, source)
    
    def classify_organization(
        self,
        organization_id: str,
        class_id: str,
        confidence: float = 1.0,
        source: str = ""
    ) -> Classification:
        """Classify an organization."""
        return self._classify_entity("organization", organization_id, class_id, confidence, source)
    
    def _classify_entity(
        self,
        entity_type: str,
        entity_id: str,
        class_id: str,
        confidence: float,
        source: str
    ) -> Classification:
        """Internal classification method."""
        ontology_class = self.registry.get_class(class_id)
        if not ontology_class:
            return Classification(
                entity_type=entity_type,
                entity_id=entity_id,
                class_id=""
            )
        
        # Assign tag
        self.registry.assign_tag(
            entity_type=entity_type,
            entity_id=entity_id,
            class_id=class_id,
            confidence=confidence,
            source=source
        )
        
        # Get domain
        domain = self.registry.get_domain(ontology_class.domain_id)
        domain_name = domain.name if domain else ""
        
        return Classification(
            entity_type=entity_type,
            entity_id=entity_id,
            class_id=class_id,
            class_name=ontology_class.name,
            domain_name=domain_name,
            confidence=confidence,
            source=source
        )
    
    def get_entity_classification(
        self,
        entity_type: str,
        entity_id: str
    ) -> Optional[Classification]:
        """
        Get classification for an entity.
        
        Args:
            entity_type: Entity type
            entity_id: Entity ID
            
        Returns:
            Classification or None
        """
        tags = self.registry.get_tags_for_entity(entity_type, entity_id)
        
        if not tags:
            return None
        
        # Return most confident classification
        best_tag = max(tags, key=lambda t: t.confidence)
        ontology_class = self.registry.get_class(best_tag.class_id)
        
        if not ontology_class:
            return None
        
        domain = self.registry.get_domain(ontology_class.domain_id)
        
        return Classification(
            entity_type=entity_type,
            entity_id=entity_id,
            class_id=best_tag.class_id,
            class_name=ontology_class.name,
            domain_name=domain.name if domain else "",
            confidence=best_tag.confidence,
            source=best_tag.source,
            assigned_at=best_tag.assigned_at
        )
    
    def get_entity_classifications(
        self,
        entity_type: str,
        entity_id: str
    ) -> List[Classification]:
        """
        Get all classifications for an entity.
        
        Args:
            entity_type: Entity type
            entity_id: Entity ID
            
        Returns:
            List of Classifications
        """
        tags = self.registry.get_tags_for_entity(entity_type, entity_id)
        classifications = []
        
        for tag in tags:
            ontology_class = self.registry.get_class(tag.class_id)
            if ontology_class:
                domain = self.registry.get_domain(ontology_class.domain_id)
                classifications.append(Classification(
                    entity_type=entity_type,
                    entity_id=entity_id,
                    class_id=tag.class_id,
                    class_name=ontology_class.name,
                    domain_name=domain.name if domain else "",
                    confidence=tag.confidence,
                    source=tag.source,
                    assigned_at=tag.assigned_at
                ))
        
        return sorted(classifications, key=lambda c: c.confidence, reverse=True)
    
    def find_entities_by_class(
        self,
        entity_type: str,
        class_id: str,
        include_subclasses: bool = True
    ) -> List[str]:
        """
        Find entities with a specific class.
        
        Args:
            entity_type: Entity type
            class_id: Class ID
            include_subclasses: Include entities with subclass
            
        Returns:
            List of entity IDs
        """
        entity_ids: Set[str] = set()
        
        # Direct class matches
        tags = [
            tag for tag in self.registry._tags.values()
            if tag.entity_type == entity_type and tag.class_id == class_id
        ]
        entity_ids.update(tag.entity_id for tag in tags)
        
        # Subclass matches
        if include_subclasses:
            from backend.src.ontology.taxonomy_engine import TaxonomyEngine
            taxonomy = TaxonomyEngine(self.registry)
            subclasses = taxonomy.get_subclasses(class_id)
            
            for subclass in subclasses:
                subclass_tags = [
                    tag for tag in self.registry._tags.values()
                    if tag.entity_type == entity_type and tag.class_id == subclass.id
                ]
                entity_ids.update(tag.entity_id for tag in subclass_tags)
        
        return list(entity_ids)
    
    def remove_classification(
        self,
        entity_type: str,
        entity_id: str,
        class_id: str
    ) -> bool:
        """
        Remove a classification from an entity.
        
        Args:
            entity_type: Entity type
            entity_id: Entity ID
            class_id: Class ID
            
        Returns:
            True if removed
        """
        entity_key = f"{entity_type}:{entity_id}"
        tag_ids = self.registry._entity_tags.get(entity_key, [])
        
        for tag_id in tag_ids:
            tag = self.registry._tags.get(tag_id)
            if tag and tag.class_id == class_id:
                del self.registry._tags[tag_id]
                tag_ids.remove(tag_id)
                return True
        
        return False
    
    def get_class_entities(
        self,
        class_id: str,
        entity_types: Optional[List[str]] = None
    ) -> Dict[str, List[str]]:
        """
        Get all entities for a class grouped by type.
        
        Args:
            class_id: Class ID
            entity_types: Filter by entity types
            
        Returns:
            Dictionary of entity_type -> [entity_ids]
        """
        tags = [
            tag for tag in self.registry._tags.values()
            if tag.class_id == class_id
        ]
        
        if entity_types:
            tags = [t for t in tags if t.entity_type in entity_types]
        
        result: Dict[str, List[str]] = {}
        for tag in tags:
            if tag.entity_type not in result:
                result[tag.entity_type] = []
            result[tag.entity_type].append(tag.entity_id)
        
        return result
