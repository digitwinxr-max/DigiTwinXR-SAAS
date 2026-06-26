"""
Digital Logbook Service

Provides immutable operational logbook operations.
Entries are append-only - no edits or deletes.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from collections import defaultdict

from ..models.logbook_entry import LogbookEntry, EntryType, Severity, LogbookSummary
from ..schemas.logbook import (
    LogbookEntryCreate,
    LogbookSearchQuery,
    SeveritySummary,
    TypeSummary,
    AuthorSummary
)


class LogbookService:
    """
    Service for digital logbook operations.
    
    This service provides:
    - Entry creation (append-only)
    - Entry retrieval
    - Search functionality
    - History building
    
    NO edits, NO deletes.
    Entries are immutable.
    """
    
    def __init__(self):
        # In-memory entry storage
        self._entries: Dict[str, LogbookEntry] = {}
        # Index by entity
        self._by_entity: Dict[tuple, List[str]] = defaultdict(list)
        # Index by type
        self._by_type: Dict[str, List[str]] = defaultdict(list)
        # Index by severity
        self._by_severity: Dict[str, List[str]] = defaultdict(list)
        # Index by author
        self._by_author: Dict[str, List[str]] = defaultdict(list)
        # Index by timeline
        self._by_timeline: Dict[str, List[str]] = defaultdict(list)
    
    def create_entry(self, data: LogbookEntryCreate) -> LogbookEntry:
        """
        Create a new logbook entry.
        
        This is the ONLY write operation allowed.
        Entries are immutable once created.
        
        Args:
            data: Entry data
            
        Returns:
            Created LogbookEntry
        """
        entry = LogbookEntry(
            title=data.title,
            entry_type=EntryType(data.entry_type),
            entity_type=data.entity_type,
            entity_id=data.entity_id,
            severity=Severity(data.severity),
            content=data.content,
            author=data.author,
            timestamp=data.timestamp or datetime.utcnow(),
            timeline_snapshot_id=data.timeline_snapshot_id
        )
        
        self._entries[entry.id] = entry
        
        # Update indexes
        if data.entity_type and data.entity_id:
            self._by_entity[(data.entity_type, data.entity_id)].append(entry.id)
        
        self._by_type[data.entry_type].append(entry.id)
        self._by_severity[data.severity].append(entry.id)
        self._by_author[data.author].append(entry.id)
        
        if data.timeline_snapshot_id:
            self._by_timeline[data.timeline_snapshot_id].append(entry.id)
        
        return entry
    
    def get_entry(self, entry_id: str) -> Optional[LogbookEntry]:
        """Get an entry by ID."""
        return self._entries.get(entry_id)
    
    def list_entries(
        self,
        entry_type: Optional[str] = None,
        severity: Optional[str] = None,
        author: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[LogbookEntry]:
        """
        List logbook entries with filters.
        
        Args:
            entry_type: Filter by entry type
            severity: Filter by severity
            author: Filter by author
            limit: Max results
            offset: Result offset
            
        Returns:
            List of entries
        """
        results = list(self._entries.values())
        
        # Apply filters
        if entry_type:
            results = [e for e in results if e.entry_type.value == entry_type]
        
        if severity:
            results = [e for e in results if e.severity.value == severity]
        
        if author:
            results = [e for e in results if e.author == author]
        
        # Sort by timestamp descending
        results.sort(key=lambda e: e.timestamp, reverse=True)
        
        return results[offset:offset + limit]
    
    def search_entries(self, query: LogbookSearchQuery) -> List[LogbookEntry]:
        """
        Search logbook entries.
        
        Args:
            query: Search parameters
            
        Returns:
            List of matching entries
        """
        results = list(self._entries.values())
        
        # Text search
        if query.query:
            query_lower = query.query.lower()
            results = [
                e for e in results
                if query_lower in e.title.lower() or
                   query_lower in e.content.lower()
            ]
        
        # Apply filters
        if query.entry_type:
            results = [e for e in results if e.entry_type.value == query.entry_type]
        
        if query.entity_type:
            results = [e for e in results if e.entity_type == query.entity_type]
        
        if query.entity_id:
            results = [e for e in results if e.entity_id == query.entity_id]
        
        if query.severity:
            results = [e for e in results if e.severity.value == query.severity]
        
        if query.author:
            results = [e for e in results if e.author == query.author]
        
        # Time range filter
        if query.start_time:
            results = [e for e in results if e.timestamp >= query.start_time]
        
        if query.end_time:
            results = [e for e in results if e.timestamp <= query.end_time]
        
        # Sort by timestamp descending
        results.sort(key=lambda e: e.timestamp, reverse=True)
        
        return results[offset:offset + limit]
    
    def get_by_entity(
        self,
        entity_type: str,
        entity_id: str
    ) -> List[LogbookEntry]:
        """
        Get all entries for an entity.
        
        Args:
            entity_type: Entity type
            entity_id: Entity ID
            
        Returns:
            List of entries
        """
        entry_ids = self._by_entity.get((entity_type, entity_id), [])
        entries = [self._entries[eid] for eid in entry_ids if eid in self._entries]
        entries.sort(key=lambda e: e.timestamp, reverse=True)
        return entries
    
    def get_by_type(self, entry_type: str) -> List[LogbookEntry]:
        """Get entries by type."""
        entry_ids = self._by_type.get(entry_type, [])
        entries = [self._entries[eid] for eid in entry_ids if eid in self._entries]
        entries.sort(key=lambda e: e.timestamp, reverse=True)
        return entries
    
    def get_by_severity(self, severity: str) -> List[LogbookEntry]:
        """Get entries by severity."""
        entry_ids = self._by_severity.get(severity, [])
        entries = [self._entries[eid] for eid in entry_ids if eid in self._entries]
        entries.sort(key=lambda e: e.timestamp, reverse=True)
        return entries
    
    def get_by_time_range(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[LogbookEntry]:
        """Get entries within a time range."""
        results = [
            e for e in self._entries.values()
            if start_time <= e.timestamp <= end_time
        ]
        results.sort(key=lambda e: e.timestamp, reverse=True)
        return results
    
    def get_by_timeline(self, timeline_snapshot_id: str) -> List[LogbookEntry]:
        """Get entries linked to a timeline snapshot."""
        entry_ids = self._by_timeline.get(timeline_snapshot_id, [])
        entries = [self._entries[eid] for eid in entry_ids if eid in self._entries]
        entries.sort(key=lambda e: e.timestamp, reverse=True)
        return entries
    
    def build_incident_history(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[LogbookEntry]:
        """
        Build incident history.
        
        Args:
            start_time: Start of range
            end_time: End of range
            
        Returns:
            List of incident entries
        """
        incidents = [e for e in self._entries.values() 
                     if e.entry_type == EntryType.INCIDENT]
        
        if start_time:
            incidents = [e for e in incidents if e.timestamp >= start_time]
        
        if end_time:
            incidents = [e for e in incidents if e.timestamp <= end_time]
        
        incidents.sort(key=lambda e: e.timestamp, reverse=True)
        return incidents
    
    def build_asset_history(
        self,
        entity_type: str,
        entity_id: str
    ) -> List[LogbookEntry]:
        """
        Build complete history for an asset.
        
        Combines all entries related to the asset.
        
        Args:
            entity_type: Entity type
            entity_id: Entity ID
            
        Returns:
            List of all related entries
        """
        # Get direct entries
        direct_entries = self.get_by_entity(entity_type, entity_id)
        
        # Also get related entries through timeline
        related_ids = set()
        for entry in direct_entries:
            if entry.timeline_snapshot_id:
                related_ids.update(self._by_timeline.get(entry.timeline_snapshot_id, []))
        
        related_entries = [self._entries[eid] for eid in related_ids 
                          if eid in self._entries]
        
        # Combine and deduplicate
        all_entries = {e.id: e for e in direct_entries + related_entries}
        
        # Sort by timestamp
        result = list(all_entries.values())
        result.sort(key=lambda e: e.timestamp, reverse=True)
        
        return result
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get logbook summary statistics.
        
        Returns:
            Summary statistics
        """
        summary = LogbookSummary()
        
        for entry in self._entries.values():
            summary.add_entry(entry)
        
        # Convert to response format
        return {
            "total_entries": summary.total_entries,
            "by_severity": SeveritySummary(
                info=summary.by_severity.get(Severity.INFO, 0),
                warning=summary.by_severity.get(Severity.WARNING, 0),
                critical=summary.by_severity.get(Severity.CRITICAL, 0)
            ),
            "by_type": TypeSummary(
                observation=summary.by_type.get(EntryType.OBSERVATION, 0),
                incident=summary.by_type.get(EntryType.INCIDENT, 0),
                maintenance=summary.by_type.get(EntryType.MAINTENANCE, 0),
                inspection=summary.by_type.get(EntryType.INSPECTION, 0),
                investigation=summary.by_type.get(EntryType.INVESTIGATION, 0),
                annotation=summary.by_type.get(EntryType.ANNOTATION, 0)
            ),
            "by_author": [
                AuthorSummary(author=author, count=count)
                for author, count in sorted(
                    summary.by_author.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            ],
            "latest_entry": summary.latest_entry.to_dict() if summary.latest_entry else None,
            "oldest_entry": summary.oldest_entry.to_dict() if summary.oldest_entry else None
        }


# Global instance
logbook_service = LogbookService()
