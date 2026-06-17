"""
Graph Projection Manager

Manages graph projections from PostgreSQL to Neo4j.
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from backend.src.integrations.neo4j.neo4j_client import Neo4jClient
from backend.src.integrations.neo4j.graph_types import (
    ProjectionJob,
    ProjectionStatus,
    EntityType,
    GraphNode,
    GraphRelationship,
)
from backend.src.core.events import get_event_bus, EventType


class GraphProjectionManager:
    """
    Manages graph projections.
    
    Responsibilities:
    - Create projections
    - Track projection status
    - Manage projection jobs
    """
    
    def __init__(self, client: Optional[Neo4jClient] = None):
        self.client = client or Neo4jClient()
        self.event_bus = get_event_bus()
        
        # Local storage for jobs
        self._jobs: Dict[str, ProjectionJob] = {}
    
    def close(self):
        """Close resources."""
        self.client.close()
    
    def create_projection_job(
        self,
        name: str,
        entity_type: EntityType,
        filters: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None
    ) -> ProjectionJob:
        """
        Create a projection job.
        
        Args:
            name: Job name
            entity_type: Type to project
            filters: Optional filters
            options: Projection options
            created_by: User creating job
            
        Returns:
            Created ProjectionJob
        """
        job = ProjectionJob(
            id=str(uuid.uuid4()),
            name=name,
            entity_type=entity_type,
            filters=filters or {},
            options=options or {},
            created_by=created_by
        )
        
        self._jobs[job.id] = job
        return job
    
    def start_projection(self, job: ProjectionJob) -> ProjectionJob:
        """
        Start a projection job.
        
        Args:
            job: Job to start
            
        Returns:
            Updated ProjectionJob
        """
        job.status = ProjectionStatus.RUNNING
        job.started_at = datetime.utcnow()
        
        self.event_bus.publish(
            EventType.GRAPH_SYNC_STARTED,
            source="projection_manager",
            data={
                "job_id": job.id,
                "entity_type": job.entity_type.value,
                "name": job.name
            }
        )
        
        return job
    
    def complete_projection(
        self,
        job: ProjectionJob,
        node_count: int,
        relationship_count: int
    ) -> ProjectionJob:
        """
        Complete a projection job.
        
        Args:
            job: Job to complete
            node_count: Number of nodes projected
            relationship_count: Number of relationships
            
        Returns:
            Updated ProjectionJob
        """
        job.status = ProjectionStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.node_count = node_count
        job.relationship_count = relationship_count
        
        self.event_bus.publish(
            EventType.GRAPH_SYNC_COMPLETED,
            source="projection_manager",
            data={
                "job_id": job.id,
                "entity_type": job.entity_type.value,
                "node_count": node_count,
                "relationship_count": relationship_count
            }
        )
        
        return job
    
    def fail_projection(self, job: ProjectionJob, error: str) -> ProjectionJob:
        """
        Mark a projection job as failed.
        
        Args:
            job: Job that failed
            error: Error message
            
        Returns:
            Updated ProjectionJob
        """
        job.status = ProjectionStatus.FAILED
        job.completed_at = datetime.utcnow()
        job.error_message = error
        
        return job
    
    def get_job(self, job_id: str) -> Optional[ProjectionJob]:
        """Get a job by ID."""
        return self._jobs.get(job_id)
    
    def get_jobs(
        self,
        status: Optional[ProjectionStatus] = None,
        entity_type: Optional[EntityType] = None
    ) -> List[ProjectionJob]:
        """Get all jobs with optional filtering."""
        jobs = list(self._jobs.values())
        
        if status:
            jobs = [j for j in jobs if j.status == status]
        
        if entity_type:
            jobs = [j for j in jobs if j.entity_type == entity_type]
        
        return sorted(jobs, key=lambda x: x.created_at, reverse=True)
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job."""
        job = self._jobs.get(job_id)
        if not job:
            return False
        
        if job.status in [ProjectionStatus.PENDING, ProjectionStatus.RUNNING]:
            job.status = ProjectionStatus.CANCELLED
            job.completed_at = datetime.utcnow()
            return True
        
        return False
    
    def get_running_jobs(self) -> List[ProjectionJob]:
        """Get all running jobs."""
        return self.get_jobs(status=ProjectionStatus.RUNNING)
    
    def get_pending_jobs(self) -> List[ProjectionJob]:
        """Get all pending jobs."""
        return self.get_jobs(status=ProjectionStatus.PENDING)
    
    # =========================================================================
    # Entity Projections
    # =========================================================================
    
    def project_assets(
        self,
        filters: Optional[Dict] = None
    ) -> ProjectionJob:
        """Project assets to graph."""
        return self.create_projection_job(
            name="Asset Projection",
            entity_type=EntityType.ASSET,
            filters=filters
        )
    
    def project_relationships(
        self,
        filters: Optional[Dict] = None
    ) -> ProjectionJob:
        """Project relationships to graph."""
        return self.create_projection_job(
            name="Relationship Projection",
            entity_type=EntityType.RELATIONSHIP,
            filters=filters
        )
    
    def project_work_orders(
        self,
        filters: Optional[Dict] = None
    ) -> ProjectionJob:
        """Project work orders to graph."""
        return self.create_projection_job(
            name="Work Order Projection",
            entity_type=EntityType.WORK_ORDER,
            filters=filters
        )
    
    def project_documents(
        self,
        filters: Optional[Dict] = None
    ) -> ProjectionJob:
        """Project documents to graph."""
        return self.create_projection_job(
            name="Document Projection",
            entity_type=EntityType.DOCUMENT,
            filters=filters
        )
    
    def project_devices(
        self,
        filters: Optional[Dict] = None
    ) -> ProjectionJob:
        """Project devices to graph."""
        return self.create_projection_job(
            name="Device Projection",
            entity_type=EntityType.DEVICE,
            filters=filters
        )
