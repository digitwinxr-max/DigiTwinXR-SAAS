"""
Trace Manager

Manages distributed tracing across the application.
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .request_context import RequestContextManager


class TraceSpan:
    """
    Represents a single trace span.
    """
    
    def __init__(
        self,
        name: str,
        trace_id: str,
        span_id: Optional[str] = None,
        parent_span_id: Optional[str] = None
    ):
        self.name = name
        self.trace_id = trace_id
        self.span_id = span_id or str(uuid.uuid4())
        self.parent_span_id = parent_span_id
        self.start_time = datetime.utcnow()
        self.end_time: Optional[datetime] = None
        self.tags: Dict[str, Any] = {}
        self.events: List[Dict] = []
    
    def add_tag(self, key: str, value: Any) -> None:
        """Add a tag to the span."""
        self.tags[key] = value
    
    def add_event(self, name: str, attributes: Optional[Dict] = None) -> None:
        """Add an event to the span."""
        self.events.append({
            "name": name,
            "timestamp": datetime.utcnow().isoformat(),
            "attributes": attributes or {}
        })
    
    def finish(self) -> None:
        """Finish the span."""
        self.end_time = datetime.utcnow()
    
    def get_duration_ms(self) -> int:
        """Get duration in milliseconds."""
        if self.end_time:
            return int((self.end_time - self.start_time).total_seconds() * 1000)
        return 0
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.get_duration_ms(),
            "tags": self.tags,
            "events": self.events
        }


class TraceManager:
    """
    Manages distributed tracing.
    
    Responsibilities:
    - Request traces
    - Event traces
    - Timeline traces
    - Service timing
    - Execution chains
    """
    
    def __init__(self):
        self._active_spans: Dict[str, TraceSpan] = {}
        self._completed_traces: Dict[str, List[TraceSpan]] = {}
        self._max_trace_age = timedelta(hours=24)
    
    def start_span(
        self,
        name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        tags: Optional[Dict] = None
    ) -> TraceSpan:
        """
        Start a new trace span.
        
        Args:
            name: Span name
            trace_id: Optional trace ID
            parent_span_id: Optional parent span ID
            tags: Optional tags
            
        Returns:
            TraceSpan
        """
        trace_id = trace_id or RequestContextManager.get_trace_id() or str(uuid.uuid4())
        
        span = TraceSpan(
            name=name,
            trace_id=trace_id,
            parent_span_id=parent_span_id
        )
        
        if tags:
            for key, value in tags.items():
                span.add_tag(key, value)
        
        self._active_spans[span.span_id] = span
        return span
    
    def end_span(self, span: TraceSpan) -> None:
        """End a trace span."""
        span.finish()
        
        if span.span_id in self._active_spans:
            del self._active_spans[span.span_id]
        
        if span.trace_id not in self._completed_traces:
            self._completed_traces[span.trace_id] = []
        self._completed_traces[span.trace_id].append(span)
        
        # Clean old traces
        self._cleanup_old_traces()
    
    def get_trace(self, trace_id: str) -> List[TraceSpan]:
        """Get all spans for a trace."""
        return self._completed_traces.get(trace_id, [])
    
    def get_active_spans(self) -> List[TraceSpan]:
        """Get all active spans."""
        return list(self._active_spans.values())
    
    def get_trace_tree(self, trace_id: str) -> Optional[Dict]:
        """Get trace as a tree structure."""
        spans = self.get_trace(trace_id)
        if not spans:
            return None
        
        # Build tree
        span_map = {s.span_id: s for s in spans}
        root_spans = [s for s in spans if not s.parent_span_id or s.parent_span_id not in span_map]
        
        def build_tree(span: TraceSpan) -> Dict:
            children = [s for s in spans if s.parent_span_id == span.span_id]
            return {
                **span.to_dict(),
                "children": [build_tree(c) for c in children]
            }
        
        if root_spans:
            return build_tree(root_spans[0])
        return None
    
    def get_trace_duration(self, trace_id: str) -> int:
        """Get total trace duration in milliseconds."""
        spans = self.get_trace(trace_id)
        if not spans:
            return 0
        
        start = min(s.start_time for s in spans)
        end = max(s.end_time for s in spans if s.end_time)
        
        if end:
            return int((end - start).total_seconds() * 1000)
        return 0
    
    def _cleanup_old_traces(self) -> None:
        """Clean up traces older than max age."""
        cutoff = datetime.utcnow() - self._max_trace_age
        to_remove = []
        
        for trace_id, spans in self._completed_traces.items():
            if spans and all(s.end_time and s.end_time < cutoff for s in spans if s.end_time):
                to_remove.append(trace_id)
        
        for trace_id in to_remove:
            del self._completed_traces[trace_id]
    
    def get_trace_count(self) -> int:
        """Get total trace count."""
        return len(self._completed_traces)
