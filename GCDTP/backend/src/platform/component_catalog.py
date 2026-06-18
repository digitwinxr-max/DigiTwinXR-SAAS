"""
Component Catalog

Manages component catalog.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


class ComponentType(str):
    """Component types."""
    ENGINE = "engine"
    INTEGRATION = "integration"
    SECURITY = "security"
    OBSERVABILITY = "observability"
    PERFORMANCE = "performance"
    DEVOPS = "devops"


class ComponentStatus(str):
    """Component status."""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    REMOVED = "removed"
    BETA = "beta"
    PREVIEW = "preview"


@dataclass
class CatalogEntry:
    """Catalog entry."""
    name: str
    key: str
    component_type: ComponentType
    version: str
    status: ComponentStatus
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class ComponentCatalog:
    """
    Manages component catalog.
    
    Registers:
    - Core engines
    - Topology engines
    - Timeline engines
    - Ontology layer
    - Node-RED
    - EMQX
    - GeoServer
    - Neo4j
    - Cesium
    - Security
    - Observability
    - Performance
    - DevOps
    """
    
    def __init__(self):
        self._components: Dict[str, CatalogEntry] = {}
        self._initialize_defaults()
    
    def _initialize_defaults(self) -> None:
        """Initialize default components."""
        # Core
        self.register(CatalogEntry(
            name="EventBus",
            key="eventbus",
            component_type=ComponentType.ENGINE,
            version="1.0.0",
            status=ComponentStatus.ACTIVE,
            description="Event bus for system-wide events"
        ))
        
        # Integrations
        self.register(CatalogEntry(
            name="GeoServer Integration",
            key="geoserver",
            component_type=ComponentType.INTEGRATION,
            version="1.0.0",
            status=ComponentStatus.ACTIVE,
            description="GeoServer spatial data integration"
        ))
        
        self.register(CatalogEntry(
            name="Neo4j Integration",
            key="neo4j",
            component_type=ComponentType.INTEGRATION,
            version="1.0.0",
            status=ComponentStatus.ACTIVE,
            description="Neo4j graph database integration"
        ))
        
        self.register(CatalogEntry(
            name="EMQX Integration",
            key="emqx",
            component_type=ComponentType.INTEGRATION,
            version="1.0.0",
            status=ComponentStatus.ACTIVE,
            description="EMQX MQTT broker integration"
        ))
        
        self.register(CatalogEntry(
            name="Node-RED Integration",
            key="nodered",
            component_type=ComponentType.INTEGRATION,
            version="1.0.0",
            status=ComponentStatus.ACTIVE,
            description="Node-RED workflow integration"
        ))
        
        # Observability
        self.register(CatalogEntry(
            name="Observability Layer",
            key="observability",
            component_type=ComponentType.OBSERVABILITY,
            version="1.0.0",
            status=ComponentStatus.ACTIVE,
            description="Observability and diagnostics"
        ))
        
        # Performance
        self.register(CatalogEntry(
            name="Performance Layer",
            key="performance",
            component_type=ComponentType.PERFORMANCE,
            version="1.0.0",
            status=ComponentStatus.ACTIVE,
            description="Performance and scaling"
        ))
        
        # DevOps
        self.register(CatalogEntry(
            name="DevOps Layer",
            key="devops",
            component_type=ComponentType.DEVOPS,
            version="1.0.0",
            status=ComponentStatus.ACTIVE,
            description="Deployment and DevOps"
        ))
    
    def register(self, entry: CatalogEntry) -> None:
        """Register a component."""
        self._components[entry.key] = entry
    
    def get(self, key: str) -> Optional[CatalogEntry]:
        """Get a component."""
        return self._components.get(key)
    
    def get_all(self) -> List[CatalogEntry]:
        """Get all components."""
        return list(self._components.values())
    
    def get_by_type(self, component_type: ComponentType) -> List[CatalogEntry]:
        """Get components by type."""
        return [c for c in self._components.values() if c.component_type == component_type]
    
    def get_active(self) -> List[CatalogEntry]:
        """Get active components."""
        return [c for c in self._components.values() if c.status == ComponentStatus.ACTIVE]
    
    def update_status(self, key: str, status: ComponentStatus) -> bool:
        """Update component status."""
        component = self._components.get(key)
        if component:
            component.status = status
            return True
        return False
