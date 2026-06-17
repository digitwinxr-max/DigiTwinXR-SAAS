"""
Node-RED Client

Client for communicating with Node-RED REST API.
FastAPI remains authoritative for business logic.
Node-RED provides workflow automation and connectors only.
"""

import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class NodeREDClientError(Exception):
    """Node-RED client error."""
    pass


class NodeREDStatus(str, Enum):
    """Node-RED flow status."""
    ENABLED = "enabled"
    DISABLED = "disabled"
    UNKNOWN = "unknown"


class NodeREDClient:
    """
    Client for Node-RED API integration.
    
    Responsibilities:
    - Flow management (get, create, update, delete)
    - Flow enable/disable
    - Flow execution trigger
    - Node information retrieval
    
    Note: All business logic remains in FastAPI.
    Node-RED is used only for workflow orchestration.
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:1880",
        username: str = "admin",
        password: str = ""
    ):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self._client: Optional[httpx.Client] = None
    
    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                auth=(self.username, self.password),
                timeout=30.0
            )
        return self._client
    
    def close(self):
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None
    
    # =========================================================================
    # Flow Management
    # =========================================================================
    
    def get_flows(self) -> List[Dict[str, Any]]:
        """
        Get all flows from Node-RED.
        
        Returns:
            List of flow definitions
        """
        try:
            response = self._get_client().get("/flows")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise NodeREDClientError(f"Failed to get flows: {e}")
    
    def get_flow(self, flow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific flow by ID.
        
        Args:
            flow_id: Flow ID
            
        Returns:
            Flow definition or None
        """
        try:
            flows = self.get_flows()
            for flow in flows:
                if flow.get("id") == flow_id:
                    return flow
            return None
        except httpx.HTTPError as e:
            raise NodeREDClientError(f"Failed to get flow {flow_id}: {e}")
    
    def create_flow(self, flow_def: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new flow in Node-RED.
        
        Args:
            flow_def: Flow definition
            
        Returns:
            Created flow
        """
        try:
            response = self._get_client().post(
                "/flows",
                json=flow_def
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise NodeREDClientError(f"Failed to create flow: {e}")
    
    def update_flow(self, flow_id: str, flow_def: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing flow.
        
        Args:
            flow_id: Flow ID
            flow_def: Updated flow definition
            
        Returns:
            Updated flow
        """
        try:
            response = self._get_client().put(
                f"/flows/{flow_id}",
                json=flow_def
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise NodeREDClientError(f"Failed to update flow {flow_id}: {e}")
    
    def delete_flow(self, flow_id: str) -> bool:
        """
        Delete a flow.
        
        Args:
            flow_id: Flow ID
            
        Returns:
            True if deleted
        """
        try:
            response = self._get_client().delete(f"/flows/{flow_id}")
            response.raise_for_status()
            return True
        except httpx.HTTPError as e:
            raise NodeREDClientError(f"Failed to delete flow {flow_id}: {e}")
    
    # =========================================================================
    # Flow Status
    # =========================================================================
    
    def enable_flow(self, flow_id: str) -> bool:
        """
        Enable a flow.
        
        Args:
            flow_id: Flow ID
            
        Returns:
            True if enabled
        """
        try:
            flow = self.get_flow(flow_id)
            if not flow:
                raise NodeREDClientError(f"Flow {flow_id} not found")
            
            flow["enabled"] = True
            self.update_flow(flow_id, flow)
            return True
        except httpx.HTTPError as e:
            raise NodeREDClientError(f"Failed to enable flow {flow_id}: {e}")
    
    def disable_flow(self, flow_id: str) -> bool:
        """
        Disable a flow.
        
        Args:
            flow_id: Flow ID
            
        Returns:
            True if disabled
        """
        try:
            flow = self.get_flow(flow_id)
            if not flow:
                raise NodeREDClientError(f"Flow {flow_id} not found")
            
            flow["enabled"] = False
            self.update_flow(flow_id, flow)
            return True
        except httpx.HTTPError as e:
            raise NodeREDClientError(f"Failed to disable flow {flow_id}: {e}")
    
    def get_flow_status(self, flow_id: str) -> NodeREDStatus:
        """
        Get flow status.
        
        Args:
            flow_id: Flow ID
            
        Returns:
            Flow status
        """
        try:
            flow = self.get_flow(flow_id)
            if not flow:
                return NodeREDStatus.UNKNOWN
            
            return NodeREDStatus.ENABLED if flow.get("enabled", False) else NodeREDStatus.DISABLED
        except httpx.HTTPError:
            return NodeREDStatus.UNKNOWN
    
    # =========================================================================
    # Flow Execution
    # =========================================================================
    
    def trigger_flow(self, flow_id: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Trigger a flow execution.
        
        Args:
            flow_id: Flow ID
            payload: Optional input payload
            
        Returns:
            Execution result
        """
        try:
            # Node-RED can be triggered via HTTP injection
            response = self._get_client().post(
                f"/inject/{flow_id}",
                json=payload or {}
            )
            response.raise_for_status()
            return {"status": "triggered", "flow_id": flow_id}
        except httpx.HTTPError as e:
            raise NodeREDClientError(f"Failed to trigger flow {flow_id}: {e}")
    
    # =========================================================================
    # Connector Endpoints
    # =========================================================================
    
    def test_http_connector(self, url: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Test an HTTP connector.
        
        Args:
            url: Endpoint URL
            method: HTTP method
            data: Optional request data
            
        Returns:
            Response data
        """
        try:
            client = self._get_client()
            if method == "GET":
                response = client.get(url)
            elif method == "POST":
                response = client.post(url, json=data)
            elif method == "PUT":
                response = client.put(url, json=data)
            elif method == "DELETE":
                response = client.delete(url)
            else:
                raise NodeREDClientError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except httpx.HTTPError as e:
            return {"status": "error", "error": str(e)}
    
    def test_webhook(self, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test a webhook.
        
        Args:
            url: Webhook URL
            data: Webhook payload
            
        Returns:
            Result
        """
        try:
            response = self._get_client().post(url, json=data)
            response.raise_for_status()
            return {"status": "success", "code": response.status_code}
        except httpx.HTTPError as e:
            return {"status": "error", "error": str(e)}
    
    # =========================================================================
    # Node Information
    # =========================================================================
    
    def get_available_nodes(self) -> List[Dict[str, Any]]:
        """
        Get available Node-RED nodes.
        
        Returns:
            List of available nodes
        """
        try:
            response = self._get_client().get("/nodes")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise NodeREDClientError(f"Failed to get nodes: {e}")
    
    def get_node_info(self, node_type: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific node type.
        
        Args:
            node_type: Node type
            
        Returns:
            Node information or None
        """
        try:
            response = self._get_client().get(f"/nodes/{node_type}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            return None
    
    # =========================================================================
    # Health Check
    # =========================================================================
    
    def health_check(self) -> bool:
        """
        Check Node-RED health.
        
        Returns:
            True if healthy
        """
        try:
            response = self._get_client().get("/status")
            return response.status_code == 200
        except httpx.HTTPError:
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get Node-RED instance information.
        
        Returns:
            Instance information
        """
        try:
            response = self._get_client().get("/")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise NodeREDClientError(f"Failed to get Node-RED info: {e}")


class NodeREDFlowBuilder:
    """
    Helper class for building Node-RED flow definitions.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.nodes: List[Dict[str, Any]] = []
        self.connections: List[Dict[str, Any]] = []
    
    def add_inject_node(
        self,
        node_id: str,
        name: str,
        payload: Optional[Dict] = None
    ) -> "NodeREDFlowBuilder":
        """Add an inject node."""
        self.nodes.append({
            "id": node_id,
            "type": "inject",
            "name": name,
            "payload": payload or {},
            "repeat": "",
            "wires": []
        })
        return self
    
    def add_http_node(
        self,
        node_id: str,
        name: str,
        url: str,
        method: str = "GET"
    ) -> "NodeREDFlowBuilder":
        """Add an HTTP request node."""
        self.nodes.append({
            "id": node_id,
            "type": "http request",
            "name": name,
            "url": url,
            "method": method.upper(),
            "wires": []
        })
        return self
    
    def add_function_node(
        self,
        node_id: str,
        name: str,
        func: str
    ) -> "NodeREDFlowBuilder":
        """Add a function node."""
        self.nodes.append({
            "id": node_id,
            "type": "function",
            "name": name,
            "func": func,
            "wires": []
        })
        return self
    
    def add_debug_node(
        self,
        node_id: str,
        name: str = "debug"
    ) -> "NodeREDFlowBuilder":
        """Add a debug node."""
        self.nodes.append({
            "id": node_id,
            "type": "debug",
            "name": name,
            "wires": []
        })
        return self
    
    def add_webhook_node(
        self,
        node_id: str,
        name: str,
        url: str
    ) -> "NodeREDFlowBuilder":
        """Add a webhook (http-in) node."""
        self.nodes.append({
            "id": node_id,
            "type": "http in",
            "name": name,
            "url": url,
            "method": "post",
            "wires": []
        })
        return self
    
    def add_response_node(self, node_id: str) -> "NodeREDFlowBuilder":
        """Add an http response node."""
        self.nodes.append({
            "id": node_id,
            "type": "http response",
            "wires": []
        })
        return self
    
    def connect(self, source_id: str, target_id: str, port: int = 0) -> "NodeREDFlowBuilder":
        """Add a connection between nodes."""
        # Find source node and add target to its wires
        for node in self.nodes:
            if node["id"] == source_id:
                if "wires" not in node:
                    node["wires"] = []
                if len(node["wires"]) <= port:
                    node["wires"].append([])
                node["wires"][port].append(target_id)
                break
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build the flow definition."""
        return {
            "label": self.name,
            "nodes": self.nodes
        }
