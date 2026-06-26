"""
Node-RED Integration Module

External orchestration layer for FastAPI.
FastAPI remains authoritative for business logic.

Components:
- Node-RED Client
- Workflow Adapter
- Flow Manager
- Connector Registry
- Workflow Validator
"""

from .workflow_types import (
    ExecutionStatus,
    TriggerType,
    ConnectorType,
    WorkflowTrigger,
    Connector,
    WorkflowDefinition,
    WorkflowInstance,
    WorkflowExecution,
    WorkflowSummary,
)

from .node_red_client import NodeREDClient, NodeREDClientError, NodeREDStatus, NodeREDFlowBuilder
from .workflow_adapter import WorkflowAdapter
from .flow_manager import FlowManager
from .connector_registry import ConnectorRegistry, ConnectorConfig
from .workflow_validator import WorkflowValidator


__all__ = [
    # Enums
    "ExecutionStatus",
    "TriggerType",
    "ConnectorType",
    "NodeREDStatus",
    # Types
    "WorkflowTrigger",
    "Connector",
    "WorkflowDefinition",
    "WorkflowInstance",
    "WorkflowExecution",
    "WorkflowSummary",
    # Client
    "NodeREDClient",
    "NodeREDClientError",
    "NodeREDFlowBuilder",
    # Managers
    "WorkflowAdapter",
    "FlowManager",
    "ConnectorRegistry",
    "ConnectorConfig",
    # Validators
    "WorkflowValidator",
]
