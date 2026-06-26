"""
Domain Base

Base class for infrastructure domain plugins.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class DomainMetadata:
    """Metadata for a domain plugin."""
    name: str
    display_name: str
    description: str
    version: str
    flow_unit: str
    cost_multiplier: float


class BaseDomainPlugin(ABC):
    """
    Base class for infrastructure domain plugins.
    
    Each domain (electrical, water, transport) implements this interface
    to provide domain-specific behavior.
    """
    
    @abstractmethod
    def get_metadata(self) -> DomainMetadata:
        """Get domain metadata."""
        pass
    
    @abstractmethod
    def compute_cost(self, edge: Any, **kwargs) -> float:
        """
        Compute cost for traversing an edge in this domain.
        
        Args:
            edge: The topology edge
            **kwargs: Additional parameters
            
        Returns:
            Cost value
        """
        pass
    
    @abstractmethod
    def compute_flow(
        self,
        edge: Any,
        load: float,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Compute flow through an edge.
        
        Args:
            edge: The topology edge
            load: Current load
            **kwargs: Additional parameters
            
        Returns:
            Flow result dictionary
        """
        pass
    
    @abstractmethod
    def validate_edge(self, edge: Any) -> List[str]:
        """
        Validate an edge for this domain.
        
        Args:
            edge: The topology edge
            
        Returns:
            List of validation issues
        """
        pass
    
    def get_constraints(self) -> Dict[str, Any]:
        """Get domain-specific constraints."""
        return {}
    
    def get_custom_properties(self) -> Dict[str, type]:
        """Get custom properties for edges in this domain."""
        return {}


class GenericDomain(BaseDomainPlugin):
    """Generic domain with default behavior."""
    
    def get_metadata(self) -> DomainMetadata:
        return DomainMetadata(
            name="generic",
            display_name="Generic",
            description="Generic infrastructure domain",
            version="1.0.0",
            flow_unit="units",
            cost_multiplier=1.0
        )
    
    def compute_cost(self, edge: Any, **kwargs) -> float:
        base = 1.0
        resistance_factor = edge.resistance * 2.0
        capacity_penalty = 10.0 / max(edge.capacity, 0.1)
        return base + resistance_factor + capacity_penalty
    
    def compute_flow(
        self,
        edge: Any,
        load: float,
        **kwargs
    ) -> Dict[str, Any]:
        utilization = load / max(edge.capacity, 1.0)
        status = "stable" if utilization < 0.8 else "degraded" if utilization < 1.0 else "overloaded"
        return {
            "utilization": utilization,
            "status": status,
            "overflow": max(0, load - edge.capacity)
        }
    
    def validate_edge(self, edge: Any) -> List[str]:
        issues = []
        if edge.capacity <= 0:
            issues.append("Capacity must be positive")
        if edge.resistance < 0:
            issues.append("Resistance cannot be negative")
        return issues
