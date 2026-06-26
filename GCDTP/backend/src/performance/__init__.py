"""
Performance Module

Provides performance and scaling capabilities:
- Caching
- Pagination
- Bulk operations
- Batch processing
- Rate limiting
- API versioning
- Query optimization
- Connection pool management
- Memory profiling
- Performance analysis

Components:
- CacheManager
- PaginationEngine
- BulkOperationEngine
- BatchProcessor
- RateLimitManager
- APIVersionManager
- QueryOptimizer
- ConnectionPoolManager
- MemoryProfiler
- PerformanceAnalyzer
"""

from .cache_manager import CacheManager, CacheEntry
from .pagination_engine import (
    PaginationEngine,
    PaginationParams,
    PageMetadata,
    PaginatedResult
)
from .bulk_operation_engine import (
    BulkOperationEngine,
    BulkJob,
    BulkItem,
    BulkJobStatus,
    BulkItemStatus,
    BulkResult
)
from .batch_processor import (
    BatchProcessor,
    BatchJob,
    BatchStatus,
    BatchResult
)
from .rate_limit_manager import (
    RateLimitManager,
    RateLimitRule,
    RateLimitResult,
    RateLimitAlgorithm
)
from .api_version_manager import (
    APIVersionManager,
    APIVersion,
    APIVersionStatus,
    VersionNegotiationResult
)
from .query_optimizer import QueryOptimizer, QueryStatistics
from .connection_pool_manager import (
    ConnectionPoolManager,
    PoolStats,
    PoolStatus
)
from .memory_profiler import MemoryProfiler, MemorySnapshot
from .performance_analyzer import PerformanceAnalyzer, PerformanceMetrics
from .performance_validator import PerformanceValidator


__all__ = [
    # Cache
    "CacheManager",
    "CacheEntry",
    # Pagination
    "PaginationEngine",
    "PaginationParams",
    "PageMetadata",
    "PaginatedResult",
    # Bulk Operations
    "BulkOperationEngine",
    "BulkJob",
    "BulkItem",
    "BulkJobStatus",
    "BulkItemStatus",
    "BulkResult",
    # Batch Processing
    "BatchProcessor",
    "BatchJob",
    "BatchStatus",
    "BatchResult",
    # Rate Limiting
    "RateLimitManager",
    "RateLimitRule",
    "RateLimitResult",
    "RateLimitAlgorithm",
    # API Versioning
    "APIVersionManager",
    "APIVersion",
    "APIVersionStatus",
    "VersionNegotiationResult",
    # Query Optimization
    "QueryOptimizer",
    "QueryStatistics",
    # Connection Pool
    "ConnectionPoolManager",
    "PoolStats",
    "PoolStatus",
    # Memory Profiling
    "MemoryProfiler",
    "MemorySnapshot",
    # Performance Analysis
    "PerformanceAnalyzer",
    "PerformanceMetrics",
    # Validation
    "PerformanceValidator",
]
