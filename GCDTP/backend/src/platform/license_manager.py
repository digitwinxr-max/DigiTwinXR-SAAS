"""
License Manager

Manages license metadata (no enforcement).
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, date


class LicenseType(str):
    """License types."""
    TRIAL = "trial"
    STANDARD = "standard"
    ENTERPRISE = "enterprise"


@dataclass
class LicenseMetadata:
    """License metadata (no enforcement)."""
    key: str
    license_type: LicenseType
    edition: str
    issued_to: str
    organizations: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    max_users: int = 0
    max_assets: int = 0
    expiry_date: Optional[date] = None
    issued_at: date = None
    
    def __post_init__(self):
        if self.issued_at is None:
            self.issued_at = date.today()


class LicenseManager:
    """
    Manages license metadata.
    
    Note: No enforcement logic - metadata only.
    """
    
    def __init__(self):
        self._licenses: Dict[str, LicenseMetadata] = {}
    
    def register_license(
        self,
        key: str,
        license_type: LicenseType,
        edition: str,
        issued_to: str,
        **kwargs
    ) -> LicenseMetadata:
        """Register a license."""
        license = LicenseMetadata(
            key=key,
            license_type=license_type,
            edition=edition,
            issued_to=issued_to,
            **kwargs
        )
        self._licenses[key] = license
        return license
    
    def get_license(self, key: str) -> Optional[LicenseMetadata]:
        """Get license metadata."""
        return self._licenses.get(key)
    
    def get_all_licenses(self) -> List[LicenseMetadata]:
        """Get all licenses."""
        return list(self._licenses.values())
    
    def get_licenses_by_type(self, license_type: LicenseType) -> List[LicenseMetadata]:
        """Get licenses by type."""
        return [l for l in self._licenses.values() if l.license_type == license_type]
    
    def get_licenses_by_edition(self, edition: str) -> List[LicenseMetadata]:
        """Get licenses by edition."""
        return [l for l in self._licenses.values() if l.edition == edition]
    
    def is_expired(self, key: str) -> bool:
        """Check if license is expired."""
        license = self._licenses.get(key)
        if not license or not license.expiry_date:
            return False
        return license.expiry_date < date.today()
