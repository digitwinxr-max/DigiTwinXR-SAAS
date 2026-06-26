"""
Disaster Recovery Manager

Manages disaster recovery plans.
"""

import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


class DRPlanType(str):
    """DR plan types."""
    DATABASE_FAILURE = "database_failure"
    EMQX_FAILURE = "emqx_failure"
    GEOSERVER_FAILURE = "geoserver_failure"
    NEO4J_FAILURE = "neo4j_failure"
    NODERED_FAILURE = "nodered_failure"
    FULL_OUTAGE = "full_outage"


@dataclass
class DRPlan:
    """Disaster recovery plan."""
    id: str
    name: str
    plan_type: DRPlanType
    target_rto_minutes: int  # Recovery Time Objective
    target_rpo_minutes: int  # Recovery Point Objective
    steps: List[Dict] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    is_active: bool = False
    last_tested: Optional[datetime] = None
    last_successful_test: bool = False


class DisasterRecoveryManager:
    """
    Manages disaster recovery plans.
    
    Supports:
    - Database failure recovery
    - EMQX failure recovery
    - GeoServer failure recovery
    - Neo4j failure recovery
    - Node-RED failure recovery
    """
    
    def __init__(self):
        self._plans: Dict[str, DRPlan] = {}
        self._initialize_defaults()
    
    def _initialize_defaults(self) -> None:
        """Initialize default DR plans."""
        self.create_plan(
            name="Database Failure Recovery",
            plan_type=DRPlanType.DATABASE_FAILURE,
            target_rto_minutes=30,
            target_rpo_minutes=15,
            steps=[
                {"step": 1, "action": "Switch to read replica"},
                {"step": 2, "action": "Notify operations team"},
                {"step": 3, "action": "Begin database restoration"},
                {"step": 4, "action": "Verify data integrity"},
                {"step": 5, "action": "Resume primary operations"}
            ]
        )
        
        self.create_plan(
            name="EMQX Failure Recovery",
            plan_type=DRPlanType.EMQX_FAILURE,
            target_rto_minutes=15,
            target_rpo_minutes=5,
            steps=[
                {"step": 1, "action": "Switch to backup broker"},
                {"step": 2, "action": "Reconnect clients"},
                {"step": 3, "action": "Verify message persistence"},
                {"step": 4, "action": "Resume operations"}
            ]
        )
        
        self.create_plan(
            name="GeoServer Failure Recovery",
            plan_type=DRPlanType.GEOSERVER_FAILURE,
            target_rto_minutes=20,
            target_rpo_minutes=10,
            steps=[
                {"step": 1, "action": "Failover to backup GeoServer"},
                {"step": 2, "action": "Update DNS records"},
                {"step": 3, "action": "Verify tile cache"},
                {"step": 4, "action": "Resume mapping services"}
            ]
        )
        
        self.create_plan(
            name="Neo4j Failure Recovery",
            plan_type=DRPlanType.NEO4J_FAILURE,
            target_rto_minutes=25,
            target_rpo_minutes=10,
            steps=[
                {"step": 1, "action": "Switch to Neo4j cluster backup"},
                {"step": 2, "action": "Restore graph projections"},
                {"step": 3, "action": "Verify graph integrity"},
                {"step": 4, "action": "Resume graph queries"}
            ]
        )
        
        self.create_plan(
            name="Node-RED Failure Recovery",
            plan_type=DRPlanType.NODERED_FAILURE,
            target_rto_minutes=15,
            target_rpo_minutes=5,
            steps=[
                {"step": 1, "action": "Restore from last backup"},
                {"step": 2, "action": "Redeploy workflows"},
                {"step": 3, "action": "Verify automation flows"},
                {"step": 4, "action": "Resume workflow operations"}
            ]
        )
    
    def create_plan(
        self,
        name: str,
        plan_type: DRPlanType,
        target_rto_minutes: int,
        target_rpo_minutes: int,
        steps: Optional[List[Dict]] = None,
        dependencies: Optional[List[str]] = None
    ) -> DRPlan:
        """Create a DR plan."""
        plan_id = str(uuid.uuid4())
        
        plan = DRPlan(
            id=plan_id,
            name=name,
            plan_type=plan_type,
            target_rto_minutes=target_rto_minutes,
            target_rpo_minutes=target_rpo_minutes,
            steps=steps or [],
            dependencies=dependencies or []
        )
        
        self._plans[plan_id] = plan
        return plan
    
    def get_plan(self, plan_id: str) -> Optional[DRPlan]:
        """Get a DR plan."""
        return self._plans.get(plan_id)
    
    def get_plan_by_type(self, plan_type: DRPlanType) -> Optional[DRPlan]:
        """Get a DR plan by type."""
        for plan in self._plans.values():
            if plan.plan_type == plan_type:
                return plan
        return None
    
    def get_all_plans(self) -> List[DRPlan]:
        """Get all DR plans."""
        return list(self._plans.values())
    
    def get_active_plans(self) -> List[DRPlan]:
        """Get active DR plans."""
        return [p for p in self._plans.values() if p.is_active]
    
    def activate_plan(self, plan_id: str) -> bool:
        """Activate a DR plan."""
        plan = self._plans.get(plan_id)
        if not plan:
            return False
        
        # Deactivate others of same type
        for p in self._plans.values():
            if p.plan_type == plan.plan_type:
                p.is_active = False
        
        plan.is_active = True
        return True
    
    def deactivate_plan(self, plan_id: str) -> bool:
        """Deactivate a DR plan."""
        plan = self._plans.get(plan_id)
        if not plan:
            return False
        
        plan.is_active = False
        return True
    
    def mark_tested(
        self,
        plan_id: str,
        successful: bool
    ) -> bool:
        """Mark a plan as tested."""
        plan = self._plans.get(plan_id)
        if not plan:
            return False
        
        plan.last_tested = datetime.utcnow()
        plan.last_successful_test = successful
        return True
    
    def get_recovery_summary(self) -> Dict[str, Any]:
        """Get recovery summary."""
        plans = list(self._plans.values())
        
        return {
            "total_plans": len(plans),
            "active_plans": len([p for p in plans if p.is_active]),
            "tested_plans": len([p for p in plans if p.last_tested]),
            "successful_tests": len([p for p in plans if p.last_successful_test]),
            "avg_rto_minutes": sum(p.target_rto_minutes for p in plans) / len(plans) if plans else 0,
            "avg_rpo_minutes": sum(p.target_rpo_minutes for p in plans) / len(plans) if plans else 0
        }
