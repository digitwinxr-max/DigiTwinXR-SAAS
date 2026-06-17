"""Threshold rule service for business logic."""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models.threshold import ThresholdRule
from ..models.sensor import Sensor
from ..schemas.threshold import ThresholdRuleCreate, ThresholdRuleUpdate, EvaluationResult
from ..events import emit, EventType


class ThresholdService:
    """Service class for threshold rule operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_threshold_rule(self, rule_data: ThresholdRuleCreate) -> ThresholdRule:
        """Create a new threshold rule."""
        # If sensor_id is provided, verify sensor exists
        if rule_data.sensor_id:
            sensor = self.db.query(Sensor).filter(Sensor.id == rule_data.sensor_id).first()
            if not sensor:
                return None
        
        rule = ThresholdRule(
            sensor_id=rule_data.sensor_id,
            name=rule_data.name,
            rule_type=rule_data.rule_type,
            warning_min=rule_data.warning_min,
            warning_max=rule_data.warning_max,
            critical_min=rule_data.critical_min,
            critical_max=rule_data.critical_max,
            is_active=rule_data.is_active,
        )
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def get_threshold_rule(self, rule_id: UUID) -> Optional[ThresholdRule]:
        """Get a threshold rule by ID."""
        return self.db.query(ThresholdRule).filter(ThresholdRule.id == rule_id).first()

    def get_threshold_rules(
        self,
        skip: int = 0,
        limit: int = 100,
        sensor_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[List[ThresholdRule], int]:
        """Get all threshold rules with optional filtering."""
        query = self.db.query(ThresholdRule)

        if sensor_id:
            query = query.filter(ThresholdRule.sensor_id == sensor_id)
        if is_active is not None:
            query = query.filter(ThresholdRule.is_active == is_active)

        total = query.count()
        rules = query.order_by(desc(ThresholdRule.created_at)).offset(skip).limit(limit).all()

        return rules, total

    def update_threshold_rule(self, rule_id: UUID, rule_data: ThresholdRuleUpdate) -> Optional[ThresholdRule]:
        """Update a threshold rule."""
        rule = self.get_threshold_rule(rule_id)
        if not rule:
            return None

        update_data = rule_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)

        self.db.commit()
        self.db.refresh(rule)
        return rule

    def delete_threshold_rule(self, rule_id: UUID) -> bool:
        """Delete a threshold rule."""
        rule = self.get_threshold_rule(rule_id)
        if not rule:
            return False

        self.db.delete(rule)
        self.db.commit()
        return True

    def get_thresholds_by_sensor(self, sensor_id: UUID) -> List[ThresholdRule]:
        """Get all threshold rules for a specific sensor."""
        return self.db.query(ThresholdRule).filter(
            ThresholdRule.sensor_id == sensor_id
        ).order_by(desc(ThresholdRule.created_at)).all()

    def evaluate_measurement(self, sensor_id: UUID, value: float) -> EvaluationResult:
        """Evaluate a measurement value against threshold rules.
        
        Returns the most severe status from all applicable rules.
        Emits threshold.evaluated event.
        """
        # Get active rules for this sensor (including global rules with null sensor_id)
        rules = self.db.query(ThresholdRule).filter(
            ThresholdRule.is_active == True,
            (ThresholdRule.sensor_id == sensor_id) | (ThresholdRule.sensor_id.is_(None))
        ).all()

        if not rules:
            result = EvaluationResult(
                status="OK",
                rule_id="",
                sensor_id=str(sensor_id),
                message="No active rules for this sensor"
            )
            self._emit_evaluation_event(sensor_id, value, result)
            return result

        # Evaluate against all rules and collect statuses
        statuses = []
        for rule in rules:
            status = rule.evaluate(value)
            statuses.append({
                "status": status,
                "rule_id": str(rule.id),
                "rule_name": rule.name,
            })

        # Determine most severe status
        # CRITICAL > WARNING > OK
        worst_status = "OK"
        worst_rule = None
        
        for s in statuses:
            if s["status"] == "CRITICAL":
                worst_status = "CRITICAL"
                worst_rule = s
                break  # Can't get worse than CRITICAL
            elif s["status"] == "WARNING" and worst_status != "CRITICAL":
                worst_status = "WARNING"
                worst_rule = s

        if worst_rule:
            result = EvaluationResult(
                status=worst_status,
                rule_id=worst_rule["rule_id"],
                sensor_id=str(sensor_id),
                rule_name=worst_rule["rule_name"],
                message=f"Value {value} triggered {worst_status} threshold"
            )
        else:
            result = EvaluationResult(
                status="OK",
                rule_id="",
                sensor_id=str(sensor_id),
                message="Value within acceptable range"
            )
        
        # Emit threshold.evaluated event
        self._emit_evaluation_event(sensor_id, value, result)
        
        return result

    def _emit_evaluation_event(self, sensor_id: UUID, value: float, result: EvaluationResult):
        """Emit threshold.evaluated event.
        
        Args:
            sensor_id: The sensor that was evaluated
            value: The value that was evaluated
            result: The evaluation result
        """
        emit(
            event_type=EventType.THRESHOLD_EVALUATED,
            source="ThresholdService",
            payload={
                "status": result.status,
                "rule_id": result.rule_id,
                "rule_name": result.rule_name,
                "message": result.message,
            },
            sensor_id=sensor_id,
        )