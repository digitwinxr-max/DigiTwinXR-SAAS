"""
Workflow Types

Core data types for Node-RED workflow integration.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from enum import Enum


class ExecutionStatus(str, Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TriggerType(str, Enum):
    """Workflow trigger type."""
    EVENTBUS = "eventbus"
    TIMELINE = "timeline"
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    ASSET_EVENT = "asset_event"
    WORKORDER_EVENT = "workorder_event"
    DOCUMENT_EVENT = "document_event"


class ConnectorType(str, Enum):
    """Connector type."""
    HTTP = "http"
    REST = "rest"
    WEBHOOK = "webhook"
    FILE = "file"
    EMAIL = "email"
    MQTT = "mqtt"
    GEOSERVER = "geoserver"
    EMQX = "emqx"


@dataclass
class WorkflowTrigger:
    """Workflow trigger configuration."""
    type: TriggerType
    config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "type": self.type.value,
            "config": self.config,
        }


@dataclass
class Connector:
    """External connector for workflows."""
    id: str
    connector_type: ConnectorType
    name: str
    config: Dict[str, Any] = field(default_factory=dict)
    is_enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "connector_type": self.connector_type.value,
            "name": self.name,
            "config": self.config,
            "is_enabled": self.is_enabled,
        }


@dataclass
class WorkflowDefinition:
    """
    Workflow definition (Node-RED flow).
    """
    id: str
    name: str
    flow_json: Dict[str, Any]
    trigger_type: TriggerType = TriggerType.MANUAL
    description: str = ""
    
    # Trigger configuration
    trigger_config: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    is_enabled: bool = True
    is_template: bool = False
    version: int = 1
    
    # Audit
    created_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Stats
    last_executed_at: Optional[datetime] = None
    execution_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "flow_json": self.flow_json,
            "trigger_type": self.trigger_type.value,
            "trigger_config": self.trigger_config,
            "is_enabled": self.is_enabled,
            "is_template": self.is_template,
            "version": self.version,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_executed_at": self.last_executed_at.isoformat() if self.last_executed_at else None,
            "execution_count": self.execution_count,
        }


@dataclass
class WorkflowInstance:
    """
    Workflow execution instance.
    """
    id: str
    workflow_id: str
    name: str = ""
    status: ExecutionStatus = ExecutionStatus.PENDING
    
    # Data
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    
    # Error
    error_message: str = ""
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Retry
    retry_count: int = 0
    max_retries: int = 3
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "name": self.name,
            "status": self.status.value,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
        }
    
    @property
    def is_running(self) -> bool:
        """Check if instance is running."""
        return self.status == ExecutionStatus.RUNNING
    
    @property
    def is_completed(self) -> bool:
        """Check if instance is completed."""
        return self.status == ExecutionStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if instance failed."""
        return self.status == ExecutionStatus.FAILED
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


@dataclass
class WorkflowExecution:
    """
    Node-level execution record.
    """
    id: str
    workflow_id: str
    status: ExecutionStatus
    execution_order: int = 1
    
    # References
    instance_id: Optional[str] = None
    node_id: str = ""
    node_name: str = ""
    
    # Data
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    
    # Error
    error_message: str = ""
    
    # Timing
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "instance_id": self.instance_id,
            "node_id": self.node_id,
            "node_name": self.node_name,
            "status": self.status.value,
            "execution_order": self.execution_order,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_ms": self.duration_ms,
        }


@dataclass
class WorkflowSummary:
    """Summary view of a workflow."""
    workflow: WorkflowDefinition
    total_instances: int = 0
    running_instances: int = 0
    failed_instances: int = 0
    connector_count: int = 0
    
    def to_dict(self) -> Dict:
        data = self.workflow.to_dict()
        data["total_instances"] = self.total_instances
        data["running_instances"] = self.running_instances
        data["failed_instances"] = self.failed_instances
        data["connector_count"] = self.connector_count
        return data
