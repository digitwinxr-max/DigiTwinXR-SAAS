"""
Platform Registry

Manages platform module registry.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


class ModuleStatus(str):
    """Module status."""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    REMOVED = "removed"
    BETA = "beta"


@dataclass
class ModuleEntry:
    """Module registry entry."""
    name: str
    key: str
    module_type: str
    version: str
    status: ModuleStatus
    owner: str = ""
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    installed_at: Optional[datetime] = None


class PlatformRegistry:
    """
    Manages platform module registry.
    
    Tracks:
    - Modules
    - Versions
    - Dependencies
    - Statuses
    - Owners
    - Capabilities
    """
    
    def __init__(self):
        self._modules: Dict[str, ModuleEntry] = {}
        self._initialize_defaults()
    
    def _initialize_defaults(self) -> None:
        """Initialize default modules."""
        self.register(ModuleEntry(
            name="API",
            key="api",
            module_type="module",
            version="1.0.0",
            status=ModuleStatus.ACTIVE,
            owner="Platform Team",
            capabilities=["REST", "GraphQL"]
        ))
        
        self.register(ModuleEntry(
            name="EventBus",
            key="eventbus",
            module_type="module",
            version="1.0.0",
            status=ModuleStatus.ACTIVE,
            owner="Platform Team",
            capabilities=["Event Publishing", "Event Subscription"]
        ))
    
    def register(self, entry: ModuleEntry) -> None:
        """Register a module."""
        self._modules[entry.key] = entry
    
    def get(self, key: str) -> Optional[ModuleEntry]:
        """Get a module."""
        return self._modules.get(key)
    
    def get_all(self) -> List[ModuleEntry]:
        """Get all modules."""
        return list(self._modules.values())
    
    def get_by_type(self, module_type: str) -> List[ModuleEntry]:
        """Get modules by type."""
        return [m for m in self._modules.values() if m.module_type == module_type]
    
    def get_by_status(self, status: ModuleStatus) -> List[ModuleEntry]:
        """Get modules by status."""
        return [m for m in self._modules.values() if m.status == status]
    
    def update_status(self, key: str, status: ModuleStatus) -> bool:
        """Update module status."""
        module = self._modules.get(key)
        if module:
            module.status = status
            return True
        return False
    
    def mark_installed(self, key: str) -> bool:
        """Mark module as installed."""
        module = self._modules.get(key)
        if module:
            module.installed_at = datetime.utcnow()
            return True
        return False
    
    def get_dependencies(self, key: str) -> List[str]:
        """Get module dependencies."""
        module = self._modules.get(key)
        return module.dependencies if module else []
