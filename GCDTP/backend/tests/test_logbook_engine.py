"""
Tests for Digital Logbook Engine

Tests entry creation, search, history retrieval,
append-only behavior, and timeline references.
"""

import pytest
from datetime import datetime, timedelta
from src.models.logbook_entry import LogbookEntry, EntryType, Severity
from src.services.logbook_service import LogbookService
from src.schemas.logbook import LogbookEntryCreate, LogbookSearchQuery


class TestLogbookEntry:
    """Tests for logbook entry operations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = LogbookService()
    
    def test_create_entry(self):
        """Test creating a logbook entry."""
        data = LogbookEntryCreate(
            title="Test Entry",
            entry_type="observation",
            severity="info",
            content="This is a test observation",
            author="Test Author"
        )
        
        entry = self.service.create_entry(data)
        
        assert entry is not None
        assert entry.title == "Test Entry"
        assert entry.entry_type == EntryType.OBSERVATION
        assert entry.severity == Severity.INFO
        assert entry.content == "This is a test observation"
        assert entry.author == "Test Author"
    
    def test_create_entry_all_types(self):
        """Test creating entries of all types."""
        types = [
            "observation", "incident", "maintenance",
            "inspection", "investigation", "annotation"
        ]
        
        for entry_type in types:
            data = LogbookEntryCreate(
                title=f"Test {entry_type}",
                entry_type=entry_type,
                severity="info",
                content="Test content",
                author="Test"
            )
            entry = self.service.create_entry(data)
            assert entry is not None
            assert entry.entry_type.value == entry_type
    
    def test_create_entry_all_severities(self):
        """Test creating entries with all severities."""
        severities = ["info", "warning", "critical"]
        
        for severity in severities:
            data = LogbookEntryCreate(
                title=f"Test {severity}",
                entry_type="observation",
                severity=severity,
                content="Test content",
                author="Test"
            )
            entry = self.service.create_entry(data)
            assert entry is not None
            assert entry.severity.value == severity
    
    def test_entry_with_entity(self):
        """Test creating entry with entity reference."""
        data = LogbookEntryCreate(
            title="Asset Observation",
            entry_type="observation",
            severity="info",
            content="Observation about asset",
            author="Operator",
            entity_type="asset",
            entity_id="asset-001"
        )
        
        entry = self.service.create_entry(data)
        
        assert entry.entity_type == "asset"
        assert entry.entity_id == "asset-001"
    
    def test_entry_with_timeline(self):
        """Test creating entry with timeline reference."""
        data = LogbookEntryCreate(
            title="Timeline Reference",
            entry_type="annotation",
            severity="info",
            content="Annotation at specific time",
            author="Analyst",
            timeline_snapshot_id="snapshot-123"
        )
        
        entry = self.service.create_entry(data)
        
        assert entry.timeline_snapshot_id == "snapshot-123"


class TestLogbookImmutable:
    """Tests for append-only behavior."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = LogbookService()
    
    def test_entries_are_created(self):
        """Test that entries can be created."""
        data = LogbookEntryCreate(
            title="Entry 1",
            entry_type="observation",
            severity="info",
            content="Content",
            author="Test"
        )
        
        entry = self.service.create_entry(data)
        
        # Verify entry was created
        assert entry is not None
        
        # Verify we can retrieve it
        retrieved = self.service.get_entry(entry.id)
        assert retrieved is not None
        assert retrieved.id == entry.id
    
    def test_no_update_method(self):
        """Test that service has no update method."""
        # Verify no update methods exist
        methods = [m for m in dir(self.service) if not m.startswith('_')]
        update_methods = [m for m in methods if 'update' in m.lower()]
        
        # Service should have no update/delete methods
        assert len(update_methods) == 0
    
    def test_no_delete_method(self):
        """Test that service has no delete method."""
        # Verify no delete methods exist
        methods = [m for m in dir(self.service) if not m.startswith('_')]
        delete_methods = [m for m in methods if 'delete' in m.lower()]
        
        # Service should have no delete methods
        assert len(delete_methods) == 0


class TestLogbookSearch:
    """Tests for logbook search."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = LogbookService()
        
        # Create test entries
        self.entries = []
        for i in range(10):
            data = LogbookEntryCreate(
                title=f"Entry {i}",
                entry_type=["observation", "incident"][i % 2],
                severity=["info", "warning", "critical"][i % 3],
                content=f"Content for entry {i} with keyword",
                author=f"Author{i % 3}"
            )
            self.entries.append(self.service.create_entry(data))
    
    def test_list_entries(self):
        """Test listing all entries."""
        entries = self.service.list_entries()
        assert len(entries) == 10
    
    def test_search_by_type(self):
        """Test filtering by entry type."""
        entries = self.service.list_entries(entry_type="observation")
        assert all(e.entry_type == EntryType.OBSERVATION for e in entries)
    
    def test_search_by_severity(self):
        """Test filtering by severity."""
        entries = self.service.list_entries(severity="critical")
        assert all(e.severity == Severity.CRITICAL for e in entries)
    
    def test_search_by_author(self):
        """Test filtering by author."""
        entries = self.service.list_entries(author="Author0")
        assert all(e.author == "Author0" for e in entries)
    
    def test_text_search(self):
        """Test text search in title and content."""
        query = LogbookSearchQuery(query="keyword")
        results = self.service.search_entries(query)
        assert len(results) == 10
        assert all("keyword" in e.content.lower() for e in results)


class TestLogbookHistory:
    """Tests for history retrieval."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = LogbookService()
        
        # Create entries for entity
        for i in range(5):
            data = LogbookEntryCreate(
                title=f"Asset Entry {i}",
                entry_type="observation",
                severity="info",
                content=f"Observation {i}",
                author="Test",
                entity_type="asset",
                entity_id="test-asset"
            )
            self.service.create_entry(data)
    
    def test_get_by_entity(self):
        """Test getting entries by entity."""
        entries = self.service.get_by_entity("asset", "test-asset")
        assert len(entries) == 5
        assert all(e.entity_id == "test-asset" for e in entries)
    
    def test_build_asset_history(self):
        """Test building complete asset history."""
        entries = self.service.build_asset_history("asset", "test-asset")
        assert len(entries) == 5
    
    def test_build_incident_history(self):
        """Test building incident history."""
        # Create some incidents
        self.service.create_entry(LogbookEntryCreate(
            title="Incident 1",
            entry_type="incident",
            severity="critical",
            content="Critical incident",
            author="Test"
        ))
        
        incidents = self.service.build_incident_history()
        assert len(incidents) >= 1
        assert all(e.entry_type == EntryType.INCIDENT for e in incidents)


class TestLogbookSummary:
    """Tests for logbook summary."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = LogbookService()
        
        # Create various entries
        for i in range(20):
            data = LogbookEntryCreate(
                title=f"Entry {i}",
                entry_type=["observation", "incident"][i % 2],
                severity=["info", "warning", "critical"][i % 3],
                content=f"Content {i}",
                author=f"Author{i % 4}"
            )
            self.service.create_entry(data)
    
    def test_get_summary(self):
        """Test getting summary statistics."""
        summary = self.service.get_summary()
        
        assert summary["total_entries"] == 20
        assert summary["by_severity"]["info"] >= 0
        assert summary["by_severity"]["warning"] >= 0
        assert summary["by_severity"]["critical"] >= 0
        assert summary["by_type"]["observation"] >= 0
        assert summary["by_type"]["incident"] >= 0
    
    def test_summary_by_author(self):
        """Test summary by author."""
        summary = self.service.get_summary()
        assert len(summary["by_author"]) > 0
        assert all("author" in a and "count" in a for a in summary["by_author"])


class TestLogbookTimeline:
    """Tests for timeline integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = LogbookService()
    
    def test_entry_with_timeline_reference(self):
        """Test entry with timeline reference."""
        data = LogbookEntryCreate(
            title="Timeline Note",
            entry_type="annotation",
            severity="info",
            content="Note at this time",
            author="Analyst",
            timeline_snapshot_id="snap-123"
        )
        
        entry = self.service.create_entry(data)
        assert entry.timeline_snapshot_id == "snap-123"
    
    def test_get_by_timeline(self):
        """Test getting entries by timeline snapshot."""
        # Create entries with same timeline reference
        for i in range(3):
            self.service.create_entry(LogbookEntryCreate(
                title=f"Timeline Entry {i}",
                entry_type="annotation",
                severity="info",
                content=f"Annotation {i}",
                author="Test",
                timeline_snapshot_id="snap-shared"
            ))
        
        entries = self.service.get_by_timeline("snap-shared")
        assert len(entries) == 3
        assert all(e.timeline_snapshot_id == "snap-shared" for e in entries)
