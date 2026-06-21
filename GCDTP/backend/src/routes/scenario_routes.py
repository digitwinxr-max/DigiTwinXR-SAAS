"""API routes for Scenario Simulation Engine."""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database.config import get_db
from ..services.simulation_service import SimulationService
from ..schemas.scenario import (
    ScenarioCreate,
    ScenarioUpdate,
    ScenarioResponse,
    ScenarioListResponse,
    ScenarioResultResponse,
    ScenarioResultListResponse,
    SimulationResults,
    SimulationResultsResponse,
    SimulationStats,
    ScenarioComparison,
    ScenarioSummary,
    RunSimulationResponse,
    ImpactNode,
)

router = APIRouter(prefix="/scenarios", tags=["simulation"])


def get_service(db: Session = Depends(get_db)) -> SimulationService:
    """Dependency for getting the simulation service."""
    return SimulationService(db)


@router.post("", response_model=ScenarioResponse, status_code=201)
def create_scenario(
    data: ScenarioCreate,
    service: SimulationService = Depends(get_service),
):
    """Create a new simulation scenario."""
    scenario = service.create_scenario(data)
    return ScenarioResponse(
        id=scenario.id,
        name=scenario.name,
        description=scenario.description,
        scenario_type=scenario.scenario_type.value,
        root_asset_id=scenario.root_asset_id,
        severity=scenario.severity,
        status=scenario.status.value,
        created_at=scenario.created_at,
        result_count=len(scenario.results) if scenario.results else 0,
    )


@router.get("", response_model=ScenarioListResponse)
def list_scenarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, description="Filter by status"),
    scenario_type: Optional[str] = Query(None, description="Filter by type"),
    service: SimulationService = Depends(get_service),
):
    """List all scenarios."""
    scenarios, total = service.list_scenarios(
        skip=skip,
        limit=limit,
        status=status,
        scenario_type=scenario_type,
    )
    
    items = [
        ScenarioResponse(
            id=s.id,
            name=s.name,
            description=s.description,
            scenario_type=s.scenario_type.value,
            root_asset_id=s.root_asset_id,
            severity=s.severity,
            status=s.status.value,
            created_at=s.created_at,
            result_count=len(s.results) if s.results else 0,
        )
        for s in scenarios
    ]
    
    return ScenarioListResponse(items=items, total=total)


@router.get("/{scenario_id}", response_model=ScenarioResponse)
def get_scenario(
    scenario_id: UUID,
    service: SimulationService = Depends(get_service),
):
    """Get a specific scenario."""
    scenario = service.get_scenario(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    return ScenarioResponse(
        id=scenario.id,
        name=scenario.name,
        description=scenario.description,
        scenario_type=scenario.scenario_type.value,
        root_asset_id=scenario.root_asset_id,
        severity=scenario.severity,
        status=scenario.status.value,
        created_at=scenario.created_at,
        result_count=len(scenario.results) if scenario.results else 0,
    )


@router.delete("/{scenario_id}")
def delete_scenario(
    scenario_id: UUID,
    service: SimulationService = Depends(get_service),
):
    """Delete a scenario and its results."""
    deleted = service.delete_scenario(scenario_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return {"message": "Scenario deleted"}


@router.post("/{scenario_id}/run", response_model=RunSimulationResponse)
def run_simulation(
    scenario_id: UUID,
    service: SimulationService = Depends(get_service),
):
    """Run a simulation for a scenario.
    
    This executes the simulation and stores results, but does NOT
    modify live data (events, propagated_events, or asset_health).
    """
    try:
        result = service.run_simulation(scenario_id)
        return RunSimulationResponse(
            scenario_id=result["scenario_id"],
            status="completed",
            total_affected=result["total_affected"],
            max_depth=result["max_depth"],
            worst_health=result["worst_health"],
            average_health=result["average_health"],
            message="Simulation completed successfully",
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{scenario_id}/results", response_model=ScenarioResultListResponse)
def get_scenario_results(
    scenario_id: UUID,
    service: SimulationService = Depends(get_service),
):
    """Get results for a scenario."""
    scenario = service.get_scenario(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    results = service.get_scenario_results(scenario_id)
    
    items = [
        ScenarioResultResponse(
            id=r["id"],
            scenario_id=r["scenario_id"],
            asset_id=r["asset_id"],
            predicted_health=r["predicted_health"],
            current_health=r["current_health"],
            delta_health=r["delta_health"],
            propagation_depth=r["propagation_depth"],
            relationship_path=r["relationship_path"],
            created_at=r["created_at"],
            asset_name=r["asset_name"],
            asset_type=r.get("asset_type"),
        )
        for r in results
    ]
    
    return ScenarioResultListResponse(items=items, total=len(items))


@router.get("/{scenario_id}/impact-tree")
def get_impact_tree(
    scenario_id: UUID,
    service: SimulationService = Depends(get_service),
):
    """Get impact tree for a scenario."""
    tree = service.get_impact_tree(scenario_id)
    if not tree:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return tree


@router.get("/{scenario_id}/compare")
def compare_scenario(
    scenario_id: UUID,
    service: SimulationService = Depends(get_service),
):
    """Compare simulation results with live health."""
    try:
        comparison = service.compare_with_live_health(scenario_id)
        return comparison
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{scenario_id}/summary")
def get_scenario_summary(
    scenario_id: UUID,
    service: SimulationService = Depends(get_service),
):
    """Get a summary of a scenario."""
    summary = service.get_scenario_summary(scenario_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return summary