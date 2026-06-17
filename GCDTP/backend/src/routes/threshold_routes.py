"""Threshold rule API routes."""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database.config import get_db
from ..schemas.threshold import (
    ThresholdRuleCreate,
    ThresholdRuleUpdate,
    ThresholdRuleResponse,
    ThresholdRuleListResponse,
    EvaluationInput,
    EvaluationResult,
)
from ..services.threshold_service import ThresholdService

router = APIRouter(prefix="/thresholds", tags=["thresholds"])


@router.post("", response_model=ThresholdRuleResponse, status_code=201)
def create_threshold_rule(
    rule_data: ThresholdRuleCreate,
    db: Session = Depends(get_db)
):
    """Create a new threshold rule."""
    service = ThresholdService(db)
    rule = service.create_threshold_rule(rule_data)
    if not rule:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return rule


@router.get("", response_model=ThresholdRuleListResponse)
def get_threshold_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=10000),
    sensor_id: Optional[UUID] = Query(None, description="Filter by sensor ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """Get all threshold rules with optional filtering."""
    service = ThresholdService(db)
    rules, total = service.get_threshold_rules(
        skip=skip,
        limit=limit,
        sensor_id=sensor_id,
        is_active=is_active,
    )
    return ThresholdRuleListResponse(items=rules, total=total)


@router.get("/{rule_id}", response_model=ThresholdRuleResponse)
def get_threshold_rule(
    rule_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a threshold rule by ID."""
    service = ThresholdService(db)
    rule = service.get_threshold_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Threshold rule not found")
    return rule


@router.put("/{rule_id}", response_model=ThresholdRuleResponse)
def update_threshold_rule(
    rule_id: UUID,
    rule_data: ThresholdRuleUpdate,
    db: Session = Depends(get_db)
):
    """Update a threshold rule."""
    service = ThresholdService(db)
    rule = service.update_threshold_rule(rule_id, rule_data)
    if not rule:
        raise HTTPException(status_code=404, detail="Threshold rule not found")
    return rule


@router.delete("/{rule_id}", status_code=204)
def delete_threshold_rule(
    rule_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a threshold rule."""
    service = ThresholdService(db)
    success = service.delete_threshold_rule(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Threshold rule not found")
    return None


# Sensor-threshold relationship endpoints
@router.get("/sensor/{sensor_id}", response_model=ThresholdRuleListResponse)
def get_thresholds_by_sensor(
    sensor_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all threshold rules for a specific sensor."""
    service = ThresholdService(db)
    rules = service.get_thresholds_by_sensor(sensor_id)
    return ThresholdRuleListResponse(items=rules, total=len(rules))


# Evaluation endpoint
@router.post("/evaluate", response_model=EvaluationResult)
def evaluate_measurement(
    evaluation_data: EvaluationInput,
    db: Session = Depends(get_db)
):
    """Evaluate a measurement value against threshold rules.
    
    Returns the evaluation result with status (OK, WARNING, or CRITICAL).
    """
    service = ThresholdService(db)
    result = service.evaluate_measurement(
        sensor_id=evaluation_data.sensor_id,
        value=evaluation_data.value,
    )
    return result