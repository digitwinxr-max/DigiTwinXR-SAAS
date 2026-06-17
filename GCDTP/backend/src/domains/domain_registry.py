"""
Domain Registry

Registry for infrastructure domain plugins.
"""

from typing import Dict, Type, Optional, Any
from .base_domain import BaseDomainPlugin, GenericDomain
from .electrical.electrical_domain import ElectricalDomain
from .water.water_domain import WaterDomain
from .transport.transport_domain import TransportDomain


class DomainRegistry:
    """
    Registry for infrastructure domain plugins.
    
    Allows hot-swapping of domain implementations.
    """
    
    def __init__(self):
        self._domains: Dict[str, Type[BaseDomainPlugin]] = {}
        self._instances: Dict[str, Optional[BaseDomainPlugin]] = {}
        self._register_defaults()
    
    def _register_defaults(self) -> None:
        """Register default domains."""
        self.register("generic", GenericDomain)
        self.register("electrical", ElectricalDomain)
        self.register("water", WaterDomain)
        self.register("transport", TransportDomain)
    
    def register(self, name: str, domain_class: Type[BaseDomainPlugin]) -> None:
        """Register a domain plugin."""
        self._domains[name] = domain_class
        self._instances[name] = None  # Lazy instantiation
    
    def unregister(self, name: str) -> bool:
        """Unregister a domain plugin."""
        if name in self._domains:
            del self._domains[name]
            if name in self._instances:
                del self._instances[name]
            return True
        return False
    
    def get(self, name: str) -> Optional[BaseDomainPlugin]:
        """Get a domain instance."""
        if name not in self._domains:
            return None
        
        if self._instances.get(name) is None:
            self._instances[name] = self._domains[name]()
        
        return self._instances[name]
    
    def get_class(self, name: str) -> Optional[Type[BaseDomainPlugin]]:
        """Get a domain class."""
        return self._domains.get(name)
    
    def list_domains(self) -> Dict[str, str]:
        """List all registered domains."""
        return {
            name: domain_class.__name__
            for name, domain_class in self._domains.items()
        }
    
    def has_domain(self, name: str) -> bool:
        """Check if domain exists."""
        return name in self._domains


# Global registry instance
_domain_registry: Optional[DomainRegistry] = None


def get_domain_registry() -> DomainRegistry:
    """Get global domain registry."""
    global _domain_registry
    if _domain_registry is None:
        _domain_registry = DomainRegistry()
    return _domain_registry


def reset_domain_registry() -> None:
    """Reset global domain registry."""
    global _domain_registry
    _domain_registry = None


def get_domain(name: str) -> Optional[BaseDomainPlugin]:
    """Get a domain by name."""
    return get_domain_registry().get(name)


def list_domains() -> Dict[str, str]:
    """List all available domains."""
    return get_domain_registry().list_domains()
