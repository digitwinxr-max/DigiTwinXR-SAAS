"""Asset Health Dependency model for tracking dependency-based health penalties."""
import enum
from datetime import datetime
from uuid import UUID
from sqlalchemy import Column, Float, DateTime, Enum, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from .base import Base


class RelationshipType(str, enum.Enum):
    """Types of relationships for health dependencies."""
    CONTAINS = "contains"
    CONNECTED_TO = "connected_to"
    FEEDS = "feeds"
    MONITORS = "monitors"
    CONTROLS = "controls"


class AssetHealthDependency(Base):
    """Asset Health Dependency model for storing calculated health penalties.
    
    This model tracks the health penalty that one asset applies to another
    through their relationships. The penalty is calculated based on:
    - Source asset's health score
    - Relationship type weight
    - Propagation depth
    
    Example:
    - Transformer A has health 20 (CRITICAL)
    - Transformer A feeds Gaborone HQ
    - Gaborone HQ receives a penalty of: (100-20) * 0.7 * 1.0 = 56
    - If Gaborone HQ also contains Building B at depth 2, penalty is reduced
    """
    
    __tablename__ = "asset_health_dependencies"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=UUID)
    asset_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey('assets.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="The asset receiving the health penalty"
    )
    source_asset_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey('assets.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="The asset causing the health penalty"
    )
    relationship_type = Column(
        Enum(RelationshipType, name='relationship_type', create_type=False),
        nullable=False,
        index=True,
        comment="Type of relationship between assets"
    )
    impact_weight = Column(
        Float,
        nullable=False,
        default=1.0,
        comment="Weight factor for this relationship type (0.0-1.0)"
    )
    penalty = Column(
        Float,
        nullable=False,
        default=0.0,
        comment="Calculated health penalty amount"
    )
    depth = Column(
        Integer,
        nullable=False,
        default=1,
        comment="How many hops from the source asset"
    )
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    asset = relationship(
        "Asset",
        foreign_keys=[asset_id],
        backref="health_dependencies_received"
    )
    source_asset = relationship(
        "Asset",
        foreign_keys=[source_asset_id],
        backref="health_dependencies_caused"
    )
    
    # Constraints
    __table_args__ = (
        # Prevent duplicate dependency entries
        UniqueConstraint(
            'asset_id',
            'source_asset_id',
            'relationship_type',
            name='unique_dependency'
        ),
    )
    
    def __repr__(self):
        return (
            f"<AssetHealthDependency("
            f"id={self.id}, "
            f"asset={self.asset_id}, "
            f"source={self.source_asset_id}, "
            f"type={self.relationship_type}, "
            f"penalty={self.penalty})>"
        )
    
    @property
    def penalty_percentage(self) -> float:
        """Get penalty as a percentage (0-100 scale)."""
        return self.penalty
    
    @property
    def effective_weight(self) -> float:
        """Get effective weight considering depth decay."""
        return self.impact_weight * self._depth_decay(self.depth)
    
    @staticmethod
    def _depth_decay(depth: int) -> float:
        """Calculate depth decay factor.
        
        Args:
            depth: Propagation depth (1, 2, or 3)
            
        Returns:
            Decay factor: 1.0, 0.5, or 0.25
        """
        if depth <= 1:
            return 1.0
        elif depth == 2:
            return 0.5
        else:  # depth >= 3
            return 0.25


# Relationship weight constants
RELATIONSHIP_WEIGHTS = {
    RelationshipType.CONTAINS: 0.5,
    RelationshipType.FEEDS: 0.7,
    RelationshipType.CONTROLS: 0.6,
    RelationshipType.CONNECTED_TO: 0.3,
    RelationshipType.MONITORS: 0.0,  # No health impact
}


def get_relationship_weight(rel_type: RelationshipType) -> float:
    """Get the weight for a relationship type.
    
    Args:
        rel_type: The relationship type
        
    Returns:
        Weight value between 0.0 and 1.0
    """
    return RELATIONSHIP_WEIGHTS.get(rel_type, 0.0)


def get_depth_decay(depth: int) -> float:
    """Get the decay factor for a given depth.
    
    Args:
        depth: Propagation depth
        
    Returns:
        Decay factor
    """
    return AssetHealthDependency._depth_decay(depth)


def calculate_penalty(
    source_health_score: float,
    relationship_type: RelationshipType,
    depth: int
) -> float:
    """Calculate the health penalty for a dependency.
    
    Formula:
        penalty = (100 - source_health_score) * weight * depth_decay
    
    Args:
        source_health_score: Health score of source asset (0-100)
        relationship_type: Type of relationship
        depth: Propagation depth (1, 2, or 3)
        
    Returns:
        Penalty amount (0-100)
    """
    weight = get_relationship_weight(relationship_type)
    decay = get_depth_decay(depth)
    
    penalty = (100 - source_health_score) * weight * decay
    
    # Clamp to valid range
    return max(0.0, min(100.0, penalty))