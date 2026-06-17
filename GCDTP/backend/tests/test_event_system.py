"""Tests for GCDTP Event System."""
import pytest
import threading
from uuid import uuid4
from backend.src.events import (
    EventType,
    EventPayload,
    EventBuilder,
    EventDispatcher,
    get_dispatcher,
    emit,
    subscribe,
    validate_event_structure,
)


class TestEventTypes:
    """Tests for event type registry."""

    def test_event_types_are_strings(self):
        """Test that event types are string values."""
        assert EventType.MEASUREMENT_CREATED == "measurement.created"
        assert EventType.EVENT_CREATED == "event.created"
        assert EventType.HEALTH_UPDATED == "health.updated"

    def test_is_valid_event_type(self):
        """Test validation of event types."""
        from backend.src.events.event_types import is_valid_event_type
        
        assert is_valid_event_type("measurement.created") is True
        assert is_valid_event_type("event.created") is True
        assert is_valid_event_type("invalid.type") is False


class TestEventPayload:
    """Tests for event payload schema."""

    def test_event_payload_creation(self):
        """Test creating an event payload."""
        event = EventPayload(
            event_type="test.event",
            source="TestService",
            payload={"key": "value"},
        )
        
        assert event.event_type == "test.event"
        assert event.source == "TestService"
        assert event.payload["key"] == "value"
        assert event.event_id is not None
        assert event.timestamp is not None

    def test_event_to_dict(self):
        """Test converting event to dictionary."""
        event = EventPayload(
            event_type="test.event",
            source="TestService",
        )
        
        data = event.to_dict()
        assert "event_id" in data
        assert "event_type" in data
        assert "timestamp" in data
        assert "source" in data


class TestEventBuilder:
    """Tests for event builder."""

    def test_create_event(self):
        """Test creating event via builder."""
        event = EventBuilder.create_event(
            event_type=EventType.EVENT_CREATED,
            source="TestService",
            asset_id=uuid4(),
        )
        
        assert event.event_type == "event.created"
        assert event.source == "TestService"
        assert event.asset_id is not None

    def test_create_event_with_correlation(self):
        """Test creating event with correlation ID."""
        correlation_id = uuid4()
        event = EventBuilder.create_event(
            event_type=EventType.MEASUREMENT_CREATED,
            source="TestService",
            correlation_id=correlation_id,
        )
        
        assert event.correlation_id == correlation_id


class TestEventDispatcher:
    """Tests for event dispatcher."""

    def test_dispatcher_is_singleton(self):
        """Test that dispatcher follows singleton pattern."""
        d1 = EventDispatcher()
        d2 = EventDispatcher()
        assert d1 is d2

    def test_emit_returns_event(self):
        """Test that emit returns an event payload."""
        dispatcher = EventDispatcher()
        event = dispatcher.emit(
            event_type=EventType.EVENT_CREATED,
            source="TestService",
        )
        
        assert isinstance(event, EventPayload)
        assert event.event_type == "event.created"

    def test_subscribe_receives_events(self):
        """Test that subscribers receive emitted events."""
        dispatcher = EventDispatcher()
        received = []
        
        def callback(event):
            received.append(event)
        
        unsubscribe = dispatcher.subscribe(
            callback=callback,
            event_types=[EventType.EVENT_CREATED],
        )
        
        dispatcher.emit(
            event_type=EventType.EVENT_CREATED,
            source="TestService",
        )
        
        assert len(received) == 1
        assert received[0].event_type == "event.created"
        
        unsubscribe()

    def test_subscribe_multiple_types(self):
        """Test subscribing to multiple event types."""
        dispatcher = EventDispatcher()
        received = []
        
        def callback(event):
            received.append(event)
        
        unsubscribe = dispatcher.subscribe(
            callback=callback,
            event_types=[EventType.EVENT_CREATED, EventType.HEALTH_UPDATED],
        )
        
        dispatcher.emit(event_type=EventType.EVENT_CREATED, source="Test")
        dispatcher.emit(event_type=EventType.HEALTH_UPDATED, source="Test")
        dispatcher.emit(event_type=EventType.MEASUREMENT_CREATED, source="Test")  # Should not receive
        
        assert len(received) == 2
        
        unsubscribe()

    def test_subscribe_filters_by_asset_id(self):
        """Test subscribing filtered by asset_id."""
        dispatcher = EventDispatcher()
        received = []
        asset_id = uuid4()
        
        def callback(event):
            received.append(event)
        
        unsubscribe = dispatcher.subscribe(
            callback=callback,
            event_types=[EventType.EVENT_CREATED],
            asset_id=asset_id,
        )
        
        dispatcher.emit(
            event_type=EventType.EVENT_CREATED,
            source="Test",
            asset_id=asset_id,
        )
        dispatcher.emit(
            event_type=EventType.EVENT_CREATED,
            source="Test",
            asset_id=uuid4(),  # Different asset
        )
        
        assert len(received) == 1
        
        unsubscribe()

    def test_unsubscribe_stops_events(self):
        """Test that unsubscribe stops event delivery."""
        dispatcher = EventDispatcher()
        received = []
        
        def callback(event):
            received.append(event)
        
        unsubscribe = dispatcher.subscribe(
            callback=callback,
            event_types=[EventType.EVENT_CREATED],
        )
        
        dispatcher.emit(event_type=EventType.EVENT_CREATED, source="Test")
        assert len(received) == 1
        
        unsubscribe()
        
        dispatcher.emit(event_type=EventType.EVENT_CREATED, source="Test")
        assert len(received) == 1  # No new events received

    def test_get_dispatcher_module_function(self):
        """Test get_dispatcher module function."""
        d = get_dispatcher()
        assert d is not None
        assert isinstance(d, EventDispatcher)

    def test_emit_module_function(self):
        """Test emit module function."""
        event = emit(
            event_type=EventType.HEALTH_UPDATED,
            source="TestModule",
        )
        assert event.event_type == "health.updated"

    def test_subscribe_module_function(self):
        """Test subscribe module function."""
        received = []
        
        def callback(event):
            received.append(event)
        
        unsubscribe = subscribe(
            callback=callback,
            event_types=[EventType.EVENT_RESOLVED],
        )
        
        emit(event_type=EventType.EVENT_RESOLVED, source="Test")
        assert len(received) == 1
        
        unsubscribe()

    def test_get_event_history(self):
        """Test getting event history."""
        dispatcher = EventDispatcher()
        
        emit(event_type=EventType.MEASUREMENT_CREATED, source="Test1")
        emit(event_type=EventType.EVENT_CREATED, source="Test2")
        
        history = dispatcher.get_event_history()
        assert len(history) == 2
        
        # Filter by type
        history = dispatcher.get_event_history(event_type=EventType.EVENT_CREATED)
        assert len(history) == 1
        assert history[0].event_type == "event.created"

    def test_get_subscription_count(self):
        """Test getting subscription count."""
        dispatcher = EventDispatcher()
        
        assert dispatcher.get_subscription_count() == 0
        
        unsub1 = dispatcher.subscribe(
            callback=lambda e: None,
            event_types=[EventType.EVENT_CREATED],
        )
        
        assert dispatcher.get_subscription_count() == 1
        
        unsub2 = dispatcher.subscribe(
            callback=lambda e: None,
            event_types=[EventType.HEALTH_UPDATED],
        )
        
        assert dispatcher.get_subscription_count() == 2
        
        unsub1()
        unsub2()
        
        assert dispatcher.get_subscription_count() == 0


class TestEventDispatcherThreadSafety:
    """Tests for thread safety of event dispatcher."""

    def test_concurrent_emissions(self):
        """Test concurrent event emissions."""
        dispatcher = EventDispatcher()
        received = []
        lock = threading.Lock()
        
        def callback(event):
            with lock:
                received.append(event)
        
        unsubscribe = dispatcher.subscribe(
            callback=callback,
            event_types=[EventType.MEASUREMENT_CREATED],
        )
        
        def emit_events():
            for _ in range(10):
                dispatcher.emit(
                    event_type=EventType.MEASUREMENT_CREATED,
                    source="TestThread",
                )
        
        threads = [threading.Thread(target=emit_events) for _ in range(5)]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        assert len(received) == 50
        
        unsubscribe()


class TestValidateEventStructure:
    """Tests for event structure validation."""

    def test_valid_event(self):
        """Test validating a valid event."""
        event = {
            "event_id": str(uuid4()),
            "event_type": "test.event",
            "timestamp": "2026-06-16T10:00:00",
            "source": "TestService",
        }
        
        assert validate_event_structure(event) is True

    def test_missing_event_id(self):
        """Test validation fails without event_id."""
        event = {
            "event_type": "test.event",
            "timestamp": "2026-06-16T10:00:00",
            "source": "TestService",
        }
        
        with pytest.raises(ValueError, match="Missing required field: event_id"):
            validate_event_structure(event)

    def test_missing_event_type(self):
        """Test validation fails without event_type."""
        event = {
            "event_id": str(uuid4()),
            "timestamp": "2026-06-16T10:00:00",
            "source": "TestService",
        }
        
        with pytest.raises(ValueError, match="Missing required field: event_type"):
            validate_event_structure(event)