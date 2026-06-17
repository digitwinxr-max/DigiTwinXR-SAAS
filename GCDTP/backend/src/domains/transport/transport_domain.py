"""
Transport Domain Plugin

Domain plugin for transport network infrastructure.
"""

from typing import Dict, Any, List
from ..base_domain import BaseDomainPlugin, DomainMetadata


class TransportDomain(BaseDomainPlugin):
    """
    Domain plugin for transport networks.
    
    Characteristics:
    - Low cost multiplier (0.8)
    - Higher tolerance for utilization (0.70 threshold)
    - Congestion modeling
    """
    
    def get_metadata(self) -> DomainMetadata:
        return DomainMetadata(
            name="transport",
            display_name="Transport Network",
            description="Road and rail transport networks",
            version="1.0.0",
            flow_unit="vehicles/h",
            cost_multiplier=0.8
        )
    
    def compute_cost(self, edge: Any, **kwargs) -> float:
        """Compute transport routing cost."""
        base = 1.0
        resistance_factor = edge.resistance * 1.5
        
        # Capacity penalty
        if edge.capacity < 100:
            capacity_penalty = 5.0
        elif edge.capacity < 500:
            capacity_penalty = 2.0
        else:
            capacity_penalty = 0.3
        
        # Congestion penalty
        current_load = kwargs.get("current_load", 0)
        congestion_penalty = 0.0
        if edge.capacity > 0:
            utilization = current_load / edge.capacity
            if utilization > 0.7:
                congestion_penalty = ((utilization - 0.7) / 0.3) ** 2 * 20
        
        # Domain multiplier
        domain_factor = 0.8
        
        return (base + resistance_factor + capacity_penalty + congestion_penalty) * domain_factor
    
    def compute_flow(
        self,
        edge: Any,
        load: float,
        **kwargs
    ) -> Dict[str, Any]:
        """Compute traffic flow."""
        utilization = load / max(edge.capacity, 1.0)
        
        # Flow rate (fundamental diagram - flow decreases at high density)
        base_flow = load
        if utilization > 0.8:
            # Reduced flow at high density
            flow_factor = 1.0 - ((utilization - 0.8) / 0.2) * 0.3
            base_flow *= flow_factor
        
        # Status determination
        if utilization >= 1.0:
            status = "congested"
        elif utilization >= 0.70:
            status = "heavy"
        else:
            status = "free"
        
        return {
            "utilization": utilization,
            "status": status,
            "overflow": max(0, load - edge.capacity),
            "flow_rate": base_flow,
            "congestion_level": min(1.0, utilization)
        }
    
    def validate_edge(self, edge: Any) -> List[str]:
        """Validate transport edge."""
        issues = []
        
        if edge.capacity <= 0:
            issues.append("Capacity must be positive for transport edges")
        
        if edge.capacity < 50:
            issues.append("Transport capacity should be at least 50 vehicles/h")
        
        if edge.resistance < 0:
            issues.append("Resistance cannot be negative")
        
        return issues
    
    def get_constraints(self) -> Dict[str, Any]:
        """Get transport domain constraints."""
        return {
            "max_utilization": 0.70,
            "min_capacity": 50.0,
            "congestion_threshold": 0.70
        }
    
    def get_custom_properties(self) -> Dict[str, type]:
        """Get transport-specific edge properties."""
        return {
            "lanes": int,
            "speed_limit": float,
            "road_type": str
        }
