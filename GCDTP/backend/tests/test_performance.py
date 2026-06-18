"""
Tests for Performance Module

Tests caching, pagination, bulk operations, rate limiting, API versioning, and query optimization.
"""

import pytest
from backend.src.performance import (
    CacheManager,
    CacheEntry,
    PaginationEngine,
    PaginationParams,
    PageMetadata,
    PaginatedResult,
    BulkOperationEngine,
    BulkJob,
    BulkJobStatus,
    BulkItemStatus,
    BatchProcessor,
    BatchStatus,
    BatchResult,
    RateLimitManager,
    RateLimitRule,
    RateLimitAlgorithm,
    APIVersionManager,
    APIVersion,
    APIVersionStatus,
    QueryOptimizer,
    ConnectionPoolManager,
    PoolStatus,
    MemoryProfiler,
    PerformanceAnalyzer,
    PerformanceValidator,
)


class TestCacheManager:
    """Tests for CacheManager."""
    
    def test_set_and_get(self):
        """Test setting and getting cache."""
        cache = CacheManager()
        cache.set("key1", "value1")
        
        result = cache.get("key1")
        assert result == "value1"
    
    def test_cache_miss(self):
        """Test cache miss."""
        cache = CacheManager()
        result = cache.get("nonexistent")
        
        assert result is None
    
    def test_cache_delete(self):
        """Test cache deletion."""
        cache = CacheManager()
        cache.set("key1", "value1")
        cache.delete("key1")
        
        result = cache.get("key1")
        assert result is None
    
    def test_cache_ttl(self):
        """Test cache TTL."""
        cache = CacheManager()
        cache.set("key1", "value1", ttl_seconds=1)
        
        result = cache.get("key1")
        assert result == "value1"
    
    def test_cache_stats(self):
        """Test cache statistics."""
        cache = CacheManager()
        cache.set("key1", "value1")
        cache.get("key1")
        cache.get("key2")
        
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
    
    def test_query_cache(self):
        """Test query cache."""
        cache = CacheManager()
        cache.set_query_cache("hash123", {"result": "data"})
        
        result = cache.get_query_cache("hash123")
        assert result == {"result": "data"}
    
    def test_snapshot_cache(self):
        """Test snapshot cache."""
        cache = CacheManager()
        cache.set_snapshot_cache("snap1", {"data": "snapshot"})
        
        result = cache.get_snapshot_cache("snap1")
        assert result == {"data": "snapshot"}


class TestPaginationEngine:
    """Tests for PaginationEngine."""
    
    def test_offset_pagination(self):
        """Test offset pagination."""
        engine = PaginationEngine()
        items = [1, 2, 3, 4, 5]
        
        params = PaginationParams(page=1, page_size=2)
        result = engine.paginate_offset(items, 5, params)
        
        assert result.pagination_type == "offset"
        assert len(result.items) == 2
        assert result.metadata.total_items == 5
        assert result.metadata.total_pages == 3
    
    def test_cursor_pagination(self):
        """Test cursor pagination."""
        engine = PaginationEngine()
        items = [{"id": 1}, {"id": 2}, {"id": 3}]
        
        params = PaginationParams(page_size=2)
        result = engine.paginate_cursor(items, 3, params, cursor_field="id")
        
        assert result.pagination_type == "cursor"
        assert len(result.items) == 2
    
    def test_sorting(self):
        """Test sorting."""
        engine = PaginationEngine()
        items = [{"name": "z"}, {"name": "a"}, {"name": "m"}]
        
        sorted_items = engine.sort_items(items, "name", "asc")
        assert sorted_items[0]["name"] == "a"
    
    def test_filtering(self):
        """Test filtering."""
        engine = PaginationEngine()
        items = [{"status": "active"}, {"status": "inactive"}, {"status": "active"}]
        
        filtered = engine.filter_items(items, {"status": "active"})
        assert len(filtered) == 2
    
    def test_page_slice(self):
        """Test getting page slice."""
        engine = PaginationEngine()
        items = list(range(100))
        
        page = engine.get_page_slice(items, 2, 10)
        assert len(page) == 10
        assert page[0] == 10


class TestBulkOperationEngine:
    """Tests for BulkOperationEngine."""
    
    def test_create_job(self):
        """Test creating a bulk job."""
        engine = BulkOperationEngine()
        items = [{"id": "1"}, {"id": "2"}]
        
        job = engine.create_job("create", "asset", items, "user1")
        
        assert job.job_type == "create"
        assert job.entity_type == "asset"
        assert job.total_items == 2
    
    def test_start_job(self):
        """Test starting a job."""
        engine = BulkOperationEngine()
        items = [{"id": "1"}]
        job = engine.create_job("create", "asset", items)
        
        result = engine.start_job(job.id)
        
        assert result is True
        assert engine.get_job(job.id).status == BulkJobStatus.RUNNING
    
    def test_complete_job(self):
        """Test completing a job."""
        engine = BulkOperationEngine()
        items = [{"id": "1"}]
        job = engine.create_job("create", "asset", items)
        engine.start_job(job.id)
        
        engine.complete_job(job.id)
        
        assert engine.get_job(job.id).status == BulkJobStatus.COMPLETED
    
    def test_fail_job(self):
        """Test failing a job."""
        engine = BulkOperationEngine()
        items = [{"id": "1"}]
        job = engine.create_job("create", "asset", items)
        
        engine.fail_job(job.id, "Error")
        
        assert engine.get_job(job.id).status == BulkJobStatus.FAILED
    
    def test_validate_items(self):
        """Test validating items."""
        engine = BulkOperationEngine()
        items = [{"id": "1"}, {"id": "2"}]
        
        def validator(item):
            return "id" in item
        
        valid, invalid = engine.validate_items(items, validator)
        
        assert len(valid) == 2
        assert len(invalid) == 0


class TestBatchProcessor:
    """Tests for BatchProcessor."""
    
    def test_create_job(self):
        """Test creating a batch job."""
        processor = BatchProcessor()
        
        job = processor.create_job(
            "test_batch",
            "scheduled",
            interval_seconds=60
        )
        
        assert job.name == "test_batch"
        assert job.batch_type == "scheduled"
    
    def test_run_job(self):
        """Test running a job."""
        processor = BatchProcessor()
        job = processor.create_job("test", "manual")
        
        def processor_func(batch_job):
            return {"processed": 10, "failed": 0}
        
        result = processor.run_job(job.id, processor_func)
        
        assert result.status == BatchStatus.COMPLETED
        assert result.processed == 10
    
    def test_cancel_job(self):
        """Test cancelling a job."""
        processor = BatchProcessor()
        job = processor.create_job("test", "manual")
        
        processor.cancel_job(job.id)
        
        assert processor.get_job(job.id).status == BatchStatus.CANCELLED
    
    def test_get_stats(self):
        """Test getting stats."""
        processor = BatchProcessor()
        
        stats = processor.get_stats()
        
        assert "total_jobs" in stats
        assert stats["total_jobs"] >= 0


class TestRateLimitManager:
    """Tests for RateLimitManager."""
    
    def test_add_rule(self):
        """Test adding a rate limit rule."""
        manager = RateLimitManager()
        rule = RateLimitRule(
            rule_id="rule1",
            limit_type="user",
            target_id="user123",
            requests_per_minute=100
        )
        
        manager.add_rule(rule)
        
        assert manager.check_limit("user", "user123").allowed is True
    
    def test_rate_limit_exceeded(self):
        """Test rate limit exceeded."""
        manager = RateLimitManager()
        rule = RateLimitRule(
            rule_id="rule1",
            limit_type="user",
            target_id="user123",
            requests_per_minute=2
        )
        manager.add_rule(rule)
        
        # Make requests up to limit
        manager.check_limit("user", "user123")
        manager.check_limit("user", "user123")
        result = manager.check_limit("user", "user123")
        
        assert result.allowed is False
    
    def test_burst_limit(self):
        """Test burst limit."""
        manager = RateLimitManager()
        rule = RateLimitRule(
            rule_id="rule1",
            limit_type="global",
            target_id=None,
            requests_per_minute=60,
            burst_limit=10
        )
        manager.add_rule(rule)
        
        result = manager.check_limit("global", None)
        assert result.allowed is True
    
    def test_get_stats(self):
        """Test getting stats."""
        manager = RateLimitManager()
        
        stats = manager.get_stats()
        
        assert "total_rules" in stats


class TestAPIVersionManager:
    """Tests for APIVersionManager."""
    
    def test_get_default_version(self):
        """Test getting default version."""
        manager = APIVersionManager()
        
        version = manager.get_default_version()
        
        assert version.version == "v1"
    
    def test_negotiate_version(self):
        """Test version negotiation."""
        manager = APIVersionManager()
        
        result = manager.negotiate_version(requested_version="v1")
        
        assert result.negotiated_version == "v1"
        assert result.is_supported is True
    
    def test_parse_accept_header(self):
        """Test parsing Accept header."""
        manager = APIVersionManager()
        
        version = manager._parse_accept_header("application/vnd.gcdtp.v2+json")
        
        assert version == "v2"
    
    def test_deprecate_version(self):
        """Test deprecating a version."""
        manager = APIVersionManager()
        from datetime import date
        
        manager.deprecate_version("v1", date(2027, 1, 1), "Migrate to v2")
        
        version = manager.get_version("v1")
        assert version.status == APIVersionStatus.DEPRECATED


class TestQueryOptimizer:
    """Tests for QueryOptimizer."""
    
    def test_record_query(self):
        """Test recording a query."""
        optimizer = QueryOptimizer()
        
        stats = optimizer.record_query("SELECT * FROM assets", 100)
        
        assert stats.query_hash is not None
        assert stats.avg_time_ms == 100
    
    def test_get_slow_queries(self):
        """Test getting slow queries."""
        optimizer = QueryOptimizer()
        optimizer.set_slow_query_threshold(50)
        
        optimizer.record_query("SELECT 1", 100)
        optimizer.record_query("SELECT 2", 200)
        
        slow = optimizer.get_slow_queries()
        
        assert len(slow) == 2
    
    def test_get_stats_summary(self):
        """Test getting stats summary."""
        optimizer = QueryOptimizer()
        
        optimizer.record_query("SELECT 1", 50)
        
        summary = optimizer.get_stats_summary()
        
        assert "total_queries" in summary


class TestConnectionPoolManager:
    """Tests for ConnectionPoolManager."""
    
    def test_get_pool_stats(self):
        """Test getting pool stats."""
        manager = ConnectionPoolManager()
        
        stats = manager.get_pool_stats("postgresql")
        
        assert stats.pool_name == "postgresql"
        assert stats.max_connections == 20
    
    def test_record_connection(self):
        """Test recording connection."""
        manager = ConnectionPoolManager()
        
        manager.record_connection("postgresql", "acquire")
        
        stats = manager.get_pool_stats("postgresql")
        assert stats.active_connections >= 0
    
    def test_get_overall_health(self):
        """Test getting overall health."""
        manager = ConnectionPoolManager()
        
        health = manager.get_overall_health()
        
        assert "overall_status" in health
        assert "total_pools" in health


class TestMemoryProfiler:
    """Tests for MemoryProfiler."""
    
    def test_take_snapshot(self):
        """Test taking a snapshot."""
        profiler = MemoryProfiler()
        
        snapshot = profiler.take_snapshot()
        
        assert snapshot.heap_used_mb > 0
    
    def test_get_heap_usage(self):
        """Test getting heap usage."""
        profiler = MemoryProfiler()
        
        usage = profiler.get_heap_usage()
        
        assert "heap_used_mb" in usage
        assert "heap_percent" in usage
    
    def test_force_gc(self):
        """Test forcing garbage collection."""
        profiler = MemoryProfiler()
        
        result = profiler.force_gc()
        
        assert "collected" in result


class TestPerformanceAnalyzer:
    """Tests for PerformanceAnalyzer."""
    
    def test_record_latency(self):
        """Test recording latency."""
        analyzer = PerformanceAnalyzer()
        
        analyzer.record_latency(100)
        analyzer.record_latency(200)
        
        stats = analyzer.get_latency_stats()
        
        assert stats["avg"] == 150
    
    def test_record_cache_hit(self):
        """Test recording cache hit."""
        analyzer = PerformanceAnalyzer()
        
        analyzer.record_cache_hit()
        analyzer.record_cache_hit()
        analyzer.record_cache_miss()
        
        ratio = analyzer.get_cache_hit_ratio()
        
        assert ratio == 2/3
    
    def test_get_throughput_stats(self):
        """Test getting throughput stats."""
        analyzer = PerformanceAnalyzer()
        
        analyzer.record_throughput(100)
        analyzer.record_throughput(200)
        
        stats = analyzer.get_throughput_stats()
        
        assert stats["avg"] == 150


class TestPerformanceValidator:
    """Tests for PerformanceValidator."""
    
    def test_validate_cache_config(self):
        """Test validating cache config."""
        validator = PerformanceValidator()
        
        issues = validator.validate_cache_config(1000, 300)
        
        assert len(issues) == 0
    
    def test_validate_cache_config_invalid(self):
        """Test validating invalid cache config."""
        validator = PerformanceValidator()
        
        issues = validator.validate_cache_config(-1, -1)
        
        assert len(issues) > 0
    
    def test_validate_rate_limit_rule(self):
        """Test validating rate limit rule."""
        validator = PerformanceValidator()
        
        issues = validator.validate_rate_limit_rule(100, 10)
        
        assert len(issues) == 0
    
    def test_validate_pagination_params(self):
        """Test validating pagination params."""
        validator = PerformanceValidator()
        
        issues = validator.validate_pagination_params(1, 20, 100)
        
        assert len(issues) == 0
    
    def test_validate_api_version(self):
        """Test validating API version."""
        validator = PerformanceValidator()
        
        issues = validator.validate_api_version("v1", ["v1", "v2"])
        
        assert len(issues) == 0


class TestAPIVersion:
    """Tests for APIVersion."""
    
    def test_create_version(self):
        """Test creating API version."""
        from datetime import date
        
        version = APIVersion(
            version="v2",
            display_name="API v2",
            status=APIVersionStatus.ACTIVE,
            release_date=date(2026, 6, 1)
        )
        
        assert version.version == "v2"


class TestBatchStatus:
    """Tests for BatchStatus enum."""
    
    def test_batch_statuses(self):
        """Test batch status values."""
        assert BatchStatus.SCHEDULED.value == "scheduled"
        assert BatchStatus.RUNNING.value == "running"
        assert BatchStatus.COMPLETED.value == "completed"


class TestPoolStatus:
    """Tests for PoolStatus enum."""
    
    def test_pool_statuses(self):
        """Test pool status values."""
        assert PoolStatus.HEALTHY.value == "healthy"
        assert PoolStatus.DEGRADED.value == "degraded"
        assert PoolStatus.UNHEALTHY.value == "unhealthy"


class TestRateLimitAlgorithm:
    """Tests for RateLimitAlgorithm enum."""
    
    def test_algorithms(self):
        """Test rate limit algorithms."""
        assert RateLimitAlgorithm.TOKEN_BUCKET.value == "token_bucket"
        assert RateLimitAlgorithm.SLIDING_WINDOW.value == "sliding_window"
