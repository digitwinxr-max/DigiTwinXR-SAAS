"""
Predictive Maintenance Routes

FastAPI routes for Predictive Maintenance Engine.
Deterministic predictions only - NO ML/AI.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from ..schemas.predictive_maintenance import (
    PredictionRequest,
    PredictionResponse,
    HealthTimeline,
    RiskSummary,
    RiskDistribution,
    RecommendationsListResponse,
    RecommendationResponse,
    FactorBreakdown,
    DetailedPredictionResponse,
    HighRiskAssetsResponse,
    HighRiskAsset,
    PredictionHistoryResponse,
    PredictionHistoryItem,
    FailureProbabilityResponse
)
from ..services.predictive_maintenance_service import predictive_maintenance_service


router = APIRouter(prefix="/predictive", tags=["predictive"])


@router.post("/run/{asset_id}", response_model=PredictionResponse)
async def run_prediction(
    asset_id: str,
    current_health: float = Query(100.0, ge=0, le=100, description="Current health score"),
    health_trend: float = Query(0.0, description="Daily health trend"),
    active_events: int = Query(0, ge=0, description="Number of active events"),
    measurement_anomalies: int = Query(0, ge=0, description="Number of measurement anomalies"),
    days_since_maintenance: int = Query(0, ge=0, description="Days since last maintenance"),
    asset_type: str = Query("generic", description="Asset type"),
    data_quality_score: float = Query(0.8, ge=0, le=1, description="Data quality score")
):
    """
    Run prediction for an asset.
    
    Generates deterministic failure probability prediction.
    NO ML/AI - pure mathematical calculation.
    """
    prediction = predictive_maintenance_service.run_prediction(
        asset_id=asset_id,
        current_health=current_health,
        health_trend=health_trend,
        active_events=active_events,
        measurement_anomalies=measurement_anomalies,
        days_since_maintenance=days_since_maintenance,
        asset_type=asset_type,
        data_quality_score=data_quality_score
    )
    
    return PredictionResponse(
        id=prediction.id,
        asset_id=prediction.asset_id,
        prediction_date=prediction.prediction_date,
        failure_probability=prediction.failure_probability,
        predicted_health=prediction.predicted_health,
        risk_level=prediction.risk_level.value,
        recommended_action=prediction.recommended_action,
        confidence=prediction.confidence,
        health_degradation_factor=prediction.health_degradation_factor,
        active_events_factor=prediction.active_events_factor,
        measurement_anomalies_factor=prediction.measurement_anomalies_factor,
        maintenance_age_factor=prediction.maintenance_age_factor,
        created_at=prediction.created_at
    )


@router.get("/{asset_id}", response_model=PredictionResponse)
async def get_prediction(asset_id: str):
    """
    Get latest prediction for an asset.
    """
    prediction = predictive_maintenance_service.get_prediction(asset_id)
    
    if not prediction:
        raise HTTPException(
            status_code=404,
            detail=f"No prediction found for asset {asset_id}"
        )
    
    return PredictionResponse(
        id=prediction.id,
        asset_id=prediction.asset_id,
        prediction_date=prediction.prediction_date,
        failure_probability=prediction.failure_probability,
        predicted_health=prediction.predicted_health,
        risk_level=prediction.risk_level.value,
        recommended_action=prediction.recommended_action,
        confidence=prediction.confidence,
        health_degradation_factor=prediction.health_degradation_factor,
        active_events_factor=prediction.active_events_factor,
        measurement_anomalies_factor=prediction.measurement_anomalies_factor,
        maintenance_age_factor=prediction.maintenance_age_factor,
        created_at=prediction.created_at
    )


@router.get("/history/{asset_id}", response_model=PredictionHistoryResponse)
async def get_prediction_history(
    asset_id: str,
    limit: int = Query(30, ge=1, le=365, description="Number of historical predictions")
):
    """
    Get prediction history for an asset.
    """
    predictions = predictive_maintenance_service.get_prediction_history(asset_id)
    
    history_items = [
        PredictionHistoryItem(
            prediction_date=p.prediction_date,
            failure_probability=p.failure_probability,
            predicted_health=p.predicted_health,
            risk_level=p.risk_level.value
        )
        for p in predictions[-limit:]
    ]
    
    # Determine trend
    trend = "stable"
    if len(history_items) >= 2:
        if history_items[-1].failure_probability > history_items[0].failure_probability * 1.1:
            trend = "degrading"
        elif history_items[-1].failure_probability < history_items[0].failure_probability * 0.9:
            trend = "improving"
    
    return PredictionHistoryResponse(
        asset_id=asset_id,
        predictions=history_items,
        total=len(history_items),
        trend=trend
    )


@router.get("/high-risk", response_model=HighRiskAssetsResponse)
async def get_high_risk_assets(
    limit: int = Query(10, ge=1, le=100, description="Maximum number of assets to return")
):
    """
    Get high-risk assets (HIGH or CRITICAL risk level).
    """
    assets = predictive_maintenance_service.get_high_risk_assets(limit=limit)
    
    high_risk_assets = [
        HighRiskAsset(
            asset_id=a["asset_id"],
            asset_name=f"Asset {a['asset_id'][:8]}",
            asset_type="unknown",
            failure_probability=a["failure_probability"],
            predicted_health=a["predicted_health"],
            risk_level=a["risk_level"],
            recommended_action=a["recommended_action"],
            prediction_date=a["prediction_date"]
        )
        for a in assets
    ]
    
    critical_count = sum(1 for a in assets if a["risk_level"] == "CRITICAL")
    high_count = sum(1 for a in assets if a["risk_level"] == "HIGH")
    
    return HighRiskAssetsResponse(
        assets=high_risk_assets,
        total=len(high_risk_assets),
        critical_count=critical_count,
        high_count=high_count
    )


@router.get("/recommendations", response_model=RecommendationsListResponse)
async def get_recommendations(
    limit: int = Query(20, ge=1, le=100, description="Maximum recommendations to return")
):
    """
    Get maintenance recommendations for all assets.
    """
    recs = predictive_maintenance_service.get_recommendations(limit=limit)
    
    recommendations = [
        RecommendationResponse(
            asset_id=r["asset_id"],
            asset_name=f"Asset {r['asset_id'][:8]}",
            recommendation=r["recommendation"],
            priority=r["priority"],
            reason=r["reason"]
        )
        for r in recs
    ]
    
    return RecommendationsListResponse(
        recommendations=recommendations,
        total=len(recommendations)
    )


@router.get("/timeline/{asset_id}", response_model=HealthTimeline)
async def get_health_timeline(
    asset_id: str,
    current_health: float = Query(100.0, ge=0, le=100),
    health_trend: float = Query(0.0)
):
    """
    Get health timeline with projections.
    """
    return predictive_maintenance_service.get_health_timeline(
        current_health=current_health,
        health_trend=health_trend
    )


@router.get("/probability/{asset_id}", response_model=FailureProbabilityResponse)
async def get_failure_probability(
    asset_id: str,
    current_health: float = Query(100.0, ge=0, le=100),
    health_trend: float = Query(0.0),
    active_events: int = Query(0, ge=0),
    measurement_anomalies: int = Query(0, ge=0),
    days_since_maintenance: int = Query(0, ge=0)
):
    """
    Get detailed failure probability analysis.
    """
    # Get current prediction
    prediction = predictive_maintenance_service.get_prediction(asset_id)
    
    # Calculate current probability
    probability, confidence, factors = predictive_maintenance_service.calculate_failure_probability(
        current_health=current_health,
        health_trend=health_trend,
        active_events=active_events,
        measurement_anomalies=measurement_anomalies,
        days_since_maintenance=days_since_maintenance
    )
    
    # Calculate projections
    probability_7d = predictive_maintenance_service._calculate_projected_probability(
        current_health, health_trend, 7
    )
    probability_30d = predictive_maintenance_service._calculate_projected_probability(
        current_health, health_trend, 30
    )
    probability_90d = predictive_maintenance_service._calculate_projected_probability(
        current_health, health_trend, 90
    )
    
    return FailureProbabilityResponse(
        asset_id=asset_id,
        current_probability=probability,
        probability_7d=probability_7d,
        probability_30d=probability_30d,
        probability_90d=probability_90d,
        confidence=confidence,
        factors=factors
    )
