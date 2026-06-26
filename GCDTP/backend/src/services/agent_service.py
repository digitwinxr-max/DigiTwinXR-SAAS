"""
Agent Service

AI Agent Framework with human approval workflow.
Agents propose actions - humans approve - execution follows.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from collections import defaultdict

from ..models.agent_definition import AgentDefinition, AgentType
from ..models.agent_task import AgentTask, TaskStatus
from ..models.agent_action import AgentAction, ApprovalStatus
from ..schemas.agent import (
    AgentTaskCreate,
    AgentActionCreate,
    TaskApprovalRequest,
    TaskRejectRequest
)


class AgentService:
    """
    Agent Service for AI-powered operations.
    
    Execution Flow:
    1. Human Request → Agent
    2. Agent → Proposal
    3. Proposal → Approval Queue
    4. Human Approval → Execution
    5. Execution → Audit Trail
    
    IMPORTANT:
    - Agents NEVER autonomously modify the operational twin
    - Human approval is mandatory
    - All actions are audited
    """
    
    def __init__(self):
        # In-memory storage
        self._agents: Dict[str, AgentDefinition] = {}
        self._tasks: Dict[str, AgentTask] = {}
        self._actions: Dict[str, AgentAction] = {}
        
        # Indexes
        self._tasks_by_agent: Dict[str, List[str]] = defaultdict(list)
        self._actions_by_task: Dict[str, List[str]] = defaultdict(list)
        
        # Initialize default agents
        self._initialize_default_agents()
    
    def _initialize_default_agents(self):
        """Initialize default agent definitions."""
        default_agents = [
            AgentDefinition(
                name="Diagnostic Agent",
                description="Analyzes system health and identifies issues",
                agent_type=AgentType.DIAGNOSTIC
            ),
            AgentDefinition(
                name="Maintenance Agent",
                description="Suggests maintenance procedures",
                agent_type=AgentType.MAINTENANCE
            ),
            AgentDefinition(
                name="Recovery Agent",
                description="Proposes recovery actions for failed systems",
                agent_type=AgentType.RECOVERY
            ),
            AgentDefinition(
                name="Knowledge Agent",
                description="Retrieves relevant knowledge and documentation",
                agent_type=AgentType.KNOWLEDGE
            ),
            AgentDefinition(
                name="Timeline Agent",
                description="Analyzes historical patterns and timelines",
                agent_type=AgentType.TIMELINE
            )
        ]
        
        for agent in default_agents:
            self._agents[agent.id] = agent
    
    def get_all_agents(self) -> List[AgentDefinition]:
        """Get all agent definitions."""
        return list(self._agents.values())
    
    def get_agent(self, agent_id: str) -> Optional[AgentDefinition]:
        """Get agent by ID."""
        return self._agents.get(agent_id)
    
    def get_enabled_agents(self) -> List[AgentDefinition]:
        """Get all enabled agents."""
        return [a for a in self._agents.values() if a.enabled]
    
    def create_task(self, request: AgentTaskCreate) -> AgentTask:
        """
        Create a new agent task.
        
        Args:
            request: Task creation request
            
        Returns:
            Created AgentTask
        """
        # Validate agent exists
        if request.agent_id not in self._agents:
            raise ValueError(f"Agent {request.agent_id} not found")
        
        # Create task
        task = AgentTask(
            agent_id=request.agent_id,
            task_type=request.task_type,
            status=TaskStatus.PENDING,
            requested_by=request.requested_by,
            context_data=request.context_data
        )
        
        self._tasks[task.id] = task
        self._tasks_by_agent[request.agent_id].append(task.id)
        
        return task
    
    def get_task(self, task_id: str) -> Optional[AgentTask]:
        """Get task by ID."""
        return self._tasks.get(task_id)
    
    def get_tasks(
        self,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[AgentTask]:
        """Get tasks with optional filters."""
        tasks = list(self._tasks.values())
        
        if agent_id:
            tasks = [t for t in tasks if t.agent_id == agent_id]
        
        if status:
            tasks = [t for t in tasks if t.status.value == status]
        
        # Sort by created_at descending
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        return tasks[offset:offset + limit]
    
    def approve_task(self, task_id: str, request: TaskApprovalRequest) -> Optional[AgentTask]:
        """
        Approve a task.
        
        Args:
            task_id: Task ID
            request: Approval request
            
        Returns:
            Updated task or None
        """
        task = self._tasks.get(task_id)
        if not task:
            return None
        
        if not task.can_approve():
            raise ValueError(f"Task {task_id} cannot be approved (status: {task.status})")
        
        task.status = TaskStatus.APPROVED
        task.approved_by = request.approved_by
        
        return task
    
    def reject_task(self, task_id: str, request: TaskRejectRequest) -> Optional[AgentTask]:
        """
        Reject a task.
        
        Args:
            task_id: Task ID
            request: Rejection request
            
        Returns:
            Updated task or None
        """
        task = self._tasks.get(task_id)
        if not task:
            return None
        
        if not task.can_approve():
            raise ValueError(f"Task {task_id} cannot be rejected (status: {task.status})")
        
        task.status = TaskStatus.REJECTED
        task.result_data = {"rejection_reason": request.reason}
        
        return task
    
    def execute_task(self, task_id: str, executed_by: str) -> Optional[AgentTask]:
        """
        Execute an approved task.
        
        NOTE: This simulates execution. In reality, this would:
        - NOT modify the operational twin
        - Create audit records
        - Return recommendations
        
        Args:
            task_id: Task ID
            executed_by: Who executed
            
        Returns:
            Updated task or None
        """
        task = self._tasks.get(task_id)
        if not task:
            return None
        
        if not task.can_execute():
            raise ValueError(f"Task {task_id} cannot be executed (status: {task.status})")
        
        # Get agent
        agent = self._agents.get(task.agent_id)
        
        # Generate execution result based on agent type
        result = self._generate_execution_result(task, agent)
        
        task.status = TaskStatus.EXECUTED
        task.executed_at = datetime.utcnow()
        task.result_data = result
        
        return task
    
    def _generate_execution_result(
        self,
        task: AgentTask,
        agent: Optional[AgentDefinition]
    ) -> Dict[str, Any]:
        """Generate execution result based on agent type."""
        if not agent:
            return {"status": "completed", "message": "Agent not found"}
        
        task_type = task.task_type
        
        if agent.agent_type == AgentType.DIAGNOSTIC:
            return {
                "status": "completed",
                "message": "Diagnostic analysis complete",
                "recommendations": [
                    "Review health metrics for anomalies",
                    "Check recent event logs",
                    "Verify sensor readings"
                ],
                "findings": [
                    "System health appears normal",
                    "No critical issues detected",
                    "Consider routine maintenance"
                ]
            }
        
        elif agent.agent_type == AgentType.MAINTENANCE:
            return {
                "status": "completed",
                "message": "Maintenance recommendations generated",
                "recommendations": [
                    "Schedule routine inspection",
                    "Check critical components",
                    "Update maintenance records"
                ],
                "procedures": [
                    "Visual inspection checklist",
                    "Sensor calibration procedure",
                    "Documentation update"
                ]
            }
        
        elif agent.agent_type == AgentType.RECOVERY:
            return {
                "status": "completed",
                "message": "Recovery plan generated",
                "recommendations": [
                    "Review recovery procedures",
                    "Contact maintenance team",
                    "Prepare recovery materials"
                ],
                "steps": [
                    "Assess current state",
                    "Execute recovery plan",
                    "Verify recovery success"
                ]
            }
        
        elif agent.agent_type == AgentType.KNOWLEDGE:
            return {
                "status": "completed",
                "message": "Knowledge retrieval complete",
                "documents": [
                    "Related SOPs found",
                    "Historical incidents reviewed",
                    "Best practices identified"
                ],
                "references": [
                    "Maintenance manual",
                    "Safety procedures",
                    "Operational guidelines"
                ]
            }
        
        elif agent.agent_type == AgentType.TIMELINE:
            return {
                "status": "completed",
                "message": "Timeline analysis complete",
                "patterns": [
                    "No unusual patterns detected",
                    "Normal operational cycle observed",
                    "Historical performance within expected range"
                ],
                "recommendations": [
                    "Continue monitoring",
                    "Review timeline for anomalies"
                ]
            }
        
        return {
            "status": "completed",
            "message": "Task execution complete"
        }
    
    def add_action(self, request: AgentActionCreate) -> AgentAction:
        """
        Add an action to a task.
        
        Args:
            request: Action creation request
            
        Returns:
            Created AgentAction
        """
        if request.task_id not in self._tasks:
            raise ValueError(f"Task {request.task_id} not found")
        
        action = AgentAction(
            task_id=request.task_id,
            action_type=request.action_type,
            action_payload=request.action_payload
        )
        
        self._actions[action.id] = action
        self._actions_by_task[request.task_id].append(action.id)
        
        return action
    
    def get_action(self, action_id: str) -> Optional[AgentAction]:
        """Get action by ID."""
        return self._actions.get(action_id)
    
    def get_task_actions(self, task_id: str) -> List[AgentAction]:
        """Get all actions for a task."""
        action_ids = self._actions_by_task.get(task_id, [])
        return [self._actions[aid] for aid in action_ids if aid in self._actions]
    
    def get_pending_tasks(self) -> List[AgentTask]:
        """Get all pending tasks."""
        return [t for t in self._tasks.values() if t.is_pending()]
    
    def get_pending_actions(self) -> List[AgentAction]:
        """Get all pending actions."""
        return [a for a in self._actions.values() if a.is_pending()]
    
    def get_task_history(
        self,
        agent_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[AgentTask]:
        """Get task execution history."""
        tasks = self.get_tasks(agent_id=agent_id, limit=1000)
        
        # Filter to completed tasks
        completed = [t for t in tasks if t.status in [
            TaskStatus.EXECUTED,
            TaskStatus.REJECTED,
            TaskStatus.FAILED
        ]]
        
        completed.sort(key=lambda t: t.created_at, reverse=True)
        
        return completed[offset:offset + limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get task statistics."""
        stats = defaultdict(lambda: {
            "total": 0,
            "pending": 0,
            "approved": 0,
            "executed": 0,
            "rejected": 0,
            "failed": 0
        })
        
        for task in self._tasks.values():
            agent_id = task.agent_id
            stats[agent_id]["total"] += 1
            stats[agent_id][task.status.value] += 1
        
        return dict(stats)


# Global instance
agent_service = AgentService()
