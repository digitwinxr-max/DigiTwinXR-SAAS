"""
Flow Interface

Interface definition for flow engines.
"""

from abc import abstractmethod
from typing import List, Dict, Any
from .base import IEngine


class IFlowEngine(IEngine):
    """
    Interface for flow engines.
    
    Responsible for flow allocation and load distribution.
    """
    
    @abstractmethod
    def simulate_flow(
        self,
        graph: Any,
        route: Any,
        load: float,
        **kwargs
    ) -> Any:
        """
        Simulate flow on a route.
        
        Args:
            graph: The topology graph
            route: Route to simulate flow on
            load: Amount of load to simulate
            **kwargs: Additional parameters
            
        Returns:
            Flow result object
        """
        pass
    
    @abstractmethod
    def allocate_flow(
        self,
        route: Any,
        total_load: float,
        strategy: str = "equal",
        **kwargs
    ) -> Any:
        """
        Allocate flow across a route.
        
        Args:
            route: Route to allocate flow on
            total_load: Total load to allocate
            strategy: Allocation strategy
            **kwargs: Additional parameters
            
        Returns:
            Flow allocation object
        """
        pass
    
    @abstractmethod
    def detect_overload(
        self,
        allocations: List[Any],
        **kwargs
    ) -> List[Any]:
        """
        Detect overloaded edges.
        
        Args:
            allocations: List of flow allocations
            **kwargs: Additional parameters
            
        Returns:
            List of overloaded allocations
        """
        pass
    
    @abstractmethod
    def balance_load(
        self,
        graph: Any,
        routes: List[Any],
        total_load: float,
        **kwargs
    ) -> List[Any]:
        """
        Balance load across multiple routes.
        
        Args:
            graph: The topology graph
            routes: List of routes
            total_load: Total load to balance
            **kwargs: Additional parameters
            
        Returns:
            List of flow distributions
        """
        pass
