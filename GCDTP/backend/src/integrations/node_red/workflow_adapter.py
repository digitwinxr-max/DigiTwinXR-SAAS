"""
Workflow Adapter

Bridge between FastAPI (authoritative) and Node-RED (orchestration).
Handles:
- EventBus integration
- Timeline Engine integration
- Work Orders
- Documents
- Security
- Simulation events

No direct database ownership - FastAPI manages all business logic.
"""

import uuid
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from backend.src.integrations.node_red.node_red_client import NodeREDClient
from backend.src.core.events import get_event_bus, EventType


class WorkflowAdapter:
    """
    Adapter for connecting FastAPI services to Node-RED workflows.
    
    Responsibilities:
    - Bridge EventBus events to Node-RED
    - Bridge Timeline events to Node-RED
    - Handle work order triggers
    - Handle document events
    - Route workflow results back to FastAPI
    
    Note: All business logic remains in FastAPI services.
    """
    
    def __init__(self, node_red_url: str = "http://localhost:1880"):
        self.node_red_client = NodeREDClient(base_url=node_red_url)
        self.event_bus = get_event_bus()
        self._handlers: Dict[str, Callable] = {}
        self._workflow_mappings: Dict[str, str] = {}  # event_type -> workflow_id
    
    def close(self):
        """Close the adapter and cleanup resources."""
        self.node_red_client.close()
    
    # =========================================================================
    # EventBus Integration
    # =========================================================================
    
    def register_event_workflow(
        self,
        event_type: EventType,
        workflow_id: str
    ) -> None:
        """
        Register a workflow to handle an EventBus event.
        
        Args:
            event_type: Event type to listen for
            workflow_id: Node-RED workflow ID to trigger
        """
        self._workflow_mappings[event_type.value] = workflow_id
    
    def trigger_workflow_from_event(
        self,
        event_type: EventType,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Trigger a workflow from an EventBus event.
        
        Args:
            event_type: Event type
            event_data: Event payload
            
        Returns:
            Trigger result
        """
        workflow_id = self._workflow_mappings.get(event_type.value)
        
        if not workflow_id:
            return {"status": "no_workflow", "event_type": event_type.value}
        
        # Build payload for Node-RED
        payload = {
            "event_type": event_type.value,
            "data": event_data,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "fastapi_eventbus"
        }
        
        try:
            result = self.node_red_client.trigger_flow(workflow_id, payload)
            return {"status": "triggered", "result": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def setup_event_listeners(self) -> None:
        """Setup EventBus listeners for all registered workflows."""
        for event_type_str, workflow_id in self._workflow_mappings.items():
            try:
                event_type = EventType(event_type_str)
                self.event_bus.subscribe(
                    event_type,
                    lambda data, wt=workflow_id: self._handle_event(wt, data)
                )
            except ValueError:
                pass  # Skip invalid event types
    
    def _handle_event(self, workflow_id: str, data: Dict[str, Any]) -> None:
        """Internal handler for events."""
        try:
            self.node_red_client.trigger_flow(workflow_id, {
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception:
            pass  # Log error in production
    
    # =========================================================================
    # Timeline Engine Integration
    # =========================================================================
    
    def trigger_timeline_replay(
        self,
        workflow_id: str,
        replay_session_id: str,
        timeline_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Trigger a workflow for timeline replay.
        
        Args:
            workflow_id: Node-RED workflow ID
            replay_session_id: Timeline replay session
            timeline_data: Replay data
            
        Returns:
            Trigger result
        """
        payload = {
            "type": "timeline_replay",
            "session_id": replay_session_id,
            "data": timeline_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self.node_red_client.trigger_flow(workflow_id, payload)
    
    def handle_timeline_snapshot(
        self,
        workflow_id: str,
        snapshot_id: str
    ) -> Dict[str, Any]:
        """
        Handle timeline snapshot with a workflow.
        
        Args:
            workflow_id: Node-RED workflow ID
            snapshot_id: Snapshot ID
            
        Returns:
            Result
        """
        payload = {
            "type": "timeline_snapshot",
            "snapshot_id": snapshot_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self.node_red_client.trigger_flow(workflow_id, payload)
    
    # =========================================================================
    # Work Order Integration
    # =========================================================================
    
    def trigger_work_order_workflow(
        self,
        workflow_id: str,
        work_order_id: str,
        action: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Trigger a workflow for work order events.
        
        Args:
            workflow_id: Node-RED workflow ID
            work_order_id: Work order ID
            action: Action type (created, updated, completed, etc.)
            context: Additional context
            
        Returns:
            Trigger result
        """
        payload = {
            "type": "work_order",
            "action": action,
            "work_order_id": work_order_id,
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self.node_red_client.trigger_flow(workflow_id, payload)
    
    def handle_inspection_result(
        self,
        workflow_id: str,
        inspection_id: str,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle inspection result with a workflow.
        
        Args:
            workflow_id: Node-RED workflow ID
            inspection_id: Inspection ID
            result: Inspection result
            
        Returns:
            Result
        """
        payload = {
            "type": "inspection_result",
            "inspection_id": inspection_id,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self.node_red_client.trigger_flow(workflow_id, payload)
    
    # =========================================================================
    # Document Integration
    # =========================================================================
    
    def trigger_document_workflow(
        self,
        workflow_id: str,
        document_id: str,
        action: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Trigger a workflow for document events.
        
        Args:
            workflow_id: Node-RED workflow ID
            document_id: Document ID
            action: Action type
            metadata: Document metadata
            
        Returns:
            Trigger result
        """
        payload = {
            "type": "document",
            "action": action,
            "document_id": document_id,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self.node_red_client.trigger_flow(workflow_id, payload)
    
    # =========================================================================
    # Security Integration
    # =========================================================================
    
    def trigger_user_workflow(
        self,
        workflow_id: str,
        user_id: str,
        action: str
    ) -> Dict[str, Any]:
        """
        Trigger a workflow for user events.
        
        Args:
            workflow_id: Node-RED workflow ID
            user_id: User ID
            action: Action type
            
        Returns:
            Trigger result
        """
        payload = {
            "type": "user_event",
            "action": action,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self.node_red_client.trigger_flow(workflow_id, payload)
    
    # =========================================================================
    # Simulation Integration
    # =========================================================================
    
    def trigger_simulation_workflow(
        self,
        workflow_id: str,
        simulation_id: str,
        simulation_type: str,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Trigger a workflow for simulation results.
        
        Args:
            workflow_id: Node-RED workflow ID
            simulation_id: Simulation ID
            simulation_type: Type of simulation
            results: Simulation results
            
        Returns:
            Trigger result
        """
        payload = {
            "type": "simulation_result",
            "simulation_id": simulation_id,
            "simulation_type": simulation_type,
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self.node_red_client.trigger_flow(workflow_id, payload)
    
    def handle_simulation_failure(
        self,
        workflow_id: str,
        simulation_id: str,
        failure_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle simulation failure with a workflow.
        
        Args:
            workflow_id: Node-RED workflow ID
            simulation_id: Simulation ID
            failure_data: Failure information
            
        Returns:
            Result
        """
        payload = {
            "type": "simulation_failure",
            "simulation_id": simulation_id,
            "failure": failure_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self.node_red_client.trigger_flow(workflow_id, payload)
    
    # =========================================================================
    # Generic Workflow Execution
    # =========================================================================
    
    def execute_workflow(
        self,
        workflow_id: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a workflow with custom payload.
        
        Args:
            workflow_id: Node-RED workflow ID
            payload: Custom payload
            
        Returns:
            Execution result
        """
        return self.node_red_client.trigger_flow(workflow_id, payload)
    
    def execute_workflow_by_name(
        self,
        workflow_name: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a workflow by name.
        
        Args:
            workflow_name: Workflow name
            payload: Custom payload
            
        Returns:
            Execution result
        """
        # Find workflow by name
        flows = self.node_red_client.get_flows()
        for flow in flows:
            if flow.get("label", "").lower() == workflow_name.lower():
                return self.node_red_client.trigger_flow(flow["id"], payload)
        
        return {"status": "not_found", "workflow_name": workflow_name}
    
    # =========================================================================
    # Connector Helpers
    # =========================================================================
    
    def test_connector(
        self,
        connector_type: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Test a connector configuration.
        
        Args:
            connector_type: Type of connector
            config: Connector configuration
            
        Returns:
            Test result
        """
        if connector_type == "http":
            return self.node_red_client.test_http_connector(
                config.get("url", ""),
                config.get("method", "GET"),
                config.get("data")
            )
        elif connector_type == "webhook":
            return self.node_red_client.test_webhook(
                config.get("url", ""),
                config.get("data", {})
            )
        else:
            return {"status": "unsupported", "type": connector_type}
