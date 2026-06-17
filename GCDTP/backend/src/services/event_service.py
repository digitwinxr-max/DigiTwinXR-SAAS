"""Event service for business logic."""
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models.event import Event
from ..models.sensor import Sensor
from ..schemas.event import EventCreate, EvaluationResultInput, MeasurementInput
from ..events import emit, EventType


class EventService:
    """Service class for event operations."""

    def __init__(self, db: Session):
        self.db = db

    def _recalculate_asset_health(self, asset_id: UUID):
        """Recalculate health for an asset after event changes.
        
        This is called after event creation/resolution to keep
        health state synchronized with events.
        """
        from ..services.health_service import HealthService
        health_service = HealthService(self.db)
        health_service.recalculate_health(asset_id)

    def create_event(self, event_data: EventCreate) -> Event:
        """Create a new event.
        
        Emits event.created event via dispatcher.
        Triggers failure propagation for WARNING/CRITICAL events.
        """
        event = Event(
            sensor_id=event_data.sensor_id,
            asset_id=event_data.asset_id,
            event_type=event_data.event_type,
            severity=event_data.severity,
            message=event_data.message,
            value=event_data.value,
            threshold_rule_id=event_data.threshold_rule_id,
            timestamp=event_data.timestamp or datetime.utcnow(),
            status=event_data.status,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        
        # Trigger health recalculation for the asset
        self._recalculate_asset_health(event_data.asset_id)
        
        # Propagate failure for WARNING and CRITICAL events
        if event.severity in ('WARNING', 'CRITICAL'):
            self._propagate_failure(event)
        
        # Emit event.created event
        emit(
            event_type=EventType.EVENT_CREATED,
            source="EventService",
            payload={
                "event_id": str(event.id),
                "event_type": event.event_type,
                "severity": event.severity,
                "message": event.message,
                "status": event.status,
            },
            asset_id=event.asset_id,
            sensor_id=event.sensor_id,
        )
        
        return event

    def _propagate_failure(self, event: Event):
        """Propagate failure through asset relationships.
        
        Args:
            event: The event to propagate
        """
        from .failure_propagation_service import FailurePropagationService
        
        try:
            propagation_service = FailurePropagationService(self.db)
            propagated_count, affected_assets = propagation_service.propagate_event(event.id)
            
            if propagated_count > 0:
                # Emit propagation created event
                emit(
                    event_type=EventType.PROPAGATION_CREATED,
                    source="EventService",
                    payload={
                        "source_event_id": str(event.id),
                        "propagated_count": propagated_count,
                        "affected_assets": [str(a) for a in affected_assets],
                    },
                    asset_id=event.asset_id,
                )
        except Exception as e:
            # Log but don't fail event creation if propagation fails
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to propagate failure: {e}")

    def create_event_from_evaluation(
        self,
        evaluation_result: EvaluationResultInput,
        measurement: MeasurementInput,
    ) -> Optional[Event]:
        """Create an event from threshold evaluation result.
        
        Rules:
        - If status == OK, DO NOT create event
        - If WARNING or CRITICAL, create event linked to sensor, asset, and threshold rule
        
        Args:
            evaluation_result: Result from threshold evaluation
            measurement: The measurement that was evaluated
            
        Returns:
            Event if created, None if evaluation was OK
        """
        # Don't create events for OK status
        if evaluation_result.status == "OK":
            return None
        
        # Get sensor with asset relationship
        sensor = self.db.query(Sensor).filter(Sensor.id == measurement.sensor_id).first()
        if not sensor:
            return None
        
        # Create event from evaluation
        event_data = EventCreate(
            sensor_id=measurement.sensor_id,
            asset_id=sensor.asset_id,  # Derived from sensor
            event_type="THRESHOLD_VIOLATION",
            severity=evaluation_result.status,
            message=evaluation_result.message or f"Threshold violation: {evaluation_result.status}",
            value=measurement.value,
            threshold_rule_id=UUID(evaluation_result.rule_id) if evaluation_result.rule_id else None,
            timestamp=measurement.timestamp,
        )
        
        # Note: create_event will trigger health recalculation and emit event
        return self.create_event(event_data)

    def get_event(self, event_id: UUID) -> Optional[Event]:
        """Get an event by ID."""
        return self.db.query(Event).filter(Event.id == event_id).first()

    def get_events(
        self,
        skip: int = 0,
        limit: int = 100,
        sensor_id: Optional[UUID] = None,
        asset_id: Optional[UUID] = None,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        event_type: Optional[str] = None,
    ) -> tuple[List[Event], int]:
        """Get all events with optional filtering."""
        query = self.db.query(Event)

        if sensor_id:
            query = query.filter(Event.sensor_id == sensor_id)
        if asset_id:
            query = query.filter(Event.asset_id == asset_id)
        if status:
            query = query.filter(Event.status == status)
        if severity:
            query = query.filter(Event.severity == severity)
        if event_type:
            query = query.filter(Event.event_type == event_type)

        total = query.count()
        events = query.order_by(desc(Event.timestamp)).offset(skip).limit(limit).all()

        return events, total

    def get_active_events(
        self,
        skip: int = 0,
        limit: int = 100,
        severity: Optional[str] = None,
    ) -> tuple[List[Event], int]:
        """Get all active (unresolved) events."""
        query = self.db.query(Event).filter(Event.status == "ACTIVE")

        if severity:
            query = query.filter(Event.severity == severity)

        total = query.count()
        events = query.order_by(desc(Event.timestamp)).offset(skip).limit(limit).all()

        return events, total

    def resolve_event(
        self,
        event_id: UUID,
        resolution_notes: Optional[str] = None,
    ) -> Optional[Event]:
        """Mark an event as resolved.
        
        Emits event.resolved event via dispatcher.
        Cleans up propagated events for this source event.
        """
        event = self.get_event(event_id)
        if not event:
            return None

        event.status = "RESOLVED"
        if resolution_notes:
            event.message = f"{event.message}\n[Resolved]: {resolution_notes}"
        
        self.db.commit()
        self.db.refresh(event)
        
        # Trigger health recalculation for the asset
        self._recalculate_asset_health(event.asset_id)
        
        # Clean up propagated events for this source event
        self._cleanup_propagations(event_id)
        
        # Emit event.resolved event
        emit(
            event_type=EventType.EVENT_RESOLVED,
            source="EventService",
            payload={
                "event_id": str(event.id),
                "event_type": event.event_type,
                "severity": event.severity,
                "resolution_notes": resolution_notes,
            },
            asset_id=event.asset_id,
            sensor_id=event.sensor_id,
        )
        
        return event

    def _cleanup_propagations(self, event_id: UUID):
        """Clean up propagated events when source event is resolved.
        
        Args:
            event_id: The source event ID
        """
        from .failure_propagation_service import FailurePropagationService
        
        try:
            propagation_service = FailurePropagationService(self.db)
            propagations = propagation_service.get_event_propagation(event_id)
            
            for prop in propagations:
                self.db.delete(prop)
            
            self.db.commit()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to cleanup propagations: {e}")

    def get_events_by_sensor(self, sensor_id: UUID) -> List[Event]:
        """Get all events for a specific sensor."""
        return self.db.query(Event).filter(
            Event.sensor_id == sensor_id
        ).order_by(desc(Event.timestamp)).all()

    def get_events_by_asset(self, asset_id: UUID) -> List[Event]:
        """Get all events for a specific asset."""
        return self.db.query(Event).filter(
            Event.asset_id == asset_id
        ).order_by(desc(Event.timestamp)).all()

    def get_active_event_count(self) -> int:
        """Get count of active events."""
        return self.db.query(Event).filter(Event.status == "ACTIVE").count()

    def get_critical_event_count(self) -> int:
        """Get count of active critical events."""
        return self.db.query(Event).filter(
            Event.status == "ACTIVE",
            Event.severity == "CRITICAL",
        ).count()