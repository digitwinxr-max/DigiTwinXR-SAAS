"""
Engine Registry

Registry for simulation engines with hot-swapping support.
"""

from typing import Dict, Type, Optional, Any, List, Callable
from dataclasses import dataclass
from datetime import datetime


@dataclass
class EngineRegistration:
    """Registration info for an engine."""
    engine_class: Type
    name: str
    version: str
    description: str
    capabilities: List[str]
    registered_at: datetime
    default: bool = False


class EngineRegistry:
    """
    Registry for managing simulation engines.
    
    Features:
    - Register/unregister engines
    - Hot swapping
    - Multiple implementations
    - A/B testing support
    """
    
    def __init__(self):
        self._engines: Dict[str, Dict[str, EngineRegistration]] = {}
        self._factories: Dict[str, Callable] = {}
    
    def register(
        self,
        category: str,
        engine_class: Type,
        name: Optional[str] = None,
        version: str = "1.0.0",
        description: str = "",
        capabilities: Optional[List[str]] = None,
        default: bool = False,
        factory: Optional[Callable] = None
    ) -> None:
        """Register an engine."""
        engine_name = name or engine_class.__name__
        
        if category not in self._engines:
            self._engines[category] = {}
        
        registration = EngineRegistration(
            engine_class=engine_class,
            name=engine_name,
            version=version,
            description=description,
            capabilities=capabilities or [],
            registered_at=datetime.utcnow(),
            default=default
        )
        
        self._engines[category][engine_name] = registration
        
        if factory:
            self._factories[f"{category}:{engine_name}"] = factory
        
        if default:
            for reg in self._engines[category].values():
                reg.default = False
            registration.default = True
    
    def unregister(self, category: str, name: str) -> bool:
        """Unregister an engine."""
        if category in self._engines and name in self._engines[category]:
            del self._engines[category][name]
            factory_key = f"{category}:{name}"
            if factory_key in self._factories:
                del self._factories[factory_key]
            return True
        return False
    
    def get(self, category: str, name: Optional[str] = None) -> Optional[Type]:
        """Get an engine class."""
        if category not in self._engines:
            return None
        
        if name:
            reg = self._engines[category].get(name)
            return reg.engine_class if reg else None
        
        for reg in self._engines[category].values():
            if reg.default:
                return reg.engine_class
        
        if self._engines[category]:
            return next(iter(self._engines[category].values())).engine_class
        
        return None
    
    def create(self, category: str, name: Optional[str] = None, **kwargs) -> Optional[Any]:
        """Create an engine instance."""
        engine_class = self.get(category, name)
        if not engine_class:
            return None
        
        factory_key = f"{category}:{name or 'default'}"
        if factory_key in self._factories:
            return self._factories[factory_key](**kwargs)
        
        return engine_class(**kwargs)
    
    def list_engines(self, category: Optional[str] = None) -> Dict[str, List[str]]:
        """List all registered engines."""
        if category:
            if category in self._engines:
                return {category: list(self._engines[category].keys())}
            return {}
        
        return {
            cat: list(engines.keys())
            for cat, engines in self._engines.items()
        }
    
    def get_info(self, category: str, name: str) -> Optional[Dict]:
        """Get registration info."""
        if category in self._engines:
            reg = self._engines[category].get(name)
            if reg:
                return {
                    "name": reg.name,
                    "version": reg.version,
                    "description": reg.description,
                    "capabilities": reg.capabilities,
                    "registered_at": reg.registered_at.isoformat(),
                    "default": reg.default,
                }
        return None
    
    def get_default(self, category: str) -> Optional[str]:
        """Get default engine name."""
        if category in self._engines:
            for name, reg in self._engines[category].items():
                if reg.default:
                    return name
        return None
    
    def set_default(self, category: str, name: str) -> bool:
        """Set default engine."""
        if category in self._engines and name in self._engines[category]:
            for reg in self._engines[category].values():
                reg.default = False
            self._engines[category][name].default = True
            return True
        return False


_registry: Optional[EngineRegistry] = None


def get_registry() -> EngineRegistry:
    """Get global registry."""
    global _registry
    if _registry is None:
        _registry = EngineRegistry()
    return _registry


def reset_registry() -> None:
    """Reset global registry."""
    global _registry
    _registry = None


def register_engine(
    category: str,
    name: Optional[str] = None,
    version: str = "1.0.0",
    description: str = "",
    capabilities: Optional[List[str]] = None,
    default: bool = False
):
    """Decorator to register an engine."""
    def decorator(cls):
        registry = get_registry()
        registry.register(
            category=category,
            engine_class=cls,
            name=name or cls.__name__,
            version=version,
            description=description,
            capabilities=capabilities,
            default=default
        )
        return cls
    return decorator
