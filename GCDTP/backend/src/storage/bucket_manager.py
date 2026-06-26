"""
Bucket Manager

Manages storage buckets.
"""

import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

from .storage_types import BucketType, BucketStatus


@dataclass
class StorageBucket:
    """Storage bucket."""
    id: str
    name: str
    bucket_type: BucketType
    status: BucketStatus
    description: str = ""
    max_size_bytes: int = 0
    max_object_count: int = 0
    encryption_enabled: bool = False
    version_enabled: bool = True
    owner_organization_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


class BucketManager:
    """
    Manages storage buckets.
    
    Buckets supported:
    - documents
    - attachments
    - images
    - cad
    - bim
    - pointclouds
    - rasters
    - datasets
    - backups
    - temporary
    """
    
    def __init__(self):
        self._buckets: Dict[str, StorageBucket] = {}
        self._initialize_defaults()
    
    def _initialize_defaults(self) -> None:
        """Initialize default buckets."""
        bucket_configs = [
            (BucketType.DOCUMENTS, "gcdtp-documents", "Document storage"),
            (BucketType.ATTACHMENTS, "gcdtp-attachments", "File attachments"),
            (BucketType.IMAGES, "gcdtp-images", "Image storage"),
            (BucketType.CAD, "gcdtp-cad", "CAD files"),
            (BucketType.BIM, "gcdtp-bim", "BIM models"),
            (BucketType.POINTCLOUDS, "gcdtp-pointclouds", "Point cloud data"),
            (BucketType.RASTERS, "gcdtp-rasters", "Raster data"),
            (BucketType.DATASETS, "gcdtp-datasets", "Dataset files"),
            (BucketType.BACKUPS, "gcdtp-backups", "Backup storage"),
            (BucketType.TEMPORARY, "gcdtp-temporary", "Temporary files"),
        ]
        
        for bucket_type, name, description in bucket_configs:
            self.create_bucket(name, bucket_type, description)
    
    def create_bucket(
        self,
        name: str,
        bucket_type: BucketType,
        description: str = "",
        **kwargs
    ) -> StorageBucket:
        """Create a bucket."""
        bucket_id = str(uuid.uuid4())
        
        bucket = StorageBucket(
            id=bucket_id,
            name=name,
            bucket_type=bucket_type,
            status=BucketStatus.ACTIVE,
            description=description,
            **kwargs
        )
        
        self._buckets[bucket_id] = bucket
        return bucket
    
    def get_bucket(self, bucket_id: str) -> Optional[StorageBucket]:
        """Get a bucket."""
        return self._buckets.get(bucket_id)
    
    def get_bucket_by_name(self, name: str) -> Optional[StorageBucket]:
        """Get bucket by name."""
        for bucket in self._buckets.values():
            if bucket.name == name:
                return bucket
        return None
    
    def get_all_buckets(self) -> List[StorageBucket]:
        """Get all buckets."""
        return list(self._buckets.values())
    
    def get_buckets_by_type(self, bucket_type: BucketType) -> List[StorageBucket]:
        """Get buckets by type."""
        return [b for b in self._buckets.values() if b.bucket_type == bucket_type]
    
    def get_active_buckets(self) -> List[StorageBucket]:
        """Get active buckets."""
        return [b for b in self._buckets.values() if b.status == BucketStatus.ACTIVE]
    
    def suspend_bucket(self, bucket_id: str) -> bool:
        """Suspend a bucket."""
        bucket = self._buckets.get(bucket_id)
        if bucket:
            bucket.status = BucketStatus.SUSPENDED
            return True
        return False
    
    def activate_bucket(self, bucket_id: str) -> bool:
        """Activate a bucket."""
        bucket = self._buckets.get(bucket_id)
        if bucket:
            bucket.status = BucketStatus.ACTIVE
            return True
        return False
    
    def archive_bucket(self, bucket_id: str) -> bool:
        """Archive a bucket."""
        bucket = self._buckets.get(bucket_id)
        if bucket:
            bucket.status = BucketStatus.ARCHIVED
            return True
        return False
