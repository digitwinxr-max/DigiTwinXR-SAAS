"""
Agent Routes

FastAPI routes for Agent Framework API.
Agents propose - humans approve - execution follows.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from ..schemas.agent import (
    AgentDefinitionCreate,
    AgentDefinitionResponse,
    AgentDefinitionWithCapabilities,
    AgentTaskCreate,
    AgentTaskResponse,
    AgentTaskWithAgent,
    AgentActionCreate,
    AgentActionResponse,
    TaskApprovalRequest,
    TaskRejectRequest,
    TaskExecutionRequest,
    AgentTaskListResponse,
    PendingTasksResponse,
    TaskHistoryResponse,
    AgentsResponse,
    TaskStatsResponse,
    AgentTaskStats
)
from ..services.agent_service import agent_service


router = APIRouter(prefix="/agent", tags=["agent"])


# Agent Definition Routes
@router.get("/agents", response_model=AgentsResponse)
async def get_agents():
    """
    Get all available agents.
    
    Returns agent definitions with capabilities.
    """
    agents = agent_service.get_all_agents()
    
    agent_responses = [
        AgentDefinitionWithCapabilities(
            id=a.id,
            name=a.name,
            description=a.description,
            agent_type=a.agent_type.value,
            enabled=a.enabled,
            created_at=a.created_at,
            capabilities=a.get_capabilities()
        )
        for a in agents
    ]
    
    return AgentsResponse(
        agents=agent_responses,
        total=len(agent_responses)
    )


@router.get("/agent/{agent_id}", response_model=AgentDefinitionWithCapabilities)
async def get_agent(agent_id: str):
    """
    Get a specific agent.
    """
    agent = agent_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return AgentDefinitionWithCapabilities(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        agent_type=agent.agent_type.value,
        enabled=agent.enabled,
        created_at=agent.created_at,
        capabilities=agent.get_capabilities()
    )


# Task Routes
@router.post("/task", response_model=AgentTaskResponse)
async def create_task(request: AgentTaskCreate):
    """
    Create a new agent task.
    
    Task is created in pending status and requires approval.
    """
    try:
        task = agent_service.create_task(request)
        return task.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tasks", response_model=AgentTaskListResponse)
async def get_tasks(
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get tasks with optional filters.
    """
    tasks = agent_service.get_tasks(
        agent_id=agent_id,
        status=status,
        limit=limit,
        offset=offset
    )
    
    return AgentTaskListResponse(
        tasks=[t.to_dict() for t in tasks],
        total=len(tasks)
    )


@router.get("/task/{task_id}", response_model=AgentTaskResponse)
async def get_task(task_id: str):
    """
    Get a specific task.
    """
    task = agent_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task.to_dict()


# Approval Routes
@router.post("/task/{task_id}/approve", response_model=AgentTaskResponse)
async def approve_task(task_id: str, request: TaskApprovalRequest):
    """
    Approve a task.
    
    After approval, task can be executed.
    """
    try:
        task = agent_service.approve_task(task_id, request)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/task/{task_id}/reject", response_model=AgentTaskResponse)
async def reject_task(task_id: str, request: TaskRejectRequest):
    """
    Reject a task.
    
    Rejected tasks are not executed.
    """
    try:
        task = agent_service.reject_task(task_id, request)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Execution Routes
@router.post("/task/{task_id}/execute", response_model=AgentTaskResponse)
async def execute_task(task_id: str, request: TaskExecutionRequest):
    """
    Execute an approved task.
    
    Only approved tasks can be executed.
    """
    try:
        task = agent_service.execute_task(task_id, request.executed_by)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Pending Routes
@router.get("/pending", response_model=PendingTasksResponse)
async def get_pending_tasks():
    """
    Get all pending tasks awaiting approval.
    """
    tasks = agent_service.get_pending_tasks()
    
    task_responses = []
    for task in tasks:
        agent = agent_service.get_agent(task.agent_id)
        task_responses.append(AgentTaskWithAgent(
            id=task.id,
            agent_id=task.agent_id,
            task_type=task.task_type,
            status=task.status.value,
            requested_by=task.requested_by,
            approved_by=task.approved_by,
            created_at=task.created_at,
            executed_at=task.executed_at,
            context_data=task.context_data,
            result_data=task.result_data,
            agent_name=agent.name if agent else "Unknown",
            agent_type=agent.agent_type.value if agent else "Unknown"
        ))
    
    return PendingTasksResponse(
        tasks=task_responses,
        total=len(task_responses)
    )


# History Routes
@router.get("/history", response_model=TaskHistoryResponse)
async def get_history(
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get task execution history.
    """
    tasks = agent_service.get_task_history(
        agent_id=agent_id,
        limit=limit,
        offset=offset
    )
    
    return TaskHistoryResponse(
        tasks=[t.to_dict() for t in tasks],
        total=len(tasks)
    )


# Action Routes
@router.post("/action", response_model=AgentActionResponse)
async def create_action(request: AgentActionCreate):
    """
    Add an action to a task.
    """
    try:
        action = agent_service.add_action(request)
        return action.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/task/{task_id}/actions")
async def get_task_actions(task_id: str):
    """
    Get all actions for a task.
    """
    task = agent_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    actions = agent_service.get_task_actions(task_id)
    
    return {
        "task_id": task_id,
        "actions": [a.to_dict() for a in actions],
        "total": len(actions)
    }


# Stats Routes
@router.get("/stats", response_model=TaskStatsResponse)
async def get_stats():
    """
    Get task statistics.
    """
    stats_dict = agent_service.get_stats()
    
    stats = [
        AgentTaskStats(
            agent_id=agent_id,
            total_tasks=data["total"],
            pending_tasks=data["pending"],
            approved_tasks=data["approved"],
            executed_tasks=data["executed"],
            rejected_tasks=data["rejected"],
            failed_tasks=data["failed"]
        )
        for agent_id, data in stats_dict.items()
    ]
    
    return TaskStatsResponse(stats=stats)
