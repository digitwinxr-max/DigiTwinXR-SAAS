"""Pydantic schemas for Asset Relationships."""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class RelationshipType(str, Enum):
    """Types of relationships between assets."""
    CONTAINS = "contains"
    CONNECTED_TO = "connected_to"
    FEEDS = "feeds"
    MONITORS = "monitors"
    CONTROLS = "controls"


class AssetRelationshipBase(BaseModel):
    """Base schema for asset relationships."""
    parent_asset_id: UUID = Field(..., description="Parent/containing asset ID")
    child_asset_id: UUID = Field(..., description="Child/contained asset ID")
    relationship_type: RelationshipType = Field(..., description="Type of relationship")


class AssetRelationshipCreate(AssetRelationshipBase):
    """Schema for creating an asset relationship."""
    
    @field_validator('parent_asset_id', 'child_asset_id')
    @classmethod
    def validate_not_same(cls, v, info):
        """Validate that parent and child are not the same."""
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "parent_asset_id": "123e4567-e89b-12d3-a456-426614174000",
                "child_asset_id": "123e4567-e89b-12d3-a456-426614174001",
                "relationship_type": "contains"
            }
        }
    }


class AssetRelationshipResponse(AssetRelationshipBase):
    """Schema for asset relationship response."""
    id: UUID
    created_at: datetime
    
    # Include asset names for convenience
    parent_asset_name: Optional[str] = None
    child_asset_name: Optional[str] = None
    
    model_config = {"from_attributes": True}


class AssetRelationshipListResponse(BaseModel):
    """Schema for paginated list of relationships."""
    items: List[AssetRelationshipResponse]
    total: int
    page: int
    page_size: int
    pages: int


class AssetRelationshipGraphNode(BaseModel):
    """Schema for a node in the relationship graph."""
    asset_id: UUID
    asset_name: str
    asset_type: Optional[str] = None
    health_status: Optional[str] = None
    health_score: Optional[float] = None
    relationship_type: Optional[RelationshipType] = None  # Only set for child nodes
    children: List["AssetRelationshipGraphNode"] = Field(default_factory=list)


# Enable forward reference resolution
AssetRelationshipGraphNode.model_rebuild()


class AssetRelationshipGraphResponse(BaseModel):
    """Schema for the full relationship graph."""
    asset_id: UUID
    asset_name: str
    asset_type: Optional[str] = None
    health_status: Optional[str] = None
    health_score: Optional[float] = None
    children: List[AssetRelationshipGraphNode] = Field(default_factory=list)
    parents: List[AssetRelationshipGraphNode] = Field(default_factory=list)
    depth: int = 0  # Maximum depth of the graph


class AssetRelationshipCreateResponse(BaseModel):
    """Schema for relationship creation response."""
    relationship: AssetRelationshipResponse
    message: str = "Relationship created successfully"


class AssetRelationshipDeleteResponse(BaseModel):
    """Schema for relationship deletion response."""
    id: UUID
    message: str = "Relationship deleted successfully"


class RelationshipTypeInfo(BaseModel):
    """Information about a relationship type."""
    type: RelationshipType
    description: str
    inverse_type: Optional[RelationshipType] = None


# Relationship type descriptions
RELATIONSHIP_TYPE_INFO = {
    RelationshipType.CONTAINS: RelationshipTypeInfo(
        type=RelationshipType.CONTAINS,
        description="Parent contains the child (hierarchical ownership)",
        inverse_type=None,  # Inverse is implied containment
    ),
    RelationshipType.CONNECTED_TO: RelationshipTypeInfo(
        type=RelationshipType.CONNECTED_TO,
        description="Assets are physically or logically connected",
        inverse_type=RelationshipType.CONNECTED_TO,  # Symmetric relationship
    ),
    RelationshipType.FEEDS: RelationshipTypeInfo(
        type=RelationshipType.FEEDS,
        description="Parent provides input/material/energy to child",
        inverse_type=RelationshipType.FEEDS,  # Could also be "receives_from"
    ),
    RelationshipType.MONITORS: RelationshipTypeInfo(
        type=RelationshipType.MONITORS,
        description="Parent monitors or measures child",
        inverse_type=None,  # Inverse would be "monitored_by"
    ),
    RelationshipType.CONTROLS: RelationshipTypeInfo(
        type=RelationshipType.CONTROLS,
        description="Parent controls or commands child",
        inverse_type=None,  # Inverse would be "controlled_by"
    ),
}