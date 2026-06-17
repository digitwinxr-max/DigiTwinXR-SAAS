"""Central event type registry for GCDTP.

All event types must be defined here. No string literals allowed elsewhere.
"""
from enum import Enum


class EventType(str, Enum):
    """System-wide event types.
    
    All services must use these constants. No string literals allowed.
    """
    
    # Measurement events
    MEASUREMENT_CREATED = "measurement.created"
    
    # Threshold events
    THRESHOLD_EVALUATED = "threshold.evaluated"
    
    # Event engine events
    EVENT_CREATED = "event.created"
    EVENT_RESOLVED = "event.resolved"
    
    # Health events
    HEALTH_UPDATED = "health.updated"
    
    # Asset events
    ASSET_UPDATED = "asset.updated"
    
    # Sensor events
    SENSOR_CREATED = "sensor.created"
    SENSOR_UPDATED = "sensor.updated"
    SENSOR_DELETED = "sensor.deleted"
    
    # Propagation events (cascading failure)
    PROPAGATION_CREATED = "propagation.created"
    UPSTREAM_FAILURE = "propagation.upstream_failure"
    DOWNSTREAM_FAILURE = "propagation.downstream_failure"
    CHILD_FAILURE = "propagation.child_failure"
    DEPENDENCY_IMPACT = "propagation.dependency_impact"


# Event type to human-readable description mapping
EVENT_DESCRIPTIONS = {
    EventType.MEASUREMENT_CREATED: "A new measurement was recorded",
    EventType.THRESHOLD_EVALUATED: "A threshold rule was evaluated against a measurement",
    EventType.EVENT_CREATED: "A new event was created from a threshold violation",
    EventType.EVENT_RESOLVED: "An event was resolved",
    EventType.HEALTH_UPDATED: "Asset health was recalculated",
    EventType.ASSET_UPDATED: "An asset was created or updated",
    EventType.SENSOR_CREATED: "A new sensor was created",
    EventType.SENSOR_UPDATED: "A sensor was updated",
    EventType.SENSOR_DELETED: "A sensor was deleted",
    EventType.PROPAGATION_CREATED: "A failure was propagated through the asset graph",
    EventType.UPSTREAM_FAILURE: "An upstream asset failure affected this asset",
    EventType.DOWNSTREAM_FAILURE: "A downstream asset failure affected this asset",
    EventType.CHILD_FAILURE: "A child asset failure affected the parent",
    EventType.DEPENDENCY_IMPACT: "A dependency failure impacted this asset",
}


def get_event_description(event_type: EventType) -> str:
    """Get human-readable description for an event type.
    
    Args:
        event_type: The event type constant
        
    Returns:
        Human-readable description
    """
    return EVENT_DESCRIPTIONS.get(event_type, "Unknown event")


def is_valid_event_type(value: str) -> bool:
    """Check if a string is a valid event type.
    
    Args:
        value: String to check
        
    Returns:
        True if valid event type
    """
    try:
        EventType(value)
        return True
    except ValueError:
        return False