"""
Work Order Engine

Main engine for asset-centric work order management.
Coordinates inspection and maintenance tasks.
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from backend.src.services.work_orders.work_order_types import (
    WorkOrder,
    WorkOrderStatus,
    WorkOrderCategory,
    Priority,
    WorkOrderFilter,
    WorkOrderSummary,
)
from backend.src.services.work_orders.work_order_validator import WorkOrderValidator
from backend.src.core.events import get_event_bus, EventType


class WorkOrderEngine:
    """
    Main engine for work order management.
    
    Responsibilities:
    - Create work orders
    - Update status
    - Assign users
    - Manage tasks
    - Publish events
    """
    
    def __init__(self):
        self.validator = WorkOrderValidator()
        self.event_bus = get_event_bus()
    
    def create_work_order(
        self,
        asset_id: str,
        title: str,
        description: str = "",
        priority: Priority = Priority.MEDIUM,
        category: WorkOrderCategory = WorkOrderCategory.ROUTINE,
        assigned_to: Optional[str] = None,
        created_by: Optional[str] = None,
        due_date: Optional[datetime] = None,
        estimated_hours: Optional[float] = None,
        metadata: Optional[Dict] = None,
        session_id: Optional[str] = None
    ) -> WorkOrder:
        """
        Create a new work order.
        
        Args:
            asset_id: Target asset ID
            title: Work order title
            description: Detailed description
            priority: Work order priority
            category: Work order category
            assigned_to: Assigned user
            created_by: Creating user
            due_date: Required completion date
            estimated_hours: Estimated labor hours
            metadata: Additional metadata
            session_id: Timeline session ID
            
        Returns:
            Created WorkOrder
        """
        work_order = WorkOrder(
            id=str(uuid.uuid4()),
            asset_id=asset_id,
            title=title,
            description=description,
            priority=priority,
            status=WorkOrderStatus.PENDING,
            category=category,
            assigned_to=assigned_to,
            created_by=created_by,
            due_date=due_date,
            estimated_hours=estimated_hours,
            metadata=metadata or {},
            created_session_id=session_id
        )
        
        # Validate
        issues = self.validator.validate_work_order(work_order)
        if issues:
            raise ValueError(f"Validation failed: {', '.join(issues)}")
        
        # Publish event
        self.event_bus.publish(
            EventType.WORK_ORDER_CREATED,
            source="work_order_engine",
            data={
                "work_order_id": work_order.id,
                "asset_id": work_order.asset_id,
                "title": work_order.title,
                "priority": work_order.priority.value,
                "category": work_order.category.value,
                "assigned_to": work_order.assigned_to,
            }
        )
        
        return work_order
    
    def update_work_order(
        self,
        work_order: WorkOrder,
        **kwargs
    ) -> WorkOrder:
        """
        Update a work order.
        
        Args:
            work_order: Work order to update
            **kwargs: Fields to update
            
        Returns:
            Updated WorkOrder
        """
        old_status = work_order.status
        
        # Apply updates
        for key, value in kwargs.items():
            if hasattr(work_order, key):
                setattr(work_order, key, value)
        
        work_order.updated_at = datetime.utcnow()
        
        # Validate
        issues = self.validator.validate_work_order(work_order)
        if issues:
            raise ValueError(f"Validation failed: {', '.join(issues)}")
        
        # Publish status change event if status changed
        if old_status != work_order.status:
            self._publish_status_change(work_order, old_status)
        
        return work_order
    
    def assign_work_order(
        self,
        work_order: WorkOrder,
        assigned_to: str,
        assigned_by: Optional[str] = None
    ) -> WorkOrder:
        """
        Assign a work order to a user.
        
        Args:
            work_order: Work order to assign
            assigned_to: User to assign to
            assigned_by: User making assignment
            
        Returns:
            Updated WorkOrder
        """
        work_order.assigned_to = assigned_to
        work_order.updated_at = datetime.utcnow()
        
        # Publish assignment event
        self.event_bus.publish(
            EventType.WORK_ORDER_ASSIGNED,
            source="work_order_engine",
            data={
                "work_order_id": work_order.id,
                "asset_id": work_order.asset_id,
                "assigned_to": assigned_to,
                "assigned_by": assigned_by,
            }
        )
        
        return work_order
    
    def start_work_order(
        self,
        work_order: WorkOrder,
        started_by: Optional[str] = None
    ) -> WorkOrder:
        """
        Start work on a work order.
        
        Args:
            work_order: Work order to start
            started_by: User starting work
            
        Returns:
            Updated WorkOrder
        """
        if work_order.status != WorkOrderStatus.PENDING:
            raise ValueError(f"Cannot start work order with status: {work_order.status.value}")
        
        old_status = work_order.status
        work_order.status = WorkOrderStatus.IN_PROGRESS
        work_order.updated_at = datetime.utcnow()
        
        self._publish_status_change(work_order, old_status)
        
        return work_order
    
    def complete_work_order(
        self,
        work_order: WorkOrder,
        completed_by: Optional[str] = None,
        actual_hours: Optional[float] = None,
        notes: Optional[str] = None
    ) -> WorkOrder:
        """
        Complete a work order.
        
        Args:
            work_order: Work order to complete
            completed_by: User completing
            actual_hours: Actual hours spent
            notes: Completion notes
            
        Returns:
            Updated WorkOrder
        """
        if work_order.status == WorkOrderStatus.COMPLETED:
            raise ValueError("Work order is already completed")
        
        if work_order.status == WorkOrderStatus.CANCELLED:
            raise ValueError("Cannot complete a cancelled work order")
        
        old_status = work_order.status
        work_order.status = WorkOrderStatus.COMPLETED
        work_order.completed_at = datetime.utcnow()
        work_order.updated_at = datetime.utcnow()
        
        if actual_hours is not None:
            work_order.actual_hours = actual_hours
        
        if notes:
            work_order.notes = notes
        
        self._publish_status_change(work_order, old_status)
        
        return work_order
    
    def cancel_work_order(
        self,
        work_order: WorkOrder,
        cancelled_by: Optional[str] = None,
        reason: Optional[str] = None
    ) -> WorkOrder:
        """
        Cancel a work order.
        
        Args:
            work_order: Work order to cancel
            cancelled_by: User cancelling
            reason: Cancellation reason
            
        Returns:
            Updated WorkOrder
        """
        if work_order.status == WorkOrderStatus.COMPLETED:
            raise ValueError("Cannot cancel a completed work order")
        
        old_status = work_order.status
        work_order.status = WorkOrderStatus.CANCELLED
        work_order.updated_at = datetime.utcnow()
        
        if reason:
            work_order.notes = f"{work_order.notes}\nCancellation reason: {reason}".strip()
        
        self.event_bus.publish(
            EventType.WORK_ORDER_CANCELLED,
            source="work_order_engine",
            data={
                "work_order_id": work_order.id,
                "asset_id": work_order.asset_id,
                "cancelled_by": cancelled_by,
                "reason": reason,
                "previous_status": old_status.value,
            }
        )
        
        return work_order
    
    def hold_work_order(
        self,
        work_order: WorkOrder,
        reason: Optional[str] = None
    ) -> WorkOrder:
        """
        Put a work order on hold.
        
        Args:
            work_order: Work order to hold
            reason: Hold reason
            
        Returns:
            Updated WorkOrder
        """
        if work_order.status == WorkOrderStatus.COMPLETED:
            raise ValueError("Cannot hold a completed work order")
        
        if work_order.status == WorkOrderStatus.CANCELLED:
            raise ValueError("Cannot hold a cancelled work order")
        
        old_status = work_order.status
        work_order.status = WorkOrderStatus.ON_HOLD
        work_order.updated_at = datetime.utcnow()
        
        if reason:
            work_order.notes = f"{work_order.notes}\nHold reason: {reason}".strip()
        
        self._publish_status_change(work_order, old_status)
        
        return work_order
    
    def update_priority(
        self,
        work_order: WorkOrder,
        new_priority: Priority
    ) -> WorkOrder:
        """
        Update work order priority.
        
        Args:
            work_order: Work order
            new_priority: New priority
            
        Returns:
            Updated WorkOrder
        """
        old_priority = work_order.priority
        work_order.priority = new_priority
        work_order.updated_at = datetime.utcnow()
        
        self.event_bus.publish(
            EventType.WORK_ORDER_PRIORITY_CHANGED,
            source="work_order_engine",
            data={
                "work_order_id": work_order.id,
                "asset_id": work_order.asset_id,
                "old_priority": old_priority.value,
                "new_priority": new_priority.value,
            }
        )
        
        return work_order
    
    def get_work_order_state(self, work_order: WorkOrder) -> str:
        """
        Get computed work order state.
        
        Args:
            work_order: Work order
            
        Returns:
            State string
        """
        return work_order.work_order_state.value
    
    def is_work_order_overdue(self, work_order: WorkOrder) -> bool:
        """Check if work order is overdue."""
        return work_order.is_overdue
    
    def filter_work_orders(
        self,
        work_orders: List[WorkOrder],
        work_order_filter: WorkOrderFilter
    ) -> List[WorkOrder]:
        """
        Filter work orders by criteria.
        
        Args:
            work_orders: List of work orders
            work_order_filter: Filter criteria
            
        Returns:
            Filtered work orders
        """
        filtered = work_orders
        
        if work_order_filter.asset_id:
            filtered = [wo for wo in filtered if wo.asset_id == work_order_filter.asset_id]
        
        if work_order_filter.status:
            filtered = [wo for wo in filtered if wo.status in work_order_filter.status]
        
        if work_order_filter.priority:
            filtered = [wo for wo in filtered if wo.priority in work_order_filter.priority]
        
        if work_order_filter.category:
            filtered = [wo for wo in filtered if wo.category in work_order_filter.category]
        
        if work_order_filter.assigned_to:
            filtered = [wo for wo in filtered if wo.assigned_to == work_order_filter.assigned_to]
        
        if work_order_filter.due_before:
            filtered = [wo for wo in filtered 
                       if wo.due_date and wo.due_date <= work_order_filter.due_before]
        
        if work_order_filter.due_after:
            filtered = [wo for wo in filtered 
                       if wo.due_date and wo.due_date >= work_order_filter.due_after]
        
        if work_order_filter.overdue:
            filtered = [wo for wo in filtered if wo.is_overdue]
        
        # Apply pagination
        return filtered[work_order_filter.offset:work_order_filter.offset + work_order_filter.limit]
    
    def _publish_status_change(
        self,
        work_order: WorkOrder,
        old_status: WorkOrderStatus
    ) -> None:
        """Publish status change event."""
        if work_order.status == WorkOrderStatus.IN_PROGRESS:
            event_type = EventType.WORK_ORDER_STARTED
        elif work_order.status == WorkOrderStatus.COMPLETED:
            event_type = EventType.WORK_ORDER_COMPLETED
        elif work_order.status == WorkOrderStatus.CANCELLED:
            event_type = EventType.WORK_ORDER_CANCELLED
        else:
            event_type = EventType.WORK_ORDER_STATUS_CHANGED
        
        self.event_bus.publish(
            event_type,
            source="work_order_engine",
            data={
                "work_order_id": work_order.id,
                "asset_id": work_order.asset_id,
                "old_status": old_status.value,
                "new_status": work_order.status.value,
                "priority": work_order.priority.value,
            }
        )
