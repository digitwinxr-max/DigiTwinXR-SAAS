"""
Tests for Platform Module

Tests platform packaging, component catalog, bundles, installations, upgrades, compatibility, and license management.
"""

import pytest
from backend.src.platform import (
    PlatformManifestManager,
    PlatformManifest,
    ComponentManifest,
    ComponentCatalog,
    ComponentType,
    ComponentStatus,
    CatalogEntry,
    EditionManager,
    EditionType,
    PlatformEdition,
    BundleManager,
    BundleType,
    Bundle,
    InstallationManager,
    InstallationProfile,
    Installation,
    UpgradeManager,
    UpgradeStatus,
    UpgradeType,
    Upgrade,
    CompatibilityManager,
    LicenseManager,
    LicenseType,
    LicenseMetadata,
    PlatformRegistry,
    ModuleStatus,
    ModuleEntry,
    ReleaseBundleManager,
    ReleaseBundle,
    PackageValidator,
)


class TestPlatformManifestManager:
    """Tests for PlatformManifestManager."""
    
    def test_create_manifest(self):
        """Test creating a manifest."""
        manager = PlatformManifestManager()
        manifest = manager.create_manifest("v1.0.0", "GCDTP", "enterprise")
        
        assert manifest.platform_version == "v1.0.0"
        assert manifest.edition == "enterprise"
    
    def test_get_manifest(self):
        """Test getting a manifest."""
        manager = PlatformManifestManager()
        manager.create_manifest("v1.0.0", "GCDTP", "enterprise")
        
        manifest = manager.get_manifest("v1.0.0")
        assert manifest is not None
    
    def test_add_component(self):
        """Test adding component to manifest."""
        manager = PlatformManifestManager()
        manager.create_manifest("v1.0.0", "GCDTP", "enterprise")
        
        component = ComponentManifest(
            name="API",
            key="api",
            version="1.0.0",
            type="module"
        )
        result = manager.add_component("v1.0.0", component)
        assert result is True


class TestComponentCatalog:
    """Tests for ComponentCatalog."""
    
    def test_get_component(self):
        """Test getting a component."""
        catalog = ComponentCatalog()
        entry = catalog.get("eventbus")
        assert entry is not None
    
    def test_get_by_type(self):
        """Test getting components by type."""
        catalog = ComponentCatalog()
        entries = catalog.get_by_type(ComponentType.INTEGRATION)
        assert len(entries) >= 1
    
    def test_update_status(self):
        """Test updating component status."""
        catalog = ComponentCatalog()
        result = catalog.update_status("eventbus", ComponentStatus.DEPRECATED)
        assert result is True


class TestEditionManager:
    """Tests for EditionManager."""
    
    def test_get_edition(self):
        """Test getting an edition."""
        manager = EditionManager()
        edition = manager.get_edition("Community Edition")
        assert edition is not None
    
    def test_get_all_editions(self):
        """Test getting all editions."""
        manager = EditionManager()
        editions = manager.get_all_editions()
        assert len(editions) >= 1
    
    def test_get_active_editions(self):
        """Test getting active editions."""
        manager = EditionManager()
        editions = manager.get_active_editions()
        assert len(editions) >= 1


class TestBundleManager:
    """Tests for BundleManager."""
    
    def test_create_bundle(self):
        """Test creating a bundle."""
        manager = BundleManager()
        bundle = manager.create_bundle(
            "Docker Bundle",
            "docker-bundle",
            BundleType.DOCKER,
            "1.0.0"
        )
        assert bundle.name == "Docker Bundle"
    
    def test_get_bundle(self):
        """Test getting a bundle."""
        manager = BundleManager()
        bundle = manager.get_bundle("docker-bundle")
        assert bundle is not None
    
    def test_get_bundles_by_type(self):
        """Test getting bundles by type."""
        manager = BundleManager()
        bundles = manager.get_bundles_by_type(BundleType.DOCKER)
        assert len(bundles) >= 1


class TestInstallationManager:
    """Tests for InstallationManager."""
    
    def test_create_installation(self):
        """Test creating an installation."""
        manager = InstallationManager()
        installation = manager.create_installation(
            InstallationProfile.STANDARD,
            "v1.0.0"
        )
        assert installation.profile == InstallationProfile.STANDARD
    
    def test_get_profile_components(self):
        """Test getting profile components."""
        manager = InstallationManager()
        components = manager.get_profile_components(InstallationProfile.MINIMAL)
        assert "api" in components
    
    def test_validate_components(self):
        """Test validating components."""
        manager = InstallationManager()
        result = manager.validate_components(["geoserver"])
        assert len(result["errors"]) > 0


class TestUpgradeManager:
    """Tests for UpgradeManager."""
    
    def test_create_upgrade(self):
        """Test creating an upgrade."""
        manager = UpgradeManager()
        upgrade = manager.create_upgrade(
            "v1.0.0",
            "v1.1.0",
            1,
            UpgradeType.MINOR
        )
        assert upgrade.from_version == "v1.0.0"
    
    def test_start_upgrade(self):
        """Test starting an upgrade."""
        manager = UpgradeManager()
        upgrade = manager.create_upgrade("v1.0.0", "v1.1.0", 1, UpgradeType.MINOR)
        result = manager.start_upgrade(upgrade.id)
        assert result is True
    
    def test_complete_upgrade(self):
        """Test completing an upgrade."""
        manager = UpgradeManager()
        upgrade = manager.create_upgrade("v1.0.0", "v1.1.0", 1, UpgradeType.MINOR)
        manager.start_upgrade(upgrade.id)
        manager.complete_upgrade(upgrade.id)
        assert manager.get_current_version() == "v1.1.0"


class TestCompatibilityManager:
    """Tests for CompatibilityManager."""
    
    def test_add_compatibility(self):
        """Test adding compatibility."""
        manager = CompatibilityManager()
        manager.add_compatibility("test", "1.0", {"compatible": ["1.1"]})
        compat = manager.get_compatibility("test", "1.0")
        assert compat is not None
    
    def test_is_compatible(self):
        """Test checking compatibility."""
        manager = CompatibilityManager()
        manager.add_compatibility("test", "1.0", incompatible=["0.9"])
        assert manager.is_compatible("test", "1.0", "0.9") is False


class TestLicenseManager:
    """Tests for LicenseManager."""
    
    def test_register_license(self):
        """Test registering a license."""
        manager = LicenseManager()
        license = manager.register_license(
            "LIC-123",
            LicenseType.STANDARD,
            "enterprise",
            "Test Corp"
        )
        assert license.key == "LIC-123"
    
    def test_get_license(self):
        """Test getting a license."""
        manager = LicenseManager()
        manager.register_license("LIC-123", LicenseType.STANDARD, "enterprise", "Test")
        license = manager.get_license("LIC-123")
        assert license is not None
    
    def test_get_licenses_by_type(self):
        """Test getting licenses by type."""
        manager = LicenseManager()
        manager.register_license("LIC-1", LicenseType.TRIAL, "community", "Test1")
        licenses = manager.get_licenses_by_type(LicenseType.TRIAL)
        assert len(licenses) >= 1


class TestPlatformRegistry:
    """Tests for PlatformRegistry."""
    
    def test_get_module(self):
        """Test getting a module."""
        registry = PlatformRegistry()
        module = registry.get("api")
        assert module is not None
    
    def test_register_module(self):
        """Test registering a module."""
        registry = PlatformRegistry()
        entry = ModuleEntry(
            name="Test Module",
            key="test-module",
            module_type="module",
            version="1.0.0",
            status=ModuleStatus.ACTIVE
        )
        result = registry.register(entry)
        assert result is None  # No return, modifies in place
    
    def test_update_status(self):
        """Test updating module status."""
        registry = PlatformRegistry()
        result = registry.update_status("api", ModuleStatus.DEPRECATED)
        assert result is True


class TestReleaseBundleManager:
    """Tests for ReleaseBundleManager."""
    
    def test_create_bundle(self):
        """Test creating a release bundle."""
        manager = ReleaseBundleManager()
        bundle = manager.create_bundle("v1.0.0", "docker", "/path/to/bundle")
        assert bundle.version == "v1.0.0"
    
    def test_mark_stable(self):
        """Test marking bundle as stable."""
        manager = ReleaseBundleManager()
        manager.create_bundle("v1.0.0", "docker", "/path")
        result = manager.mark_stable("v1.0.0")
        assert result is True
    
    def test_get_stable_bundles(self):
        """Test getting stable bundles."""
        manager = ReleaseBundleManager()
        manager.create_bundle("v1.0.0", "docker", "/path")
        manager.mark_stable("v1.0.0")
        bundles = manager.get_stable_bundles()
        assert len(bundles) >= 1


class TestPackageValidator:
    """Tests for PackageValidator."""
    
    def test_validate_bundle(self):
        """Test validating a bundle."""
        validator = PackageValidator()
        issues = validator.validate_bundle("docker", ["api", "database"])
        assert len(issues) == 0
    
    def test_validate_bundle_invalid(self):
        """Test validating invalid bundle."""
        validator = PackageValidator()
        issues = validator.validate_bundle("invalid", [])
        assert len(issues) > 0
    
    def test_validate_installation(self):
        """Test validating installation."""
        validator = PackageValidator()
        issues = validator.validate_installation("standard", ["api"])
        assert len(issues) == 0
    
    def test_validate_upgrade(self):
        """Test validating upgrade."""
        validator = PackageValidator()
        issues = validator.validate_upgrade("v1.0.0", "v1.1.0")
        assert len(issues) == 0


class TestComponentType:
    """Tests for ComponentType."""
    
    def test_component_types(self):
        """Test component type values."""
        assert ComponentType.ENGINE.value == "engine"
        assert ComponentType.INTEGRATION.value == "integration"


class TestEditionType:
    """Tests for EditionType."""
    
    def test_edition_types(self):
        """Test edition type values."""
        assert EditionType.COMMUNITY.value == "community"
        assert EditionType.ENTERPRISE.value == "enterprise"


class TestBundleType:
    """Tests for BundleType."""
    
    def test_bundle_types(self):
        """Test bundle type values."""
        assert BundleType.DOCKER.value == "docker"
        assert BundleType.OFFLINE.value == "offline"


class TestInstallationProfile:
    """Tests for InstallationProfile."""
    
    def test_installation_profiles(self):
        """Test installation profile values."""
        assert InstallationProfile.MINIMAL.value == "minimal"
        assert InstallationProfile.ENTERPRISE.value == "enterprise"


class TestUpgradeStatus:
    """Tests for UpgradeStatus."""
    
    def test_upgrade_statuses(self):
        """Test upgrade status values."""
        assert UpgradeStatus.PENDING.value == "pending"
        assert UpgradeStatus.COMPLETED.value == "completed"


class TestUpgradeType:
    """Tests for UpgradeType."""
    
    def test_upgrade_types(self):
        """Test upgrade type values."""
        assert UpgradeType.MAJOR.value == "major"
        assert UpgradeType.MINOR.value == "minor"


class TestLicenseType:
    """Tests for LicenseType."""
    
    def test_license_types(self):
        """Test license type values."""
        assert LicenseType.TRIAL.value == "trial"
        assert LicenseType.ENTERPRISE.value == "enterprise"


class TestModuleStatus:
    """Tests for ModuleStatus."""
    
    def test_module_statuses(self):
        """Test module status values."""
        assert ModuleStatus.ACTIVE.value == "active"
        assert ModuleStatus.DEPRECATED.value == "deprecated"


class TestCatalogEntry:
    """Tests for CatalogEntry."""
    
    def test_create_entry(self):
        """Test creating a catalog entry."""
        entry = CatalogEntry(
            name="Test",
            key="test",
            component_type=ComponentType.ENGINE,
            version="1.0.0",
            status=ComponentStatus.ACTIVE
        )
        assert entry.name == "Test"


class TestPlatformEdition:
    """Tests for PlatformEdition."""
    
    def test_create_edition(self):
        """Test creating a platform edition."""
        edition = PlatformEdition(
            name="Test Edition",
            edition_type=EditionType.ENTERPRISE,
            features=["Feature 1"]
        )
        assert edition.name == "Test Edition"


class TestBundle:
    """Tests for Bundle."""
    
    def test_create_bundle(self):
        """Test creating a bundle."""
        bundle = Bundle(
            name="Test Bundle",
            key="test-bundle",
            bundle_type=BundleType.DOCKER,
            version="1.0.0"
        )
        assert bundle.name == "Test Bundle"


class TestInstallation:
    """Tests for Installation."""
    
    def test_create_installation(self):
        """Test creating an installation."""
        from backend.src.platform import InstallationManager, InstallationProfile
        
        manager = InstallationManager()
        inst = manager.create_installation(InstallationProfile.STANDARD, "v1.0.0")
        assert inst.version == "v1.0.0"


class TestUpgrade:
    """Tests for Upgrade."""
    
    def test_create_upgrade(self):
        """Test creating an upgrade."""
        from backend.src.platform import UpgradeManager, UpgradeType
        
        manager = UpgradeManager()
        upgrade = manager.create_upgrade("v1.0.0", "v1.1.0", 1, UpgradeType.MINOR)
        assert upgrade.migration_version == 1


class TestLicenseMetadata:
    """Tests for LicenseMetadata."""
    
    def test_create_metadata(self):
        """Test creating license metadata."""
        metadata = LicenseMetadata(
            key="LIC-123",
            license_type=LicenseType.ENTERPRISE,
            edition="enterprise",
            issued_to="Test Corp"
        )
        assert metadata.key == "LIC-123"


class TestModuleEntry:
    """Tests for ModuleEntry."""
    
    def test_create_entry(self):
        """Test creating a module entry."""
        entry = ModuleEntry(
            name="Test Module",
            key="test-module",
            module_type="module",
            version="1.0.0",
            status=ModuleStatus.ACTIVE
        )
        assert entry.name == "Test Module"


class TestReleaseBundle:
    """Tests for ReleaseBundle."""
    
    def test_create_bundle(self):
        """Test creating a release bundle."""
        bundle = ReleaseBundle(
            version="v1.0.0",
            bundle_type="docker",
            bundle_path="/path/to/bundle"
        )
        assert bundle.version == "v1.0.0"
