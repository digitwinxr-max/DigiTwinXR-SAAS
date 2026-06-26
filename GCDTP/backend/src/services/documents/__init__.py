"""
Document Management Module

Asset-centric document management.
Document creation, versioning, search, and lifecycle management.
"""

from .document_types import (
    DocumentType,
    DocumentStatus,
    DocumentState,
    MIMEType,
    Document,
    DocumentVersion,
    DocumentTag,
    Attachment,
    DocumentSummary,
    DocumentFilter,
    DocumentIndex,
    DocumentSearchResult,
)

from .document_engine import DocumentEngine
from .document_indexer import DocumentIndexer
from .attachment_manager import AttachmentManager
from .document_validator import DocumentValidator


__all__ = [
    # Enums
    "DocumentType",
    "DocumentStatus",
    "DocumentState",
    "MIMEType",
    # Types
    "Document",
    "DocumentVersion",
    "DocumentTag",
    "Attachment",
    "DocumentSummary",
    "DocumentFilter",
    "DocumentIndex",
    "DocumentSearchResult",
    # Engines
    "DocumentEngine",
    "DocumentIndexer",
    "AttachmentManager",
    "DocumentValidator",
]
