"""
Maintenance Engine

Manages maintenance tasks for work orders.
Handles repairs, replacements, and corrective actions.
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from backend.src.services.work_orders.work_order_types import (
    MaintenanceTask,
    MaintenanceType,
    TaskStatus,
    WorkOrder,
    WorkOrderStatus,
    WorkOrderCategory,
)
from backend.src.core.events import get_event_bus, EventType


class MaintenanceEngine:
    """
    Engine for managing maintenance tasks.
    
    Responsibilities:
    - Create maintenance tasks
    - Track parts and labor
    - Record root cause analysis
    - Calculate costs
    - Manage task status
    """
    
    def __init__(self):
        self.event_bus = get_event_bus()
    
    def create_maintenance_task(
        self,
        work_order: WorkOrder,
        asset_id: str,
        maintenance_type: MaintenanceType,
        technician: Optional[str] = None,
        estimated_hours: Optional[float] = None,
        session_id: Optional[str] = None
    ) -> MaintenanceTask:
        """
        Create a maintenance task.
        
        Args:
            work_order: Parent work order
            asset_id: Target asset ID
            maintenance_type: Type of maintenance
            technician: Assigned technician
            estimated_hours: Estimated labor hours
            session_id: Timeline session ID
            
        Returns:
            Created MaintenanceTask
        """
        task = MaintenanceTask(
            id=str(uuid.uuid4()),
            work_order_id=work_order.id,
            asset_id=asset_id,
            maintenance_type=maintenance_type,
            technician=technician,
            task_status=TaskStatus.PENDING,
            metadata={"session_id": session_id} if session_id else {}
        )
        
        # Publish event
        self.event_bus.publish(
            EventType.MAINTENANCE_CREATED,
            source="maintenance_engine",
            data={
                "maintenance_id": task.id,
                "work_order_id": work_order.id,
                "asset_id": asset_id,
                "maintenance_type": maintenance_type.value,
                "technician": technician,
            }
        )
        
        return task
    
    def start_task(
        self,
        task: MaintenanceTask,
        started_by: Optional[str] = None
    ) -> MaintenanceTask:
        """
        Start a maintenance task.
        
        Args:
            task: Task to start
            started_by: User starting
            
        Returns:
            Updated MaintenanceTask
        """
        if task.task_status != TaskStatus.PENDING:
            raise ValueError(f"Cannot start task with status: {task.task_status.value}")
        
        task.task_status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        
        self.event_bus.publish(
            EventType.MAINTENANCE_STARTED,
            source="maintenance_engine",
            data={
                "maintenance_id": task.id,
                "work_order_id": task.work_order_id,
                "asset_id": task.asset_id,
                "started_by": started_by,
            }
        )
        
        return task
    
    def complete_task(
        self,
        task: MaintenanceTask,
        completed_by: Optional[str] = None,
        actual_hours: Optional[float] = None,
        corrective_action: Optional[str] = None
    ) -> MaintenanceTask:
        """
        Complete a maintenance task.
        
        Args:
            task: Task to complete
            completed_by: User completing
            actual_hours: Actual hours spent
            corrective_action: What was done
            
        Returns:
            Updated MaintenanceTask
        """
        if task.task_status == TaskStatus.COMPLETED:
            raise ValueError("Task is already completed")
        
        task.task_status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        
        if actual_hours is not None:
            task.labor_hours = actual_hours
        
        if corrective_action:
            task.corrective_action = corrective_action
        
        self.event_bus.publish(
            EventType.MAINTENANCE_COMPLETED,
            source="maintenance_engine",
            data={
                "maintenance_id": task.id,
                "work_order_id": task.work_order_id,
                "asset_id": task.asset_id,
                "completed_by": completed_by,
                "labor_hours": task.labor_hours,
                "cost": task.cost,
            }
        )
        
        return task
    
    def cancel_task(
        self,
        task: MaintenanceTask,
        cancelled_by: Optional[str] = None,
        reason: Optional[str] = None
    ) -> MaintenanceTask:
        """
        Cancel a maintenance task.
        
        Args:
            task: Task to cancel
            cancelled_by: User cancelling
            reason: Cancellation reason
            
        Returns:
            Updated MaintenanceTask
        """
        task.task_status = TaskStatus.CANCELLED
        task.updated_at = datetime.utcnow()
        
        if reason:
            task.failure_symptoms = f"Cancelled: {reason}"
        
        self.event_bus.publish(
            EventType.MAINTENANCE_CANCELLED,
            source="maintenance_engine",
            data={
                "maintenance_id": task.id,
                "work_order_id": task.work_order_id,
                "cancelled_by": cancelled_by,
                "reason": reason,
            }
        )
        
        return task
    
    def add_part(
        self,
        task: MaintenanceTask,
        part_number: str,
        part_name: str,
        quantity: int = 1,
        unit_cost: float = 0.0
    ) -> MaintenanceTask:
        """
        Add a part to the task.
        
        Args:
            task: Maintenance task
            part_number: Part number/SKU
            part_name: Part description
            quantity: Quantity used
            unit_cost: Cost per unit
            
        Returns:
            Updated MaintenanceTask
        """
        part = {
            "part_number": part_number,
            "part_name": part_name,
            "quantity": quantity,
            "unit_cost": unit_cost,
            "total_cost": quantity * unit_cost,
            "added_at": datetime.utcnow().isoformat()
        }
        
        task.parts_used.append(part)
        task.cost += part["total_cost"]
        task.updated_at = datetime.utcnow()
        
        return task
    
    def remove_part(
        self,
        task: MaintenanceTask,
        part_index: int
    ) -> MaintenanceTask:
        """
        Remove a part from the task.
        
        Args:
            task: Maintenance task
            part_index: Index of part to remove
            
        Returns:
            Updated MaintenanceTask
        """
        if 0 <= part_index < len(task.parts_used):
            removed = task.parts_used.pop(part_index)
            task.cost -= removed.get("total_cost", 0)
            task.updated_at = datetime.utcnow()
        
        return task
    
    def record_failure_symptoms(
        self,
        task: MaintenanceTask,
        symptoms: str
    ) -> MaintenanceTask:
        """
        Record failure symptoms.
        
        Args:
            task: Maintenance task
            symptoms: Description of symptoms
            
        Returns:
            Updated MaintenanceTask
        """
        task.failure_symptoms = symptoms
        task.updated_at = datetime.utcnow()
        return task
    
    def record_root_cause(
        self,
        task: MaintenanceTask,
        root_cause: str
    ) -> MaintenanceTask:
        """
        Record root cause analysis.
        
        Args:
            task: Maintenance task
            root_cause: Root cause description
            
        Returns:
            Updated MaintenanceTask
        """
        task.root_cause = root_cause
        task.updated_at = datetime.utcnow()
        return task
    
    def record_corrective_action(
        self,
        task: MaintenanceTask,
        corrective_action: str
    ) -> MaintenanceTask:
        """
        Record corrective action taken.
        
        Args:
            task: Maintenance task
            corrective_action: Description of action
            
        Returns:
            Updated MaintenanceTask
        """
        task.corrective_action = corrective_action
        task.updated_at = datetime.utcnow()
        return task
    
    def set_warranty_info(
        self,
        task: MaintenanceTask,
        warranty_type: str,
        warranty_end_date: Optional[datetime] = None,
        warranty_provider: Optional[str] = None,
        warranty_number: Optional[str] = None
    ) -> MaintenanceTask:
        """
        Set warranty information.
        
        Args:
            task: Maintenance task
            warranty_type: Type of warranty
            warranty_end_date: When warranty expires
            warranty_provider: Warranty provider
            warranty_number: Warranty claim number
            
        Returns:
            Updated MaintenanceTask
        """
        task.warranty_info = {
            "type": warranty_type,
            "end_date": warranty_end_date.isoformat() if warranty_end_date else None,
            "provider": warranty_provider,
            "claim_number": warranty_number,
            "recorded_at": datetime.utcnow().isoformat()
        }
        task.updated_at = datetime.utcnow()
        return task
    
    def calculate_total_cost(self, task: MaintenanceTask) -> Dict[str, float]:
        """
        Calculate total maintenance cost.
        
        Args:
            task: Maintenance task
            
        Returns:
            Cost breakdown
        """
        parts_cost = sum(p.get("total_cost", 0) for p in task.parts_used)
        labor_cost = task.labor_hours * 50.0  # Assuming $50/hour labor rate
        
        return {
            "parts_cost": parts_cost,
            "labor_cost": labor_cost,
            "total_cost": parts_cost + labor_cost,
            "labor_hours": task.labor_hours,
            "parts_count": len(task.parts_used),
        }
    
    def get_task_duration(self, task: MaintenanceTask) -> Optional[float]:
        """
        Get task duration in hours.
        
        Args:
            task: Maintenance task
            
        Returns:
            Duration in hours or None
        """
        if not task.started_at or not task.completed_at:
            return None
        
        delta = task.completed_at - task.started_at
        return delta.total_seconds() / 3600
    
    def is_task_overdue(self, task: MaintenanceTask, due_date: datetime) -> bool:
        """
        Check if task is overdue.
        
        Args:
            task: Maintenance task
            due_date: Expected completion date
            
        Returns:
            True if overdue
        """
        if task.task_status == TaskStatus.COMPLETED:
            return False
        
        return datetime.utcnow() > due_date
    
    def generate_maintenance_report(self, task: MaintenanceTask) -> Dict:
        """
        Generate maintenance task report.
        
        Args:
            task: Maintenance task
            
        Returns:
            Report dictionary
        """
        cost_breakdown = self.calculate_total_cost(task)
        
        return {
            "maintenance_id": task.id,
            "work_order_id": task.work_order_id,
            "asset_id": task.asset_id,
            "type": task.maintenance_type.value,
            "technician": task.technician,
            "status": task.task_status.value,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "duration_hours": self.get_task_duration(task),
            "failure_symptoms": task.failure_symptoms,
            "root_cause": task.root_cause,
            "corrective_action": task.corrective_action,
            "parts_used": task.parts_used,
            "labor_hours": task.labor_hours,
            "cost_breakdown": cost_breakdown,
            "warranty_info": task.warranty_info,
        }
    
    def create_preventive_maintenance(
        self,
        work_order: WorkOrder,
        asset_id: str,
        maintenance_type: MaintenanceType,
        technician: Optional[str] = None
    ) -> MaintenanceTask:
        """
        Create a preventive maintenance task.
        
        Args:
            work_order: Parent work order
            asset_id: Target asset
            maintenance_type: Type of preventive maintenance
            technician: Assigned technician
            
        Returns:
            Created MaintenanceTask
        """
        return self.create_maintenance_task(
            work_order=work_order,
            asset_id=asset_id,
            maintenance_type=maintenance_type,
            technician=technician
        )
    
    def create_corrective_maintenance(
        self,
        work_order: WorkOrder,
        asset_id: str,
        failure_symptoms: str,
        technician: Optional[str] = None
    ) -> MaintenanceTask:
        """
        Create a corrective maintenance task.
        
        Args:
            work_order: Parent work order
            asset_id: Target asset
            failure_symptoms: Observed symptoms
            technician: Assigned technician
            
        Returns:
            Created MaintenanceTask
        """
        task = self.create_maintenance_task(
            work_order=work_order,
            asset_id=asset_id,
            maintenance_type=MaintenanceType.REPAIR,
            technician=technician
        )
        
        task = self.record_failure_symptoms(task, failure_symptoms)
        
        return task
