"""
Observability Module

Provides observability and diagnostics capabilities:
- Request tracing
- Health monitoring
- Metrics collection
- Diagnostics
- Request IDs
- Error standardization

Components:
- Request Context Manager
- Request ID Manager
- Trace Manager
- Metrics Registry
- Health Check Engine
- Diagnostics Engine
- Error Registry
- Performance Monitor
- Logging Manager
"""

from .request_context import RequestContext, RequestContextManager
from .request_id_manager import RequestIDManager
from .trace_manager import TraceManager, TraceSpan
from .metrics_registry import MetricsRegistry, Metric
from .health_check_engine import HealthCheckEngine, HealthStatus, HealthCheckResult
from .diagnostics_engine import DiagnosticsEngine, DiagnosticEvent
from .error_registry import ErrorRegistry, ErrorDefinition, ErrorSeverity
from .performance_monitor import PerformanceMonitor, PerformanceSnapshot
from .logging_manager import LoggingManager, LogLevel
from .observability_validator import ObservabilityValidator


__all__ = [
    # Request Context
    "RequestContext",
    "RequestContextManager",
    # Request ID
    "RequestIDManager",
    # Tracing
    "TraceManager",
    "TraceSpan",
    # Metrics
    "MetricsRegistry",
    "Metric",
    # Health
    "HealthCheckEngine",
    "HealthStatus",
    "HealthCheckResult",
    # Diagnostics
    "DiagnosticsEngine",
    "DiagnosticEvent",
    # Errors
    "ErrorRegistry",
    "ErrorDefinition",
    "ErrorSeverity",
    # Performance
    "PerformanceMonitor",
    "PerformanceSnapshot",
    # Logging
    "LoggingManager",
    "LogLevel",
    # Validation
    "ObservabilityValidator",
]
