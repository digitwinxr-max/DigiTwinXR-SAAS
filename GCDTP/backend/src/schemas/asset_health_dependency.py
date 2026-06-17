"""Pydantic schemas for Asset Health Dependencies."""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class RelationshipType(str, Enum):
    """Types of relationships for health dependencies."""
    CONTAINS = "contains"
    CONNECTED_TO = "connected_to"
    FEEDS = "feeds"
    MONITORS = "monitors"
    CONTROLS = "controls"


# Relationship weight constants
RELATIONSHIP_WEIGHTS = {
    RelationshipType.CONTAINS: 0.5,
    RelationshipType.FEEDS: 0.7,
    RelationshipType.CONTROLS: 0.6,
    RelationshipType.CONNECTED_TO: 0.3,
    RelationshipType.MONITORS: 0.0,
}


# Depth decay constants
DEPTH_DECAY = {
    1: 1.0,
    2: 0.5,
    3: 0.25,
}


class AssetHealthDependencyResponse(BaseModel):
    """Schema for health dependency response."""
    id: UUID
    asset_id: UUID
    source_asset_id: UUID
    relationship_type: RelationshipType
    impact_weight: float
    penalty: float
    depth: int
    created_at: datetime
    
    # Asset names for convenience
    asset_name: Optional[str] = None
    source_asset_name: Optional[str] = None
    
    model_config = {"from_attributes": True}


class AssetHealthDependencyListResponse(BaseModel):
    """Schema for paginated list of health dependencies."""
    items: List[AssetHealthDependencyResponse]
    total: int


class HealthContributorNode(BaseModel):
    """Schema for a health contributor node in the tree."""
    asset_id: UUID
    asset_name: str
    asset_type: Optional[str] = None
    health_score: float
    health_status: str
    penalty: float
    depth: int
    relationship_type: Optional[RelationshipType] = None
    is_source: bool = False  # True if this is the original source of penalty
    children: List["HealthContributorNode"] = Field(default_factory=list)


# Enable forward reference resolution
HealthContributorNode.model_rebuild()


class HealthTreeNode(BaseModel):
    """Schema for a node in the health tree."""
    asset_id: UUID
    asset_name: str
    asset_type: Optional[str] = None
    health_score: float
    health_status: str
    local_penalty: float  # From local events only
    dependency_penalty: float  # From dependencies
    total_penalty: float
    contributors: List[HealthContributorNode] = Field(default_factory=list)
    children: List["HealthTreeNode"] = Field(default_factory=list)


# Enable forward reference resolution
HealthTreeNode.model_rebuild()


class HealthTreeResponse(BaseModel):
    """Schema for the full health tree response."""
    asset_id: UUID
    asset_name: str
    asset_type: Optional[str] = None
    health_score: float
    health_status: str
    local_penalty: float
    dependency_penalty: float
    total_penalty: float
    contributors: List[HealthContributorNode]
    depth: int
    max_depth: int = 3


class HealthContributorsResponse(BaseModel):
    """Schema for health contributors response."""
    asset_id: UUID
    asset_name: str
    current_health_score: float
    total_dependency_penalty: float
    contributors: List[HealthContributorNode]
    count: int


class NetworkHealthSummary(BaseModel):
    """Schema for network-wide health summary."""
    total_assets: int
    healthy_count: int
    degraded_count: int
    critical_count: int
    average_health_score: float
    total_dependency_penalties: float


class NetworkHealthResponse(BaseModel):
    """Schema for network health response."""
    summary: NetworkHealthSummary
    assets: List[HealthTreeNode]


class RecalculateResponse(BaseModel):
    """Response for network recalculation."""
    assets_recalculated: int
    total_penalties_updated: int
    message: str = "Network health recalculated successfully"


class RelationshipWeightInfo(BaseModel):
    """Information about relationship weights."""
    type: RelationshipType
    weight: float
    description: str


# Relationship descriptions
RELATIONSHIP_INFO = {
    RelationshipType.CONTAINS: {
        "description": "Parent affected by child failure",
        "weight": 0.5,
    },
    RelationshipType.CONNECTED_TO: {
        "description": "Connected assets share dependency",
        "weight": 0.3,
    },
    RelationshipType.FEEDS: {
        "description": "Consumer affected by provider failure",
        "weight": 0.7,
    },
    RelationshipType.MONITORS: {
        "description": "No health impact (informational only)",
        "weight": 0.0,
    },
    RelationshipType.CONTROLS: {
        "description": "Controlled asset affected by controller failure",
        "weight": 0.6,
    },
}