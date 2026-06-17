"""GCDTP Events Module.

Centralized event system for GCDTP.
"""
from .event_types import EventType, get_event_description, is_valid_event_type
from .event_schema import EventPayload, EventBuilder, validate_event_structure
from .event_dispatcher import EventDispatcher, get_dispatcher, emit, subscribe

__all__ = [
    # Types
    "EventType",
    # Schema
    "EventPayload",
    "EventBuilder",
    "validate_event_structure",
    # Dispatcher
    "EventDispatcher",
    "get_dispatcher",
    "emit",
    "subscribe",
    # Utilities
    "get_event_description",
    "is_valid_event_type",
]