"""
Memory Profiler

Tracks memory usage and identifies hotspots.
"""

import gc
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from collections import Counter


@dataclass
class MemorySnapshot:
    """Memory usage snapshot."""
    timestamp: datetime
    heap_used_mb: float
    heap_available_mb: float
    object_counts: Dict[str, int]
    gc_runs: Dict[str, int]
    largest_objects: List[Dict]


class MemoryProfiler:
    """
    Tracks memory usage.
    
    Monitors:
    - Heap usage
    - Object counts
    - Memory hotspots
    - Growth trends
    """
    
    def __init__(self):
        self._snapshots: List[MemorySnapshot] = []
        self._max_snapshots = 100
        self._tracked_types: Counter = Counter()
    
    def take_snapshot(self) -> MemorySnapshot:
        """Take a memory snapshot."""
        import psutil
        import sys
        
        process = psutil.Process()
        memory = process.memory_info()
        
        # Get object counts
        object_counts = self._count_objects()
        
        # Get GC stats
        gc_stats = {
            "gen0": gc.get_count()[0],
            "gen1": gc.get_count()[1],
            "gen2": gc.get_count()[2],
        }
        
        # Find largest objects
        largest = self._find_largest_objects()
        
        snapshot = MemorySnapshot(
            timestamp=datetime.utcnow(),
            heap_used_mb=memory.rss / (1024 * 1024),
            heap_available_mb=psutil.virtual_memory().available / (1024 * 1024),
            object_counts=object_counts,
            gc_runs=gc_stats,
            largest_objects=largest
        )
        
        self._snapshots.append(snapshot)
        
        # Trim old snapshots
        if len(self._snapshots) > self._max_snapshots:
            self._snapshots = self._snapshots[-self._max_snapshots:]
        
        return snapshot
    
    def _count_objects(self) -> Dict[str, int]:
        """Count objects by type."""
        counts = Counter()
        
        for obj in gc.get_objects():
            obj_type = type(obj).__name__
            counts[obj_type] += 1
        
        return dict(counts.most_common(20))
    
    def _find_largest_objects(self) -> List[Dict]:
        """Find largest objects in memory."""
        largest = []
        
        for obj in gc.get_objects():
            try:
                size = sys.getsizeof(obj)
                if size > 10000:  # Objects larger than 10KB
                    largest.append({
                        "type": type(obj).__name__,
                        "size_kb": size / 1024
                    })
            except:
                pass
        
        largest.sort(key=lambda x: x["size_kb"], reverse=True)
        return largest[:10]
    
    def get_heap_usage(self) -> Dict[str, float]:
        """Get current heap usage."""
        import psutil
        
        process = psutil.Process()
        memory = process.memory_info()
        total_memory = psutil.virtual_memory()
        
        return {
            "heap_used_mb": memory.rss / (1024 * 1024),
            "heap_available_mb": total_memory.available / (1024 * 1024),
            "heap_percent": memory.rss / total_memory.total * 100
        }
    
    def get_object_count(self, type_name: str) -> int:
        """Get count of objects by type."""
        return self._tracked_types.get(type_name, 0)
    
    def track_type(self, obj_type: str) -> int:
        """Track a specific object type."""
        count = sum(1 for obj in gc.get_objects() if type(obj).__name__ == obj_type)
        self._tracked_types[obj_type] = count
        return count
    
    def get_growth_trend(self, metric: str = "heap_used_mb") -> List[float]:
        """Get growth trend for a metric."""
        if not self._snapshots:
            return []
        
        if metric == "heap_used_mb":
            return [s.heap_used_mb for s in self._snapshots]
        return []
    
    def get_memory_hotspots(self) -> List[Dict[str, Any]]:
        """Get memory hotspots."""
        if not self._snapshots:
            return []
        
        latest = self._snapshots[-1]
        
        hotspots = []
        for obj_type, count in latest.object_counts.items():
            hotspots.append({
                "type": obj_type,
                "count": count
            })
        
        return sorted(hotspots, key=lambda x: x["count"], reverse=True)[:10]
    
    def get_gc_info(self) -> Dict[str, Any]:
        """Get garbage collector information."""
        return {
            "collections": {
                "gen0": gc.get_count()[0],
                "gen1": gc.get_count()[1],
                "gen2": gc.get_count()[2]
            },
            "thresholds": gc.get_threshold(),
            "tracked_objects": len(gc.get_objects())
        }
    
    def force_gc(self) -> Dict[str, int]:
        """Force garbage collection."""
        before = len(gc.get_objects())
        collected = gc.collect()
        after = len(gc.get_objects())
        
        return {
            "collected": collected,
            "before": before,
            "after": after,
            "freed": before - after
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get memory summary."""
        heap = self.get_heap_usage()
        gc_info = self.get_gc_info()
        hotspots = self.get_memory_hotspots()
        
        return {
            "heap_usage_mb": heap["heap_used_mb"],
            "heap_available_mb": heap["heap_available_mb"],
            "heap_percent": heap["heap_percent"],
            "tracked_objects": gc_info["tracked_objects"],
            "top_hotspots": hotspots[:5],
            "snapshots_collected": len(self._snapshots)
        }
