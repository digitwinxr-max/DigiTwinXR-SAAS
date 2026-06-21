"""
LangGraph Checkpoint Metadata

Checkpoint definitions for state persistence.
NO autonomous execution - only checkpoint metadata.
"""

from typing import Dict, List, Optional, Any, TypedDict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class CheckpointStatus(str, Enum):
    """Checkpoint status."""
    PENDING = "pending"
    SAVED = "saved"
    FAILED = "failed"
    RESTORED = "restored"


@dataclass
class CheckpointMetadata:
    """Metadata for a checkpoint."""
    checkpoint_id: str
    graph_name: str
    session_id: str
    step: int
    created_at: datetime
    status: CheckpointStatus
    size_bytes: Optional[int] = None
    error: Optional[str] = None
    parent_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class StateSnapshot:
    """
    State snapshot metadata.
    
    Contains state data but no execution logic.
    """
    checkpoint_id: str
    graph_name: str
    session_id: str
    step: int
    state: Dict[str, Any]
    created_at: datetime
    metadata: CheckpointMetadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "checkpoint_id": self.checkpoint_id,
            "graph_name": self.graph_name,
            "session_id": self.session_id,
            "step": self.step,
            "state": self.state,
            "created_at": self.created_at.isoformat(),
            "metadata": {
                "status": self.metadata.status.value,
                "size_bytes": self.metadata.size_bytes,
                "tags": self.metadata.tags,
            }
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class CheckpointRegistry:
    """
    Registry for checkpoint metadata.
    
    Manages checkpoint metadata without executing state saves.
    """
    
    def __init__(self):
        self._checkpoints: Dict[str, CheckpointMetadata] = {}
        self._snapshots: Dict[str, StateSnapshot] = {}
    
    def create_checkpoint(
        self,
        checkpoint_id: str,
        graph_name: str,
        session_id: str,
        step: int,
        state: Dict[str, Any],
        parent_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> CheckpointMetadata:
        """
        Create checkpoint metadata.
        
        Note: This only creates metadata - actual state saving
        must be handled by the application.
        """
        metadata = CheckpointMetadata(
            checkpoint_id=checkpoint_id,
            graph_name=graph_name,
            session_id=session_id,
            step=step,
            created_at=datetime.now(),
            status=CheckpointStatus.PENDING,
            parent_id=parent_id,
            tags=tags or []
        )
        
        self._checkpoints[checkpoint_id] = metadata
        
        # Create snapshot
        snapshot = StateSnapshot(
            checkpoint_id=checkpoint_id,
            graph_name=graph_name,
            session_id=session_id,
            step=step,
            state=state,
            created_at=datetime.now(),
            metadata=metadata
        )
        self._snapshots[checkpoint_id] = snapshot
        
        return metadata
    
    def mark_saved(
        self,
        checkpoint_id: str,
        size_bytes: Optional[int] = None
    ) -> CheckpointMetadata:
        """Mark checkpoint as saved."""
        if checkpoint_id not in self._checkpoints:
            raise ValueError(f"Checkpoint {checkpoint_id} not found")
        
        metadata = self._checkpoints[checkpoint_id]
        metadata.status = CheckpointStatus.SAVED
        metadata.size_bytes = size_bytes
        
        return metadata
    
    def mark_failed(
        self,
        checkpoint_id: str,
        error: str
    ) -> CheckpointMetadata:
        """Mark checkpoint as failed."""
        if checkpoint_id not in self._checkpoints:
            raise ValueError(f"Checkpoint {checkpoint_id} not found")
        
        metadata = self._checkpoints[checkpoint_id]
        metadata.status = CheckpointStatus.FAILED
        metadata.error = error
        
        return metadata
    
    def mark_restored(self, checkpoint_id: str) -> CheckpointMetadata:
        """Mark checkpoint as restored."""
        if checkpoint_id not in self._checkpoints:
            raise ValueError(f"Checkpoint {checkpoint_id} not found")
        
        metadata = self._checkpoints[checkpoint_id]
        metadata.status = CheckpointStatus.RESTORED
        
        return metadata
    
    def get_checkpoint(self, checkpoint_id: str) -> Optional[CheckpointMetadata]:
        """Get checkpoint metadata."""
        return self._checkpoints.get(checkpoint_id)
    
    def get_snapshot(self, checkpoint_id: str) -> Optional[StateSnapshot]:
        """Get state snapshot."""
        return self._snapshots.get(checkpoint_id)
    
    def list_checkpoints(
        self,
        session_id: Optional[str] = None,
        graph_name: Optional[str] = None,
        status: Optional[CheckpointStatus] = None
    ) -> List[CheckpointMetadata]:
        """List checkpoints with optional filters."""
        checkpoints = list(self._checkpoints.values())
        
        if session_id:
            checkpoints = [c for c in checkpoints if c.session_id == session_id]
        
        if graph_name:
            checkpoints = [c for c in checkpoints if c.graph_name == graph_name]
        
        if status:
            checkpoints = [c for c in checkpoints if c.status == status]
        
        return sorted(checkpoints, key=lambda c: c.created_at, reverse=True)
    
    def get_latest(
        self,
        session_id: str,
        graph_name: Optional[str] = None
    ) -> Optional[CheckpointMetadata]:
        """Get the latest checkpoint for a session."""
        checkpoints = self.list_checkpoints(
            session_id=session_id,
            graph_name=graph_name,
            status=CheckpointStatus.SAVED
        )
        return checkpoints[0] if checkpoints else None
    
    def get_lineage(
        self,
        checkpoint_id: str
    ) -> List[CheckpointMetadata]:
        """Get the lineage of a checkpoint (all ancestors)."""
        lineage = []
        current_id = checkpoint_id
        
        while current_id:
            checkpoint = self._checkpoints.get(current_id)
            if not checkpoint:
                break
            lineage.append(checkpoint)
            current_id = checkpoint.parent_id
        
        return lineage
    
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint."""
        if checkpoint_id in self._checkpoints:
            del self._checkpoints[checkpoint_id]
        if checkpoint_id in self._snapshots:
            del self._snapshots[checkpoint_id]
        return True


# Singleton instance
_registry: Optional[CheckpointRegistry] = None


def get_checkpoint_registry() -> CheckpointRegistry:
    """Get or create checkpoint registry singleton."""
    global _registry
    if _registry is None:
        _registry = CheckpointRegistry()
    return _registry
