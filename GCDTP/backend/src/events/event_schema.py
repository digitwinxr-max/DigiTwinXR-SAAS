"""Standard event payload schema for GCDTP.

All events MUST follow this schema for consistency.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class EventPayload(BaseModel):
    """Standard event payload structure.
    
    All events in GCDTP MUST follow this schema.
    
    Required fields:
    - event_id: Unique identifier for this event
    - event_type: Type of event (from EventType enum)
    - timestamp: When the event occurred
    - source: Service/component that generated the event
    
    Optional fields:
    - correlation_id: For tracing related events
    - asset_id: Associated asset (if applicable)
    - sensor_id: Associated sensor (if applicable)
    - payload: Event-specific data
    """
    event_id: UUID = Field(default_factory=uuid4)
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str
    correlation_id: Optional[UUID] = None
    asset_id: Optional[UUID] = None
    sensor_id: Optional[UUID] = None
    payload: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "correlation_id": str(self.correlation_id) if self.correlation_id else None,
            "asset_id": str(self.asset_id) if self.asset_id else None,
            "sensor_id": str(self.sensor_id) if self.sensor_id else None,
            "payload": self.payload,
        }


class EventBuilder:
    """Helper class to build standardized events."""
    
    @staticmethod
    def create_event(
        event_type: str,
        source: str,
        payload: Optional[Dict[str, Any]] = None,
        asset_id: Optional[UUID] = None,
        sensor_id: Optional[UUID] = None,
        correlation_id: Optional[UUID] = None,
    ) -> EventPayload:
        """Create a standardized event payload.
        
        Args:
            event_type: Type of event (use EventType constants)
            source: Service/component generating the event
            payload: Event-specific data
            asset_id: Associated asset ID
            sensor_id: Associated sensor ID
            correlation_id: For tracing related events
            
        Returns:
            Standardized EventPayload
        """
        return EventPayload(
            event_type=event_type,
            source=source,
            payload=payload or {},
            asset_id=asset_id,
            sensor_id=sensor_id,
            correlation_id=correlation_id,
        )


def validate_event_structure(event_data: Dict[str, Any]) -> bool:
    """Validate that an event follows the standard schema.
    
    Args:
        event_data: Event dictionary to validate
        
    Returns:
        True if valid, raises ValueError if invalid
    """
    required_fields = ["event_id", "event_type", "timestamp", "source"]
    
    for field in required_fields:
        if field not in event_data:
            raise ValueError(f"Missing required field: {field}")
    
    return True