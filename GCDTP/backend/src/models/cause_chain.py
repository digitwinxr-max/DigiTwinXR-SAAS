"""
Cause Chain Model

Causal chain of asset dependencies.
"""

import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class CauseChain:
    """
    Cause Chain record.
    
    Represents a link in the causal chain between assets.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str = ""
    depth: int = 0
    source_asset_id: str = ""
    target_asset_id: str = ""
    relationship_type: Optional[str] = None
    description: Optional[str] = None
    propagation_time_seconds: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "depth": self.depth,
            "source_asset_id": self.source_asset_id,
            "target_asset_id": self.target_asset_id,
            "relationship_type": self.relationship_type,
            "description": self.description,
            "propagation_time_seconds": self.propagation_time_seconds,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CauseChain":
        """Create from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            analysis_id=data.get("analysis_id", ""),
            depth=data.get("depth", 0),
            source_asset_id=data.get("source_asset_id", ""),
            target_asset_id=data.get("target_asset_id", ""),
            relationship_type=data.get("relationship_type"),
            description=data.get("description"),
            propagation_time_seconds=data.get("propagation_time_seconds"),
            created_at=created_at or datetime.utcnow()
        )
    
    def get_depth_display(self) -> str:
        """Get depth as ordinal."""
        ordinal = {1: "1st", 2: "2nd", 3: "3rd"}
        return ordinal.get(self.depth, f"{self.depth}th")
    
    def get_propagation_display(self) -> str:
        """Get propagation time as human-readable."""
        if self.propagation_time_seconds is None:
            return "Unknown"
        
        seconds = self.propagation_time_seconds
        if seconds < 60:
            return f"{seconds}s"
        if seconds < 3600:
            return f"{seconds // 60}m"
        if seconds < 86400:
            return f"{seconds // 3600}h"
        return f"{seconds // 86400}d"
