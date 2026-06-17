"""Unit tests for Event Engine."""
import pytest


class TestCreateEvent:
    """Tests for POST /events endpoints."""

    def test_create_event_manual_success(self, client):
        """Test successful manual event creation."""
        # Create asset and sensor
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        sensor_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Temperature Sensor",
            "sensor_type": "temperature",
        })
        sensor_id = sensor_response.json()["id"]
        
        # Create event
        payload = {
            "sensor_id": sensor_id,
            "asset_id": asset_id,
            "event_type": "THRESHOLD_VIOLATION",
            "severity": "WARNING",
            "message": "Temperature exceeded warning threshold",
            "value": 28.5,
        }
        response = client.post("/events/manual", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["severity"] == "WARNING"
        assert data["status"] == "ACTIVE"
        assert data["value"] == 28.5

    def test_create_event_from_evaluation_critical(self, client):
        """Test event creation from threshold evaluation with CRITICAL status."""
        # Create asset and sensor
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        sensor_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Temperature Sensor",
            "sensor_type": "temperature",
        })
        sensor_id = sensor_response.json()["id"]
        
        # Create threshold rule
        rule_response = client.post("/thresholds", json={
            "sensor_id": sensor_id,
            "name": "High Temp Alert",
            "warning_min": 20.0,
            "warning_max": 30.0,
            "critical_min": 15.0,
            "critical_max": 35.0,
        })
        rule_id = rule_response.json()["id"]
        
        # Create event from evaluation
        evaluation = {
            "status": "CRITICAL",
            "rule_id": rule_id,
            "sensor_id": sensor_id,
            "message": "Temperature exceeded critical threshold",
        }
        measurement = {
            "id": "00000000-0000-0000-0000-000000000001",
            "sensor_id": sensor_id,
            "value": 40.0,
            "timestamp": "2026-06-16T10:00:00Z",
        }
        
        response = client.post("/events/from-evaluation", json={
            "evaluation": evaluation,
            "measurement": measurement,
        })
        assert response.status_code == 201
        data = response.json()
        assert data["severity"] == "CRITICAL"
        assert data["sensor_id"] == sensor_id
        assert data["asset_id"] == asset_id

    def test_create_event_from_evaluation_warning(self, client):
        """Test event creation from threshold evaluation with WARNING status."""
        # Create asset and sensor
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        sensor_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Temperature Sensor",
            "sensor_type": "temperature",
        })
        sensor_id = sensor_response.json()["id"]
        
        # Create threshold rule
        rule_response = client.post("/thresholds", json={
            "sensor_id": sensor_id,
            "name": "High Temp Alert",
            "warning_min": 20.0,
            "warning_max": 30.0,
        })
        rule_id = rule_response.json()["id"]
        
        # Create event from evaluation
        evaluation = {
            "status": "WARNING",
            "rule_id": rule_id,
            "sensor_id": sensor_id,
            "message": "Temperature exceeded warning threshold",
        }
        measurement = {
            "id": "00000000-0000-0000-0000-000000000001",
            "sensor_id": sensor_id,
            "value": 25.0,
            "timestamp": "2026-06-16T10:00:00Z",
        }
        
        response = client.post("/events/from-evaluation", json={
            "evaluation": evaluation,
            "measurement": measurement,
        })
        assert response.status_code == 201
        data = response.json()
        assert data["severity"] == "WARNING"

    def test_no_event_created_for_ok_evaluation(self, client):
        """Test that no event is created when evaluation status is OK."""
        # Create asset and sensor
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        sensor_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Temperature Sensor",
            "sensor_type": "temperature",
        })
        sensor_id = sensor_response.json()["id"]
        
        # Create event from OK evaluation
        evaluation = {
            "status": "OK",
            "rule_id": "00000000-0000-0000-0000-000000000001",
            "sensor_id": sensor_id,
            "message": "Value within acceptable range",
        }
        measurement = {
            "id": "00000000-0000-0000-0000-000000000001",
            "sensor_id": sensor_id,
            "value": 22.0,
            "timestamp": "2026-06-16T10:00:00Z",
        }
        
        response = client.post("/events/from-evaluation", json={
            "evaluation": evaluation,
            "measurement": measurement,
        })
        # Should return success but indicate no event created
        assert response.status_code == 200
        data = response.json()
        assert "No event created" in data.get("message", "")


class TestGetEvents:
    """Tests for GET /events endpoints."""

    def test_get_events_empty(self, client):
        """Test getting events when none exist."""
        response = client.get("/events")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_get_events_with_data(self, client):
        """Test getting events after creating some."""
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
        
        # Create events
        for severity in ["WARNING", "CRITICAL", "WARNING"]:
            client.post("/events/manual", json={
                "sensor_id": sensor_id,
                "asset_id": asset_id,
                "event_type": "THRESHOLD_VIOLATION",
                "severity": severity,
                "message": f"{severity} event",
            })
        
        response = client.get("/events")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 3

    def test_get_events_filter_by_status(self, client):
        """Test filtering events by status."""
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
        
        # Create active and resolved events
        for i, status in enumerate(["ACTIVE", "ACTIVE", "RESOLVED"]):
            event_data = {
                "sensor_id": sensor_id,
                "asset_id": asset_id,
                "event_type": "THRESHOLD_VIOLATION",
                "severity": "WARNING",
                "message": f"Event {i}",
            }
            response = client.post("/events/manual", json=event_data)
            if status == "RESOLVED":
                event_id = response.json()["id"]
                client.patch(f"/events/{event_id}/resolve")
        
        # Filter by ACTIVE
        response = client.get("/events?status=ACTIVE")
        data = response.json()
        assert data["total"] == 2

    def test_get_active_events(self, client):
        """Test getting only active events."""
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
        
        # Create events
        for i in range(3):
            client.post("/events/manual", json={
                "sensor_id": sensor_id,
                "asset_id": asset_id,
                "event_type": "THRESHOLD_VIOLATION",
                "severity": "WARNING",
                "message": f"Event {i}",
            })
        
        response = client.get("/events/active")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        for event in data["items"]:
            assert event["status"] == "ACTIVE"

    def test_get_events_by_sensor(self, client):
        """Test getting events for a specific sensor."""
        # Create assets and sensors
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        sensor1_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Sensor 1",
            "sensor_type": "temperature",
        })
        sensor1_id = sensor1_response.json()["id"]
        
        sensor2_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Sensor 2",
            "sensor_type": "pressure",
        })
        sensor2_id = sensor2_response.json()["id"]
        
        # Create events for each sensor
        for i in range(2):
            client.post("/events/manual", json={
                "sensor_id": sensor1_id,
                "asset_id": asset_id,
                "severity": "WARNING",
                "message": f"Sensor 1 Event {i}",
            })
        client.post("/events/manual", json={
            "sensor_id": sensor2_id,
            "asset_id": asset_id,
            "severity": "WARNING",
            "message": "Sensor 2 Event",
        })
        
        response = client.get(f"/events/sensor/{sensor1_id}")
        data = response.json()
        assert data["total"] == 2


class TestEventPersistence:
    """Tests for event persistence and data integrity."""

    def test_event_contains_sensor_and_asset(self, client):
        """Test that events correctly store sensor and asset IDs."""
        # Create asset and sensor
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        sensor_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Temperature Sensor",
            "sensor_type": "temperature",
        })
        sensor_id = sensor_response.json()["id"]
        
        # Create event
        response = client.post("/events/manual", json={
            "sensor_id": sensor_id,
            "asset_id": asset_id,
            "severity": "CRITICAL",
            "message": "Test event",
        })
        
        event_id = response.json()["id"]
        
        # Get event and verify
        get_response = client.get(f"/events/{event_id}")
        event = get_response.json()
        assert event["sensor_id"] == sensor_id
        assert event["asset_id"] == asset_id

    def test_event_from_evaluation_derives_asset(self, client):
        """Test that events created from evaluation derive asset_id from sensor."""
        # Create asset and sensor
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        sensor_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Temperature Sensor",
            "sensor_type": "temperature",
        })
        sensor_id = sensor_response.json()["id"]
        
        # Create event from evaluation
        evaluation = {
            "status": "CRITICAL",
            "rule_id": "00000000-0000-0000-0000-000000000001",
            "sensor_id": sensor_id,
            "message": "Critical event",
        }
        measurement = {
            "id": "00000000-0000-0000-0000-000000000001",
            "sensor_id": sensor_id,
            "value": 40.0,
            "timestamp": "2026-06-16T10:00:00Z",
        }
        
        response = client.post("/events/from-evaluation", json={
            "evaluation": evaluation,
            "measurement": measurement,
        })
        event = response.json()
        
        # Verify asset_id is correctly derived from sensor
        assert event["sensor_id"] == sensor_id
        assert event["asset_id"] == asset_id

    def test_delete_sensor_cascades_to_events(self, client):
        """Test that deleting a sensor deletes its events."""
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
        
        # Create event
        event_response = client.post("/events/manual", json={
            "sensor_id": sensor_id,
            "asset_id": asset_id,
            "severity": "WARNING",
            "message": "Test event",
        })
        event_id = event_response.json()["id"]
        
        # Delete sensor
        client.delete(f"/sensors/{sensor_id}")
        
        # Verify event is deleted
        response = client.get(f"/events/{event_id}")
        assert response.status_code == 404


class TestEventResolution:
    """Tests for event resolution functionality."""

    def test_resolve_event_success(self, client):
        """Test resolving an event."""
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
        
        # Create event
        event_response = client.post("/events/manual", json={
            "sensor_id": sensor_id,
            "asset_id": asset_id,
            "severity": "WARNING",
            "message": "Test event",
        })
        event_id = event_response.json()["id"]
        assert event_response.json()["status"] == "ACTIVE"
        
        # Resolve event
        resolve_response = client.patch(f"/events/{event_id}/resolve")
        assert resolve_response.status_code == 200
        assert resolve_response.json()["status"] == "RESOLVED"

    def test_resolve_event_with_notes(self, client):
        """Test resolving an event with resolution notes."""
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
        
        # Create event
        event_response = client.post("/events/manual", json={
            "sensor_id": sensor_id,
            "asset_id": asset_id,
            "severity": "WARNING",
            "message": "Temperature exceeded threshold",
        })
        event_id = event_response.json()["id"]
        
        # Resolve with notes
        resolve_response = client.patch(
            f"/events/{event_id}/resolve",
            json={"resolution_notes": "Sensor was recalibrated"},
        )
        resolved_event = resolve_response.json()
        assert resolved_event["status"] == "RESOLVED"
        assert "Sensor was recalibrated" in resolved_event["message"]

    def test_resolved_event_not_in_active_list(self, client):
        """Test that resolved events are not in active events list."""
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
        
        # Create and resolve event
        event_response = client.post("/events/manual", json={
            "sensor_id": sensor_id,
            "asset_id": asset_id,
            "severity": "WARNING",
            "message": "Test event",
        })
        event_id = event_response.json()["id"]
        client.patch(f"/events/{event_id}/resolve")
        
        # Get active events
        active_response = client.get("/events/active")
        active_events = active_response.json()["items"]
        active_ids = [e["id"] for e in active_events]
        assert event_id not in active_ids


class TestEventSeverityFiltering:
    """Tests for event severity filtering."""

    def test_filter_by_severity_critical(self, client):
        """Test filtering events by CRITICAL severity."""
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
        
        # Create events with different severities
        for severity in ["WARNING", "CRITICAL", "WARNING", "CRITICAL"]:
            client.post("/events/manual", json={
                "sensor_id": sensor_id,
                "asset_id": asset_id,
                "severity": severity,
                "message": f"{severity} event",
            })
        
        response = client.get("/events?severity=CRITICAL")
        data = response.json()
        assert data["total"] == 2

    def test_filter_active_by_severity(self, client):
        """Test filtering active events by severity."""
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
        
        # Create events
        for severity in ["WARNING", "CRITICAL", "WARNING"]:
            client.post("/events/manual", json={
                "sensor_id": sensor_id,
                "asset_id": asset_id,
                "severity": severity,
                "message": f"{severity} event",
            })
        
        response = client.get("/events/active?severity=CRITICAL")
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["severity"] == "CRITICAL"