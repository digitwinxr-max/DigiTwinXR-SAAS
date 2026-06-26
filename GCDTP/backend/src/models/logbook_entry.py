"""
Digital Logbook Entry Model

Represents immutable operational logbook entries.
Entries are append-only - no edits or deletes.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


class EntryType(str, Enum):
    """Types of logbook entries."""
    OBSERVATION = "observation"
    INCIDENT = "incident"
    MAINTENANCE = "maintenance"
    INSPECTION = "inspection"
    INVESTIGATION = "investigation"
    ANNOTATION = "annotation"


class Severity(str, Enum):
    """Severity levels for logbook entries."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class LogbookEntry:
    """
    Immutable logbook entry.
    
    This model represents an operational logbook entry.
    Entries are append-only - no edits or deletes allowed.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    entry_type: EntryType = EntryType.OBSERVATION
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    severity: Severity = Severity.INFO
    content: str = ""
    author: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    timeline_snapshot_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def summary(self, max_length: int = 100) -> str:
        """
        Generate a summary of the entry.
        
        Args:
            max_length: Maximum length of summary.
            
        Returns:
            Summary string.
        """
        if len(self.content) <= max_length:
            return self.content
        
        return self.content[:max_length].rsplit(' ', 1)[0] + '...'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "entry_type": self.entry_type.value if isinstance(self.entry_type, Enum) else self.entry_type,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "severity": self.severity.value if isinstance(self.severity, Enum) else self.severity,
            "content": self.content,
            "author": self.author,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "timeline_snapshot_id": self.timeline_snapshot_id,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LogbookEntry":
        """Create from dictionary."""
        entry_type = data.get("entry_type")
        if isinstance(entry_type, str):
            entry_type = EntryType(entry_type)
        
        severity = data.get("severity")
        if isinstance(severity, str):
            severity = Severity(severity)
        
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data.get("title", ""),
            entry_type=entry_type or EntryType.OBSERVATION,
            entity_type=data.get("entity_type"),
            entity_id=data.get("entity_id"),
            severity=severity or Severity.INFO,
            content=data.get("content", ""),
            author=data.get("author", ""),
            timestamp=timestamp or datetime.utcnow(),
            timeline_snapshot_id=data.get("timeline_snapshot_id"),
            created_at=created_at or datetime.utcnow()
        )
    
    def get_severity_color(self) -> str:
        """Get color for severity."""
        colors = {
            Severity.INFO: "#2196F3",
            Severity.WARNING: "#FF9800",
            Severity.CRITICAL: "#F44336"
        }
        return colors.get(self.severity, "#9E9E9E")
    
    def get_entry_type_icon(self) -> str:
        """Get icon for entry type."""
        icons = {
            EntryType.OBSERVATION: "👁",
            EntryType.INCIDENT: "🚨",
            EntryType.MAINTENANCE: "🔧",
            EntryType.INSPECTION: "🔍",
            EntryType.INVESTIGATION: "📋",
            EntryType.ANNOTATION: "📝"
        }
        return icons.get(self.entry_type, "📄")


class LogbookSummary:
    """Summary statistics for logbook."""
    
    def __init__(self):
        self.total_entries = 0
        self.by_severity: Dict[Severity, int] = {
            Severity.INFO: 0,
            Severity.WARNING: 0,
            Severity.CRITICAL: 0
        }
        self.by_type: Dict[EntryType, int] = {
            EntryType.OBSERVATION: 0,
            EntryType.INCIDENT: 0,
            EntryType.MAINTENANCE: 0,
            EntryType.INSPECTION: 0,
            EntryType.INVESTIGATION: 0,
            EntryType.ANNOTATION: 0
        }
        self.by_author: Dict[str, int] = {}
        self.latest_entry: Optional[LogbookEntry] = None
        self.oldest_entry: Optional[LogbookEntry] = None
    
    def add_entry(self, entry: LogbookEntry) -> None:
        """Add entry to summary."""
        self.total_entries += 1
        
        if isinstance(entry.severity, Enum):
            severity_key = entry.severity
        else:
            severity_key = Severity(entry.severity)
        self.by_severity[severity_key] = self.by_severity.get(severity_key, 0) + 1
        
        if isinstance(entry.entry_type, Enum):
            type_key = entry.entry_type
        else:
            type_key = EntryType(entry.entry_type)
        self.by_type[type_key] = self.by_type.get(type_key, 0) + 1
        
        self.by_author[entry.author] = self.by_author.get(entry.author, 0) + 1
        
        if self.latest_entry is None or entry.timestamp > self.latest_entry.timestamp:
            self.latest_entry = entry
        
        if self.oldest_entry is None or entry.timestamp < self.oldest_entry.timestamp:
            self.oldest_entry = entry
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_entries": self.total_entries,
            "by_severity": {
                k.value if isinstance(k, Enum) else k: v 
                for k, v in self.by_severity.items()
            },
            "by_type": {
                k.value if isinstance(k, Enum) else k: v 
                for k, v in self.by_type.items()
            },
            "by_author": self.by_author,
            "latest_entry": self.latest_entry.to_dict() if self.latest_entry else None,
            "oldest_entry": self.oldest_entry.to_dict() if self.oldest_entry else None
        }
