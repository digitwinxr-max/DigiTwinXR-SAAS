"""Event API routes."""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database.config import get_db
from ..schemas.event import (
    EventCreate,
    EventResponse,
    EventListResponse,
    EventResolveRequest,
    EvaluationResultInput,
    MeasurementInput,
)
from ..services.event_service import EventService

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/from-evaluation", response_model=EventResponse, status_code=201)
def create_event_from_evaluation(
    evaluation: EvaluationResultInput,
    measurement: MeasurementInput,
    db: Session = Depends(get_db)
):
    """Create an event from threshold evaluation result.
    
    Only creates event if status is WARNING or CRITICAL.
    Returns null if evaluation was OK.
    """
    service = EventService(db)
    event = service.create_event_from_evaluation(evaluation, measurement)
    
    if not event:
        return {"message": "No event created (evaluation was OK)"}
    
    return event


@router.post("/manual", response_model=EventResponse, status_code=201)
def create_event_manual(
    event_data: EventCreate,
    db: Session = Depends(get_db)
):
    """Create a new event manually."""
    service = EventService(db)
    event = service.create_event(event_data)
    return event


@router.get("", response_model=EventListResponse)
def get_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=10000),
    sensor_id: Optional[UUID] = Query(None, description="Filter by sensor ID"),
    asset_id: Optional[UUID] = Query(None, description="Filter by asset ID"),
    status: Optional[str] = Query(None, description="Filter by status (ACTIVE, RESOLVED)"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    db: Session = Depends(get_db)
):
    """Get all events with optional filtering."""
    service = EventService(db)
    events, total = service.get_events(
        skip=skip,
        limit=limit,
        sensor_id=sensor_id,
        asset_id=asset_id,
        status=status,
        severity=severity,
        event_type=event_type,
    )
    return EventListResponse(items=events, total=total)


@router.get("/active", response_model=EventListResponse)
def get_active_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=10000),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    db: Session = Depends(get_db)
):
    """Get all active (unresolved) events."""
    service = EventService(db)
    events, total = service.get_active_events(
        skip=skip,
        limit=limit,
        severity=severity,
    )
    return EventListResponse(items=events, total=total)


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: UUID,
    db: Session = Depends(get_db)
):
    """Get an event by ID."""
    service = EventService(db)
    event = service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.patch("/{event_id}/resolve", response_model=EventResponse)
def resolve_event(
    event_id: UUID,
    resolve_data: EventResolveRequest = None,
    db: Session = Depends(get_db)
):
    """Mark an event as resolved."""
    service = EventService(db)
    
    resolution_notes = resolve_data.resolution_notes if resolve_data else None
    event = service.resolve_event(event_id, resolution_notes)
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


# Additional convenience endpoints
@router.get("/sensor/{sensor_id}", response_model=EventListResponse)
def get_events_by_sensor(
    sensor_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all events for a specific sensor."""
    service = EventService(db)
    events = service.get_events_by_sensor(sensor_id)
    return EventListResponse(items=events, total=len(events))


@router.get("/asset/{asset_id}", response_model=EventListResponse)
def get_events_by_asset(
    asset_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all events for a specific asset."""
    service = EventService(db)
    events = service.get_events_by_asset(asset_id)
    return EventListResponse(items=events, total=len(events))