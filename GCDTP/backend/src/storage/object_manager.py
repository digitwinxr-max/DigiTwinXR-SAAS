"""
Object Manager

Manages stored objects.
"""

import uuid
from typing import Dict, List, Optional, Any, BinaryIO
from dataclasses import dataclass, field
from datetime import datetime

from .storage_types import ObjectStatus, ChecksumAlgorithm


@dataclass
class StoredObject:
    """Stored object."""
    id: str
    bucket_id: str
    object_key: str
    version_id: str
    content_type: str
    size_bytes: int
    checksum: str
    checksum_algorithm: ChecksumAlgorithm
    status: ObjectStatus
    is_latest: bool
    owner_user_id: str
    owner_organization_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None


class ObjectManager:
    """
    Manages stored objects.
    
    Operations:
    - upload
    - download
    - copy
    - move
    - delete
    - soft delete
    - restore
    - checksum validation
    """
    
    def __init__(self):
        self._objects: Dict[str, StoredObject] = {}
        self._key_index: Dict[str, str] = {}  # bucket:key -> object_id
    
    def create_object(
        self,
        bucket_id: str,
        object_key: str,
        content_type: str,
        size_bytes: int,
        checksum: str,
        owner_user_id: str,
        owner_organization_id: str
    ) -> StoredObject:
        """Create an object record."""
        object_id = str(uuid.uuid4())
        version_id = str(uuid.uuid4())
        
        # Mark previous versions as not latest
        index_key = f"{bucket_id}:{object_key}"
        if index_key in self._key_index:
            prev_id = self._key_index[index_key]
            if prev_id in self._objects:
                self._objects[prev_id].is_latest = False
        
        obj = StoredObject(
            id=object_id,
            bucket_id=bucket_id,
            object_key=object_key,
            version_id=version_id,
            content_type=content_type,
            size_bytes=size_bytes,
            checksum=checksum,
            checksum_algorithm=ChecksumAlgorithm.SHA256,
            status=ObjectStatus.AVAILABLE,
            is_latest=True,
            owner_user_id=owner_user_id,
            owner_organization_id=owner_organization_id
        )
        
        self._objects[object_id] = obj
        self._key_index[index_key] = object_id
        return obj
    
    def get_object(self, object_id: str) -> Optional[StoredObject]:
        """Get an object."""
        return self._objects.get(object_id)
    
    def get_object_by_key(self, bucket_id: str, object_key: str) -> Optional[StoredObject]:
        """Get object by bucket and key."""
        index_key = f"{bucket_id}:{object_key}"
        object_id = self._key_index.get(index_key)
        if object_id:
            return self._objects.get(object_id)
        return None
    
    def get_latest_version(self, bucket_id: str, object_key: str) -> Optional[StoredObject]:
        """Get latest version of an object."""
        obj = self.get_object_by_key(bucket_id, object_key)
        if obj and obj.is_latest:
            return obj
        return None
    
    def list_objects(self, bucket_id: str) -> List[StoredObject]:
        """List objects in a bucket."""
        return [
            obj for obj in self._objects.values()
            if obj.bucket_id == bucket_id and obj.is_latest and obj.status == ObjectStatus.AVAILABLE
        ]
    
    def soft_delete(self, object_id: str) -> bool:
        """Soft delete an object."""
        obj = self._objects.get(object_id)
        if obj:
            obj.status = ObjectStatus.DELETED
            obj.deleted_at = datetime.utcnow()
            return True
        return False
    
    def restore(self, object_id: str) -> bool:
        """Restore a soft-deleted object."""
        obj = self._objects.get(object_id)
        if obj and obj.status == ObjectStatus.DELETED:
            obj.status = ObjectStatus.AVAILABLE
            obj.deleted_at = None
            return True
        return False
    
    def permanent_delete(self, object_id: str) -> bool:
        """Permanently delete an object."""
        obj = self._objects.get(object_id)
        if obj:
            index_key = f"{obj.bucket_id}:{obj.object_key}"
            if index_key in self._key_index:
                del self._key_index[index_key]
            del self._objects[object_id]
            return True
        return False
    
    def validate_checksum(self, object_id: str, expected_checksum: str) -> bool:
        """Validate object checksum."""
        obj = self._objects.get(object_id)
        if obj:
            return obj.checksum == expected_checksum
        return False
