"""
Error Registry

Standardizes error codes and severity.
"""

import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ErrorSeverity(str, Enum):
    """Error severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ErrorDefinition:
    """Standardized error definition."""
    error_code: str
    error_name: str
    severity: ErrorSeverity
    category: str
    description: str = ""
    recovery_suggestions: List[str] = field(default_factory=list)
    trace_link_template: str = ""
    http_status_code: int = 500
    is_retryable: bool = False


class ErrorRegistry:
    """
    Standardizes error codes and severity.
    
    Provides:
    - Error codes
    - Severity levels
    - Categories
    - Recovery suggestions
    - Trace links
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Initialize error registry with standard errors."""
        self._errors: Dict[str, ErrorDefinition] = {}
        self._error_history: List[Dict] = []
        
        # Register standard errors
        self._register_standard_errors()
    
    def _register_standard_errors(self) -> None:
        """Register standard error definitions."""
        errors = [
            ErrorDefinition(
                error_code="ERR001",
                error_name="ValidationError",
                severity=ErrorSeverity.WARNING,
                category="validation",
                description="Input validation failed",
                recovery_suggestions=["Check input format", "Review required fields"],
                http_status_code=400
            ),
            ErrorDefinition(
                error_code="ERR002",
                error_name="AuthenticationError",
                severity=ErrorSeverity.ERROR,
                category="security",
                description="Authentication failed",
                recovery_suggestions=["Check credentials", "Refresh token"],
                http_status_code=401
            ),
            ErrorDefinition(
                error_code="ERR003",
                error_name="AuthorizationError",
                severity=ErrorSeverity.ERROR,
                category="security",
                description="Insufficient permissions",
                recovery_suggestions=["Check role assignments", "Contact administrator"],
                http_status_code=403
            ),
            ErrorDefinition(
                error_code="ERR004",
                error_name="NotFoundError",
                severity=ErrorSeverity.INFO,
                category="resource",
                description="Resource not found",
                recovery_suggestions=["Verify resource ID", "Check if resource exists"],
                http_status_code=404
            ),
            ErrorDefinition(
                error_code="ERR005",
                error_name="DatabaseError",
                severity=ErrorSeverity.CRITICAL,
                category="infrastructure",
                description="Database operation failed",
                recovery_suggestions=["Retry operation", "Check database connection"],
                http_status_code=500,
                is_retryable=True
            ),
            ErrorDefinition(
                error_code="ERR006",
                error_name="EventBusError",
                severity=ErrorSeverity.ERROR,
                category="infrastructure",
                description="EventBus operation failed",
                recovery_suggestions=["Retry operation", "Check EventBus status"],
                http_status_code=500,
                is_retryable=True
            ),
            ErrorDefinition(
                error_code="ERR007",
                error_name="ExternalServiceError",
                severity=ErrorSeverity.ERROR,
                category="external",
                description="External service unavailable",
                recovery_suggestions=["Retry later", "Check service status"],
                http_status_code=503,
                is_retryable=True
            ),
            ErrorDefinition(
                error_code="ERR008",
                error_name="RateLimitError",
                severity=ErrorSeverity.WARNING,
                category="rate_limiting",
                description="Rate limit exceeded",
                recovery_suggestions=["Wait before retry", "Implement backoff"],
                http_status_code=429
            ),
            ErrorDefinition(
                error_code="ERR009",
                error_name="ConflictError",
                severity=ErrorSeverity.WARNING,
                category="resource",
                description="Resource conflict",
                recovery_suggestions=["Check for duplicates", "Use optimistic locking"],
                http_status_code=409
            ),
            ErrorDefinition(
                error_code="ERR010",
                error_name="TimeoutError",
                severity=ErrorSeverity.ERROR,
                category="infrastructure",
                description="Operation timed out",
                recovery_suggestions=["Retry with longer timeout", "Check service status"],
                http_status_code=504,
                is_retryable=True
            ),
        ]
        
        for error in errors:
            self._errors[error.error_code] = error
    
    def register_error(
        self,
        error_code: str,
        error_name: str,
        severity: ErrorSeverity,
        category: str,
        description: str = "",
        recovery_suggestions: Optional[List[str]] = None,
        http_status_code: int = 500,
        is_retryable: bool = False
    ) -> None:
        """Register a custom error."""
        error = ErrorDefinition(
            error_code=error_code,
            error_name=error_name,
            severity=severity,
            category=category,
            description=description,
            recovery_suggestions=recovery_suggestions or [],
            http_status_code=http_status_code,
            is_retryable=is_retryable
        )
        self._errors[error_code] = error
    
    def get_error(self, error_code: str) -> Optional[ErrorDefinition]:
        """Get error definition by code."""
        return self._errors.get(error_code)
    
    def get_errors_by_category(self, category: str) -> List[ErrorDefinition]:
        """Get all errors in a category."""
        return [e for e in self._errors.values() if e.category == category]
    
    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[ErrorDefinition]:
        """Get all errors of a severity level."""
        return [e for e in self._errors.values() if e.severity == severity]
    
    def record_error(
        self,
        error_code: str,
        trace_id: Optional[str] = None,
        request_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> None:
        """Record an error occurrence."""
        error_def = self.get_error(error_code)
        self._error_history.append({
            "error_code": error_code,
            "error_name": error_def.error_name if error_def else "Unknown",
            "severity": error_def.severity.value if error_def else "unknown",
            "trace_id": trace_id,
            "request_id": request_id,
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_error_history(
        self,
        limit: int = 100,
        severity: Optional[ErrorSeverity] = None
    ) -> List[Dict]:
        """Get error history."""
        history = self._error_history
        
        if severity:
            history = [h for h in history if h.get("severity") == severity.value]
        
        return sorted(history, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def get_error_count(self) -> int:
        """Get total registered error count."""
        return len(self._errors)
