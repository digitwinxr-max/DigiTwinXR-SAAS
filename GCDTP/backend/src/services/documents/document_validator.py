"""
Document Validator

Validates documents and attachments for correctness.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from backend.src.services.documents.document_types import (
    Document,
    DocumentType,
    DocumentStatus,
    Attachment,
)


class DocumentValidator:
    """
    Validates documents and related entities.
    
    Checks:
    - File type validation
    - Size validation
    - Duplicate detection
    - Version consistency
    - Metadata validation
    """
    
    # Maximum file size (100 MB)
    MAX_FILE_SIZE = 100 * 1024 * 1024
    
    # Supported MIME types
    SUPPORTED_TYPES = {
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/gif",
        "image/svg+xml",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "text/plain",
        "text/csv",
        "application/zip",
        "video/mp4",
        "video/x-msvideo",
    }
    
    def __init__(self):
        self.issues: List[str] = []
    
    def validate_document(self, document: Document) -> List[str]:
        """
        Validate a document.
        
        Args:
            document: Document to validate
            
        Returns:
            List of validation issues
        """
        self.issues = []
        
        # Required fields
        if not document.id:
            self.issues.append("Document ID is required")
        
        if not document.title or not document.title.strip():
            self.issues.append("Title is required")
        
        if document.title and len(document.title) > 255:
            self.issues.append("Title must be 255 characters or less")
        
        # Type validation
        if not isinstance(document.document_type, DocumentType):
            self.issues.append("Invalid document type")
        
        # Status validation
        if not isinstance(document.status, DocumentStatus):
            self.issues.append("Invalid document status")
        
        # File size validation
        if document.file_size < 0:
            self.issues.append("File size cannot be negative")
        
        if document.file_size > self.MAX_FILE_SIZE:
            self.issues.append(f"File size exceeds maximum ({self.MAX_FILE_SIZE} bytes)")
        
        # MIME type validation
        if document.mime_type and document.mime_type not in self.SUPPORTED_TYPES:
            self.issues.append(f"Unsupported MIME type: {document.mime_type}")
        
        # Version validation
        if document.version < 1:
            self.issues.append("Version must be at least 1")
        
        # Metadata validation
        if document.metadata:
            if not isinstance(document.metadata, dict):
                self.issues.append("Metadata must be a dictionary")
        
        return self.issues.copy()
    
    def validate_file_type(self, mime_type: str) -> List[str]:
        """
        Validate file type.
        
        Args:
            mime_type: MIME type to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not mime_type:
            issues.append("MIME type is required")
        elif mime_type not in self.SUPPORTED_TYPES:
            issues.append(f"Unsupported MIME type: {mime_type}")
        
        return issues
    
    def validate_file_size(self, file_size: int) -> List[str]:
        """
        Validate file size.
        
        Args:
            file_size: File size in bytes
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if file_size < 0:
            issues.append("File size cannot be negative")
        
        if file_size > self.MAX_FILE_SIZE:
            issues.append(f"File size exceeds maximum of {self.MAX_FILE_SIZE} bytes ({self.MAX_FILE_SIZE / (1024*1024):.0f} MB)")
        
        return issues
    
    def validate_duplicate(
        self,
        new_checksum: str,
        existing_checksums: List[str]
    ) -> bool:
        """
        Check for duplicate content.
        
        Args:
            new_checksum: New document checksum
            existing_checksums: List of existing checksums
            
        Returns:
            True if duplicate found
        """
        return new_checksum in existing_checksums
    
    def validate_version_consistency(
        self,
        document_version: int,
        version_count: int
    ) -> List[str]:
        """
        Validate version consistency.
        
        Args:
            document_version: Document's version number
            version_count: Number of version records
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if document_version != version_count + 1:
            issues.append(
                f"Version mismatch: document version {document_version} "
                f"but {version_count} version records exist"
            )
        
        return issues
    
    def validate_metadata(
        self,
        metadata: Dict[str, Any]
    ) -> List[str]:
        """
        Validate document metadata.
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not isinstance(metadata, dict):
            issues.append("Metadata must be a dictionary")
            return issues
        
        # Check for invalid types
        for key, value in metadata.items():
            if isinstance(value, (list, dict)):
                # These are allowed
                pass
            elif not isinstance(value, (str, int, float, bool, type(None))):
                issues.append(f"Invalid metadata type for key '{key}': {type(value)}")
        
        return issues
    
    def validate_attachment(self, attachment: Attachment) -> List[str]:
        """
        Validate an attachment.
        
        Args:
            attachment: Attachment to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not attachment.id:
            issues.append("Attachment ID is required")
        
        if not attachment.document_id:
            issues.append("Document ID is required")
        
        if not attachment.file_name or not attachment.file_name.strip():
            issues.append("File name is required")
        
        if attachment.file_size < 0:
            issues.append("File size cannot be negative")
        
        if attachment.mime_type and attachment.mime_type not in self.SUPPORTED_TYPES:
            issues.append(f"Unsupported MIME type: {attachment.mime_type}")
        
        return issues
    
    def validate_title(self, title: str) -> List[str]:
        """
        Validate document title.
        
        Args:
            title: Title to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not title or not title.strip():
            issues.append("Title is required")
        
        if title and len(title) > 255:
            issues.append("Title must be 255 characters or less")
        
        return issues
    
    def validate_tag(self, tag: str) -> List[str]:
        """
        Validate a document tag.
        
        Args:
            tag: Tag to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not tag or not tag.strip():
            issues.append("Tag is required")
        
        if tag and len(tag) > 100:
            issues.append("Tag must be 100 characters or less")
        
        if tag and not tag.replace("_", "").replace("-", "").isalnum():
            issues.append("Tag must be alphanumeric with optional hyphens/underscores")
        
        return issues
    
    def validate_storage_path(self, path: str) -> List[str]:
        """
        Validate storage path.
        
        Args:
            path: Storage path to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not path:
            issues.append("Storage path is required")
        
        if path and len(path) > 500:
            issues.append("Storage path must be 500 characters or less")
        
        return issues
    
    def validate_asset_linkage(
        self,
        document: Document,
        allowed_asset_ids: List[str]
    ) -> List[str]:
        """
        Validate asset linkage.
        
        Args:
            document: Document
            allowed_asset_ids: List of valid asset IDs
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if document.asset_id and document.asset_id not in allowed_asset_ids:
            issues.append(f"Invalid asset ID: {document.asset_id}")
        
        return issues
    
    def validate_work_order_linkage(
        self,
        document: Document,
        allowed_work_order_ids: List[str]
    ) -> List[str]:
        """
        Validate work order linkage.
        
        Args:
            document: Document
            allowed_work_order_ids: List of valid work order IDs
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if document.work_order_id and document.work_order_id not in allowed_work_order_ids:
            issues.append(f"Invalid work order ID: {document.work_order_id}")
        
        return issues
    
    def get_validation_summary(self) -> Dict:
        """
        Get validation summary.
        
        Returns:
            Summary dictionary
        """
        return {
            "issues": self.issues,
            "issue_count": len(self.issues),
            "has_critical": any("required" in i.lower() for i in self.issues),
        }
