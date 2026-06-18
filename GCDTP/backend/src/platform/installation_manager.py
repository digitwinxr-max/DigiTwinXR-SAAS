"""
Installation Manager

Manages platform installations.
"""

import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


class InstallationProfile(str):
    """Installation profile types."""
    MINIMAL = "minimal"
    STANDARD = "standard"
    ENTERPRISE = "enterprise"
    FULL = "full"


@dataclass
class Installation:
    """Platform installation."""
    id: str
    profile: InstallationProfile
    components: List[str]
    version: str
    installed_at: datetime = field(default_factory=datetime.utcnow)


class InstallationManager:
    """
    Manages platform installations.
    
    Profiles:
    - Minimal
    - Standard
    - Enterprise
    - Full
    """
    
    def __init__(self):
        self._installations: Dict[str, Installation] = {}
        self._profiles: Dict[InstallationProfile, Dict] = {
            InstallationProfile.MINIMAL: {
                "components": ["api", "database"],
                "description": "Minimal installation"
            },
            InstallationProfile.STANDARD: {
                "components": ["api", "database", "eventbus"],
                "description": "Standard installation"
            },
            InstallationProfile.ENTERPRISE: {
                "components": ["api", "database", "eventbus", "geoserver", "neo4j"],
                "description": "Enterprise installation"
            },
            InstallationProfile.FULL: {
                "components": ["api", "database", "eventbus", "geoserver", "neo4j", "emqx", "nodered"],
                "description": "Full installation"
            }
        }
    
    def create_installation(
        self,
        profile: InstallationProfile,
        version: str,
        components: Optional[List[str]] = None
    ) -> Installation:
        """Create an installation."""
        inst_id = str(uuid.uuid4())
        
        if components is None:
            components = self._profiles.get(profile, {}).get("components", [])
        
        installation = Installation(
            id=inst_id,
            profile=profile,
            components=components,
            version=version
        )
        
        self._installations[inst_id] = installation
        return installation
    
    def get_installation(self, inst_id: str) -> Optional[Installation]:
        """Get an installation."""
        return self._installations.get(inst_id)
    
    def get_all_installations(self) -> List[Installation]:
        """Get all installations."""
        return list(self._installations.values())
    
    def get_profile_components(self, profile: InstallationProfile) -> List[str]:
        """Get components for a profile."""
        return self._profiles.get(profile, {}).get("components", [])
    
    def validate_components(self, components: List[str]) -> Dict[str, Any]:
        """Validate component dependencies."""
        errors = []
        warnings = []
        
        # Check for required dependencies
        if "geoserver" in components and "database" not in components:
            errors.append("GeoServer requires database")
        
        if "neo4j" in components and "database" not in components:
            warnings.append("Neo4j recommends database")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
