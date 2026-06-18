"""
Tests for Semantic Layer

Tests entity creation, tag creation, relationships, search,
context aggregation, and duplicate prevention.
"""

import pytest
from src.models.semantic_entity import SemanticEntity, EntityType
from src.models.semantic_tag import SemanticTag
from src.models.semantic_relationship import SemanticRelationship, RelationshipType
from src.services.semantic_service import SemanticService
from src.schemas.semantic import (
    SemanticEntityCreate,
    SemanticTagCreate,
    SemanticRelationshipCreate,
    SemanticSearchQuery
)


class TestSemanticEntity:
    """Tests for semantic entity operations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = SemanticService()
    
    def test_create_entity(self):
        """Test creating a semantic entity."""
        data = SemanticEntityCreate(
            entity_type="asset",
            entity_id="asset-001",
            name="Test Substation",
            description="A test substation",
            category="power",
            ontology_class="power_grid.substation"
        )
        
        entity = self.service.create_entity(data)
        
        assert entity is not None
        assert entity.entity_type == EntityType.ASSET
        assert entity.entity_id == "asset-001"
        assert entity.name == "Test Substation"
        assert entity.description == "A test substation"
        assert entity.category == "power"
        assert entity.ontology_class == "power_grid.substation"
    
    def test_create_entity_all_types(self):
        """Test creating entities of all types."""
        types = [
            "asset", "sensor", "measurement", "event",
            "health", "relationship", "scenario", "recovery",
            "timeline", "work_order", "document"
        ]
        
        for entity_type in types:
            data = SemanticEntityCreate(
                entity_type=entity_type,
                entity_id=f"{entity_type}-001",
                name=f"Test {entity_type}",
                category="test"
            )
            entity = self.service.create_entity(data)
            assert entity is not None
            assert entity.entity_type.value == entity_type
    
    def test_get_entity(self):
        """Test getting an entity by ID."""
        data = SemanticEntityCreate(
            entity_type="asset",
            entity_id="asset-002",
            name="Test Asset",
            category="test"
        )
        
        created = self.service.create_entity(data)
        retrieved = self.service.get_entity(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Test Asset"
    
    def test_get_nonexistent_entity(self):
        """Test getting a non-existent entity."""
        result = self.service.get_entity("nonexistent-id")
        assert result is None
    
    def test_update_entity(self):
        """Test updating an entity."""
        from src.schemas.semantic import SemanticEntityUpdate
        
        data = SemanticEntityCreate(
            entity_type="asset",
            entity_id="asset-003",
            name="Original Name",
            category="original"
        )
        
        entity = self.service.create_entity(data)
        
        update_data = SemanticEntityUpdate(
            name="Updated Name",
            description="New description",
            category="updated"
        )
        
        updated = self.service.update_entity(entity.id, update_data)
        
        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.description == "New description"
        assert updated.category == "updated"
    
    def test_delete_entity(self):
        """Test deleting an entity."""
        data = SemanticEntityCreate(
            entity_type="asset",
            entity_id="asset-004",
            name="To Delete",
            category="test"
        )
        
        entity = self.service.create_entity(data)
        result = self.service.delete_entity(entity.id)
        
        assert result is True
        assert self.service.get_entity(entity.id) is None
    
    def test_duplicate_prevention_entity(self):
        """Test that duplicate entities are not created."""
        data = SemanticEntityCreate(
            entity_type="asset",
            entity_id="duplicate-test",
            name="First",
            category="test"
        )
        
        first = self.service.create_entity(data)
        second = self.service.create_entity(data)
        
        # Should return the same entity
        assert first.id == second.id
        assert self.service.list_entities() == [first]


class TestSemanticTag:
    """Tests for semantic tag operations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = SemanticService()
    
    def test_create_tag(self):
        """Test creating a semantic tag."""
        # Create entity first
        entity_data = SemanticEntityCreate(
            entity_type="asset",
            entity_id="asset-tag-test",
            name="Test Asset",
            category="test"
        )
        entity = self.service.create_entity(entity_data)
        
        # Create tag
        tag_data = SemanticTagCreate(
            entity_id=entity.id,
            tag_name="voltage",
            tag_value="400V"
        )
        
        tag = self.service.create_tag(tag_data)
        
        assert tag is not None
        assert tag.tag_name == "voltage"
        assert tag.tag_value == "400V"
        assert tag.entity_id == entity.id
    
    def test_get_tags(self):
        """Test getting tags for an entity."""
        entity_data = SemanticEntityCreate(
            entity_type="sensor",
            entity_id="sensor-tag-test",
            name="Test Sensor",
            category="test"
        )
        entity = self.service.create_entity(entity_data)
        
        # Create multiple tags
        self.service.create_tag(SemanticTagCreate(entity_id=entity.id, tag_name="temperature", tag_value="25C"))
        self.service.create_tag(SemanticTagCreate(entity_id=entity.id, tag_name="humidity", tag_value="60%"))
        self.service.create_tag(SemanticTagCreate(entity_id=entity.id, tag_name="location", tag_value="Building A"))
        
        tags = self.service.get_tags(entity.id)
        
        assert len(tags) == 3
        tag_names = [t.tag_name for t in tags]
        assert "temperature" in tag_names
        assert "humidity" in tag_names
        assert "location" in tag_names
    
    def test_duplicate_prevention_tag(self):
        """Test that duplicate tags on same entity are not created."""
        entity_data = SemanticEntityCreate(
            entity_type="asset",
            entity_id="asset-dup-tag",
            name="Test Asset",
            category="test"
        )
        entity = self.service.create_entity(entity_data)
        
        tag_data = SemanticTagCreate(
            entity_id=entity.id,
            tag_name="voltage",
            tag_value="400V"
        )
        
        first = self.service.create_tag(tag_data)
        second = self.service.create_tag(tag_data)
        
        # Should return the same tag
        assert first.id == second.id
        assert len(self.service.get_tags(entity.id)) == 1


class TestSemanticRelationship:
    """Tests for semantic relationship operations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = SemanticService()
    
    def test_create_relationship(self):
        """Test creating a semantic relationship."""
        # Create two entities
        entity1 = self.service.create_entity(SemanticEntityCreate(
            entity_type="asset",
            entity_id="asset-rel-1",
            name="Asset 1",
            category="test"
        ))
        entity2 = self.service.create_entity(SemanticEntityCreate(
            entity_type="sensor",
            entity_id="sensor-rel-1",
            name="Sensor 1",
            category="test"
        ))
        
        # Create relationship
        rel_data = SemanticRelationshipCreate(
            source_entity_id=entity1.id,
            target_entity_id=entity2.id,
            relationship_type="observed_by"
        )
        
        relationship = self.service.create_relationship(rel_data)
        
        assert relationship is not None
        assert relationship.source_entity_id == entity1.id
        assert relationship.target_entity_id == entity2.id
        assert relationship.relationship_type == RelationshipType.OBSERVED_BY
    
    def test_get_relationships(self):
        """Test getting relationships for an entity."""
        entity1 = self.service.create_entity(SemanticEntityCreate(
            entity_type="asset",
            entity_id="asset-rels",
            name="Asset 1",
            category="test"
        ))
        entity2 = self.service.create_entity(SemanticEntityCreate(
            entity_type="sensor",
            entity_id="sensor-rels-1",
            name="Sensor 1",
            category="test"
        ))
        entity3 = self.service.create_entity(SemanticEntityCreate(
            entity_type="event",
            entity_id="event-rels-1",
            name="Event 1",
            category="test"
        ))
        
        self.service.create_relationship(SemanticRelationshipCreate(
            source_entity_id=entity1.id,
            target_entity_id=entity2.id,
            relationship_type="observed_by"
        ))
        self.service.create_relationship(SemanticRelationshipCreate(
            source_entity_id=entity1.id,
            target_entity_id=entity3.id,
            relationship_type="caused_by"
        ))
        
        rels = self.service.get_relationships(entity1.id)
        
        assert len(rels) == 2


class TestSemanticSearch:
    """Tests for semantic search operations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = SemanticService()
        
        # Create test entities
        self.asset1 = self.service.create_entity(SemanticEntityCreate(
            entity_type="asset",
            entity_id="search-asset-1",
            name="Power Substation Alpha",
            description="Main power substation",
            category="power",
            ontology_class="power_grid.substation"
        ))
        
        self.asset2 = self.service.create_entity(SemanticEntityCreate(
            entity_type="asset",
            entity_id="search-asset-2",
            name="Water Treatment Plant Beta",
            description="Water treatment facility",
            category="water",
            ontology_class="water.treatment_plant"
        ))
        
        self.sensor1 = self.service.create_entity(SemanticEntityCreate(
            entity_type="sensor",
            entity_id="search-sensor-1",
            name="Voltage Sensor A",
            category="power",
            ontology_class="sensor.voltage"
        ))
        
        # Add tags
        self.service.create_tag(SemanticTagCreate(entity_id=self.asset1.id, tag_name="voltage", tag_value="400V"))
        self.service.create_tag(SemanticTagCreate(entity_id=self.asset1.id, tag_name="location", tag_value="downtown"))
        self.service.create_tag(SemanticTagCreate(entity_id=self.sensor1.id, tag_name="criticality", tag_value="high"))
    
    def test_search_by_type(self):
        """Test searching by entity type."""
        query = SemanticSearchQuery(entity_type="asset")
        results = self.service.search(query)
        
        assert len(results) == 2
    
    def test_search_by_category(self):
        """Test searching by category."""
        query = SemanticSearchQuery(category="power")
        results = self.service.search(query)
        
        assert len(results) == 2
    
    def test_search_by_ontology_class(self):
        """Test searching by ontology class."""
        query = SemanticSearchQuery(ontology_class="power_grid.substation")
        results = self.service.search(query)
        
        assert len(results) == 1
        assert results[0].name == "Power Substation Alpha"
    
    def test_search_by_tag_name(self):
        """Test searching by tag name."""
        query = SemanticSearchQuery(tag_name="voltage")
        results = self.service.search(query)
        
        assert len(results) == 1
        assert results[0].name == "Power Substation Alpha"
    
    def test_search_by_query_text(self):
        """Test searching by text query."""
        query = SemanticSearchQuery(query="power")
        results = self.service.search(query)
        
        # Should match "Power Substation" and "Water Treatment Plant" (no "power")
        assert len(results) == 1
        assert results[0].name == "Power Substation Alpha"
    
    def test_search_combined_filters(self):
        """Test search with combined filters."""
        query = SemanticSearchQuery(entity_type="asset", category="power")
        results = self.service.search(query)
        
        assert len(results) == 1


class TestSemanticContext:
    """Tests for semantic context aggregation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = SemanticService()
        
        # Create entity hierarchy
        self.asset = self.service.create_entity(SemanticEntityCreate(
            entity_type="asset",
            entity_id="context-asset",
            name="Test Substation",
            category="power",
            ontology_class="power_grid.substation"
        ))
        
        self.sensor = self.service.create_entity(SemanticEntityCreate(
            entity_type="sensor",
            entity_id="context-sensor",
            name="Voltage Sensor",
            category="power",
            ontology_class="sensor.voltage"
        ))
        
        self.event = self.service.create_entity(SemanticEntityCreate(
            entity_type="event",
            entity_id="context-event",
            name="Voltage Spike Event",
            category="alert",
            ontology_class="event.voltage_spike"
        ))
        
        self.health = self.service.create_entity(SemanticEntityCreate(
            entity_type="health",
            entity_id="context-health",
            name="Health Record",
            category="status",
            ontology_class="health.record"
        ))
        
        # Create relationships
        self.service.create_relationship(SemanticRelationshipCreate(
            source_entity_id=self.asset.id,
            target_entity_id=self.sensor.id,
            relationship_type="observed_by"
        ))
        self.service.create_relationship(SemanticRelationshipCreate(
            source_entity_id=self.asset.id,
            target_entity_id=self.event.id,
            relationship_type="caused_by"
        ))
        self.service.create_relationship(SemanticRelationshipCreate(
            source_entity_id=self.asset.id,
            target_entity_id=self.health.id,
            relationship_type="related_to"
        ))
    
    def test_build_context(self):
        """Test building semantic context."""
        context = self.service.build_context("asset", "context-asset")
        
        assert context is not None
        assert context.entity is not None
        assert context.entity["name"] == "Test Substation"
        
        # Check related entities
        assert context.sensors.count == 1
        assert context.events.count == 1
        assert context.health.count == 1
        
        # Check relationships
        assert len(context.relationships) == 3


class TestSemanticGraph:
    """Tests for semantic graph building."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = SemanticService()
    
    def test_build_graph(self):
        """Test building semantic graph."""
        # Create entities
        node1 = self.service.create_entity(SemanticEntityCreate(
            entity_type="asset",
            entity_id="graph-node-1",
            name="Node 1",
            category="test"
        ))
        node2 = self.service.create_entity(SemanticEntityCreate(
            entity_type="sensor",
            entity_id="graph-node-2",
            name="Node 2",
            category="test"
        ))
        
        # Create relationship
        self.service.create_relationship(SemanticRelationshipCreate(
            source_entity_id=node1.id,
            target_entity_id=node2.id,
            relationship_type="observed_by"
        ))
        
        graph = self.service.build_graph()
        
        assert graph.total_nodes == 2
        assert graph.total_edges == 1
        assert len(graph.nodes) == 2
        assert len(graph.edges) == 1
