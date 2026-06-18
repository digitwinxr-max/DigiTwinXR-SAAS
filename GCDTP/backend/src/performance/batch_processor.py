"""
Batch Processor

Provides batch processing support.
"""

import uuid
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class BatchStatus(str, Enum):
    """Batch job status."""
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BatchJob:
    """Scheduled batch job."""
    id: str
    name: str
    batch_type: str
    schedule: Optional[str] = None  # cron expression
    interval_seconds: Optional[int] = None
    status: BatchStatus = BatchStatus.SCHEDULED
    created_at: datetime = None
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    run_count: int = 0
    config: Dict = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.config is None:
            self.config = {}


@dataclass
class BatchResult:
    """Batch execution result."""
    job_id: str
    status: BatchStatus
    processed: int
    failed: int
    duration_ms: int
    error: Optional[str] = None


class BatchProcessor:
    """
    Provides batch processing support.
    
    Supports:
    - Scheduled batches
    - Parallel execution
    - Retry handling
    - Job status
    """
    
    def __init__(self):
        self._jobs: Dict[str, BatchJob] = {}
        self._results: Dict[str, List[BatchResult]] = {}
        self._max_retries = 3
        self._running_jobs: Dict[str, bool] = {}
    
    def create_job(
        self,
        name: str,
        batch_type: str,
        schedule: Optional[str] = None,
        interval_seconds: Optional[int] = None,
        config: Optional[Dict] = None
    ) -> BatchJob:
        """
        Create a batch job.
        
        Args:
            name: Job name
            batch_type: Type of batch
            schedule: Cron schedule
            interval_seconds: Interval in seconds
            config: Job configuration
            
        Returns:
            BatchJob
        """
        job_id = str(uuid.uuid4())
        
        job = BatchJob(
            id=job_id,
            name=name,
            batch_type=batch_type,
            schedule=schedule,
            interval_seconds=interval_seconds,
            config=config or {}
        )
        
        self._jobs[job_id] = job
        self._results[job_id] = []
        
        return job
    
    def get_job(self, job_id: str) -> Optional[BatchJob]:
        """Get a job."""
        return self._jobs.get(job_id)
    
    def get_all_jobs(self) -> List[BatchJob]:
        """Get all jobs."""
        return list(self._jobs.values())
    
    def run_job(
        self,
        job_id: str,
        processor: Callable[[BatchJob], Any],
        retry: bool = True
    ) -> BatchResult:
        """
        Run a batch job.
        
        Args:
            job_id: Job ID
            processor: Processing function
            retry: Enable retries
            
        Returns:
            BatchResult
        """
        job = self._jobs.get(job_id)
        if not job:
            return BatchResult(
                job_id=job_id,
                status=BatchStatus.FAILED,
                processed=0,
                failed=0,
                duration_ms=0,
                error="Job not found"
            )
        
        self._running_jobs[job_id] = True
        job.status = BatchStatus.RUNNING
        job.last_run_at = datetime.utcnow()
        
        start_time = datetime.utcnow()
        processed = 0
        failed = 0
        error = None
        
        try:
            result = processor(job)
            if result:
                processed = result.get("processed", 0)
                failed = result.get("failed", 0)
            job.status = BatchStatus.COMPLETED
        except Exception as e:
            job.status = BatchStatus.FAILED
            error = str(e)
            
            if retry:
                failed = self._retry_job(job, processor)
        
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        result = BatchResult(
            job_id=job_id,
            status=job.status,
            processed=processed,
            failed=failed,
            duration_ms=duration_ms,
            error=error
        )
        
        self._results[job_id].append(result)
        self._running_jobs[job_id] = False
        job.run_count += 1
        
        return result
    
    def _retry_job(
        self,
        job: BatchJob,
        processor: Callable[[BatchJob], Any]
    ) -> int:
        """Retry a failed job."""
        failed = 0
        for attempt in range(self._max_retries):
            try:
                processor(job)
                return 0
            except Exception:
                failed += 1
        
        return failed
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job."""
        if job_id in self._running_jobs and self._running_jobs[job_id]:
            self._running_jobs[job_id] = False
            job = self._jobs.get(job_id)
            if job:
                job.status = BatchStatus.CANCELLED
            return True
        return False
    
    def get_job_results(
        self,
        job_id: str,
        limit: int = 100
    ) -> List[BatchResult]:
        """Get job results."""
        results = self._results.get(job_id, [])
        return results[-limit:]
    
    def is_running(self, job_id: str) -> bool:
        """Check if job is running."""
        return self._running_jobs.get(job_id, False)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get batch processor stats."""
        total_jobs = len(self._jobs)
        running_jobs = sum(1 for v in self._running_jobs.values() if v)
        
        total_runs = sum(len(r) for r in self._results.values())
        total_processed = sum(
            sum(r.processed for r in results)
            for results in self._results.values()
        )
        total_failed = sum(
            sum(r.failed for r in results)
            for results in self._results.values()
        )
        
        return {
            "total_jobs": total_jobs,
            "running_jobs": running_jobs,
            "total_runs": total_runs,
            "total_processed": total_processed,
            "total_failed": total_failed,
            "success_rate": (
                (total_processed - total_failed) / total_processed * 100
                if total_processed > 0 else 100
            )
        }
