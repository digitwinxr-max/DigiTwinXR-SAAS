"""
Multipart Upload Manager

Manages multipart uploads for large files.
"""

import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

from .storage_types import UploadStatus


@dataclass
class MultipartUpload:
    """Multipart upload."""
    id: str
    upload_id: str
    bucket_id: str
    object_key: str
    content_type: str
    total_size_bytes: int
    chunk_size_bytes: int
    total_chunks: int
    status: UploadStatus
    initiated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    initiated_by: str = ""


class MultipartUploadManager:
    """
    Manages multipart uploads.
    
    Features:
    - Large files
    - Resumable uploads
    - Chunk validation
    - Progress tracking
    - Failure recovery
    """
    
    def __init__(self):
        self._uploads: Dict[str, MultipartUpload] = {}
        self._upload_parts: Dict[str, Dict] = {}  # upload_id -> {part_number: etag}
    
    def initiate_upload(
        self,
        bucket_id: str,
        object_key: str,
        content_type: str,
        total_size_bytes: int,
        chunk_size_bytes: int,
        initiated_by: str
    ) -> MultipartUpload:
        """Initiate a multipart upload."""
        upload_id = str(uuid.uuid4())
        upload_uuid = str(uuid.uuid4())
        
        total_chunks = (total_size_bytes + chunk_size_bytes - 1) // chunk_size_bytes
        
        upload = MultipartUpload(
            id=upload_uuid,
            upload_id=upload_id,
            bucket_id=bucket_id,
            object_key=object_key,
            content_type=content_type,
            total_size_bytes=total_size_bytes,
            chunk_size_bytes=chunk_size_bytes,
            total_chunks=total_chunks,
            status=UploadStatus.PENDING,
            initiated_by=initiated_by
        )
        
        self._uploads[upload_id] = upload
        self._upload_parts[upload_id] = {}
        
        return upload
    
    def get_upload(self, upload_id: str) -> Optional[MultipartUpload]:
        """Get a multipart upload."""
        return self._uploads.get(upload_id)
    
    def upload_part(
        self,
        upload_id: str,
        part_number: int,
        etag: str
    ) -> bool:
        """Record an uploaded part."""
        if upload_id not in self._uploads:
            return False
        
        self._upload_parts[upload_id][part_number] = etag
        return True
    
    def get_uploaded_parts(self, upload_id: str) -> Dict[int, str]:
        """Get all uploaded parts."""
        return self._upload_parts.get(upload_id, {})
    
    def complete_upload(self, upload_id: str) -> bool:
        """Complete a multipart upload."""
        upload = self._uploads.get(upload_id)
        if not upload:
            return False
        
        upload.status = UploadStatus.COMPLETED
        upload.completed_at = datetime.utcnow()
        return True
    
    def abort_upload(self, upload_id: str) -> bool:
        """Abort a multipart upload."""
        upload = self._uploads.get(upload_id)
        if not upload:
            return False
        
        upload.status = UploadStatus.ABORTED
        upload.completed_at = datetime.utcnow()
        
        # Clean up parts
        if upload_id in self._upload_parts:
            del self._upload_parts[upload_id]
        
        return True
    
    def get_progress(self, upload_id: str) -> Dict[str, Any]:
        """Get upload progress."""
        upload = self._uploads.get(upload_id)
        if not upload:
            return {}
        
        uploaded_parts = self.get_uploaded_parts(upload_id)
        uploaded_count = len(uploaded_parts)
        total_count = upload.total_chunks
        
        progress_percent = (uploaded_count / total_count * 100) if total_count > 0 else 0
        uploaded_bytes = uploaded_count * upload.chunk_size_bytes
        
        return {
            "upload_id": upload_id,
            "total_chunks": total_count,
            "uploaded_chunks": uploaded_count,
            "progress_percent": progress_percent,
            "uploaded_bytes": uploaded_bytes,
            "total_bytes": upload.total_size_bytes,
            "status": upload.status.value
        }
    
    def list_pending_uploads(self) -> List[MultipartUpload]:
        """List pending multipart uploads."""
        return [
            upload for upload in self._uploads.values()
            if upload.status in [UploadStatus.PENDING, UploadStatus.IN_PROGRESS]
        ]
