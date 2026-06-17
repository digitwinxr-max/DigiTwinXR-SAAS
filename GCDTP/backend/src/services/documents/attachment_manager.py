"""
Attachment Manager

Manages file attachments and storage for documents.
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from backend.src.services.documents.document_types import Attachment


class AttachmentManager:
    """
    Manages document attachments and files.
    
    Responsibilities:
    - Store attachment metadata
    - Track file locations
    - Manage primary attachments
    - Handle file operations
    """
    
    def __init__(self):
        self._attachments: Dict[str, List[Attachment]] = {}
    
    def add_attachment(
        self,
        document_id: str,
        file_name: str,
        mime_type: str = "",
        file_size: int = 0,
        storage_path: str = "",
        is_primary: bool = False
    ) -> Attachment:
        """
        Add an attachment to a document.
        
        Args:
            document_id: Parent document ID
            file_name: Attachment file name
            mime_type: MIME type
            file_size: File size in bytes
            storage_path: Storage location
            is_primary: Is primary attachment
            
        Returns:
            Created Attachment
        """
        attachment = Attachment(
            id=str(uuid.uuid4()),
            document_id=document_id,
            file_name=file_name,
            mime_type=mime_type,
            file_size=file_size,
            storage_path=storage_path,
            is_primary=is_primary
        )
        
        if document_id not in self._attachments:
            self._attachments[document_id] = []
        
        # If this is primary, unset other primaries
        if is_primary:
            for att in self._attachments[document_id]:
                att.is_primary = False
        
        self._attachments[document_id].append(attachment)
        
        return attachment
    
    def remove_attachment(
        self,
        document_id: str,
        attachment_id: str
    ) -> bool:
        """
        Remove an attachment.
        
        Args:
            document_id: Parent document ID
            attachment_id: Attachment ID
            
        Returns:
            True if removed
        """
        if document_id not in self._attachments:
            return False
        
        attachments = self._attachments[document_id]
        
        for i, att in enumerate(attachments):
            if att.id == attachment_id:
                attachments.pop(i)
                return True
        
        return False
    
    def get_attachments(self, document_id: str) -> List[Attachment]:
        """Get all attachments for a document."""
        return self._attachments.get(document_id, [])
    
    def get_primary_attachment(self, document_id: str) -> Optional[Attachment]:
        """Get primary attachment for a document."""
        attachments = self._attachments.get(document_id, [])
        
        for att in attachments:
            if att.is_primary:
                return att
        
        # Return first if no primary
        return attachments[0] if attachments else None
    
    def set_primary_attachment(
        self,
        document_id: str,
        attachment_id: str
    ) -> bool:
        """
        Set an attachment as primary.
        
        Args:
            document_id: Parent document ID
            attachment_id: Attachment ID
            
        Returns:
            True if set
        """
        if document_id not in self._attachments:
            return False
        
        attachments = self._attachments[document_id]
        
        for att in attachments:
            att.is_primary = (att.id == attachment_id)
        
        return True
    
    def get_total_size(self, document_id: str) -> int:
        """Get total size of all attachments."""
        attachments = self._attachments.get(document_id, [])
        return sum(att.file_size for att in attachments)
    
    def get_attachment_count(self, document_id: str) -> int:
        """Get count of attachments."""
        return len(self._attachments.get(document_id, []))
    
    def clear_attachments(self, document_id: str) -> None:
        """Remove all attachments for a document."""
        if document_id in self._attachments:
            del self._attachments[document_id]
    
    def format_file_size(self, size: int) -> str:
        """
        Format file size as human-readable string.
        
        Args:
            size: Size in bytes
            
        Returns:
            Formatted string
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        
        return f"{size:.1f} PB"
    
    def get_supported_mime_types(self) -> Dict[str, str]:
        """Get supported MIME types with descriptions."""
        return {
            "application/pdf": "PDF Document",
            "image/png": "PNG Image",
            "image/jpeg": "JPEG Image",
            "image/gif": "GIF Image",
            "image/svg+xml": "SVG Image",
            "application/msword": "Word Document",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "Word Document",
            "application/vnd.ms-excel": "Excel Spreadsheet",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "Excel Spreadsheet",
            "application/vnd.ms-powerpoint": "PowerPoint Presentation",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": "PowerPoint",
            "text/plain": "Text File",
            "text/csv": "CSV File",
            "application/zip": "ZIP Archive",
            "video/mp4": "MP4 Video",
            "video/x-msvideo": "AVI Video",
        }
    
    def is_supported_type(self, mime_type: str) -> bool:
        """Check if MIME type is supported."""
        supported = self.get_supported_mime_types()
        return mime_type in supported
    
    def get_type_from_extension(self, filename: str) -> str:
        """
        Get MIME type from file extension.
        
        Args:
            filename: File name
            
        Returns:
            MIME type
        """
        extension_map = {
            ".pdf": "application/pdf",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xls": "application/vnd.ms-excel",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".ppt": "application/vnd.ms-powerpoint",
            ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            ".txt": "text/plain",
            ".csv": "text/csv",
            ".zip": "application/zip",
            ".mp4": "video/mp4",
            ".avi": "video/x-msvideo",
        }
        
        import os
        _, ext = os.path.splitext(filename.lower())
        return extension_map.get(ext, "application/octet-stream")
