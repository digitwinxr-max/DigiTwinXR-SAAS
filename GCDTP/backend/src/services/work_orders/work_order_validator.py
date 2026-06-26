"""
Work Order Validator

Validates work orders and tasks for correctness.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from backend.src.services.work_orders.work_order_types import (
    WorkOrder,
    WorkOrderStatus,
    Priority,
    InspectionTask,
    MaintenanceTask,
    TaskStatus,
)


class WorkOrderValidator:
    """
    Validates work orders and related entities.
    
    Checks:
    - Required fields
    - Status transitions
    - Priority handling
    - Date consistency
    - Asset linkage
    """
    
    # Valid status transitions
    STATUS_TRANSITIONS = {
        WorkOrderStatus.PENDING: [
            WorkOrderStatus.IN_PROGRESS,
            WorkOrderStatus.CANCELLED,
            WorkOrderStatus.ON_HOLD,
        ],
        WorkOrderStatus.IN_PROGRESS: [
            WorkOrderStatus.COMPLETED,
            WorkOrderStatus.CANCELLED,
            WorkOrderStatus.ON_HOLD,
        ],
        WorkOrderStatus.ON_HOLD: [
            WorkOrderStatus.IN_PROGRESS,
            WorkOrderStatus.CANCELLED,
        ],
        WorkOrderStatus.COMPLETED: [],  # Terminal state
        WorkOrderStatus.CANCELLED: [],  # Terminal state
    }
    
    def __init__(self):
        self.issues: List[str] = []
    
    def validate_work_order(self, work_order: WorkOrder) -> List[str]:
        """
        Validate a work order.
        
        Args:
            work_order: Work order to validate
            
        Returns:
            List of validation issues
        """
        self.issues = []
        
        # Required fields
        if not work_order.id:
            self.issues.append("Work order ID is required")
        
        if not work_order.asset_id:
            self.issues.append("Asset ID is required")
        
        if not work_order.title or not work_order.title.strip():
            self.issues.append("Title is required")
        
        if work_order.title and len(work_order.title) > 255:
            self.issues.append("Title must be 255 characters or less")
        
        # Priority validation
        if not isinstance(work_order.priority, Priority):
            self.issues.append("Invalid priority value")
        
        # Status validation
        if not isinstance(work_order.status, WorkOrderStatus):
            self.issues.append("Invalid status value")
        
        # Date validation
        if work_order.due_date and work_order.due_date < datetime.utcnow():
            self.issues.append("Due date cannot be in the past")
        
        if work_order.completed_at and work_order.completed_at < work_order.created_at:
            self.issues.append("Completed date cannot be before created date")
        
        # Hours validation
        if work_order.estimated_hours is not None and work_order.estimated_hours < 0:
            self.issues.append("Estimated hours cannot be negative")
        
        if work_order.actual_hours is not None and work_order.actual_hours < 0:
            self.issues.append("Actual hours cannot be negative")
        
        return self.issues.copy()
    
    def validate_status_transition(
        self,
        current_status: WorkOrderStatus,
        new_status: WorkOrderStatus
    ) -> List[str]:
        """
        Validate a status transition.
        
        Args:
            current_status: Current status
            new_status: New status
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if new_status not in self.STATUS_TRANSITIONS.get(current_status, []):
            issues.append(
                f"Invalid status transition from {current_status.value} to {new_status.value}"
            )
        
        return issues
    
    def validate_priority(self, priority: Priority) -> List[str]:
        """
        Validate priority value.
        
        Args:
            priority: Priority to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not isinstance(priority, Priority):
            issues.append(f"Invalid priority type: {type(priority)}")
        
        return issues
    
    def validate_assignment(
        self,
        work_order: WorkOrder,
        assigned_to: str
    ) -> List[str]:
        """
        Validate assignment.
        
        Args:
            work_order: Work order
            assigned_to: User to assign to
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if work_order.status == WorkOrderStatus.COMPLETED:
            issues.append("Cannot assign to a completed work order")
        
        if work_order.status == WorkOrderStatus.CANCELLED:
            issues.append("Cannot assign to a cancelled work order")
        
        if not assigned_to or not assigned_to.strip():
            issues.append("Assigned user is required")
        
        return issues
    
    def validate_completion(
        self,
        work_order: WorkOrder,
        actual_hours: Optional[float] = None
    ) -> List[str]:
        """
        Validate work order completion.
        
        Args:
            work_order: Work order
            actual_hours: Actual hours spent
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if work_order.status == WorkOrderStatus.COMPLETED:
            issues.append("Work order is already completed")
        
        if work_order.status == WorkOrderStatus.CANCELLED:
            issues.append("Cannot complete a cancelled work order")
        
        if actual_hours is not None and actual_hours < 0:
            issues.append("Actual hours cannot be negative")
        
        return issues
    
    def validate_inspection_task(self, inspection: InspectionTask) -> List[str]:
        """
        Validate an inspection task.
        
        Args:
            inspection: Inspection task to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not inspection.id:
            issues.append("Inspection ID is required")
        
        if not inspection.work_order_id:
            issues.append("Work order ID is required")
        
        if not inspection.asset_id:
            issues.append("Asset ID is required")
        
        if inspection.condition_rating:
            if not 1 <= inspection.condition_rating <= 5:
                issues.append("Condition rating must be between 1 and 5")
        
        if inspection.next_inspection_date:
            if inspection.next_inspection_date < datetime.utcnow():
                issues.append("Next inspection date cannot be in the past")
        
        return issues
    
    def validate_maintenance_task(self, task: MaintenanceTask) -> List[str]:
        """
        Validate a maintenance task.
        
        Args:
            task: Maintenance task to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not task.id:
            issues.append("Task ID is required")
        
        if not task.work_order_id:
            issues.append("Work order ID is required")
        
        if not task.asset_id:
            issues.append("Asset ID is required")
        
        if task.labor_hours < 0:
            issues.append("Labor hours cannot be negative")
        
        if task.cost < 0:
            issues.append("Cost cannot be negative")
        
        if task.task_status == TaskStatus.COMPLETED:
            if not task.completed_at:
                issues.append("Completed tasks must have completion timestamp")
        
        return issues
    
    def validate_task_status_transition(
        self,
        current_status: TaskStatus,
        new_status: TaskStatus
    ) -> List[str]:
        """
        Validate a task status transition.
        
        Args:
            current_status: Current status
            new_status: New status
            
        Returns:
            List of validation issues
        """
        issues = []
        
        valid_transitions = {
            TaskStatus.PENDING: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
            TaskStatus.IN_PROGRESS: [TaskStatus.COMPLETED, TaskStatus.CANCELLED],
            TaskStatus.COMPLETED: [],  # Terminal
            TaskStatus.CANCELLED: [],  # Terminal
        }
        
        if new_status not in valid_transitions.get(current_status, []):
            issues.append(
                f"Invalid task status transition from {current_status.value} to {new_status.value}"
            )
        
        return issues
    
    def validate_asset_linkage(
        self,
        work_order: WorkOrder,
        task_asset_id: str
    ) -> List[str]:
        """
        Validate that task asset matches work order asset.
        
        Args:
            work_order: Parent work order
            task_asset_id: Asset ID from task
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if work_order.asset_id != task_asset_id:
            issues.append(
                f"Task asset ID ({task_asset_id}) does not match "
                f"work order asset ID ({work_order.asset_id})"
            )
        
        return issues
    
    def validate_priority_change(
        self,
        old_priority: Priority,
        new_priority: Priority
    ) -> List[str]:
        """
        Validate priority change.
        
        Args:
            old_priority: Current priority
            new_priority: New priority
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not isinstance(new_priority, Priority):
            issues.append(f"Invalid priority value: {new_priority}")
        
        return issues
    
    def validate_due_date(
        self,
        work_order: WorkOrder,
        new_due_date: datetime
    ) -> List[str]:
        """
        Validate due date change.
        
        Args:
            work_order: Work order
            new_due_date: New due date
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if new_due_date < datetime.utcnow():
            issues.append("Due date cannot be in the past")
        
        if work_order.completed_at and new_due_date < work_order.completed_at:
            issues.append("Due date cannot be before completion date")
        
        return issues
    
    def get_validation_summary(self) -> Dict:
        """
        Get validation summary.
        
        Returns:
            Summary dictionary
        """
        return {
            "issues": self.issues,
            "issue_count": len(self.issues),
            "has_critical": any("required" in i.lower() for i in self.issues),
        }
