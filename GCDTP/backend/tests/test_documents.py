"""
Tests for Document Management Engine

Tests document creation, versioning, asset/work order linkage,
search, indexing, tagging, validation, and timeline events.
"""

import pytest
from datetime import datetime, timedelta
from backend.src.services.documents import (
    DocumentEngine,
    DocumentIndexer,
    AttachmentManager,
    DocumentValidator,
    Document,
    DocumentVersion,
    DocumentTag,
    DocumentType,
    DocumentStatus,
    DocumentFilter,
    Attachment,
)


class TestDocumentTypes:
    """Tests for document types."""
    
    def test_create_document(self):
        """Test creating a document."""
        doc = Document(
            id="doc-1",
            title="Test Document",
            document_type=DocumentType.PDF,
            description="Test description"
        )
        
        assert doc.id == "doc-1"
        assert doc.title == "Test Document"
        assert doc.document_type == DocumentType.PDF
    
    def test_document_state_active(self):
        """Test document state when active."""
        doc = Document(
            id="doc-1",
            title="Test",
            document_type=DocumentType.PDF,
            status=DocumentStatus.ACTIVE
        )
        
        assert doc.is_active is True
        assert doc.document_state.value == "active"
    
    def test_document_state_archived(self):
        """Test document state when archived."""
        doc = Document(
            id="doc-1",
            title="Test",
            document_type=DocumentType.PDF,
            status=DocumentStatus.ARCHIVED,
            archived_at=datetime.utcnow()
        )
        
        assert doc.is_archived is True
        assert doc.document_state.value == "archived"
    
    def test_document_state_deleted(self):
        """Test document state when deleted."""
        doc = Document(
            id="doc-1",
            title="Test",
            document_type=DocumentType.PDF,
            status=DocumentStatus.DELETED,
            deleted_at=datetime.utcnow()
        )
        
        assert doc.is_deleted is True
        assert doc.document_state.value == "deleted"
    
    def test_document_to_dict(self):
        """Test document serialization."""
        doc = Document(
            id="doc-1",
            title="Test",
            document_type=DocumentType.PDF
        )
        
        data = doc.to_dict()
        assert data["id"] == "doc-1"
        assert data["document_type"] == "pdf"


class TestDocumentEngine:
    """Tests for document engine."""
    
    @pytest.fixture
    def engine(self):
        """Create document engine."""
        return DocumentEngine()
    
    def test_create_document(self, engine):
        """Test creating a document."""
        doc = engine.create_document(
            title="Test Document",
            document_type=DocumentType.PDF,
            asset_id="asset-1"
        )
        
        assert doc is not None
        assert doc.id is not None
        assert doc.title == "Test Document"
        assert doc.asset_id == "asset-1"
    
    def test_create_document_with_work_order(self, engine):
        """Test creating document linked to work order."""
        doc = engine.create_document(
            title="Maintenance Report",
            document_type=DocumentType.MAINTENANCE_REPORT,
            work_order_id="wo-1"
        )
        
        assert doc.work_order_id == "wo-1"
    
    def test_update_document(self, engine):
        """Test updating a document."""
        doc = engine.create_document(
            title="Original Title",
            document_type=DocumentType.PDF
        )
        
        updated = engine.update_document(doc, title="New Title")
        
        assert updated.title == "New Title"
    
    def test_create_new_version(self, engine):
        """Test creating a new version."""
        doc = engine.create_document(
            title="Test",
            document_type=DocumentType.PDF,
            version=1
        )
        
        version = engine.create_new_version(
            doc,
            change_notes="Updated content",
            created_by="user1"
        )
        
        assert version.version_number == 2
        assert version.change_notes == "Updated content"
        assert doc.version == 2
    
    def test_archive_document(self, engine):
        """Test archiving a document."""
        doc = engine.create_document(
            title="Test",
            document_type=DocumentType.PDF
        )
        
        archived = engine.archive_document(doc)
        
        assert archived.status == DocumentStatus.ARCHIVED
        assert archived.archived_at is not None
    
    def test_restore_document(self, engine):
        """Test restoring an archived document."""
        doc = engine.create_document(
            title="Test",
            document_type=DocumentType.PDF
        )
        engine.archive_document(doc)
        
        restored = engine.restore_document(doc)
        
        assert restored.status == DocumentStatus.ACTIVE
        assert restored.archived_at is None
    
    def test_delete_document_soft(self, engine):
        """Test soft deleting a document."""
        doc = engine.create_document(
            title="Test",
            document_type=DocumentType.PDF
        )
        
        deleted = engine.delete_document(doc, hard=False)
        
        assert deleted.status == DocumentStatus.DELETED
        assert deleted.deleted_at is not None
    
    def test_delete_document_hard(self, engine):
        """Test hard deleting a document."""
        doc = engine.create_document(
            title="Test",
            document_type=DocumentType.PDF
        )
        
        engine.delete_document(doc, hard=True)
        
        assert engine.get_document(doc.id) is None
    
    def test_restore_deleted_document(self, engine):
        """Test restoring a deleted document."""
        doc = engine.create_document(
            title="Test",
            document_type=DocumentType.PDF
        )
        engine.delete_document(doc, hard=False)
        
        restored = engine.restore_deleted_document(doc)
        
        assert restored.status == DocumentStatus.ACTIVE
    
    def test_get_documents_by_asset(self, engine):
        """Test getting documents by asset."""
        engine.create_document(title="Doc1", document_type=DocumentType.PDF, asset_id="a1")
        engine.create_document(title="Doc2", document_type=DocumentType.PDF, asset_id="a1")
        engine.create_document(title="Doc3", document_type=DocumentType.PDF, asset_id="a2")
        
        docs = engine.get_documents_by_asset("a1")
        
        assert len(docs) == 2
    
    def test_get_documents_by_work_order(self, engine):
        """Test getting documents by work order."""
        engine.create_document(title="Doc1", document_type=DocumentType.PDF, work_order_id="wo-1")
        engine.create_document(title="Doc2", document_type=DocumentType.PDF, work_order_id="wo-1")
        
        docs = engine.get_documents_by_work_order("wo-1")
        
        assert len(docs) == 2
    
    def test_get_active_documents(self, engine):
        """Test getting active documents."""
        doc1 = engine.create_document(title="Doc1", document_type=DocumentType.PDF)
        doc2 = engine.create_document(title="Doc2", document_type=DocumentType.PDF)
        engine.archive_document(doc2)
        
        active = engine.get_active_documents()
        
        assert len(active) == 1
        assert active[0].title == "Doc1"
    
    def test_get_document_summary(self, engine):
        """Test getting document summary."""
        doc = engine.create_document(title="Test", document_type=DocumentType.PDF)
        engine.create_new_version(doc, change_notes="v2")
        
        summary = engine.get_document_summary(doc)
        
        assert summary.document.id == doc.id
        assert summary.version_count == 1


class TestDocumentIndexer:
    """Tests for document indexer."""
    
    @pytest.fixture
    def indexer(self):
        """Create document indexer."""
        return DocumentIndexer()
    
    @pytest.fixture
    def sample_doc(self):
        """Create sample document."""
        return Document(
            id="doc-1",
            title="Test Document",
            description="This is a test document",
            document_type=DocumentType.PDF,
            asset_id="asset-1"
        )
    
    def test_index_document(self, indexer, sample_doc):
        """Test indexing a document."""
        indexer.index_document(sample_doc)
        
        assert indexer.get_document_count() == 1
    
    def test_search_by_text(self, indexer, sample_doc):
        """Test text search."""
        indexer.index_document(sample_doc)
        
        results = indexer.search_by_text("test")
        
        assert len(results) >= 1
    
    def test_search_by_tag(self, indexer, sample_doc):
        """Test tag search."""
        indexer.index_document(sample_doc, tags=["important", "review"])
        
        results = indexer.search_by_tag("important")
        
        assert len(results) >= 1
    
    def test_search_by_asset(self, indexer):
        """Test asset search."""
        doc = Document(
            id="doc-1",
            title="Asset Doc",
            document_type=DocumentType.PDF,
            asset_id="asset-1"
        )
        indexer.index_document(doc)
        
        results = indexer.search_by_asset("asset-1")
        
        assert len(results) == 1
    
    def test_search_by_type(self, indexer):
        """Test type search."""
        doc = Document(
            id="doc-1",
            title="PDF Doc",
            document_type=DocumentType.PDF
        )
        indexer.index_document(doc)
        
        results = indexer.search_by_type(DocumentType.PDF)
        
        assert len(results) == 1
    
    def test_get_all_tags(self, indexer):
        """Test getting all tags."""
        doc1 = Document(id="d1", title="D1", document_type=DocumentType.PDF)
        doc2 = Document(id="d2", title="D2", document_type=DocumentType.PDF)
        
        indexer.index_document(doc1, tags=["tag1", "tag2"])
        indexer.index_document(doc2, tags=["tag2", "tag3"])
        
        tags = indexer.get_all_tags()
        
        assert "tag1" in tags
        assert "tag2" in tags
        assert "tag3" in tags
    
    def test_get_tag_counts(self, indexer):
        """Test getting tag counts."""
        doc1 = Document(id="d1", title="D1", document_type=DocumentType.PDF)
        doc2 = Document(id="d2", title="D2", document_type=DocumentType.PDF)
        
        indexer.index_document(doc1, tags=["test"])
        indexer.index_document(doc2, tags=["test"])
        
        counts = indexer.get_tag_counts()
        
        assert counts.get("test") == 2
    
    def test_remove_document(self, indexer, sample_doc):
        """Test removing document from index."""
        indexer.index_document(sample_doc)
        assert indexer.get_document_count() == 1
        
        indexer.remove_document(sample_doc.id)
        
        assert indexer.get_document_count() == 0
    
    def test_update_document(self, indexer, sample_doc):
        """Test updating document in index."""
        indexer.index_document(sample_doc)
        
        sample_doc.title = "Updated Title"
        indexer.update_document(sample_doc)
        
        results = indexer.search_by_text("Updated")
        assert len(results) >= 1
    
    def test_clear_index(self, indexer):
        """Test clearing the index."""
        doc1 = Document(id="d1", title="D1", document_type=DocumentType.PDF)
        doc2 = Document(id="d2", title="D2", document_type=DocumentType.PDF)
        
        indexer.index_document(doc1)
        indexer.index_document(doc2)
        
        indexer.clear()
        
        assert indexer.get_document_count() == 0
    
    def test_filter_by_status(self, indexer):
        """Test filtering by status."""
        doc1 = Document(
            id="d1", title="D1", document_type=DocumentType.PDF,
            status=DocumentStatus.ACTIVE
        )
        doc2 = Document(
            id="d2", title="D2", document_type=DocumentType.PDF,
            status=DocumentStatus.ARCHIVED
        )
        
        indexer.index_document(doc1)
        indexer.index_document(doc2)
        
        filter_obj = DocumentFilter(statuses=[DocumentStatus.ACTIVE])
        results = indexer.search(filter_obj)
        
        assert len(results) == 1


class TestAttachmentManager:
    """Tests for attachment manager."""
    
    @pytest.fixture
    def manager(self):
        """Create attachment manager."""
        return AttachmentManager()
    
    def test_add_attachment(self, manager):
        """Test adding an attachment."""
        att = manager.add_attachment(
            document_id="doc-1",
            file_name="test.pdf",
            mime_type="application/pdf",
            file_size=1024
        )
        
        assert att is not None
        assert att.file_name == "test.pdf"
    
    def test_get_attachments(self, manager):
        """Test getting attachments."""
        manager.add_attachment(document_id="doc-1", file_name="file1.pdf")
        manager.add_attachment(document_id="doc-1", file_name="file2.pdf")
        
        attachments = manager.get_attachments("doc-1")
        
        assert len(attachments) == 2
    
    def test_remove_attachment(self, manager):
        """Test removing an attachment."""
        att = manager.add_attachment(document_id="doc-1", file_name="test.pdf")
        
        result = manager.remove_attachment("doc-1", att.id)
        
        assert result is True
        assert len(manager.get_attachments("doc-1")) == 0
    
    def test_set_primary_attachment(self, manager):
        """Test setting primary attachment."""
        att1 = manager.add_attachment(document_id="doc-1", file_name="file1.pdf")
        att2 = manager.add_attachment(document_id="doc-1", file_name="file2.pdf", is_primary=True)
        
        manager.set_primary_attachment("doc-1", att1.id)
        
        primary = manager.get_primary_attachment("doc-1")
        
        assert primary.id == att1.id
        assert primary.is_primary is True
    
    def test_get_total_size(self, manager):
        """Test getting total size."""
        manager.add_attachment(document_id="doc-1", file_name="file1.pdf", file_size=1000)
        manager.add_attachment(document_id="doc-1", file_name="file2.pdf", file_size=2000)
        
        total = manager.get_total_size("doc-1")
        
        assert total == 3000
    
    def test_is_supported_type(self, manager):
        """Test checking supported type."""
        assert manager.is_supported_type("application/pdf") is True
        assert manager.is_supported_type("application/xyz") is False
    
    def test_format_file_size(self, manager):
        """Test formatting file size."""
        assert "1.0 KB" in manager.format_file_size(1024)
        assert "1.0 MB" in manager.format_file_size(1024 * 1024)


class TestDocumentValidator:
    """Tests for document validator."""
    
    @pytest.fixture
    def validator(self):
        """Create validator."""
        return DocumentValidator()
    
    def test_validate_valid_document(self, validator):
        """Test validating a valid document."""
        doc = Document(
            id="doc-1",
            title="Valid Document",
            document_type=DocumentType.PDF,
            file_size=1024
        )
        
        issues = validator.validate_document(doc)
        
        assert len(issues) == 0
    
    def test_validate_missing_title(self, validator):
        """Test validation with missing title."""
        doc = Document(
            id="doc-1",
            title="",
            document_type=DocumentType.PDF
        )
        
        issues = validator.validate_document(doc)
        
        assert any("title" in i.lower() for i in issues)
    
    def test_validate_file_size(self, validator):
        """Test validating file size."""
        issues = validator.validate_file_size(200 * 1024 * 1024)  # 200 MB
        
        assert len(issues) > 0
        assert any("exceeds" in i.lower() for i in issues)
    
    def test_validate_file_type(self, validator):
        """Test validating file type."""
        issues = validator.validate_file_type("application/pdf")
        
        assert len(issues) == 0
    
    def test_validate_unsupported_type(self, validator):
        """Test validating unsupported type."""
        issues = validator.validate_file_type("application/xyz")
        
        assert len(issues) > 0
    
    def test_validate_duplicate(self, validator):
        """Test duplicate detection."""
        existing = ["abc123", "def456"]
        
        is_duplicate = validator.validate_duplicate("abc123", existing)
        
        assert is_duplicate is True
    
    def test_validate_version_consistency(self, validator):
        """Test version consistency."""
        issues = validator.validate_version_consistency(
            document_version=3,
            version_count=1
        )
        
        assert len(issues) > 0
    
    def test_validate_tag(self, validator):
        """Test tag validation."""
        issues = validator.validate_tag("valid-tag")
        
        assert len(issues) == 0
    
    def test_validate_invalid_tag(self, validator):
        """Test invalid tag validation."""
        issues = validator.validate_tag("")
        
        assert len(issues) > 0
    
    def test_validate_metadata(self, validator):
        """Test metadata validation."""
        issues = validator.validate_metadata({"key": "value"})
        
        assert len(issues) == 0


class TestDocumentFilter:
    """Tests for document filter."""
    
    def test_create_filter(self):
        """Test creating a filter."""
        filter_obj = DocumentFilter(
            asset_id="asset-1",
            document_types=[DocumentType.PDF],
            statuses=[DocumentStatus.ACTIVE]
        )
        
        assert filter_obj.asset_id == "asset-1"
        assert DocumentType.PDF in filter_obj.document_types
    
    def test_filter_to_dict(self):
        """Test filter serialization."""
        filter_obj = DocumentFilter(asset_id="asset-1")
        
        data = filter_obj.to_dict()
        
        assert data["asset_id"] == "asset-1"


class TestDocumentStatus:
    """Tests for document status."""
    
    def test_all_statuses(self):
        """Test all status values."""
        statuses = [
            DocumentStatus.ACTIVE,
            DocumentStatus.ARCHIVED,
            DocumentStatus.DELETED,
            DocumentStatus.PENDING_REVIEW,
            DocumentStatus.APPROVED
        ]
        
        assert len(statuses) == 5
    
    def test_status_values(self):
        """Test status values."""
        assert DocumentStatus.ACTIVE.value == "active"
        assert DocumentStatus.DELETED.value == "deleted"


class TestDocumentType:
    """Tests for document type."""
    
    def test_all_types(self):
        """Test all document types."""
        types = [
            DocumentType.PDF,
            DocumentType.IMAGE,
            DocumentType.REPORT,
            DocumentType.MANUAL,
            DocumentType.DRAWING,
            DocumentType.INSPECTION_FORM,
            DocumentType.MAINTENANCE_REPORT,
        ]
        
        assert len(types) == 7
    
    def test_type_values(self):
        """Test type values."""
        assert DocumentType.PDF.value == "pdf"
        assert DocumentType.MAINTENANCE_REPORT.value == "maintenance_report"


class TestDocumentVersioning:
    """Tests for document versioning."""
    
    @pytest.fixture
    def engine(self):
        """Create document engine."""
        return DocumentEngine()
    
    def test_version_numbers_increment(self, engine):
        """Test version numbers increment correctly."""
        doc = engine.create_document(
            title="Test",
            document_type=DocumentType.PDF,
            version=1
        )
        
        engine.create_new_version(doc)
        engine.create_new_version(doc)
        
        assert doc.version == 3
    
    def test_version_records_created(self, engine):
        """Test version records are created."""
        doc = engine.create_document(title="Test", document_type=DocumentType.PDF)
        
        engine.create_new_version(doc)
        engine.create_new_version(doc)
        
        versions = engine.get_versions(doc.id)
        
        assert len(versions) == 2
    
    def test_version_content_updates(self, engine):
        """Test version updates document content."""
        doc = engine.create_document(
            title="Test",
            document_type=DocumentType.PDF,
            file_name="v1.pdf",
            file_size=1000
        )
        
        engine.create_new_version(
            doc,
            file_name="v2.pdf",
            file_size=2000
        )
        
        assert doc.file_name == "v2.pdf"
        assert doc.file_size == 2000


class TestDocumentSearch:
    """Tests for document search."""
    
    @pytest.fixture
    def indexer(self):
        """Create indexer with documents."""
        indexer = DocumentIndexer()
        
        docs = [
            Document(id="d1", title="Safety Manual", description="Safety procedures", document_type=DocumentType.MANUAL, tags=["safety", "manual"]),
            Document(id="d2", title="Maintenance Guide", description="Maintenance procedures", document_type=DocumentType.MANUAL, tags=["maintenance", "guide"]),
            Document(id="d3", title="Inspection Report", description="Inspection results", document_type=DocumentType.REPORT, tags=["inspection", "report"]),
        ]
        
        for doc in docs:
            indexer.index_document(doc, tags=doc.tags)
        
        return indexer
    
    def test_search_multiple_terms(self, indexer):
        """Test searching with multiple terms."""
        results = indexer.search_by_text("manual maintenance")
        
        assert len(results) >= 1
    
    def test_search_with_filter(self, indexer):
        """Test search with filter."""
        filter_obj = DocumentFilter(
            document_types=[DocumentType.MANUAL],
            tags=["safety"]
        )
        
        results = indexer.search(filter_obj)
        
        assert len(results) >= 1
        assert results[0].document.document_type == DocumentType.MANUAL


class TestDocumentLifecycle:
    """Tests for document lifecycle."""
    
    @pytest.fixture
    def engine(self):
        """Create document engine."""
        return DocumentEngine()
    
    def test_full_lifecycle(self, engine):
        """Test complete document lifecycle."""
        # Create
        doc = engine.create_document(
            title="Test Document",
            document_type=DocumentType.PDF
        )
        
        # Update
        engine.update_document(doc, description="Updated description")
        
        # Archive
        engine.archive_document(doc)
        
        # Restore
        engine.restore_document(doc)
        
        # Delete
        engine.delete_document(doc, hard=False)
        
        # Restore
        engine.restore_deleted_document(doc)
        
        assert doc.title == "Test Document"
        assert doc.status == DocumentStatus.ACTIVE
