"""
Resilience Analysis Model

This model stores resilience analysis results for individual assets.
It is read-only from the perspective of operational systems.
"""

from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from backend.src.database.config import Base


class ResilienceAnalysis(Base):
    """
    Stores resilience analysis results for an asset.
    
    This table is populated only by the Resilience Analysis Engine
    and is never modified by operational systems.
    """
    
    __tablename__ = "resilience_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    
    # Scoring metrics (0-100 scale)
    criticality_score = Column(Float, nullable=False, default=0.0)
    resilience_score = Column(Float, nullable=False, default=100.0)
    
    # Dependency counts
    dependency_count = Column(Integer, nullable=False, default=0)
    upstream_count = Column(Integer, nullable=False, default=0)
    downstream_count = Column(Integer, nullable=False, default=0)
    
    # Risk indicators
    single_point_of_failure = Column(Boolean, nullable=False, default=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    # Relationships
    recommendations = relationship(
        "ResilienceRecommendation",
        back_populates="analysis",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<ResilienceAnalysis(id={self.id}, asset_id={self.asset_id}, criticality={self.criticality_score:.1f}, resilience={self.resilience_score:.1f})>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "asset_id": str(self.asset_id),
            "criticality_score": self.criticality_score,
            "resilience_score": self.resilience_score,
            "dependency_count": self.dependency_count,
            "upstream_count": self.upstream_count,
            "downstream_count": self.downstream_count,
            "single_point_of_failure": self.single_point_of_failure,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
