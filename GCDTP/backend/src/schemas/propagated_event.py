"""Pydantic schemas for Propagated Events."""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class PropagationType(str, Enum):
    """Types of propagation through asset relationships."""
    CHILD_FAILURE = "child_failure"
    UPSTREAM_FAILURE = "upstream_failure"
    DOWNSTREAM_FAILURE = "downstream_failure"
    DEPENDENCY_IMPACT = "dependency_impact"


class PropagatedEventResponse(BaseModel):
    """Schema for propagated event response."""
    id: UUID
    source_event_id: UUID
    source_asset_id: UUID
    affected_asset_id: UUID
    propagation_type: PropagationType
    severity: str
    depth: int
    created_at: datetime
    
    # Asset names for convenience
    source_asset_name: Optional[str] = None
    affected_asset_name: Optional[str] = None
    source_event_message: Optional[str] = None
    
    model_config = {"from_attributes": True}


class PropagatedEventListResponse(BaseModel):
    """Schema for paginated list of propagated events."""
    items: List[PropagatedEventResponse]
    total: int
    page: int
    page_size: int
    pages: int


class ImpactChainNode(BaseModel):
    """Schema for a node in the impact chain."""
    asset_id: UUID
    asset_name: str
    asset_type: Optional[str] = None
    severity: str
    depth: int
    relationship_type: Optional[str] = None
    propagation_type: PropagationType
    health_status: Optional[str] = None
    health_score: Optional[float] = None
    children: List["ImpactChainNode"] = Field(default_factory=list)


# Enable forward reference resolution
ImpactChainNode.model_rebuild()


class ImpactChainResponse(BaseModel):
    """Schema for the full impact chain response."""
    source_event_id: UUID
    source_asset_id: UUID
    source_asset_name: str
    source_severity: str
    root_event_message: Optional[str] = None
    chain: List[ImpactChainNode]
    max_depth: int
    total_affected: int


class AssetImpactSummary(BaseModel):
    """Summary of impacts on an asset."""
    asset_id: UUID
    asset_name: str
    total_impacts: int
    critical_impacts: int
    warning_impacts: int
    upstream_impacts: int
    downstream_impacts: int
    source_events: List[dict] = Field(default_factory=list)


class PropagationCreateResponse(BaseModel):
    """Response when propagation is created."""
    propagated_count: int
    max_depth_reached: int
    affected_assets: List[dict]
    message: str = "Propagation completed"


class PropagationTypesInfo(BaseModel):
    """Information about propagation types."""
    type: PropagationType
    description: str
    direction: str  # "up", "down", or "both"


# Propagation type descriptions
PROPAGATION_TYPE_INFO = {
    PropagationType.CHILD_FAILURE: PropagationTypesInfo(
        type=PropagationType.CHILD_FAILURE,
        description="Child failure propagated to parent",
        direction="up",
    ),
    PropagationType.UPSTREAM_FAILURE: PropagationTypesInfo(
        type=PropagationType.UPSTREAM_FAILURE,
        description="Upstream asset failure affected this asset",
        direction="up",
    ),
    PropagationType.DOWNSTREAM_FAILURE: PropagationTypesInfo(
        type=PropagationType.DOWNSTREAM_FAILURE,
        description="Downstream asset failure affected this asset",
        direction="down",
    ),
    PropagationType.DEPENDENCY_IMPACT: PropagationTypesInfo(
        type=PropagationType.DEPENDENCY_IMPACT,
        description="Dependency failure impacted this asset",
        direction="both",
    ),
}