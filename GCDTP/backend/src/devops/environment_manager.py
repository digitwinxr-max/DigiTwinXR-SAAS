"""
Environment Manager

Manages environment profiles and configurations.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class EnvironmentConfig:
    """Environment configuration."""
    name: str
    base_url: str
    debug: bool
    log_level: str
    features: Dict[str, bool]


class EnvironmentManager:
    """
    Manages environment configurations.
    
    Supports:
    - Development
    - Test
    - Staging
    - Production
    """
    
    def __init__(self):
        self._environments: Dict[str, EnvironmentConfig] = {}
        self._current_env: Optional[str] = None
        self._initialize_environments()
    
    def _initialize_environments(self) -> None:
        """Initialize default environments."""
        self.register_environment(EnvironmentConfig(
            name="development",
            base_url="http://localhost:8000",
            debug=True,
            log_level="DEBUG",
            features={"debug_mode": True, "hot_reload": True}
        ))
        
        self.register_environment(EnvironmentConfig(
            name="test",
            base_url="http://localhost:8001",
            debug=True,
            log_level="DEBUG",
            features={"debug_mode": True, "hot_reload": False}
        ))
        
        self.register_environment(EnvironmentConfig(
            name="staging",
            base_url="https://staging.gcdtp.example.com",
            debug=False,
            log_level="INFO",
            features={"debug_mode": False, "hot_reload": False}
        ))
        
        self.register_environment(EnvironmentConfig(
            name="production",
            base_url="https://api.gcdtp.example.com",
            debug=False,
            log_level="WARNING",
            features={"debug_mode": False, "hot_reload": False}
        ))
    
    def register_environment(self, config: EnvironmentConfig) -> None:
        """Register an environment."""
        self._environments[config.name] = config
    
    def get_environment(self, name: str) -> Optional[EnvironmentConfig]:
        """Get environment configuration."""
        return self._environments.get(name)
    
    def get_current_environment(self) -> Optional[EnvironmentConfig]:
        """Get current environment."""
        if self._current_env:
            return self._environments.get(self._current_env)
        return None
    
    def set_current_environment(self, name: str) -> bool:
        """Set current environment."""
        if name in self._environments:
            self._current_env = name
            return True
        return False
    
    def get_all_environments(self) -> List[EnvironmentConfig]:
        """Get all environments."""
        return list(self._environments.values())
    
    def is_development(self) -> bool:
        """Check if current environment is development."""
        return self._current_env == "development"
    
    def is_test(self) -> bool:
        """Check if current environment is test."""
        return self._current_env == "test"
    
    def is_staging(self) -> bool:
        """Check if current environment is staging."""
        return self._current_env == "staging"
    
    def is_production(self) -> bool:
        """Check if current environment is production."""
        return self._current_env == "production"
