"""
Connection Pool Manager

Manages connection pools for external services.
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class PoolStatus(str, Enum):
    """Connection pool status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class PoolStats:
    """Connection pool statistics."""
    pool_name: str
    total_connections: int
    active_connections: int
    idle_connections: int
    waiting_requests: int
    max_connections: int
    avg_wait_time_ms: int
    status: PoolStatus
    recorded_at: datetime


class ConnectionPoolManager:
    """
    Manages connection pools.
    
    Monitors:
    - PostgreSQL pools
    - Neo4j pools
    - GeoServer sessions
    - EMQX connections
    """
    
    def __init__(self):
        self._pools: Dict[str, Dict[str, Any]] = {}
        self._stats_history: Dict[str, List[PoolStats]] = {}
        self._max_history = 100
        self._initialize_pools()
    
    def _initialize_pools(self) -> None:
        """Initialize connection pools."""
        pools = [
            ("postgresql", 20),
            ("neo4j", 10),
            ("geoserver", 5),
            ("emqx", 50),
        ]
        
        for name, max_conn in pools:
            self._pools[name] = {
                "max_connections": max_conn,
                "total_connections": 0,
                "active_connections": 0,
                "idle_connections": max_conn,
                "waiting_requests": 0,
                "avg_wait_time_ms": 0,
                "created_at": datetime.utcnow()
            }
            self._stats_history[name] = []
    
    def record_connection(
        self,
        pool_name: str,
        connection_type: str  # "acquire" or "release"
    ) -> None:
        """Record a connection acquisition/release."""
        if pool_name not in self._pools:
            return
        
        pool = self._pools[pool_name]
        
        if connection_type == "acquire":
            pool["active_connections"] += 1
            pool["idle_connections"] -= 1
        else:
            pool["active_connections"] -= 1
            pool["idle_connections"] += 1
    
    def record_wait(self, pool_name: str, wait_time_ms: int) -> None:
        """Record wait time for a connection."""
        if pool_name not in self._pools:
            return
        
        pool = self._pools[pool_name]
        current_avg = pool["avg_wait_time_ms"]
        count = pool["total_connections"]
        
        # Rolling average
        pool["avg_wait_time_ms"] = int(
            (current_avg * count + wait_time_ms) / (count + 1)
        )
    
    def get_pool_stats(self, pool_name: str) -> Optional[PoolStats]:
        """Get current pool statistics."""
        if pool_name not in self._pools:
            return None
        
        pool = self._pools[pool_name]
        
        return PoolStats(
            pool_name=pool_name,
            total_connections=pool["total_connections"],
            active_connections=pool["active_connections"],
            idle_connections=pool["idle_connections"],
            waiting_requests=pool["waiting_requests"],
            max_connections=pool["max_connections"],
            avg_wait_time_ms=pool["avg_wait_time_ms"],
            status=self._determine_status(pool),
            recorded_at=datetime.utcnow()
        )
    
    def _determine_status(self, pool: Dict) -> PoolStatus:
        """Determine pool status."""
        utilization = pool["active_connections"] / pool["max_connections"]
        wait_time = pool["avg_wait_time_ms"]
        
        if utilization > 0.9 or wait_time > 5000:
            return PoolStatus.UNHEALTHY
        elif utilization > 0.7 or wait_time > 1000:
            return PoolStatus.DEGRADED
        return PoolStatus.HEALTHY
    
    def get_all_pool_stats(self) -> List[PoolStats]:
        """Get statistics for all pools."""
        return [
            self.get_pool_stats(name)
            for name in self._pools.keys()
        ]
    
    def get_pool_health(self, pool_name: str) -> Dict[str, Any]:
        """Get pool health information."""
        if pool_name not in self._pools:
            return {"status": "unknown"}
        
        pool = self._pools[pool_name]
        stats = self.get_pool_stats(pool_name)
        
        utilization = pool["active_connections"] / pool["max_connections"]
        
        return {
            "pool_name": pool_name,
            "status": stats.status.value if stats else "unknown",
            "utilization_percent": round(utilization * 100, 2),
            "active_connections": pool["active_connections"],
            "max_connections": pool["max_connections"],
            "avg_wait_time_ms": pool["avg_wait_time_ms"]
        }
    
    def record_stats_snapshot(self, pool_name: str) -> None:
        """Record a statistics snapshot."""
        stats = self.get_pool_stats(pool_name)
        if stats:
            self._stats_history[pool_name].append(stats)
            
            # Trim history
            if len(self._stats_history[pool_name]) > self._max_history:
                self._stats_history[pool_name] = self._stats_history[pool_name][-self._max_history:]
    
    def get_pool_history(
        self,
        pool_name: str,
        limit: int = 50
    ) -> List[PoolStats]:
        """Get pool statistics history."""
        history = self._stats_history.get(pool_name, [])
        return history[-limit:]
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall connection pool health."""
        all_stats = self.get_all_pool_stats()
        
        healthy = sum(1 for s in all_stats if s and s.status == PoolStatus.HEALTHY)
        degraded = sum(1 for s in all_stats if s and s.status == PoolStatus.DEGRADED)
        unhealthy = sum(1 for s in all_stats if s and s.status == PoolStatus.UNHEALTHY)
        
        overall_status = "healthy"
        if unhealthy > 0:
            overall_status = "unhealthy"
        elif degraded > 0:
            overall_status = "degraded"
        
        return {
            "overall_status": overall_status,
            "total_pools": len(all_stats),
            "healthy": healthy,
            "degraded": degraded,
            "unhealthy": unhealthy,
            "pools": [self.get_pool_health(name) for name in self._pools.keys()]
        }
