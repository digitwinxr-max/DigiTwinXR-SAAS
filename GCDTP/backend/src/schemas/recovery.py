"""Pydantic schemas for Recovery Simulation Engine."""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class RecoveryType(str, Enum):
    """Types of recovery strategies."""
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    STAGED = "staged"
    REROUTE = "reroute"


class RiskLevel(str, Enum):
    """Risk levels."""
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# === Recovery Simulation Schemas ===

class RecoverySimulationBase(BaseModel):
    """Base recovery simulation schema."""
    strategy_name: str = Field(..., min_length=1, max_length=255)
    recovery_type: RecoveryType = Field(default=RecoveryType.MANUAL)
    estimated_duration_minutes: int = Field(default=60, ge=0)
    recovery_order: int = Field(default=1, ge=1)


class RecoverySimulationCreate(RecoverySimulationBase):
    """Schema for creating a recovery simulation."""
    scenario_id: UUID


class RecoverySimulationResponse(RecoverySimulationBase):
    """Schema for recovery simulation response."""
    id: UUID
    scenario_id: UUID
    created_at: datetime
    result_count: int = 0
    
    model_config = {"from_attributes": True}


class RecoverySimulationListResponse(BaseModel):
    """Schema for paginated list of recovery simulations."""
    items: List[RecoverySimulationResponse]
    total: int


# === Recovery Result Schemas ===

class RecoveryResultResponse(BaseModel):
    """Schema for recovery result response."""
    id: UUID
    recovery_simulation_id: UUID
    asset_id: UUID
    before_health: float
    after_health: float
    improvement: float
    recovery_depth: int
    remaining_risk: RiskLevel
    created_at: datetime
    
    # Asset info
    asset_name: Optional[str] = None
    asset_type: Optional[str] = None
    
    model_config = {"from_attributes": True}


class RecoveryResultListResponse(BaseModel):
    """Schema for list of recovery results."""
    items: List[RecoveryResultResponse]
    total: int


# === Recovery Tree Schemas ===

class RecoveryNode(BaseModel):
    """Schema for recovery tree node."""
    asset_id: UUID
    asset_name: str
    asset_type: Optional[str] = None
    before_health: float
    after_health: float
    improvement: float
    recovery_depth: int
    remaining_risk: RiskLevel
    children: List["RecoveryNode"] = Field(default_factory=list)


# Enable forward reference resolution
RecoveryNode.model_rebuild()


# === Recovery Summary Schemas ===

class RecoverySummary(BaseModel):
    """Schema for recovery summary."""
    recovery_id: UUID
    strategy_name: str
    recovery_type: RecoveryType
    estimated_duration_minutes: int
    total_assets: int
    assets_recovered: int
    worst_recovery: float
    best_recovery: float
    average_improvement: float
    remaining_critical: int


class RecoveryComparison(BaseModel):
    """Schema for comparing before/after recovery."""
    recovery_id: UUID
    strategy_name: str
    before_health: float
    after_health: float
    improvement: float
    remaining_critical: int
    assets: List[RecoveryResultResponse]


class RecoveryStats(BaseModel):
    """Schema for recovery statistics."""
    total_assets: int
    assets_fully_recovered: int
    average_improvement: float
    worst_after_health: float
    best_after_health: float
    estimated_duration_minutes: int
    remaining_critical_count: int


# === Run Recovery ===

class RunRecoveryRequest(BaseModel):
    """Schema for running a recovery simulation."""
    recovery_id: UUID


class RunRecoveryResponse(BaseModel):
    """Schema for recovery run response."""
    recovery_id: UUID
    status: str = "completed"
    total_assets: int
    assets_recovered: int
    average_improvement: float
    message: str


# === Recovery Values (Constants) ===

RECOVERY_VALUES = {
    RecoveryType.MANUAL: 20,
    RecoveryType.AUTOMATIC: 30,
    RecoveryType.STAGED: 15,  # per depth
    RecoveryType.REROUTE: 25,  # base value
}


# === Risk Level Functions ===

RISK_THRESHOLDS = {
    RiskLevel.NONE: 90,
    RiskLevel.LOW: 80,
    RiskLevel.MEDIUM: 60,
    RiskLevel.HIGH: 40,
}


def calculate_risk_level(health_score: float) -> RiskLevel:
    """Calculate risk level based on health score.
    
    Args:
        health_score: Asset health score (0-100)
        
    Returns:
        RiskLevel enum value
    """
    if health_score >= 90:
        return RiskLevel.NONE
    elif health_score >= 80:
        return RiskLevel.LOW
    elif health_score >= 60:
        return RiskLevel.MEDIUM
    elif health_score >= 40:
        return RiskLevel.HIGH
    else:
        return RiskLevel.CRITICAL


def get_risk_color(risk_level: RiskLevel) -> str:
    """Get color for risk level.
    
    Args:
        risk_level: Risk level enum
        
    Returns:
        Hex color string
    """
    colors = {
        RiskLevel.NONE: "#22c55e",
        RiskLevel.LOW: "#84cc16",
        RiskLevel.MEDIUM: "#eab308",
        RiskLevel.HIGH: "#f97316",
        RiskLevel.CRITICAL: "#ef4444",
    }
    return colors.get(risk_level, "#6b7280")