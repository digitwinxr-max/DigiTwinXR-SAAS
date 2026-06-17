"""
Performance Monitor

Monitors performance metrics.
"""

import psutil
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PerformanceSnapshot:
    """A snapshot of performance metrics."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    active_sessions: int
    queue_sizes: Dict[str, int]
    latency_ms: float
    throughput: float
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "memory_used_mb": self.memory_used_mb,
            "memory_available_mb": self.memory_available_mb,
            "active_sessions": self.active_sessions,
            "queue_sizes": self.queue_sizes,
            "latency_ms": self.latency_ms,
            "throughput": self.throughput,
        }


class PerformanceMonitor:
    """
    Monitors performance metrics.
    
    Measures:
    - CPU usage
    - Memory usage
    - Cache usage
    - Queue sizes
    - Active sessions
    - Latency
    - Throughput
    """
    
    def __init__(self):
        self._snapshots: List[PerformanceSnapshot] = []
        self._max_snapshots = 1000
        self._process = psutil.Process()
    
    def take_snapshot(
        self,
        active_sessions: int = 0,
        queue_sizes: Optional[Dict[str, int]] = None,
        latency_ms: float = 0.0,
        throughput: float = 0.0
    ) -> PerformanceSnapshot:
        """Take a performance snapshot."""
        memory = self._process.memory_info()
        
        snapshot = PerformanceSnapshot(
            timestamp=datetime.utcnow(),
            cpu_percent=self._process.cpu_percent(),
            memory_percent=self._process.memory_percent(),
            memory_used_mb=memory.rss / (1024 * 1024),
            memory_available_mb=psutil.virtual_memory().available / (1024 * 1024),
            active_sessions=active_sessions,
            queue_sizes=queue_sizes or {},
            latency_ms=latency_ms,
            throughput=throughput
        )
        
        self._snapshots.append(snapshot)
        
        # Trim old snapshots
        if len(self._snapshots) > self._max_snapshots:
            self._snapshots = self._snapshots[-self._max_snapshots:]
        
        return snapshot
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage."""
        return self._process.cpu_percent()
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage."""
        memory = self._process.memory_info()
        total_memory = psutil.virtual_memory()
        
        return {
            "rss_mb": memory.rss / (1024 * 1024),
            "vms_mb": memory.vms / (1024 * 1024),
            "percent": self._process.memory_percent(),
            "available_mb": total_memory.available / (1024 * 1024),
            "total_mb": total_memory.total / (1024 * 1024),
        }
    
    def get_queue_sizes(self) -> Dict[str, int]:
        """Get queue sizes."""
        # In production, would get actual queue sizes
        return {}
    
    def get_active_sessions(self) -> int:
        """Get active session count."""
        # In production, would count actual sessions
        return 0
    
    def get_average_latency(self, window_seconds: int = 60) -> float:
        """Get average latency over a time window."""
        cutoff = datetime.utcnow().timestamp() - window_seconds
        recent = [s for s in self._snapshots if s.timestamp.timestamp() >= cutoff]
        
        if not recent:
            return 0.0
        
        return sum(s.latency_ms for s in recent) / len(recent)
    
    def get_throughput(self, window_seconds: int = 60) -> float:
        """Get throughput over a time window."""
        cutoff = datetime.utcnow().timestamp() - window_seconds
        recent = [s for s in self._snapshots if s.timestamp.timestamp() >= cutoff]
        
        if not recent:
            return 0.0
        
        return sum(s.throughput for s in recent) / len(recent)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        memory = self.get_memory_usage()
        
        return {
            "cpu_percent": self.get_cpu_usage(),
            "memory": memory,
            "queue_sizes": self.get_queue_sizes(),
            "active_sessions": self.get_active_sessions(),
            "average_latency_ms": self.get_average_latency(),
            "throughput_per_second": self.get_throughput(),
            "snapshots_collected": len(self._snapshots)
        }
