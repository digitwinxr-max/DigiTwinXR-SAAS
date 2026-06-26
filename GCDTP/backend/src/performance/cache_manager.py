"""
Cache Manager

Provides multi-level caching support.
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import OrderedDict


@dataclass
class CacheEntry:
    """Cache entry."""
    key: str
    value: Any
    ttl_seconds: int
    created_at: datetime
    accessed_at: datetime
    hits: int = 0
    misses: int = 0


class CacheManager:
    """
    Multi-level cache manager.
    
    Supports:
    - TTL cache
    - LRU cache
    - Memory cache
    - Query cache
    - Snapshot cache
    - Ontology cache
    - Graph cache
    - Metrics cache
    """
    
    def __init__(self):
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._max_size = 10000
        self._default_ttl = 300  # 5 minutes
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }
    
    def get(
        self,
        key: str,
        cache_type: str = "memory"
    ) -> Optional[Any]:
        """Get a value from cache."""
        if key not in self._cache:
            self._stats["misses"] += 1
            return None
        
        entry = self._cache[key]
        
        # Check TTL
        if entry.ttl_seconds > 0:
            age = (datetime.utcnow() - entry.created_at).total_seconds()
            if age > entry.ttl_seconds:
                del self._cache[key]
                self._stats["misses"] += 1
                return None
        
        # Update access info
        entry.accessed_at = datetime.utcnow()
        entry.hits += 1
        self._stats["hits"] += 1
        
        # Move to end (LRU)
        self._cache.move_to_end(key)
        
        return entry.value
    
    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        cache_type: str = "memory"
    ) -> None:
        """Set a value in cache."""
        ttl = ttl_seconds or self._default_ttl
        
        entry = CacheEntry(
            key=key,
            value=value,
            ttl_seconds=ttl,
            created_at=datetime.utcnow(),
            accessed_at=datetime.utcnow()
        )
        
        # Remove if exists
        if key in self._cache:
            del self._cache[key]
        
        # Add new entry
        self._cache[key] = entry
        
        # Evict if needed
        if len(self._cache) > self._max_size:
            self._evict_lru()
    
    def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self, cache_type: Optional[str] = None) -> None:
        """Clear cache."""
        if cache_type:
            # Would filter by type in production
            self._cache.clear()
        else:
            self._cache.clear()
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if self._cache:
            self._cache.popitem(last=False)
            self._stats["evictions"] += 1
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total * 100) if total > 0 else 0
        
        return {
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "evictions": self._stats["evictions"],
            "size": len(self._cache),
            "hit_rate_percent": round(hit_rate, 2)
        }
    
    def get_query_cache(
        self,
        query_hash: str
    ) -> Optional[Dict]:
        """Get query cache entry."""
        return self.get(f"query:{query_hash}", cache_type="query")
    
    def set_query_cache(
        self,
        query_hash: str,
        result: Dict,
        ttl_seconds: int = 300
    ) -> None:
        """Set query cache entry."""
        self.set(f"query:{query_hash}", result, ttl_seconds, cache_type="query")
    
    def get_snapshot_cache(
        self,
        snapshot_id: str
    ) -> Optional[Dict]:
        """Get snapshot cache entry."""
        return self.get(f"snapshot:{snapshot_id}", cache_type="snapshot")
    
    def set_snapshot_cache(
        self,
        snapshot_id: str,
        data: Dict,
        ttl_seconds: int = 3600
    ) -> None:
        """Set snapshot cache entry."""
        self.set(f"snapshot:{snapshot_id}", data, ttl_seconds, cache_type="snapshot")
    
    def get_ontology_cache(
        self,
        class_id: str
    ) -> Optional[Dict]:
        """Get ontology cache entry."""
        return self.get(f"ontology:{class_id}", cache_type="ontology")
    
    def set_ontology_cache(
        self,
        class_id: str,
        data: Dict,
        ttl_seconds: int = 1800
    ) -> None:
        """Set ontology cache entry."""
        self.set(f"ontology:{class_id}", data, ttl_seconds, cache_type="ontology")
    
    def get_graph_cache(
        self,
        entity_id: str
    ) -> Optional[Dict]:
        """Get graph cache entry."""
        return self.get(f"graph:{entity_id}", cache_type="graph")
    
    def set_graph_cache(
        self,
        entity_id: str,
        data: Dict,
        ttl_seconds: int = 600
    ) -> None:
        """Set graph cache entry."""
        self.set(f"graph:{entity_id}", data, ttl_seconds, cache_type="graph")
    
    def get_metrics_cache(
        self,
        metric_name: str
    ) -> Optional[Dict]:
        """Get metrics cache entry."""
        return self.get(f"metrics:{metric_name}", cache_type="metrics")
    
    def set_metrics_cache(
        self,
        metric_name: str,
        data: Dict,
        ttl_seconds: int = 60
    ) -> None:
        """Set metrics cache entry."""
        self.set(f"metrics:{metric_name}", data, ttl_seconds, cache_type="metrics")
