"""
Connector Registry

Registry for managing external connectors.
Supports HTTP, REST, Webhook, File, Email, and future integrations.
"""

import uuid
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from backend.src.integrations.node_red.workflow_types import ConnectorType


@dataclass
class ConnectorConfig:
    """Configuration for a connector."""
    connector_type: ConnectorType
    name: str
    url: str = ""
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    auth: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    retry_count: int = 3
    custom_config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "connector_type": self.connector_type.value,
            "name": self.name,
            "url": self.url,
            "method": self.method,
            "headers": self.headers,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "custom_config": self.custom_config,
        }


class ConnectorRegistry:
    """
    Registry for managing external connectors.
    
    Supported connectors:
    - HTTP/REST
    - Webhook
    - File
    - Email (metadata)
    - MQTT (future)
    - GeoServer (future)
    - EMQX (future)
    """
    
    def __init__(self):
        self._connectors: Dict[str, ConnectorConfig] = {}
        self._handlers: Dict[ConnectorType, Callable] = {}
    
    # =========================================================================
    # Connector Registration
    # =========================================================================
    
    def register_http_connector(
        self,
        name: str,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        auth: Optional[Dict[str, str]] = None,
        timeout: int = 30
    ) -> str:
        """
        Register an HTTP connector.
        
        Args:
            name: Connector name
            url: Endpoint URL
            method: HTTP method
            headers: Request headers
            auth: Authentication config
            timeout: Request timeout
            
        Returns:
            Connector ID
        """
        connector_id = str(uuid.uuid4())
        
        self._connectors[connector_id] = ConnectorConfig(
            connector_type=ConnectorType.HTTP,
            name=name,
            url=url,
            method=method,
            headers=headers or {},
            auth=auth or {},
            timeout=timeout
        )
        
        return connector_id
    
    def register_webhook_connector(
        self,
        name: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        secret: str = ""
    ) -> str:
        """
        Register a webhook connector.
        
        Args:
            name: Connector name
            url: Webhook URL
            headers: Request headers
            secret: Webhook secret
            
        Returns:
            Connector ID
        """
        connector_id = str(uuid.uuid4())
        
        self._connectors[connector_id] = ConnectorConfig(
            connector_type=ConnectorType.WEBHOOK,
            name=name,
            url=url,
            headers=headers or {},
            custom_config={"secret": secret}
        )
        
        return connector_id
    
    def register_rest_connector(
        self,
        name: str,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        auth: Optional[Dict[str, str]] = None,
        timeout: int = 30
    ) -> str:
        """
        Register a REST connector.
        
        Args:
            name: Connector name
            base_url: Base URL for REST API
            headers: Request headers
            auth: Authentication config
            timeout: Request timeout
            
        Returns:
            Connector ID
        """
        connector_id = str(uuid.uuid4())
        
        self._connectors[connector_id] = ConnectorConfig(
            connector_type=ConnectorType.REST,
            name=name,
            url=base_url,
            headers=headers or {},
            auth=auth or {},
            timeout=timeout
        )
        
        return connector_id
    
    def register_file_connector(
        self,
        name: str,
        path: str,
        mode: str = "read"
    ) -> str:
        """
        Register a file connector.
        
        Args:
            name: Connector name
            path: File path
            mode: File mode (read/write)
            
        Returns:
            Connector ID
        """
        connector_id = str(uuid.uuid4())
        
        self._connectors[connector_id] = ConnectorConfig(
            connector_type=ConnectorType.FILE,
            name=name,
            url=path,
            custom_config={"mode": mode}
        )
        
        return connector_id
    
    def register_email_connector(
        self,
        name: str,
        smtp_host: str,
        smtp_port: int = 587,
        from_address: str = "",
        to_addresses: Optional[List[str]] = None
    ) -> str:
        """
        Register an email connector (metadata only).
        
        Args:
            name: Connector name
            smtp_host: SMTP host
            smtp_port: SMTP port
            from_address: From address
            to_addresses: To addresses
            
        Returns:
            Connector ID
        """
        connector_id = str(uuid.uuid4())
        
        self._connectors[connector_id] = ConnectorConfig(
            connector_type=ConnectorType.EMAIL,
            name=name,
            custom_config={
                "smtp_host": smtp_host,
                "smtp_port": smtp_port,
                "from_address": from_address,
                "to_addresses": to_addresses or [],
            }
        )
        
        return connector_id
    
    # =========================================================================
    # Connector Management
    # =========================================================================
    
    def get_connector(self, connector_id: str) -> Optional[ConnectorConfig]:
        """Get a connector by ID."""
        return self._connectors.get(connector_id)
    
    def get_connectors(
        self,
        connector_type: Optional[ConnectorType] = None
    ) -> List[ConnectorConfig]:
        """Get all connectors, optionally filtered by type."""
        if connector_type:
            return [c for c in self._connectors.values() if c.connector_type == connector_type]
        return list(self._connectors.values())
    
    def update_connector(
        self,
        connector_id: str,
        **kwargs
    ) -> Optional[ConnectorConfig]:
        """Update a connector configuration."""
        connector = self._connectors.get(connector_id)
        if not connector:
            return None
        
        for key, value in kwargs.items():
            if hasattr(connector, key):
                setattr(connector, key, value)
        
        return connector
    
    def delete_connector(self, connector_id: str) -> bool:
        """Delete a connector."""
        if connector_id in self._connectors:
            del self._connectors[connector_id]
            return True
        return False
    
    # =========================================================================
    # Connector Execution
    # =========================================================================
    
    def register_handler(
        self,
        connector_type: ConnectorType,
        handler: Callable
    ) -> None:
        """
        Register a handler for a connector type.
        
        Args:
            connector_type: Connector type
            handler: Handler function
        """
        self._handlers[connector_type] = handler
    
    def execute_connector(
        self,
        connector_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a connector.
        
        Args:
            connector_id: Connector ID
            data: Data to send
            
        Returns:
            Execution result
        """
        connector = self.get_connector(connector_id)
        if not connector:
            return {"status": "error", "error": "Connector not found"}
        
        handler = self._handlers.get(connector.connector_type)
        if handler:
            return handler(connector, data)
        
        return {"status": "unsupported", "type": connector.connector_type.value}
    
    # =========================================================================
    # Validation
    # =========================================================================
    
    def validate_connector(self, connector: ConnectorConfig) -> List[str]:
        """
        Validate a connector configuration.
        
        Args:
            connector: Connector to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not connector.name:
            issues.append("Connector name is required")
        
        if connector.connector_type in [ConnectorType.HTTP, ConnectorType.REST, ConnectorType.WEBHOOK]:
            if not connector.url:
                issues.append("URL is required for HTTP/REST/Webhook connectors")
        
        if connector.timeout < 1:
            issues.append("Timeout must be at least 1 second")
        
        if connector.timeout > 300:
            issues.append("Timeout must not exceed 300 seconds")
        
        return issues
    
    # =========================================================================
    # Helpers
    # =========================================================================
    
    def get_connector_count(self) -> int:
        """Get total connector count."""
        return len(self._connectors)
    
    def get_connectors_by_type(self) -> Dict[str, int]:
        """Get count of connectors by type."""
        counts: Dict[str, int] = {}
        for connector in self._connectors.values():
            type_name = connector.connector_type.value
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts
    
    def clear_all(self) -> None:
        """Clear all registered connectors."""
        self._connectors.clear()
        self._handlers.clear()
