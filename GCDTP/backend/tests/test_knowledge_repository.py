"""
Tests for Knowledge Repository Engine

Tests document CRUD, search, relationships, 
graph creation, and category summary.
"""

import pytest
from datetime import datetime
from src.models.knowledge_document import KnowledgeDocument, DocumentType
from src.models.knowledge_reference import KnowledgeReference, RelationshipType
from src.services.knowledge_service import KnowledgeService
from src.schemas.knowledge import KnowledgeDocumentCreate, KnowledgeSearchQuery


class TestKnowledgeDocument:
    """Tests for knowledge document operations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = KnowledgeService()
    
    def test_create_document(self):
        """Test creating a knowledge document."""
        data = KnowledgeDocumentCreate(
            title="Test Manual",
            document_type="manual",
            category="infrastructure",
            author="Test Author",
            summary="A test manual",
            tags=["test", "manual"],
            source="Test Source"
        )
        
        doc = self.service.create_document(data)
        
        assert doc is not None
        assert doc.title == "Test Manual"
        assert doc.document_type == DocumentType.MANUAL
        assert doc.category == "infrastructure"
        assert doc.author == "Test Author"
        assert "test" in doc.tags
    
    def test_create_all_document_types(self):
        """Test creating documents of all types."""
        types = [
            "manual", "sop", "troubleshooting", "adr",
            "report", "lesson_learned", "reference", "external"
        ]
        
        for doc_type in types:
            data = KnowledgeDocumentCreate(
                title=f"Test {doc_type}",
                document_type=doc_type,
                category="general",
                author="Test"
            )
            doc = self.service.create_document(data)
            assert doc is not None
            assert doc.document_type.value == doc_type
    
    def test_get_document(self):
        """Test getting a document by ID."""
        data = KnowledgeDocumentCreate(
            title="Test Doc",
            document_type="manual",
            category="test",
            author="Test"
        )
        
        created = self.service.create_document(data)
        retrieved = self.service.get_document(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.title == "Test Doc"
    
    def test_list_documents(self):
        """Test listing documents."""
        for i in range(5):
            self.service.create_document(KnowledgeDocumentCreate(
                title=f"Doc {i}",
                document_type="manual",
                category="test",
                author="Test"
            ))
        
        docs = self.service.list_documents()
        assert len(docs) == 5
    
    def test_delete_document(self):
        """Test deleting a document."""
        data = KnowledgeDocumentCreate(
            title="To Delete",
            document_type="manual",
            category="test",
            author="Test"
        )
        
        doc = self.service.create_document(data)
        result = self.service.delete_document(doc.id)
        
        assert result is True
        assert self.service.get_document(doc.id) is None


class TestKnowledgeSearch:
    """Tests for knowledge search."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = KnowledgeService()
        
        # Create test documents
        self.service.create_document(KnowledgeDocumentCreate(
            title="Power Grid Manual",
            document_type="manual",
            category="infrastructure",
            author="Engineer A",
            summary="Manual for power grid operations",
            tags=["power", "grid"]
        ))
        
        self.service.create_document(KnowledgeDocumentCreate(
            title="Safety SOP",
            document_type="sop",
            category="safety",
            author="Safety Team",
            summary="Safety operating procedures",
            tags=["safety", "operations"]
        ))
    
    def test_search_by_title(self):
        """Test searching by title."""
        query = KnowledgeSearchQuery(query="power")
        results = self.service.search_documents(query)
        
        assert len(results) >= 1
        assert any("power" in d.title.lower() for d in results)
    
    def test_search_by_category(self):
        """Test filtering by category."""
        query = KnowledgeSearchQuery(category="infrastructure")
        results = self.service.search_documents(query)
        
        assert all(d.category == "infrastructure" for d in results)
    
    def test_search_by_type(self):
        """Test filtering by type."""
        query = KnowledgeSearchQuery(document_type="manual")
        results = self.service.search_documents(query)
        
        assert all(d.document_type == DocumentType.MANUAL for d in results)
    
    def test_search_by_tags(self):
        """Test filtering by tags."""
        query = KnowledgeSearchQuery(tags=["power"])
        results = self.service.search_documents(query)
        
        assert all("power" in d.tags for d in results)


class TestKnowledgeRelationships:
    """Tests for knowledge relationships."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = KnowledgeService()
        
        # Create test documents
        self.doc1 = self.service.create_document(KnowledgeDocumentCreate(
            title="Base Manual",
            document_type="manual",
            category="test",
            author="Test"
        ))
        
        self.doc2 = self.service.create_document(KnowledgeDocumentCreate(
            title="Extended Manual",
            document_type="manual",
            category="test",
            author="Test"
        ))
    
    def test_create_reference(self):
        """Test creating a reference."""
        ref = self.service.create_reference(
            source_id=self.doc1.id,
            target_id=self.doc2.id,
            relationship_type="extends"
        )
        
        assert ref is not None
        assert ref.source_document_id == self.doc1.id
        assert ref.target_document_id == self.doc2.id
        assert ref.relationship_type == RelationshipType.EXTENDS
    
    def test_get_references(self):
        """Test getting references for a document."""
        self.service.create_reference(
            source_id=self.doc1.id,
            target_id=self.doc2.id,
            relationship_type="related_to"
        )
        
        refs = self.service.get_references(self.doc1.id)
        assert len(refs) >= 1
    
    def test_reference_same_document_fails(self):
        """Test that self-referencing is not allowed."""
        ref = self.service.create_reference(
            source_id=self.doc1.id,
            target_id=self.doc1.id,
            relationship_type="related_to"
        )
        
        assert ref is None


class TestKnowledgeGraph:
    """Tests for knowledge graph."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = KnowledgeService()
        
        # Create test documents
        for i in range(3):
            self.service.create_document(KnowledgeDocumentCreate(
                title=f"Doc {i}",
                document_type="manual",
                category="test",
                author="Test",
                tags=[f"tag{i}"]
            ))
        
        docs = self.service.list_documents()
        if len(docs) >= 2:
            self.service.create_reference(
                source_id=docs[0].id,
                target_id=docs[1].id,
                relationship_type="references"
            )
    
    def test_build_graph(self):
        """Test building knowledge graph."""
        graph = self.service.build_knowledge_graph()
        
        assert "nodes" in graph
        assert "edges" in graph
        assert graph["total_nodes"] >= 1
    
    def test_graph_structure(self):
        """Test graph has correct structure."""
        graph = self.service.build_knowledge_graph()
        
        assert all("id" in n for n in graph["nodes"])
        assert all("title" in n for n in graph["nodes"])
        assert all("source" in e for e in graph["edges"])


class TestKnowledgeCategorySummary:
    """Tests for category summary."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = KnowledgeService()
        
        # Create documents in different categories
        self.service.create_document(KnowledgeDocumentCreate(
            title="Infra Doc 1",
            document_type="manual",
            category="infrastructure",
            author="Test"
        ))
        
        self.service.create_document(KnowledgeDocumentCreate(
            title="Infra Doc 2",
            document_type="sop",
            category="infrastructure",
            author="Test"
        ))
        
        self.service.create_document(KnowledgeDocumentCreate(
            title="Safety Doc",
            document_type="sop",
            category="safety",
            author="Test"
        ))
    
    def test_category_summary(self):
        """Test getting category summary."""
        summary = self.service.get_category_summary()
        
        assert len(summary) >= 2
        
        infra_summary = next(
            (s for s in summary if s["category"] == "infrastructure"),
            None
        )
        assert infra_summary is not None
        assert infra_summary["document_count"] >= 2


class TestKnowledgeRelated:
    """Tests for related documents."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = KnowledgeService()
        
        # Create test documents
        self.doc1 = self.service.create_document(KnowledgeDocumentCreate(
            title="Main Document",
            document_type="manual",
            category="test",
            author="Test"
        ))
        
        self.doc2 = self.service.create_document(KnowledgeDocumentCreate(
            title="Related Document 1",
            document_type="sop",
            category="test",
            author="Test"
        ))
        
        self.doc3 = self.service.create_document(KnowledgeDocumentCreate(
            title="Related Document 2",
            document_type="reference",
            category="test",
            author="Test"
        ))
        
        # Create references
        self.service.create_reference(
            source_id=self.doc1.id,
            target_id=self.doc2.id,
            relationship_type="references"
        )
        
        self.service.create_reference(
            source_id=self.doc1.id,
            target_id=self.doc3.id,
            relationship_type="related_to"
        )
    
    def test_get_related_documents(self):
        """Test getting related documents."""
        related = self.service.get_related_documents(self.doc1.id)
        
        assert len(related) >= 2
        
        titles = [r["title"] for r in related]
        assert "Related Document 1" in titles
        assert "Related Document 2" in titles
