"""
Request ID Manager

Manages request ID generation and propagation.
"""

import uuid
from typing import Dict, List, Optional
from datetime import datetime
from .request_context import RequestContextManager


class RequestIDManager:
    """
    Manages request IDs across the application.
    
    Responsibilities:
    - Generate unique request IDs
    - Propagate IDs through the system
    - Track ID lineage
    """
    
    def __init__(self):
        self._id_history: Dict[str, List[str]] = {}  # trace_id -> [request_ids]
        self._parent_child_map: Dict[str, List[str]] = {}  # parent_id -> [child_ids]
    
    def generate_request_id(self) -> str:
        """Generate a unique request ID."""
        return str(uuid.uuid4())
    
    def generate_trace_id(self) -> str:
        """Generate a unique trace ID."""
        return str(uuid.uuid4())
    
    def start_trace(
        self,
        request_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        parent_request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> RequestContextManager:
        """
        Start a new trace.
        
        Args:
            request_id: Optional request ID
            correlation_id: Optional correlation ID
            parent_request_id: Optional parent request ID
            user_id: Optional user ID
            organization_id: Optional organization ID
            
        Returns:
            RequestContextManager with new context
        """
        context = RequestContextManager.create_context(
            request_id=request_id or self.generate_request_id(),
            correlation_id=correlation_id,
            parent_request_id=parent_request_id,
            user_id=user_id,
            organization_id=organization_id
        )
        
        # Track lineage
        trace_id = context.trace_id
        if trace_id not in self._id_history:
            self._id_history[trace_id] = []
        self._id_history[trace_id].append(context.request_id)
        
        # Track parent-child relationship
        if parent_request_id:
            if parent_request_id not in self._parent_child_map:
                self._parent_child_map[parent_request_id] = []
            self._parent_child_map[parent_request_id].append(context.request_id)
        
        return RequestContextManager
    
    def end_trace(self) -> None:
        """End the current trace."""
        RequestContextManager.clear_context()
    
    def get_trace_requests(self, trace_id: str) -> List[str]:
        """Get all request IDs in a trace."""
        return self._id_history.get(trace_id, [])
    
    def get_child_requests(self, parent_id: str) -> List[str]:
        """Get all child request IDs."""
        return self._parent_child_map.get(parent_id, [])
    
    def get_trace_depth(self, trace_id: str) -> int:
        """Get the depth of a trace."""
        requests = self._id_history.get(trace_id, [])
        return len(requests)
