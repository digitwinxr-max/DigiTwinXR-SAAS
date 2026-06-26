"""API routes for Recovery Simulation Engine."""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database.config import get_db
from ..services.recovery_simulation_service import RecoverySimulationService
from ..schemas.recovery import (
    RecoverySimulationCreate,
    RecoverySimulationResponse,
    RecoverySimulationListResponse,
    RecoveryResultResponse,
    RecoveryResultListResponse,
    RunRecoveryResponse,
)

router = APIRouter(prefix="/recovery", tags=["recovery"])


def get_service(db: Session = Depends(get_db)) -> RecoverySimulationService:
    """Dependency for getting the recovery simulation service."""
    return RecoverySimulationService(db)


@router.post("", response_model=RecoverySimulationResponse, status_code=201)
def create_recovery(
    data: RecoverySimulationCreate,
    service: RecoverySimulationService = Depends(get_service),
):
    """Create a new recovery simulation."""
    recovery = service.create_recovery(data)
    return RecoverySimulationResponse(
        id=recovery.id,
        scenario_id=recovery.scenario_id,
        strategy_name=recovery.strategy_name,
        recovery_type=recovery.recovery_type.value,
        estimated_duration_minutes=recovery.estimated_duration_minutes,
        recovery_order=recovery.recovery_order,
        created_at=recovery.created_at,
        result_count=len(recovery.results) if recovery.results else 0,
    )


@router.get("", response_model=RecoverySimulationListResponse)
def list_recoveries(
    scenario_id: Optional[UUID] = Query(None, description="Filter by scenario"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: RecoverySimulationService = Depends(get_service),
):
    """List all recovery simulations."""
    recoveries, total = service.list_recoveries(
        scenario_id=scenario_id,
        skip=skip,
        limit=limit,
    )
    
    items = [
        RecoverySimulationResponse(
            id=r.id,
            scenario_id=r.scenario_id,
            strategy_name=r.strategy_name,
            recovery_type=r.recovery_type.value,
            estimated_duration_minutes=r.estimated_duration_minutes,
            recovery_order=r.recovery_order,
            created_at=r.created_at,
            result_count=len(r.results) if r.results else 0,
        )
        for r in recoveries
    ]
    
    return RecoverySimulationListResponse(items=items, total=total)


@router.get("/{recovery_id}", response_model=RecoverySimulationResponse)
def get_recovery(
    recovery_id: UUID,
    service: RecoverySimulationService = Depends(get_service),
):
    """Get a specific recovery simulation."""
    recovery = service.get_recovery(recovery_id)
    if not recovery:
        raise HTTPException(status_code=404, detail="Recovery not found")
    
    return RecoverySimulationResponse(
        id=recovery.id,
        scenario_id=recovery.scenario_id,
        strategy_name=recovery.strategy_name,
        recovery_type=recovery.recovery_type.value,
        estimated_duration_minutes=recovery.estimated_duration_minutes,
        recovery_order=recovery.recovery_order,
        created_at=recovery.created_at,
        result_count=len(recovery.results) if recovery.results else 0,
    )


@router.delete("/{recovery_id}")
def delete_recovery(
    recovery_id: UUID,
    service: RecoverySimulationService = Depends(get_service),
):
    """Delete a recovery simulation and its results."""
    deleted = service.delete_recovery(recovery_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Recovery not found")
    return {"message": "Recovery deleted"}


@router.post("/{recovery_id}/run", response_model=RunRecoveryResponse)
def run_recovery(
    recovery_id: UUID,
    service: RecoverySimulationService = Depends(get_service),
):
    """Run a recovery simulation.
    
    This executes the recovery simulation and stores results, but does NOT
    modify live data (events, propagated_events, or asset_health).
    """
    try:
        result = service.run_recovery(recovery_id)
        return RunRecoveryResponse(
            recovery_id=result["recovery_id"],
            status="completed",
            total_assets=result["total_assets"],
            assets_recovered=result["assets_recovered"],
            average_improvement=result["average_improvement"],
            message="Recovery simulation completed successfully",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{recovery_id}/results", response_model=RecoveryResultListResponse)
def get_recovery_results(
    recovery_id: UUID,
    service: RecoverySimulationService = Depends(get_service),
):
    """Get results for a recovery simulation."""
    recovery = service.get_recovery(recovery_id)
    if not recovery:
        raise HTTPException(status_code=404, detail="Recovery not found")
    
    results = service.get_recovery_results(recovery_id)
    
    items = [
        RecoveryResultResponse(
            id=r["id"],
            recovery_simulation_id=r["recovery_simulation_id"],
            asset_id=r["asset_id"],
            before_health=r["before_health"],
            after_health=r["after_health"],
            improvement=r["improvement"],
            recovery_depth=r["recovery_depth"],
            remaining_risk=r["remaining_risk"],
            created_at=r["created_at"],
            asset_name=r["asset_name"],
            asset_type=r.get("asset_type"),
        )
        for r in results
    ]
    
    return RecoveryResultListResponse(items=items, total=len(items))


@router.get("/{recovery_id}/tree")
def get_recovery_tree(
    recovery_id: UUID,
    service: RecoverySimulationService = Depends(get_service),
):
    """Get recovery tree for a recovery simulation."""
    tree = service.get_recovery_tree(recovery_id)
    if not tree:
        raise HTTPException(status_code=404, detail="Recovery not found")
    return tree


@router.get("/{recovery_id}/compare")
def compare_recovery(
    recovery_id: UUID,
    service: RecoverySimulationService = Depends(get_service),
):
    """Compare recovery results (before vs after)."""
    try:
        comparison = service.compare_recovery(recovery_id)
        return comparison
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))