"""
Audit Module

Comprehensive audit trail for all AI operations.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class AuditEntry:
    """Audit entry."""
    entry_id: str
    timestamp: datetime
    operation: str
    user: str
    details: Dict[str, Any]
    evidence: List[str]
    reversible: bool


class AuditLogger:
    """
    Comprehensive audit logger.
    """
    
    def __init__(self):
        self._entries: Dict[str, AuditEntry] = {}
    
    def log(
        self,
        entry_id: str,
        operation: str,
        user: str,
        details: Dict[str, Any],
        evidence: Optional[List[str]] = None,
        reversible: bool = False
    ) -> AuditEntry:
        """Log an audit entry."""
        entry = AuditEntry(
            entry_id=entry_id,
            timestamp=datetime.now(),
            operation=operation,
            user=user,
            details=details,
            evidence=evidence or [],
            reversible=reversible
        )
        self._entries[entry_id] = entry
        return entry
    
    def get_entries(
        self,
        operation: Optional[str] = None,
        user: Optional[str] = None
    ) -> List[AuditEntry]:
        """Get audit entries."""
        entries = list(self._entries.values())
        if operation:
            entries = [e for e in entries if e.operation == operation]
        if user:
            entries = [e for e in entries if e.user == user]
        return sorted(entries, key=lambda e: e.timestamp, reverse=True)


_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get or create audit logger singleton."""
    global _logger
    if _logger is None:
        _logger = AuditLogger()
    return _logger
