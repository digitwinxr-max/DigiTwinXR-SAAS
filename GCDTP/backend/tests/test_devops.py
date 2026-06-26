"""
Tests for DevOps Module

Tests configuration, feature flags, backup, restore, disaster recovery, release management, service registry, and health probes.
"""

import pytest
from backend.src.devops import (
    ConfigManager,
    Environment,
    ProfileType,
    ConfigEntry,
    EnvironmentProfile,
    EnvironmentManager,
    SecretManager,
    SecretBackend,
    SecretType,
    SecretMetadata,
    BackupManager,
    BackupStatus,
    BackupType,
    RestoreManager,
    RestoreStatus,
    RestoreType,
    DisasterRecoveryManager,
    DRPlanType,
    DRPlan,
    HealthProbeManager,
    ProbeType,
    HealthProbe,
    ServiceRegistry,
    ServiceType,
    ServiceStatus,
    Service,
    FeatureFlagManager,
    FeatureFlagStatus,
    FeatureFlag,
    ReleaseManager,
    Release,
    DeploymentValidator,
)


class TestConfigManager:
    """Tests for ConfigManager."""
    
    def test_get_default_config(self):
        """Test getting default configuration."""
        manager = ConfigManager()
        value = manager.get("database.pool_size")
        assert value == 20
    
    def test_set_override(self):
        """Test setting runtime override."""
        manager = ConfigManager()
        manager.set_override("database.pool_size", 50)
        assert manager.get("database.pool_size") == 50
    
    def test_clear_override(self):
        """Test clearing runtime override."""
        manager = ConfigManager()
        manager.set_override("database.pool_size", 50)
        manager.clear_override("database.pool_size")
        assert manager.get("database.pool_size") == 20
    
    def test_register_profile(self):
        """Test registering a profile."""
        manager = ConfigManager()
        profile = EnvironmentProfile(
            name="production",
            environment=Environment.PRODUCTION,
            profile_type=ProfileType.ENTERPRISE,
            config_overrides={"database.pool_size": 100}
        )
        manager.register_profile(profile)
        manager.activate_profile("production")
        assert manager.get("database.pool_size") == 100


class TestEnvironmentManager:
    """Tests for EnvironmentManager."""
    
    def test_get_environment(self):
        """Test getting environment."""
        manager = EnvironmentManager()
        env = manager.get_environment("production")
        assert env.name == "production"
    
    def test_set_current_environment(self):
        """Test setting current environment."""
        manager = EnvironmentManager()
        manager.set_current_environment("production")
        assert manager.is_production() is True
    
    def test_is_development(self):
        """Test development check."""
        manager = EnvironmentManager()
        manager.set_current_environment("development")
        assert manager.is_development() is True


class TestSecretManager:
    """Tests for SecretManager."""
    
    def test_get_secret(self):
        """Test getting secret metadata."""
        manager = SecretManager()
        secret = manager.get_secret("database_password")
        assert secret.name == "database_password"
    
    def test_get_secrets_by_type(self):
        """Test getting secrets by type."""
        manager = SecretManager()
        secrets = manager.get_secrets_by_type(SecretType.DATABASE)
        assert len(secrets) >= 1
    
    def test_mark_rotation_required(self):
        """Test marking secret for rotation."""
        manager = SecretManager()
        manager.mark_rotation_required("database_password")
        secret = manager.get_secret("database_password")
        assert secret.rotation_required is True


class TestBackupManager:
    """Tests for BackupManager."""
    
    def test_create_backup(self):
        """Test creating a backup."""
        manager = BackupManager()
        job = manager.create_backup(BackupType.POSTGRESQL, "admin")
        assert job.backup_type == BackupType.POSTGRESQL
        assert job.status == BackupStatus.PENDING
    
    def test_start_backup(self):
        """Test starting a backup."""
        manager = BackupManager()
        job = manager.create_backup(BackupType.POSTGRESQL)
        manager.start_backup(job.id)
        assert job.status == BackupStatus.RUNNING
    
    def test_complete_backup(self):
        """Test completing a backup."""
        manager = BackupManager()
        job = manager.create_backup(BackupType.POSTGRESQL)
        manager.start_backup(job.id)
        manager.complete_backup(job.id, 1024, "/backup/postgresql", 300)
        assert job.status == BackupStatus.COMPLETED
        assert job.size_bytes == 1024
    
    def test_get_statistics(self):
        """Test getting backup statistics."""
        manager = BackupManager()
        stats = manager.get_statistics()
        assert "total_jobs" in stats


class TestRestoreManager:
    """Tests for RestoreManager."""
    
    def test_create_restore(self):
        """Test creating a restore job."""
        manager = RestoreManager()
        job = manager.create_restore(
            "backup-123",
            RestoreType.FULL,
            "production",
            "admin"
        )
        assert job.restore_type == RestoreType.FULL
        assert job.status == RestoreStatus.PENDING
    
    def test_validate_restore(self):
        """Test validating a restore."""
        manager = RestoreManager()
        job = manager.create_restore(
            "backup-123",
            RestoreType.POINT_IN_TIME,
            "production"
        )
        validation = manager.validate_restore(job.id)
        assert validation["valid"] is False


class TestDisasterRecoveryManager:
    """Tests for DisasterRecoveryManager."""
    
    def test_get_plan(self):
        """Test getting DR plan."""
        manager = DisasterRecoveryManager()
        plan = manager.get_plan_by_type(DRPlanType.DATABASE_FAILURE)
        assert plan is not None
        assert plan.plan_type == DRPlanType.DATABASE_FAILURE
    
    def test_activate_plan(self):
        """Test activating a DR plan."""
        manager = DisasterRecoveryManager()
        plan = manager.get_plan_by_type(DRPlanType.DATABASE_FAILURE)
        manager.activate_plan(plan.id)
        assert plan.is_active is True
    
    def test_mark_tested(self):
        """Test marking plan as tested."""
        manager = DisasterRecoveryManager()
        plan = manager.get_plan_by_type(DRPlanType.DATABASE_FAILURE)
        manager.mark_tested(plan.id, True)
        assert plan.last_successful_test is True
    
    def test_get_recovery_summary(self):
        """Test getting recovery summary."""
        manager = DisasterRecoveryManager()
        summary = manager.get_recovery_summary()
        assert "total_plans" in summary


class TestHealthProbeManager:
    """Tests for HealthProbeManager."""
    
    def test_get_probe(self):
        """Test getting a probe."""
        manager = HealthProbeManager()
        probe = manager.get_probe("api_readiness")
        assert probe.probe_type == ProbeType.READINESS
    
    def test_record_result(self):
        """Test recording probe result."""
        manager = HealthProbeManager()
        manager.record_result("api_readiness", True, 50)
        result = manager.get_result("api_readiness")
        assert result["healthy"] is True
    
    def test_is_ready(self):
        """Test readiness check."""
        manager = HealthProbeManager()
        manager.record_result("api_readiness", True, 50)
        assert manager.is_ready() is True


class TestServiceRegistry:
    """Tests for ServiceRegistry."""
    
    def test_get_service(self):
        """Test getting a service."""
        registry = ServiceRegistry()
        service = registry.get_service("api")
        assert service.name == "api"
    
    def test_update_status(self):
        """Test updating service status."""
        registry = ServiceRegistry()
        registry.update_status("api", ServiceStatus.DEGRADED)
        service = registry.get_service("api")
        assert service.status == ServiceStatus.DEGRADED
    
    def test_is_healthy(self):
        """Test health check."""
        registry = ServiceRegistry()
        assert registry.is_healthy() is True


class TestFeatureFlagManager:
    """Tests for FeatureFlagManager."""
    
    def test_create_flag(self):
        """Test creating a feature flag."""
        manager = FeatureFlagManager()
        flag = manager.create_flag("Test Feature", "test_feature")
        assert flag.name == "Test Feature"
    
    def test_enable_flag(self):
        """Test enabling a flag."""
        manager = FeatureFlagManager()
        manager.enable("new_simulation_engine")
        flag = manager.get_flag("new_simulation_engine")
        assert flag.status == FeatureFlagStatus.ACTIVE
    
    def test_set_rollout_percentage(self):
        """Test setting rollout percentage."""
        manager = FeatureFlagManager()
        manager.set_rollout_percentage("new_simulation_engine", 50)
        flag = manager.get_flag("new_simulation_engine")
        assert flag.rollout_percentage == 50
    
    def test_is_enabled(self):
        """Test checking if flag is enabled."""
        manager = FeatureFlagManager()
        manager.enable("new_simulation_engine")
        assert manager.is_enabled("new_simulation_engine") is True
    
    def test_is_enabled_for_org(self):
        """Test checking if flag is enabled for organization."""
        manager = FeatureFlagManager()
        manager.enable("new_simulation_engine")
        manager.add_organization("new_simulation_engine", "org-123")
        assert manager.is_enabled("new_simulation_engine", "org-123") is True


class TestReleaseManager:
    """Tests for ReleaseManager."""
    
    def test_create_release(self):
        """Test creating a release."""
        manager = ReleaseManager()
        release = manager.create_release(
            "v1.0.0",
            "Initial Release",
            "First release"
        )
        assert release.version == "v1.0.0"
    
    def test_mark_stable(self):
        """Test marking release as stable."""
        manager = ReleaseManager()
        manager.create_release("v1.0.0", "Initial Release")
        manager.mark_stable("v1.0.0")
        release = manager.get_release("v1.0.0")
        assert release.is_stable is True
    
    def test_set_current_version(self):
        """Test setting current version."""
        manager = ReleaseManager()
        manager.create_release("v1.0.0", "Initial Release")
        manager.set_current_version("v1.0.0")
        assert manager.get_current_version() == "v1.0.0"
    
    def test_get_recent_releases(self):
        """Test getting recent releases."""
        manager = ReleaseManager()
        manager.create_release("v1.0.0", "Initial Release")
        releases = manager.get_recent_releases()
        assert len(releases) >= 1


class TestDeploymentValidator:
    """Tests for DeploymentValidator."""
    
    def test_validate_deployment_config(self):
        """Test validating deployment config."""
        validator = DeploymentValidator()
        issues = validator.validate_deployment_config(
            "v1.0.0",
            "production",
            "rolling"
        )
        assert len(issues) == 0
    
    def test_validate_deployment_config_invalid(self):
        """Test validating invalid deployment config."""
        validator = DeploymentValidator()
        issues = validator.validate_deployment_config(
            "",
            "invalid_env",
            "invalid_type"
        )
        assert len(issues) > 0
    
    def test_validate_backup_config(self):
        """Test validating backup config."""
        validator = DeploymentValidator()
        issues = validator.validate_backup_config("postgresql", True)
        assert len(issues) == 0
    
    def test_validate_restore_config(self):
        """Test validating restore config."""
        validator = DeploymentValidator()
        issues = validator.validate_restore_config("full", False)
        assert len(issues) == 0


class TestDRPlanType:
    """Tests for DRPlanType."""
    
    def test_dr_plan_types(self):
        """Test DR plan type values."""
        assert DRPlanType.DATABASE_FAILURE.value == "database_failure"
        assert DRPlanType.EMQX_FAILURE.value == "emqx_failure"


class TestProbeType:
    """Tests for ProbeType."""
    
    def test_probe_types(self):
        """Test probe type values."""
        assert ProbeType.READINESS.value == "readiness"
        assert ProbeType.LIVENESS.value == "liveness"


class TestServiceType:
    """Tests for ServiceType."""
    
    def test_service_types(self):
        """Test service type values."""
        assert ServiceType.MODULE.value == "module"
        assert ServiceType.ADAPTER.value == "adapter"


class TestBackupType:
    """Tests for BackupType."""
    
    def test_backup_types(self):
        """Test backup type values."""
        assert BackupType.POSTGRESQL.value == "postgresql"
        assert BackupType.CONFIG.value == "config"


class TestRestoreType:
    """Tests for RestoreType."""
    
    def test_restore_types(self):
        """Test restore type values."""
        assert RestoreType.FULL.value == "full"
        assert RestoreType.POINT_IN_TIME.value == "point_in_time"


class TestFeatureFlagStatus:
    """Tests for FeatureFlagStatus."""
    
    def test_flag_statuses(self):
        """Test flag status values."""
        assert FeatureFlagStatus.ACTIVE.value == "active"
        assert FeatureFlagStatus.INACTIVE.value == "inactive"
