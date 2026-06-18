"""
Platform Module

Provides enterprise packaging capabilities:
- Platform manifests
- Component catalog
- Bundle management
- Installation management
- Upgrade management
- Compatibility management
- License management
- Platform registry
- Release bundle management

Components:
- PlatformManifestManager
- ComponentCatalog
- BundleManager
- InstallationManager
- UpgradeManager
- CompatibilityManager
- LicenseManager
- PlatformRegistry
- ReleaseBundleManager
"""

from .platform_manifest import (
    PlatformManifestManager,
    PlatformManifest,
    ComponentManifest
)
from .component_catalog import (
    ComponentCatalog,
    ComponentType,
    ComponentStatus,
    CatalogEntry
)
from .edition_manager import (
    EditionManager,
    EditionType,
    PlatformEdition
)
from .bundle_manager import BundleManager, BundleType, Bundle
from .installation_manager import (
    InstallationManager,
    InstallationProfile,
    Installation
)
from .upgrade_manager import (
    UpgradeManager,
    UpgradeStatus,
    UpgradeType,
    Upgrade
)
from .compatibility_manager import CompatibilityManager
from .license_manager import (
    LicenseManager,
    LicenseType,
    LicenseMetadata
)
from .platform_registry import (
    PlatformRegistry,
    ModuleStatus,
    ModuleEntry
)
from .release_bundle_manager import (
    ReleaseBundleManager,
    ReleaseBundle
)
from .package_validator import PackageValidator


__all__ = [
    # Manifest
    "PlatformManifestManager",
    "PlatformManifest",
    "ComponentManifest",
    # Catalog
    "ComponentCatalog",
    "ComponentType",
    "ComponentStatus",
    "CatalogEntry",
    # Edition
    "EditionManager",
    "EditionType",
    "PlatformEdition",
    # Bundle
    "BundleManager",
    "BundleType",
    "Bundle",
    # Installation
    "InstallationManager",
    "InstallationProfile",
    "Installation",
    # Upgrade
    "UpgradeManager",
    "UpgradeStatus",
    "UpgradeType",
    "Upgrade",
    # Compatibility
    "CompatibilityManager",
    # License
    "LicenseManager",
    "LicenseType",
    "LicenseMetadata",
    # Registry
    "PlatformRegistry",
    "ModuleStatus",
    "ModuleEntry",
    # Release Bundle
    "ReleaseBundleManager",
    "ReleaseBundle",
    # Validation
    "PackageValidator",
]
