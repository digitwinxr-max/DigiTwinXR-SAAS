"""Centralized event dispatcher for GCDTP.

Single entry point for all event emissions across the system.
"""
import logging
import threading
from datetime import datetime
from typing import Dict, List, Callable, Optional, Any
from uuid import UUID, uuid4
from dataclasses import dataclass

from .event_types import EventType, get_event_description
from .event_schema import EventPayload, EventBuilder


logger = logging.getLogger(__name__)


@dataclass
class EventSubscription:
    """Subscription to event types."""
    callback: Callable[[EventPayload], None]
    event_types: List[str]
    asset_id_filter: Optional[UUID] = None
    sensor_id_filter: Optional[UUID] = None


class EventDispatcher:
    """Centralized event dispatcher.
    
    Single entry point for emitting and subscribing to events.
    Thread-safe, in-memory only, no external dependencies.
    """
    
    _instance: Optional['EventDispatcher'] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern for global dispatcher."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize dispatcher state."""
        if self._initialized:
            return
            
        self._subscriptions: List[EventSubscription] = []
        self._subscription_lock = threading.Lock()
        self._event_history: List[EventPayload] = []
        self._history_lock = threading.Lock()
        self._history_max_size = 1000
        
        self._initialized = True
        logger.info("EventDispatcher initialized")
    
    def emit(
        self,
        event_type: str,
        source: str,
        payload: Optional[Dict[str, Any]] = None,
        asset_id: Optional[UUID] = None,
        sensor_id: Optional[UUID] = None,
        correlation_id: Optional[UUID] = None,
    ) -> EventPayload:
        """Emit a standardized event.
        
        This is the SINGLE ENTRY POINT for all event emissions.
        All services MUST use this method.
        
        Args:
            event_type: Type of event (use EventType constants)
            source: Service/component generating the event
            payload: Event-specific data
            asset_id: Associated asset ID
            sensor_id: Associated sensor ID
            correlation_id: For tracing related events
            
        Returns:
            The created EventPayload
        """
        event = EventBuilder.create_event(
            event_type=event_type,
            source=source,
            payload=payload,
            asset_id=asset_id,
            sensor_id=sensor_id,
            correlation_id=correlation_id,
        )
        
        self._dispatch_event(event)
        
        return event
    
    def _dispatch_event(self, event: EventPayload):
        """Internal method to dispatch event to subscribers.
        
        Args:
            event: The event to dispatch
        """
        # Log the event
        logger.info(
            f"Event emitted: type={event.event_type}, "
            f"source={event.source}, event_id={event.event_id}"
        )
        
        # Store in history
        with self._history_lock:
            self._event_history.append(event)
            # Trim history if needed
            if len(self._event_history) > self._history_max_size:
                self._event_history = self._event_history[-self._history_max_size:]
        
        # Notify subscribers
        with self._subscription_lock:
            for subscription in self._subscriptions:
                self._notify_subscriber(subscription, event)
    
    def _notify_subscriber(self, subscription: EventSubscription, event: EventPayload):
        """Notify a subscriber of an event.
        
        Args:
            subscription: The subscription to notify
            event: The event to deliver
        """
        # Check if subscriber wants this event type
        if event.event_type not in subscription.event_types:
            return
        
        # Check asset_id filter
        if subscription.asset_id_filter is not None:
            if event.asset_id != subscription.asset_id_filter:
                return
        
        # Check sensor_id filter
        if subscription.sensor_id_filter is not None:
            if event.sensor_id != subscription.sensor_id_filter:
                return
        
        # Deliver event
        try:
            subscription.callback(event)
        except Exception as e:
            logger.error(f"Error in event subscriber: {e}")
    
    def subscribe(
        self,
        callback: Callable[[EventPayload], None],
        event_types: List[str],
        asset_id: Optional[UUID] = None,
        sensor_id: Optional[UUID] = None,
    ) -> Callable[[], None]:
        """Subscribe to events.
        
        Args:
            callback: Function to call when matching events are emitted
            event_types: List of event types to subscribe to
            asset_id: Optional filter for specific asset
            sensor_id: Optional filter for specific sensor
            
        Returns:
            Unsubscribe function to call to stop receiving events
        """
        subscription = EventSubscription(
            callback=callback,
            event_types=event_types,
            asset_id_filter=asset_id,
            sensor_id_filter=sensor_id,
        )
        
        with self._subscription_lock:
            self._subscriptions.append(subscription)
        
        logger.debug(f"New subscription for types: {event_types}")
        
        def unsubscribe():
            """Unsubscribe from events."""
            with self._subscription_lock:
                if subscription in self._subscriptions:
                    self._subscriptions.remove(subscription)
            logger.debug(f"Unsubscribed from types: {event_types}")
        
        return unsubscribe
    
    def get_event_history(
        self,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[EventPayload]:
        """Get recent event history.
        
        Args:
            event_type: Optional filter by event type
            limit: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        with self._history_lock:
            events = self._event_history
            
            if event_type:
                events = [e for e in events if e.event_type == event_type]
            
            return events[-limit:]
    
    def clear_history(self):
        """Clear event history."""
        with self._history_lock:
            self._event_history.clear()
        logger.info("Event history cleared")
    
    def get_subscription_count(self) -> int:
        """Get number of active subscriptions."""
        with self._subscription_lock:
            return len(self._subscriptions)


# Module-level convenience functions

_dispatcher: Optional[EventDispatcher] = None


def get_dispatcher() -> EventDispatcher:
    """Get the global event dispatcher instance."""
    global _dispatcher
    if _dispatcher is None:
        _dispatcher = EventDispatcher()
    return _dispatcher


def emit(
    event_type: str,
    source: str,
    payload: Optional[Dict[str, Any]] = None,
    asset_id: Optional[UUID] = None,
    sensor_id: Optional[UUID] = None,
    correlation_id: Optional[UUID] = None,
) -> EventPayload:
    """Convenience function to emit events via global dispatcher.
    
    Args:
        event_type: Type of event (use EventType constants)
        source: Service/component generating the event
        payload: Event-specific data
        asset_id: Associated asset ID
        sensor_id: Associated sensor ID
        correlation_id: For tracing related events
        
    Returns:
        The created EventPayload
    """
    return get_dispatcher().emit(
        event_type=event_type,
        source=source,
        payload=payload,
        asset_id=asset_id,
        sensor_id=sensor_id,
        correlation_id=correlation_id,
    )


def subscribe(
    callback: Callable[[EventPayload], None],
    event_types: List[str],
    asset_id: Optional[UUID] = None,
    sensor_id: Optional[UUID] = None,
) -> Callable[[], None]:
    """Convenience function to subscribe via global dispatcher.
    
    Args:
        callback: Function to call when matching events are emitted
        event_types: List of event types to subscribe to
        asset_id: Optional filter for specific asset
        sensor_id: Optional filter for specific sensor
        
    Returns:
        Unsubscribe function
    """
    return get_dispatcher().subscribe(
        callback=callback,
        event_types=event_types,
        asset_id=asset_id,
        sensor_id=sensor_id,
    )