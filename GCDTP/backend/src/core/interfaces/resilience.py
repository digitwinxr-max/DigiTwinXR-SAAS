"""
Resilience Interface

Interface definition for resilience engines.
"""

from abc import abstractmethod
from typing import List, Dict, Any
from .base import IEngine


class IResilienceEngine(IEngine):
    """
    Interface for resilience engines.
    
    Responsible for measuring network robustness and stability.
    """
    
    @abstractmethod
    def compute_resilience_score(
        self,
        graph: Any,
        route: Any,
        **kwargs
    ) -> Any:
        """
        Compute resilience score for a route.
        
        Args:
            graph: The topology graph
            route: Route to evaluate
            **kwargs: Additional parameters
            
        Returns:
            Resilience metrics object
        """
        pass
    
    @abstractmethod
    def compute_network_resilience(
        self,
        graph: Any,
        **kwargs
    ) -> Any:
        """
        Compute overall network resilience.
        
        Args:
            graph: The topology graph
            **kwargs: Additional parameters
            
        Returns:
            Network resilience result object
        """
        pass
    
    @abstractmethod
    def find_critical_nodes(
        self,
        graph: Any,
        **kwargs
    ) -> List[Any]:
        """
        Find critical nodes in the network.
        
        Args:
            graph: The topology graph
            **kwargs: Additional parameters
            
        Returns:
            List of (node_id, criticality_score) tuples
        """
        pass
    
    @abstractmethod
    def find_critical_edges(
        self,
        graph: Any,
        **kwargs
    ) -> List[Any]:
        """
        Find critical edges in the network.
        
        Args:
            graph: The topology graph
            **kwargs: Additional parameters
            
        Returns:
            List of (edge_id, is_critical) tuples
        """
        pass
    
    @abstractmethod
    def evaluate_route_alternatives(
        self,
        graph: Any,
        source: str,
        destination: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Evaluate resilience of alternative routes.
        
        Args:
            graph: The topology graph
            source: Source node
            destination: Destination node
            **kwargs: Additional parameters
            
        Returns:
            Dictionary mapping route keys to resilience metrics
        """
        pass
