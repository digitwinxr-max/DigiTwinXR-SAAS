"""Pydantic schemas for Scenario Simulation Engine."""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class ScenarioType(str, Enum):
    """Types of scenarios."""
    FAILURE = "failure"
    RECOVERY = "recovery"
    MAINTENANCE = "maintenance"
    CUSTOM = "custom"


class ScenarioStatus(str, Enum):
    """Status of a scenario."""
    DRAFT = "draft"
    COMPLETED = "completed"


class Severity(str, Enum):
    """Event severity."""
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


# === Scenario Schemas ===

class ScenarioBase(BaseModel):
    """Base scenario schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    scenario_type: ScenarioType = Field(default=ScenarioType.FAILURE)
    severity: Severity = Field(default=Severity.CRITICAL)


class ScenarioCreate(ScenarioBase):
    """Schema for creating a scenario."""
    root_asset_id: UUID


class ScenarioUpdate(BaseModel):
    """Schema for updating a scenario."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    scenario_type: Optional[ScenarioType] = None
    severity: Optional[Severity] = None


class ScenarioResponse(ScenarioBase):
    """Schema for scenario response."""
    id: UUID
    root_asset_id: UUID
    status: ScenarioStatus
    created_at: datetime
    result_count: int = 0
    
    model_config = {"from_attributes": True}


class ScenarioListResponse(BaseModel):
    """Schema for paginated list of scenarios."""
    items: List[ScenarioResponse]
    total: int


# === Scenario Result Schemas ===

class ScenarioResultResponse(BaseModel):
    """Schema for scenario result response."""
    id: UUID
    scenario_id: UUID
    asset_id: UUID
    predicted_health: float
    current_health: float
    delta_health: float
    propagation_depth: int
    relationship_path: Optional[str] = None
    created_at: datetime
    
    # Asset info
    asset_name: Optional[str] = None
    asset_type: Optional[str] = None
    
    model_config = {"from_attributes": True}


class ScenarioResultListResponse(BaseModel):
    """Schema for list of scenario results."""
    items: List[ScenarioResultResponse]
    total: int


# === Impact Tree Schemas ===

class ImpactNode(BaseModel):
    """Schema for impact tree node."""
    asset_id: UUID
    asset_name: str
    asset_type: Optional[str] = None
    current_health: float
    predicted_health: float
    delta_health: float
    propagation_depth: int
    relationship_type: Optional[str] = None
    children: List["ImpactNode"] = Field(default_factory=list)


# Enable forward reference resolution
ImpactNode.model_rebuild()


# === Simulation Results Schemas ===

class SimulationResults(BaseModel):
    """Schema for complete simulation results."""
    scenario_id: UUID
    scenario_name: str
    scenario_type: ScenarioType
    severity: Severity
    root_asset_id: UUID
    root_asset_name: str
    affected_assets: List[ScenarioResultResponse]
    impact_tree: Optional[ImpactNode] = None
    max_depth: int
    worst_health: float
    average_health: float
    total_affected: int


class SimulationStats(BaseModel):
    """Schema for simulation statistics."""
    total_affected: int
    max_depth: int
    worst_health: float
    average_health: float
    total_health_loss: float


class SimulationResultsResponse(BaseModel):
    """Schema for simulation results with stats."""
    results: SimulationResults
    stats: SimulationStats


# === Comparison Schemas ===

class AssetComparison(BaseModel):
    """Schema for comparing current vs predicted health."""
    asset_id: UUID
    asset_name: str
    asset_type: Optional[str] = None
    current_health: float
    predicted_health: float
    delta: float


class ScenarioComparison(BaseModel):
    """Schema for scenario comparison."""
    scenario_id: UUID
    scenario_name: str
    root_asset_id: UUID
    root_asset_name: str
    root_current_health: float
    root_predicted_health: float
    root_delta: float
    affected_assets: List[AssetComparison]
    total_delta: float
    worst_delta: float
    affected_count: int


class ScenarioSummary(BaseModel):
    """Schema for scenario summary."""
    scenario_id: UUID
    scenario_name: str
    scenario_type: ScenarioType
    severity: Severity
    status: ScenarioStatus
    created_at: datetime
    total_affected: int
    worst_health: float
    average_delta: float


# === Virtual Objects (In-Memory Only) ===

class VirtualEvent(BaseModel):
    """In-memory virtual event for simulation.
    
    This represents an event that would occur but is NOT written
    to the events table. It only exists during simulation.
    """
    asset_id: UUID
    severity: Severity
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class VirtualPropagation(BaseModel):
    """In-memory virtual propagation for simulation.
    
    This represents a propagation that would occur but is NOT written
    to the propagated_events table. It only exists during simulation.
    """
    source_event: VirtualEvent
    affected_asset_id: UUID
    propagation_type: str
    depth: int
    severity: Severity


class VirtualHealth(BaseModel):
    """In-memory virtual health calculation.
    
    This represents what an asset's health would be but is NOT written
    to the asset_health table. It only exists during simulation.
    """
    asset_id: UUID
    live_health: float
    local_virtual_penalty: float
    virtual_dependency_penalty: float
    predicted_health: float
    depth: int = 0


# === Run Simulation ===

class RunSimulationRequest(BaseModel):
    """Schema for running a simulation."""
    scenario_id: UUID


class RunSimulationResponse(BaseModel):
    """Schema for simulation run response."""
    scenario_id: UUID
    status: str = "completed"
    total_affected: int
    max_depth: int
    worst_health: float
    average_health: float
    message: str