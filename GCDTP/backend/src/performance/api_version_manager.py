"""
API Version Manager

Provides API versioning support.
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, date


class APIVersionStatus(str):
    """API version status."""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"


@dataclass
class APIVersion:
    """API version definition."""
    version: str
    display_name: str
    status: APIVersionStatus
    release_date: date
    sunset_date: Optional[date] = None
    migration_guide: Optional[str] = None
    is_default: bool = False


@dataclass
class VersionNegotiationResult:
    """Version negotiation result."""
    negotiated_version: str
    is_supported: bool
    is_deprecated: bool
    sunset_date: Optional[date] = None
    deprecation_message: Optional[str] = None


class APIVersionManager:
    """
    Provides API versioning support.
    
    Supports:
    - v1
    - Future v2 compatibility
    - Version negotiation
    - Backward compatibility
    - Deprecation metadata
    """
    
    def __init__(self):
        self._versions: Dict[str, APIVersion] = {}
        self._default_version = "v1"
        self._initialize_default_versions()
    
    def _initialize_default_versions(self) -> None:
        """Initialize default API versions."""
        self.register_version(APIVersion(
            version="v1",
            display_name="API v1",
            status=APIVersionStatus.ACTIVE,
            release_date=date(2026, 1, 1),
            is_default=True
        ))
    
    def register_version(self, version: APIVersion) -> None:
        """Register an API version."""
        if version.is_default:
            # Unset other defaults
            for v in self._versions.values():
                v.is_default = False
        
        self._versions[version.version] = version
    
    def get_version(self, version: str) -> Optional[APIVersion]:
        """Get an API version."""
        return self._versions.get(version)
    
    def get_all_versions(self) -> List[APIVersion]:
        """Get all API versions."""
        return list(self._versions.values())
    
    def get_active_versions(self) -> List[APIVersion]:
        """Get active API versions."""
        return [v for v in self._versions.values() if v.status == APIVersionStatus.ACTIVE]
    
    def get_default_version(self) -> APIVersion:
        """Get the default API version."""
        for v in self._versions.values():
            if v.is_default:
                return v
        return self._versions[self._default_version]
    
    def negotiate_version(
        self,
        accept_header: Optional[str] = None,
        requested_version: Optional[str] = None
    ) -> VersionNegotiationResult:
        """
        Negotiate API version.
        
        Args:
            accept_header: Accept header (e.g., "application/vnd.gcdtp.v2+json")
            requested_version: Explicitly requested version
            
        Returns:
            VersionNegotiationResult
        """
        version = None
        
        # Parse from Accept header
        if accept_header:
            version = self._parse_accept_header(accept_header)
        
        # Use explicit version if provided
        if requested_version:
            version = requested_version
        
        # Use default if none specified
        if not version:
            default = self.get_default_version()
            return VersionNegotiationResult(
                negotiated_version=default.version,
                is_supported=True,
                is_deprecated=False
            )
        
        # Check if version exists
        api_version = self._versions.get(version)
        if not api_version:
            # Try to find compatible version
            for v in self._versions.values():
                if v.version.startswith(version.rstrip("0123456789")):
                    api_version = v
                    break
        
        if not api_version:
            default = self.get_default_version()
            return VersionNegotiationResult(
                negotiated_version=default.version,
                is_supported=False,
                is_deprecated=False,
                deprecation_message=f"Version '{version}' not found, using default"
            )
        
        # Check status
        is_deprecated = api_version.status == APIVersionStatus.DEPRECATED
        deprecation_msg = None
        
        if is_deprecated:
            deprecation_msg = f"Version '{api_version.version}' is deprecated"
            if api_version.sunset_date:
                deprecation_msg += f". Sunset date: {api_version.sunset_date}"
        
        return VersionNegotiationResult(
            negotiated_version=api_version.version,
            is_supported=True,
            is_deprecated=is_deprecated,
            sunset_date=api_version.sunset_date,
            deprecation_message=deprecation_msg
        )
    
    def _parse_accept_header(self, header: str) -> Optional[str]:
        """Parse Accept header for version."""
        # Match patterns like:
        # application/vnd.gcdtp.v2+json
        # application/vnd.gcdtp-v2+json
        patterns = [
            r'vnd\.gcdtp\.v(\d+)',
            r'vnd-gcdtp-v(\d+)',
            r'gcdtp-v(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, header)
            if match:
                return f"v{match.group(1)}"
        
        return None
    
    def deprecate_version(
        self,
        version: str,
        sunset_date: date,
        migration_guide: str
    ) -> bool:
        """Deprecate an API version."""
        api_version = self._versions.get(version)
        if not api_version:
            return False
        
        api_version.status = APIVersionStatus.DEPRECATED
        api_version.sunset_date = sunset_date
        api_version.migration_guide = migration_guide
        return True
    
    def sunset_version(self, version: str) -> bool:
        """Sunset an API version."""
        api_version = self._versions.get(version)
        if not api_version:
            return False
        
        api_version.status = APIVersionStatus.SUNSET
        return True
    
    def is_version_active(self, version: str) -> bool:
        """Check if a version is active."""
        api_version = self._versions.get(version)
        return api_version is not None and api_version.status == APIVersionStatus.ACTIVE
    
    def is_version_supported(self, version: str) -> bool:
        """Check if a version is supported."""
        return version in self._versions
    
    def get_version_header(self, version: str) -> Dict[str, str]:
        """Get headers for a version."""
        api_version = self._versions.get(version)
        if not api_version:
            return {}
        
        headers = {
            "API-Version": version
        }
        
        if api_version.status == APIVersionStatus.DEPRECATED:
            headers["Deprecation"] = f"version '{version}'"
            if api_version.sunset_date:
                headers["Sunset"] = api_version.sunset_date.isoformat()
        
        return headers
