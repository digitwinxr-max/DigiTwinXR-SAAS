"""
Observability Validator

Validates observability components.
"""

from typing import Dict, List, Set, Optional
from .request_context import RequestContext


class ObservabilityValidator:
    """
    Validates observability components.
    
    Checks:
    - Request ID propagation
    - Trace integrity
    - Metrics consistency
    - Health check coverage
    - Error registry completeness
    """
    
    def __init__(self):
        self.issues: List[str] = []
    
    def validate_request_context(self, context: RequestContext) -> List[str]:
        """Validate a request context."""
        issues = []
        
        if not context.request_id:
            issues.append("Request ID is required")
        
        if not context.trace_id:
            issues.append("Trace ID is required")
        
        if context.request_id == context.trace_id:
            issues.append("Request ID and Trace ID should be different")
        
        return issues
    
    def validate_trace_spans(self, spans: List[Dict]) -> List[str]:
        """Validate trace spans."""
        issues = []
        
        if not spans:
            issues.append("No spans in trace")
            return issues
        
        span_ids = set()
        parent_ids = set()
        
        for span in spans:
            if "span_id" not in span:
                issues.append("Span missing span_id")
            
            if "span_id" in span:
                span_ids.add(span["span_id"])
            
            if "parent_span_id" in span and span["parent_span_id"]:
                parent_ids.add(span["parent_span_id"])
                if span["parent_span_id"] not in span_ids:
                    issues.append(f"Orphan span: {span['span_id']}")
        
        return issues
    
    def validate_metrics(self, metrics: Dict) -> List[str]:
        """Validate metrics dictionary."""
        issues = []
        
        required_keys = ["counters", "gauges", "histograms"]
        for key in required_keys:
            if key not in metrics:
                issues.append(f"Missing metrics key: {key}")
        
        # Validate counters
        if "counters" in metrics:
            for name, value in metrics["counters"].items():
                if value < 0:
                    issues.append(f"Counter {name} has negative value")
        
        # Validate gauges
        if "gauges" in metrics:
            for name, value in metrics["gauges"].items():
                if value < 0:
                    issues.append(f"Gauge {name} has negative value")
        
        return issues
    
    def validate_health_check_result(self, result: Dict) -> List[str]:
        """Validate a health check result."""
        issues = []
        
        required_keys = ["component", "check_name", "status"]
        for key in required_keys:
            if key not in result:
                issues.append(f"Health check missing: {key}")
        
        valid_statuses = ["healthy", "degraded", "unhealthy", "unknown"]
        if "status" in result and result["status"] not in valid_statuses:
            issues.append(f"Invalid health status: {result['status']}")
        
        if "response_time_ms" in result and result["response_time_ms"] < 0:
            issues.append("Response time cannot be negative")
        
        return issues
    
    def validate_error_definition(self, error_def: Dict) -> List[str]:
        """Validate an error definition."""
        issues = []
        
        required_keys = ["error_code", "error_name", "severity", "category"]
        for key in required_keys:
            if key not in error_def:
                issues.append(f"Error definition missing: {key}")
        
        valid_severities = ["debug", "info", "warning", "error", "critical"]
        if "severity" in error_def and error_def["severity"] not in valid_severities:
            issues.append(f"Invalid severity: {error_def['severity']}")
        
        if "http_status_code" in error_def:
            code = error_def["http_status_code"]
            if not isinstance(code, int) or code < 100 or code > 599:
                issues.append(f"Invalid HTTP status code: {code}")
        
        return issues
    
    def get_validation_summary(self) -> Dict:
        """Get validation summary."""
        return {
            "issues": self.issues,
            "issue_count": len(self.issues),
            "has_critical": any("required" in i.lower() for i in self.issues),
        }
