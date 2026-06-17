"""
Document Engine

Main engine for asset-centric document management.
Handles document creation, versioning, and lifecycle management.
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from backend.src.services.documents.document_types import (
    Document,
    DocumentVersion,
    DocumentTag,
    DocumentStatus,
    DocumentType,
    DocumentSummary,
)
from backend.src.services.documents.document_validator import DocumentValidator
from backend.src.services.documents.document_indexer import DocumentIndexer
from backend.src.core.events import get_event_bus, EventType


class DocumentEngine:
    """
    Main engine for document management.
    
    Responsibilities:
    - Create documents
    - Version control
    - Asset linkage
    - Work order linkage
    - Archive/restore
    - Soft delete
    """
    
    def __init__(self):
        self.validator = DocumentValidator()
        self.indexer = DocumentIndexer()
        self.event_bus = get_event_bus()
        self._documents: Dict[str, Document] = {}
        self._versions: Dict[str, List[DocumentVersion]] = {}
        self._tags: Dict[str, List[DocumentTag]] = {}
    
    def create_document(
        self,
        title: str,
        document_type: DocumentType,
        description: str = "",
        asset_id: Optional[str] = None,
        work_order_id: Optional[str] = None,
        file_name: str = "",
        mime_type: str = "",
        file_size: int = 0,
        storage_path: str = "",
        checksum: str = "",
        uploaded_by: Optional[str] = None,
        metadata: Optional[Dict] = None,
        session_id: Optional[str] = None
    ) -> Document:
        """
        Create a new document.
        
        Args:
            title: Document title
            document_type: Type of document
            description: Document description
            asset_id: Associated asset ID
            work_order_id: Associated work order ID
            file_name: Original file name
            mime_type: MIME type
            file_size: File size in bytes
            storage_path: Storage location
            checksum: Content checksum
            uploaded_by: User who uploaded
            metadata: Additional metadata
            session_id: Timeline session ID
            
        Returns:
            Created Document
        """
        document = Document(
            id=str(uuid.uuid4()),
            title=title,
            document_type=document_type,
            description=description,
            asset_id=asset_id,
            work_order_id=work_order_id,
            file_name=file_name,
            mime_type=mime_type,
            file_size=file_size,
            storage_path=storage_path,
            checksum=checksum,
            uploaded_by=uploaded_by,
            metadata=metadata or {},
            created_session_id=session_id
        )
        
        # Validate
        issues = self.validator.validate_document(document)
        if issues:
            raise ValueError(f"Validation failed: {', '.join(issues)}")
        
        # Store document
        self._documents[document.id] = document
        self._versions[document.id] = []
        self._tags[document.id] = []
        
        # Index document
        self.indexer.index_document(document)
        
        # Publish event
        self.event_bus.publish(
            EventType.DOCUMENT_CREATED,
            source="document_engine",
            data={
                "document_id": document.id,
                "title": document.title,
                "document_type": document.document_type.value,
                "asset_id": document.asset_id,
                "work_order_id": document.work_order_id,
            }
        )
        
        return document
    
    def update_document(
        self,
        document: Document,
        **kwargs
    ) -> Document:
        """
        Update a document.
        
        Args:
            document: Document to update
            **kwargs: Fields to update
            
        Returns:
            Updated Document
        """
        for key, value in kwargs.items():
            if hasattr(document, key):
                setattr(document, key, value)
        
        document.updated_at = datetime.utcnow()
        
        # Validate
        issues = self.validator.validate_document(document)
        if issues:
            raise ValueError(f"Validation failed: {', '.join(issues)}")
        
        # Re-index
        self.indexer.update_document(document)
        
        # Publish event
        self.event_bus.publish(
            EventType.DOCUMENT_UPDATED,
            source="document_engine",
            data={
                "document_id": document.id,
                "title": document.title,
                "updated_fields": list(kwargs.keys()),
            }
        )
        
        return document
    
    def create_new_version(
        self,
        document: Document,
        file_name: str = "",
        mime_type: str = "",
        file_size: int = 0,
        storage_path: str = "",
        checksum: str = "",
        change_notes: str = "",
        created_by: Optional[str] = None
    ) -> DocumentVersion:
        """
        Create a new version of a document.
        
        Args:
            document: Parent document
            file_name: New file name
            mime_type: New MIME type
            file_size: New file size
            storage_path: New storage path
            checksum: New checksum
            change_notes: Version change notes
            created_by: User creating version
            
        Returns:
            Created DocumentVersion
        """
        version = DocumentVersion(
            id=str(uuid.uuid4()),
            document_id=document.id,
            version_number=document.version + 1,
            file_name=file_name or document.file_name,
            mime_type=mime_type or document.mime_type,
            file_size=file_size or document.file_size,
            storage_path=storage_path or document.storage_path,
            checksum=checksum or document.checksum,
            change_notes=change_notes,
            created_by=created_by
        )
        
        # Update document
        document.version += 1
        document.file_name = version.file_name
        document.mime_type = version.mime_type
        document.file_size = version.file_size
        document.storage_path = version.storage_path
        document.checksum = version.checksum
        document.updated_at = datetime.utcnow()
        
        # Store version
        self._versions[document.id].append(version)
        
        # Re-index
        self.indexer.update_document(document)
        
        # Publish event
        self.event_bus.publish(
            EventType.DOCUMENT_VERSION_CREATED,
            source="document_engine",
            data={
                "document_id": document.id,
                "version_number": version.version_number,
                "change_notes": change_notes,
            }
        )
        
        return version
    
    def get_document(self, document_id: str) -> Optional[Document]:
        """Get a document by ID."""
        return self._documents.get(document_id)
    
    def get_versions(self, document_id: str) -> List[DocumentVersion]:
        """Get all versions of a document."""
        return self._versions.get(document_id, [])
    
    def archive_document(self, document: Document) -> Document:
        """
        Archive a document.
        
        Args:
            document: Document to archive
            
        Returns:
            Updated Document
        """
        document.status = DocumentStatus.ARCHIVED
        document.archived_at = datetime.utcnow()
        document.updated_at = datetime.utcnow()
        
        # Re-index
        self.indexer.update_document(document)
        
        # Publish event
        self.event_bus.publish(
            EventType.DOCUMENT_ARCHIVED,
            source="document_engine",
            data={
                "document_id": document.id,
                "title": document.title,
            }
        )
        
        return document
    
    def restore_document(self, document: Document) -> Document:
        """
        Restore an archived document.
        
        Args:
            document: Document to restore
            
        Returns:
            Updated Document
        """
        if document.is_deleted:
            raise ValueError("Cannot restore a deleted document")
        
        document.status = DocumentStatus.ACTIVE
        document.archived_at = None
        document.updated_at = datetime.utcnow()
        
        # Re-index
        self.indexer.update_document(document)
        
        # Publish event
        self.event_bus.publish(
            EventType.DOCUMENT_RESTORED,
            source="document_engine",
            data={
                "document_id": document.id,
                "title": document.title,
            }
        )
        
        return document
    
    def delete_document(self, document: Document, hard: bool = False) -> Document:
        """
        Delete a document (soft delete by default).
        
        Args:
            document: Document to delete
            hard: If True, permanently delete
            
        Returns:
            Updated Document
        """
        if hard:
            # Permanent deletion
            del self._documents[document.id]
            if document.id in self._versions:
                del self._versions[document.id]
            if document.id in self._tags:
                del self._tags[document.id]
            
            # Remove from index
            self.indexer.remove_document(document.id)
            
            self.event_bus.publish(
                EventType.DOCUMENT_DELETED,
                source="document_engine",
                data={
                    "document_id": document.id,
                    "hard_delete": True,
                }
            )
            return document
        else:
            # Soft delete
            document.status = DocumentStatus.DELETED
            document.deleted_at = datetime.utcnow()
            document.updated_at = datetime.utcnow()
            
            # Re-index
            self.indexer.update_document(document)
            
            # Publish event
            self.event_bus.publish(
                EventType.DOCUMENT_DELETED,
                source="document_engine",
                data={
                    "document_id": document.id,
                    "title": document.title,
                    "hard_delete": False,
                }
            )
            
            return document
    
    def restore_deleted_document(self, document: Document) -> Document:
        """
        Restore a soft-deleted document.
        
        Args:
            document: Document to restore
            
        Returns:
            Updated Document
        """
        if not document.is_deleted:
            raise ValueError("Document is not deleted")
        
        document.status = DocumentStatus.ACTIVE
        document.deleted_at = None
        document.updated_at = datetime.utcnow()
        
        # Re-index
        self.indexer.update_document(document)
        
        # Publish event
        self.event_bus.publish(
            EventType.DOCUMENT_RESTORED,
            source="document_engine",
            data={
                "document_id": document.id,
                "title": document.title,
            }
        )
        
        return document
    
    def get_documents_by_asset(self, asset_id: str) -> List[Document]:
        """Get all documents for an asset."""
        return [
            doc for doc in self._documents.values()
            if doc.asset_id == asset_id and not doc.is_deleted
        ]
    
    def get_documents_by_work_order(self, work_order_id: str) -> List[Document]:
        """Get all documents for a work order."""
        return [
            doc for doc in self._documents.values()
            if doc.work_order_id == work_order_id and not doc.is_deleted
        ]
    
    def get_active_documents(self) -> List[Document]:
        """Get all active documents."""
        return [
            doc for doc in self._documents.values()
            if doc.is_active
        ]
    
    def get_document_summary(self, document: Document) -> DocumentSummary:
        """Get summary with counts."""
        versions = self._versions.get(document.id, [])
        tags = self._tags.get(document.id, [])
        
        return DocumentSummary(
            document=document,
            version_count=len(versions),
            tag_count=len(tags),
            tags=[t.tag for t in tags]
        )
