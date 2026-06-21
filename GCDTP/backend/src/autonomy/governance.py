"""
Autonomy Governance

Governance layer above all AI systems.
LEVEL 0-3 only. NO LEVEL 4 autonomy.
MANDATORY: audit trails, rollback, explanations, evidence chains.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AutonomyLevel(str, Enum):
    """
    Autonomy levels.
    
    LEVEL 0: Manual - Human does everything
    LEVEL 1: Recommendations - AI suggests, human decides
    LEVEL 2: Human Approval Required - AI prepares, human approves
    LEVEL 3: Supervised Execution - AI executes, human monitors
    
    NO LEVEL 4 AUTONOMY.
    """
    MANUAL = "manual"           # LEVEL 0
    RECOMMENDATIONS = "recs"   # LEVEL 1
    APPROVAL_REQUIRED = "approval"  # LEVEL 2
    SUPERVISED = "supervised"  # LEVEL 3
    # LEVEL 4 IS FORBIDDEN


class ActionCategory(str, Enum):
    """Categories of actions requiring governance."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    APPROVE = "approve"


@dataclass
class GovernanceRule:
    """Governance rule for an action."""
    rule_id: str
    category: ActionCategory
    required_level: AutonomyLevel
    requires_audit: bool
    requires_approval: bool
    requires_explanation: bool


@dataclass
class AuditRecord:
    """Audit trail record."""
    audit_id: str
    timestamp: datetime
    user: str
    action: str
    category: ActionCategory
    details: Dict[str, Any]
    autonomy_level: AutonomyLevel
    explanation: Optional[str]
    evidence: List[str]
    approved_by: Optional[str]


@dataclass
class RollbackRecord:
    """Rollback record for reverting actions."""
    rollback_id: str
    timestamp: datetime
    action_id: str
    original_state: Dict[str, Any]
    reverted_by: str
    reason: str


class GovernanceLayer:
    """
    Governance layer for autonomy control.
    
    MANDATORY FEATURES:
    - Audit trails
    - Rollback records
    - Explanations
    - Evidence chains
    
    LEVELS:
    - LEVEL 0: Manual
    - LEVEL 1: Recommendations
    - LEVEL 2: Human approval required
    - LEVEL 3: Supervised execution
    
    FORBIDDEN:
    - LEVEL 4: Fully autonomous
    - Self-healing without approval
    - Asset modification without approval
    """
    
    def __init__(self):
        self._audit_trail: Dict[str, AuditRecord] = {}
        self._rollback_records: Dict[str, RollbackRecord] = {}
        self._governance_rules: Dict[str, GovernanceRule] = {}
        self._current_level: AutonomyLevel = AutonomyLevel.MANUAL
        
        # Initialize default rules
        self._init_default_rules()
    
    def _init_default_rules(self):
        """Initialize default governance rules."""
        rules = [
            GovernanceRule("read", ActionCategory.READ, AutonomyLevel.MANUAL, True, False, True),
            GovernanceRule("write", ActionCategory.WRITE, AutonomyLevel.APPROVAL_REQUIRED, True, True, True),
            GovernanceRule("delete", ActionCategory.DELETE, AutonomyLevel.SUPERVISED, True, True, True),
            GovernanceRule("execute", ActionCategory.EXECUTE, AutonomyLevel.APPROVAL_REQUIRED, True, True, True),
            GovernanceRule("approve", ActionCategory.APPROVE, AutonomyLevel.MANUAL, True, False, True),
        ]
        for rule in rules:
            self._governance_rules[rule.rule_id] = rule
    
    def set_autonomy_level(self, level: AutonomyLevel) -> bool:
        """
        Set the autonomy level.
        
        LEVEL 4 IS FORBIDDEN.
        """
        if level == "level_4":  # This should never happen but defensive check
            return False
        self._current_level = level
        return True
    
    def get_autonomy_level(self) -> AutonomyLevel:
        """Get current autonomy level."""
        return self._current_level
    
    def requires_approval(self, action: str) -> bool:
        """Check if action requires approval."""
        rule = self._governance_rules.get(action)
        if rule:
            return rule.requires_approval
        return True  # Default to requiring approval
    
    def requires_explanation(self, action: str) -> bool:
        """Check if action requires explanation."""
        rule = self._governance_rules.get(action)
        if rule:
            return rule.requires_explanation
        return True  # Default to requiring explanation
    
    def record_audit(
        self,
        audit_id: str,
        user: str,
        action: str,
        category: ActionCategory,
        details: Dict[str, Any],
        explanation: Optional[str] = None,
        evidence: Optional[List[str]] = None
    ) -> AuditRecord:
        """Record an audit trail entry."""
        record = AuditRecord(
            audit_id=audit_id,
            timestamp=datetime.now(),
            user=user,
            action=action,
            category=category,
            details=details,
            autonomy_level=self._current_level,
            explanation=explanation,
            evidence=evidence or [],
            approved_by=None
        )
        self._audit_trail[audit_id] = record
        return record
    
    def record_rollback(
        self,
        rollback_id: str,
        action_id: str,
        original_state: Dict[str, Any],
        reverted_by: str,
        reason: str
    ) -> RollbackRecord:
        """Record a rollback."""
        record = RollbackRecord(
            rollback_id=rollback_id,
            timestamp=datetime.now(),
            action_id=action_id,
            original_state=original_state,
            reverted_by=reverted_by,
            reason=reason
        )
        self._rollback_records[rollback_id] = record
        return record
    
    def get_audit_trail(
        self,
        user: Optional[str] = None,
        action: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[AuditRecord]:
        """Get audit trail with filters."""
        records = list(self._audit_trail.values())
        
        if user:
            records = [r for r in records if r.user == user]
        if action:
            records = [r for r in records if r.action == action]
        if start_time:
            records = [r for r in records if r.timestamp >= start_time]
        if end_time:
            records = [r for r in records if r.timestamp <= end_time]
        
        return sorted(records, key=lambda r: r.timestamp, reverse=True)
    
    def get_rollback_records(
        self,
        action_id: Optional[str] = None
    ) -> List[RollbackRecord]:
        """Get rollback records."""
        records = list(self._rollback_records.values())
        
        if action_id:
            records = [r for r in records if r.action_id == action_id]
        
        return sorted(records, key=lambda r: r.timestamp, reverse=True)


# Singleton instance
_layer: Optional[GovernanceLayer] = None


def get_governance_layer() -> GovernanceLayer:
    """Get or create governance layer singleton."""
    global _layer
    if _layer is None:
        _layer = GovernanceLayer()
    return _layer
