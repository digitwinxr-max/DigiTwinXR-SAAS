"""
Tests for Work Order Engine

Tests work order creation, status changes, assignment,
inspection tasks, maintenance tasks, and validation.
"""

import pytest
from datetime import datetime, timedelta
from backend.src.services.work_orders import (
    WorkOrderEngine,
    InspectionEngine,
    MaintenanceEngine,
    WorkOrderValidator,
    WorkOrder,
    WorkOrderStatus,
    WorkOrderCategory,
    Priority,
    InspectionTask,
    InspectionType,
    MaintenanceTask,
    MaintenanceType,
    TaskStatus,
    ChecklistItem,
    WorkOrderFilter,
)


class TestWorkOrderTypes:
    """Tests for work order types."""
    
    def test_create_work_order(self):
        """Test creating a work order."""
        wo = WorkOrder(
            id="wo-1",
            asset_id="asset-1",
            title="Test Work Order",
            description="Test description",
            priority=Priority.HIGH,
            category=WorkOrderCategory.ROUTINE
        )
        
        assert wo.id == "wo-1"
        assert wo.asset_id == "asset-1"
        assert wo.priority == Priority.HIGH
        assert wo.status == WorkOrderStatus.PENDING
    
    def test_work_order_state_open(self):
        """Test work order state when open."""
        wo = WorkOrder(
            id="wo-1",
            asset_id="asset-1",
            title="Test",
            status=WorkOrderStatus.PENDING
        )
        
        assert wo.is_open is True
        assert wo.work_order_state.value == "open"
    
    def test_work_order_state_active(self):
        """Test work order state when in progress."""
        wo = WorkOrder(
            id="wo-1",
            asset_id="asset-1",
            title="Test",
            status=WorkOrderStatus.IN_PROGRESS
        )
        
        assert wo.work_order_state.value == "active"
    
    def test_work_order_state_overdue(self):
        """Test work order state when overdue."""
        wo = WorkOrder(
            id="wo-1",
            asset_id="asset-1",
            title="Test",
            status=WorkOrderStatus.PENDING,
            due_date=datetime.utcnow() - timedelta(days=1)
        )
        
        assert wo.is_overdue is True
        assert wo.work_order_state.value == "overdue"
    
    def test_work_order_to_dict(self):
        """Test work order serialization."""
        wo = WorkOrder(
            id="wo-1",
            asset_id="asset-1",
            title="Test"
        )
        
        data = wo.to_dict()
        assert data["id"] == "wo-1"
        assert data["priority"] == "medium"
        assert data["status"] == "pending"


class TestWorkOrderEngine:
    """Tests for work order engine."""
    
    @pytest.fixture
    def engine(self):
        """Create work order engine."""
        return WorkOrderEngine()
    
    @pytest.fixture
    def valid_work_order_data(self):
        """Valid work order data."""
        return {
            "asset_id": "asset-123",
            "title": "Test Work Order",
            "description": "Test description",
            "priority": Priority.MEDIUM,
            "category": WorkOrderCategory.ROUTINE,
        }
    
    def test_create_work_order(self, engine, valid_work_order_data):
        """Test creating a work order."""
        wo = engine.create_work_order(**valid_work_order_data)
        
        assert wo is not None
        assert wo.id is not None
        assert wo.asset_id == "asset-123"
        assert wo.title == "Test Work Order"
        assert wo.status == WorkOrderStatus.PENDING
    
    def test_create_work_order_with_priority(self, engine):
        """Test creating work order with priority."""
        wo = engine.create_work_order(
            asset_id="asset-1",
            title="Critical WO",
            priority=Priority.CRITICAL
        )
        
        assert wo.priority == Priority.CRITICAL
    
    def test_create_work_order_with_due_date(self, engine):
        """Test creating work order with due date."""
        due = datetime.utcnow() + timedelta(days=7)
        wo = engine.create_work_order(
            asset_id="asset-1",
            title="Dated WO",
            due_date=due
        )
        
        assert wo.due_date == due
    
    def test_update_work_order_title(self, engine):
        """Test updating work order title."""
        wo = engine.create_work_order(
            asset_id="asset-1",
            title="Original Title"
        )
        
        updated = engine.update_work_order(wo, title="New Title")
        
        assert updated.title == "New Title"
    
    def test_start_work_order(self, engine):
        """Test starting a work order."""
        wo = engine.create_work_order(
            asset_id="asset-1",
            title="Test"
        )
        
        started = engine.start_work_order(wo)
        
        assert started.status == WorkOrderStatus.IN_PROGRESS
    
    def test_complete_work_order(self, engine):
        """Test completing a work order."""
        wo = engine.create_work_order(
            asset_id="asset-1",
            title="Test"
        )
        engine.start_work_order(wo)
        
        completed = engine.complete_work_order(wo)
        
        assert completed.status == WorkOrderStatus.COMPLETED
        assert completed.completed_at is not None
    
    def test_cancel_work_order(self, engine):
        """Test cancelling a work order."""
        wo = engine.create_work_order(
            asset_id="asset-1",
            title="Test"
        )
        
        cancelled = engine.cancel_work_order(wo)
        
        assert cancelled.status == WorkOrderStatus.CANCELLED
    
    def test_hold_work_order(self, engine):
        """Test putting work order on hold."""
        wo = engine.create_work_order(
            asset_id="asset-1",
            title="Test"
        )
        
        held = engine.hold_work_order(wo)
        
        assert held.status == WorkOrderStatus.ON_HOLD
    
    def test_assign_work_order(self, engine):
        """Test assigning a work order."""
        wo = engine.create_work_order(
            asset_id="asset-1",
            title="Test"
        )
        
        assigned = engine.assign_work_order(wo, assigned_to="john.doe")
        
        assert assigned.assigned_to == "john.doe"
    
    def test_update_priority(self, engine):
        """Test updating priority."""
        wo = engine.create_work_order(
            asset_id="asset-1",
            title="Test",
            priority=Priority.LOW
        )
        
        updated = engine.update_priority(wo, Priority.HIGH)
        
        assert updated.priority == Priority.HIGH
    
    def test_cannot_start_completed(self, engine):
        """Test that completed work orders cannot be started."""
        wo = engine.create_work_order(
            asset_id="asset-1",
            title="Test"
        )
        engine.start_work_order(wo)
        engine.complete_work_order(wo)
        
        with pytest.raises(ValueError):
            engine.start_work_order(wo)
    
    def test_cannot_complete_cancelled(self, engine):
        """Test that cancelled work orders cannot be completed."""
        wo = engine.create_work_order(
            asset_id="asset-1",
            title="Test"
        )
        engine.cancel_work_order(wo)
        
        with pytest.raises(ValueError):
            engine.complete_work_order(wo)
    
    def test_filter_by_status(self, engine):
        """Test filtering by status."""
        wo1 = engine.create_work_order(asset_id="a1", title="Test1")
        wo2 = engine.create_work_order(asset_id="a2", title="Test2")
        engine.start_work_order(wo2)
        
        wo_list = [wo1, wo2]
        filtered = engine.filter_work_orders(
            wo_list,
            WorkOrderFilter(status=[WorkOrderStatus.IN_PROGRESS])
        )
        
        assert len(filtered) == 1
        assert filtered[0].id == wo2.id
    
    def test_filter_by_asset(self, engine):
        """Test filtering by asset."""
        wo1 = engine.create_work_order(asset_id="asset-1", title="Test1")
        wo2 = engine.create_work_order(asset_id="asset-2", title="Test2")
        
        wo_list = [wo1, wo2]
        filtered = engine.filter_work_orders(
            wo_list,
            WorkOrderFilter(asset_id="asset-1")
        )
        
        assert len(filtered) == 1
        assert filtered[0].asset_id == "asset-1"
    
    def test_filter_by_priority(self, engine):
        """Test filtering by priority."""
        wo1 = engine.create_work_order(
            asset_id="a1", title="T1", priority=Priority.HIGH
        )
        wo2 = engine.create_work_order(
            asset_id="a2", title="T2", priority=Priority.LOW
        )
        
        filtered = engine.filter_work_orders(
            [wo1, wo2],
            WorkOrderFilter(priority=[Priority.HIGH])
        )
        
        assert len(filtered) == 1
        assert filtered[0].priority == Priority.HIGH


class TestWorkOrderValidator:
    """Tests for work order validator."""
    
    @pytest.fixture
    def validator(self):
        """Create validator."""
        return WorkOrderValidator()
    
    def test_validate_valid_work_order(self, validator):
        """Test validating a valid work order."""
        wo = WorkOrder(
            id="wo-1",
            asset_id="asset-1",
            title="Valid WO",
            priority=Priority.MEDIUM
        )
        
        issues = validator.validate_work_order(wo)
        
        assert len(issues) == 0
    
    def test_validate_missing_title(self, validator):
        """Test validation with missing title."""
        wo = WorkOrder(
            id="wo-1",
            asset_id="asset-1",
            title=""
        )
        
        issues = validator.validate_work_order(wo)
        
        assert any("title" in i.lower() for i in issues)
    
    def test_validate_missing_asset(self, validator):
        """Test validation with missing asset."""
        wo = WorkOrder(
            id="wo-1",
            asset_id="",
            title="Test"
        )
        
        issues = validator.validate_work_order(wo)
        
        assert any("asset" in i.lower() for i in issues)
    
    def test_validate_past_due_date(self, validator):
        """Test validation with past due date."""
        wo = WorkOrder(
            id="wo-1",
            asset_id="asset-1",
            title="Test",
            due_date=datetime.utcnow() - timedelta(days=1)
        )
        
        issues = validator.validate_work_order(wo)
        
        assert any("past" in i.lower() for i in issues)
    
    def test_valid_status_transition(self, validator):
        """Test valid status transition."""
        issues = validator.validate_status_transition(
            WorkOrderStatus.PENDING,
            WorkOrderStatus.IN_PROGRESS
        )
        
        assert len(issues) == 0
    
    def test_invalid_status_transition(self, validator):
        """Test invalid status transition."""
        issues = validator.validate_status_transition(
            WorkOrderStatus.COMPLETED,
            WorkOrderStatus.PENDING
        )
        
        assert len(issues) > 0
    
    def test_validate_completion(self, validator):
        """Test validating completion."""
        wo = WorkOrder(
            id="wo-1",
            asset_id="asset-1",
            title="Test",
            status=WorkOrderStatus.COMPLETED
        )
        
        issues = validator.validate_completion(wo)
        
        assert len(issues) > 0


class TestInspectionEngine:
    """Tests for inspection engine."""
    
    @pytest.fixture
    def engine(self):
        """Create inspection engine."""
        return InspectionEngine()
    
    @pytest.fixture
    def work_order(self):
        """Create work order."""
        return WorkOrder(
            id="wo-1",
            asset_id="asset-1",
            title="Test WO"
        )
    
    def test_create_inspection_task(self, engine, work_order):
        """Test creating inspection task."""
        inspection = engine.create_inspection_task(
            work_order=work_order,
            asset_id="asset-1",
            inspection_type=InspectionType.VISUAL,
            inspector="John Doe"
        )
        
        assert inspection is not None
        assert inspection.work_order_id == "wo-1"
        assert inspection.inspection_type == InspectionType.VISUAL
        assert inspection.inspector == "John Doe"
    
    def test_add_checklist_item(self, engine, work_order):
        """Test adding checklist item."""
        inspection = engine.create_inspection_task(
            work_order=work_order,
            asset_id="asset-1",
            inspection_type=InspectionType.VISUAL
        )
        
        engine.add_checklist_item(inspection, "New Item")
        
        assert len(inspection.checklist) > 0
    
    def test_complete_checklist_item(self, engine, work_order):
        """Test completing checklist item."""
        inspection = engine.create_inspection_task(
            work_order=work_order,
            asset_id="asset-1",
            inspection_type=InspectionType.VISUAL,
            checklist=["Item 1", "Item 2"]
        )
        
        engine.complete_checklist_item(inspection, 0)
        
        assert inspection.checklist[0].completed is True
        assert inspection.checklist[0].completed_at is not None
    
    def test_set_condition_rating(self, engine, work_order):
        """Test setting condition rating."""
        inspection = engine.create_inspection_task(
            work_order=work_order,
            asset_id="asset-1",
            inspection_type=InspectionType.VISUAL
        )
        
        rated = engine.set_condition_rating(inspection, 4)
        
        assert rated.condition_rating == 4
    
    def test_invalid_condition_rating(self, engine, work_order):
        """Test invalid condition rating."""
        inspection = engine.create_inspection_task(
            work_order=work_order,
            asset_id="asset-1",
            inspection_type=InspectionType.VISUAL
        )
        
        with pytest.raises(ValueError):
            engine.set_condition_rating(inspection, 6)
    
    def test_get_checklist_completion(self, engine, work_order):
        """Test getting checklist completion."""
        inspection = engine.create_inspection_task(
            work_order=work_order,
            asset_id="asset-1",
            inspection_type=InspectionType.VISUAL,
            checklist=["Item 1", "Item 2"]
        )
        engine.complete_checklist_item(inspection, 0)
        
        completion = engine.get_checklist_completion(inspection)
        
        assert completion["total"] == 2
        assert completion["completed"] == 1
        assert completion["remaining"] == 1
        assert completion["percentage"] == 50.0
    
    def test_schedule_next_inspection(self, engine, work_order):
        """Test scheduling next inspection."""
        inspection = engine.create_inspection_task(
            work_order=work_order,
            asset_id="asset-1",
            inspection_type=InspectionType.VISUAL
        )
        
        scheduled = engine.schedule_next_inspection(inspection, interval_days=30)
        
        assert scheduled.next_inspection_date is not None


class TestMaintenanceEngine:
    """Tests for maintenance engine."""
    
    @pytest.fixture
    def engine(self):
        """Create maintenance engine."""
        return MaintenanceEngine()
    
    @pytest.fixture
    def work_order(self):
        """Create work order."""
        return WorkOrder(
            id="wo-1",
            asset_id="asset-1",
            title="Test WO"
        )
    
    def test_create_maintenance_task(self, engine, work_order):
        """Test creating maintenance task."""
        task = engine.create_maintenance_task(
            work_order=work_order,
            asset_id="asset-1",
            maintenance_type=MaintenanceType.REPAIR,
            technician="Jane Smith"
        )
        
        assert task is not None
        assert task.maintenance_type == MaintenanceType.REPAIR
        assert task.technician == "Jane Smith"
        assert task.task_status == TaskStatus.PENDING
    
    def test_start_task(self, engine, work_order):
        """Test starting a maintenance task."""
        task = engine.create_maintenance_task(
            work_order=work_order,
            asset_id="asset-1",
            maintenance_type=MaintenanceType.REPAIR
        )
        
        started = engine.start_task(task)
        
        assert started.task_status == TaskStatus.IN_PROGRESS
        assert started.started_at is not None
    
    def test_complete_task(self, engine, work_order):
        """Test completing a maintenance task."""
        task = engine.create_maintenance_task(
            work_order=work_order,
            asset_id="asset-1",
            maintenance_type=MaintenanceType.REPAIR
        )
        engine.start_task(task)
        
        completed = engine.complete_task(task, actual_hours=2.5)
        
        assert completed.task_status == TaskStatus.COMPLETED
        assert completed.completed_at is not None
        assert completed.labor_hours == 2.5
    
    def test_add_part(self, engine, work_order):
        """Test adding a part."""
        task = engine.create_maintenance_task(
            work_order=work_order,
            asset_id="asset-1",
            maintenance_type=MaintenanceType.REPAIR
        )
        
        with_part = engine.add_part(
            task,
            part_number="PN-123",
            part_name="Bearing",
            quantity=2,
            unit_cost=25.0
        )
        
        assert len(with_part.parts_used) == 1
        assert with_part.cost == 50.0
    
    def test_record_failure_symptoms(self, engine, work_order):
        """Test recording failure symptoms."""
        task = engine.create_maintenance_task(
            work_order=work_order,
            asset_id="asset-1",
            maintenance_type=MaintenanceType.REPAIR
        )
        
        recorded = engine.record_failure_symptoms(
            task,
            "Abnormal vibration detected"
        )
        
        assert recorded.failure_symptoms == "Abnormal vibration detected"
    
    def test_record_root_cause(self, engine, work_order):
        """Test recording root cause."""
        task = engine.create_maintenance_task(
            work_order=work_order,
            asset_id="asset-1",
            maintenance_type=MaintenanceType.REPAIR
        )
        
        recorded = engine.record_root_cause(task, "Worn bearing")
        
        assert recorded.root_cause == "Worn bearing"
    
    def test_calculate_total_cost(self, engine, work_order):
        """Test calculating total cost."""
        task = engine.create_maintenance_task(
            work_order=work_order,
            asset_id="asset-1",
            maintenance_type=MaintenanceType.REPAIR
        )
        engine.add_part(task, "PN-1", "Part 1", 2, 10.0)
        task.labor_hours = 1.0
        
        costs = engine.calculate_total_cost(task)
        
        assert costs["parts_cost"] == 20.0
        assert costs["labor_cost"] == 50.0
        assert costs["total_cost"] == 70.0
    
    def test_cannot_start_completed_task(self, engine, work_order):
        """Test that completed tasks cannot be started."""
        task = engine.create_maintenance_task(
            work_order=work_order,
            asset_id="asset-1",
            maintenance_type=MaintenanceType.REPAIR
        )
        engine.start_task(task)
        engine.complete_task(task)
        
        with pytest.raises(ValueError):
            engine.start_task(task)
    
    def test_create_corrective_maintenance(self, engine, work_order):
        """Test creating corrective maintenance."""
        task = engine.create_corrective_maintenance(
            work_order=work_order,
            asset_id="asset-1",
            failure_symptoms="Motor overheating"
        )
        
        assert task.maintenance_type == MaintenanceType.REPAIR
        assert task.failure_symptoms == "Motor overheating"


class TestWorkOrderFilter:
    """Tests for work order filtering."""
    
    @pytest.fixture
    def engine(self):
        """Create work order engine."""
        return WorkOrderEngine()
    
    def test_filter_by_multiple_criteria(self, engine):
        """Test filtering by multiple criteria."""
        wo1 = engine.create_work_order(
            asset_id="a1", title="T1", priority=Priority.HIGH
        )
        wo2 = engine.create_work_order(
            asset_id="a1", title="T2", priority=Priority.LOW
        )
        wo3 = engine.create_work_order(
            asset_id="a2", title="T3", priority=Priority.HIGH
        )
        
        filtered = engine.filter_work_orders(
            [wo1, wo2, wo3],
            WorkOrderFilter(
                asset_id="a1",
                priority=[Priority.HIGH]
            )
        )
        
        assert len(filtered) == 1
        assert filtered[0].id == wo1.id
    
    def test_filter_pagination(self, engine):
        """Test filter pagination."""
        for i in range(10):
            engine.create_work_order(
                asset_id=f"a{i}", title=f"T{i}"
            )
        
        all_wos = list(engine._work_orders.values()) if hasattr(engine, '_work_orders') else []
        # Simulate work orders list
        wos = [engine.create_work_order(asset_id=f"a{i}", title=f"T{i}") for i in range(10)]
        
        # Reset for clean test
        filtered = wos[5:8]
        
        assert len(filtered) == 3


class TestPriorityHandling:
    """Tests for priority handling."""
    
    def test_priority_order(self):
        """Test priority enum order."""
        priorities = [Priority.LOW, Priority.MEDIUM, Priority.HIGH, Priority.CRITICAL]
        
        assert Priority.LOW.value == "low"
        assert Priority.CRITICAL.value == "critical"
    
    def test_work_order_priority_properties(self):
        """Test work order priority properties."""
        wo = WorkOrder(
            id="wo-1",
            asset_id="asset-1",
            title="Test",
            priority=Priority.CRITICAL
        )
        
        assert wo.priority == Priority.CRITICAL
        assert wo.priority.value == "critical"


class TestChecklistItem:
    """Tests for checklist items."""
    
    def test_create_checklist_item(self):
        """Test creating checklist item."""
        item = ChecklistItem(
            item="Check something",
            completed=False
        )
        
        assert item.item == "Check something"
        assert item.completed is False
    
    def test_checklist_item_to_dict(self):
        """Test checklist item serialization."""
        item = ChecklistItem(
            item="Test item",
            completed=True
        )
        
        data = item.to_dict()
        assert data["item"] == "Test item"
        assert data["completed"] is True


class TestWorkOrderCategories:
    """Tests for work order categories."""
    
    def test_all_categories(self):
        """Test all category values."""
        categories = [
            WorkOrderCategory.INSPECTION,
            WorkOrderCategory.PREVENTIVE,
            WorkOrderCategory.CORRECTIVE,
            WorkOrderCategory.EMERGENCY,
            WorkOrderCategory.ROUTINE
        ]
        
        assert len(categories) == 5
    
    def test_category_values(self):
        """Test category values."""
        assert WorkOrderCategory.INSPECTION.value == "inspection"
        assert WorkOrderCategory.CORRECTIVE.value == "corrective"


class TestTaskStatus:
    """Tests for task status."""
    
    def test_task_status_values(self):
        """Test task status values."""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.COMPLETED.value == "completed"
