"""
Backup Manager

Manages backup operations.
"""

import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class BackupStatus(str, Enum):
    """Backup status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BackupType(str, Enum):
    """Backup types."""
    POSTGRESQL = "postgresql"
    CONFIG = "config"
    METADATA = "metadata"
    SNAPSHOT = "snapshot"


@dataclass
class BackupJob:
    """Backup job."""
    id: str
    backup_type: BackupType
    status: BackupStatus
    size_bytes: int = 0
    duration_seconds: int = 0
    path: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by: str = ""
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BackupManager:
    """
    Manages backup operations.
    
    Supports:
    - PostgreSQL backups
    - Configuration backups
    - Metadata backups
    - Snapshot backups
    """
    
    def __init__(self):
        self._jobs: Dict[str, BackupJob] = {}
    
    def create_backup(
        self,
        backup_type: BackupType,
        created_by: str = ""
    ) -> BackupJob:
        """Create a new backup job."""
        job_id = str(uuid.uuid4())
        
        job = BackupJob(
            id=job_id,
            backup_type=backup_type,
            status=BackupStatus.PENDING,
            created_by=created_by
        )
        
        self._jobs[job_id] = job
        return job
    
    def start_backup(self, job_id: str) -> bool:
        """Start a backup job."""
        job = self._jobs.get(job_id)
        if not job or job.status != BackupStatus.PENDING:
            return False
        
        job.status = BackupStatus.RUNNING
        job.started_at = datetime.utcnow()
        return True
    
    def complete_backup(
        self,
        job_id: str,
        size_bytes: int,
        path: str,
        duration_seconds: int
    ) -> bool:
        """Complete a backup job."""
        job = self._jobs.get(job_id)
        if not job or job.status != BackupStatus.RUNNING:
            return False
        
        job.status = BackupStatus.COMPLETED
        job.size_bytes = size_bytes
        job.path = path
        job.duration_seconds = duration_seconds
        job.completed_at = datetime.utcnow()
        return True
    
    def fail_backup(self, job_id: str) -> bool:
        """Fail a backup job."""
        job = self._jobs.get(job_id)
        if not job:
            return False
        
        job.status = BackupStatus.FAILED
        job.completed_at = datetime.utcnow()
        return True
    
    def cancel_backup(self, job_id: str) -> bool:
        """Cancel a backup job."""
        job = self._jobs.get(job_id)
        if not job or job.status not in [BackupStatus.PENDING, BackupStatus.RUNNING]:
            return False
        
        job.status = BackupStatus.CANCELLED
        job.completed_at = datetime.utcnow()
        return True
    
    def get_job(self, job_id: str) -> Optional[BackupJob]:
        """Get a backup job."""
        return self._jobs.get(job_id)
    
    def get_jobs_by_status(self, status: BackupStatus) -> List[BackupJob]:
        """Get jobs by status."""
        return [j for j in self._jobs.values() if j.status == status]
    
    def get_jobs_by_type(self, backup_type: BackupType) -> List[BackupJob]:
        """Get jobs by type."""
        return [j for j in self._jobs.values() if j.backup_type == backup_type]
    
    def get_recent_jobs(self, limit: int = 10) -> List[BackupJob]:
        """Get recent backup jobs."""
        sorted_jobs = sorted(
            self._jobs.values(),
            key=lambda x: x.started_at or datetime.min,
            reverse=True
        )
        return sorted_jobs[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get backup statistics."""
        jobs = list(self._jobs.values())
        
        completed = [j for j in jobs if j.status == BackupStatus.COMPLETED]
        failed = [j for j in jobs if j.status == BackupStatus.FAILED]
        
        total_size = sum(j.size_bytes for j in completed)
        total_duration = sum(j.duration_seconds for j in completed)
        
        return {
            "total_jobs": len(jobs),
            "completed": len(completed),
            "failed": len(failed),
            "pending": len([j for j in jobs if j.status == BackupStatus.PENDING]),
            "running": len([j for j in jobs if j.status == BackupStatus.RUNNING]),
            "total_size_bytes": total_size,
            "avg_duration_seconds": total_duration / len(completed) if completed else 0
        }
