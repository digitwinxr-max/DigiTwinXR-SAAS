"""
Routing Interface

Interface definition for routing engines.
"""

from abc import abstractmethod
from typing import List, Optional, Dict, Any
from .base import IEngine


class IRoutingEngine(IEngine):
    """
    Interface for routing engines.
    
    Responsible for finding paths through a network.
    """
    
    @abstractmethod
    def find_route(
        self,
        graph: Any,
        start: str,
        end: str,
        **kwargs
    ) -> Optional[Any]:
        """
        Find a route from start to end.
        
        Args:
            graph: The topology graph
            start: Source node ID
            end: Destination node ID
            **kwargs: Additional parameters
            
        Returns:
            Route object or None if no path exists
        """
        pass
    
    @abstractmethod
    def find_all_routes(
        self,
        graph: Any,
        start: str,
        end: str,
        max_routes: int = 10,
        **kwargs
    ) -> List[Any]:
        """
        Find multiple routes from start to end.
        
        Args:
            graph: The topology graph
            start: Source node ID
            end: Destination node ID
            max_routes: Maximum number of routes to find
            **kwargs: Additional parameters
            
        Returns:
            List of Route objects
        """
        pass
    
    @abstractmethod
    def find_route_with_constraints(
        self,
        graph: Any,
        start: str,
        end: str,
        constraints: Dict[str, Any],
        **kwargs
    ) -> Optional[Any]:
        """
        Find a route that satisfies constraints.
        
        Args:
            graph: The topology graph
            start: Source node ID
            end: Destination node ID
            constraints: Route constraints
            **kwargs: Additional parameters
            
        Returns:
            Route object or None
        """
        pass
    
    @abstractmethod
    def get_reachable_nodes(
        self,
        graph: Any,
        start: str,
        **kwargs
    ) -> List[str]:
        """
        Get all nodes reachable from start.
        
        Args:
            graph: The topology graph
            start: Starting node ID
            **kwargs: Additional parameters
            
        Returns:
            List of reachable node IDs
        """
        pass
