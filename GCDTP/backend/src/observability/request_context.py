"""
Request Context Manager

Manages request context including request IDs and correlation IDs.
"""

import uuid
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime


# Context variables for request-scoped data
_request_id: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
_correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)
_trace_id: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)
_parent_request_id: ContextVar[Optional[str]] = ContextVar("parent_request_id", default=None)
_user_id: ContextVar[Optional[str]] = ContextVar("user_id", default=None)
_organization_id: ContextVar[Optional[str]] = ContextVar("organization_id", default=None)


@dataclass
class RequestContext:
    """
    Request context containing tracing information.
    """
    request_id: str
    trace_id: str
    correlation_id: Optional[str] = None
    parent_request_id: Optional[str] = None
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "trace_id": self.trace_id,
            "correlation_id": self.correlation_id,
            "parent_request_id": self.parent_request_id,
            "user_id": self.user_id,
            "organization_id": self.organization_id,
            "metadata": self.metadata,
        }
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers for downstream propagation."""
        headers = {
            "X-Request-ID": self.request_id,
            "X-Trace-ID": self.trace_id,
        }
        if self.correlation_id:
            headers["X-Correlation-ID"] = self.correlation_id
        if self.parent_request_id:
            headers["X-Parent-Request-ID"] = self.parent_request_id
        return headers


class RequestContextManager:
    """
    Manages request context across the application.
    """
    
    _current_context: Optional[RequestContext] = None
    
    @classmethod
    def get_context(cls) -> Optional[RequestContext]:
        """Get current request context."""
        return cls._current_context
    
    @classmethod
    def set_context(cls, context: RequestContext) -> None:
        """Set current request context."""
        cls._current_context = context
        _request_id.set(context.request_id)
        _trace_id.set(context.trace_id)
        if context.correlation_id:
            _correlation_id.set(context.correlation_id)
        if context.parent_request_id:
            _parent_request_id.set(context.parent_request_id)
        if context.user_id:
            _user_id.set(context.user_id)
        if context.organization_id:
            _organization_id.set(context.organization_id)
    
    @classmethod
    def clear_context(cls) -> None:
        """Clear current request context."""
        cls._current_context = None
        _request_id.set(None)
        _trace_id.set(None)
        _correlation_id.set(None)
        _parent_request_id.set(None)
        _user_id.set(None)
        _organization_id.set(None)
    
    @classmethod
    def get_request_id(cls) -> Optional[str]:
        """Get current request ID."""
        return _request_id.get()
    
    @classmethod
    def get_trace_id(cls) -> Optional[str]:
        """Get current trace ID."""
        return _trace_id.get()
    
    @classmethod
    def get_correlation_id(cls) -> Optional[str]:
        """Get current correlation ID."""
        return _correlation_id.get()
    
    @classmethod
    def get_user_id(cls) -> Optional[str]:
        """Get current user ID."""
        return _user_id.get()
    
    @classmethod
    def get_organization_id(cls) -> Optional[str]:
        """Get current organization ID."""
        return _organization_id.get()
    
    @classmethod
    def create_context(
        cls,
        request_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        parent_request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> RequestContext:
        """
        Create a new request context.
        
        Args:
            request_id: Optional request ID (generated if not provided)
            correlation_id: Optional correlation ID
            parent_request_id: Optional parent request ID
            user_id: Optional user ID
            organization_id: Optional organization ID
            metadata: Optional metadata
            
        Returns:
            New RequestContext
        """
        trace_id = _trace_id.get() or str(uuid.uuid4())
        request_id = request_id or str(uuid.uuid4())
        
        context = RequestContext(
            request_id=request_id,
            trace_id=trace_id,
            correlation_id=correlation_id or _correlation_id.get(),
            parent_request_id=parent_request_id or _parent_request_id.get(),
            user_id=user_id,
            organization_id=organization_id,
            metadata=metadata or {}
        )
        
        cls.set_context(context)
        return context
