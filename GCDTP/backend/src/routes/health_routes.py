"""Asset health API routes."""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database.config import get_db
from ..schemas.health import (
    AssetHealthResponse,
    AssetHealthListResponse,
    HealthRecalculateResponse,
    HealthSummaryResponse,
)
from ..services.health_service import HealthService

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/summary", response_model=HealthSummaryResponse)
def get_health_summary(db: Session = Depends(get_db)):
    """Get overall health summary for all assets."""
    service = HealthService(db)
    return service.get_health_summary()


@router.get("/assets", response_model=AssetHealthListResponse)
def get_all_asset_health(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=10000),
    status: Optional[str] = Query(None, description="Filter by status (HEALTHY, DEGRADED, CRITICAL)"),
    db: Session = Depends(get_db)
):
    """Get health records for all assets."""
    service = HealthService(db)
    records, total = service.get_health_with_asset_info(skip=skip, limit=limit, status=status)
    return AssetHealthListResponse(items=records, total=total)


@router.get("/assets/{asset_id}", response_model=AssetHealthResponse)
def get_asset_health(
    asset_id: UUID,
    db: Session = Depends(get_db)
):
    """Get health record for a specific asset."""
    service = HealthService(db)
    health = service.get_health_for_asset(asset_id)
    if not health:
        raise HTTPException(status_code=404, detail="Health record not found for this asset")
    return health


@router.post("/recalculate/{asset_id}", response_model=HealthRecalculateResponse)
def recalculate_asset_health(
    asset_id: UUID,
    db: Session = Depends(get_db)
):
    """Manually recalculate health for an asset."""
    service = HealthService(db)
    return service.recalculate_health(asset_id)


@router.post("/recalculate-all")
def recalculate_all_health(db: Session = Depends(get_db)):
    """Recalculate health for all assets."""
    service = HealthService(db)
    results = service.recalculate_all_health()
    return {
        "message": f"Recalculated health for {len(results)} assets",
        "results": results,
    }