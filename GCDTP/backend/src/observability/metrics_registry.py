"""
Metrics Registry

Centralized metrics collection.
"""

import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field


@dataclass
class Metric:
    """Represents a single metric."""
    name: str
    value: float
    unit: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


class MetricsRegistry:
    """
    Centralized metrics registry.
    
    Tracks:
    - Request count
    - Response times
    - Error count
    - Event throughput
    - Timeline throughput
    - Graph queries
    - Ontology queries
    - Simulation count
    - Work orders
    - Documents
    - MQTT messages
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Initialize metrics storage."""
        self._counters: Dict[str, float] = {}
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = {}
        self._timers: Dict[str, datetime] = {}
        self._metrics_history: List[Metric] = []
        self._max_history_size = 10000
    
    # =========================================================================
    # Counter Operations
    # =========================================================================
    
    def increment_counter(
        self,
        name: str,
        value: float = 1.0,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Increment a counter metric."""
        key = self._make_key(name, tags)
        self._counters[key] = self._counters.get(key, 0) + value
        self._record_metric(name, self._counters[key], "count", tags)
    
    def get_counter(self, name: str, tags: Optional[Dict[str, str]] = None) -> float:
        """Get counter value."""
        key = self._make_key(name, tags)
        return self._counters.get(key, 0)
    
    # =========================================================================
    # Gauge Operations
    # =========================================================================
    
    def set_gauge(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Set a gauge metric."""
        key = self._make_key(name, tags)
        self._gauges[key] = value
        self._record_metric(name, value, "gauge", tags)
    
    def get_gauge(self, name: str, tags: Optional[Dict[str, str]] = None) -> float:
        """Get gauge value."""
        key = self._make_key(name, tags)
        return self._gauges.get(key, 0)
    
    # =========================================================================
    # Histogram Operations
    # =========================================================================
    
    def record_histogram(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a histogram value."""
        key = self._make_key(name, tags)
        if key not in self._histograms:
            self._histograms[key] = []
        self._histograms[key].append(value)
        self._record_metric(name, value, "histogram", tags)
    
    def get_histogram_stats(
        self,
        name: str,
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, float]:
        """Get histogram statistics."""
        key = self._make_key(name, tags)
        values = self._histograms.get(key, [])
        
        if not values:
            return {"count": 0, "min": 0, "max": 0, "avg": 0, "p50": 0, "p95": 0, "p99": 0}
        
        sorted_values = sorted(values)
        count = len(sorted_values)
        
        return {
            "count": count,
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "avg": sum(sorted_values) / count,
            "p50": sorted_values[int(count * 0.5)],
            "p95": sorted_values[int(count * 0.95)] if count > 1 else sorted_values[0],
            "p99": sorted_values[int(count * 0.99)] if count > 1 else sorted_values[0],
        }
    
    # =========================================================================
    # Timer Operations
    # =========================================================================
    
    def start_timer(self, name: str, tags: Optional[Dict[str, str]] = None) -> str:
        """Start a timer."""
        key = self._make_key(name, tags)
        self._timers[key] = datetime.utcnow()
        return key
    
    def stop_timer(
        self,
        name: str,
        tags: Optional[Dict[str, str]] = None,
        record: bool = True
    ) -> Optional[float]:
        """Stop a timer and record duration."""
        key = self._make_key(name, tags)
        start_time = self._timers.get(key)
        
        if not start_time:
            return None
        
        duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        if record:
            self.record_histogram(f"{name}_duration_ms", duration_ms, tags)
            self.increment_counter(f"{name}_count", 1, tags)
        
        del self._timers[key]
        return duration_ms
    
    # =========================================================================
    # Predefined Metrics
    # =========================================================================
    
    def record_request(self, duration_ms: float, status_code: int) -> None:
        """Record an HTTP request."""
        self.increment_counter("requests_total")
        self.record_histogram("request_duration_ms", duration_ms)
        self.increment_counter(f"requests_by_status_{status_code}")
    
    def record_event(self, event_type: str) -> None:
        """Record an event."""
        self.increment_counter("events_total")
        self.increment_counter(f"events_by_type_{event_type}")
    
    def record_error(self, error_type: str) -> None:
        """Record an error."""
        self.increment_counter("errors_total")
        self.increment_counter(f"errors_by_type_{error_type}")
    
    def record_timeline_event(self) -> None:
        """Record a timeline event."""
        self.increment_counter("timeline_events_total")
    
    def record_graph_query(self, duration_ms: float) -> None:
        """Record a graph query."""
        self.increment_counter("graph_queries_total")
        self.record_histogram("graph_query_duration_ms", duration_ms)
    
    def record_ontology_query(self, duration_ms: float) -> None:
        """Record an ontology query."""
        self.increment_counter("ontology_queries_total")
        self.record_histogram("ontology_query_duration_ms", duration_ms)
    
    def record_mqtt_message(self) -> None:
        """Record an MQTT message."""
        self.increment_counter("mqtt_messages_total")
    
    def record_simulation(self) -> None:
        """Record a simulation."""
        self.increment_counter("simulations_total")
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def _make_key(self, name: str, tags: Optional[Dict[str, str]]) -> str:
        """Create a metric key from name and tags."""
        if not tags:
            return name
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}[{tag_str}]"
    
    def _record_metric(
        self,
        name: str,
        value: float,
        unit: str,
        tags: Optional[Dict[str, str]]
    ) -> None:
        """Record a metric to history."""
        metric = Metric(name=name, value=value, unit=unit, tags=tags or {})
        self._metrics_history.append(metric)
        
        # Trim history if needed
        if len(self._metrics_history) > self._max_history_size:
            self._metrics_history = self._metrics_history[-self._max_history_size:]
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all current metrics."""
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {
                k: self.get_histogram_stats(k.split("[")[0], self._parse_tags(k))
                for k in self._histograms.keys()
            }
        }
    
    def _parse_tags(self, key: str) -> Optional[Dict[str, str]]:
        """Parse tags from metric key."""
        if "[" not in key:
            return None
        tag_str = key.split("[")[1].rstrip("]")
        return dict(t.split("=") for t in tag_str.split(","))
    
    def reset(self) -> None:
        """Reset all metrics."""
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
        self._timers.clear()
        self._metrics_history.clear()
