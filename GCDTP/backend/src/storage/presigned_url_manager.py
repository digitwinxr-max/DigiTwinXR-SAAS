"""
Presigned URL Manager

Manages presigned URLs for temporary access.
"""

import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class PresignedURL:
    """Presigned URL."""
    id: str
    url: str
    object_key: str
    bucket_name: str
    expires_at: datetime
    permissions: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)


class PresignedURLManager:
    """
    Manages presigned URLs.
    
    Features:
    - Temporary access URLs
    - Download URLs
    - Upload URLs
    - Expiration
    - Permissions
    """
    
    def __init__(self):
        self._urls: Dict[str, PresignedURL] = {}
    
    def create_download_url(
        self,
        object_key: str,
        bucket_name: str,
        expiry_seconds: int = 3600,
        permissions: Optional[List[str]] = None
    ) -> PresignedURL:
        """Create a presigned download URL."""
        url_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(seconds=expiry_seconds)
        
        url = f"https://minio.example.com/{bucket_name}/{object_key}?token={url_id}"
        
        presigned = PresignedURL(
            id=url_id,
            url=url,
            object_key=object_key,
            bucket_name=bucket_name,
            expires_at=expires_at,
            permissions=permissions or ["read"]
        )
        
        self._urls[url_id] = presigned
        return presigned
    
    def create_upload_url(
        self,
        object_key: str,
        bucket_name: str,
        expiry_seconds: int = 3600,
        permissions: Optional[List[str]] = None
    ) -> PresignedURL:
        """Create a presigned upload URL."""
        url_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(seconds=expiry_seconds)
        
        url = f"https://minio.example.com/{bucket_name}/{object_key}?token={url_id}&action=upload"
        
        presigned = PresignedURL(
            id=url_id,
            url=url,
            object_key=object_key,
            bucket_name=bucket_name,
            expires_at=expires_at,
            permissions=permissions or ["write"]
        )
        
        self._urls[url_id] = presigned
        return presigned
    
    def get_url(self, url_id: str) -> Optional[PresignedURL]:
        """Get a presigned URL."""
        return self._urls.get(url_id)
    
    def is_valid(self, url_id: str) -> bool:
        """Check if a presigned URL is still valid."""
        url = self._urls.get(url_id)
        if not url:
            return False
        
        return datetime.utcnow() < url.expires_at
    
    def revoke_url(self, url_id: str) -> bool:
        """Revoke a presigned URL."""
        if url_id in self._urls:
            del self._urls[url_id]
            return True
        return False
    
    def cleanup_expired(self) -> int:
        """Clean up expired URLs."""
        now = datetime.utcnow()
        expired = [
            url_id for url_id, url in self._urls.items()
            if now >= url.expires_at
        ]
        
        for url_id in expired:
            del self._urls[url_id]
        
        return len(expired)
