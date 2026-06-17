"""
Water Domain Plugin

Domain plugin for water distribution infrastructure.
"""

from typing import Dict, Any, List
from ..base_domain import BaseDomainPlugin, DomainMetadata


class WaterDomain(BaseDomainPlugin):
    """
    Domain plugin for water distribution systems.
    
    Characteristics:
    - Baseline cost multiplier (1.0)
    - Moderate capacity margins (0.75 threshold)
    - Pressure drop modeling
    """
    
    def get_metadata(self) -> DomainMetadata:
        return DomainMetadata(
            name="water",
            display_name="Water Distribution",
            description="Water transmission and distribution",
            version="1.0.0",
            flow_unit="m3/h",
            cost_multiplier=1.0
        )
    
    def compute_cost(self, edge: Any, **kwargs) -> float:
        """Compute water routing cost."""
        base = 1.0
        resistance_factor = edge.resistance * 2.0
        
        # Capacity penalty
        if edge.capacity < 100:
            capacity_penalty = 8.0
        elif edge.capacity < 500:
            capacity_penalty = 3.0
        else:
            capacity_penalty = 0.5
        
        # Length penalty (longer pipes = more pressure drop)
        length_penalty = 0.0
        if hasattr(edge, 'length') and edge.length:
            length_penalty = edge.length * 0.01
        
        # Domain multiplier
        domain_factor = 1.0
        
        return (base + resistance_factor + capacity_penalty + length_penalty) * domain_factor
    
    def compute_flow(
        self,
        edge: Any,
        load: float,
        **kwargs
    ) -> Dict[str, Any]:
        """Compute water flow."""
        utilization = load / max(edge.capacity, 1.0)
        
        # Pressure drop (Darcy-Weisbach approximation)
        pressure_drop = 0.0
        if hasattr(edge, 'length') and edge.length:
            # Simplified pressure drop calc
            pressure_drop = edge.length * edge.resistance * (load / edge.capacity) * 0.1
        
        # Status determination
        if utilization >= 1.0:
            status = "blocked"
        elif utilization >= 0.75:
            status = "degraded"
        else:
            status = "stable"
        
        return {
            "utilization": utilization,
            "status": status,
            "overflow": max(0, load - edge.capacity),
            "pressure_drop": pressure_drop,
            "flow_rate": load
        }
    
    def validate_edge(self, edge: Any) -> List[str]:
        """Validate water edge."""
        issues = []
        
        if edge.capacity <= 0:
            issues.append("Capacity must be positive for water pipes")
        
        if edge.capacity < 10:
            issues.append("Water capacity should be at least 10 m3/h")
        
        if edge.resistance < 0:
            issues.append("Resistance cannot be negative")
        
        return issues
    
    def get_constraints(self) -> Dict[str, Any]:
        """Get water domain constraints."""
        return {
            "max_utilization": 0.75,
            "min_capacity": 10.0,
            "pressure_loss_coefficient": 0.1
        }
    
    def get_custom_properties(self) -> Dict[str, type]:
        """Get water-specific edge properties."""
        return {
            "diameter": float,
            "material": str,
            "age": int
        }
