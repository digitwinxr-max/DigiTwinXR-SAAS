"""
Root Cause Analysis Routes

FastAPI routes for Root Cause Analysis Engine.
READ ONLY - NO automation, NO work orders.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from ..schemas.root_cause import (
    RootCauseResponse,
    CauseFactorSchema,
    CauseChainSchema,
    CauseChainResponse,
    ConfidenceResponse,
    HighConfidenceAnalysis,
    AnalysisRequest,
    AnalysisResponse,
    RankedFactorResponse
)
from ..services.root_cause_service import root_cause_service


router = APIRouter(prefix="/root-cause", tags=["root-cause"])


@router.post("/analyze/{asset_id}", response_model=RootCauseResponse)
async def analyze_asset(
    asset_id: str,
    analysis_type: str = Query("failure", description="Type of analysis"),
    event_id: Optional[str] = Query(None, description="Specific event ID"),
    time_window_hours: int = Query(24, ge=1, le=720, description="Analysis time window")
):
    """
    Analyze an asset for root cause.
    
    READ ONLY operation - explains WHY failures occurred.
    NO automation, NO work order creation.
    """
    from ..models.root_cause_analysis import AnalysisType
    
    # Convert analysis type
    try:
        a_type = AnalysisType(analysis_type)
    except ValueError:
        a_type = AnalysisType.FAILURE
    
    # Run analysis
    analysis = root_cause_service.analyze_asset(
        asset_id=asset_id,
        analysis_type=a_type,
        time_window_hours=time_window_hours
    )
    
    # Get factors and chains
    factors = root_cause_service.get_factors_for_analysis(analysis.id)
    chains = root_cause_service.get_chains_for_analysis(analysis.id)
    
    return RootCauseResponse(
        id=analysis.id,
        asset_id=analysis.asset_id,
        event_id=analysis.event_id,
        analysis_type=analysis.analysis_type.value if hasattr(analysis.analysis_type, 'value') else analysis.analysis_type,
        probable_cause=analysis.probable_cause,
        confidence=analysis.confidence,
        summary=analysis.summary,
        impacted_assets=analysis.impacted_assets,
        root_assets=analysis.root_assets,
        created_at=analysis.created_at,
        factors=[
            CauseFactorSchema(
                id=f.id,
                analysis_id=f.analysis_id,
                factor_type=f.factor_type.value if hasattr(f.factor_type, 'value') else f.factor_type,
                reference_id=f.reference_id,
                weight=f.weight,
                description=f.description,
                evidence=f.evidence,
                created_at=f.created_at
            )
            for f in factors
        ],
        chains=[
            CauseChainSchema(
                id=c.id,
                analysis_id=c.analysis_id,
                depth=c.depth,
                source_asset_id=c.source_asset_id,
                target_asset_id=c.target_asset_id,
                relationship_type=c.relationship_type,
                description=c.description,
                propagation_time_seconds=c.propagation_time_seconds,
                created_at=c.created_at
            )
            for c in chains
        ]
    )


@router.get("/{analysis_id}", response_model=RootCauseResponse)
async def get_analysis(analysis_id: str):
    """
    Get analysis by ID.
    """
    analysis = root_cause_service.get_analysis(analysis_id)
    
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis {analysis_id} not found"
        )
    
    factors = root_cause_service.get_factors_for_analysis(analysis_id)
    chains = root_cause_service.get_chains_for_analysis(analysis_id)
    
    return RootCauseResponse(
        id=analysis.id,
        asset_id=analysis.asset_id,
        event_id=analysis.event_id,
        analysis_type=analysis.analysis_type.value if hasattr(analysis.analysis_type, 'value') else analysis.analysis_type,
        probable_cause=analysis.probable_cause,
        confidence=analysis.confidence,
        summary=analysis.summary,
        impacted_assets=analysis.impacted_assets,
        root_assets=analysis.root_assets,
        created_at=analysis.created_at,
        factors=[
            CauseFactorSchema(
                id=f.id,
                analysis_id=f.analysis_id,
                factor_type=f.factor_type.value if hasattr(f.factor_type, 'value') else f.factor_type,
                reference_id=f.reference_id,
                weight=f.weight,
                description=f.description,
                evidence=f.evidence,
                created_at=f.created_at
            )
            for f in factors
        ],
        chains=[
            CauseChainSchema(
                id=c.id,
                analysis_id=c.analysis_id,
                depth=c.depth,
                source_asset_id=c.source_asset_id,
                target_asset_id=c.target_asset_id,
                relationship_type=c.relationship_type,
                description=c.description,
                propagation_time_seconds=c.propagation_time_seconds,
                created_at=c.created_at
            )
            for c in chains
        ]
    )


@router.get("/asset/{asset_id}")
async def get_analyses_for_asset(
    asset_id: str,
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get all analyses for an asset.
    """
    analyses = root_cause_service.get_analyses_for_asset(asset_id)
    
    return {
        "asset_id": asset_id,
        "analyses": analyses[-limit:],
        "total": len(analyses)
    }


@router.get("/event/{event_id}", response_model=RootCauseResponse)
async def analyze_event(
    event_id: str,
    asset_id: str = Query(..., description="Asset ID")
):
    """
    Analyze a specific event for root cause.
    """
    analysis = root_cause_service.analyze_event(event_id, asset_id)
    
    factors = root_cause_service.get_factors_for_analysis(analysis.id)
    chains = root_cause_service.get_chains_for_analysis(analysis.id)
    
    return RootCauseResponse(
        id=analysis.id,
        asset_id=analysis.asset_id,
        event_id=analysis.event_id,
        analysis_type=analysis.analysis_type.value if hasattr(analysis.analysis_type, 'value') else analysis.analysis_type,
        probable_cause=analysis.probable_cause,
        confidence=analysis.confidence,
        summary=analysis.summary,
        impacted_assets=analysis.impacted_assets,
        root_assets=analysis.root_assets,
        created_at=analysis.created_at,
        factors=[
            CauseFactorSchema(
                id=f.id,
                analysis_id=f.analysis_id,
                factor_type=f.factor_type.value if hasattr(f.factor_type, 'value') else f.factor_type,
                reference_id=f.reference_id,
                weight=f.weight,
                description=f.description,
                evidence=f.evidence,
                created_at=f.created_at
            )
            for f in factors
        ],
        chains=[
            CauseChainSchema(
                id=c.id,
                analysis_id=c.analysis_id,
                depth=c.depth,
                source_asset_id=c.source_asset_id,
                target_asset_id=c.target_asset_id,
                relationship_type=c.relationship_type,
                description=c.description,
                propagation_time_seconds=c.propagation_time_seconds,
                created_at=c.created_at
            )
            for c in chains
        ]
    )


@router.get("/factors/{analysis_id}")
async def get_factors(analysis_id: str):
    """
    Get factors for an analysis.
    """
    factors = root_cause_service.get_factors_for_analysis(analysis_id)
    ranked = root_cause_service.rank_factors(analysis_id)
    
    return {
        "analysis_id": analysis_id,
        "factors": factors,
        "ranked_factors": ranked,
        "total": len(factors)
    }


@router.get("/chains/{analysis_id}")
async def get_chains(analysis_id: str):
    """
    Get causal chains for an analysis.
    """
    chains = root_cause_service.get_chains_for_analysis(analysis_id)
    
    chain_responses = [
        CauseChainResponse(
            id=c.id,
            depth=c.depth,
            source_asset_id=c.source_asset_id,
            target_asset_id=c.target_asset_id,
            relationship_type=c.relationship_type,
            description=c.description,
            propagation_time_seconds=c.propagation_time_seconds
        )
        for c in chains
    ]
    
    return {
        "analysis_id": analysis_id,
        "chains": chain_responses,
        "total": len(chains)
    }


@router.get("/high-confidence")
async def get_high_confidence(
    threshold: float = Query(0.7, ge=0, le=1)
):
    """
    Get high confidence analyses.
    """
    analyses = root_cause_service.get_high_confidence_analyses(threshold)
    
    return {
        "threshold": threshold,
        "analyses": analyses,
        "total": len(analyses)
    }


@router.get("/history")
async def get_history(
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get analysis history.
    """
    from ..models.root_cause_analysis import RootCauseAnalysis
    
    all_analyses = sorted(
        root_cause_service._analyses.values(),
        key=lambda a: a.created_at,
        reverse=True
    )
    
    return {
        "analyses": all_analyses[:limit],
        "total": len(all_analyses)
    }
