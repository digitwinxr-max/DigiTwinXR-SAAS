"""
Root Cause Analysis Model

READ ONLY engine - explains WHY failures occurred.
NO automation, NO event modification, NO work orders.
"""

import uuid
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


class AnalysisType(str, Enum):
    """Types of root cause analysis."""
    FAILURE = "failure"
    HEALTH_DEGRADATION = "health_degradation"
    DEPENDENCY_CHAIN = "dependency_chain"
    EVENT_SEQUENCE = "event_sequence"


@dataclass
class RootCauseAnalysis:
    """
    Root Cause Analysis record.
    
    READ ONLY - Explains WHY failures occurred.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    asset_id: str = ""
    event_id: Optional[str] = None
    analysis_type: AnalysisType = AnalysisType.FAILURE
    probable_cause: str = ""
    confidence: float = 0.0
    summary: Optional[str] = None
    impacted_assets: List[str] = field(default_factory=list)
    root_assets: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "asset_id": self.asset_id,
            "event_id": self.event_id,
            "analysis_type": self.analysis_type.value if isinstance(self.analysis_type, Enum) else self.analysis_type,
            "probable_cause": self.probable_cause,
            "confidence": self.confidence,
            "summary": self.summary,
            "impacted_assets": self.impacted_assets,
            "root_assets": self.root_assets,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RootCauseAnalysis":
        """Create from dictionary."""
        analysis_type = data.get("analysis_type")
        if isinstance(analysis_type, str):
            analysis_type = AnalysisType(analysis_type)
        
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            asset_id=data.get("asset_id", ""),
            event_id=data.get("event_id"),
            analysis_type=analysis_type or AnalysisType.FAILURE,
            probable_cause=data.get("probable_cause", ""),
            confidence=data.get("confidence", 0.0),
            summary=data.get("summary"),
            impacted_assets=data.get("impacted_assets", []),
            root_assets=data.get("root_assets", []),
            created_at=created_at or datetime.utcnow()
        )
    
    def get_confidence_display(self) -> str:
        """Get percentage display."""
        return f"{self.confidence * 100:.0f}%"
    
    def get_analysis_type_display(self) -> str:
        """Get human-readable analysis type."""
        names = {
            AnalysisType.FAILURE: "Failure Analysis",
            AnalysisType.HEALTH_DEGRADATION: "Health Degradation",
            AnalysisType.DEPENDENCY_CHAIN: "Dependency Chain",
            AnalysisType.EVENT_SEQUENCE: "Event Sequence"
        }
        return names.get(self.analysis_type, "Unknown")
