"""
Document Types

Core data types for the Document Management Engine.
Asset-centric document management.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from enum import Enum
import hashlib


class DocumentType(str, Enum):
    """Document types supported."""
    PDF = "pdf"
    IMAGE = "image"
    REPORT = "report"
    MANUAL = "manual"
    DRAWING = "drawing"
    INSPECTION_FORM = "inspection_form"
    MAINTENANCE_REPORT = "maintenance_report"
    VIDEO_METADATA = "video_metadata"
    CERTIFICATE = "certificate"
    CONTRACT = "contract"
    OTHER = "other"


class DocumentStatus(str, Enum):
    """Document status."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"


class DocumentState(str, Enum):
    """Computed document state."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class MIMEType(str, Enum):
    """Common MIME types."""
    PDF = "application/pdf"
    PNG = "image/png"
    JPEG = "image/jpeg"
    GIF = "image/gif"
    SVG = "image/svg+xml"
    DOC = "application/msword"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    XLS = "application/vnd.ms-excel"
    XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    PPT = "application/vnd.ms-powerpoint"
    PPTX = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    TXT = "text/plain"
    CSV = "text/csv"
    ZIP = "application/zip"
    MP4 = "video/mp4"
    AVI = "video/x-msvideo"
    UNKNOWN = "application/octet-stream"


@dataclass
class Document:
    """
    Asset-centric document.
    
    Links documents to assets and work orders.
    """
    id: str
    title: str
    document_type: DocumentType
    description: str = ""
    
    # Linkages
    asset_id: Optional[str] = None
    work_order_id: Optional[str] = None
    
    # File info
    file_name: str = ""
    mime_type: str = ""
    file_size: int = 0
    storage_path: str = ""
    checksum: str = ""
    
    # Versioning
    version: int = 1
    
    # Status
    status: DocumentStatus = DocumentStatus.ACTIVE
    
    # Metadata
    uploaded_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    archived_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_session_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "asset_id": self.asset_id,
            "work_order_id": self.work_order_id,
            "title": self.title,
            "description": self.description,
            "document_type": self.document_type.value,
            "file_name": self.file_name,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
            "storage_path": self.storage_path,
            "version": self.version,
            "status": self.status.value,
            "uploaded_by": self.uploaded_by,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "archived_at": self.archived_at.isoformat() if self.archived_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
            "metadata": self.metadata,
        }
    
    @property
    def is_active(self) -> bool:
        """Check if document is active."""
        return self.status == DocumentStatus.ACTIVE and self.deleted_at is None
    
    @property
    def is_archived(self) -> bool:
        """Check if document is archived."""
        return self.status == DocumentStatus.ARCHIVED or self.archived_at is not None
    
    @property
    def is_deleted(self) -> bool:
        """Check if document is deleted."""
        return self.status == DocumentStatus.DELETED or self.deleted_at is not None
    
    @property
    def document_state(self) -> DocumentState:
        """Compute document state."""
        if self.is_deleted:
            return DocumentState.DELETED
        if self.is_archived:
            return DocumentState.ARCHIVED
        return DocumentState.ACTIVE
    
    def get_checksum(self, content: bytes = None) -> str:
        """Calculate SHA-256 checksum of content."""
        if content:
            return hashlib.sha256(content).hexdigest()
        return self.checksum


@dataclass
class DocumentVersion:
    """
    Document version record.
    
    Tracks version history of documents.
    """
    id: str
    document_id: str
    version_number: int
    file_name: str = ""
    mime_type: str = ""
    file_size: int = 0
    storage_path: str = ""
    checksum: str = ""
    change_notes: str = ""
    created_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "document_id": self.document_id,
            "version_number": self.version_number,
            "file_name": self.file_name,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
            "storage_path": self.storage_path,
            "checksum": self.checksum,
            "change_notes": self.change_notes,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class DocumentTag:
    """
    Document tag.
    
    Tags for document categorization.
    """
    id: str
    document_id: str
    tag: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "document_id": self.document_id,
            "tag": self.tag,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Attachment:
    """
    Document attachment.
    
    Additional files attached to documents.
    """
    id: str
    document_id: str
    file_name: str
    mime_type: str = ""
    file_size: int = 0
    storage_path: str = ""
    is_primary: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "document_id": self.document_id,
            "file_name": self.file_name,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
            "storage_path": self.storage_path,
            "is_primary": self.is_primary,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class DocumentSummary:
    """
    Summary view of a document with counts.
    """
    document: Document
    version_count: int = 0
    tag_count: int = 0
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        data = self.document.to_dict()
        data["version_count"] = self.version_count
        data["tag_count"] = self.tag_count
        data["tags"] = self.tags
        data["document_state"] = self.document.document_state.value
        return data


@dataclass
class DocumentFilter:
    """Filter criteria for document queries."""
    asset_id: Optional[str] = None
    work_order_id: Optional[str] = None
    document_types: Optional[List[DocumentType]] = None
    statuses: Optional[List[DocumentStatus]] = None
    tags: Optional[List[str]] = None
    uploaded_by: Optional[str] = None
    search_text: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    include_archived: bool = False
    include_deleted: bool = False
    limit: int = 100
    offset: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "asset_id": self.asset_id,
            "work_order_id": self.work_order_id,
            "document_types": [t.value for t in self.document_types] if self.document_types else None,
            "statuses": [s.value for s in self.statuses] if self.statuses else None,
            "tags": self.tags,
            "uploaded_by": self.uploaded_by,
            "search_text": self.search_text,
            "created_after": self.created_after.isoformat() if self.created_after else None,
            "created_before": self.created_before.isoformat() if self.created_before else None,
            "include_archived": self.include_archived,
            "include_deleted": self.include_deleted,
            "limit": self.limit,
            "offset": self.offset,
        }


@dataclass
class DocumentIndex:
    """
    Document index entry for search.
    
    In-memory index for fast searching.
    """
    document_id: str
    title: str
    description: str
    document_type: str
    tags: List[str]
    asset_id: Optional[str]
    work_order_id: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    
    def matches(self, filter: DocumentFilter) -> bool:
        """Check if this document matches the filter."""
        if self.asset_id and filter.asset_id and self.asset_id != filter.asset_id:
            return False
        
        if self.work_order_id and filter.work_order_id and self.work_order_id != filter.work_order_id:
            return False
        
        if filter.document_types and DocumentType(self.document_type) not in filter.document_types:
            return False
        
        if filter.statuses and DocumentStatus(self.status) not in filter.statuses:
            return False
        
        if filter.tags:
            if not any(tag in self.tags for tag in filter.tags):
                return False
        
        if filter.search_text:
            search_lower = filter.search_text.lower()
            if (search_lower not in self.title.lower() and
                search_lower not in self.description.lower()):
                return False
        
        return True
    
    def to_dict(self) -> Dict:
        return {
            "document_id": self.document_id,
            "title": self.title,
            "description": self.description,
            "document_type": self.document_type,
            "tags": self.tags,
            "asset_id": self.asset_id,
            "work_order_id": self.work_order_id,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class DocumentSearchResult:
    """Search result with relevance score."""
    document: Document
    score: float = 1.0
    matched_fields: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        data = self.document.to_dict()
        data["score"] = self.score
        data["matched_fields"] = self.matched_fields
        return data
