"""
Release Bundle Manager

Manages release bundles.
"""

import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ReleaseBundle:
    """Release bundle."""
    version: str
    bundle_type: str
    bundle_path: str
    size_bytes: int = 0
    checksum: str = ""
    components: List[str] = field(default_factory=list)
    included_editions: List[str] = field(default_factory=list)
    is_stable: bool = False
    released_at: Optional[datetime] = None


class ReleaseBundleManager:
    """
    Manages release bundles.
    """
    
    def __init__(self):
        self._bundles: Dict[str, ReleaseBundle] = {}
    
    def create_bundle(
        self,
        version: str,
        bundle_type: str,
        bundle_path: str,
        components: Optional[List[str]] = None,
        included_editions: Optional[List[str]] = None
    ) -> ReleaseBundle:
        """Create a release bundle."""
        bundle = ReleaseBundle(
            version=version,
            bundle_type=bundle_type,
            bundle_path=bundle_path,
            components=components or [],
            included_editions=included_editions or []
        )
        self._bundles[version] = bundle
        return bundle
    
    def get_bundle(self, version: str) -> Optional[ReleaseBundle]:
        """Get a bundle."""
        return self._bundles.get(version)
    
    def get_all_bundles(self) -> List[ReleaseBundle]:
        """Get all bundles."""
        return list(self._bundles.values())
    
    def get_stable_bundles(self) -> List[ReleaseBundle]:
        """Get stable bundles."""
        return [b for b in self._bundles.values() if b.is_stable]
    
    def mark_stable(self, version: str) -> bool:
        """Mark bundle as stable."""
        bundle = self._bundles.get(version)
        if bundle:
            bundle.is_stable = True
            bundle.released_at = datetime.utcnow()
            return True
        return False
    
    def update_bundle_info(
        self,
        version: str,
        size_bytes: int,
        checksum: str
    ) -> bool:
        """Update bundle info."""
        bundle = self._bundles.get(version)
        if bundle:
            bundle.size_bytes = size_bytes
            bundle.checksum = checksum
            return True
        return False
