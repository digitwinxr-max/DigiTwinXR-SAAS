"""Simulation Routes"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict

from .scenarios import get_scenario_manager, ScenarioStatus
from .optimizer import SimulationOptimizer

router = APIRouter(prefix="/simulation", tags=["simulation"])


class ScenarioCreate(BaseModel):
    scenario_id: str
    name: str
    description: str


class ScenarioScore(BaseModel):
    metrics: Dict[str, float]
    weights: Dict[str, float]


@router.get("/scenarios")
async def list_scenarios():
    """List scenarios."""
    manager = get_scenario_manager()
    scenarios = manager.list_scenarios()
    return {"scenarios": [{"id": s.scenario_id, "name": s.name, "status": s.status.value} for s in scenarios]}


@router.post("/scenarios")
async def create_scenario(request: ScenarioCreate):
    """Create a scenario."""
    manager = get_scenario_manager()
    from .scenarios import ScenarioParameter
    scenario = manager.create_scenario(request.scenario_id, request.name, request.description, [])
    return {"id": scenario.scenario_id, "name": scenario.name}


@router.post("/score")
async def score_scenario(request: ScenarioScore):
    """Score a scenario."""
    optimizer = SimulationOptimizer()
    score = optimizer.score_scenario(request.metrics, request.weights)
    return {"score": score}
