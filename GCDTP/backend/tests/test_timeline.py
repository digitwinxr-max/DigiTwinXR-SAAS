"""
Tests for Timeline and Replay Engines

Tests event recording, snapshot management, timeline building, replay, and diff.
"""

import pytest
import uuid
from datetime import datetime, timedelta
from backend.src.services.timeline import (
    TimelineEvent,
    TimelineSnapshot,
    TimelineSegment,
    ReplaySession,
    Timeline,
    EventRecorder,
    SnapshotManager,
    TimelineEngine,
    ReplayEngine,
    DeterministicReplayEngine,
    TimelineQueryEngine,
    DiffEngine,
    TimelineValidator,
    Severity,
    TimelineEventType,
    ReplayState,
    AssetState,
    FlowState,
)


class TestTimelineTypes:
    """Tests for timeline types."""
    
    def test_create_timeline_event(self):
        """Test creating a timeline event."""
        event = TimelineEvent(
            event_id="evt-1",
            timestamp=datetime.now(),
            event_type=TimelineEventType.NODE_FAILED,
            source_engine="resilience",
            entity_id="node-1",
            payload={"reason": "power_outage"},
            severity=Severity.ERROR
        )
        
        assert event.event_id == "evt-1"
        assert event.event_type == TimelineEventType.NODE_FAILED
        assert event.severity == Severity.ERROR
    
    def test_timeline_event_to_dict(self):
        """Test event serialization."""
        event = TimelineEvent(
            event_id="evt-1",
            timestamp=datetime.now(),
            event_type=TimelineEventType.NODE_FAILED,
            source_engine="test",
            entity_id="node-1"
        )
        
        data = event.to_dict()
        assert "event_id" in data
        assert "timestamp" in data
        assert data["event_type"] == "node_failed"
    
    def test_create_asset_state(self):
        """Test creating asset state."""
        state = AssetState(
            asset_id="asset-1",
            status="operational",
            health=1.0,
            load=50.0,
            capacity=100.0
        )
        
        assert state.asset_id == "asset-1"
        assert state.health == 1.0
    
    def test_create_flow_state(self):
        """Test creating flow state."""
        flow = FlowState(
            route_id="route-1",
            source="a",
            destination="b",
            path=["a", "c", "b"],
            load=80.0,
            utilization=0.8,
            status="stable"
        )
        
        assert len(flow.path) == 3
        assert flow.utilization == 0.8


class TestEventRecorder:
    """Tests for event recorder."""
    
    def test_start_stop_recording(self):
        """Test starting and stopping recording."""
        recorder = EventRecorder()
        
        recorder.start_recording()
        assert recorder._is_recording is True
        
        events = recorder.stop_recording()
        assert recorder._is_recording is False
    
    def test_manual_event_recording(self):
        """Test manually recording events."""
        recorder = EventRecorder()
        
        event = recorder.record_event(
            event_type=TimelineEventType.NODE_FAILED,
            source_engine="test",
            entity_id="node-1",
            severity=Severity.ERROR
        )
        
        assert event.event_id is not None
        assert len(recorder.recorded_events) == 1
    
    def test_batch_record(self):
        """Test batch recording."""
        recorder = EventRecorder()
        
        events = recorder.batch_record([
            {
                "event_type": "node_failed",
                "source_engine": "test",
                "entity_id": "node-1",
                "timestamp": datetime.now().isoformat()
            },
            {
                "event_type": "node_recovered",
                "source_engine": "test",
                "entity_id": "node-1",
                "timestamp": datetime.now().isoformat()
            }
        ])
        
        assert len(events) == 2
        assert len(recorder.recorded_events) == 2
    
    def test_filter_events(self):
        """Test event filtering."""
        recorder = EventRecorder()
        
        recorder.record_event(
            TimelineEventType.NODE_FAILED, "test", "node-1", severity=Severity.ERROR
        )
        recorder.record_event(
            TimelineEventType.NODE_RECOVERED, "test", "node-1", severity=Severity.INFO
        )
        recorder.record_event(
            TimelineEventType.EDGE_FAILED, "test", "edge-1", severity=Severity.ERROR
        )
        
        # Filter by type
        failures = recorder.filter_events(
            event_types=[TimelineEventType.NODE_FAILED]
        )
        assert len(failures) == 1
        
        # Filter by severity
        errors = recorder.filter_events(
            severities=[Severity.ERROR]
        )
        assert len(errors) == 2
    
    def test_get_stats(self):
        """Test getting recording stats."""
        recorder = EventRecorder()
        
        recorder.record_event(
            TimelineEventType.NODE_FAILED, "engine1", "node-1", severity=Severity.ERROR
        )
        recorder.record_event(
            TimelineEventType.NODE_RECOVERED, "engine1", "node-1", severity=Severity.INFO
        )
        
        stats = recorder.get_stats()
        assert stats["total_events"] == 2
        assert "node_failed" in stats["events_by_type"]
        assert "engine1" in stats["events_by_source"]


class TestSnapshotManager:
    """Tests for snapshot manager."""
    
    def test_capture_snapshot(self):
        """Test capturing a snapshot."""
        manager = SnapshotManager()
        
        snapshot = manager.capture_snapshot(
            snapshot_id="snap-1",
            metadata={"label": "before_test"}
        )
        
        assert snapshot.snapshot_id == "snap-1"
        assert snapshot.timestamp is not None
    
    def test_restore_snapshot(self):
        """Test restoring a snapshot."""
        manager = SnapshotManager()
        
        manager.capture_snapshot(snapshot_id="snap-1")
        
        restored = manager.restore_snapshot("snap-1")
        assert restored is not None
        assert restored.snapshot_id == "snap-1"
    
    def test_list_snapshots(self):
        """Test listing snapshots."""
        manager = SnapshotManager()
        
        manager.capture_snapshot(snapshot_id="snap-1")
        manager.capture_snapshot(snapshot_id="snap-2")
        
        snapshots = manager.list_snapshots()
        assert len(snapshots) == 2
    
    def test_prune_snapshots(self):
        """Test pruning old snapshots."""
        manager = SnapshotManager()
        
        # Create snapshots
        manager.capture_snapshot(snapshot_id="snap-1")
        manager.capture_snapshot(snapshot_id="snap-2")
        manager.capture_snapshot(snapshot_id="snap-3")
        
        # Keep only 2
        deleted = manager.prune_snapshots(keep_count=2)
        
        assert len(deleted) == 1
        
        remaining = manager.list_snapshots()
        assert len(remaining) == 2


class TestTimelineEngine:
    """Tests for timeline engine."""
    
    def test_start_stop_recording(self):
        """Test starting and stopping timeline recording."""
        engine = TimelineEngine()
        
        timeline = engine.start_recording(
            name="test_recording",
            description="Test timeline"
        )
        
        assert engine._is_recording is True
        assert timeline.name == "test_recording"
        
        result = engine.stop_recording()
        assert result is not None
        assert engine._is_recording is False
    
    def test_add_event_to_timeline(self):
        """Test adding events during recording."""
        engine = TimelineEngine()
        
        engine.start_recording()
        
        event = engine.add_event(
            event_type=TimelineEventType.NODE_FAILED,
            source_engine="test",
            entity_id="node-1",
            severity=Severity.ERROR
        )
        
        assert event is not None
        assert len(engine.recorder.recorded_events) == 1
        
        engine.stop_recording()
    
    def test_capture_snapshot_during_recording(self):
        """Test capturing snapshots during recording."""
        engine = TimelineEngine()
        
        engine.start_recording()
        
        snapshot = engine.capture_snapshot(label="test-snap")
        
        assert snapshot is not None
        
        engine.stop_recording()
    
    def test_get_recording_status(self):
        """Test getting recording status."""
        engine = TimelineEngine()
        
        engine.start_recording()
        
        status = engine.get_recording_status()
        assert status["is_recording"] is True
        assert status["total_timelines"] == 1
        
        engine.stop_recording()


class TestReplayEngine:
    """Tests for replay engine."""
    
    @pytest.fixture
    def sample_segment(self):
        """Create a sample timeline segment."""
        events = [
            TimelineEvent(
                event_id=f"evt-{i}",
                timestamp=datetime.now() + timedelta(minutes=i),
                event_type=TimelineEventType.NODE_FAILED,
                source_engine="test",
                entity_id="node-1",
                severity=Severity.ERROR
            )
            for i in range(5)
        ]
        
        return TimelineSegment(
            segment_id="seg-1",
            start_time=events[0].timestamp,
            end_time=events[-1].timestamp,
            events=events
        )
    
    def test_create_session(self, sample_segment):
        """Test creating a replay session."""
        engine = ReplayEngine()
        
        session = engine.create_session(sample_segment)
        
        assert session is not None
        assert session.session_id is not None
        assert session.total_events == 5
        assert session.current_index == 0
    
    def test_play_pause_stop(self, sample_segment):
        """Test play, pause, stop controls."""
        engine = ReplayEngine()
        engine.create_session(sample_segment)
        
        # Play
        result = engine.play()
        assert result is True
        assert engine.current_session.state == ReplayState.PLAYING
        
        # Pause
        result = engine.pause()
        assert result is True
        assert engine.current_session.state == ReplayState.PAUSED
        
        # Resume
        result = engine.resume()
        assert result is True
        
        # Stop
        result = engine.stop()
        assert result is True
        assert engine.current_session.state == ReplayState.STOPPED
    
    def test_step_forward_backward(self, sample_segment):
        """Test stepping through events."""
        engine = ReplayEngine()
        engine.create_session(sample_segment)
        
        # Step forward
        event = engine.step_forward()
        assert event is not None
        assert engine.current_session.current_index == 1
        
        # Step backward
        event = engine.step_backward()
        assert event is not None
        assert engine.current_session.current_index == 0
    
    def test_seek(self, sample_segment):
        """Test seeking to timestamp."""
        engine = ReplayEngine()
        engine.create_session(sample_segment)
        
        target_time = sample_segment.events[2].timestamp
        
        result = engine.seek(target_time)
        assert result is True
        assert engine.current_session.current_index == 2
    
    def test_change_speed(self, sample_segment):
        """Test changing playback speed."""
        engine = ReplayEngine()
        engine.create_session(sample_segment)
        
        result = engine.change_speed(2.0)
        assert result is True
        assert engine.current_session.speed == 2.0
        
        # Invalid speed
        result = engine.change_speed(3.0)  # Not in available speeds
        assert result is False
    
    def test_get_current_event(self, sample_segment):
        """Test getting current event."""
        engine = ReplayEngine()
        engine.create_session(sample_segment)
        
        event = engine.get_current_event()
        assert event is not None
        assert event.event_id == "evt-0"
        
        engine.step_forward()
        event = engine.get_current_event()
        assert event.event_id == "evt-1"
    
    def test_progress(self, sample_segment):
        """Test progress tracking."""
        engine = ReplayEngine()
        engine.create_session(sample_segment)
        
        assert engine.current_session.progress == 0.0
        
        engine.step_forward()
        engine.step_forward()
        
        assert engine.current_session.progress == 0.4  # 2/5
    
    def test_create_branch(self, sample_segment):
        """Test creating branch session."""
        engine = ReplayEngine()
        engine.create_session(sample_segment)
        
        engine.seek_to_index(2)
        
        branch = engine.create_branch("alt-history")
        
        assert branch is not None
        assert branch.is_branch is True
        assert branch.parent_session_id == engine.current_session.session_id


class TestTimelineQueryEngine:
    """Tests for timeline query engine."""
    
    @pytest.fixture
    def sample_timeline(self):
        """Create a sample timeline."""
        events = [
            TimelineEvent(
                event_id="evt-1",
                timestamp=datetime.now(),
                event_type=TimelineEventType.NODE_FAILED,
                source_engine="resilience",
                entity_id="node-1",
                severity=Severity.ERROR
            ),
            TimelineEvent(
                event_id="evt-2",
                timestamp=datetime.now() + timedelta(minutes=5),
                event_type=TimelineEventType.EDGE_OVERLOADED,
                source_engine="flow",
                entity_id="edge-1",
                severity=Severity.WARNING
            ),
            TimelineEvent(
                event_id="evt-3",
                timestamp=datetime.now() + timedelta(minutes=10),
                event_type=TimelineEventType.NODE_RECOVERED,
                source_engine="recovery",
                entity_id="node-1",
                severity=Severity.INFO
            ),
        ]
        
        timeline = Timeline(
            timeline_id="tl-1",
            name="Test Timeline",
            description="Test",
            start_time=events[0].timestamp,
            end_time=events[-1].timestamp,
            events=events
        )
        
        return timeline
    
    def test_get_events_between(self, sample_timeline):
        """Test getting events in time range."""
        engine = TimelineQueryEngine(sample_timeline)
        
        start = datetime.now()
        end = datetime.now() + timedelta(minutes=7)
        
        events = engine.get_events_between(start, end)
        
        assert len(events) == 2
    
    def test_get_failures(self, sample_timeline):
        """Test getting failure events."""
        engine = TimelineQueryEngine(sample_timeline)
        
        failures = engine.get_failures()
        
        assert len(failures) >= 1
    
    def test_get_events_by_asset(self, sample_timeline):
        """Test getting events by asset."""
        engine = TimelineQueryEngine(sample_timeline)
        
        events = engine.get_events_by_asset("node-1")
        
        assert len(events) == 2
    
    def test_get_event_summary(self, sample_timeline):
        """Test getting event summary."""
        engine = TimelineQueryEngine(sample_timeline)
        
        summary = engine.get_event_summary()
        
        assert summary["total_events"] == 3
        assert "node_failed" in summary["by_type"]


class TestDiffEngine:
    """Tests for diff engine."""
    
    def test_diff_snapshots(self):
        """Test diffing two snapshots."""
        engine = DiffEngine()
        
        snap_a = TimelineSnapshot(
            snapshot_id="snap-a",
            timestamp=datetime.now(),
            graph_snapshot={
                "nodes": {"a": {}, "b": {}},
                "edges": [{"from_node": "a", "to_node": "b"}]
            }
        )
        
        snap_b = TimelineSnapshot(
            snapshot_id="snap-b",
            timestamp=datetime.now() + timedelta(minutes=5),
            graph_snapshot={
                "nodes": {"a": {}, "b": {}, "c": {}},
                "edges": [{"from_node": "a", "to_node": "b"}]
            }
        )
        
        result = engine.diff_snapshots(snap_a, snap_b)
        
        assert "c" in result.nodes_added
        assert result.total_changes >= 1
    
    def test_generate_change_report(self):
        """Test generating change report."""
        engine = DiffEngine()
        
        snap_a = TimelineSnapshot(
            snapshot_id="snap-a",
            timestamp=datetime.now(),
            graph_snapshot={
                "nodes": {"a": {}},
                "edges": []
            }
        )
        
        snap_b = TimelineSnapshot(
            snapshot_id="snap-b",
            timestamp=datetime.now(),
            graph_snapshot={
                "nodes": {"a": {}, "b": {}},
                "edges": []
            }
        )
        
        result = engine.diff_snapshots(snap_a, snap_b)
        report = engine.generate_change_report(result)
        
        assert "SNAPSHOT DIFF REPORT" in report
        assert "Nodes Added" in report


class TestTimelineValidator:
    """Tests for timeline validator."""
    
    def test_validate_timeline(self):
        """Test validating a timeline."""
        validator = TimelineValidator()
        
        timeline = Timeline(
            timeline_id="tl-1",
            name="Test",
            description="Test",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1)
        )
        
        result = validator.validate_timeline(timeline)
        
        assert result["valid"] is True
    
    def test_validate_event_ordering(self):
        """Test event ordering validation."""
        validator = TimelineValidator()
        
        events = [
            TimelineEvent(
                event_id="evt-1",
                timestamp=datetime.now() + timedelta(minutes=5),
                event_type=TimelineEventType.NODE_FAILED,
                source_engine="test",
                entity_id="node-1"
            ),
            TimelineEvent(
                event_id="evt-2",
                timestamp=datetime.now(),  # Earlier timestamp
                event_type=TimelineEventType.NODE_RECOVERED,
                source_engine="test",
                entity_id="node-1"
            ),
        ]
        
        result = validator.validate_events(events)
        
        assert result["valid"] is False
        assert len(result["issues"]) > 0
    
    def test_validate_duplicate_events(self):
        """Test detecting duplicate event IDs."""
        validator = TimelineValidator()
        
        events = [
            TimelineEvent(
                event_id="evt-1",
                timestamp=datetime.now(),
                event_type=TimelineEventType.NODE_FAILED,
                source_engine="test",
                entity_id="node-1"
            ),
            TimelineEvent(
                event_id="evt-1",  # Duplicate ID
                timestamp=datetime.now() + timedelta(minutes=1),
                event_type=TimelineEventType.NODE_RECOVERED,
                source_engine="test",
                entity_id="node-1"
            ),
        ]
        
        result = validator.validate_events(events)
        
        assert result["valid"] is False
        assert any("Duplicate" in issue for issue in result["issues"])


class TestDeterministicReplay:
    """Tests for deterministic replay."""
    
    def test_deterministic_replay(self):
        """Test deterministic replay with same seed."""
        engine1 = DeterministicReplayEngine()
        engine1.set_seed(42)
        
        events = [
            TimelineEvent(
                event_id=f"evt-{i}",
                timestamp=datetime.now() + timedelta(minutes=i),
                event_type=TimelineEventType.NODE_FAILED,
                source_engine="test",
                entity_id="node-1"
            )
            for i in range(10)
        ]
        
        segment = TimelineSegment(
            segment_id="seg-1",
            start_time=events[0].timestamp,
            end_time=events[-1].timestamp,
            events=events
        )
        
        session1 = engine1.create_session(segment)
        
        # Events should be sorted
        assert session1.timeline_segment.events[0].event_id == "evt-0"
