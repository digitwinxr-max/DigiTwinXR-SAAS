"""Simulation Service for Scenario Simulation Engine.

This service creates virtual events, propagations, and health calculations
that are completely isolated from live data. No writes to:
- events table
- propagated_events table
- asset_health table
"""
from typing import Optional, List, Dict, Any, Set, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from ..models.asset import Asset
from ..models.asset_relationship import AssetRelationship, RelationshipType
from ..models.health import AssetHealth
from ..models.scenario import Scenario, ScenarioType, ScenarioStatus
from ..models.scenario_result import ScenarioResult
from ..schemas.scenario import (
    VirtualEvent,
    VirtualPropagation,
    VirtualHealth,
    ScenarioCreate,
    ImpactNode,
)


# Maximum propagation depth
MAX_DEPTH = 3

# Severity penalties
SEVERITY_PENALTIES = {
    "WARNING": 10,
    "CRITICAL": 20,
}

# Relationship propagation rules (from propagation service)
RELATIONSHIP_PROPS = {
    RelationshipType.CONTAINS: {"direction": "up", "type": "child_failure"},
    RelationshipType.FEEDS: {"direction": "down", "type": "downstream_failure"},
    RelationshipType.CONTROLS: {"direction": "down", "type": "dependency_impact"},
    RelationshipType.CONNECTED_TO: {"direction": "both", "type": "dependency_impact"},
    RelationshipType.MONITORS: {"direction": "none", "type": None},
}

# Relationship weights (from dependency health service)
RELATIONSHIP_WEIGHTS = {
    RelationshipType.CONTAINS: 0.5,
    RelationshipType.FEEDS: 0.7,
    RelationshipType.CONTROLS: 0.6,
    RelationshipType.CONNECTED_TO: 0.3,
    RelationshipType.MONITORS: 0.0,
}

# Depth decay
DEPTH_DECAY = {
    1: 1.0,
    2: 0.5,
    3: 0.25,
}


class SimulationService:
    """Service for running scenario simulations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_scenario(self, data: ScenarioCreate) -> Scenario:
        """Create a new scenario.
        
        Args:
            data: Scenario creation data
            
        Returns:
            Created scenario
        """
        scenario = Scenario(
            name=data.name,
            description=data.description,
            scenario_type=ScenarioType(data.scenario_type.value),
            root_asset_id=data.root_asset_id,
            severity=data.severity.value,
            status=ScenarioStatus.DRAFT,
        )
        self.db.add(scenario)
        self.db.commit()
        self.db.refresh(scenario)
        return scenario
    
    def get_scenario(self, scenario_id: UUID) -> Optional[Scenario]:
        """Get a scenario by ID.
        
        Args:
            scenario_id: Scenario ID
            
        Returns:
            Scenario or None
        """
        return self.db.query(Scenario).filter(Scenario.id == scenario_id).first()
    
    def list_scenarios(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        scenario_type: Optional[str] = None,
    ) -> Tuple[List[Scenario], int]:
        """List all scenarios.
        
        Args:
            skip: Number to skip
            limit: Maximum to return
            status: Filter by status
            scenario_type: Filter by type
            
        Returns:
            Tuple of (scenarios, total count)
        """
        query = self.db.query(Scenario)
        
        if status:
            query = query.filter(Scenario.status == status)
        if scenario_type:
            query = query.filter(Scenario.scenario_type == scenario_type)
        
        total = query.count()
        scenarios = query.order_by(Scenario.created_at.desc()).offset(skip).limit(limit).all()
        
        return scenarios, total
    
    def delete_scenario(self, scenario_id: UUID) -> bool:
        """Delete a scenario and its results.
        
        Args:
            scenario_id: Scenario ID
            
        Returns:
            True if deleted
        """
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            return False
        
        self.db.delete(scenario)
        self.db.commit()
        return True
    
    def run_simulation(self, scenario_id: UUID) -> Dict[str, Any]:
        """Run a simulation for a scenario.
        
        This creates virtual events, propagations, and health calculations
        that are stored as results but NOT written to live tables.
        
        Args:
            scenario_id: Scenario ID
            
        Returns:
            Simulation results
        """
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")
        
        # Get root asset
        root_asset = self.db.query(Asset).filter(Asset.id == scenario.root_asset_id).first()
        if not root_asset:
            raise ValueError(f"Root asset {scenario.root_asset_id} not found")
        
        # Build virtual event
        virtual_event = self.build_virtual_event(
            asset_id=scenario.root_asset_id,
            severity=scenario.severity,
            scenario_type=scenario.scenario_type,
        )
        
        # Build virtual propagation
        virtual_propagations = self.build_virtual_propagation(
            virtual_event=virtual_event,
            root_asset_id=scenario.root_asset_id,
        )
        
        # Compute virtual health for all affected assets
        affected_assets = [scenario.root_asset_id] + [
            vp.affected_asset_id for vp in virtual_propagations
        ]
        
        virtual_healths = self.compute_virtual_health(
            asset_ids=affected_assets,
            virtual_event=virtual_event,
            virtual_propagations=virtual_propagations,
        )
        
        # Store results (but NOT in live tables)
        results = self._store_results(
            scenario_id=scenario_id,
            virtual_event=virtual_event,
            virtual_propagations=virtual_propagations,
            virtual_healths=virtual_healths,
        )
        
        # Update scenario status
        scenario.status = ScenarioStatus.COMPLETED
        self.db.commit()
        
        # Calculate stats
        stats = self._calculate_stats(results)
        
        return {
            "scenario_id": scenario_id,
            "total_affected": len(results),
            "max_depth": stats["max_depth"],
            "worst_health": stats["worst_health"],
            "average_health": stats["average_health"],
            "results": results,
        }
    
    def build_virtual_event(
        self,
        asset_id: UUID,
        severity: str,
        scenario_type: ScenarioType,
    ) -> VirtualEvent:
        """Build a virtual event for simulation.
        
        This creates an in-memory event that is NOT written to the events table.
        
        Args:
            asset_id: Asset ID
            severity: Event severity
            scenario_type: Type of scenario
            
        Returns:
            VirtualEvent
        """
        message = self._get_scenario_message(scenario_type, severity)
        
        return VirtualEvent(
            asset_id=asset_id,
            severity=severity,
            message=message,
            timestamp=datetime.utcnow(),
        )
    
    def _get_scenario_message(self, scenario_type: ScenarioType, severity: str) -> str:
        """Get appropriate message for scenario type."""
        messages = {
            ScenarioType.FAILURE: f"Simulated {severity} failure",
            ScenarioType.RECOVERY: f"Simulated {severity} recovery",
            ScenarioType.MAINTENANCE: f"Simulated {severity} maintenance",
            ScenarioType.CUSTOM: f"Simulated {severity} custom scenario",
        }
        return messages.get(scenario_type, "Simulated event")
    
    def build_virtual_propagation(
        self,
        virtual_event: VirtualEvent,
        root_asset_id: UUID,
    ) -> List[VirtualPropagation]:
        """Build virtual propagations using the relationship graph.
        
        This traverses the relationship graph to find affected assets,
        using the same rules as the FailurePropagationService but
        without writing to the propagated_events table.
        
        Args:
            virtual_event: The virtual event
            root_asset_id: Root asset ID
            
        Returns:
            List of VirtualPropagation
        """
        propagations = []
        visited: Set[UUID] = set()
        
        self._propagate_to_related(
            virtual_event=virtual_event,
            current_asset_id=root_asset_id,
            depth=0,
            visited=visited,
            propagations=propagations,
        )
        
        return propagations
    
    def _propagate_to_related(
        self,
        virtual_event: VirtualEvent,
        current_asset_id: UUID,
        depth: int,
        visited: Set[UUID],
        propagations: List[VirtualPropagation],
    ) -> None:
        """Recursively propagate to related assets.
        
        Args:
            virtual_event: The virtual event
            current_asset_id: Current asset in traversal
            depth: Current depth
            visited: Set of visited asset IDs
            propagations: List to append to
        """
        if depth >= MAX_DEPTH or current_asset_id in visited:
            return
        
        visited.add(current_asset_id)
        
        # Get relationships for this asset
        relationships = self.db.query(AssetRelationship).filter(
            AssetRelationship.parent_asset_id == current_asset_id
        ).all()
        
        for rel in relationships:
            rel_type = rel.relationship_type
            if hasattr(rel_type, 'value'):
                rel_type = rel_type.value
            
            try:
                rel_enum = RelationshipType(rel_type)
            except ValueError:
                continue
            
            # Check propagation rules
            rule = RELATIONSHIP_PROPS.get(rel_enum)
            if not rule or rule["direction"] == "none":
                continue
            
            # Get target asset
            target_id = rel.child_asset_id
            
            # Skip if already visited
            if target_id in visited:
                continue
            
            # Create virtual propagation
            vp = VirtualPropagation(
                source_event=virtual_event,
                affected_asset_id=target_id,
                propagation_type=rule["type"],
                depth=depth + 1,
                severity=virtual_event.severity,
            )
            propagations.append(vp)
            
            # Recursively propagate
            self._propagate_to_related(
                virtual_event=virtual_event,
                current_asset_id=target_id,
                depth=depth + 1,
                visited=visited,
                propagations=propagations,
            )
        
        # Also check upstream relationships (for CONTAINS direction=up)
        upstream_rels = self.db.query(AssetRelationship).filter(
            AssetRelationship.child_asset_id == current_asset_id,
            AssetRelationship.relationship_type == RelationshipType.CONTAINS,
        ).all()
        
        for rel in upstream_rels:
            target_id = rel.parent_asset_id
            
            if target_id in visited:
                continue
            
            # Create upstream propagation
            vp = VirtualPropagation(
                source_event=virtual_event,
                affected_asset_id=target_id,
                propagation_type="child_failure",
                depth=depth + 1,
                severity=virtual_event.severity,
            )
            propagations.append(vp)
            
            # Recursively propagate
            self._propagate_to_related(
                virtual_event=virtual_event,
                current_asset_id=target_id,
                depth=depth + 1,
                visited=visited,
                propagations=propagations,
            )
    
    def compute_virtual_health(
        self,
        asset_ids: List[UUID],
        virtual_event: VirtualEvent,
        virtual_propagations: List[VirtualPropagation],
    ) -> List[VirtualHealth]:
        """Compute virtual health for affected assets.
        
        This calculates what each asset's health would be if the
        virtual event and propagations occurred, WITHOUT writing
        to the asset_health table.
        
        Formula:
            virtual_health = live_health - local_penalty - dependency_penalty
            
        Args:
            asset_ids: List of affected asset IDs
            virtual_event: The virtual event
            virtual_propagations: List of virtual propagations
            
        Returns:
            List of VirtualHealth
        """
        virtual_healths = []
        
        for asset_id in asset_ids:
            # Get live health
            health_record = self.db.query(AssetHealth).filter(
                AssetHealth.asset_id == asset_id
            ).first()
            live_health = health_record.health_score if health_record else 100.0
            
            # Calculate local virtual penalty
            local_penalty = 0.0
            if virtual_event.asset_id == asset_id:
                local_penalty = SEVERITY_PENALTIES.get(virtual_event.severity, 0)
            
            # Calculate virtual dependency penalty
            dependency_penalty = self._calculate_virtual_dependency_penalty(
                asset_id=asset_id,
                virtual_propagations=virtual_propagations,
            )
            
            # Calculate predicted health
            predicted_health = live_health - local_penalty - dependency_penalty
            
            # Clamp to valid range
            predicted_health = max(0.0, min(100.0, predicted_health))
            
            # Get depth
            depth = 0
            if asset_id == virtual_event.asset_id:
                depth = 0
            else:
                for vp in virtual_propagations:
                    if vp.affected_asset_id == asset_id:
                        depth = vp.depth
                        break
            
            virtual_healths.append(VirtualHealth(
                asset_id=asset_id,
                live_health=live_health,
                local_virtual_penalty=local_penalty,
                virtual_dependency_penalty=dependency_penalty,
                predicted_health=predicted_health,
                depth=depth,
            ))
        
        return virtual_healths
    
    def _calculate_virtual_dependency_penalty(
        self,
        asset_id: UUID,
        virtual_propagations: List[VirtualPropagation],
    ) -> float:
        """Calculate dependency penalty from virtual propagations.
        
        Args:
            asset_id: Asset ID
            virtual_propagations: List of virtual propagations
            
        Returns:
            Total penalty from dependencies
        """
        total_penalty = 0.0
        
        for vp in virtual_propagations:
            if vp.affected_asset_id == asset_id:
                # Get source health
                source_health = 100.0
                if vp.source_event.asset_id == vp.affected_asset_id:
                    source_health = 100.0 - SEVERITY_PENALTIES.get(vp.source_event.severity, 0)
                else:
                    # Source is affected by the virtual event
                    source_health = 100.0 - SEVERITY_PENALTIES.get(vp.source_event.severity, 0)
                
                # Get relationship weight
                rel_type = vp.propagation_type
                weight = 0.5  # Default
                if "downstream" in rel_type:
                    weight = 0.7
                elif "child" in rel_type:
                    weight = 0.5
                elif "dependency" in rel_type:
                    weight = 0.6
                
                # Get depth decay
                decay = DEPTH_DECAY.get(vp.depth, 0.25)
                
                # Calculate penalty
                penalty = (100.0 - source_health) * weight * decay
                total_penalty += penalty
        
        return total_penalty
    
    def _store_results(
        self,
        scenario_id: UUID,
        virtual_event: VirtualEvent,
        virtual_propagations: List[VirtualPropagation],
        virtual_healths: List[VirtualHealth],
    ) -> List[Dict[str, Any]]:
        """Store simulation results in the database.
        
        Note: These are stored in scenario_results table, NOT in
        the live events, propagated_events, or asset_health tables.
        
        Args:
            scenario_id: Scenario ID
            virtual_event: The virtual event
            virtual_propagations: Virtual propagations
            virtual_healths: Virtual health calculations
            
        Returns:
            List of result dictionaries
        """
        results = []
        
        # Store result for root asset
        root_health = next(
            (vh for vh in virtual_healths if vh.asset_id == virtual_event.asset_id),
            None
        )
        if root_health:
            result = ScenarioResult(
                scenario_id=scenario_id,
                asset_id=root_health.asset_id,
                predicted_health=root_health.predicted_health,
                current_health=root_health.live_health,
                delta_health=root_health.predicted_health - root_health.live_health,
                propagation_depth=0,
                relationship_path="root",
            )
            self.db.add(result)
            results.append(self._result_to_dict(result))
        
        # Store results for propagated assets
        for vp in virtual_propagations:
            vh = next(
                (h for h in virtual_healths if h.asset_id == vp.affected_asset_id),
                None
            )
            if vh:
                result = ScenarioResult(
                    scenario_id=scenario_id,
                    asset_id=vh.asset_id,
                    predicted_health=vh.predicted_health,
                    current_health=vh.live_health,
                    delta_health=vh.predicted_health - vh.live_health,
                    propagation_depth=vp.depth,
                    relationship_path=vp.propagation_type,
                )
                self.db.add(result)
                results.append(self._result_to_dict(result))
        
        self.db.commit()
        return results
    
    def _result_to_dict(self, result: ScenarioResult) -> Dict[str, Any]:
        """Convert result to dictionary with asset info."""
        asset = self.db.query(Asset).filter(Asset.id == result.asset_id).first()
        return {
            "id": str(result.id),
            "scenario_id": str(result.scenario_id),
            "asset_id": str(result.asset_id),
            "asset_name": asset.name if asset else "Unknown",
            "asset_type": asset.asset_type if asset else None,
            "predicted_health": result.predicted_health,
            "current_health": result.current_health,
            "delta_health": result.delta_health,
            "propagation_depth": result.propagation_depth,
            "relationship_path": result.relationship_path,
            "created_at": result.created_at,
        }
    
    def _calculate_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate simulation statistics."""
        if not results:
            return {
                "max_depth": 0,
                "worst_health": 100.0,
                "average_health": 100.0,
            }
        
        depths = [r["propagation_depth"] for r in results]
        healths = [r["predicted_health"] for r in results]
        
        return {
            "max_depth": max(depths) if depths else 0,
            "worst_health": min(healths) if healths else 100.0,
            "average_health": sum(healths) / len(healths) if healths else 100.0,
        }
    
    def get_scenario_results(self, scenario_id: UUID) -> List[Dict[str, Any]]:
        """Get results for a scenario.
        
        Args:
            scenario_id: Scenario ID
            
        Returns:
            List of result dictionaries
        """
        results = self.db.query(ScenarioResult).filter(
            ScenarioResult.scenario_id == scenario_id
        ).order_by(ScenarioResult.propagation_depth).all()
        
        return [self._result_to_dict(r) for r in results]
    
    def get_impact_tree(self, scenario_id: UUID) -> Optional[Dict[str, Any]]:
        """Build an impact tree for a scenario.
        
        Args:
            scenario_id: Scenario ID
            
        Returns:
            Impact tree dictionary
        """
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            return None
        
        results = self.get_scenario_results(scenario_id)
        
        # Get root asset info
        root_asset = self.db.query(Asset).filter(
            Asset.id == scenario.root_asset_id
        ).first()
        
        root_result = next(
            (r for r in results if r["asset_id"] == str(scenario.root_asset_id)),
            None
        )
        
        # Build tree structure
        tree = {
            "asset_id": str(scenario.root_asset_id),
            "asset_name": root_asset.name if root_asset else "Unknown",
            "asset_type": root_asset.asset_type if root_asset else None,
            "current_health": root_result["current_health"] if root_result else 100.0,
            "predicted_health": root_result["predicted_health"] if root_result else 100.0,
            "delta_health": root_result["delta_health"] if root_result else 0.0,
            "propagation_depth": 0,
            "relationship_type": "root",
            "children": [],
        }
        
        # Add children
        children_results = [r for r in results if r["propagation_depth"] > 0]
        for child in children_results:
            child_node = {
                "asset_id": child["asset_id"],
                "asset_name": child["asset_name"],
                "asset_type": child["asset_type"],
                "current_health": child["current_health"],
                "predicted_health": child["predicted_health"],
                "delta_health": child["delta_health"],
                "propagation_depth": child["propagation_depth"],
                "relationship_type": child["relationship_path"],
                "children": [],
            }
            tree["children"].append(child_node)
        
        return tree
    
    def compare_with_live_health(self, scenario_id: UUID) -> Dict[str, Any]:
        """Compare simulation results with live health.
        
        Args:
            scenario_id: Scenario ID
            
        Returns:
            Comparison dictionary
        """
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")
        
        results = self.get_scenario_results(scenario_id)
        
        if not results:
            return {
                "current_health": 100.0,
                "predicted_health": 100.0,
                "delta": 0.0,
            }
        
        # Get root asset results
        root_result = next(
            (r for r in results if r["asset_id"] == str(scenario.root_asset_id)),
            results[0]
        )
        
        return {
            "current_health": root_result["current_health"],
            "predicted_health": root_result["predicted_health"],
            "delta": root_result["delta_health"],
        }
    
    def get_scenario_summary(self, scenario_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a summary of a scenario.
        
        Args:
            scenario_id: Scenario ID
            
        Returns:
            Summary dictionary
        """
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            return None
        
        results = self.get_scenario_results(scenario_id)
        
        if not results:
            return {
                "scenario_id": str(scenario.id),
                "scenario_name": scenario.name,
                "scenario_type": scenario.scenario_type.value,
                "severity": scenario.severity,
                "status": scenario.status.value,
                "created_at": scenario.created_at,
                "total_affected": 0,
                "worst_health": 100.0,
                "average_delta": 0.0,
            }
        
        predicted_healths = [r["predicted_health"] for r in results]
        deltas = [r["delta_health"] for r in results]
        
        return {
            "scenario_id": str(scenario.id),
            "scenario_name": scenario.name,
            "scenario_type": scenario.scenario_type.value,
            "severity": scenario.severity,
            "status": scenario.status.value,
            "created_at": scenario.created_at,
            "total_affected": len(results),
            "worst_health": min(predicted_healths),
            "average_delta": sum(deltas) / len(deltas) if deltas else 0.0,
        }