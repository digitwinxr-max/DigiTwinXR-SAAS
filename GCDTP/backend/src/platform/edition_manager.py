"""
Edition Manager

Manages platform editions.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


class EditionType(str):
    """Edition types."""
    COMMUNITY = "community"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    GOVERNMENT = "government"
    UTILITY = "utility"
    INDUSTRIAL = "industrial"
    CUSTOM = "custom"


@dataclass
class PlatformEdition:
    """Platform edition."""
    name: str
    edition_type: EditionType
    description: str = ""
    features: List[str] = field(default_factory=list)
    is_active: bool = True


class EditionManager:
    """
    Manages platform editions.
    """
    
    def __init__(self):
        self._editions: Dict[str, PlatformEdition] = {}
        self._initialize_defaults()
    
    def _initialize_defaults(self) -> None:
        """Initialize default editions."""
        self.create_edition(
            name="Community Edition",
            edition_type=EditionType.COMMUNITY,
            description="Free community edition",
            features=["Basic features", "Community support"]
        )
        
        self.create_edition(
            name="Professional Edition",
            edition_type=EditionType.PROFESSIONAL,
            description="Professional edition with advanced features",
            features=["All community features", "Email support", "Advanced analytics"]
        )
        
        self.create_edition(
            name="Enterprise Edition",
            edition_type=EditionType.ENTERPRISE,
            description="Full enterprise edition",
            features=["All professional features", "24/7 support", "SLA guarantee", "Custom integrations"]
        )
        
        self.create_edition(
            name="Government Edition",
            edition_type=EditionType.GOVERNMENT,
            description="Government-specific edition",
            features=["All enterprise features", "FedRAMP compliance", "Government support"]
        )
    
    def create_edition(
        self,
        name: str,
        edition_type: EditionType,
        description: str = "",
        features: Optional[List[str]] = None
    ) -> PlatformEdition:
        """Create an edition."""
        edition = PlatformEdition(
            name=name,
            edition_type=edition_type,
            description=description,
            features=features or []
        )
        self._editions[name] = edition
        return edition
    
    def get_edition(self, name: str) -> Optional[PlatformEdition]:
        """Get an edition."""
        return self._editions.get(name)
    
    def get_all_editions(self) -> List[PlatformEdition]:
        """Get all editions."""
        return list(self._editions.values())
    
    def get_active_editions(self) -> List[PlatformEdition]:
        """Get active editions."""
        return [e for e in self._editions.values() if e.is_active]
