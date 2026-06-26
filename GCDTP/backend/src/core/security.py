"""
Security Configuration Module

Centralizes all JWT and security settings.
Application fails startup if required secrets are missing.
"""
import os
from typing import List, Optional
from datetime import timedelta


class SecurityConfig:
    """
    Centralized security configuration.
    
    Loads JWT secrets from environment variables.
    Validates required secrets on initialization.
    """
    
    # JWT Algorithm
    ALGORITHM = "HS256"
    
    # Token expiration times
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    # Token type identifiers
    ACCESS_TOKEN_TYPE = "access"
    REFRESH_TOKEN_TYPE = "refresh"
    
    def __init__(self):
        """Initialize and validate security configuration."""
        self._jwt_secret_key: Optional[str] = None
        self._jwt_refresh_secret_key: Optional[str] = None
        self._allowed_origins: List[str] = []
        
        self._load_jwt_secrets()
        self._load_allowed_origins()
    
    def _load_jwt_secrets(self) -> None:
        """Load JWT secrets from environment variables."""
        self._jwt_secret_key = os.getenv("JWT_SECRET_KEY")
        self._jwt_refresh_secret_key = os.getenv("JWT_REFRESH_SECRET_KEY")
        
        # Fail startup if secrets are missing
        if not self._jwt_secret_key:
            raise ValueError(
                "JWT_SECRET_KEY environment variable is required. "
                "Set it to a secure random string."
            )
        
        if not self._jwt_refresh_secret_key:
            raise ValueError(
                "JWT_REFRESH_SECRET_KEY environment variable is required. "
                "Set it to a secure random string."
            )
        
        # Warn about default/weak secrets
        if self._jwt_secret_key in ("change_me", "your_jwt_secret_key_here"):
            raise ValueError(
                "JWT_SECRET_KEY must not be a placeholder value. "
                "Use a secure random string."
            )
        
        if self._jwt_refresh_secret_key in ("change_me", "your_jwt_secret_key_here"):
            raise ValueError(
                "JWT_REFRESH_SECRET_KEY must not be a placeholder value. "
                "Use a secure random string."
            )
    
    def _load_allowed_origins(self) -> None:
        """Load allowed CORS origins from environment variable."""
        origins_str = os.getenv("ALLOWED_ORIGINS", "")
        
        if not origins_str:
            # Default to localhost for development
            self._allowed_origins = ["http://localhost:3000", "http://localhost:5173"]
            return
        
        # Parse comma-separated list
        self._allowed_origins = [
            origin.strip() 
            for origin in origins_str.split(",") 
            if origin.strip()
        ]
    
    @property
    def jwt_secret_key(self) -> str:
        """Get JWT secret key for access tokens."""
        return self._jwt_secret_key
    
    @property
    def jwt_refresh_secret_key(self) -> str:
        """Get JWT secret key for refresh tokens."""
        return self._jwt_refresh_secret_key
    
    @property
    def allowed_origins(self) -> List[str]:
        """Get list of allowed CORS origins."""
        return self._allowed_origins
    
    @property
    def access_token_expire_minutes(self) -> int:
        """Get access token expiration in minutes."""
        return self.ACCESS_TOKEN_EXPIRE_MINUTES
    
    @property
    def refresh_token_expire_days(self) -> int:
        """Get refresh token expiration in days."""
        return self.REFRESH_TOKEN_EXPIRE_DAYS
    
    def get_access_token_expire_timedelta(self) -> timedelta:
        """Get access token expiration as timedelta."""
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    def get_refresh_token_expire_timedelta(self) -> timedelta:
        """Get refresh token expiration as timedelta."""
        return timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)


# Global security config instance (initialized on first import)
_security_config: Optional[SecurityConfig] = None


def get_security_config() -> SecurityConfig:
    """
    Get the global security configuration.
    
    Initializes on first call, validates secrets at that point.
    """
    global _security_config
    if _security_config is None:
        _security_config = SecurityConfig()
    return _security_config


def reset_security_config() -> None:
    """Reset security config (for testing)."""
    global _security_config
    _security_config = None