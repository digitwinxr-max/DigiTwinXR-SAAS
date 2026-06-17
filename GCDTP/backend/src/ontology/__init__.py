"""
Semantic Ontology Module

Provides meaning and classification across all domains.
No AI, no inference engines.

Components:
- Ontology Registry
- Taxonomy Engine
- Classification Engine
- Inheritance Engine
- Capability Engine
- Semantic Query Engine
- Ontology Validator
- Ontology Sync Engine
"""

from .ontology_types import (
    OntologyDomain,
    SyncStatus,
    OntologyClass,
    OntologyRelationship,
    Taxonomy,
    Capability,
    SemanticTag,
    Classification,
    ClassHierarchy,
    CapabilitySet,
    SemanticQueryResult,
    SyncRecord,
)

from .ontology_registry import OntologyRegistry
from .taxonomy_engine import TaxonomyEngine
from .classification_engine import ClassificationEngine
from .inheritance_engine import InheritanceEngine
from .capability_engine import CapabilityEngine
from .semantic_query_engine import SemanticQueryEngine
from .ontology_validator import OntologyValidator
from .ontology_sync_engine import OntologySyncEngine


__all__ = [
    # Enums
    "OntologyDomain",
    "SyncStatus",
    # Types
    "OntologyClass",
    "OntologyRelationship",
    "Taxonomy",
    "Capability",
    "SemanticTag",
    "Classification",
    "ClassHierarchy",
    "CapabilitySet",
    "SemanticQueryResult",
    "SyncRecord",
    # Engines
    "OntologyRegistry",
    "TaxonomyEngine",
    "ClassificationEngine",
    "InheritanceEngine",
    "CapabilityEngine",
    "SemanticQueryEngine",
    "OntologyValidator",
    "OntologySyncEngine",
]
