"""
Performance Analyzer

Measures and analyzes performance metrics.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class PerformanceMetrics:
    """Performance metrics."""
    latency_ms: float
    throughput: float
    cache_hit_ratio: float
    query_time_ms: float
    event_throughput: float
    timeline_replay_speed: float
    simulation_speed: float


class PerformanceAnalyzer:
    """
    Measures performance metrics.
    
    Measures:
    - Latency
    - Throughput
    - Cache hit ratio
    - Query time
    - Event throughput
    - Timeline replay speed
    - Simulation speed
    """
    
    def __init__(self):
        self._metrics: Dict[str, List[float]] = {
            "latency": [],
            "throughput": [],
            "cache_hits": [],
            "cache_misses": [],
            "query_time": [],
            "event_throughput": [],
            "timeline_replay": [],
            "simulation_speed": []
        }
        self._max_history = 1000
    
    def record_latency(self, latency_ms: float) -> None:
        """Record latency."""
        self._metrics["latency"].append(latency_ms)
        self._trim("latency")
    
    def record_throughput(self, throughput: float) -> None:
        """Record throughput."""
        self._metrics["throughput"].append(throughput)
        self._trim("throughput")
    
    def record_cache_hit(self) -> None:
        """Record cache hit."""
        self._metrics["cache_hits"].append(1)
        self._trim("cache_hits")
    
    def record_cache_miss(self) -> None:
        """Record cache miss."""
        self._metrics["cache_misses"].append(1)
        self._trim("cache_misses")
    
    def record_query_time(self, time_ms: float) -> None:
        """Record query time."""
        self._metrics["query_time"].append(time_ms)
        self._trim("query_time")
    
    def record_event_throughput(self, events_per_second: float) -> None:
        """Record event throughput."""
        self._metrics["event_throughput"].append(events_per_second)
        self._trim("event_throughput")
    
    def record_timeline_replay_speed(self, speed_factor: float) -> None:
        """Record timeline replay speed."""
        self._metrics["timeline_replay"].append(speed_factor)
        self._trim("timeline_replay")
    
    def record_simulation_speed(self, speed_factor: float) -> None:
        """Record simulation speed."""
        self._metrics["simulation_speed"].append(speed_factor)
        self._trim("simulation_speed")
    
    def _trim(self, key: str) -> None:
        """Trim metrics history."""
        if len(self._metrics[key]) > self._max_history:
            self._metrics[key] = self._metrics[key][-self._max_history:]
    
    def get_latency_stats(self) -> Dict[str, float]:
        """Get latency statistics."""
        latencies = self._metrics["latency"]
        if not latencies:
            return {"min": 0, "max": 0, "avg": 0, "p50": 0, "p95": 0, "p99": 0}
        
        sorted_latencies = sorted(latencies)
        count = len(sorted_latencies)
        
        return {
            "min": min(latencies),
            "max": max(latencies),
            "avg": sum(latencies) / count,
            "p50": sorted_latencies[int(count * 0.5)],
            "p95": sorted_latencies[int(count * 0.95)] if count > 1 else sorted_latencies[0],
            "p99": sorted_latencies[int(count * 0.99)] if count > 1 else sorted_latencies[0],
        }
    
    def get_throughput_stats(self) -> Dict[str, float]:
        """Get throughput statistics."""
        throughputs = self._metrics["throughput"]
        if not throughputs:
            return {"min": 0, "max": 0, "avg": 0}
        
        return {
            "min": min(throughputs),
            "max": max(throughputs),
            "avg": sum(throughputs) / len(throughputs)
        }
    
    def get_cache_hit_ratio(self) -> float:
        """Get cache hit ratio."""
        hits = sum(self._metrics["cache_hits"])
        misses = sum(self._metrics["cache_misses"])
        total = hits + misses
        
        if total == 0:
            return 0.0
        
        return hits / total
    
    def get_query_time_stats(self) -> Dict[str, float]:
        """Get query time statistics."""
        times = self._metrics["query_time"]
        if not times:
            return {"min": 0, "max": 0, "avg": 0}
        
        return {
            "min": min(times),
            "max": max(times),
            "avg": sum(times) / len(times)
        }
    
    def get_event_throughput_stats(self) -> Dict[str, float]:
        """Get event throughput statistics."""
        throughputs = self._metrics["event_throughput"]
        if not throughputs:
            return {"min": 0, "max": 0, "avg": 0}
        
        return {
            "min": min(throughputs),
            "max": max(throughputs),
            "avg": sum(throughputs) / len(throughputs)
        }
    
    def get_timeline_replay_stats(self) -> Dict[str, float]:
        """Get timeline replay statistics."""
        speeds = self._metrics["timeline_replay"]
        if not speeds:
            return {"min": 0, "max": 0, "avg": 0}
        
        return {
            "min": min(speeds),
            "max": max(speeds),
            "avg": sum(speeds) / len(speeds)
        }
    
    def get_simulation_speed_stats(self) -> Dict[str, float]:
        """Get simulation speed statistics."""
        speeds = self._metrics["simulation_speed"]
        if not speeds:
            return {"min": 0, "max": 0, "avg": 0}
        
        return {
            "min": min(speeds),
            "max": max(speeds),
            "avg": sum(speeds) / len(speeds)
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all performance metrics."""
        return {
            "latency": self.get_latency_stats(),
            "throughput": self.get_throughput_stats(),
            "cache_hit_ratio": self.get_cache_hit_ratio(),
            "query_time": self.get_query_time_stats(),
            "event_throughput": self.get_event_throughput_stats(),
            "timeline_replay": self.get_timeline_replay_stats(),
            "simulation_speed": self.get_simulation_speed_stats()
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        latency = self.get_latency_stats()
        cache_ratio = self.get_cache_hit_ratio()
        
        return {
            "latency_avg_ms": latency.get("avg", 0),
            "latency_p95_ms": latency.get("p95", 0),
            "cache_hit_ratio": cache_ratio,
            "throughput_avg": self.get_throughput_stats().get("avg", 0),
            "query_time_avg_ms": self.get_query_time_stats().get("avg", 0),
            "event_throughput_avg": self.get_event_throughput_stats().get("avg", 0),
            "recorded_samples": len(self._metrics["latency"])
        }
