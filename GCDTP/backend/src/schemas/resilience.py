"""
Resilience Schemas

Pydantic schemas for resilience analysis endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class RecommendationPriority(str, Enum):
    """Priority levels for recommendations."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RecommendationType(str, Enum):
    """Types of resilience recommendations."""
    REDUNDANCY = "redundancy"
    MONITORING = "monitoring"
    BACKUP = "backup"
    FAILOVER = "failover"
    MAINTENANCE = "maintenance"
    DIVERSIFICATION = "diversification"
    RECONFIGURATION = "reconfiguration"
    EARLY_WARNING = "early_warning"


# ============================================================================
# Analysis Schemas
# ============================================================================

class ResilienceAnalysisResponse(BaseModel):
    """Response schema for a single resilience analysis."""
    id: str
    asset_id: str
    criticality_score: float = Field(ge=0, le=100)
    resilience_score: float = Field(ge=0, le=100)
    dependency_count: int = Field(ge=0)
    upstream_count: int = Field(ge=0)
    downstream_count: int = Field(ge=0)
    single_point_of_failure: bool
    created_at: datetime
    recommendations: List["RecommendationResponse"] = []

    class Config:
        from_attributes = True


# ============================================================================
# Recommendation Schemas
# ============================================================================

class RecommendationResponse(BaseModel):
    """Response schema for a recommendation."""
    id: str
    analysis_id: str
    recommendation_type: RecommendationType
    priority: RecommendationPriority
    description: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Critical Asset Schemas
# ============================================================================

class CriticalAssetResponse(BaseModel):
    """Response schema for a critical asset."""
    asset_id: str
    asset_name: str
    asset_type: str
    criticality_score: float = Field(ge=0, le=100)
    resilience_score: float = Field(ge=0, le=100)
    single_point_of_failure: bool
    dependency_count: int
    upstream_count: int
    downstream_count: int
    top_recommendation: Optional[RecommendationResponse] = None


class TopCriticalAssetsResponse(BaseModel):
    """Response for top critical assets."""
    assets: List[CriticalAssetResponse]
    total: int
    network_avg_criticality: float
    network_avg_resilience: float


# ============================================================================
# Network Resilience Schemas
# ============================================================================

class NetworkResilienceResponse(BaseModel):
    """Response schema for overall network resilience."""
    total_assets: int
    analyzed_assets: int
    avg_criticality: float = Field(ge=0, le=100)
    avg_resilience: float = Field(ge=0, le=100)
    single_points_of_failure: int
    high_criticality_count: int  # > 70
    medium_criticality_count: int  # 40-70
    low_criticality_count: int  # < 40
    critical_assets: List[CriticalAssetResponse]
    recommendations_by_priority: dict = Field(default_factory=dict)


# ============================================================================
# Request Schemas
# ============================================================================

class AnalyzeAssetRequest(BaseModel):
    """Request to analyze a single asset."""
    force_refresh: bool = Field(default=False, description="Force re-analysis even if recent analysis exists")


class AnalyzeNetworkRequest(BaseModel):
    """Request to analyze the entire network."""
    force_refresh: bool = Field(default=False, description="Force re-analysis of all assets")


# ============================================================================
# Helper Functions
# ============================================================================

def get_criticality_level(score: float) -> str:
    """Get criticality level label based on score."""
    if score >= 70:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    else:
        return "LOW"


def get_resilience_level(score: float) -> str:
    """Get resilience level label based on score."""
    if score >= 70:
        return "GOOD"
    elif score >= 40:
        return "MODERATE"
    else:
        return "POOR"


def get_criticality_color(score: float) -> str:
    """Get color for criticality visualization."""
    if score < 40:
        return "#22c55e"  # Green
    elif score < 70:
        return "#f97316"  # Orange
    else:
        return "#ef4444"  # Red


def get_priority_color(priority: RecommendationPriority) -> str:
    """Get color for priority visualization."""
    colors = {
        RecommendationPriority.LOW: "#22c55e",
        RecommendationPriority.MEDIUM: "#eab308",
        RecommendationPriority.HIGH: "#f97316",
        RecommendationPriority.CRITICAL: "#ef4444",
    }
    return colors.get(priority, "#6b7280")


# Update forward references
ResilienceAnalysisResponse.model_rebuild()
