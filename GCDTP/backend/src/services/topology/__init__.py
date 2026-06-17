"""
Topology Module

Infrastructure topology analysis for electrical grids, water distribution,
and transport systems.
"""

from .topology_types import (
    TopologyNode,
    TopologyEdge,
    TopologyGraph,
    Path,
    FlowResult,
    NodeType,
    Layer,
    Direction,
    FlowType,
    FlowStatus,
)

from .graph_builder import GraphBuilder
from .flow_models import FlowModels
from .topology_engine import TopologyEngine
from .topology_validator import TopologyValidator, ValidationResult


__all__ = [
    # Types
    "TopologyNode",
    "TopologyEdge",
    "TopologyGraph",
    "Path",
    "FlowResult",
    # Enums
    "NodeType",
    "Layer",
    "Direction",
    "FlowType",
    "FlowStatus",
    # Classes
    "GraphBuilder",
    "FlowModels",
    "TopologyEngine",
    "TopologyValidator",
    "ValidationResult",
]
