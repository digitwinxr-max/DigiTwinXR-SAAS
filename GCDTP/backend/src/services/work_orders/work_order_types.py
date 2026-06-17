"""
Work Order Types

Core data types for the Work Order Engine.
Asset-centric work order management.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from uuid import UUID


class Priority(str, Enum):
    """Work order priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WorkOrderStatus(str, Enum):
    """Work order status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class WorkOrderCategory(str, Enum):
    """Work order categories."""
    INSPECTION = "inspection"
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    EMERGENCY = "emergency"
    ROUTINE = "routine"


class TaskStatus(str, Enum):
    """Task status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InspectionType(str, Enum):
    """Inspection types."""
    VISUAL = "visual"
    TECHNICAL = "technical"
    SAFETY = "safety"
    ENVIRONMENTAL = "environmental"
    PERFORMANCE = "performance"


class MaintenanceType(str, Enum):
    """Maintenance types."""
    REPAIR = "repair"
    REPLACEMENT = "replacement"
    CALIBRATION = "calibration"
    ALIGNMENT = "alignment"
    LUBRICATION = "lubrication"
    CLEANING = "cleaning"
    UPGRADE = "upgrade"


class WorkOrderState(str, Enum):
    """Computed work order state."""
    OPEN = "open"
    ACTIVE = "active"
    CLOSED = "closed"
    OVERDUE = "overdue"


@dataclass
class ChecklistItem:
    """Inspection checklist item."""
    item: str
    completed: bool = False
    notes: str = ""
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            "item": self.item,
            "completed": self.completed,
            "notes": self.notes,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


@dataclass
class WorkOrder:
    """
    Asset-centric work order.
    
    Links maintenance activities to specific assets.
    """
    id: str
    asset_id: str
    title: str
    description: str = ""
    priority: Priority = Priority.MEDIUM
    status: WorkOrderStatus = WorkOrderStatus.PENDING
    category: WorkOrderCategory = WorkOrderCategory.ROUTINE
    assigned_to: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_session_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "asset_id": self.asset_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "category": self.category.value,
            "assigned_to": self.assigned_to,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "estimated_hours": self.estimated_hours,
            "actual_hours": self.actual_hours,
            "notes": self.notes,
            "metadata": self.metadata,
        }
    
    @property
    def is_open(self) -> bool:
        """Check if work order is open."""
        return self.status in [WorkOrderStatus.PENDING, WorkOrderStatus.IN_PROGRESS]
    
    @property
    def is_overdue(self) -> bool:
        """Check if work order is overdue."""
        if self.completed_at or not self.due_date:
            return False
        return datetime.utcnow() > self.due_date and self.status != WorkOrderStatus.COMPLETED
    
    @property
    def work_order_state(self) -> WorkOrderState:
        """Compute work order state."""
        if self.status == WorkOrderStatus.COMPLETED:
            return WorkOrderState.CLOSED
        if self.due_date and self.is_overdue:
            return WorkOrderState.OVERDUE
        if self.status == WorkOrderStatus.IN_PROGRESS:
            return WorkOrderState.ACTIVE
        return WorkOrderState.OPEN


@dataclass
class InspectionTask:
    """
    Inspection task linked to a work order.
    
    Records inspection findings and recommendations.
    """
    id: str
    work_order_id: str
    asset_id: str
    inspection_type: InspectionType
    inspection_method: Optional[str] = None
    checklist: List[ChecklistItem] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)
    inspector: Optional[str] = None
    inspection_date: datetime = field(default_factory=datetime.utcnow)
    findings: str = ""
    recommendations: str = ""
    condition_rating: Optional[int] = None  # 1-5
    next_inspection_date: Optional[datetime] = None
    attachments: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "work_order_id": self.work_order_id,
            "asset_id": self.asset_id,
            "inspection_type": self.inspection_type.value,
            "inspection_method": self.inspection_method,
            "checklist": [c.to_dict() for c in self.checklist],
            "results": self.results,
            "inspector": self.inspector,
            "inspection_date": self.inspection_date.isoformat(),
            "findings": self.findings,
            "recommendations": self.recommendations,
            "condition_rating": self.condition_rating,
            "next_inspection_date": self.next_inspection_date.isoformat() if self.next_inspection_date else None,
            "attachments": self.attachments,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class MaintenanceTask:
    """
    Maintenance task linked to a work order.
    
    Records repair/replacement activities.
    """
    id: str
    work_order_id: str
    asset_id: str
    maintenance_type: MaintenanceType
    parts_used: List[Dict] = field(default_factory=list)
    labor_hours: float = 0.0
    technician: Optional[str] = None
    task_status: TaskStatus = TaskStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failure_symptoms: str = ""
    root_cause: str = ""
    corrective_action: str = ""
    cost: float = 0.0
    warranty_info: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "work_order_id": self.work_order_id,
            "asset_id": self.asset_id,
            "maintenance_type": self.maintenance_type.value,
            "parts_used": self.parts_used,
            "labor_hours": self.labor_hours,
            "technician": self.technician,
            "task_status": self.task_status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "failure_symptoms": self.failure_symptoms,
            "root_cause": self.root_cause,
            "corrective_action": self.corrective_action,
            "cost": self.cost,
            "warranty_info": self.warranty_info,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class WorkOrderSummary:
    """Summary view of a work order with counts."""
    work_order: WorkOrder
    inspection_count: int = 0
    maintenance_count: int = 0
    
    def to_dict(self) -> Dict:
        data = self.work_order.to_dict()
        data["inspection_count"] = self.inspection_count
        data["maintenance_count"] = self.maintenance_count
        data["work_order_state"] = self.work_order.work_order_state.value
        return data


@dataclass
class WorkOrderFilter:
    """Filter criteria for work order queries."""
    asset_id: Optional[str] = None
    status: Optional[List[WorkOrderStatus]] = None
    priority: Optional[List[Priority]] = None
    category: Optional[List[WorkOrderCategory]] = None
    assigned_to: Optional[str] = None
    created_by: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    due_before: Optional[datetime] = None
    due_after: Optional[datetime] = None
    overdue: bool = False
    limit: int = 100
    offset: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "asset_id": self.asset_id,
            "status": [s.value for s in self.status] if self.status else None,
            "priority": [p.value for p in self.priority] if self.priority else None,
            "category": [c.value for c in self.category] if self.category else None,
            "assigned_to": self.assigned_to,
            "created_by": self.created_by,
            "created_after": self.created_after.isoformat() if self.created_after else None,
            "created_before": self.created_before.isoformat() if self.created_before else None,
            "due_before": self.due_before.isoformat() if self.due_before else None,
            "due_after": self.due_after.isoformat() if self.due_after else None,
            "overdue": self.overdue,
            "limit": self.limit,
            "offset": self.offset,
        }
