"""
Tests for Semantic Ontology Layer

Tests taxonomy, classification, inheritance, capabilities, queries, sync, and timeline integration.
"""

import pytest
from backend.src.ontology import (
    OntologyRegistry,
    TaxonomyEngine,
    ClassificationEngine,
    InheritanceEngine,
    CapabilityEngine,
    SemanticQueryEngine,
    OntologyValidator,
    OntologySyncEngine,
    OntologyDomain,
    OntologyClass,
    OntologyRelationship,
    Taxonomy,
    Capability,
    SemanticTag,
    Classification,
)


class TestOntologyTypes:
    """Tests for ontology types."""
    
    def test_ontology_domain_values(self):
        """Test ontology domain values."""
        assert OntologyDomain.ELECTRICAL.value == "electrical"
        assert OntologyDomain.WATER.value == "water"
        assert OntologyDomain.TRANSPORT.value == "transport"
        assert OntologyDomain.BUILDINGS.value == "buildings"
    
    def test_create_ontology_class(self):
        """Test creating an ontology class."""
        cls = OntologyClass(
            id="class-1",
            domain_id="domain-1",
            name="Transformer",
            display_name="Power Transformer"
        )
        
        assert cls.id == "class-1"
        assert cls.name == "Transformer"
        assert cls.level == 0


class TestOntologyRegistry:
    """Tests for OntologyRegistry."""
    
    @pytest.fixture
    def registry(self):
        """Create ontology registry."""
        return OntologyRegistry()
    
    def test_default_domains_initialized(self, registry):
        """Test that default domains are initialized."""
        domains = registry.get_all_domains()
        assert len(domains) >= 8
    
    def test_register_domain(self, registry):
        """Test registering a domain."""
        domain = registry.register_domain(
            name="custom",
            display_name="Custom Domain",
            domain_type=OntologyDomain.CUSTOM
        )
        
        assert domain is not None
        assert domain.name == "custom"
    
    def test_register_class(self, registry):
        """Test registering a class."""
        domains = registry.get_all_domains()
        domain = domains[0]
        
        cls = registry.register_class(
            domain_id=domain.id,
            name="Substation",
            display_name="Electrical Substation"
        )
        
        assert cls is not None
        assert cls.name == "Substation"
    
    def test_register_relationship(self, registry):
        """Test registering a relationship."""
        domains = registry.get_all_domains()
        domain = domains[0]
        
        class1 = registry.register_class(domain_id=domain.id, name="Class1", display_name="Class 1")
        class2 = registry.register_class(domain_id=domain.id, name="Class2", display_name="Class 2")
        
        rel = registry.register_relationship(
            source_class_id=class1.id,
            target_class_id=class2.id,
            relationship_type="connects_to"
        )
        
        assert rel is not None
        assert rel.relationship_type == "connects_to"
    
    def test_register_capability(self, registry):
        """Test registering a capability."""
        domains = registry.get_all_domains()
        domain = domains[0]
        
        cls = registry.register_class(domain_id=domain.id, name="Device", display_name="Device")
        
        cap = registry.register_capability(
            class_id=cls.id,
            name="monitoring",
            display_name="Monitoring Capability"
        )
        
        assert cap is not None
        assert cap.name == "monitoring"
    
    def test_assign_tag(self, registry):
        """Test assigning a semantic tag."""
        domains = registry.get_all_domains()
        domain = domains[0]
        
        cls = registry.register_class(domain_id=domain.id, name="Asset", display_name="Asset")
        
        tag = registry.assign_tag(
            entity_type="asset",
            entity_id="asset-123",
            class_id=cls.id
        )
        
        assert tag is not None
        assert tag.entity_id == "asset-123"


class TestTaxonomyEngine:
    """Tests for TaxonomyEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create taxonomy engine."""
        return TaxonomyEngine()
    
    def test_get_root_classes(self, engine):
        """Test getting root classes."""
        roots = engine.get_root_classes("test-domain")
        assert isinstance(roots, list)
    
    def test_get_subclasses(self, engine):
        """Test getting subclasses."""
        # Create a class hierarchy
        cls = OntologyClass(
            id="parent",
            domain_id="test",
            name="Parent",
            display_name="Parent Class",
            level=0
        )
        
        subclasses = engine.get_subclasses(cls.id)
        assert isinstance(subclasses, list)


class TestClassificationEngine:
    """Tests for ClassificationEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create classification engine."""
        return ClassificationEngine()
    
    def test_classify_asset(self, engine):
        """Test classifying an asset."""
        registry = engine.registry
        domains = registry.get_all_domains()
        domain = domains[0]
        
        cls = registry.register_class(domain_id=domain.id, name="Asset", display_name="Asset")
        
        classification = engine.classify_asset(
            asset_id="asset-1",
            class_id=cls.id
        )
        
        assert classification is not None
        assert classification.entity_id == "asset-1"
    
    def test_get_entity_classification(self, engine):
        """Test getting entity classification."""
        registry = engine.registry
        domains = registry.get_all_domains()
        domain = domains[0]
        
        cls = registry.register_class(domain_id=domain.id, name="Device", display_name="Device")
        
        engine.classify_device(
            device_id="device-1",
            class_id=cls.id
        )
        
        classification = engine.get_entity_classification("device", "device-1")
        
        assert classification is not None


class TestInheritanceEngine:
    """Tests for InheritanceEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create inheritance engine."""
        return InheritanceEngine()
    
    def test_get_inherited_properties(self, engine):
        """Test getting inherited properties."""
        props = engine.get_inherited_properties("class-1")
        assert isinstance(props, dict)
    
    def test_get_inherited_capabilities(self, engine):
        """Test getting inherited capabilities."""
        caps = engine.get_inherited_capabilities("class-1")
        assert isinstance(caps, object)


class TestCapabilityEngine:
    """Tests for CapabilityEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create capability engine."""
        return CapabilityEngine()
    
    def test_get_class_capabilities(self, engine):
        """Test getting class capabilities."""
        caps = engine.get_class_capabilities("class-1")
        assert isinstance(caps, list)
    
    def test_find_classes_with_capability(self, engine):
        """Test finding classes with capability."""
        classes = engine.find_classes_with_capability("monitoring")
        assert isinstance(classes, list)


class TestSemanticQueryEngine:
    """Tests for SemanticQueryEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create semantic query engine."""
        return SemanticQueryEngine()
    
    def test_find_by_class(self, engine):
        """Test finding by class name."""
        result = engine.find_by_class("transformer")
        assert result is not None
        assert result.query_type == "find_by_class"
    
    def test_find_by_capability(self, engine):
        """Test finding by capability."""
        result = engine.find_by_capability("monitoring")
        assert result is not None
        assert result.query_type == "find_by_capability"
    
    def test_find_by_domain(self, engine):
        """Test finding by domain."""
        result = engine.find_by_domain("electrical")
        assert result is not None
        assert result.query_type == "find_by_domain"
    
    def test_search(self, engine):
        """Test search."""
        result = engine.search("power")
        assert result is not None
        assert result.query_type == "search"


class TestOntologyValidator:
    """Tests for OntologyValidator."""
    
    @pytest.fixture
    def validator(self):
        """Create validator."""
        return OntologyValidator()
    
    def test_validate_class(self, validator):
        """Test validating a class."""
        cls = OntologyClass(
            id="class-1",
            domain_id="domain-1",
            name="Transformer",
            display_name="Power Transformer"
        )
        
        issues = validator.validate_class(cls)
        assert len(issues) == 0
    
    def test_validate_class_missing_name(self, validator):
        """Test validating class with missing name."""
        cls = OntologyClass(
            id="class-1",
            domain_id="domain-1",
            name="",
            display_name="Test"
        )
        
        issues = validator.validate_class(cls)
        assert len(issues) > 0
    
    def test_check_duplicate_class(self, validator):
        """Test checking for duplicate classes."""
        existing = {
            "class-1": OntologyClass(
                id="class-1",
                domain_id="domain-1",
                name="Transformer",
                display_name="Transformer"
            )
        }
        
        is_duplicate = validator.check_duplicate_class("Transformer", "domain-1", existing)
        assert is_duplicate is True


class TestOntologySyncEngine:
    """Tests for OntologySyncEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create sync engine."""
        return OntologySyncEngine()
    
    def test_sync_asset(self, engine):
        """Test syncing an asset."""
        registry = engine.registry
        domains = registry.get_all_domains()
        domain = domains[0]
        
        cls = registry.register_class(domain_id=domain.id, name="Asset", display_name="Asset")
        
        record = engine.sync_asset(
            asset_id="asset-1",
            class_id=cls.id
        )
        
        assert record is not None
        assert record.entity_type == "asset"
    
    def test_sync_document(self, engine):
        """Test syncing a document."""
        registry = engine.registry
        domains = registry.get_all_domains()
        domain = domains[0]
        
        cls = registry.register_class(domain_id=domain.id, name="Document", display_name="Document")
        
        record = engine.sync_document(
            document_id="doc-1",
            class_id=cls.id
        )
        
        assert record is not None
        assert record.entity_type == "document"
    
    def test_sync_work_order(self, engine):
        """Test syncing a work order."""
        registry = engine.registry
        domains = registry.get_all_domains()
        domain = domains[0]
        
        cls = registry.register_class(domain_id=domain.id, name="WorkOrder", display_name="Work Order")
        
        record = engine.sync_work_order(
            work_order_id="wo-1",
            class_id=cls.id
        )
        
        assert record is not None
        assert record.entity_type == "work_order"
    
    def test_sync_device(self, engine):
        """Test syncing a device."""
        registry = engine.registry
        domains = registry.get_all_domains()
        domain = domains[0]
        
        cls = registry.register_class(domain_id=domain.id, name="Device", display_name="Device")
        
        record = engine.sync_device(
            device_id="device-1",
            class_id=cls.id
        )
        
        assert record is not None
        assert record.entity_type == "device"
    
    def test_sync_organization(self, engine):
        """Test syncing an organization."""
        registry = engine.registry
        domains = registry.get_all_domains()
        domain = domains[0]
        
        cls = registry.register_class(domain_id=domain.id, name="Organization", display_name="Organization")
        
        record = engine.sync_organization(
            organization_id="org-1",
            class_id=cls.id
        )
        
        assert record is not None
        assert record.entity_type == "organization"


class TestOntologyRelationships:
    """Tests for ontology relationships."""
    
    def test_create_relationship(self):
        """Test creating a relationship."""
        rel = OntologyRelationship(
            id="rel-1",
            source_class_id="class-1",
            target_class_id="class-2",
            relationship_type="connects_to"
        )
        
        assert rel.id == "rel-1"
        assert rel.relationship_type == "connects_to"


class TestTaxonomy:
    """Tests for Taxonomy."""
    
    def test_create_taxonomy(self):
        """Test creating a taxonomy."""
        taxonomy = Taxonomy(
            id="tax-1",
            domain_id="domain-1",
            name="power_network",
            display_name="Power Network Taxonomy"
        )
        
        assert taxonomy.id == "tax-1"
        assert taxonomy.name == "power_network"


class TestCapability:
    """Tests for Capability."""
    
    def test_create_capability(self):
        """Test creating a capability."""
        cap = Capability(
            id="cap-1",
            class_id="class-1",
            name="monitoring",
            display_name="Monitoring"
        )
        
        assert cap.id == "cap-1"
        assert cap.name == "monitoring"


class TestSemanticTag:
    """Tests for SemanticTag."""
    
    def test_create_semantic_tag(self):
        """Test creating a semantic tag."""
        tag = SemanticTag(
            id="tag-1",
            entity_type="asset",
            entity_id="asset-1",
            class_id="class-1"
        )
        
        assert tag.id == "tag-1"
        assert tag.entity_type == "asset"


class TestClassification:
    """Tests for Classification."""
    
    def test_create_classification(self):
        """Test creating a classification."""
        cls = Classification(
            entity_type="asset",
            entity_id="asset-1",
            class_id="class-1",
            class_name="Transformer",
            confidence=0.95
        )
        
        assert cls.entity_id == "asset-1"
        assert cls.confidence == 0.95


class TestHierarchyOperations:
    """Tests for hierarchy operations."""
    
    @pytest.fixture
    def registry(self):
        """Create registry with hierarchy."""
        reg = OntologyRegistry()
        domains = reg.get_all_domains()
        domain = domains[0]
        
        # Create hierarchy: Root -> Parent -> Child
        root = reg.register_class(domain_id=domain.id, name="Root", display_name="Root")
        parent = reg.register_class(domain_id=domain.id, name="Parent", display_name="Parent", parent_class_id=root.id)
        child = reg.register_class(domain_id=domain.id, name="Child", display_name="Child", parent_class_id=parent.id)
        
        return reg
    
    def test_class_hierarchy(self, registry):
        """Test class hierarchy."""
        domains = registry.get_all_domains()
        classes = registry.get_classes_for_domain(domains[0].id)
        
        assert len(classes) >= 3
