"""
Secret Manager

Manages secret metadata (not actual secrets).
Supports env variables, docker secrets, vault-ready architecture.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


class SecretBackend(str):
    """Secret backend types."""
    ENV = "env"
    DOCKER_SECRET = "docker_secret"
    VAULT = "vault"
    AWS_SECRETS = "aws_secrets"
    AZURE_KEYVAULT = "azure_keyvault"


class SecretType(str):
    """Secret types."""
    DATABASE = "database"
    KEYCLOAK = "keycloak"
    GEOSERVER = "geoserver"
    EMQX = "emqx"
    NEO4J = "neo4j"
    NODERED = "nodered"


@dataclass
class SecretMetadata:
    """Secret metadata (no actual secret values)."""
    name: str
    secret_type: SecretType
    path: str
    backend: SecretBackend
    description: str = ""
    last_rotated: Optional[datetime] = None
    rotation_required: bool = False
    rotation_interval_days: int = 90


class SecretManager:
    """
    Manages secret metadata.
    
    Note: Does NOT store actual secrets, only metadata.
    Secrets should be stored in appropriate backends.
    """
    
    def __init__(self):
        self._secrets: Dict[str, SecretMetadata] = {}
        self._initialize_defaults()
    
    def _initialize_defaults(self) -> None:
        """Initialize default secret metadata."""
        self.register_secret(SecretMetadata(
            name="database_password",
            secret_type=SecretType.DATABASE,
            path="database/password",
            backend=SecretBackend.ENV,
            description="PostgreSQL database password"
        ))
        
        self.register_secret(SecretMetadata(
            name="keycloak_client_secret",
            secret_type=SecretType.KEYCLOAK,
            path="keycloak/client_secret",
            backend=SecretBackend.ENV,
            description="Keycloak OAuth client secret"
        ))
        
        self.register_secret(SecretMetadata(
            name="geoserver_password",
            secret_type=SecretType.GEOSERVER,
            path="geoserver/admin_password",
            backend=SecretBackend.ENV,
            description="GeoServer admin password"
        ))
        
        self.register_secret(SecretMetadata(
            name="emqx_password",
            secret_type=SecretType.EMQX,
            path="emqx/api_key",
            backend=SecretBackend.ENV,
            description="EMQX API key"
        ))
        
        self.register_secret(SecretMetadata(
            name="neo4j_password",
            secret_type=SecretType.NEO4J,
            path="neo4j/password",
            backend=SecretBackend.ENV,
            description="Neo4j password"
        ))
        
        self.register_secret(SecretMetadata(
            name="nodered_password",
            secret_type=SecretType.NODERED,
            path="nodered/admin_password",
            backend=SecretBackend.ENV,
            description="Node-RED admin password"
        ))
    
    def register_secret(self, secret: SecretMetadata) -> None:
        """Register secret metadata."""
        self._secrets[secret.name] = secret
    
    def get_secret(self, name: str) -> Optional[SecretMetadata]:
        """Get secret metadata."""
        return self._secrets.get(name)
    
    def get_all_secrets(self) -> List[SecretMetadata]:
        """Get all secret metadata."""
        return list(self._secrets.values())
    
    def get_secrets_by_type(self, secret_type: SecretType) -> List[SecretMetadata]:
        """Get secrets by type."""
        return [s for s in self._secrets.values() if s.secret_type == secret_type]
    
    def get_secrets_by_backend(self, backend: SecretBackend) -> List[SecretMetadata]:
        """Get secrets by backend."""
        return [s for s in self._secrets.values() if s.backend == backend]
    
    def mark_rotation_required(self, name: str) -> bool:
        """Mark a secret as requiring rotation."""
        secret = self._secrets.get(name)
        if secret:
            secret.rotation_required = True
            return True
        return False
    
    def mark_rotated(self, name: str) -> bool:
        """Mark a secret as rotated."""
        secret = self._secrets.get(name)
        if secret:
            secret.last_rotated = datetime.utcnow()
            secret.rotation_required = False
            return True
        return False
    
    def get_secrets_requiring_rotation(self) -> List[SecretMetadata]:
        """Get secrets that need rotation."""
        return [s for s in self._secrets.values() if s.rotation_required]
