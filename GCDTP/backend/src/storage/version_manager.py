"""
Version Manager

Manages object versions.
"""

import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ObjectVersion:
    """Object version."""
    id: str
    object_id: str
    version_id: str
    size_bytes: int
    checksum: str
    is_latest: bool
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""


class VersionManager:
    """
    Manages object versions.
    
    Features:
    - Object versioning
    - Version history
    - Version rollback
    - Version comparison
    - Latest version
    """
    
    def __init__(self):
        self._versions: Dict[str, ObjectVersion] = {}
        self._object_versions: Dict[str, List[str]] = {}  # object_id -> version_ids
    
    def create_version(
        self,
        object_id: str,
        version_id: str,
        size_bytes: int,
        checksum: str,
        created_by: str = ""
    ) -> ObjectVersion:
        """Create a new version."""
        version_uuid = str(uuid.uuid4())
        
        # Mark previous latest as not latest
        if object_id in self._object_versions:
            for vid in self._object_versions[object_id]:
                version = self._versions.get(vid)
                if version and version.is_latest:
                    version.is_latest = False
        
        version = ObjectVersion(
            id=version_uuid,
            object_id=object_id,
            version_id=version_id,
            size_bytes=size_bytes,
            checksum=checksum,
            is_latest=True,
            created_by=created_by
        )
        
        self._versions[version_uuid] = version
        
        if object_id not in self._object_versions:
            self._object_versions[object_id] = []
        self._object_versions[object_id].append(version_uuid)
        
        return version
    
    def get_version(self, version_uuid: str) -> Optional[ObjectVersion]:
        """Get a version by UUID."""
        return self._versions.get(version_uuid)
    
    def get_version_by_id(self, object_id: str, version_id: str) -> Optional[ObjectVersion]:
        """Get a version by version ID."""
        version_ids = self._object_versions.get(object_id, [])
        for vid in version_ids:
            version = self._versions.get(vid)
            if version and version.version_id == version_id:
                return version
        return None
    
    def get_versions(self, object_id: str) -> List[ObjectVersion]:
        """Get all versions of an object."""
        version_ids = self._object_versions.get(object_id, [])
        versions = [self._versions[vid] for vid in version_ids if vid in self._versions]
        return sorted(versions, key=lambda v: v.created_at, reverse=True)
    
    def get_latest_version(self, object_id: str) -> Optional[ObjectVersion]:
        """Get the latest version of an object."""
        for version in self.get_versions(object_id):
            if version.is_latest:
                return version
        return None
    
    def rollback_to_version(self, object_id: str, version_id: str) -> bool:
        """Rollback to a specific version."""
        target_version = self.get_version_by_id(object_id, version_id)
        if not target_version:
            return False
        
        # Mark all versions as not latest
        for version in self.get_versions(object_id):
            version.is_latest = False
        
        # Mark target as latest
        target_version.is_latest = True
        return True
    
    def compare_versions(
        self,
        object_id: str,
        version_id_1: str,
        version_id_2: str
    ) -> Dict[str, Any]:
        """Compare two versions."""
        v1 = self.get_version_by_id(object_id, version_id_1)
        v2 = self.get_version_by_id(object_id, version_id_2)
        
        if not v1 or not v2:
            return {"error": "Version not found"}
        
        return {
            "version_1": {
                "version_id": v1.version_id,
                "size_bytes": v1.size_bytes,
                "checksum": v1.checksum,
                "created_at": v1.created_at.isoformat()
            },
            "version_2": {
                "version_id": v2.version_id,
                "size_bytes": v2.size_bytes,
                "checksum": v2.checksum,
                "created_at": v2.created_at.isoformat()
            },
            "size_diff": v2.size_bytes - v1.size_bytes,
            "checksum_match": v1.checksum == v2.checksum
        }
