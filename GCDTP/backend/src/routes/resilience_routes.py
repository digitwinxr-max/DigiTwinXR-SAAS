"""
Resilience Routes

API endpoints for resilience analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from backend.src.database.config import get_db
from backend.src.services.resilience_service import ResilienceService
from backend.src.schemas.resilience import (
    ResilienceAnalysisResponse,
    RecommendationResponse,
    CriticalAssetResponse,
    TopCriticalAssetsResponse,
    NetworkResilienceResponse,
    AnalyzeAssetRequest,
    AnalyzeNetworkRequest,
)


router = APIRouter(prefix="/resilience", tags=["resilience"])


def get_resilience_service(db: Session = Depends(get_db)) -> ResilienceService:
    """Dependency injection for ResilienceService."""
    return ResilienceService(db)


# ============================================================================
# Analysis Endpoints
# ============================================================================

@router.post("/analyze/{asset_id}", response_model=ResilienceAnalysisResponse)
def analyze_asset(
    asset_id: str,
    request: AnalyzeAssetRequest,
    service: ResilienceService = Depends(get_resilience_service),
):
    """
    Analyze resilience for a single asset.
    
    Args:
        asset_id: UUID of the asset to analyze
        request: Analysis options
        
    Returns:
        ResilienceAnalysisResponse with scores and recommendations
    """
    try:
        asset_uuid = uuid.UUID(asset_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid asset ID format")
    
    analysis = service.analyze_asset(
        asset_id=asset_uuid,
        force_refresh=request.force_refresh,
    )
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Get recommendations
    from backend.src.models import ResilienceRecommendation
    recommendations = (
        service.db.query(ResilienceRecommendation)
        .filter(ResilienceRecommendation.analysis_id == analysis.id)
        .all()
    )
    
    return ResilienceAnalysisResponse(
        id=str(analysis.id),
        asset_id=str(analysis.asset_id),
        criticality_score=analysis.criticality_score,
        resilience_score=analysis.resilience_score,
        dependency_count=analysis.dependency_count,
        upstream_count=analysis.upstream_count,
        downstream_count=analysis.downstream_count,
        single_point_of_failure=analysis.single_point_of_failure,
        created_at=analysis.created_at,
        recommendations=[
            RecommendationResponse(
                id=str(rec.id),
                analysis_id=str(rec.analysis_id),
                recommendation_type=rec.recommendation_type,
                priority=rec.priority,
                description=rec.description,
                created_at=rec.created_at,
            )
            for rec in recommendations
        ],
    )


@router.post("/analyze-network", response_model=NetworkResilienceResponse)
def analyze_network(
    request: AnalyzeNetworkRequest,
    service: ResilienceService = Depends(get_resilience_service),
):
    """
    Analyze resilience for the entire network.
    
    Args:
        request: Analysis options
        
    Returns:
        NetworkResilienceResponse with overall metrics
    """
    analyses = service.analyze_network(force_refresh=request.force_refresh)
    
    # Get top critical assets
    critical_assets = service.get_top_critical_assets(limit=10)
    
    # Get recommendations by priority
    from backend.src.models import ResilienceRecommendation
    recommendations = service.db.query(ResilienceRecommendation).all()
    
    by_priority = {}
    for rec in recommendations:
        priority = rec.priority
        if priority not in by_priority:
            by_priority[priority] = []
        by_priority[priority].append({
            "id": str(rec.id),
            "type": rec.recommendation_type,
            "description": rec.description,
        })
    
    # Get network metrics
    metrics = service.get_network_resilience()
    
    return NetworkResilienceResponse(
        total_assets=metrics["total_assets"],
        analyzed_assets=metrics["analyzed_assets"],
        avg_criticality=metrics["avg_criticality"],
        avg_resilience=metrics["avg_resilience"],
        single_points_of_failure=metrics["single_points_of_failure"],
        high_criticality_count=metrics["high_criticality_count"],
        medium_criticality_count=metrics["medium_criticality_count"],
        low_criticality_count=metrics["low_criticality_count"],
        critical_assets=[
            CriticalAssetResponse(**asset) for asset in critical_assets
        ],
        recommendations_by_priority=by_priority,
    )


# ============================================================================
# Query Endpoints
# ============================================================================

@router.get("/asset/{asset_id}", response_model=ResilienceAnalysisResponse)
def get_asset_resilience(
    asset_id: str,
    service: ResilienceService = Depends(get_resilience_service),
):
    """
    Get existing resilience analysis for an asset.
    
    Args:
        asset_id: UUID of the asset
        
    Returns:
        ResilienceAnalysisResponse if analysis exists, 404 otherwise
    """
    try:
        asset_uuid = uuid.UUID(asset_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid asset ID format")
    
    from backend.src.models import ResilienceAnalysis, ResilienceRecommendation
    
    analysis = (
        service.db.query(ResilienceAnalysis)
        .filter(ResilienceAnalysis.asset_id == asset_uuid)
        .order_by(ResilienceAnalysis.created_at.desc())
        .first()
    )
    
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="No analysis found for this asset. Run analysis first."
        )
    
    recommendations = (
        service.db.query(ResilienceRecommendation)
        .filter(ResilienceRecommendation.analysis_id == analysis.id)
        .all()
    )
    
    return ResilienceAnalysisResponse(
        id=str(analysis.id),
        asset_id=str(analysis.asset_id),
        criticality_score=analysis.criticality_score,
        resilience_score=analysis.resilience_score,
        dependency_count=analysis.dependency_count,
        upstream_count=analysis.upstream_count,
        downstream_count=analysis.downstream_count,
        single_point_of_failure=analysis.single_point_of_failure,
        created_at=analysis.created_at,
        recommendations=[
            RecommendationResponse(
                id=str(rec.id),
                analysis_id=str(rec.analysis_id),
                recommendation_type=rec.recommendation_type,
                priority=rec.priority,
                description=rec.description,
                created_at=rec.created_at,
            )
            for rec in recommendations
        ],
    )


@router.get("/top-critical", response_model=TopCriticalAssetsResponse)
def get_top_critical_assets(
    limit: int = Query(default=10, ge=1, le=100),
    service: ResilienceService = Depends(get_resilience_service),
):
    """
    Get the most critical assets in the network.
    
    Args:
        limit: Maximum number of assets to return (default 10)
        
    Returns:
        TopCriticalAssetsResponse with ranked critical assets
    """
    critical_assets = service.get_top_critical_assets(limit=limit)
    metrics = service.get_network_resilience()
    
    return TopCriticalAssetsResponse(
        assets=[CriticalAssetResponse(**asset) for asset in critical_assets],
        total=len(critical_assets),
        network_avg_criticality=metrics["avg_criticality"],
        network_avg_resilience=metrics["avg_resilience"],
    )


@router.get("/network", response_model=NetworkResilienceResponse)
def get_network_resilience(
    service: ResilienceService = Depends(get_resilience_service),
):
    """
    Get overall network resilience metrics.
    
    Returns:
        NetworkResilienceResponse with network-wide statistics
    """
    metrics = service.get_network_resilience()
    
    if metrics["analyzed_assets"] == 0:
        raise HTTPException(
            status_code=404,
            detail="No analyses found. Run network analysis first."
        )
    
    critical_assets = service.get_top_critical_assets(limit=10)
    
    from backend.src.models import ResilienceRecommendation
    recommendations = service.db.query(ResilienceRecommendation).all()
    
    by_priority = {}
    for rec in recommendations:
        priority = rec.priority
        if priority not in by_priority:
            by_priority[priority] = []
        by_priority[priority].append({
            "id": str(rec.id),
            "type": rec.recommendation_type,
            "description": rec.description,
        })
    
    return NetworkResilienceResponse(
        total_assets=metrics["total_assets"],
        analyzed_assets=metrics["analyzed_assets"],
        avg_criticality=metrics["avg_criticality"],
        avg_resilience=metrics["avg_resilience"],
        single_points_of_failure=metrics["single_points_of_failure"],
        high_criticality_count=metrics["high_criticality_count"],
        medium_criticality_count=metrics["medium_criticality_count"],
        low_criticality_count=metrics["low_criticality_count"],
        critical_assets=[
            CriticalAssetResponse(**asset) for asset in critical_assets
        ],
        recommendations_by_priority=by_priority,
    )


@router.get("/recommendations/{analysis_id}", response_model=List[RecommendationResponse])
def get_recommendations(
    analysis_id: str,
    priority: Optional[str] = Query(default=None, description="Filter by priority"),
    service: ResilienceService = Depends(get_resilience_service),
):
    """
    Get recommendations for an analysis.
    
    Args:
        analysis_id: UUID of the analysis
        priority: Optional priority filter (LOW, MEDIUM, HIGH, CRITICAL)
        
    Returns:
        List of RecommendationResponse objects
    """
    try:
        analysis_uuid = uuid.UUID(analysis_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid analysis ID format")
    
    from backend.src.models import ResilienceRecommendation
    
    query = service.db.query(ResilienceRecommendation).filter(
        ResilienceRecommendation.analysis_id == analysis_uuid
    )
    
    if priority:
        query = query.filter(ResilienceRecommendation.priority == priority)
    
    recommendations = query.all()
    
    return [
        RecommendationResponse(
            id=str(rec.id),
            analysis_id=str(rec.analysis_id),
            recommendation_type=rec.recommendation_type,
            priority=rec.priority,
            description=rec.description,
            created_at=rec.created_at,
        )
        for rec in recommendations
    ]
