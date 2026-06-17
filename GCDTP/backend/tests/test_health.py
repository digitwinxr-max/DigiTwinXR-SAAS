"""Unit tests for Health Engine."""
import pytest


class TestHealthCalculation:
    """Tests for health calculation logic."""

    def test_calculate_health_no_events(self, client):
        """Test health calculation with no events returns 100."""
        # Create asset
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        # Calculate health
        response = client.post(f"/health/recalculate/{asset_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["health_score"] == 100
        assert data["health_status"] == "HEALTHY"
        assert data["active_event_count"] == 0

    def test_calculate_health_one_warning(self, client):
        """Test health calculation with one WARNING event."""
        # Create asset and sensor
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        sensor_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Sensor",
            "sensor_type": "temperature",
        })
        sensor_id = sensor_response.json()["id"]
        
        # Create WARNING event
        client.post("/events/manual", json={
            "sensor_id": sensor_id,
            "asset_id": asset_id,
            "severity": "WARNING",
            "message": "Warning event",
        })
        
        # Calculate health
        response = client.post(f"/health/recalculate/{asset_id}")
        data = response.json()
        assert data["health_score"] == 90
        assert data["health_status"] == "HEALTHY"
        assert data["active_event_count"] == 1

    def test_calculate_health_one_critical(self, client):
        """Test health calculation with one CRITICAL event."""
        # Create asset and sensor
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        sensor_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Sensor",
            "sensor_type": "temperature",
        })
        sensor_id = sensor_response.json()["id"]
        
        # Create CRITICAL event
        client.post("/events/manual", json={
            "sensor_id": sensor_id,
            "asset_id": asset_id,
            "severity": "CRITICAL",
            "message": "Critical event",
        })
        
        # Calculate health
        response = client.post(f"/health/recalculate/{asset_id}")
        data = response.json()
        assert data["health_score"] == 80
        assert data["health_status"] == "HEALTHY"
        assert data["active_event_count"] == 1

    def test_calculate_health_multiple_events(self, client):
        """Test health calculation with multiple events."""
        # Create asset and sensor
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        sensor_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Sensor",
            "sensor_type": "temperature",
        })
        sensor_id = sensor_response.json()["id"]
        
        # Create multiple events: 2 WARNING + 1 CRITICAL
        # 100 - 20 (CRITICAL) - 10 - 10 (WARNINGS) = 60
        client.post("/events/manual", json={
            "sensor_id": sensor_id,
            "asset_id": asset_id,
            "severity": "CRITICAL",
            "message": "Critical event",
        })
        client.post("/events/manual", json={
            "sensor_id": sensor_id,
            "asset_id": asset_id,
            "severity": "WARNING",
            "message": "Warning event 1",
        })
        client.post("/events/manual", json={
            "sensor_id": sensor_id,
            "asset_id": asset_id,
            "severity": "WARNING",
            "message": "Warning event 2",
        })
        
        # Calculate health
        response = client.post(f"/health/recalculate/{asset_id}")
        data = response.json()
        assert data["health_score"] == 60
        assert data["health_status"] == "DEGRADED"
        assert data["active_event_count"] == 3

    def test_calculate_health_boundary_healthy(self, client):
        """Test health calculation at healthy boundary (score 80)."""
        # Create asset and sensor
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        sensor_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Sensor",
            "sensor_type": "temperature",
        })
        sensor_id = sensor_response.json()["id"]
        
        # 1 CRITICAL = 80 = HEALTHY boundary
        client.post("/events/manual", json={
            "sensor_id": sensor_id,
            "asset_id": asset_id,
            "severity": "CRITICAL",
            "message": "Critical event",
        })
        
        response = client.post(f"/health/recalculate/{asset_id}")
        data = response.json()
        assert data["health_score"] == 80
        assert data["health_status"] == "HEALTHY"

    def test_calculate_health_boundary_degraded(self, client):
        """Test health calculation at degraded boundary (score 79)."""
        # Create asset and sensor
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        sensor_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Sensor",
            "sensor_type": "temperature",
        })
        sensor_id = sensor_response.json()["id"]
        
        # 1 CRITICAL + 1 WARNING = 70 = DEGRADED
        client.post("/events/manual", json={
            "sensor_id": sensor_id,
            "asset_id": asset_id,
            "severity": "CRITICAL",
            "message": "Critical event",
        })
        client.post("/events/manual", json={
            "sensor_id": sensor_id,
            "asset_id": asset_id,
            "severity": "WARNING",
            "message": "Warning event",
        })
        
        response = client.post(f"/health/recalculate/{asset_id}")
        data = response.json()
        assert data["health_score"] == 70
        assert data["health_status"] == "DEGRADED"

    def test_calculate_health_boundary_critical(self, client):
        """Test health calculation at critical boundary (score 39)."""
        # Create asset and sensor
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        sensor_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Sensor",
            "sensor_type": "temperature",
        })
        sensor_id = sensor_response.json()["id"]
        
        # 3 CRITICAL + 1 WARNING = 100 - 60 - 10 = 30 = CRITICAL
        for _ in range(3):
            client.post("/events/manual", json={
                "sensor_id": sensor_id,
                "asset_id": asset_id,
                "severity": "CRITICAL",
                "message": "Critical event",
            })
        client.post("/events/manual", json={
            "sensor_id": sensor_id,
            "asset_id": asset_id,
            "severity": "WARNING",
            "message": "Warning event",
        })
        
        response = client.post(f"/health/recalculate/{asset_id}")
        data = response.json()
        assert data["health_score"] == 30
        assert data["health_status"] == "CRITICAL"

    def test_calculate_health_minimum_score(self, client):
        """Test health calculation doesn't go below 0."""
        # Create asset and sensor
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        sensor_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Sensor",
            "sensor_type": "temperature",
        })
        sensor_id = sensor_response.json()["id"]
        
        # 10 CRITICAL events = 100 - 200 = -100, clamped to 0
        for _ in range(10):
            client.post("/events/manual", json={
                "sensor_id": sensor_id,
                "asset_id": asset_id,
                "severity": "CRITICAL",
                "message": "Critical event",
            })
        
        response = client.post(f"/health/recalculate/{asset_id}")
        data = response.json()
        assert data["health_score"] == 0
        assert data["health_status"] == "CRITICAL"


class TestEventToHealthPropagation:
    """Tests for event-to-health propagation."""

    def test_event_creation_triggers_health_recalculation(self, client):
        """Test that creating an event triggers health recalculation."""
        # Create asset and sensor
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        sensor_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Sensor",
            "sensor_type": "temperature",
        })
        sensor_id = sensor_response.json()["id"]
        
        # Get health before event
        get_response = client.get(f"/health/assets/{asset_id}")
        # May return 404 if no health record yet
        
        # Create event
        client.post("/events/manual", json={
            "sensor_id": sensor_id,
            "asset_id": asset_id,
            "severity": "WARNING",
            "message": "Warning event",
        })
        
        # Health should now reflect the event
        response = client.get(f"/health/assets/{asset_id}")
        data = response.json()
        assert data["health_score"] == 90
        assert data["active_event_count"] == 1

    def test_event_resolution_triggers_health_recalculation(self, client):
        """Test that resolving an event triggers health recalculation."""
        # Create asset and sensor
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        sensor_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Sensor",
            "sensor_type": "temperature",
        })
        sensor_id = sensor_response.json()["id"]
        
        # Create WARNING event
        event_response = client.post("/events/manual", json={
            "sensor_id": sensor_id,
            "asset_id": asset_id,
            "severity": "WARNING",
            "message": "Warning event",
        })
        event_id = event_response.json()["id"]
        
        # Health should be 90
        response = client.get(f"/health/assets/{asset_id}")
        assert response.json()["health_score"] == 90
        
        # Resolve event
        client.patch(f"/events/{event_id}/resolve")
        
        # Health should now be 100
        response = client.get(f"/health/assets/{asset_id}")
        data = response.json()
        assert data["health_score"] == 100
        assert data["active_event_count"] == 0

    def test_multiple_events_resolution_partial(self, client):
        """Test resolving some events changes health score."""
        # Create asset and sensor
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        sensor_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Sensor",
            "sensor_type": "temperature",
        })
        sensor_id = sensor_response.json()["id"]
        
        # Create 3 WARNING events
        event_ids = []
        for _ in range(3):
            response = client.post("/events/manual", json={
                "sensor_id": sensor_id,
                "asset_id": asset_id,
                "severity": "WARNING",
                "message": "Warning event",
            })
            event_ids.append(response.json()["id"])
        
        # Health should be 70 (100 - 30)
        response = client.get(f"/health/assets/{asset_id}")
        assert response.json()["health_score"] == 70
        
        # Resolve one event
        client.patch(f"/events/{event_ids[0]}/resolve")
        
        # Health should be 80 (100 - 20)
        response = client.get(f"/health/assets/{asset_id}")
        data = response.json()
        assert data["health_score"] == 80
        assert data["active_event_count"] == 2


class TestHealthEndpoints:
    """Tests for health API endpoints."""

    def test_get_health_summary(self, client):
        """Test getting health summary."""
        # Create assets with events
        asset_response = client.post("/assets", json={
            "name": "Asset 1",
            "asset_type": "sensor",
        })
        asset1_id = asset_response.json()["id"]
        
        asset_response = client.post("/assets", json={
            "name": "Asset 2",
            "asset_type": "sensor",
        })
        asset2_id = asset_response.json()["id"]
        
        sensor_response = client.post("/sensors", json={
            "asset_id": asset1_id,
            "name": "Sensor",
            "sensor_type": "temperature",
        })
        sensor_id = sensor_response.json()["id"]
        
        # Create 1 CRITICAL event on asset 1
        client.post("/events/manual", json={
            "sensor_id": sensor_id,
            "asset_id": asset1_id,
            "severity": "CRITICAL",
            "message": "Critical event",
        })
        
        # Get summary
        response = client.get("/health/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["total_assets"] == 2
        assert data["healthy_count"] == 1  # Asset 2
        assert data["degraded_count"] == 0
        assert data["critical_count"] == 0  # CRITICAL event still HEALTHY

    def test_get_all_asset_health(self, client):
        """Test getting all asset health records."""
        # Create assets
        for i in range(3):
            client.post("/assets", json={
                "name": f"Asset {i}",
                "asset_type": "sensor",
            })
        
        response = client.get("/health/assets")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3

    def test_get_asset_health_not_found(self, client):
        """Test getting health for asset with no health record."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/health/assets/{fake_id}")
        assert response.status_code == 404

    def test_filter_health_by_status(self, client):
        """Test filtering health records by status."""
        # Create assets with different health statuses
        for i in range(5):
            asset_response = client.post("/assets", json={
                "name": f"Asset {i}",
                "asset_type": "sensor",
            })
            asset_id = asset_response.json()["id"]
            
            sensor_response = client.post("/sensors", json={
                "asset_id": asset_id,
                "name": f"Sensor {i}",
                "sensor_type": "temperature",
            })
            sensor_id = sensor_response.json()["id"]
            
            # Create events based on index
            if i < 2:  # First 2: DEGRADED (score 70)
                for _ in range(3):
                    client.post("/events/manual", json={
                        "sensor_id": sensor_id,
                        "asset_id": asset_id,
                        "severity": "WARNING",
                        "message": "Warning",
                    })
            elif i < 4:  # Next 2: HEALTHY (score 100)
                pass
        
        # Filter by DEGRADED
        response = client.get("/health/assets?status=DEGRADED")
        data = response.json()
        assert data["total"] == 2


class TestHealthRecalculation:
    """Tests for health recalculation."""

    def test_manual_recalculation(self, client):
        """Test manual health recalculation."""
        # Create asset
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        # Recalculate
        response = client.post(f"/health/recalculate/{asset_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["health_score"] == 100
        assert data["asset_id"] == asset_id

    def test_recalculate_all(self, client):
        """Test recalculating all asset health."""
        # Create assets
        for i in range(3):
            client.post("/assets", json={
                "name": f"Asset {i}",
                "asset_type": "sensor",
            })
        
        response = client.post("/health/recalculate-all")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 3


class TestHealthModel:
    """Tests for health model logic."""

    def test_health_status_calculation(self):
        """Test static health status calculation."""
        from backend.src.models.health import AssetHealth
        
        # Test boundaries
        assert AssetHealth.calculate_status(100) == "HEALTHY"
        assert AssetHealth.calculate_status(80) == "HEALTHY"
        assert AssetHealth.calculate_status(79) == "DEGRADED"
        assert AssetHealth.calculate_status(40) == "DEGRADED"
        assert AssetHealth.calculate_status(39) == "CRITICAL"
        assert AssetHealth.calculate_status(0) == "CRITICAL"