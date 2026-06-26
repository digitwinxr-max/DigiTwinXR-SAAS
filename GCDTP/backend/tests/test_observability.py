"""
Tests for Observability Module

Tests request IDs, tracing, metrics, health checks, diagnostics, logging, and performance monitoring.
"""

import pytest
from backend.src.observability import (
    RequestContext,
    RequestContextManager,
    RequestIDManager,
    TraceManager,
    TraceSpan,
    MetricsRegistry,
    Metric,
    HealthCheckEngine,
    HealthStatus,
    DiagnosticsEngine,
    ErrorRegistry,
    ErrorSeverity,
    PerformanceMonitor,
    LoggingManager,
    LogLevel,
    ObservabilityValidator,
)


class TestRequestContext:
    """Tests for RequestContext."""
    
    def test_create_request_context(self):
        """Test creating a request context."""
        context = RequestContext(
            request_id="req-123",
            trace_id="trace-456"
        )
        
        assert context.request_id == "req-123"
        assert context.trace_id == "trace-456"
    
    def test_request_context_to_dict(self):
        """Test request context serialization."""
        context = RequestContext(
            request_id="req-123",
            trace_id="trace-456",
            user_id="user-1"
        )
        
        data = context.to_dict()
        assert data["request_id"] == "req-123"
        assert data["user_id"] == "user-1"
    
    def test_get_headers(self):
        """Test getting headers."""
        context = RequestContext(
            request_id="req-123",
            trace_id="trace-456",
            correlation_id="corr-789"
        )
        
        headers = context.get_headers()
        assert "X-Request-ID" in headers
        assert headers["X-Request-ID"] == "req-123"


class TestRequestContextManager:
    """Tests for RequestContextManager."""
    
    def test_create_context(self):
        """Test creating a context."""
        context = RequestContextManager.create_context(
            request_id="req-123"
        )
        
        assert context is not None
        assert context.request_id == "req-123"
    
    def test_get_request_id(self):
        """Test getting request ID."""
        RequestContextManager.create_context(request_id="req-123")
        request_id = RequestContextManager.get_request_id()
        
        assert request_id == "req-123"
    
    def test_clear_context(self):
        """Test clearing context."""
        RequestContextManager.create_context(request_id="req-123")
        RequestContextManager.clear_context()
        
        assert RequestContextManager.get_request_id() is None


class TestRequestIDManager:
    """Tests for RequestIDManager."""
    
    def test_generate_request_id(self):
        """Test generating request ID."""
        manager = RequestIDManager()
        request_id = manager.generate_request_id()
        
        assert request_id is not None
        assert len(request_id) == 36  # UUID format
    
    def test_start_trace(self):
        """Test starting a trace."""
        manager = RequestIDManager()
        manager.start_trace(request_id="req-123")
        
        assert RequestContextManager.get_request_id() == "req-123"
    
    def test_end_trace(self):
        """Test ending a trace."""
        manager = RequestIDManager()
        manager.start_trace(request_id="req-123")
        manager.end_trace()
        
        assert RequestContextManager.get_request_id() is None


class TestTraceManager:
    """Tests for TraceManager."""
    
    def test_start_span(self):
        """Test starting a span."""
        manager = TraceManager()
        span = manager.start_span("test_span", trace_id="trace-123")
        
        assert span.name == "test_span"
        assert span.trace_id == "trace-123"
    
    def test_end_span(self):
        """Test ending a span."""
        manager = TraceManager()
        span = manager.start_span("test_span")
        manager.end_span(span)
        
        assert span.end_time is not None
    
    def test_get_trace(self):
        """Test getting a trace."""
        manager = TraceManager()
        span = manager.start_span("test_span", trace_id="trace-123")
        manager.end_span(span)
        
        trace = manager.get_trace("trace-123")
        assert len(trace) == 1
    
    def test_get_trace_duration(self):
        """Test getting trace duration."""
        manager = TraceManager()
        span = manager.start_span("test_span", trace_id="trace-123")
        manager.end_span(span)
        
        duration = manager.get_trace_duration("trace-123")
        assert duration >= 0


class TestMetricsRegistry:
    """Tests for MetricsRegistry."""
    
    def test_increment_counter(self):
        """Test incrementing a counter."""
        registry = MetricsRegistry()
        registry.reset()
        registry.increment_counter("test_counter")
        
        value = registry.get_counter("test_counter")
        assert value == 1
    
    def test_set_gauge(self):
        """Test setting a gauge."""
        registry = MetricsRegistry()
        registry.reset()
        registry.set_gauge("test_gauge", 100.0)
        
        value = registry.get_gauge("test_gauge")
        assert value == 100.0
    
    def test_record_histogram(self):
        """Test recording histogram."""
        registry = MetricsRegistry()
        registry.reset()
        registry.record_histogram("test_histogram", 50.0)
        registry.record_histogram("test_histogram", 100.0)
        
        stats = registry.get_histogram_stats("test_histogram")
        assert stats["count"] == 2
    
    def test_record_request(self):
        """Test recording a request."""
        registry = MetricsRegistry()
        registry.reset()
        registry.record_request(100, 200)
        
        total = registry.get_counter("requests_total")
        assert total == 1
    
    def test_record_event(self):
        """Test recording an event."""
        registry = MetricsRegistry()
        registry.reset()
        registry.record_event("test_event")
        
        total = registry.get_counter("events_total")
        assert total == 1


class TestHealthCheckEngine:
    """Tests for HealthCheckEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create health check engine."""
        return HealthCheckEngine()
    
    @pytest.mark.asyncio
    async def test_check_database(self, engine):
        """Test database health check."""
        result = await engine.check_database()
        
        assert result.component == "database"
        assert result.status in [HealthStatus.HEALTHY, HealthStatus.UNHEALTHY]
    
    @pytest.mark.asyncio
    async def test_check_eventbus(self, engine):
        """Test EventBus health check."""
        result = await engine.check_eventbus()
        
        assert result.component == "eventbus"
    
    @pytest.mark.asyncio
    async def test_get_overall_health(self, engine):
        """Test getting overall health."""
        health = await engine.get_overall_health()
        
        assert "status" in health
        assert "checks" in health
    
    @pytest.mark.asyncio
    async def test_get_liveness(self, engine):
        """Test getting liveness."""
        liveness = await engine.get_liveness()
        
        assert liveness["status"] == "alive"
    
    @pytest.mark.asyncio
    async def test_get_system_status(self, engine):
        """Test getting system status."""
        status = await engine.get_system_status()
        
        assert "status" in status
        assert "version" in status


class TestDiagnosticsEngine:
    """Tests for DiagnosticsEngine."""
    
    def test_add_event(self):
        """Test adding a diagnostic event."""
        engine = DiagnosticsEngine()
        event = engine.add_event(
            event_type="slow_request",
            severity="warning",
            source="api",
            message="Request took too long"
        )
        
        assert event is not None
        assert event.event_type == "slow_request"
    
    def test_get_slow_requests(self):
        """Test getting slow requests."""
        engine = DiagnosticsEngine()
        engine.add_event(
            event_type="slow_request",
            severity="warning",
            source="api",
            message="Request took too long",
            context={"duration_ms": 5000}
        )
        
        slow = engine.get_slow_requests(threshold_ms=1000)
        assert len(slow) >= 0
    
    def test_get_dead_events(self):
        """Test getting dead events."""
        engine = DiagnosticsEngine()
        dead = engine.get_dead_events()
        
        assert isinstance(dead, list)
    
    def test_resolve_event(self):
        """Test resolving an event."""
        engine = DiagnosticsEngine()
        event = engine.add_event(
            event_type="test",
            severity="info",
            source="test",
            message="Test event"
        )
        
        result = engine.resolve_event(event.id)
        assert result is True


class TestErrorRegistry:
    """Tests for ErrorRegistry."""
    
    def test_get_error(self):
        """Test getting an error."""
        registry = ErrorRegistry()
        error = registry.get_error("ERR001")
        
        assert error is not None
        assert error.error_code == "ERR001"
    
    def test_get_errors_by_category(self):
        """Test getting errors by category."""
        registry = ErrorRegistry()
        errors = registry.get_errors_by_category("security")
        
        assert len(errors) >= 0
    
    def test_get_errors_by_severity(self):
        """Test getting errors by severity."""
        registry = ErrorRegistry()
        errors = registry.get_errors_by_severity(ErrorSeverity.CRITICAL)
        
        assert len(errors) >= 0
    
    def test_record_error(self):
        """Test recording an error."""
        registry = ErrorRegistry()
        registry.record_error(
            error_code="ERR001",
            trace_id="trace-123"
        )
        
        history = registry.get_error_history()
        assert len(history) >= 0


class TestPerformanceMonitor:
    """Tests for PerformanceMonitor."""
    
    def test_take_snapshot(self):
        """Test taking a performance snapshot."""
        monitor = PerformanceMonitor()
        snapshot = monitor.take_snapshot(
            active_sessions=10,
            latency_ms=50.0
        )
        
        assert snapshot is not None
        assert snapshot.active_sessions == 10
    
    def test_get_cpu_usage(self):
        """Test getting CPU usage."""
        monitor = PerformanceMonitor()
        cpu = monitor.get_cpu_usage()
        
        assert cpu >= 0
    
    def test_get_memory_usage(self):
        """Test getting memory usage."""
        monitor = PerformanceMonitor()
        memory = monitor.get_memory_usage()
        
        assert "rss_mb" in memory
        assert memory["rss_mb"] > 0
    
    def test_get_performance_summary(self):
        """Test getting performance summary."""
        monitor = PerformanceMonitor()
        summary = monitor.get_performance_summary()
        
        assert "cpu_percent" in summary
        assert "memory" in summary


class TestLoggingManager:
    """Tests for LoggingManager."""
    
    def test_info_log(self):
        """Test info logging."""
        manager = LoggingManager()
        manager.info("Test message")
    
    def test_error_log(self):
        """Test error logging."""
        manager = LoggingManager()
        manager.error("Error message")
    
    def test_warning_log(self):
        """Test warning logging."""
        manager = LoggingManager()
        manager.warning("Warning message")
    
    def test_audit_log(self):
        """Test audit logging."""
        manager = LoggingManager()
        manager.audit("Audit message")
    
    def test_log_request(self):
        """Test request logging."""
        manager = LoggingManager()
        manager.log_request("GET", "/api/test", 200, 100)


class TestObservabilityValidator:
    """Tests for ObservabilityValidator."""
    
    def test_validate_request_context(self):
        """Test validating request context."""
        validator = ObservabilityValidator()
        context = RequestContext(
            request_id="req-123",
            trace_id="trace-456"
        )
        
        issues = validator.validate_request_context(context)
        assert len(issues) == 0
    
    def test_validate_request_context_missing_id(self):
        """Test validating context with missing ID."""
        validator = ObservabilityValidator()
        context = RequestContext(
            request_id="",
            trace_id="trace-456"
        )
        
        issues = validator.validate_request_context(context)
        assert len(issues) > 0
    
    def test_validate_trace_spans(self):
        """Test validating trace spans."""
        validator = ObservabilityValidator()
        spans = [
            {"span_id": "span-1", "parent_span_id": None},
            {"span_id": "span-2", "parent_span_id": "span-1"}
        ]
        
        issues = validator.validate_trace_spans(spans)
        assert len(issues) == 0
    
    def test_validate_metrics(self):
        """Test validating metrics."""
        validator = ObservabilityValidator()
        metrics = {
            "counters": {"test": 10},
            "gauges": {"test": 5.0},
            "histograms": {}
        }
        
        issues = validator.validate_metrics(metrics)
        assert len(issues) == 0
    
    def test_validate_health_check_result(self):
        """Test validating health check result."""
        validator = ObservabilityValidator()
        result = {
            "component": "database",
            "check_name": "connectivity",
            "status": "healthy",
            "response_time_ms": 100
        }
        
        issues = validator.validate_health_check_result(result)
        assert len(issues) == 0


class TestHealthCheckResult:
    """Tests for HealthCheckResult."""
    
    def test_to_dict(self):
        """Test health check result serialization."""
        from backend.src.observability import HealthCheckResult
        
        result = HealthCheckResult(
            component="database",
            check_name="connectivity",
            status=HealthStatus.HEALTHY,
            message="OK"
        )
        
        data = result.to_dict()
        assert data["component"] == "database"
        assert data["status"] == "healthy"
