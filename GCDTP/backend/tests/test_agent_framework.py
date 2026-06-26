"""
Tests for Agent Framework

Tests agent definitions, task workflow, 
approval process, and execution.
"""

import pytest
from src.models.agent_definition import AgentDefinition, AgentType
from src.models.agent_task import AgentTask, TaskStatus
from src.models.agent_action import AgentAction, ApprovalStatus
from src.services.agent_service import AgentService
from src.schemas.agent import AgentTaskCreate, TaskApprovalRequest, TaskRejectRequest


class TestAgentDefinition:
    """Tests for agent definition."""
    
    def test_default_agents_created(self):
        """Test that default agents are created."""
        service = AgentService()
        agents = service.get_all_agents()
        
        assert len(agents) >= 5
        types = [a.agent_type for a in agents]
        assert AgentType.DIAGNOSTIC in types
        assert AgentType.MAINTENANCE in types
        assert AgentType.RECOVERY in types
        assert AgentType.KNOWLEDGE in types
        assert AgentType.TIMELINE in types
    
    def test_agent_capabilities(self):
        """Test agent capabilities."""
        service = AgentService()
        agents = service.get_all_agents()
        
        for agent in agents:
            caps = agent.get_capabilities()
            
            # All agents can analyze and propose
            assert caps["analyze_context"] is True
            assert caps["propose_actions"] is True
            
            # No agent can modify system
            assert caps["create_events"] is False
            assert caps["modify_health"] is False
            assert caps["alter_measurements"] is False
            assert caps["execute_automatically"] is False
    
    def test_get_enabled_agents(self):
        """Test getting enabled agents."""
        service = AgentService()
        enabled = service.get_enabled_agents()
        
        assert all(a.enabled for a in enabled)


class TestAgentTask:
    """Tests for agent task workflow."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = AgentService()
    
    def test_create_task(self):
        """Test creating a task."""
        agents = self.service.get_all_agents()
        agent = agents[0]
        
        request = AgentTaskCreate(
            agent_id=agent.id,
            task_type="diagnose",
            requested_by="test_user",
            context_data={"asset_id": "test-123"}
        )
        
        task = self.service.create_task(request)
        
        assert task is not None
        assert task.agent_id == agent.id
        assert task.task_type == "diagnose"
        assert task.status == TaskStatus.PENDING
        assert task.requested_by == "test_user"
    
    def test_task_pending_status(self):
        """Test task starts in pending status."""
        agents = self.service.get_all_agents()
        request = AgentTaskCreate(
            agent_id=agents[0].id,
            task_type="diagnose",
            requested_by="test"
        )
        
        task = self.service.create_task(request)
        
        assert task.is_pending() is True
        assert task.can_approve() is True
        assert task.can_execute() is False
    
    def test_approve_task(self):
        """Test approving a task."""
        agents = self.service.get_all_agents()
        request = AgentTaskCreate(
            agent_id=agents[0].id,
            task_type="diagnose",
            requested_by="test"
        )
        
        task = self.service.create_task(request)
        
        approve_request = TaskApprovalRequest(
            approved_by="supervisor"
        )
        
        updated = self.service.approve_task(task.id, approve_request)
        
        assert updated is not None
        assert updated.status == TaskStatus.APPROVED
        assert updated.approved_by == "supervisor"
        assert updated.can_execute() is True
    
    def test_reject_task(self):
        """Test rejecting a task."""
        agents = self.service.get_all_agents()
        request = AgentTaskCreate(
            agent_id=agents[0].id,
            task_type="diagnose",
            requested_by="test"
        )
        
        task = self.service.create_task(request)
        
        reject_request = TaskRejectRequest(
            rejected_by="supervisor",
            reason="Not needed"
        )
        
        updated = self.service.reject_task(task.id, reject_request)
        
        assert updated is not None
        assert updated.status == TaskStatus.REJECTED
        assert updated.result_data["rejection_reason"] == "Not needed"
    
    def test_execute_task(self):
        """Test executing an approved task."""
        agents = self.service.get_all_agents()
        request = AgentTaskCreate(
            agent_id=agents[0].id,
            task_type="diagnose",
            requested_by="test"
        )
        
        task = self.service.create_task(request)
        
        # Approve first
        self.service.approve_task(task.id, TaskApprovalRequest(approved_by="supervisor"))
        
        # Execute
        executed = self.service.execute_task(task.id, "operator")
        
        assert executed is not None
        assert executed.status == TaskStatus.EXECUTED
        assert executed.executed_at is not None
        assert executed.result_data is not None
    
    def test_cannot_execute_pending_task(self):
        """Test that pending tasks cannot be executed."""
        agents = self.service.get_all_agents()
        request = AgentTaskCreate(
            agent_id=agents[0].id,
            task_type="diagnose",
            requested_by="test"
        )
        
        task = self.service.create_task(request)
        
        with pytest.raises(ValueError):
            self.service.execute_task(task.id, "operator")
    
    def test_cannot_approve_executed_task(self):
        """Test that executed tasks cannot be approved."""
        agents = self.service.get_all_agents()
        request = AgentTaskCreate(
            agent_id=agents[0].id,
            task_type="diagnose",
            requested_by="test"
        )
        
        task = self.service.create_task(request)
        self.service.approve_task(task.id, TaskApprovalRequest(approved_by="supervisor"))
        self.service.execute_task(task.id, "operator")
        
        with pytest.raises(ValueError):
            self.service.approve_task(task.id, TaskApprovalRequest(approved_by="supervisor"))


class TestAgentActions:
    """Tests for agent actions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = AgentService()
    
    def test_add_action_to_task(self):
        """Test adding an action to a task."""
        agents = self.service.get_all_agents()
        request = AgentTaskCreate(
            agent_id=agents[0].id,
            task_type="diagnose",
            requested_by="test"
        )
        
        task = self.service.create_task(request)
        
        from src.schemas.agent import AgentActionCreate
        action_request = AgentActionCreate(
            task_id=task.id,
            action_type="analyze",
            action_payload={"asset_id": "test"}
        )
        
        action = self.service.add_action(action_request)
        
        assert action is not None
        assert action.task_id == task.id
        assert action.action_type == "analyze"
        assert action.approval_status == ApprovalStatus.PENDING
    
    def test_get_task_actions(self):
        """Test getting actions for a task."""
        agents = self.service.get_all_agents()
        request = AgentTaskCreate(
            agent_id=agents[0].id,
            task_type="diagnose",
            requested_by="test"
        )
        
        task = self.service.create_task(request)
        
        from src.schemas.agent import AgentActionCreate
        self.service.add_action(AgentActionCreate(
            task_id=task.id,
            action_type="analyze",
            action_payload={}
        ))
        
        actions = self.service.get_task_actions(task.id)
        assert len(actions) >= 1


class TestAgentWorkflow:
    """Tests for complete agent workflow."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = AgentService()
    
    def test_full_workflow(self):
        """Test complete workflow: create -> approve -> execute."""
        agents = self.service.get_all_agents()
        agent = agents[0]
        
        # 1. Create task
        request = AgentTaskCreate(
            agent_id=agent.id,
            task_type="diagnose",
            requested_by="operator",
            context_data={"asset": "substation-1"}
        )
        task = self.service.create_task(request)
        assert task.status == TaskStatus.PENDING
        
        # 2. Verify in pending list
        pending = self.service.get_pending_tasks()
        pending_ids = [t.id for t in pending]
        assert task.id in pending_ids
        
        # 3. Approve task
        task = self.service.approve_task(task.id, TaskApprovalRequest(approved_by="supervisor"))
        assert task.status == TaskStatus.APPROVED
        
        # 4. Verify not in pending list
        pending = self.service.get_pending_tasks()
        pending_ids = [t.id for t in pending]
        assert task.id not in pending_ids
        
        # 5. Execute task
        task = self.service.execute_task(task.id, "operator")
        assert task.status == TaskStatus.EXECUTED
        assert task.result_data is not None
        
        # 6. Verify in history
        history = self.service.get_task_history()
        history_ids = [t.id for t in history]
        assert task.id in history_ids


class TestAgentCapabilities:
    """Tests for agent capability restrictions."""
    
    def test_no_autonomous_actions(self):
        """Test that agents cannot act autonomously."""
        service = AgentService()
        agents = service.get_all_agents()
        
        for agent in agents:
            caps = agent.get_capabilities()
            
            # Forbidden capabilities
            assert caps["create_events"] is False
            assert caps["modify_health"] is False
            assert caps["alter_measurements"] is False
            assert caps["execute_automatically"] is False
            assert caps["close_work_orders"] is False
            assert caps["control_assets"] is False
            assert caps["send_notifications"] is False
    
    def test_allowed_capabilities(self):
        """Test that agents have allowed capabilities."""
        service = AgentService()
        agents = service.get_all_agents()
        
        for agent in agents:
            caps = agent.get_capabilities()
            
            # Allowed capabilities
            assert caps["analyze_context"] is True
            assert caps["propose_actions"] is True
            assert caps["create_recommendations"] is True
            assert caps["invoke_rag"] is True
