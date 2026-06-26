"""
Workflow Validator

Validates workflow definitions, configurations, and executions.
"""

from typing import Dict, List, Optional, Any, Set
from backend.src.integrations.node_red.workflow_types import (
    WorkflowDefinition,
    WorkflowInstance,
    ExecutionStatus,
    TriggerType,
    ConnectorType,
)


class WorkflowValidator:
    """
    Validates workflows and configurations.
    
    Checks:
    - Duplicate workflows
    - Invalid connectors
    - Cyclic dependencies
    - Execution states
    - Configuration integrity
    """
    
    def __init__(self):
        self.issues: List[str] = []
    
    def validate_workflow(self, workflow: WorkflowDefinition) -> List[str]:
        """
        Validate a workflow definition.
        
        Args:
            workflow: Workflow to validate
            
        Returns:
            List of validation issues
        """
        self.issues = []
        
        # Required fields
        if not workflow.id:
            self.issues.append("Workflow ID is required")
        
        if not workflow.name or not workflow.name.strip():
            self.issues.append("Workflow name is required")
        
        if workflow.name and len(workflow.name) > 255:
            self.issues.append("Workflow name must be 255 characters or less")
        
        # Flow JSON validation
        if not workflow.flow_json:
            self.issues.append("Flow JSON is required")
        
        if workflow.flow_json and not isinstance(workflow.flow_json, dict):
            self.issues.append("Flow JSON must be a dictionary")
        
        # Version validation
        if workflow.version < 1:
            self.issues.append("Version must be at least 1")
        
        return self.issues.copy()
    
    def validate_workflow_instance(self, instance: WorkflowInstance) -> List[str]:
        """
        Validate a workflow instance.
        
        Args:
            instance: Instance to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Required fields
        if not instance.id:
            issues.append("Instance ID is required")
        
        if not instance.workflow_id:
            issues.append("Workflow ID is required")
        
        # Status validation
        if not isinstance(instance.status, ExecutionStatus):
            issues.append("Invalid execution status")
        
        # Retry validation
        if instance.retry_count < 0:
            issues.append("Retry count cannot be negative")
        
        if instance.max_retries < 0:
            issues.append("Max retries cannot be negative")
        
        if instance.retry_count > instance.max_retries:
            issues.append("Retry count exceeds max retries")
        
        # Time validation
        if instance.started_at and instance.completed_at:
            if instance.completed_at < instance.started_at:
                issues.append("Completed time cannot be before started time")
        
        return issues
    
    def validate_trigger_config(
        self,
        trigger_type: TriggerType,
        config: Dict[str, Any]
    ) -> List[str]:
        """
        Validate trigger configuration.
        
        Args:
            trigger_type: Trigger type
            config: Trigger configuration
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not isinstance(config, dict):
            issues.append("Trigger config must be a dictionary")
            return issues
        
        # EventBus trigger validation
        if trigger_type == TriggerType.EVENTBUS:
            if "event_type" not in config:
                issues.append("event_type is required for EVENTBUS trigger")
        
        # Scheduled trigger validation
        elif trigger_type == TriggerType.SCHEDULED:
            if "cron" not in config and "interval" not in config:
                issues.append("cron or interval is required for SCHEDULED trigger")
            
            if "interval" in config:
                interval = config["interval"]
                if not isinstance(interval, (int, float)) or interval <= 0:
                    issues.append("interval must be a positive number")
        
        # Timeline trigger validation
        elif trigger_type == TriggerType.TIMELINE:
            if "session_id" not in config and "replay_id" not in config:
                issues.append("session_id or replay_id is required for TIMELINE trigger")
        
        return issues
    
    def validate_connector_config(
        self,
        connector_type: ConnectorType,
        config: Dict[str, Any]
    ) -> List[str]:
        """
        Validate connector configuration.
        
        Args:
            connector_type: Connector type
            config: Connector configuration
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not isinstance(config, dict):
            issues.append("Connector config must be a dictionary")
            return issues
        
        # HTTP/REST/Webhook validation
        if connector_type in [ConnectorType.HTTP, ConnectorType.REST, ConnectorType.WEBHOOK]:
            if "url" not in config:
                issues.append("URL is required for HTTP/REST/Webhook connectors")
            else:
                url = config["url"]
                if not url.startswith(("http://", "https://")):
                    issues.append("URL must start with http:// or https://")
        
        # File connector validation
        elif connector_type == ConnectorType.FILE:
            if "path" not in config:
                issues.append("path is required for FILE connector")
        
        return issues
    
    def check_duplicate_workflow(
        self,
        name: str,
        existing_names: Set[str]
    ) -> bool:
        """
        Check for duplicate workflow name.
        
        Args:
            name: Workflow name
            existing_names: Set of existing workflow names
            
        Returns:
            True if duplicate
        """
        return name in existing_names
    
    def check_cyclic_dependencies(
        self,
        workflow_id: str,
        dependencies: Dict[str, List[str]]
    ) -> bool:
        """
        Check for cyclic dependencies in workflows.
        
        Args:
            workflow_id: Workflow ID
            dependencies: Dependency graph
            
        Returns:
            True if cyclic dependency found
        """
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        
        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in dependencies.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        return has_cycle(workflow_id)
    
    def validate_execution_state_transition(
        self,
        current_status: ExecutionStatus,
        new_status: ExecutionStatus
    ) -> List[str]:
        """
        Validate execution state transition.
        
        Args:
            current_status: Current status
            new_status: New status
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Define valid transitions
        valid_transitions = {
            ExecutionStatus.PENDING: [ExecutionStatus.RUNNING, ExecutionStatus.CANCELLED],
            ExecutionStatus.RUNNING: [
                ExecutionStatus.COMPLETED,
                ExecutionStatus.FAILED,
                ExecutionStatus.CANCELLED,
                ExecutionStatus.RETRYING
            ],
            ExecutionStatus.RETRYING: [
                ExecutionStatus.RUNNING,
                ExecutionStatus.FAILED,
                ExecutionStatus.CANCELLED
            ],
            ExecutionStatus.COMPLETED: [],  # Terminal state
            ExecutionStatus.FAILED: [ExecutionStatus.RETRYING],  # Can retry
            ExecutionStatus.CANCELLED: [],  # Terminal state
        }
        
        if new_status not in valid_transitions.get(current_status, []):
            issues.append(
                f"Invalid state transition: {current_status.value} -> {new_status.value}"
            )
        
        return issues
    
    def validate_flow_json(self, flow_json: Dict[str, Any]) -> List[str]:
        """
        Validate Node-RED flow JSON structure.
        
        Args:
            flow_json: Flow JSON
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not isinstance(flow_json, dict):
            issues.append("Flow JSON must be a dictionary")
            return issues
        
        # Check for nodes
        nodes = flow_json.get("nodes", [])
        if not nodes:
            issues.append("Flow must have at least one node")
        
        if not isinstance(nodes, list):
            issues.append("nodes must be an array")
        
        # Validate individual nodes
        node_ids = set()
        for i, node in enumerate(nodes):
            if not isinstance(node, dict):
                issues.append(f"Node {i} must be a dictionary")
                continue
            
            # Required node fields
            if "id" not in node:
                issues.append(f"Node {i} is missing id")
            else:
                if node["id"] in node_ids:
                    issues.append(f"Duplicate node id: {node['id']}")
                node_ids.add(node["id"])
            
            if "type" not in node:
                issues.append(f"Node {i} is missing type")
        
        return issues
    
    def validate_retry_config(
        self,
        retry_count: int,
        max_retries: int
    ) -> List[str]:
        """
        Validate retry configuration.
        
        Args:
            retry_count: Current retry count
            max_retries: Maximum retries allowed
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if retry_count < 0:
            issues.append("Retry count cannot be negative")
        
        if max_retries < 0:
            issues.append("Max retries cannot be negative")
        
        if max_retries > 10:
            issues.append("Max retries should not exceed 10")
        
        if retry_count > max_retries:
            issues.append("Retry count exceeds max retries")
        
        return issues
    
    def validate_workflow_name(self, name: str) -> List[str]:
        """
        Validate workflow name format.
        
        Args:
            name: Workflow name
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not name or not name.strip():
            issues.append("Workflow name is required")
            return issues
        
        if len(name) > 255:
            issues.append("Workflow name must be 255 characters or less")
        
        # Allow alphanumeric, spaces, hyphens, underscores
        import re
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
            issues.append(
                "Workflow name must contain only alphanumeric characters, "
                "spaces, hyphens, and underscores"
            )
        
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
