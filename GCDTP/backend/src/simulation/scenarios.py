"""
Simulation Scenarios

Scenario definitions for simulation.
NO automatic execution.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ScenarioStatus(str, Enum):
    """Scenario status."""
    DRAFT = "draft"
    VALIDATED = "validated"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ScenarioParameter:
    """Scenario parameter."""
    name: str
    value: Any
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None


@dataclass
class Scenario:
    """Simulation scenario."""
    scenario_id: str
    name: str
    description: str
    parameters: List[ScenarioParameter]
    status: ScenarioStatus
    created_at: datetime
    updated_at: datetime


@dataclass
class SimulationResult:
    """Simulation result."""
    result_id: str
    scenario_id: str
    timestamp: datetime
    metrics: Dict[str, float]
    summary: str
    requires_review: bool = True


class ScenarioManager:
    """
    Scenario management.
    
    Features:
    - Scenario definitions
    - Parameter management
    - Ranking and scoring
    
    LIMITATIONS:
    - NO automatic execution
    """
    
    def __init__(self):
        self._scenarios: Dict[str, Scenario] = {}
        self._results: Dict[str, SimulationResult] = {}
    
    def create_scenario(
        self,
        scenario_id: str,
        name: str,
        description: str,
        parameters: List[ScenarioParameter]
    ) -> Scenario:
        """Create a scenario."""
        scenario = Scenario(
            scenario_id=scenario_id,
            name=name,
            description=description,
            parameters=parameters,
            status=ScenarioStatus.DRAFT,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self._scenarios[scenario_id] = scenario
        return scenario
    
    def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """Get scenario by ID."""
        return self._scenarios.get(scenario_id)
    
    def list_scenarios(self, status: Optional[ScenarioStatus] = None) -> List[Scenario]:
        """List scenarios."""
        scenarios = list(self._scenarios.values())
        if status:
            scenarios = [s for s in scenarios if s.status == status]
        return scenarios
    
    def add_result(self, result: SimulationResult) -> SimulationResult:
        """Add simulation result."""
        self._results[result.result_id] = result
        return result
    
    def rank_scenarios(
        self,
        results: List[SimulationResult]
    ) -> List[tuple]:
        """Rank scenarios by metrics."""
        scored = []
        for result in results:
            total = sum(result.metrics.values())
            scored.append((result, total))
        return sorted(scored, key=lambda x: x[1], reverse=True)


_manager: Optional[ScenarioManager] = None


def get_scenario_manager() -> ScenarioManager:
    """Get or create scenario manager singleton."""
    global _manager
    if _manager is None:
        _manager = ScenarioManager()
    return _manager
