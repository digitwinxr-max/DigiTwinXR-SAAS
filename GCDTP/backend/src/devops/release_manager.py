"""
Release Manager

Manages releases and versioning.
"""

import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Release:
    """Release version."""
    version: str
    name: str
    changelog: str = ""
    migration_version: int = 0
    rollback_version: Optional[str] = None
    compatibility_matrix: Dict = field(default_factory=dict)
    is_stable: bool = False
    released_at: Optional[datetime] = None
    released_by: str = ""


class ReleaseManager:
    """
    Manages releases.
    
    Tracks:
    - Release versions
    - Changelogs
    - Migration versions
    - Rollback information
    - Compatibility matrix
    """
    
    def __init__(self):
        self._releases: Dict[str, Release] = {}
        self._current_version: Optional[str] = None
    
    def create_release(
        self,
        version: str,
        name: str,
        changelog: str = "",
        migration_version: int = 0,
        compatibility_matrix: Optional[Dict] = None
    ) -> Release:
        """Create a release."""
        release = Release(
            version=version,
            name=name,
            changelog=changelog,
            migration_version=migration_version,
            compatibility_matrix=compatibility_matrix or {}
        )
        self._releases[version] = release
        return release
    
    def get_release(self, version: str) -> Optional[Release]:
        """Get a release."""
        return self._releases.get(version)
    
    def get_all_releases(self) -> List[Release]:
        """Get all releases."""
        return sorted(
            list(self._releases.values()),
            key=lambda r: r.version,
            reverse=True
        )
    
    def get_stable_releases(self) -> List[Release]:
        """Get stable releases."""
        return [r for r in self._releases.values() if r.is_stable]
    
    def mark_stable(self, version: str) -> bool:
        """Mark a release as stable."""
        release = self._releases.get(version)
        if release:
            release.is_stable = True
            return True
        return False
    
    def set_current_version(self, version: str) -> bool:
        """Set current version."""
        if version in self._releases:
            self._current_version = version
            return True
        return False
    
    def get_current_version(self) -> Optional[str]:
        """Get current version."""
        return self._current_version
    
    def set_rollback_version(self, version: str, rollback_to: str) -> bool:
        """Set rollback version for a release."""
        release = self._releases.get(version)
        if release:
            release.rollback_version = rollback_to
            return True
        return False
    
    def record_release(
        self,
        version: str,
        released_by: str
    ) -> bool:
        """Record a release as deployed."""
        release = self._releases.get(version)
        if release:
            release.released_at = datetime.utcnow()
            release.released_by = released_by
            return True
        return False
    
    def get_recent_releases(self, limit: int = 10) -> List[Release]:
        """Get recent releases."""
        releases = sorted(
            [r for r in self._releases.values() if r.released_at],
            key=lambda r: r.released_at or datetime.min,
            reverse=True
        )
        return releases[:limit]
    
    def get_compatibility(self, version: str) -> Dict:
        """Get compatibility matrix for a version."""
        release = self._releases.get(version)
        return release.compatibility_matrix if release else {}
    
    def is_compatible(
        self,
        version1: str,
        version2: str
    ) -> bool:
        """Check if two versions are compatible."""
        release1 = self._releases.get(version1)
        release2 = self._releases.get(version2)
        
        if not release1 or not release2:
            return False
        
        return release1.version in release2.compatibility_matrix.get(version2, [])
