"""
Cost Models

Defines how "distance" behaves across different infrastructure types.
Used by the routing engine to calculate path costs.
"""

from typing import Dict, Optional
from backend.src.services.topology import TopologyEdge


class CostModels:
    """
    Provides cost calculation models for different infrastructure domains.
    
    Cost is not just distance - it represents the "expense" of routing
    through an edge, considering resistance, capacity, and domain factors.
    """
    
    # Domain cost multipliers
    DOMAIN_FACTORS = {
        "electrical": 1.2,   # Power transmission is expensive
        "water": 1.0,         # Baseline
        "transport": 0.8,     # Traffic flows more freely
        "generic": 1.0,       # Default
    }
    
    # Capacity penalty thresholds
    HIGH_CAPACITY_THRESHOLD = 100.0
    LOW_CAPACITY_THRESHOLD = 10.0
    
    def compute_cost(
        self,
        edge: TopologyEdge,
        domain: str = "generic",
        current_load: float = 0.0
    ) -> float:
        """
        Compute the cost of traversing an edge.
        
        Args:
            edge: The topology edge
            domain: Infrastructure domain (electrical, water, transport)
            current_load: Current load on the edge (for dynamic costing)
            
        Returns:
            Cost value (higher = more expensive route)
        """
        # Base cost
        base_cost = 1.0
        
        # Resistance factor - higher resistance = higher cost
        resistance_factor = edge.resistance * 2.0
        
        # Capacity penalty - lower capacity = higher cost
        capacity_penalty = self._compute_capacity_penalty(edge.capacity)
        
        # Domain factor
        domain_factor = self.DOMAIN_FACTORS.get(domain, 1.0)
        
        # Load factor (optional - for dynamic routing)
        load_factor = self._compute_load_factor(edge.capacity, current_load)
        
        # Calculate total cost
        total_cost = (
            base_cost +
            resistance_factor +
            capacity_penalty * domain_factor +
            load_factor
        )
        
        return max(0.01, total_cost)  # Minimum cost of 0.01
    
    def _compute_capacity_penalty(self, capacity: float) -> float:
        """
        Compute capacity penalty.
        
        Lower capacity edges are penalized more heavily.
        """
        if capacity <= 0:
            return 100.0  # Severe penalty for no capacity
        
        if capacity >= self.HIGH_CAPACITY_THRESHOLD:
            return 0.1  # Low penalty for high capacity
        
        if capacity <= self.LOW_CAPACITY_THRESHOLD:
            return 10.0  # High penalty for low capacity
        
        # Linear interpolation
        return 10.0 * (self.HIGH_CAPACITY_THRESHOLD - capacity) / (
            self.HIGH_CAPACITY_THRESHOLD - self.LOW_CAPACITY_THRESHOLD
        )
    
    def _compute_load_factor(
        self,
        capacity: float,
        current_load: float
    ) -> float:
        """
        Compute load-based cost factor.
        
        Heavily loaded edges become more expensive to route through.
        """
        if capacity <= 0 or current_load <= 0:
            return 0.0
        
        utilization = current_load / capacity
        
        if utilization < 0.5:
            return 0.0  # No penalty for low utilization
        
        if utilization > 1.0:
            return 50.0  # Severe penalty for overloaded
        
        # Exponential penalty for high utilization
        # Penalty ranges from 0 at 50% to 20 at 100%
        return 20.0 * ((utilization - 0.5) / 0.5) ** 2
    
    def compute_path_cost(
        self,
        edges: list,
        domain: str = "generic"
    ) -> float:
        """
        Compute total cost of a path (list of edges).
        
        Args:
            edges: List of TopologyEdge objects
            domain: Infrastructure domain
            
        Returns:
            Total path cost
        """
        return sum(self.compute_cost(e, domain) for e in edges)
    
    def get_domain_factor(self, domain: str) -> float:
        """Get the cost multiplier for a domain."""
        return self.DOMAIN_FACTORS.get(domain, 1.0)
    
    def set_domain_factor(self, domain: str, factor: float) -> None:
        """Set a custom cost multiplier for a domain."""
        self.DOMAIN_FACTORS[domain] = factor


class ElectricalCostModel(CostModels):
    """
    Specialized cost model for electrical power systems.
    
    Factors in:
    - I²R power losses
    - Thermal limits
    - Grid stability margins
    """
    
    def __init__(self):
        super().__init__()
        self.DOMAIN_FACTORS["electrical"] = 1.5  # Higher base cost
    
    def compute_cost(
        self,
        edge: TopologyEdge,
        domain: str = "electrical",
        current_load: float = 0.0
    ) -> float:
        """Compute electrical routing cost with power-specific factors."""
        # Base cost from parent
        cost = super().compute_cost(edge, domain, current_load)
        
        # Add thermal margin factor
        if edge.capacity > 0:
            thermal_margin = 1.0 - (current_load / edge.capacity)
            if thermal_margin < 0.2:  # Less than 20% margin
                cost *= 2.0  # Double cost near thermal limit
        
        # Add resistance-based loss penalty (I²R approximation)
        if current_load > 0 and edge.capacity > 0:
            loss_factor = (current_load / edge.capacity) ** 2 * edge.resistance * 10
            cost += loss_factor
        
        return cost


class WaterCostModel(CostModels):
    """
    Specialized cost model for water distribution systems.
    
    Factors in:
    - Pressure drop along pipes
    - Pump energy costs
    - Pipe diameter/capacity
    """
    
    def __init__(self):
        super().__init__()
        self.DOMAIN_FACTORS["water"] = 1.0  # Baseline
    
    def compute_cost(
        self,
        edge: TopologyEdge,
        domain: str = "water",
        current_load: float = 0.0
    ) -> float:
        """Compute water routing cost with hydraulic factors."""
        cost = super().compute_cost(edge, domain, current_load)
        
        # Add pressure drop penalty (longer pipes = more pressure loss)
        if hasattr(edge, 'length') and edge.length:
            length_factor = edge.length * 0.01
            cost += length_factor
        
        # Add friction penalty (higher resistance = more friction loss)
        friction_penalty = edge.resistance * 5.0
        cost += friction_penalty
        
        return cost


class TransportCostModel(CostModels):
    """
    Specialized cost model for transport networks.
    
    Factors in:
    - Traffic congestion
    - Road capacity
    - Speed limits (implied by capacity)
    """
    
    def __init__(self):
        super().__init__()
        self.DOMAIN_FACTORS["transport"] = 0.8  # Lower base cost
    
    def compute_cost(
        self,
        edge: TopologyEdge,
        domain: str = "transport",
        current_load: float = 0.0
    ) -> float:
        """Compute transport routing cost with traffic factors."""
        cost = super().compute_cost(edge, domain, current_load)
        
        # Add congestion penalty
        if edge.capacity > 0:
            utilization = current_load / edge.capacity
            
            if utilization > 0.7:
                # Exponential congestion penalty
                congestion_factor = ((utilization - 0.7) / 0.3) ** 2 * 30
                cost += congestion_factor
        
        # Add delay factor for low-capacity edges (fewer lanes)
        if edge.capacity < 50:
            cost *= 1.5  # Multiply cost for low-capacity roads
        
        return cost


def get_cost_model(domain: str) -> CostModels:
    """
    Factory function to get the appropriate cost model for a domain.
    
    Args:
        domain: Infrastructure domain
        
    Returns:
        Appropriate CostModels subclass instance
    """
    models = {
        "electrical": ElectricalCostModel,
        "water": WaterCostModel,
        "transport": TransportCostModel,
    }
    
    model_class = models.get(domain, CostModels)
    return model_class()
