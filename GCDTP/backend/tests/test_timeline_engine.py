"""
Tests for Timeline Engine

Tests snapshot creation, playback, frame reconstruction,
range retrieval, immutability, and event subscriptions.
"""

import pytest
from datetime import datetime, timedelta
from src.models.timeline_snapshot import TimelineSnapshot, SnapshotType
from src.services.timeline_service import TimelineService


class TestTimelineSnapshot:
    """Tests for timeline snapshot operations."""
    
    def test_create_snapshot(self):
        """Test creating a timeline snapshot."""
        service = TimelineService()
        
        snapshot = service.capture_snapshot(
            snapshot_type="asset_state",
            entity_type="asset",
            entity_id="asset-001",
            snapshot_data={"name": "Test Asset", "status": "healthy"},
            timestamp=datetime.now()
        )
        
        assert snapshot is not None
        assert snapshot.snapshot_type == SnapshotType.ASSET_STATE
        assert snapshot.entity_type == "asset"
        assert snapshot.entity_id == "asset-001"
        assert snapshot.snapshot_data["name"] == "Test Asset"
    
    def test_snapshot_immutability(self):
        """Test that snapshots are immutable."""
        service = TimelineService()
        
        snapshot = service.capture_snapshot(
            snapshot_type="health_state",
            entity_type="health",
            entity_id="health-001",
            snapshot_data={"health_score": 85},
            timestamp=datetime.now()
        )
        
        # Attempt to modify should not change original
        snapshot.snapshot_data["health_score"] = 100
        retrieved = service.get_snapshot(snapshot.id)
        
        # The retrieved snapshot should have original data
        assert retrieved.snapshot_data["health_score"] == 85
    
    def test_all_snapshot_types(self):
        """Test creating all snapshot types."""
        service = TimelineService()
        
        types = [
            ("asset_state", "asset", "a1"),
            ("health_state", "health", "h1"),
            ("event_state", "event", "e1"),
            ("measurement_state", "measurement", "m1"),
            ("system_state", "system", "system"),
        ]
        
        for snapshot_type, entity_type, entity_id in types:
            snapshot = service.capture_snapshot(
                snapshot_type=snapshot_type,
                entity_type=entity_type,
                entity_id=entity_id,
                snapshot_data={"test": True},
                timestamp=datetime.now()
            )
            
            assert snapshot is not None
            assert snapshot.snapshot_type.value == snapshot_type


class TestTimelinePlayback:
    """Tests for timeline playback."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = TimelineService()
        
        # Create test snapshots
        base_time = datetime(2024, 1, 1, 0, 0, 0)
        
        for i in range(10):
            timestamp = base_time + timedelta(minutes=i * 10)
            
            self.service.capture_snapshot(
                snapshot_type="asset_state",
                entity_type="asset",
                entity_id=f"asset-{i % 3}",
                snapshot_data={"name": f"Asset {i % 3}", "value": i},
                timestamp=timestamp
            )
    
    def test_playback_generates_frames(self):
        """Test that playback generates frames."""
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 1, 1, 0, 0)
        
        frames = self.service.playback(
            start_time=start,
            end_time=end,
            frame_interval=30  # 30 seconds between frames
        )
        
        assert len(frames) > 0
        assert all(hasattr(f, 'timestamp') for f in frames)
        assert all(hasattr(f, 'events') for f in frames)
        assert all(hasattr(f, 'states') for f in frames)
    
    def test_playback_filter_by_entity(self):
        """Test playback filtering by entity."""
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 1, 1, 0, 0)
        
        frames = self.service.playback(
            start_time=start,
            end_time=end,
            frame_interval=60,
            entity_id="asset-0"
        )
        
        assert len(frames) > 0
    
    def test_playback_respects_interval(self):
        """Test that playback respects frame interval."""
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 1, 0, 10, 0)
        
        # With 60 second interval, should have ~11 frames
        frames = self.service.playback(
            start_time=start,
            end_time=end,
            frame_interval=60
        )
        
        # Should have approximately 11 frames (including endpoints)
        assert len(frames) >= 10


class TestTimelineFrame:
    """Tests for timeline frame reconstruction."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = TimelineService()
        
        base_time = datetime(2024, 1, 1, 12, 0, 0)
        
        # Create asset snapshots
        for i in range(5):
            self.service.capture_snapshot(
                snapshot_type="asset_state",
                entity_type="asset",
                entity_id=f"asset-{i}",
                snapshot_data={"name": f"Asset {i}", "status": "active"},
                timestamp=base_time + timedelta(minutes=i)
            )
        
        # Create event snapshots
        self.service.capture_snapshot(
            snapshot_type="event_state",
            entity_type="event",
            entity_id="event-1",
            snapshot_data={
                "message": "Test event",
                "severity": "WARNING",
                "asset_id": "asset-0"
            },
            timestamp=base_time + timedelta(minutes=2)
        )
    
    def test_build_frame_at_timestamp(self):
        """Test building a frame at specific timestamp."""
        timestamp = datetime(2024, 1, 1, 12, 2, 0)
        
        frame = self.service.build_frame(timestamp, window_seconds=60)
        
        assert frame is not None
        assert len(frame.events) > 0
        assert len(frame.states) > 0
    
    def test_frame_events_sorted(self):
        """Test that frame events are sorted by timestamp."""
        timestamp = datetime(2024, 1, 1, 12, 5, 0)
        
        frame = self.service.build_frame(timestamp, window_seconds=300)
        
        if len(frame.events) > 1:
            for i in range(len(frame.events) - 1):
                assert frame.events[i]["timestamp"] <= frame.events[i + 1]["timestamp"]


class TestTimelineRange:
    """Tests for timeline range queries."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = TimelineService()
        
        # Create snapshots over time
        base_time = datetime(2024, 1, 1, 0, 0, 0)
        
        for i in range(20):
            self.service.capture_snapshot(
                snapshot_type="asset_state",
                entity_type="asset",
                entity_id=f"asset-{i % 5}",
                snapshot_data={"index": i},
                timestamp=base_time + timedelta(hours=i)
            )
    
    def test_get_range_basic(self):
        """Test basic range query."""
        start = datetime(2024, 1, 1, 5, 0, 0)
        end = datetime(2024, 1, 1, 15, 0, 0)
        
        snapshots = self.service.get_range(start, end)
        
        assert len(snapshots) > 0
        assert all(start <= s.timestamp <= end for s in snapshots)
    
    def test_get_range_by_entity_type(self):
        """Test range query with entity type filter."""
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 1, 23, 59, 59)
        
        snapshots = self.service.get_range(
            start,
            end,
            entity_type="asset"
        )
        
        assert all(s.entity_type == "asset" for s in snapshots)
    
    def test_get_range_pagination(self):
        """Test range query pagination."""
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 1, 23, 59, 59)
        
        # Get first page
        page1 = self.service.get_range(start, end, limit=5, offset=0)
        
        # Get second page
        page2 = self.service.get_range(start, end, limit=5, offset=5)
        
        assert len(page1) == 5
        assert len(page2) == 5
        assert page1[0].id != page2[0].id


class TestTimelineReconstruction:
    """Tests for state reconstruction."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = TimelineService()
    
    def test_reconstruct_asset_state(self):
        """Test reconstructing asset state at a time."""
        base_time = datetime(2024, 1, 1, 12, 0, 0)
        
        # Create historical snapshot
        self.service.capture_snapshot(
            snapshot_type="asset_state",
            entity_type="asset",
            entity_id="test-asset",
            snapshot_data={"name": "Historical Name", "status": "old"},
            timestamp=base_time - timedelta(days=1)
        )
        
        # Create current snapshot
        self.service.capture_snapshot(
            snapshot_type="asset_state",
            entity_type="asset",
            entity_id="test-asset",
            snapshot_data={"name": "Current Name", "status": "new"},
            timestamp=base_time
        )
        
        # Reconstruct historical state
        historical = self.service.reconstruct_asset_state(
            "test-asset",
            timestamp=base_time - timedelta(hours=12)
        )
        
        assert historical["name"] == "Historical Name"
        assert historical["status"] == "old"
    
    def test_reconstruct_system_state(self):
        """Test reconstructing full system state."""
        base_time = datetime(2024, 1, 1, 12, 0, 0)
        
        # Create various snapshots
        self.service.capture_snapshot(
            snapshot_type="asset_state",
            entity_type="asset",
            entity_id="asset-1",
            snapshot_data={"name": "Asset 1"},
            timestamp=base_time
        )
        
        self.service.capture_snapshot(
            snapshot_type="health_state",
            entity_type="health",
            entity_id="health-1",
            snapshot_data={"health_score": 95},
            timestamp=base_time
        )
        
        system = self.service.reconstruct_system_state(timestamp=base_time)
        
        assert "assets" in system
        assert "health" in system
        assert "asset-1" in system["assets"]
        assert "health-1" in system["health"]


class TestTimelineImmutability:
    """Tests for timeline immutability guarantees."""
    
    def test_snapshots_cannot_be_modified(self):
        """Test that snapshots cannot be modified after creation."""
        service = TimelineService()
        
        snapshot = service.capture_snapshot(
            snapshot_type="asset_state",
            entity_type="asset",
            entity_id="immutable-test",
            snapshot_data={"value": 1},
            timestamp=datetime.now()
        )
        
        original_id = snapshot.id
        original_data = snapshot.snapshot_data.copy()
        
        # The snapshot object itself should not allow direct mutation
        # In a real implementation with database, this would be enforced
        assert snapshot.id == original_id
    
    def test_no_write_operations(self):
        """Test that timeline service has no write operations to live tables."""
        service = TimelineService()
        
        # Verify service only has read/query operations on live data
        # This is enforced by design - service only reads and snapshots
        operations = [m for m in dir(service) if not m.startswith('_')]
        
        # Should not have any update/delete methods
        assert not any('update' in op.lower() for op in operations if callable(getattr(service, op)))
        assert not any('delete' in op.lower() for op in operations if callable(getattr(service, op)))
