"""
Platform Manifest

Manages platform manifests.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ComponentManifest:
    """Component manifest entry."""
    name: str
    key: str
    version: str
    type: str
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class PlatformManifest:
    """Platform manifest."""
    platform_version: str
    platform_name: str
    edition: str
    components: List[ComponentManifest] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict = field(default_factory=dict)


class PlatformManifestManager:
    """
    Manages platform manifests.
    """
    
    def __init__(self):
        self._manifests: Dict[str, PlatformManifest] = {}
    
    def create_manifest(
        self,
        platform_version: str,
        platform_name: str,
        edition: str,
        components: Optional[List[ComponentManifest]] = None
    ) -> PlatformManifest:
        """Create a platform manifest."""
        manifest = PlatformManifest(
            platform_version=platform_version,
            platform_name=platform_name,
            edition=edition,
            components=components or []
        )
        self._manifests[platform_version] = manifest
        return manifest
    
    def get_manifest(self, version: str) -> Optional[PlatformManifest]:
        """Get a manifest."""
        return self._manifests.get(version)
    
    def get_all_manifests(self) -> List[PlatformManifest]:
        """Get all manifests."""
        return list(self._manifests.values())
    
    def add_component(
        self,
        version: str,
        component: ComponentManifest
    ) -> bool:
        """Add component to manifest."""
        manifest = self._manifests.get(version)
        if manifest:
            manifest.components.append(component)
            return True
        return False
    
    def validate_manifest(self, version: str) -> Dict[str, Any]:
        """Validate a manifest."""
        manifest = self._manifests.get(version)
        if not manifest:
            return {"valid": False, "errors": ["Manifest not found"]}
        
        errors = []
        component_keys = set()
        
        for component in manifest.components:
            if component.key in component_keys:
                errors.append(f"Duplicate component key: {component.key}")
            component_keys.add(component.key)
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "component_count": len(manifest.components)
        }
