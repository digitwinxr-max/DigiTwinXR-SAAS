"""
Inspection Engine

Manages inspection tasks for work orders.
Handles inspection checklists, findings, and recommendations.
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from backend.src.services.work_orders.work_order_types import (
    InspectionTask,
    InspectionType,
    ChecklistItem,
    WorkOrder,
    WorkOrderStatus,
    WorkOrderCategory,
)
from backend.src.core.events import get_event_bus, EventType


class InspectionEngine:
    """
    Engine for managing inspection tasks.
    
    Responsibilities:
    - Create inspection tasks
    - Manage checklists
    - Record findings
    - Generate recommendations
    - Calculate condition ratings
    """
    
    # Default inspection checklists by type
    DEFAULT_CHECKLISTS = {
        InspectionType.VISUAL: [
            "Visual inspection of exterior",
            "Check for physical damage",
            "Inspect mounting and support",
            "Check warning labels",
            "Verify access panels secured",
        ],
        InspectionType.TECHNICAL: [
            "Check electrical connections",
            "Verify grounding",
            "Test control systems",
            "Calibrate sensors",
            "Check for firmware updates",
            "Test safety interlocks",
        ],
        InspectionType.SAFETY: [
            "Verify emergency stops",
            "Check guard protection",
            "Test alarm systems",
            "Inspect fire protection",
            "Check ventilation",
            "Verify lockout/tagout points",
        ],
        InspectionType.ENVIRONMENTAL: [
            "Check emissions controls",
            "Verify containment",
            "Inspect drainage",
            "Check spill prevention",
            "Test monitoring equipment",
            "Verify permits compliance",
        ],
        InspectionType.PERFORMANCE: [
            "Measure output capacity",
            "Check efficiency",
            "Verify response times",
            "Test load capacity",
            "Check stability",
            "Measure noise levels",
        ],
    }
    
    def __init__(self):
        self.event_bus = get_event_bus()
    
    def create_inspection_task(
        self,
        work_order: WorkOrder,
        asset_id: str,
        inspection_type: InspectionType,
        inspector: Optional[str] = None,
        inspection_method: Optional[str] = None,
        checklist: Optional[List[str]] = None,
        session_id: Optional[str] = None
    ) -> InspectionTask:
        """
        Create an inspection task.
        
        Args:
            work_order: Parent work order
            asset_id: Target asset ID
            inspection_type: Type of inspection
            inspector: Inspector name
            inspection_method: Specific method
            checklist: Custom checklist items
            session_id: Timeline session ID
            
        Returns:
            Created InspectionTask
        """
        # Use default checklist if not provided
        if checklist is None:
            checklist = self.DEFAULT_CHECKLISTS.get(inspection_type, [])
        
        # Convert to ChecklistItem objects
        checklist_items = [
            ChecklistItem(item=item)
            for item in checklist
        ]
        
        inspection = InspectionTask(
            id=str(uuid.uuid4()),
            work_order_id=work_order.id,
            asset_id=asset_id,
            inspection_type=inspection_type,
            inspection_method=inspection_method,
            checklist=checklist_items,
            inspector=inspector,
            metadata={"session_id": session_id} if session_id else {}
        )
        
        # Publish event
        self.event_bus.publish(
            EventType.INSPECTION_CREATED,
            source="inspection_engine",
            data={
                "inspection_id": inspection.id,
                "work_order_id": work_order.id,
                "asset_id": asset_id,
                "inspection_type": inspection_type.value,
                "inspector": inspector,
            }
        )
        
        return inspection
    
    def add_checklist_item(
        self,
        inspection: InspectionTask,
        item: str
    ) -> InspectionTask:
        """
        Add an item to the inspection checklist.
        
        Args:
            inspection: Inspection task
            item: Checklist item text
            
        Returns:
            Updated InspectionTask
        """
        inspection.checklist.append(ChecklistItem(item=item))
        inspection.updated_at = datetime.utcnow()
        return inspection
    
    def complete_checklist_item(
        self,
        inspection: InspectionTask,
        item_index: int,
        notes: Optional[str] = None
    ) -> InspectionTask:
        """
        Mark a checklist item as completed.
        
        Args:
            inspection: Inspection task
            item_index: Index of item to complete
            notes: Completion notes
            
        Returns:
            Updated InspectionTask
        """
        if 0 <= item_index < len(inspection.checklist):
            inspection.checklist[item_index].completed = True
            inspection.checklist[item_index].completed_at = datetime.utcnow()
            if notes:
                inspection.checklist[item_index].notes = notes
            inspection.updated_at = datetime.utcnow()
        return inspection
    
    def record_findings(
        self,
        inspection: InspectionTask,
        findings: str,
        results: Optional[Dict] = None
    ) -> InspectionTask:
        """
        Record inspection findings.
        
        Args:
            inspection: Inspection task
            findings: Text findings
            results: Structured results
            
        Returns:
            Updated InspectionTask
        """
        inspection.findings = findings
        if results:
            inspection.results = results
        inspection.updated_at = datetime.utcnow()
        return inspection
    
    def set_condition_rating(
        self,
        inspection: InspectionTask,
        rating: int
    ) -> InspectionTask:
        """
        Set condition rating (1-5).
        
        Args:
            inspection: Inspection task
            rating: Rating value (1-5)
            
        Returns:
            Updated InspectionTask
        """
        if not 1 <= rating <= 5:
            raise ValueError("Condition rating must be between 1 and 5")
        
        inspection.condition_rating = rating
        inspection.updated_at = datetime.utcnow()
        return inspection
    
    def add_recommendation(
        self,
        inspection: InspectionTask,
        recommendation: str
    ) -> InspectionTask:
        """
        Add a recommendation.
        
        Args:
            inspection: Inspection task
            recommendation: Recommendation text
            
        Returns:
            Updated InspectionTask
        """
        if inspection.recommendations:
            inspection.recommendations += f"\n- {recommendation}"
        else:
            inspection.recommendations = f"- {recommendation}"
        inspection.updated_at = datetime.utcnow()
        return inspection
    
    def schedule_next_inspection(
        self,
        inspection: InspectionTask,
        interval_days: int = 90
    ) -> InspectionTask:
        """
        Schedule next inspection.
        
        Args:
            inspection: Inspection task
            interval_days: Days until next inspection
            
        Returns:
            Updated InspectionTask
        """
        inspection.next_inspection_date = datetime.utcnow() + timedelta(days=interval_days)
        inspection.updated_at = datetime.utcnow()
        return inspection
    
    def add_attachment(
        self,
        inspection: InspectionTask,
        attachment_url: str,
        description: Optional[str] = None
    ) -> InspectionTask:
        """
        Add an attachment reference.
        
        Args:
            inspection: Inspection task
            attachment_url: URL to attachment
            description: Attachment description
            
        Returns:
            Updated InspectionTask
        """
        attachment = {
            "url": attachment_url,
            "description": description,
            "added_at": datetime.utcnow().isoformat()
        }
        inspection.attachments.append(attachment)
        inspection.updated_at = datetime.utcnow()
        return inspection
    
    def get_checklist_completion(self, inspection: InspectionTask) -> Dict:
        """
        Get checklist completion status.
        
        Args:
            inspection: Inspection task
            
        Returns:
            Completion statistics
        """
        total = len(inspection.checklist)
        completed = sum(1 for item in inspection.checklist if item.completed)
        
        return {
            "total": total,
            "completed": completed,
            "remaining": total - completed,
            "percentage": (completed / total * 100) if total > 0 else 100,
        }
    
    def is_inspection_complete(self, inspection: InspectionTask) -> bool:
        """
        Check if inspection is complete.
        
        Args:
            inspection: Inspection task
            
        Returns:
            True if complete
        """
        # All checklist items completed
        if not all(item.completed for item in inspection.checklist):
            return False
        
        # Has findings
        if not inspection.findings:
            return False
        
        # Has condition rating
        if not inspection.condition_rating:
            return False
        
        return True
    
    def generate_report(self, inspection: InspectionTask) -> Dict:
        """
        Generate inspection report.
        
        Args:
            inspection: Inspection task
            
        Returns:
            Report dictionary
        """
        completion = self.get_checklist_completion(inspection)
        
        return {
            "inspection_id": inspection.id,
            "work_order_id": inspection.work_order_id,
            "asset_id": inspection.asset_id,
            "type": inspection.inspection_type.value,
            "method": inspection.inspection_method,
            "inspector": inspection.inspector,
            "date": inspection.inspection_date.isoformat(),
            "checklist_completion": completion,
            "findings": inspection.findings,
            "condition_rating": inspection.condition_rating,
            "recommendations": inspection.recommendations,
            "next_inspection": inspection.next_inspection_date.isoformat() if inspection.next_inspection_date else None,
            "attachments_count": len(inspection.attachments),
        }
    
    def create_inspection_from_category(
        self,
        work_order: WorkOrder,
        asset_id: str,
        inspector: Optional[str] = None
    ) -> InspectionTask:
        """
        Create inspection task based on work order category.
        
        Args:
            work_order: Parent work order
            asset_id: Target asset
            inspector: Inspector name
            
        Returns:
            Created InspectionTask
        """
        # Map category to inspection type
        category_to_type = {
            WorkOrderCategory.INSPECTION: InspectionType.VISUAL,
            WorkOrderCategory.PREVENTIVE: InspectionType.TECHNICAL,
            WorkOrderCategory.EMERGENCY: InspectionType.SAFETY,
            WorkOrderCategory.ROUTINE: InspectionType.VISUAL,
        }
        
        inspection_type = category_to_type.get(
            work_order.category,
            InspectionType.VISUAL
        )
        
        return self.create_inspection_task(
            work_order=work_order,
            asset_id=asset_id,
            inspection_type=inspection_type,
            inspector=inspector
        )
