"""
Flow Models

Physics abstraction layer for flow calculations.
Supports electrical, water, and transport flow types.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from .topology_types import TopologyEdge, FlowType, FlowStatus


@dataclass
class FlowResult:
    """Result of a single flow calculation."""
    status: FlowStatus
    utilization: float
    overflow: float = 0.0
    message: str = ""


class FlowModels:
    """
    Provides flow calculation models for different infrastructure types.
    
    Flow Types:
    - power: Electrical power flow
    - water: Water/pressure flow
    - traffic: Transport flow
    - generic: Default flow model
    """
    
    def __init__(self):
        self.flow_calculators = {
            FlowType.POWER.value: self._calculate_power_flow,
            FlowType.WATER.value: self._calculate_water_flow,
            FlowType.TRAFFIC.value: self._calculate_traffic_flow,
            FlowType.GENERIC.value: self._calculate_generic_flow,
        }
    
    def calculate_flow(self, edge: TopologyEdge, load: float) -> FlowResult:
        """
        Calculate flow through an edge given incoming load.
        
        Args:
            edge: The topology edge
            load: Current load on the edge
            
        Returns:
            FlowResult with status and utilization
        """
        calculator = self.flow_calculators.get(
            edge.flow_type,
            self._calculate_generic_flow
        )
        return calculator(edge, load)
    
    def _calculate_generic_flow(self, edge: TopologyEdge, load: float) -> FlowResult:
        """
        Generic flow calculation model.
        
        Formula:
            effective_capacity = capacity - resistance
            utilization = load / effective_capacity
            
        Status:
            - STABLE: utilization < 0.8
            - DEGRADED: 0.8 <= utilization < 1.0
            - OVERLOADED: utilization >= 1.0
        """
        effective_capacity = edge.effective_capacity()
        
        if effective_capacity <= 0:
            return FlowResult(
                status=FlowStatus.BLOCKED,
                utilization=1.0,
                overflow=load,
                message="No effective capacity"
            )
        
        utilization = load / effective_capacity
        
        if utilization >= 1.0:
            return FlowResult(
                status=FlowStatus.OVERLOADED,
                utilization=utilization,
                overflow=(utilization - 1.0) * effective_capacity,
                message="Flow exceeds capacity"
            )
        elif utilization >= 0.8:
            return FlowResult(
                status=FlowStatus.DEGRADED,
                utilization=utilization,
                message="Flow approaching capacity"
            )
        else:
            return FlowResult(
                status=FlowStatus.STABLE,
                utilization=utilization,
                message="Flow within limits"
            )
    
    def _calculate_power_flow(self, edge: TopologyEdge, load: float) -> FlowResult:
        """
        Electrical power flow model.
        
        Considerations:
        - Line resistance causes power loss (I²R)
        - Power loss increases with square of current
        - Capacity based on thermal limits
        
        Returns:
            FlowResult with power-specific metrics
        """
        effective_capacity = edge.capacity - (edge.resistance * 0.5)
        
        if effective_capacity <= 0:
            return FlowResult(
                status=FlowStatus.BLOCKED,
                utilization=1.0,
                overflow=load,
                message="Line overloaded"
            )
        
        utilization = load / effective_capacity
        
        # Power lines have tighter margins
        if utilization >= 1.0:
            return FlowResult(
                status=FlowStatus.OVERLOADED,
                utilization=utilization,
                overflow=(utilization - 1.0) * effective_capacity,
                message="Power line thermal limit exceeded"
            )
        elif utilization >= 0.85:
            return FlowResult(
                status=FlowStatus.DEGRADED,
                utilization=utilization,
                message="Power line operating near capacity"
            )
        else:
            return FlowResult(
                status=FlowStatus.STABLE,
                utilization=utilization,
                message="Power flow stable"
            )
    
    def _calculate_water_flow(self, edge: TopologyEdge, load: float) -> FlowResult:
        """
        Water distribution flow model.
        
        Considerations:
        - Pressure drop along pipes (Darcy-Weisbach)
        - Capacity based on pipe diameter
        - Resistance represents friction loss
        
        Returns:
            FlowResult with water-specific metrics
        """
        # Water systems can handle higher utilization before degradation
        effective_capacity = edge.capacity - (edge.resistance * 0.3)
        
        if effective_capacity <= 0:
            return FlowResult(
                status=FlowStatus.BLOCKED,
                utilization=1.0,
                overflow=load,
                message="Pipe blocked or no flow"
            )
        
        utilization = load / effective_capacity
        
        if utilization >= 1.0:
            return FlowResult(
                status=FlowStatus.OVERLOADED,
                utilization=utilization,
                overflow=(utilization - 1.0) * effective_capacity,
                message="Pressure drop too severe"
            )
        elif utilization >= 0.75:
            return FlowResult(
                status=FlowStatus.DEGRADED,
                utilization=utilization,
                message="Low pressure conditions"
            )
        else:
            return FlowResult(
                status=FlowStatus.STABLE,
                utilization=utilization,
                message="Water pressure adequate"
            )
    
    def _calculate_traffic_flow(self, edge: TopologyEdge, load: float) -> FlowResult:
        """
        Traffic/transport flow model.
        
        Considerations:
        - Capacity based on lanes and road type
        - Flow decreases at high densities (fundamental diagram)
        - Resistance represents congestion/friction
        
        Returns:
            FlowResult with traffic-specific metrics
        """
        # Traffic has unique flow characteristics
        # At very high loads, flow actually decreases
        base_capacity = edge.capacity
        congestion_factor = 1.0 - (edge.resistance * load * 0.1)
        effective_capacity = base_capacity * max(0.3, congestion_factor)
        
        if effective_capacity <= 0:
            return FlowResult(
                status=FlowStatus.BLOCKED,
                utilization=1.0,
                overflow=load,
                message="Road blocked"
            )
        
        utilization = load / base_capacity  # Compare to raw capacity
        
        if utilization >= 1.0:
            return FlowResult(
                status=FlowStatus.OVERLOADED,
                utilization=utilization,
                overflow=(utilization - 1.0) * base_capacity,
                message="Traffic congestion/freeze"
            )
        elif utilization >= 0.7:
            return FlowResult(
                status=FlowStatus.DEGRADED,
                utilization=utilization,
                message="Heavy traffic conditions"
            )
        else:
            return FlowResult(
                status=FlowStatus.STABLE,
                utilization=utilization,
                message="Traffic flowing freely"
            )
    
    def propagate_flow(
        self,
        edges: List[TopologyEdge],
        source_loads: Dict[str, float]
    ) -> Dict[str, Dict[str, float]]:
        """
        Propagate flow through multiple edges from source nodes.
        
        Args:
            edges: List of edges in the network
            source_loads: Load at each source node
            
        Returns:
            Dictionary mapping edge keys to flow results
        """
        results = {}
        
        for edge in edges:
            edge_key = f"{edge.from_node}->{edge.to_node}"
            load = source_loads.get(edge.from_node, 0)
            result = self.calculate_flow(edge, load)
            results[edge_key] = {
                "status": result.status.value,
                "utilization": result.utilization,
                "overflow": result.overflow,
            }
        
        return results
    
    def calculate_network_load(
        self,
        edges: List[TopologyEdge],
        node_loads: Dict[str, float]
    ) -> Tuple[Dict[str, float], List[str]]:
        """
        Calculate total load on each edge and identify overloaded edges.
        
        Args:
            edges: List of edges
            node_loads: Load at each node
            
        Returns:
            Tuple of (edge_loads, overloaded_edge_keys)
        """
        edge_loads = {}
        overloaded = []
        
        for edge in edges:
            edge_key = f"{edge.from_node}->{edge.to_node}"
            
            # Get incoming load from source node
            load = node_loads.get(edge.from_node, 0)
            edge_loads[edge_key] = load
            
            # Check for overload
            result = self.calculate_flow(edge, load)
            if result.status == FlowStatus.OVERLOADED:
                overloaded.append(edge_key)
        
        return edge_loads, overloaded
