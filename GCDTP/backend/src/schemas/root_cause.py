"""
Root Cause Analysis Schemas

Pydantic schemas for Root Cause Analysis Engine.
READ ONLY - NO automation, NO work orders.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# Cause Factor Schema
class CauseFactorSchema(BaseModel):
    """Schema for cause factor."""
    id: str
    analysis_id: str
    factor_type: str
    reference_id: Optional[str] = None
    weight: float
    description: str
    evidence: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Cause Chain Schema
class CauseChainSchema(BaseModel):
    """Schema for cause chain."""
    id: str
    analysis_id: str
    depth: int
    source_asset_id: str
    target_asset_id: str
    relationship_type: Optional[str] = None
    description: Optional[str] = None
    propagation_time_seconds: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Root Cause Response Schema
class RootCauseResponse(BaseModel):
    """Schema for root cause response."""
    id: str
    asset_id: str
    event_id: Optional[str] = None
    analysis_type: str
    probable_cause: str
    confidence: float
    summary: Optional[str] = None
    impacted_assets: List[str] = []
    root_assets: List[str] = []
    created_at: datetime
    factors: List[CauseFactorSchema] = []
    chains: List[CauseChainSchema] = []

    class Config:
        from_attributes = True


# Factor Response Schema
class FactorResponse(BaseModel):
    """Schema for factor response."""
    id: str
    factor_type: str
    description: str
    weight: float
    evidence: Optional[str] = None


# Ranked Factor Response Schema
class RankedFactorResponse(BaseModel):
    """Schema for ranked factor."""
    rank: int
    factor: FactorResponse


# Cause Chain Response Schema
class CauseChainResponse(BaseModel):
    """Schema for cause chain response."""
    id: str
    depth: int
    source_asset_id: str
    target_asset_id: str
    relationship_type: Optional[str] = None
    description: Optional[str] = None
    propagation_time_seconds: Optional[int] = None


# Confidence Response Schema
class ConfidenceResponse(BaseModel):
    """Schema for confidence analysis."""
    overall_confidence: float
    factor_score: float
    chain_score: float
    evidence_score: float
    factor_count: int
    chain_depth: int
    evidence_count: int


# Asset Cause Summary Schema
class AssetCauseSummary(BaseModel):
    """Schema for asset cause summary."""
    asset_id: str
    asset_name: str
    analysis_count: int
    avg_confidence: float
    max_confidence: float
    common_causes: List[str] = []
    last_analysis: Optional[datetime] = None


# High Confidence Analysis Schema
class HighConfidenceAnalysis(BaseModel):
    """Schema for high confidence analysis."""
    id: str
    asset_id: str
    asset_name: Optional[str] = None
    analysis_type: str
    probable_cause: str
    confidence: float
    summary: Optional[str] = None
    created_at: datetime


# Analysis Request Schema
class AnalysisRequest(BaseModel):
    """Schema for analysis request."""
    asset_id: str
    analysis_type: str = "failure"
    event_id: Optional[str] = None
    time_window_hours: int = Field(default=24, ge=1, le=720)


# Analysis Response Schema
class AnalysisResponse(BaseModel):
    """Schema for analysis response."""
    analysis: RootCauseResponse
    confidence: ConfidenceResponse
    ranked_factors: List[RankedFactorResponse] = []
    chain: List[CauseChainResponse] = []


# Event Sequence Schema
class EventSequenceItem(BaseModel):
    """Schema for event in sequence."""
    timestamp: datetime
    event_type: str
    asset_id: str
    severity: str
    description: str


# Event Sequence Response Schema
class EventSequenceResponse(BaseModel):
    """Schema for event sequence response."""
    asset_id: str
    events: List[EventSequenceItem]
    total_events: int


# Dependency Trace Schema
class DependencyTraceItem(BaseModel):
    """Schema for dependency trace item."""
    depth: int
    asset_id: str
    asset_name: str
    relationship_type: str
    health_score: Optional[float] = None


# Dependency Trace Response Schema
class DependencyTraceResponse(BaseModel):
    """Schema for dependency trace response."""
    root_asset_id: str
    trace: List[DependencyTraceItem]
    total_depth: int
