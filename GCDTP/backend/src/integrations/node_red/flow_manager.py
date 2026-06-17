"""
Flow Manager

Manages workflow definitions, instances, and executions.
Provides local caching and state management.
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from backend.src.integrations.node_red.node_red_client import NodeREDClient
from backend.src.integrations.node_red.workflow_adapter import WorkflowAdapter
from backend.src.integrations.node_red.workflow_types import (
    WorkflowDefinition,
    WorkflowInstance,
    WorkflowExecution,
    ExecutionStatus,
    TriggerType,
)
from backend.src.core.events import get_event_bus, EventType


class FlowManager:
    """
    Manages workflow lifecycle in FastAPI.
    
    Responsibilities:
    - Create/update/delete workflows
    - Enable/disable workflows
    - Execute workflows
    - Track execution history
    - Manage retries
    - Handle cancellations
    
    Note: FastAPI is authoritative for business logic.
    Node-RED handles orchestration only.
    """
    
    def __init__(
        self,
        node_red_url: str = "http://localhost:1880",
        adapter: Optional[WorkflowAdapter] = None
    ):
        self.node_red_client = NodeREDClient(base_url=node_red_url)
        self.adapter = adapter or WorkflowAdapter(node_red_url)
        self.event_bus = get_event_bus()
        
        # Local storage for workflow definitions
        self._workflows: Dict[str, WorkflowDefinition] = {}
        self._instances: Dict[str, List[WorkflowInstance]] = {}
        self._executions: Dict[str, List[WorkflowExecution]] = {}
    
    def close(self):
        """Close resources."""
        self.node_red_client.close()
    
    # =========================================================================
    # Workflow CRUD
    # =========================================================================
    
    def create_workflow(
        self,
        name: str,
        flow_json: Dict[str, Any],
        trigger_type: TriggerType = TriggerType.MANUAL,
        trigger_config: Optional[Dict] = None,
        description: str = "",
        created_by: Optional[str] = None
    ) -> WorkflowDefinition:
        """
        Create a new workflow definition.
        
        Args:
            name: Workflow name
            flow_json: Node-RED flow definition
            trigger_type: Trigger type
            trigger_config: Trigger configuration
            description: Workflow description
            created_by: User creating the workflow
            
        Returns:
            Created WorkflowDefinition
        """
        workflow = WorkflowDefinition(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            flow_json=flow_json,
            trigger_type=trigger_type,
            trigger_config=trigger_config or {},
            created_by=created_by
        )
        
        # Store locally
        self._workflows[workflow.id] = workflow
        self._instances[workflow.id] = []
        self._executions[workflow.id] = []
        
        # Sync to Node-RED
        try:
            self.node_red_client.create_flow({
                "id": workflow.id,
                "label": workflow.name,
                "nodes": workflow.flow_json.get("nodes", [])
            })
        except Exception:
            pass  # Node-RED may not be running
        
        # Publish event
        self.event_bus.publish(
            EventType.WORKFLOW_CREATED,
            source="flow_manager",
            data={
                "workflow_id": workflow.id,
                "name": workflow.name,
                "trigger_type": trigger_type.value,
            }
        )
        
        return workflow
    
    def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Get a workflow by ID."""
        return self._workflows.get(workflow_id)
    
    def get_workflows(
        self,
        trigger_type: Optional[TriggerType] = None,
        enabled_only: bool = False
    ) -> List[WorkflowDefinition]:
        """Get all workflows with optional filtering."""
        workflows = list(self._workflows.values())
        
        if trigger_type:
            workflows = [w for w in workflows if w.trigger_type == trigger_type]
        
        if enabled_only:
            workflows = [w for w in workflows if w.is_enabled]
        
        return workflows
    
    def update_workflow(
        self,
        workflow: WorkflowDefinition,
        **kwargs
    ) -> WorkflowDefinition:
        """
        Update a workflow.
        
        Args:
            workflow: Workflow to update
            **kwargs: Fields to update
            
        Returns:
            Updated WorkflowDefinition
        """
        for key, value in kwargs.items():
            if hasattr(workflow, key):
                setattr(workflow, key, value)
        
        workflow.updated_at = datetime.utcnow()
        
        # Sync to Node-RED
        try:
            self.node_red_client.update_flow(workflow.id, {
                "id": workflow.id,
                "label": workflow.name,
                "nodes": workflow.flow_json.get("nodes", [])
            })
        except Exception:
            pass
        
        return workflow
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """
        Delete a workflow.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            True if deleted
        """
        if workflow_id not in self._workflows:
            return False
        
        # Delete from Node-RED
        try:
            self.node_red_client.delete_flow(workflow_id)
        except Exception:
            pass
        
        # Remove locally
        del self._workflows[workflow_id]
        if workflow_id in self._instances:
            del self._instances[workflow_id]
        if workflow_id in self._executions:
            del self._executions[workflow_id]
        
        return True
    
    # =========================================================================
    # Flow Status
    # =========================================================================
    
    def enable_workflow(self, workflow: WorkflowDefinition) -> WorkflowDefinition:
        """
        Enable a workflow.
        
        Args:
            workflow: Workflow to enable
            
        Returns:
            Updated WorkflowDefinition
        """
        workflow.is_enabled = True
        
        try:
            self.node_red_client.enable_flow(workflow.id)
        except Exception:
            pass
        
        return workflow
    
    def disable_workflow(self, workflow: WorkflowDefinition) -> WorkflowDefinition:
        """
        Disable a workflow.
        
        Args:
            workflow: Workflow to disable
            
        Returns:
            Updated WorkflowDefinition
        """
        workflow.is_enabled = False
        
        try:
            self.node_red_client.disable_flow(workflow.id)
        except Exception:
            pass
        
        return workflow
    
    # =========================================================================
    # Workflow Execution
    # =========================================================================
    
    def execute_workflow(
        self,
        workflow: WorkflowDefinition,
        input_data: Optional[Dict] = None,
        context: Optional[Dict] = None
    ) -> WorkflowInstance:
        """
        Execute a workflow.
        
        Args:
            workflow: Workflow to execute
            input_data: Input data
            context: Execution context
            
        Returns:
            Created WorkflowInstance
        """
        instance = WorkflowInstance(
            id=str(uuid.uuid4()),
            workflow_id=workflow.id,
            name=workflow.name,
            input_data=input_data or {},
            context=context or {}
        )
        
        # Store instance
        if workflow.id not in self._instances:
            self._instances[workflow.id] = []
        self._instances[workflow.id].append(instance)
        
        # Execute in Node-RED
        try:
            result = self.node_red_client.trigger_flow(workflow.id, input_data)
            instance.status = ExecutionStatus.RUNNING
            instance.started_at = datetime.utcnow()
        except Exception as e:
            instance.status = ExecutionStatus.FAILED
            instance.error_message = str(e)
        
        # Update workflow stats
        workflow.execution_count += 1
        workflow.last_executed_at = datetime.utcnow()
        
        # Publish event
        self.event_bus.publish(
            EventType.WORKFLOW_STARTED,
            source="flow_manager",
            data={
                "workflow_id": workflow.id,
                "instance_id": instance.id,
                "name": workflow.name,
            }
        )
        
        return instance
    
    def complete_workflow(
        self,
        instance: WorkflowInstance,
        output_data: Dict[str, Any]
    ) -> WorkflowInstance:
        """
        Mark a workflow as completed.
        
        Args:
            instance: Workflow instance
            output_data: Output data
            
        Returns:
            Updated WorkflowInstance
        """
        instance.status = ExecutionStatus.COMPLETED
        instance.output_data = output_data
        instance.completed_at = datetime.utcnow()
        
        # Create execution record
        execution = WorkflowExecution(
            id=str(uuid.uuid4()),
            workflow_id=instance.workflow_id,
            instance_id=instance.id,
            status=ExecutionStatus.COMPLETED,
            output_data=output_data
        )
        
        if instance.workflow_id in self._executions:
            self._executions[instance.workflow_id].append(execution)
        
        # Publish event
        workflow = self.get_workflow(instance.workflow_id)
        self.event_bus.publish(
            EventType.WORKFLOW_COMPLETED,
            source="flow_manager",
            data={
                "workflow_id": instance.workflow_id,
                "instance_id": instance.id,
                "name": workflow.name if workflow else None,
            }
        )
        
        return instance
    
    def fail_workflow(
        self,
        instance: WorkflowInstance,
        error_message: str
    ) -> WorkflowInstance:
        """
        Mark a workflow as failed.
        
        Args:
            instance: Workflow instance
            error_message: Error message
            
        Returns:
            Updated WorkflowInstance
        """
        instance.status = ExecutionStatus.FAILED
        instance.error_message = error_message
        instance.completed_at = datetime.utcnow()
        
        # Publish event
        workflow = self.get_workflow(instance.workflow_id)
        self.event_bus.publish(
            EventType.WORKFLOW_FAILED,
            source="flow_manager",
            data={
                "workflow_id": instance.workflow_id,
                "instance_id": instance.id,
                "name": workflow.name if workflow else None,
                "error": error_message,
            }
        )
        
        return instance
    
    def cancel_workflow(self, instance: WorkflowInstance) -> WorkflowInstance:
        """
        Cancel a running workflow.
        
        Args:
            instance: Workflow instance
            
        Returns:
            Updated WorkflowInstance
        """
        if instance.status != ExecutionStatus.RUNNING:
            raise ValueError("Can only cancel running workflows")
        
        instance.status = ExecutionStatus.CANCELLED
        instance.completed_at = datetime.utcnow()
        
        # Publish event
        self.event_bus.publish(
            EventType.WORKFLOW_CANCELLED,
            source="flow_manager",
            data={
                "workflow_id": instance.workflow_id,
                "instance_id": instance.id,
            }
        )
        
        return instance
    
    # =========================================================================
    # Retry Logic
    # =========================================================================
    
    def retry_workflow(
        self,
        instance: WorkflowInstance
    ) -> WorkflowInstance:
        """
        Retry a failed workflow.
        
        Args:
            instance: Failed workflow instance
            
        Returns:
            New WorkflowInstance for retry
        """
        if instance.status != ExecutionStatus.FAILED:
            raise ValueError("Can only retry failed workflows")
        
        # Check retry count
        if instance.retry_count >= instance.max_retries:
            raise ValueError(f"Maximum retries ({instance.max_retries}) exceeded")
        
        workflow = self.get_workflow(instance.workflow_id)
        if not workflow:
            raise ValueError("Workflow not found")
        
        # Create new instance for retry
        new_instance = self.execute_workflow(
            workflow,
            instance.input_data,
            {"retry_of": instance.id}
        )
        new_instance.retry_count = instance.retry_count + 1
        
        # Publish event
        self.event_bus.publish(
            EventType.WORKFLOW_RETRIED,
            source="flow_manager",
            data={
                "workflow_id": instance.workflow_id,
                "original_instance_id": instance.id,
                "new_instance_id": new_instance.id,
                "retry_count": new_instance.retry_count,
            }
        )
        
        return new_instance
    
    # =========================================================================
    # History and Status
    # =========================================================================
    
    def get_instance_history(
        self,
        workflow_id: str,
        limit: int = 50
    ) -> List[WorkflowInstance]:
        """Get execution history for a workflow."""
        instances = self._instances.get(workflow_id, [])
        return sorted(instances, key=lambda x: x.created_at, reverse=True)[:limit]
    
    def get_running_instances(self, workflow_id: str) -> List[WorkflowInstance]:
        """Get all running instances for a workflow."""
        instances = self._instances.get(workflow_id, [])
        return [i for i in instances if i.status == ExecutionStatus.RUNNING]
    
    def get_execution_history(
        self,
        workflow_id: str,
        limit: int = 100
    ) -> List[WorkflowExecution]:
        """Get execution history."""
        executions = self._executions.get(workflow_id, [])
        return sorted(executions, key=lambda x: x.started_at, reverse=True)[:limit]
    
    def get_workflow_stats(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow statistics."""
        instances = self._instances.get(workflow_id, [])
        
        return {
            "total_executions": len(instances),
            "running": len([i for i in instances if i.status == ExecutionStatus.RUNNING]),
            "completed": len([i for i in instances if i.status == ExecutionStatus.COMPLETED]),
            "failed": len([i for i in instances if i.status == ExecutionStatus.FAILED]),
            "cancelled": len([i for i in instances if i.status == ExecutionStatus.CANCELLED]),
            "pending": len([i for i in instances if i.status == ExecutionStatus.PENDING]),
        }
