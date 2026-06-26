"""
Tests for Node-RED Integration

Tests workflow lifecycle, connectors, triggers, history, retry, validation, and timeline integration.
"""

import pytest
from datetime import datetime
from backend.src.integrations.node_red import (
    FlowManager,
    WorkflowAdapter,
    ConnectorRegistry,
    WorkflowValidator,
    NodeREDClient,
    ExecutionStatus,
    TriggerType,
    ConnectorType,
    WorkflowDefinition,
    WorkflowInstance,
)


class TestWorkflowTypes:
    """Tests for workflow types."""
    
    def test_execution_status_values(self):
        """Test execution status values."""
        statuses = [
            ExecutionStatus.PENDING,
            ExecutionStatus.RUNNING,
            ExecutionStatus.COMPLETED,
            ExecutionStatus.FAILED,
            ExecutionStatus.CANCELLED,
            ExecutionStatus.RETRYING,
        ]
        assert len(statuses) == 6
    
    def test_trigger_type_values(self):
        """Test trigger type values."""
        types = [
            TriggerType.EVENTBUS,
            TriggerType.TIMELINE,
            TriggerType.MANUAL,
            TriggerType.SCHEDULED,
            TriggerType.ASSET_EVENT,
            TriggerType.WORKORDER_EVENT,
            TriggerType.DOCUMENT_EVENT,
        ]
        assert len(types) == 7
    
    def test_connector_type_values(self):
        """Test connector type values."""
        types = [
            ConnectorType.HTTP,
            ConnectorType.REST,
            ConnectorType.WEBHOOK,
            ConnectorType.FILE,
            ConnectorType.EMAIL,
        ]
        assert len(types) == 5


class TestWorkflowDefinition:
    """Tests for workflow definition."""
    
    def test_create_workflow_definition(self):
        """Test creating a workflow definition."""
        workflow = WorkflowDefinition(
            id="wf-1",
            name="Test Workflow",
            flow_json={"nodes": []},
            trigger_type=TriggerType.MANUAL
        )
        
        assert workflow.id == "wf-1"
        assert workflow.name == "Test Workflow"
        assert workflow.trigger_type == TriggerType.MANUAL
        assert workflow.is_enabled is True
    
    def test_workflow_to_dict(self):
        """Test workflow serialization."""
        workflow = WorkflowDefinition(
            id="wf-1",
            name="Test",
            flow_json={},
            trigger_type=TriggerType.MANUAL
        )
        
        data = workflow.to_dict()
        assert data["id"] == "wf-1"
        assert data["name"] == "Test"


class TestWorkflowInstance:
    """Tests for workflow instance."""
    
    def test_create_workflow_instance(self):
        """Test creating a workflow instance."""
        instance = WorkflowInstance(
            id="inst-1",
            workflow_id="wf-1",
            name="Test Instance"
        )
        
        assert instance.id == "inst-1"
        assert instance.workflow_id == "wf-1"
        assert instance.status == ExecutionStatus.PENDING
    
    def test_instance_is_running(self):
        """Test instance is_running property."""
        instance = WorkflowInstance(
            id="inst-1",
            workflow_id="wf-1",
            name="Test",
            status=ExecutionStatus.RUNNING
        )
        
        assert instance.is_running is True
        assert instance.is_completed is False
    
    def test_instance_duration(self):
        """Test instance duration calculation."""
        instance = WorkflowInstance(
            id="inst-1",
            workflow_id="wf-1",
            name="Test",
            started_at=datetime(2024, 1, 1, 10, 0, 0),
            completed_at=datetime(2024, 1, 1, 10, 5, 0)
        )
        
        assert instance.duration_seconds == 300.0


class TestFlowManager:
    """Tests for flow manager."""
    
    @pytest.fixture
    def manager(self):
        """Create flow manager."""
        return FlowManager(node_red_url="http://localhost:1880")
    
    def test_create_workflow(self, manager):
        """Test creating a workflow."""
        workflow = manager.create_workflow(
            name="Test Workflow",
            flow_json={"nodes": [{"id": "1", "type": "inject"}]},
            trigger_type=TriggerType.MANUAL
        )
        
        assert workflow is not None
        assert workflow.id is not None
        assert workflow.name == "Test Workflow"
    
    def test_get_workflow(self, manager):
        """Test getting a workflow."""
        workflow = manager.create_workflow(
            name="Test",
            flow_json={},
            trigger_type=TriggerType.MANUAL
        )
        
        retrieved = manager.get_workflow(workflow.id)
        
        assert retrieved is not None
        assert retrieved.id == workflow.id
    
    def test_update_workflow(self, manager):
        """Test updating a workflow."""
        workflow = manager.create_workflow(
            name="Original",
            flow_json={},
            trigger_type=TriggerType.MANUAL
        )
        
        updated = manager.update_workflow(workflow, name="Updated")
        
        assert updated.name == "Updated"
    
    def test_delete_workflow(self, manager):
        """Test deleting a workflow."""
        workflow = manager.create_workflow(
            name="ToDelete",
            flow_json={},
            trigger_type=TriggerType.MANUAL
        )
        workflow_id = workflow.id
        
        result = manager.delete_workflow(workflow_id)
        
        assert result is True
        assert manager.get_workflow(workflow_id) is None
    
    def test_enable_workflow(self, manager):
        """Test enabling a workflow."""
        workflow = manager.create_workflow(
            name="Test",
            flow_json={},
            trigger_type=TriggerType.MANUAL
        )
        workflow.is_enabled = False
        
        enabled = manager.enable_workflow(workflow)
        
        assert enabled.is_enabled is True
    
    def test_disable_workflow(self, manager):
        """Test disabling a workflow."""
        workflow = manager.create_workflow(
            name="Test",
            flow_json={},
            trigger_type=TriggerType.MANUAL
        )
        
        disabled = manager.disable_workflow(workflow)
        
        assert disabled.is_enabled is False
    
    def test_execute_workflow(self, manager):
        """Test executing a workflow."""
        workflow = manager.create_workflow(
            name="Test",
            flow_json={},
            trigger_type=TriggerType.MANUAL
        )
        
        instance = manager.execute_workflow(
            workflow,
            input_data={"test": "data"}
        )
        
        assert instance is not None
        assert instance.workflow_id == workflow.id
        assert instance.status in [ExecutionStatus.RUNNING, ExecutionStatus.PENDING]
    
    def test_complete_workflow(self, manager):
        """Test completing a workflow."""
        workflow = manager.create_workflow(
            name="Test",
            flow_json={},
            trigger_type=TriggerType.MANUAL
        )
        instance = manager.execute_workflow(workflow)
        
        completed = manager.complete_workflow(
            instance,
            output_data={"result": "success"}
        )
        
        assert completed.status == ExecutionStatus.COMPLETED
    
    def test_fail_workflow(self, manager):
        """Test failing a workflow."""
        workflow = manager.create_workflow(
            name="Test",
            flow_json={},
            trigger_type=TriggerType.MANUAL
        )
        instance = manager.execute_workflow(workflow)
        
        failed = manager.fail_workflow(instance, "Test error")
        
        assert failed.status == ExecutionStatus.FAILED
        assert failed.error_message == "Test error"
    
    def test_cancel_workflow(self, manager):
        """Test cancelling a workflow."""
        workflow = manager.create_workflow(
            name="Test",
            flow_json={},
            trigger_type=TriggerType.MANUAL
        )
        instance = manager.execute_workflow(workflow)
        instance.status = ExecutionStatus.RUNNING
        
        cancelled = manager.cancel_workflow(instance)
        
        assert cancelled.status == ExecutionStatus.CANCELLED
    
    def test_retry_workflow(self, manager):
        """Test retrying a workflow."""
        workflow = manager.create_workflow(
            name="Test",
            flow_json={},
            trigger_type=TriggerType.MANUAL
        )
        instance = manager.execute_workflow(workflow)
        instance.status = ExecutionStatus.FAILED
        
        new_instance = manager.retry_workflow(instance)
        
        assert new_instance.retry_count == 1
    
    def test_get_instance_history(self, manager):
        """Test getting instance history."""
        workflow = manager.create_workflow(
            name="Test",
            flow_json={},
            trigger_type=TriggerType.MANUAL
        )
        
        manager.execute_workflow(workflow)
        manager.execute_workflow(workflow)
        
        history = manager.get_instance_history(workflow.id)
        
        assert len(history) == 2
    
    def test_get_workflow_stats(self, manager):
        """Test getting workflow stats."""
        workflow = manager.create_workflow(
            name="Test",
            flow_json={},
            trigger_type=TriggerType.MANUAL
        )
        
        stats = manager.get_workflow_stats(workflow.id)
        
        assert "total_executions" in stats
        assert "running" in stats
        assert "completed" in stats


class TestConnectorRegistry:
    """Tests for connector registry."""
    
    @pytest.fixture
    def registry(self):
        """Create connector registry."""
        return ConnectorRegistry()
    
    def test_register_http_connector(self, registry):
        """Test registering an HTTP connector."""
        connector_id = registry.register_http_connector(
            name="Test HTTP",
            url="https://api.example.com"
        )
        
        assert connector_id is not None
        connector = registry.get_connector(connector_id)
        assert connector is not None
        assert connector.name == "Test HTTP"
    
    def test_register_webhook_connector(self, registry):
        """Test registering a webhook connector."""
        connector_id = registry.register_webhook_connector(
            name="Test Webhook",
            url="https://webhook.example.com"
        )
        
        connector = registry.get_connector(connector_id)
        assert connector.connector_type == ConnectorType.WEBHOOK
    
    def test_get_connectors(self, registry):
        """Test getting connectors."""
        registry.register_http_connector(name="HTTP1", url="http://a.com")
        registry.register_webhook_connector(name="Webhook1", url="http://b.com")
        
        connectors = registry.get_connectors()
        
        assert len(connectors) == 2
    
    def test_delete_connector(self, registry):
        """Test deleting a connector."""
        connector_id = registry.register_http_connector(
            name="ToDelete",
            url="http://test.com"
        )
        
        result = registry.delete_connector(connector_id)
        
        assert result is True
        assert registry.get_connector(connector_id) is None
    
    def test_get_connector_count(self, registry):
        """Test getting connector count."""
        registry.register_http_connector(name="A", url="http://a.com")
        registry.register_http_connector(name="B", url="http://b.com")
        
        count = registry.get_connector_count()
        
        assert count == 2


class TestWorkflowValidator:
    """Tests for workflow validator."""
    
    @pytest.fixture
    def validator(self):
        """Create validator."""
        return WorkflowValidator()
    
    def test_validate_workflow(self, validator):
        """Test validating a workflow."""
        workflow = WorkflowDefinition(
            id="wf-1",
            name="Test",
            flow_json={"nodes": []},
            trigger_type=TriggerType.MANUAL
        )
        
        issues = validator.validate_workflow(workflow)
        
        assert len(issues) == 0
    
    def test_validate_workflow_missing_name(self, validator):
        """Test validation with missing name."""
        workflow = WorkflowDefinition(
            id="wf-1",
            name="",
            flow_json={},
            trigger_type=TriggerType.MANUAL
        )
        
        issues = validator.validate_workflow(workflow)
        
        assert any("name" in i.lower() for i in issues)
    
    def test_validate_workflow_instance(self, validator):
        """Test validating a workflow instance."""
        instance = WorkflowInstance(
            id="inst-1",
            workflow_id="wf-1",
            name="Test"
        )
        
        issues = validator.validate_workflow_instance(instance)
        
        assert len(issues) == 0
    
    def test_validate_trigger_config(self, validator):
        """Test validating trigger config."""
        issues = validator.validate_trigger_config(
            TriggerType.EVENTBUS,
            {"event_type": "test"}
        )
        
        assert len(issues) == 0
    
    def test_validate_trigger_config_missing(self, validator):
        """Test validation with missing trigger config."""
        issues = validator.validate_trigger_config(
            TriggerType.EVENTBUS,
            {}
        )
        
        assert len(issues) > 0
    
    def test_validate_connector_config(self, validator):
        """Test validating connector config."""
        issues = validator.validate_connector_config(
            ConnectorType.HTTP,
            {"url": "https://api.example.com"}
        )
        
        assert len(issues) == 0
    
    def test_check_duplicate_workflow(self, validator):
        """Test duplicate workflow check."""
        existing = {"Test", "Workflow"}
        
        is_duplicate = validator.check_duplicate_workflow("Test", existing)
        
        assert is_duplicate is True
    
    def test_validate_execution_state_transition(self, validator):
        """Test state transition validation."""
        issues = validator.validate_execution_state_transition(
            ExecutionStatus.PENDING,
            ExecutionStatus.RUNNING
        )
        
        assert len(issues) == 0
    
    def test_validate_invalid_state_transition(self, validator):
        """Test invalid state transition."""
        issues = validator.validate_execution_state_transition(
            ExecutionStatus.COMPLETED,
            ExecutionStatus.RUNNING
        )
        
        assert len(issues) > 0
    
    def test_validate_flow_json(self, validator):
        """Test flow JSON validation."""
        issues = validator.validate_flow_json({
            "nodes": [
                {"id": "1", "type": "inject"},
                {"id": "2", "type": "debug"}
            ]
        })
        
        assert len(issues) == 0
    
    def test_validate_workflow_name(self, validator):
        """Test workflow name validation."""
        issues = validator.validate_workflow_name("Valid-Name_123")
        
        assert len(issues) == 0
    
    def test_validate_invalid_workflow_name(self, validator):
        """Test invalid workflow name validation."""
        issues = validator.validate_workflow_name("")
        
        assert len(issues) > 0


class TestNodeREDClient:
    """Tests for Node-RED client."""
    
    @pytest.fixture
    def client(self):
        """Create Node-RED client."""
        return NodeREDClient(base_url="http://localhost:1880")
    
    def test_client_initialization(self, client):
        """Test client initialization."""
        assert client.base_url == "http://localhost:1880"
    
    def test_health_check_returns_false_without_server(self, client):
        """Test health check when server is not available."""
        result = client.health_check()
        
        assert result is False


class TestWorkflowAdapter:
    """Tests for workflow adapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create workflow adapter."""
        return WorkflowAdapter(node_red_url="http://localhost:1880")
    
    def test_adapter_initialization(self, adapter):
        """Test adapter initialization."""
        assert adapter.node_red_client is not None
    
    def test_register_event_workflow(self, adapter):
        """Test registering event workflow."""
        from backend.src.core.events import EventType
        
        adapter.register_event_workflow(
            EventType.ASSET_CREATED,
            "workflow-1"
        )
        
        assert "asset_created" in adapter._workflow_mappings
    
    def test_execute_workflow(self, adapter):
        """Test executing a workflow."""
        result = adapter.execute_workflow(
            "workflow-1",
            {"test": "data"}
        )
        
        # Will fail because server is not available
        assert "status" in result
