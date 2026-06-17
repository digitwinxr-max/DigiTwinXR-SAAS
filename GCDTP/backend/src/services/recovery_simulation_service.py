"""Recovery Simulation Service for Recovery Simulation Engine.

This service simulates recovery strategies for failure scenarios.
Recovery simulations are completely isolated from live data.
"""
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.orm import Session

from ..models.asset import Asset
from ..models.asset_relationship import AssetRelationship, RelationshipType
from ..models.asset_health import AssetHealth
from ..models.scenario import Scenario
from ..models.scenario_result import ScenarioResult
from ..models.recovery_simulation import RecoverySimulation, RecoveryType, RiskLevel
from ..models.recovery_result import RecoveryResult
from ..schemas.recovery import (
    RecoverySimulationCreate,
    RecoveryType as SchemaRecoveryType,
    RiskLevel as SchemaRiskLevel,
    calculate_risk_level,
)


# Recovery restoration values
RECOVERY_VALUES = {
    SchemaRecoveryType.MANUAL: 20,
    SchemaRecoveryType.AUTOMATIC: 30,
    SchemaRecoveryType.STAGED: 15,  # per depth
    SchemaRecoveryType.REROUTE: 25,  # base value
}


# Maximum health
MAX_HEALTH = 100
MIN_HEALTH = 0


class RecoverySimulationService:
    """Service for running recovery simulations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_recovery(self, data: RecoverySimulationCreate) -> RecoverySimulation:
        """Create a new recovery simulation.
        
        Args:
            data: Recovery simulation creation data
            
        Returns:
            Created recovery simulation
        """
        recovery = RecoverySimulation(
            scenario_id=data.scenario_id,
            strategy_name=data.strategy_name,
            recovery_type=RecoveryType(data.recovery_type.value),
            estimated_duration_minutes=data.estimated_duration_minutes,
            recovery_order=data.recovery_order,
        )
        self.db.add(recovery)
        self.db.commit()
        self.db.refresh(recovery)
        return recovery
    
    def get_recovery(self, recovery_id: UUID) -> Optional[RecoverySimulation]:
        """Get a recovery simulation by ID.
        
        Args:
            recovery_id: Recovery simulation ID
            
        Returns:
            RecoverySimulation or None
        """
        return self.db.query(RecoverySimulation).filter(
            RecoverySimulation.id == recovery_id
        ).first()
    
    def list_recoveries(
        self,
        scenario_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[RecoverySimulation], int]:
        """List all recovery simulations.
        
        Args:
            scenario_id: Optional filter by scenario
            skip: Number to skip
            limit: Maximum to return
            
        Returns:
            Tuple of (recoveries, total count)
        """
        query = self.db.query(RecoverySimulation)
        
        if scenario_id:
            query = query.filter(RecoverySimulation.scenario_id == scenario_id)
        
        total = query.count()
        recoveries = query.order_by(RecoverySimulation.created_at.desc()).offset(skip).limit(limit).all()
        
        return recoveries, total
    
    def delete_recovery(self, recovery_id: UUID) -> bool:
        """Delete a recovery simulation and its results.
        
        Args:
            recovery_id: Recovery simulation ID
            
        Returns:
            True if deleted
        """
        recovery = self.get_recovery(recovery_id)
        if not recovery:
            return False
        
        self.db.delete(recovery)
        self.db.commit()
        return True
    
    def run_recovery(self, recovery_id: UUID) -> Dict[str, Any]:
        """Run a recovery simulation.
        
        This simulates the recovery and stores results, but does NOT
        modify live data (events, propagated_events, or asset_health).
        
        Args:
            recovery_id: Recovery simulation ID
            
        Returns:
            Recovery results
        """
        recovery = self.get_recovery(recovery_id)
        if not recovery:
            raise ValueError(f"Recovery {recovery_id} not found")
        
        # Get the parent scenario
        scenario = self.db.query(Scenario).filter(
            Scenario.id == recovery.scenario_id
        ).first()
        
        if not scenario:
            raise ValueError(f"Scenario {recovery.scenario_id} not found")
        
        # Get scenario results (predicted health before recovery)
        scenario_results = self.db.query(ScenarioResult).filter(
            ScenarioResult.scenario_id == scenario.id
        ).all()
        
        if not scenario_results:
            raise ValueError("No scenario results found. Run the scenario first.")
        
        # Calculate recovery based on strategy
        recovery_results = self._calculate_recovery(
            recovery=recovery,
            scenario_results=scenario_results,
        )
        
        # Store results
        stored_results = self._store_results(
            recovery_id=recovery_id,
            results=recovery_results,
        )
        
        # Calculate stats
        stats = self._calculate_stats(stored_results)
        
        return {
            "recovery_id": recovery_id,
            "total_assets": len(stored_results),
            "assets_recovered": stats["assets_recovered"],
            "average_improvement": stats["average_improvement"],
            "results": stored_results,
        }
    
    def _calculate_recovery(
        self,
        recovery: RecoverySimulation,
        scenario_results: List[ScenarioResult],
    ) -> List[Dict[str, Any]]:
        """Calculate recovery results based on strategy.
        
        Args:
            recovery: Recovery simulation
            scenario_results: Scenario results (before recovery)
            
        Returns:
            List of recovery result dictionaries
        """
        results = []
        recovery_type = SchemaRecoveryType(recovery.recovery_type.value)
        
        for result in scenario_results:
            before_health = result.predicted_health
            
            # Calculate after health based on recovery type
            after_health = self._calculate_after_health(
                before_health=before_health,
                recovery_type=recovery_type,
                depth=result.propagation_depth,
                asset_id=result.asset_id,
            )
            
            # Calculate improvement
            improvement = after_health - before_health
            
            # Calculate remaining risk
            remaining_risk = calculate_risk_level(after_health)
            
            results.append({
                "asset_id": result.asset_id,
                "before_health": before_health,
                "after_health": after_health,
                "improvement": improvement,
                "recovery_depth": result.propagation_depth,
                "remaining_risk": remaining_risk.value,
            })
        
        return results
    
    def _calculate_after_health(
        self,
        before_health: float,
        recovery_type: SchemaRecoveryType,
        depth: int,
        asset_id: UUID,
    ) -> float:
        """Calculate health after recovery based on strategy.
        
        Args:
            before_health: Health before recovery
            recovery_type: Type of recovery
            depth: Propagation depth
            asset_id: Asset ID
            
        Returns:
            Health after recovery (clamped to 0-100)
        """
        recovery_value = RECOVERY_VALUES.get(recovery_type, 20)
        
        if recovery_type == SchemaRecoveryType.MANUAL:
            # manual: restore +20
            after_health = before_health + recovery_value
        
        elif recovery_type == SchemaRecoveryType.AUTOMATIC:
            # automatic: restore +30
            after_health = before_health + recovery_value
        
        elif recovery_type == SchemaRecoveryType.STAGED:
            # staged: restore +15 per depth level
            staged_recovery = recovery_value * (depth + 1)
            after_health = before_health + staged_recovery
        
        elif recovery_type == SchemaRecoveryType.REROUTE:
            # reroute: restore based on connected_to relationships
            # Check for connected assets that might reroute
            reroute_recovery = self._calculate_reroute_recovery(asset_id, depth)
            after_health = before_health + reroute_recovery
        
        else:
            after_health = before_health + recovery_value
        
        # Clamp to valid range
        after_health = max(MIN_HEALTH, min(MAX_HEALTH, after_health))
        
        return after_health
    
    def _calculate_reroute_recovery(self, asset_id: UUID, depth: int) -> float:
        """Calculate reroute recovery value.
        
        For reroute strategy, we check if there are connected assets
        that can provide alternative paths.
        
        Args:
            asset_id: Asset ID
            depth: Propagation depth
            
        Returns:
            Recovery value based on reroute options
        """
        # Check for connected_to relationships
        connected_rels = self.db.query(AssetRelationship).filter(
            AssetRelationship.child_asset_id == asset_id,
            AssetRelationship.relationship_type == RelationshipType.CONNECTED_TO,
        ).all()
        
        # Base recovery value
        base_recovery = RECOVERY_VALUES[SchemaRecoveryType.REROUTE]
        
        # Adjust based on available reroute paths
        if len(connected_rels) >= 2:
            # Multiple paths available - better recovery
            return base_recovery * 1.5
        elif len(connected_rels) == 1:
            # One alternative path
            return base_recovery * 1.0
        else:
            # No alternative - limited recovery
            return base_recovery * 0.5
    
    def _store_results(
        self,
        recovery_id: UUID,
        results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Store recovery results in the database.
        
        Note: Results go to recovery_results table, NOT live tables.
        
        Args:
            recovery_id: Recovery simulation ID
            results: List of result dictionaries
            
        Returns:
            List of stored result dictionaries
        """
        stored = []
        
        for result_data in results:
            result = RecoveryResult(
                recovery_simulation_id=recovery_id,
                asset_id=result_data["asset_id"],
                before_health=result_data["before_health"],
                after_health=result_data["after_health"],
                improvement=result_data["improvement"],
                recovery_depth=result_data["recovery_depth"],
                remaining_risk=result_data["remaining_risk"],
            )
            self.db.add(result)
            stored.append(self._result_to_dict(result))
        
        self.db.commit()
        return stored
    
    def _result_to_dict(self, result: RecoveryResult) -> Dict[str, Any]:
        """Convert result to dictionary with asset info."""
        asset = self.db.query(Asset).filter(Asset.id == result.asset_id).first()
        return {
            "id": str(result.id),
            "recovery_simulation_id": str(result.recovery_simulation_id),
            "asset_id": str(result.asset_id),
            "asset_name": asset.name if asset else "Unknown",
            "asset_type": asset.asset_type if asset else None,
            "before_health": result.before_health,
            "after_health": result.after_health,
            "improvement": result.improvement,
            "recovery_depth": result.recovery_depth,
            "remaining_risk": result.remaining_risk,
            "created_at": result.created_at,
        }
    
    def _calculate_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate recovery statistics."""
        if not results:
            return {
                "assets_recovered": 0,
                "average_improvement": 0.0,
                "remaining_critical": 0,
            }
        
        improvements = [r["improvement"] for r in results]
        after_healths = [r["after_health"] for r in results]
        critical_count = sum(1 for r in results if r["remaining_risk"] in ["HIGH", "CRITICAL"])
        fully_recovered = sum(1 for r in results if r["after_health"] >= 90)
        
        return {
            "assets_recovered": fully_recovered,
            "average_improvement": sum(improvements) / len(improvements),
            "remaining_critical": critical_count,
            "worst_after": min(after_healths),
            "best_after": max(after_healths),
        }
    
    def get_recovery_results(self, recovery_id: UUID) -> List[Dict[str, Any]]:
        """Get results for a recovery simulation.
        
        Args:
            recovery_id: Recovery simulation ID
            
        Returns:
            List of result dictionaries
        """
        results = self.db.query(RecoveryResult).filter(
            RecoveryResult.recovery_simulation_id == recovery_id
        ).order_by(RecoveryResult.recovery_depth).all()
        
        return [self._result_to_dict(r) for r in results]
    
    def get_recovery_tree(self, recovery_id: UUID) -> Optional[Dict[str, Any]]:
        """Build a recovery tree for a recovery simulation.
        
        Args:
            recovery_id: Recovery simulation ID
            
        Returns:
            Recovery tree dictionary
        """
        recovery = self.get_recovery(recovery_id)
        if not recovery:
            return None
        
        # Get scenario for context
        scenario = self.db.query(Scenario).filter(
            Scenario.id == recovery.scenario_id
        ).first()
        
        results = self.get_recovery_results(recovery_id)
        
        if not results:
            return None
        
        # Get root asset info
        root_result = next(
            (r for r in results if r["recovery_depth"] == 0),
            results[0] if results else None
        )
        
        if not root_result:
            return None
        
        root_asset = self.db.query(Asset).filter(
            Asset.id == root_result["asset_id"]
        ).first()
        
        # Build tree structure
        tree = {
            "asset_id": root_result["asset_id"],
            "asset_name": root_asset.name if root_asset else "Unknown",
            "asset_type": root_asset.asset_type if root_asset else None,
            "before_health": root_result["before_health"],
            "after_health": root_result["after_health"],
            "improvement": root_result["improvement"],
            "recovery_depth": 0,
            "remaining_risk": root_result["remaining_risk"],
            "children": [],
        }
        
        # Add children by depth
        for result in results:
            if result["recovery_depth"] > 0:
                child_node = {
                    "asset_id": result["asset_id"],
                    "asset_name": result["asset_name"],
                    "asset_type": result["asset_type"],
                    "before_health": result["before_health"],
                    "after_health": result["after_health"],
                    "improvement": result["improvement"],
                    "recovery_depth": result["recovery_depth"],
                    "remaining_risk": result["remaining_risk"],
                    "children": [],
                }
                tree["children"].append(child_node)
        
        return tree
    
    def compare_recovery(self, recovery_id: UUID) -> Dict[str, Any]:
        """Compare recovery results (before vs after).
        
        Args:
            recovery_id: Recovery simulation ID
            
        Returns:
            Comparison dictionary
        """
        recovery = self.get_recovery(recovery_id)
        if not recovery:
            raise ValueError(f"Recovery {recovery_id} not found")
        
        results = self.get_recovery_results(recovery_id)
        
        if not results:
            return {
                "recovery_id": str(recovery_id),
                "strategy_name": recovery.strategy_name,
                "before_health": 100.0,
                "after_health": 100.0,
                "improvement": 0.0,
                "remaining_critical": 0,
                "assets": [],
            }
        
        # Aggregate stats
        before_healths = [r["before_health"] for r in results]
        after_healths = [r["after_health"] for r in results]
        improvements = [r["improvement"] for r in results]
        critical_count = sum(1 for r in results if r["remaining_risk"] in ["HIGH", "CRITICAL"])
        
        return {
            "recovery_id": str(recovery_id),
            "strategy_name": recovery.strategy_name,
            "before_health": sum(before_healths) / len(before_healths),
            "after_health": sum(after_healths) / len(after_healths),
            "improvement": sum(improvements) / len(improvements),
            "remaining_critical": critical_count,
            "assets": results,
        }
    
    def estimate_duration(
        self,
        recovery_type: SchemaRecoveryType,
        asset_count: int,
    ) -> int:
        """Estimate recovery duration based on strategy.
        
        Args:
            recovery_type: Type of recovery
            asset_count: Number of assets to recover
            
        Returns:
            Estimated duration in minutes
        """
        # Base durations per strategy
        base_durations = {
            SchemaRecoveryType.MANUAL: 120,  # 2 hours base
            SchemaRecoveryType.AUTOMATIC: 30,  # 30 min base
            SchemaRecoveryType.STAGED: 60,  # 1 hour base
            SchemaRecoveryType.REROUTE: 45,  # 45 min base
        }
        
        base = base_durations.get(recovery_type, 60)
        
        # Add time per asset
        time_per_asset = {
            SchemaRecoveryType.MANUAL: 15,
            SchemaRecoveryType.AUTOMATIC: 5,
            SchemaRecoveryType.STAGED: 10,
            SchemaRecoveryType.REROUTE: 8,
        }
        
        per_asset = time_per_asset.get(recovery_type, 10)
        
        return base + (asset_count * per_asset)
    
    def calculate_remaining_risk(self, after_health: float) -> str:
        """Calculate remaining risk based on health score.
        
        Args:
            after_health: Health score after recovery
            
        Returns:
            Risk level string
        """
        risk_level = calculate_risk_level(after_health)
        return risk_level.value