"""
Query Optimizer

Provides query optimization and statistics tracking.
"""

import hashlib
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class QueryStatistics:
    """Query statistics."""
    query_hash: str
    query_template: str
    execution_count: int
    total_time_ms: int
    avg_time_ms: int
    min_time_ms: int
    max_time_ms: int
    last_executed_at: Optional[datetime] = None
    slow_query: bool = False


class QueryOptimizer:
    """
    Provides query optimization.
    
    Tracks:
    - Slow queries
    - Query plans
    - Index recommendations
    - Query statistics
    """
    
    def __init__(self):
        self._stats: Dict[str, QueryStatistics] = {}
        self._slow_query_threshold_ms = 1000
        self._max_stats_entries = 1000
    
    def record_query(
        self,
        query: str,
        execution_time_ms: int
    ) -> QueryStatistics:
        """
        Record a query execution.
        
        Args:
            query: SQL query
            execution_time_ms: Execution time in milliseconds
            
        Returns:
            QueryStatistics
        """
        # Normalize query
        normalized = self._normalize_query(query)
        query_hash = self._compute_hash(normalized)
        
        if query_hash in self._stats:
            stats = self._stats[query_hash]
            stats.execution_count += 1
            stats.total_time_ms += execution_time_ms
            stats.avg_time_ms = stats.total_time_ms // stats.execution_count
            stats.min_time_ms = min(stats.min_time_ms, execution_time_ms)
            stats.max_time_ms = max(stats.max_time_ms, execution_time_ms)
            stats.last_executed_at = datetime.utcnow()
        else:
            stats = QueryStatistics(
                query_hash=query_hash,
                query_template=normalized,
                execution_count=1,
                total_time_ms=execution_time_ms,
                avg_time_ms=execution_time_ms,
                min_time_ms=execution_time_ms,
                max_time_ms=execution_time_ms,
                last_executed_at=datetime.utcnow(),
                slow_query=execution_time_ms > self._slow_query_threshold_ms
            )
            self._stats[query_hash] = stats
        
        return stats
    
    def get_slow_queries(self, limit: int = 50) -> List[QueryStatistics]:
        """Get slow queries."""
        slow = [s for s in self._stats.values() if s.slow_query]
        return sorted(slow, key=lambda x: x.avg_time_ms, reverse=True)[:limit]
    
    def get_frequent_queries(self, limit: int = 50) -> List[QueryStatistics]:
        """Get frequently executed queries."""
        return sorted(
            self._stats.values(),
            key=lambda x: x.execution_count,
            reverse=True
        )[:limit]
    
    def get_query_stats(self, query: str) -> Optional[QueryStatistics]:
        """Get statistics for a query."""
        normalized = self._normalize_query(query)
        query_hash = self._compute_hash(normalized)
        return self._stats.get(query_hash)
    
    def get_all_stats(self) -> List[QueryStatistics]:
        """Get all query statistics."""
        return list(self._stats.values())
    
    def get_index_recommendations(self) -> List[Dict[str, Any]]:
        """Get index recommendations based on query patterns."""
        recommendations = []
        
        # Analyze query patterns
        table_usage: Dict[str, set] = {}
        
        for stats in self._stats.values():
            tables = self._extract_tables(stats.query_template)
            for table in tables:
                if table not in table_usage:
                    table_usage[table] = set()
                table_usage[table].add(self._extract_where_columns(stats.query_template))
        
        for table, patterns in table_usage.items():
            if len(patterns) > 1:
                recommendations.append({
                    "table": table,
                    "type": "composite",
                    "reason": "Multiple query patterns",
                    "impact": "high"
                })
        
        return recommendations
    
    def _normalize_query(self, query: str) -> str:
        """Normalize a query for comparison."""
        # Remove extra whitespace
        normalized = " ".join(query.split())
        # Remove string literals
        normalized = "'" + normalized.count("'") * "?" + "'"
        normalized = normalized.replace("''", "?")
        # Remove numbers
        import re
        normalized = re.sub(r'\d+', '?', normalized)
        return normalized.lower()
    
    def _compute_hash(self, query: str) -> str:
        """Compute hash of query."""
        return hashlib.md5(query.encode()).hexdigest()
    
    def _extract_tables(self, query: str) -> List[str]:
        """Extract table names from query."""
        import re
        tables = re.findall(r'FROM\s+(\w+)|JOIN\s+(\w+)', query, re.IGNORECASE)
        return [t[0] or t[1] for t in tables]
    
    def _extract_where_columns(self, query: str) -> str:
        """Extract WHERE clause columns."""
        import re
        columns = re.findall(r'WHERE\s+(\w+)', query, re.IGNORECASE)
        return ",".join(columns) if columns else ""
    
    def set_slow_query_threshold(self, threshold_ms: int) -> None:
        """Set slow query threshold."""
        self._slow_query_threshold_ms = threshold_ms
    
    def clear_stats(self) -> None:
        """Clear all statistics."""
        self._stats.clear()
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """Get statistics summary."""
        if not self._stats:
            return {
                "total_queries": 0,
                "slow_queries": 0,
                "avg_execution_time_ms": 0
            }
        
        total_time = sum(s.total_time_ms for s in self._stats.values())
        total_count = sum(s.execution_count for s in self._stats.values())
        
        return {
            "total_queries": len(self._stats),
            "slow_queries": len(self.get_slow_queries(1000)),
            "total_executions": total_count,
            "avg_execution_time_ms": total_time // total_count if total_count > 0 else 0,
            "slow_query_threshold_ms": self._slow_query_threshold_ms
        }
