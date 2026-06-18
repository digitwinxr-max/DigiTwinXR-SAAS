"""
Restore Manager

Manages restore operations.
"""

import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class RestoreStatus(str, Enum):
    """Restore status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RestoreType(str, Enum):
    """Restore types."""
    FULL = "full"
    POINT_IN_TIME = "point_in_time"
    SELECTIVE = "selective"


@dataclass
class RestoreJob:
    """Restore job."""
    id: str
    backup_id: str
    restore_type: RestoreType
    status: RestoreStatus
    target_environment: str
    point_in_time: Optional[datetime] = None
    selective_items: List[str] = None
    dry_run: bool = False
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by: str = ""
    metadata: Dict = None
    
    def __post_init__(self):
        if self.selective_items is None:
            self.selective_items = []
        if self.metadata is None:
            self.metadata = {}


class RestoreManager:
    """
    Manages restore operations.
    
    Supports:
    - Point-in-time restore
    - Selective restore
    - Dry-run validation
    """
    
    def __init__(self):
        self._jobs: Dict[str, RestoreJob] = {}
    
    def create_restore(
        self,
        backup_id: str,
        restore_type: RestoreType,
        target_environment: str,
        created_by: str = "",
        point_in_time: Optional[datetime] = None,
        selective_items: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> RestoreJob:
        """Create a new restore job."""
        job_id = str(uuid.uuid4())
        
        job = RestoreJob(
            id=job_id,
            backup_id=backup_id,
            restore_type=restore_type,
            status=RestoreStatus.PENDING,
            target_environment=target_environment,
            point_in_time=point_in_time,
            selective_items=selective_items or [],
            dry_run=dry_run,
            created_by=created_by
        )
        
        self._jobs[job_id] = job
        return job
    
    def start_restore(self, job_id: str) -> bool:
        """Start a restore job."""
        job = self._jobs.get(job_id)
        if not job or job.status != RestoreStatus.PENDING:
            return False
        
        job.status = RestoreStatus.RUNNING
        job.started_at = datetime.utcnow()
        return True
    
    def complete_restore(self, job_id: str) -> bool:
        """Complete a restore job."""
        job = self._jobs.get(job_id)
        if not job or job.status != RestoreStatus.RUNNING:
            return False
        
        job.status = RestoreStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        return True
    
    def fail_restore(self, job_id: str) -> bool:
        """Fail a restore job."""
        job = self._jobs.get(job_id)
        if not job:
            return False
        
        job.status = RestoreStatus.FAILED
        job.completed_at = datetime.utcnow()
        return True
    
    def cancel_restore(self, job_id: str) -> bool:
        """Cancel a restore job."""
        job = self._jobs.get(job_id)
        if not job or job.status not in [RestoreStatus.PENDING, RestoreStatus.RUNNING]:
            return False
        
        job.status = RestoreStatus.CANCELLED
        job.completed_at = datetime.utcnow()
        return True
    
    def get_job(self, job_id: str) -> Optional[RestoreJob]:
        """Get a restore job."""
        return self._jobs.get(job_id)
    
    def get_jobs_by_status(self, status: RestoreStatus) -> List[RestoreJob]:
        """Get jobs by status."""
        return [j for j in self._jobs.values() if j.status == status]
    
    def get_dry_runs(self) -> List[RestoreJob]:
        """Get dry-run restore jobs."""
        return [j for j in self._jobs.values() if j.dry_run]
    
    def validate_restore(self, job_id: str) -> Dict[str, Any]:
        """Validate a restore job."""
        job = self._jobs.get(job_id)
        if not job:
            return {"valid": False, "errors": ["Job not found"]}
        
        errors = []
        
        if job.restore_type == RestoreType.POINT_IN_TIME and not job.point_in_time:
            errors.append("Point-in-time restore requires a timestamp")
        
        if job.restore_type == RestoreType.SELECTIVE and not job.selective_items:
            errors.append("Selective restore requires items to restore")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "job_id": job_id
        }
