"""
Bundle Manager

Manages deployment bundles.
"""

import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


class BundleType(str):
    """Bundle types."""
    DOCKER = "docker"
    OFFLINE = "offline"
    ENTERPRISE = "enterprise"
    UPGRADE = "upgrade"
    BACKUP = "backup"


@dataclass
class Bundle:
    """Deployment bundle."""
    name: str
    key: str
    bundle_type: BundleType
    version: str
    description: str = ""
    components: List[str] = field(default_factory=list)
    size_bytes: int = 0


class BundleManager:
    """
    Manages deployment bundles.
    """
    
    def __init__(self):
        self._bundles: Dict[str, Bundle] = {}
        self._initialize_defaults()
    
    def _initialize_defaults(self) -> None:
        """Initialize default bundles."""
        self.create_bundle(
            name="Docker Bundle",
            key="docker-bundle",
            bundle_type=BundleType.DOCKER,
            version="1.0.0",
            components=["docker-compose.yml", "Dockerfile"]
        )
        
        self.create_bundle(
            name="Offline Bundle",
            key="offline-bundle",
            bundle_type=BundleType.OFFLINE,
            version="1.0.0",
            components=["docker-compose.yml", "Dockerfile", "config"]
        )
    
    def create_bundle(
        self,
        name: str,
        key: str,
        bundle_type: BundleType,
        version: str,
        description: str = "",
        components: Optional[List[str]] = None
    ) -> Bundle:
        """Create a bundle."""
        bundle = Bundle(
            name=name,
            key=key,
            bundle_type=bundle_type,
            version=version,
            description=description,
            components=components or []
        )
        self._bundles[key] = bundle
        return bundle
    
    def get_bundle(self, key: str) -> Optional[Bundle]:
        """Get a bundle."""
        return self._bundles.get(key)
    
    def get_all_bundles(self) -> List[Bundle]:
        """Get all bundles."""
        return list(self._bundles.values())
    
    def get_bundles_by_type(self, bundle_type: BundleType) -> List[Bundle]:
        """Get bundles by type."""
        return [b for b in self._bundles.values() if b.bundle_type == bundle_type]
