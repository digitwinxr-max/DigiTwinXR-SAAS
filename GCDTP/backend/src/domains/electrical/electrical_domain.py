"""
Electrical Domain Plugin

Domain plugin for electrical power grid infrastructure.
"""

from typing import Dict, Any, List
from ..base_domain import BaseDomainPlugin, DomainMetadata


class ElectricalDomain(BaseDomainPlugin):
    """
    Domain plugin for electrical power systems.
    
    Characteristics:
    - High cost multiplier (1.2)
    - Tight capacity margins (0.85 threshold)
    - Power loss modeling (I²R)
    """
    
    def get_metadata(self) -> DomainMetadata:
        return DomainMetadata(
            name="electrical",
            display_name="Electrical Grid",
            description="Electrical power transmission and distribution",
            version="1.0.0",
            flow_unit="MW",
            cost_multiplier=1.2
        )
    
    def compute_cost(self, edge: Any, **kwargs) -> float:
        """Compute electrical routing cost."""
        # Base cost with resistance
        base = 1.0
        resistance_factor = edge.resistance * 3.0  # Higher resistance impact
        
        # Capacity penalty
        if edge.capacity < 50:
            capacity_penalty = 15.0
        elif edge.capacity < 100:
            capacity_penalty = 5.0
        else:
            capacity_penalty = 0.5
        
        # Domain multiplier
        domain_factor = 1.2
        
        # Thermal margin penalty
        current_load = kwargs.get("current_load", 0)
        if edge.capacity > 0 and current_load > 0:
            thermal_margin = 1.0 - (current_load / edge.capacity)
            if thermal_margin < 0.2:
                capacity_penalty *= 2.0  # Double penalty near thermal limit
        
        return (base + resistance_factor + capacity_penalty) * domain_factor
    
    def compute_flow(
        self,
        edge: Any,
        load: float,
        **kwargs
    ) -> Dict[str, Any]:
        """Compute electrical power flow."""
        utilization = load / max(edge.capacity, 1.0)
        
        # Power loss (I²R approximation)
        power_loss = 0.0
        if load > 0 and edge.resistance > 0:
            # P_loss = I²R, approximated as load² * resistance
            power_loss = (load ** 2) * edge.resistance * 0.01
        
        # Status determination
        if utilization >= 1.0:
            status = "overloaded"
        elif utilization >= 0.85:
            status = "degraded"
        else:
            status = "stable"
        
        return {
            "utilization": utilization,
            "status": status,
            "overflow": max(0, load - edge.capacity),
            "power_loss": power_loss,
            "thermal_margin": max(0, 1.0 - utilization)
        }
    
    def validate_edge(self, edge: Any) -> List[str]:
        """Validate electrical edge."""
        issues = []
        
        if edge.capacity <= 0:
            issues.append("Capacity must be positive for electrical edges")
        
        if edge.capacity < 10:
            issues.append("Electrical capacity should be at least 10 MW")
        
        if edge.resistance < 0:
            issues.append("Resistance cannot be negative")
        
        if edge.resistance > 1.0:
            issues.append("High resistance may cause significant power loss")
        
        return issues
    
    def get_constraints(self) -> Dict[str, Any]:
        """Get electrical domain constraints."""
        return {
            "max_utilization": 0.85,
            "min_capacity": 10.0,
            "max_resistance": 1.0,
            "thermal_limit_buffer": 0.15
        }
    
    def get_custom_properties(self) -> Dict[str, type]:
        """Get electrical-specific edge properties."""
        return {
            "voltage_level": str,
            "line_type": str,
            "impedance": float
        }
