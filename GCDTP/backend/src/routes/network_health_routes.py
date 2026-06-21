"""API routes for Network Health (Dependency-Aware Health)."""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.dependency_health_service import DependencyHealthService
from ..services.health_service import HealthService
from ..schemas.asset_health_dependency import (
    HealthTreeResponse,
    HealthContributorsResponse,
    NetworkHealthSummary,
    NetworkHealthResponse,
    RecalculateResponse,
    RelationshipWeightInfo,
    RELATIONSHIP_INFO,
)

router = APIRouter(prefix="/network", tags=["network"])


def get_dep_service(db: Session = Depends(get_db)) -> DependencyHealthService:
    """Dependency for getting the dependency health service."""
    return DependencyHealthService(db)


def get_health_service(db: Session = Depends(get_db)) -> HealthService:
    """Dependency for getting the health service."""
    return HealthService(db)


@router.get("/tree/{asset_id}", response_model=HealthTreeResponse)
def get_health_tree(
    asset_id: UUID,
    max_depth: int = Query(3, ge=1, le=10, description="Maximum depth"),
    service: DependencyHealthService = Depends(get_dep_service),
):
    """Get the health tree for an asset showing dependency relationships."""
    tree = service.build_health_tree(asset_id, max_depth)
    
    if not tree:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return tree


@router.get("/contributors/{asset_id}", response_model=HealthContributorsResponse)
def get_health_contributors(
    asset_id: UUID,
    service: DependencyHealthService = Depends(get_dep_service),
):
    """Get all health contributors for an asset."""
    contributors = service.get_contributors(asset_id)
    
    if not contributors:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return contributors


@router.get("/summary", response_model=NetworkHealthResponse)
def get_network_health(
    service: DependencyHealthService = Depends(get_dep_service),
    health_service: HealthService = Depends(get_health_service),
    db: Session = Depends(get_db),
):
    """Get network-wide health summary."""
    from ..models.asset import Asset
    from ..models.asset_health import AssetHealth
    
    # Get all assets with health
    assets = health_service.get_all_health_records(limit=10000)[0]
    
    total = len(assets)
    healthy = sum(1 for a in assets if a.health_status == "HEALTHY")
    degraded = sum(1 for a in assets if a.health_status == "DEGRADED")
    critical = sum(1 for a in assets if a.health_status == "CRITICAL")
    avg_score = sum(a.health_score for a in assets) / total if total > 0 else 0
    
    total_dep_penalty = sum(a.dependency_penalty for a in assets)
    
    # Build health tree nodes for each asset
    health_nodes = []
    for health in assets:
        asset = db.query(Asset).filter(Asset.id == health.asset_id).first()
        if asset:
            contributors = service.get_dependency_health(asset.id)
            
            node = {
                "asset_id": health.asset_id,
                "asset_name": asset.name,
                "asset_type": asset.asset_type,
                "health_score": health.health_score,
                "health_status": health.health_status,
                "local_penalty": health.active_event_count * 10,
                "dependency_penalty": health.dependency_penalty,
                "total_penalty": health.active_event_count * 10 + health.dependency_penalty,
                "contributors": [],
                "children": [],
            }
            health_nodes.append(node)
    
    return NetworkHealthResponse(
        summary=NetworkHealthSummary(
            total_assets=total,
            healthy_count=healthy,
            degraded_count=degraded,
            critical_count=critical,
            average_health_score=avg_score,
            total_dependency_penalties=total_dep_penalty,
        ),
        assets=health_nodes,
    )


@router.post("/recalculate-network", response_model=RecalculateResponse)
def recalculate_network_health(
    service: DependencyHealthService = Depends(get_dep_service),
    health_service: HealthService = Depends(get_health_service),
):
    """Recalculate the entire dependency health network."""
    # Recalculate dependency penalties
    assets_recalculated, penalties_updated = service.recalculate_network_health()
    
    # Recalculate all health records
    health_service.recalculate_all_health(recalculate_network=False)
    
    return RecalculateResponse(
        assets_recalculated=assets_recalculated,
        total_penalties_updated=penalties_updated,
        message=f"Network health recalculated for {assets_recalculated} assets",
    )


@router.get("/weights")
def get_relationship_weights():
    """Get relationship weight information."""
    return [
        {
            "type": rel_type.value,
            "weight": info["weight"],
            "description": info["description"],
        }
        for rel_type, info in RELATIONSHIP_INFO.items()
    ]


@router.get("/decay")
def get_depth_decay():
    """Get depth decay information."""
    return {
        "1": 1.0,
        "2": 0.5,
        "3": 0.25,
        "description": "Depth decay reduces penalty impact for assets further from the source",
    }