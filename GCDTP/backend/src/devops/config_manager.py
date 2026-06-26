"""
Configuration Manager

Manages system configurations across environments.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


class Environment(str):
    """Environment types."""
    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class ProfileType(str):
    """Profile types."""
    LOCAL = "local"
    DOCKER = "docker"
    ENTERPRISE = "enterprise"


@dataclass
class ConfigEntry:
    """Configuration entry."""
    key: str
    value: Any
    value_type: str
    environment: str
    is_secret: bool
    description: str = ""


@dataclass
class EnvironmentProfile:
    """Environment profile."""
    name: str
    environment: Environment
    profile_type: ProfileType
    config_overrides: Dict[str, Any]
    is_active: bool = False


class ConfigManager:
    """
    Manages configurations.
    
    Supports:
    - Environment configurations
    - Profile configurations
    - Runtime overrides
    - Secret management
    """
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._profiles: Dict[str, EnvironmentProfile] = {}
        self._overrides: Dict[str, Any] = {}
        self._defaults: Dict[str, Any] = {}
        self._initialize_defaults()
    
    def _initialize_defaults(self) -> None:
        """Initialize default configurations."""
        self._defaults = {
            "database.pool_size": 20,
            "database.timeout": 30,
            "cache.default_ttl": 300,
            "rate_limit.default_rpm": 100,
            "pagination.default_page_size": 20,
            "pagination.max_page_size": 100,
        }
    
    def get(self, key: str, environment: Optional[str] = None) -> Any:
        """
        Get configuration value.
        
        Priority: overrides > environment > profile > default
        """
        # Check overrides first
        if key in self._overrides:
            return self._overrides[key]
        
        # Check environment config
        if environment and key in self._config:
            return self._config[key]
        
        # Check profile config
        for profile in self._profiles.values():
            if profile.is_active and key in profile.config_overrides:
                return profile.config_overrides[key]
        
        # Return default
        return self._defaults.get(key)
    
    def set(self, key: str, value: Any, environment: Optional[str] = None) -> None:
        """Set configuration value."""
        if environment:
            self._config[key] = value
        else:
            self._defaults[key] = value
    
    def set_override(self, key: str, value: Any) -> None:
        """Set runtime override."""
        self._overrides[key] = value
    
    def clear_override(self, key: str) -> bool:
        """Clear runtime override."""
        if key in self._overrides:
            del self._overrides[key]
            return True
        return False
    
    def clear_all_overrides(self) -> None:
        """Clear all runtime overrides."""
        self._overrides.clear()
    
    def get_all(self, environment: Optional[str] = None) -> Dict[str, Any]:
        """Get all configurations."""
        result = dict(self._defaults)
        result.update(self._config)
        result.update(self._overrides)
        return result
    
    def register_profile(self, profile: EnvironmentProfile) -> None:
        """Register an environment profile."""
        self._profiles[profile.name] = profile
    
    def activate_profile(self, profile_name: str) -> bool:
        """Activate an environment profile."""
        profile = self._profiles.get(profile_name)
        if not profile:
            return False
        
        # Deactivate others
        for p in self._profiles.values():
            p.is_active = False
        
        profile.is_active = True
        return True
    
    def deactivate_all_profiles(self) -> None:
        """Deactivate all profiles."""
        for profile in self._profiles.values():
            profile.is_active = False
