"""
Bulk Operation Engine

Provides bulk operations support.
"""

import uuid
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class BulkJobStatus(str, Enum):
    """Bulk job status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BulkItemStatus(str, Enum):
    """Bulk item status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class BulkJob:
    """Bulk operation job."""
    id: str
    job_type: str  # create, update, delete
    entity_type: str  # asset, document, work_order
    status: BulkJobStatus
    total_items: int
    processed_items: int = 0
    failed_items: int = 0
    created_by: Optional[str] = None
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class BulkItem:
    """Bulk operation item."""
    id: str
    job_id: str
    item_id: str
    item_data: Dict
    status: BulkItemStatus = BulkItemStatus.PENDING
    error_message: Optional[str] = None
    processed_at: Optional[datetime] = None


@dataclass
class BulkResult:
    """Result of bulk operation."""
    job_id: str
    total_items: int
    processed_items: int
    failed_items: int
    failed_items_list: List[Dict]
    status: BulkJobStatus


class BulkOperationEngine:
    """
    Provides bulk operations support.
    
    Supports:
    - Bulk create
    - Bulk update
    - Bulk delete
    - Batch validation
    - Partial failure recovery
    """
    
    def __init__(self):
        self._jobs: Dict[str, BulkJob] = {}
        self._items: Dict[str, List[BulkItem]] = {}
        self._max_batch_size = 1000
    
    def create_job(
        self,
        job_type: str,
        entity_type: str,
        items: List[Dict],
        created_by: Optional[str] = None
    ) -> BulkJob:
        """
        Create a bulk job.
        
        Args:
            job_type: Type of operation (create, update, delete)
            entity_type: Entity type (asset, document, work_order)
            items: Items to process
            created_by: User creating the job
            
        Returns:
            BulkJob
        """
        job_id = str(uuid.uuid4())
        
        job = BulkJob(
            id=job_id,
            job_type=job_type,
            entity_type=entity_type,
            status=BulkJobStatus.PENDING,
            total_items=len(items),
            created_by=created_by
        )
        
        # Create items
        bulk_items = []
        for item in items:
            bulk_item = BulkItem(
                id=str(uuid.uuid4()),
                job_id=job_id,
                item_id=item.get("id", str(uuid.uuid4())),
                item_data=item
            )
            bulk_items.append(bulk_item)
        
        self._jobs[job_id] = job
        self._items[job_id] = bulk_items
        
        return job
    
    def get_job(self, job_id: str) -> Optional[BulkJob]:
        """Get a job by ID."""
        return self._jobs.get(job_id)
    
    def get_job_items(
        self,
        job_id: str,
        status: Optional[BulkItemStatus] = None
    ) -> List[BulkItem]:
        """Get items for a job."""
        items = self._items.get(job_id, [])
        if status:
            items = [i for i in items if i.status == status]
        return items
    
    def start_job(self, job_id: str) -> bool:
        """Start a job."""
        job = self._jobs.get(job_id)
        if not job or job.status != BulkJobStatus.PENDING:
            return False
        
        job.status = BulkJobStatus.RUNNING
        job.started_at = datetime.utcnow()
        return True
    
    def complete_job(self, job_id: str) -> bool:
        """Complete a job."""
        job = self._jobs.get(job_id)
        if not job or job.status != BulkJobStatus.RUNNING:
            return False
        
        job.status = BulkJobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        return True
    
    def fail_job(self, job_id: str, error: str) -> bool:
        """Fail a job."""
        job = self._jobs.get(job_id)
        if not job:
            return False
        
        job.status = BulkJobStatus.FAILED
        job.completed_at = datetime.utcnow()
        return True
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job."""
        job = self._jobs.get(job_id)
        if not job or job.status in [BulkJobStatus.COMPLETED, BulkJobStatus.FAILED]:
            return False
        
        job.status = BulkJobStatus.CANCELLED
        job.completed_at = datetime.utcnow()
        return True
    
    def update_item_status(
        self,
        item_id: str,
        job_id: str,
        status: BulkItemStatus,
        error_message: Optional[str] = None
    ) -> bool:
        """Update item status."""
        items = self._items.get(job_id, [])
        for item in items:
            if item.id == item_id:
                item.status = status
                if status == BulkItemStatus.COMPLETED:
                    item.processed_at = datetime.utcnow()
                if error_message:
                    item.error_message = error_message
                
                # Update job counters
                job = self._jobs.get(job_id)
                if job:
                    job.processed_items += 1
                    if status == BulkItemStatus.FAILED:
                        job.failed_items += 1
                
                return True
        return False
    
    def get_pending_jobs(self) -> List[BulkJob]:
        """Get pending jobs."""
        return [j for j in self._jobs.values() if j.status == BulkJobStatus.PENDING]
    
    def get_running_jobs(self) -> List[BulkJob]:
        """Get running jobs."""
        return [j for j in self._jobs.values() if j.status == BulkJobStatus.RUNNING]
    
    def validate_items(
        self,
        items: List[Dict],
        validator: Callable[[Dict], bool]
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Validate items.
        
        Args:
            items: Items to validate
            validator: Validation function
            
        Returns:
            Tuple of (valid_items, invalid_items)
        """
        valid = []
        invalid = []
        
        for item in items:
            try:
                if validator(item):
                    valid.append(item)
                else:
                    invalid.append({"item": item, "error": "Validation failed"})
            except Exception as e:
                invalid.append({"item": item, "error": str(e)})
        
        return valid, invalid
    
    def get_result(self, job_id: str) -> Optional[BulkResult]:
        """Get job result."""
        job = self._jobs.get(job_id)
        if not job:
            return None
        
        failed_items = [
            {"item_id": i.item_id, "error": i.error_message}
            for i in self._items.get(job_id, [])
            if i.status == BulkItemStatus.FAILED
        ]
        
        return BulkResult(
            job_id=job_id,
            total_items=job.total_items,
            processed_items=job.processed_items,
            failed_items=job.failed_items,
            failed_items_list=failed_items,
            status=job.status
        )
