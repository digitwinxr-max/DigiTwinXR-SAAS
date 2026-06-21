"""Asset Relationship model for graph-based asset hierarchy."""
import enum
from datetime import datetime
from uuid import UUID
from sqlalchemy import Column, String, DateTime, Enum, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from .base import Base


class RelationshipType(str, enum.Enum):
    """Types of relationships between assets.
    
    Note: These are the only allowed relationship types.
    No other types can be created.
    """
    CONTAINS = "contains"
    CONNECTED_TO = "connected_to"
    FEEDS = "feeds"
    MONITORS = "monitors"
    CONTROLS = "controls"


class AssetRelationship(Base):
    """Asset Relationship model for storing asset hierarchy.
    
    Represents directed relationships between assets:
    - parent_asset_id → The containing/larger asset
    - child_asset_id → The contained/child asset
    
    Relationships are directional. Use inverse relationship types
    for bidirectional associations (e.g., "connected_to" implies
    both directions but is stored once).
    
    Examples:
    - Site contains Building
    - Building contains Equipment
    - Equipment contains Sensor
    - PowerGrid feeds Facility
    - Controller controls Motor
    """
    
    __tablename__ = "asset_relationships"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=UUID)
    parent_asset_id = Column(
        PGUUID(as_uuid=True), 
        nullable=False, 
        index=True,
        comment="Parent/containing asset ID"
    )
    child_asset_id = Column(
        PGUUID(as_uuid=True), 
        nullable=False, 
        index=True,
        comment="Child/contained asset ID"
    )
    relationship_type = Column(
        Enum(RelationshipType, name='relationship_type', create_type=False),
        nullable=False,
        index=True,
        comment="Type of relationship"
    )
    created_at = Column(
        DateTime(timezone=True), 
        default=datetime.utcnow,
        nullable=False
    )
    
    # NOTE: Relationships with Asset are set up in setup_asset_relationships()
    # to avoid circular import issues with SQLAlchemy
    
    # Constraints
    __table_args__ = (
        # Prevent self-referencing relationships
        CheckConstraint(
            'parent_asset_id != child_asset_id',
            name='no_self_reference'
        ),
        # Prevent duplicate relationships
        UniqueConstraint(
            'parent_asset_id', 
            'child_asset_id', 
            'relationship_type',
            name='unique_relationship'
        ),
    )
    
    def __repr__(self):
        return (
            f"<AssetRelationship("
            f"id={self.id}, "
            f"parent={self.parent_asset_id}, "
            f"child={self.child_asset_id}, "
            f"type={self.relationship_type})>"
        )
    
    @property
    def is_self_referencing(self) -> bool:
        """Check if this is a self-referencing relationship."""
        return self.parent_asset_id == self.child_asset_id
    
    @classmethod
    def validate_relationship(cls, parent_id: UUID, child_id: UUID, rel_type: RelationshipType) -> bool:
        """Validate that a relationship can be created.
        
        Args:
            parent_id: Parent asset ID
            child_id: Child asset ID  
            rel_type: Relationship type
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If relationship is invalid
        """
        if parent_id == child_id:
            raise ValueError("Cannot create self-referencing relationship")
        
        if not isinstance(rel_type, RelationshipType):
            raise ValueError(f"Invalid relationship type: {rel_type}")
        
        return True


# Import Asset to set up relationships after Asset model is defined
def setup_asset_relationships():
    """Set up bidirectional relationships with Asset model.
    
    This function is called after all models are imported to avoid
    circular import issues with SQLAlchemy mapper configuration.
    
    Note: The service layer uses direct queries by ID, not ORM relationships.
    These are optional convenience relationships.
    """
    from .asset import Asset
    from sqlalchemy.orm import relationship
    
    # Add reverse relationships to Asset class
    # These allow: asset.child_relationships, asset.parent_relationships
    # They are set up here to avoid circular import issues
    pass  # Backrefs will be handled by Asset model's definition