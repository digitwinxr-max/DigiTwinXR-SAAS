"""
Agent Schemas

Pydantic schemas for Agent Framework API.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# Agent Definition Schemas
class AgentDefinitionCreate(BaseModel):
    """Schema for creating an agent definition."""
    name: str
    description: Optional[str] = None
    agent_type: str
    enabled: bool = True


class AgentDefinitionResponse(BaseModel):
    """Schema for agent definition response."""
    id: str
    name: str
    description: Optional[str] = None
    agent_type: str
    enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AgentDefinitionWithCapabilities(AgentDefinitionResponse):
    """Agent definition with capabilities."""
    capabilities: Dict[str, bool] = {}


# Task Schemas
class AgentTaskCreate(BaseModel):
    """Schema for creating an agent task."""
    agent_id: str
    task_type: str
    requested_by: str
    context_data: Dict[str, Any] = {}


class AgentTaskResponse(BaseModel):
    """Schema for agent task response."""
    id: str
    agent_id: str
    task_type: str
    status: str
    requested_by: str
    approved_by: Optional[str] = None
    created_at: datetime
    executed_at: Optional[datetime] = None
    context_data: Dict[str, Any] = {}
    result_data: Dict[str, Any] = {}

    class Config:
        from_attributes = True


class AgentTaskWithAgent(AgentTaskResponse):
    """Task with agent info."""
    agent_name: str = ""
    agent_type: str = ""


# Action Schemas
class AgentActionCreate(BaseModel):
    """Schema for creating an agent action."""
    task_id: str
    action_type: str
    action_payload: Dict[str, Any] = {}


class AgentActionResponse(BaseModel):
    """Schema for agent action response."""
    id: str
    task_id: str
    action_type: str
    action_payload: Dict[str, Any] = {}
    approval_status: str
    created_at: datetime
    executed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Approval Schemas
class TaskApprovalRequest(BaseModel):
    """Schema for task approval request."""
    approved_by: str
    notes: Optional[str] = None


class TaskRejectRequest(BaseModel):
    """Schema for task rejection request."""
    rejected_by: str
    reason: str


class ActionApprovalRequest(BaseModel):
    """Schema for action approval request."""
    approved_by: str
    notes: Optional[str] = None


class ActionRejectRequest(BaseModel):
    """Schema for action rejection request."""
    rejected_by: str
    reason: str


# Execution Schemas
class TaskExecutionRequest(BaseModel):
    """Schema for task execution request."""
    executed_by: str


class ActionExecutionRequest(BaseModel):
    """Schema for action execution request."""
    executed_by: str


# List Schemas
class AgentTaskListResponse(BaseModel):
    """Schema for task list response."""
    tasks: List[AgentTaskResponse]
    total: int


class PendingTasksResponse(BaseModel):
    """Schema for pending tasks response."""
    tasks: List[AgentTaskWithAgent]
    total: int


class TaskHistoryResponse(BaseModel):
    """Schema for task history response."""
    tasks: List[AgentTaskResponse]
    total: int


class AgentsResponse(BaseModel):
    """Schema for agents list response."""
    agents: List[AgentDefinitionWithCapabilities]
    total: int


# Summary Schemas
class AgentTaskStats(BaseModel):
    """Schema for task statistics."""
    agent_id: str
    total_tasks: int
    pending_tasks: int
    approved_tasks: int
    executed_tasks: int
    rejected_tasks: int
    failed_tasks: int


class TaskStatsResponse(BaseModel):
    """Schema for task stats response."""
    stats: List[AgentTaskStats]
