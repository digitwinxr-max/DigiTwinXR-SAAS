"""
Predictive Maintenance Schemas

Pydantic schemas for Predictive Maintenance Engine.
Deterministic predictions only - NO ML/AI.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# Prediction Request Schema
class PredictionRequest(BaseModel):
    """Schema for prediction request."""
    asset_id: str
    include_factors: bool = True


# Prediction Response Schema
class PredictionResponse(BaseModel):
    """Schema for prediction response."""
    id: str
    asset_id: str
    prediction_date: datetime
    failure_probability: float
    predicted_health: float
    risk_level: str
    recommended_action: Optional[str] = None
    confidence: Optional[float] = None
    
    # Factor breakdown
    health_degradation_factor: Optional[float] = 0.0
    active_events_factor: Optional[float] = 0.0
    measurement_anomalies_factor: Optional[float] = 0.0
    maintenance_age_factor: Optional[float] = 0.0
    
    created_at: datetime

    class Config:
        from_attributes = True


# Health Projection Schema
class HealthProjection(BaseModel):
    """Schema for health projection."""
    timeframe: str  # "7 days", "30 days", "90 days"
    predicted_health: float
    projected_probability: float
    risk_trend: str  # "improving", "stable", "degrading"


# Health Timeline Schema
class HealthTimeline(BaseModel):
    """Schema for complete health timeline."""
    current_health: float
    current_probability: float
    projections: List[HealthProjection]
    degradation_rate: float


# Risk Summary Schema
class RiskSummary(BaseModel):
    """Schema for risk summary."""
    asset_id: str
    asset_name: str
    current_health: float
    failure_probability: float
    risk_level: str
    recommended_action: Optional[str] = None


# Risk Distribution Schema
class RiskDistribution(BaseModel):
    """Schema for risk distribution across assets."""
    total_assets: int
    low_risk: int
    medium_risk: int
    high_risk: int
    critical_risk: int


# Recommendation Schema
class RecommendationResponse(BaseModel):
    """Schema for maintenance recommendation."""
    asset_id: str
    asset_name: str
    recommendation: str
    priority: str  # LOW, MEDIUM, HIGH, CRITICAL
    reason: str
    estimated_impact: Optional[str] = None


# Recommendations List Schema
class RecommendationsListResponse(BaseModel):
    """Schema for recommendations list."""
    recommendations: List[RecommendationResponse]
    total: int


# Factor Breakdown Schema
class FactorBreakdown(BaseModel):
    """Schema for prediction factor breakdown."""
    factor_name: str
    value: float
    weight: float
    contribution: float
    description: str


# Detailed Prediction Schema
class DetailedPredictionResponse(BaseModel):
    """Schema for detailed prediction with factors."""
    prediction: PredictionResponse
    factors: List[FactorBreakdown]
    health_timeline: HealthTimeline


# High Risk Assets Schema
class HighRiskAsset(BaseModel):
    """Schema for high-risk asset."""
    asset_id: str
    asset_name: str
    asset_type: str
    failure_probability: float
    predicted_health: float
    risk_level: str
    recommended_action: Optional[str] = None
    prediction_date: datetime


# High Risk Assets Response
class HighRiskAssetsResponse(BaseModel):
    """Schema for high-risk assets response."""
    assets: List[HighRiskAsset]
    total: int
    critical_count: int
    high_count: int


# Prediction History Schema
class PredictionHistoryItem(BaseModel):
    """Schema for prediction history item."""
    prediction_date: datetime
    failure_probability: float
    predicted_health: float
    risk_level: str


# Prediction History Response
class PredictionHistoryResponse(BaseModel):
    """Schema for prediction history."""
    asset_id: str
    predictions: List[PredictionHistoryItem]
    total: int
    trend: str  # "improving", "stable", "degrading"


# Failure Probability Response
class FailureProbabilityResponse(BaseModel):
    """Schema for failure probability analysis."""
    asset_id: str
    current_probability: float
    probability_7d: float
    probability_30d: float
    probability_90d: float
    confidence: float
    factors: Dict[str, float]
