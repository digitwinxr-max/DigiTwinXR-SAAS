"""Propagated Event model for cascading failure tracking."""
import enum
from datetime import datetime
from uuid import UUID
from sqlalchemy import Column, String, DateTime, Enum, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from .base import Base


class PropagationType(str, enum.Enum):
    """Types of propagation through asset relationships."""
    CHILD_FAILURE = "child_failure"
    UPSTREAM_FAILURE = "upstream_failure"
    DOWNSTREAM_FAILURE = "downstream_failure"
    DEPENDENCY_IMPACT = "dependency_impact"


class PropagatedEvent(Base):
    """Propagated Event model for storing cascading failure impacts.
    
    Represents the consequence propagation from a source event through
    the asset relationship graph.
    
    Example:
    - Sensor fails (source_event)
    - Motor is affected via "monitors" relationship
    - Motor is affected via "feeds" relationship → Building
    
    This table tracks each hop of the propagation chain.
    """
    
    __tablename__ = "propagated_events"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=UUID)
    source_event_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey('events.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="The original event that triggered propagation"
    )
    source_asset_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey('assets.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="The asset where the original event occurred"
    )
    affected_asset_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey('assets.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="The asset affected by propagation"
    )
    propagation_type = Column(
        Enum(PropagationType, name='propagation_type', create_type=False),
        nullable=False,
        comment="Type of propagation"
    )
    severity = Column(
        String(20),
        nullable=False,
        comment="Severity of the propagated impact (WARNING/CRITICAL)"
    )
    depth = Column(
        Integer,
        nullable=False,
        default=1,
        comment="How many hops from the source event"
    )
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
    # Constraints
    __table_args__ = (
        # Prevent duplicate propagation records
        UniqueConstraint(
            'source_event_id',
            'affected_asset_id',
            'propagation_type',
            name='unique_propagation'
        ),
    )
    
    def __repr__(self):
        return (
            f"<PropagatedEvent("
            f"id={self.id}, "
            f"source={self.source_asset_id}, "
            f"affected={self.affected_asset_id}, "
            f"type={self.propagation_type}, "
            f"depth={self.depth})>"
        )
    
    @property
    def is_upstream(self) -> bool:
        """Check if this is an upstream propagation."""
        return self.propagation_type in (
            PropagationType.UPSTREAM_FAILURE,
            PropagationType.CHILD_FAILURE,
        )
    
    @property
    def is_downstream(self) -> bool:
        """Check if this is a downstream propagation."""
        return self.propagation_type in (
            PropagationType.DOWNSTREAM_FAILURE,
            PropagationType.DEPENDENCY_IMPACT,
        )


def deferred_setup_propagated_events():
    """Set up relationships for PropagatedEvent model.
    
    This function is called after all models are imported to avoid
    circular import issues with SQLAlchemy mapper configuration.
    """
    from .event import Event
    from .asset import Asset
    from sqlalchemy.orm import relationship
    
    # Set up source_event relationship
    PropagatedEvent.source_event = relationship(
        Event,
        foreign_keys=[PropagatedEvent.source_event_id],
        back_populates="propagated_events"
    )
    Event.propagated_events = relationship(
        PropagatedEvent,
        foreign_keys=[PropagatedEvent.source_event_id],
        back_populates="source_event",
        cascade="all, delete-orphan"
    )
    
    # Set up source_asset relationship
    PropagatedEvent.source_asset = relationship(
        Asset,
        foreign_keys=[PropagatedEvent.source_asset_id],
        back_populates="triggered_propagations"
    )
    Asset.triggered_propagations = relationship(
        PropagatedEvent,
        foreign_keys=[PropagatedEvent.source_asset_id],
        back_populates="source_asset",
        cascade="all, delete-orphan"
    )
    
    # Set up affected_asset relationship
    PropagatedEvent.affected_asset = relationship(
        Asset,
        foreign_keys=[PropagatedEvent.affected_asset_id],
        back_populates="affected_by_propagations"
    )
    Asset.affected_by_propagations = relationship(
        PropagatedEvent,
        foreign_keys=[PropagatedEvent.affected_asset_id],
        back_populates="affected_asset",
        cascade="all, delete-orphan"
    )