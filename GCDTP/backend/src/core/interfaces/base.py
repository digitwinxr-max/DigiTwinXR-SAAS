"""
Core Interfaces

Abstract base interfaces for all simulation engines.
These interfaces define the contract between engines and the rest of the system.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class EngineMetadata:
    """Metadata for an engine."""
    name: str
    version: str
    description: str
    capabilities: List[str]


class IEngine(ABC):
    """
    Base interface for all engines.
    
    All engines must implement this interface.
    """
    
    @abstractmethod
    def get_metadata(self) -> EngineMetadata:
        """Get engine metadata."""
        pass
    
    @abstractmethod
    def validate_input(self, **kwargs) -> bool:
        """Validate engine input parameters."""
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset engine state."""
        pass


class IStrategy(ABC):
    """
    Base interface for algorithm strategies.
    
    Strategies can be swapped at runtime.
    """
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the strategy."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get strategy name."""
        pass
