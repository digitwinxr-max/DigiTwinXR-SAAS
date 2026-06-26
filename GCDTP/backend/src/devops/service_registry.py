"""
Service Registry

Manages internal service registry.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


class ServiceType(str):
    """Service types."""
    MODULE = "module"
    ADAPTER = "adapter"
    INTEGRATION = "integration"


class ServiceStatus(str):
    """Service status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"


@dataclass
class Service:
    """Service entry."""
    name: str
    service_type: ServiceType
    version: str = "1.0.0"
    status: ServiceStatus = ServiceStatus.ACTIVE
    endpoint: str = ""
    dependencies: List[str] = field(default_factory=list)
    health_check_enabled: bool = True
    last_health_check: Optional[datetime] = None


class ServiceRegistry:
    """
    Manages internal service registry.
    
    Tracks:
    - Internal modules
    - Integration adapters
    - Status
    - Version
    - Dependencies
    """
    
    def __init__(self):
        self._services: Dict[str, Service] = {}
        self._initialize_defaults()
    
    def _initialize_defaults(self) -> None:
        """Initialize default services."""
        self.register_service(Service(
            name="api",
            service_type=ServiceType.MODULE,
            version="1.0.0",
            endpoint="/api"
        ))
        
        self.register_service(Service(
            name="eventbus",
            service_type=ServiceType.MODULE,
            version="1.0.0"
        ))
        
        self.register_service(Service(
            name="geoserver_adapter",
            service_type=ServiceType.ADAPTER,
            version="1.0.0"
        ))
        
        self.register_service(Service(
            name="neo4j_adapter",
            service_type=ServiceType.ADAPTER,
            version="1.0.0"
        ))
        
        self.register_service(Service(
            name="emqx_adapter",
            service_type=ServiceType.ADAPTER,
            version="1.0.0"
        ))
        
        self.register_service(Service(
            name="nodered_adapter",
            service_type=ServiceType.ADAPTER,
            version="1.0.0"
        ))
    
    def register_service(self, service: Service) -> None:
        """Register a service."""
        self._services[service.name] = service
    
    def get_service(self, name: str) -> Optional[Service]:
        """Get a service."""
        return self._services.get(name)
    
    def get_all_services(self) -> List[Service]:
        """Get all services."""
        return list(self._services.values())
    
    def get_services_by_type(self, service_type: ServiceType) -> List[Service]:
        """Get services by type."""
        return [s for s in self._services.values() if s.service_type == service_type]
    
    def get_services_by_status(self, status: ServiceStatus) -> List[Service]:
        """Get services by status."""
        return [s for s in self._services.values() if s.status == status]
    
    def update_status(self, name: str, status: ServiceStatus) -> bool:
        """Update service status."""
        service = self._services.get(name)
        if service:
            service.status = status
            return True
        return False
    
    def update_health_check(self, name: str, healthy: bool) -> bool:
        """Update service health check status."""
        service = self._services.get(name)
        if service:
            service.last_health_check = datetime.utcnow()
            if not healthy:
                service.status = ServiceStatus.DEGRADED
            elif service.status == ServiceStatus.DEGRADED:
                service.status = ServiceStatus.ACTIVE
            return True
        return False
    
    def get_dependencies(self, name: str) -> List[str]:
        """Get service dependencies."""
        service = self._services.get(name)
        return service.dependencies if service else []
    
    def is_healthy(self) -> bool:
        """Check if all services are healthy."""
        for service in self._services.values():
            if service.health_check_enabled and service.status not in [
                ServiceStatus.ACTIVE, ServiceStatus.MAINTENANCE
            ]:
                return False
        return True
