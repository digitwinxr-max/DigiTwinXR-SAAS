"""Unit tests for Threshold Engine."""
import pytest
from uuid import UUID


class TestCreateThresholdRule:
    """Tests for POST /thresholds endpoint."""

    def test_create_threshold_rule_success(self, client):
        """Test successful threshold rule creation."""
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
            "unit": "°C",
        })
        sensor_id = sensor_response.json()["id"]
        
        # Create threshold rule
        payload = {
            "name": "High Temperature Alert",
            "sensor_id": sensor_id,
            "warning_min": 25.0,
            "warning_max": 30.0,
            "critical_min": 20.0,
            "critical_max": 35.0,
        }
        response = client.post("/thresholds", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "High Temperature Alert"
        assert data["sensor_id"] == sensor_id
        assert data["warning_min"] == 25.0
        assert data["warning_max"] == 30.0
        assert data["critical_min"] == 20.0
        assert data["critical_max"] == 35.0
        assert data["is_active"] == True

    def test_create_global_threshold_rule(self, client):
        """Test creating a global threshold rule (no sensor_id)."""
        payload = {
            "name": "Global Temperature Range",
            "warning_min": 15.0,
            "warning_max": 35.0,
            "critical_min": 10.0,
            "critical_max": 40.0,
        }
        response = client.post("/thresholds", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["sensor_id"] is None
        assert data["name"] == "Global Temperature Range"

    def test_create_threshold_rule_invalid_sensor(self, client):
        """Test threshold rule creation fails with non-existent sensor."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        payload = {
            "name": "Test Rule",
            "sensor_id": fake_id,
        }
        response = client.post("/thresholds", json=payload)
        assert response.status_code == 404

    def test_create_threshold_rule_minimal(self, client):
        """Test creating threshold rule with minimal fields."""
        payload = {
            "name": "Minimal Rule",
        }
        response = client.post("/thresholds", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Rule"
        assert data["is_active"] == True


class TestGetThresholdRules:
    """Tests for GET /thresholds endpoint."""

    def test_get_threshold_rules_empty(self, client):
        """Test getting threshold rules when none exist."""
        response = client.get("/thresholds")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_get_threshold_rules_with_data(self, client):
        """Test getting threshold rules after creating some."""
        # Create threshold rules
        for i in range(3):
            client.post("/thresholds", json={
                "name": f"Rule {i}",
                "warning_min": i * 10,
                "warning_max": i * 10 + 5,
            })
        
        response = client.get("/thresholds")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 3

    def test_get_threshold_rules_by_sensor(self, client):
        """Test filtering threshold rules by sensor."""
        # Create asset and two sensors
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
        
        # Create rules for each sensor
        client.post("/thresholds", json={
            "name": "Rule for Sensor 1",
            "sensor_id": sensor1_id,
        })
        client.post("/thresholds", json={
            "name": "Another Rule for Sensor 1",
            "sensor_id": sensor1_id,
        })
        client.post("/thresholds", json={
            "name": "Rule for Sensor 2",
            "sensor_id": sensor2_id,
        })
        
        # Filter by sensor 1
        response = client.get(f"/thresholds?sensor_id={sensor1_id}")
        data = response.json()
        assert data["total"] == 2


class TestGetThresholdRule:
    """Tests for GET /thresholds/{id} endpoint."""

    def test_get_threshold_rule_success(self, client):
        """Test getting a single threshold rule."""
        # Create rule
        create_response = client.post("/thresholds", json={
            "name": "Test Rule",
            "warning_min": 10.0,
            "warning_max": 20.0,
        })
        rule_id = create_response.json()["id"]
        
        # Get rule
        response = client.get(f"/thresholds/{rule_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Rule"
        assert data["warning_min"] == 10.0

    def test_get_threshold_rule_not_found(self, client):
        """Test getting non-existent threshold rule."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/thresholds/{fake_id}")
        assert response.status_code == 404


class TestUpdateThresholdRule:
    """Tests for PUT /thresholds/{id} endpoint."""

    def test_update_threshold_rule_success(self, client):
        """Test updating a threshold rule."""
        # Create rule
        create_response = client.post("/thresholds", json={
            "name": "Original Name",
            "warning_min": 10.0,
        })
        rule_id = create_response.json()["id"]
        
        # Update rule
        response = client.put(f"/thresholds/{rule_id}", json={
            "name": "Updated Name",
            "warning_max": 25.0,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["warning_max"] == 25.0
        assert data["warning_min"] == 10.0  # Unchanged

    def test_update_threshold_rule_not_found(self, client):
        """Test updating non-existent threshold rule."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.put(f"/thresholds/{fake_id}", json={
            "name": "New Name",
        })
        assert response.status_code == 404


class TestDeleteThresholdRule:
    """Tests for DELETE /thresholds/{id} endpoint."""

    def test_delete_threshold_rule_success(self, client):
        """Test deleting a threshold rule."""
        # Create rule
        create_response = client.post("/thresholds", json={
            "name": "To Delete",
        })
        rule_id = create_response.json()["id"]
        
        # Delete rule
        response = client.delete(f"/thresholds/{rule_id}")
        assert response.status_code == 204
        
        # Verify deleted
        get_response = client.get(f"/thresholds/{rule_id}")
        assert get_response.status_code == 404

    def test_delete_threshold_rule_not_found(self, client):
        """Test deleting non-existent threshold rule."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.delete(f"/thresholds/{fake_id}")
        assert response.status_code == 404


class TestThresholdEvaluation:
    """Tests for threshold evaluation logic."""

    def test_evaluate_measurement_critical_low(self, client):
        """Test evaluation returns CRITICAL for value below critical_min."""
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
        
        # Create rule with thresholds
        client.post("/thresholds", json={
            "sensor_id": sensor_id,
            "name": "Temperature Rule",
            "warning_min": 15.0,
            "warning_max": 30.0,
            "critical_min": 10.0,
            "critical_max": 35.0,
        })
        
        # Evaluate measurement below critical_min
        response = client.post("/thresholds/evaluate", json={
            "sensor_id": sensor_id,
            "value": 5.0,
            "measurement_id": "00000000-0000-0000-0000-000000000001",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "CRITICAL"

    def test_evaluate_measurement_critical_high(self, client):
        """Test evaluation returns CRITICAL for value above critical_max."""
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
        
        # Create rule with thresholds
        client.post("/thresholds", json={
            "sensor_id": sensor_id,
            "name": "Temperature Rule",
            "warning_min": 15.0,
            "warning_max": 30.0,
            "critical_min": 10.0,
            "critical_max": 35.0,
        })
        
        # Evaluate measurement above critical_max
        response = client.post("/thresholds/evaluate", json={
            "sensor_id": sensor_id,
            "value": 40.0,
            "measurement_id": "00000000-0000-0000-0000-000000000001",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "CRITICAL"

    def test_evaluate_measurement_warning_low(self, client):
        """Test evaluation returns WARNING for value below warning_min but above critical_min."""
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
        
        # Create rule with thresholds
        client.post("/thresholds", json={
            "sensor_id": sensor_id,
            "name": "Temperature Rule",
            "warning_min": 15.0,
            "warning_max": 30.0,
            "critical_min": 10.0,
            "critical_max": 35.0,
        })
        
        # Evaluate measurement below warning_min but above critical_min
        response = client.post("/thresholds/evaluate", json={
            "sensor_id": sensor_id,
            "value": 12.0,
            "measurement_id": "00000000-0000-0000-0000-000000000001",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "WARNING"

    def test_evaluate_measurement_ok(self, client):
        """Test evaluation returns OK for value within thresholds."""
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
        
        # Create rule with thresholds
        client.post("/thresholds", json={
            "sensor_id": sensor_id,
            "name": "Temperature Rule",
            "warning_min": 15.0,
            "warning_max": 30.0,
            "critical_min": 10.0,
            "critical_max": 35.0,
        })
        
        # Evaluate measurement within thresholds
        response = client.post("/thresholds/evaluate", json={
            "sensor_id": sensor_id,
            "value": 22.0,
            "measurement_id": "00000000-0000-0000-0000-000000000001",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "OK"

    def test_evaluate_no_rules_returns_ok(self, client):
        """Test evaluation returns OK when no rules exist for sensor."""
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
        
        # Evaluate without any rules
        response = client.post("/thresholds/evaluate", json={
            "sensor_id": sensor_id,
            "value": 100.0,
            "measurement_id": "00000000-0000-0000-0000-000000000001",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "OK"
        assert "No active rules" in data["message"]


class TestThresholdBoundaries:
    """Tests for threshold boundary conditions."""

    def test_boundary_exact_warning_min(self, client):
        """Test value exactly at warning_min returns OK."""
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
        
        client.post("/thresholds", json={
            "sensor_id": sensor_id,
            "name": "Rule",
            "warning_min": 15.0,
            "warning_max": 30.0,
        })
        
        response = client.post("/thresholds/evaluate", json={
            "sensor_id": sensor_id,
            "value": 15.0,
            "measurement_id": "00000000-0000-0000-0000-000000000001",
        })
        assert response.json()["status"] == "OK"

    def test_boundary_one_below_warning_min(self, client):
        """Test value one below warning_min returns WARNING."""
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
        
        client.post("/thresholds", json={
            "sensor_id": sensor_id,
            "name": "Rule",
            "warning_min": 15.0,
        })
        
        response = client.post("/thresholds/evaluate", json={
            "sensor_id": sensor_id,
            "value": 14.999,
            "measurement_id": "00000000-0000-0000-0000-000000000001",
        })
        assert response.json()["status"] == "WARNING"

    def test_inactive_rule_ignored(self, client):
        """Test inactive rules are not evaluated."""
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
        
        client.post("/thresholds", json={
            "sensor_id": sensor_id,
            "name": "Rule",
            "is_active": False,
            "warning_min": 15.0,
        })
        
        response = client.post("/thresholds/evaluate", json={
            "sensor_id": sensor_id,
            "value": 5.0,
            "measurement_id": "00000000-0000-0000-0000-000000000001",
        })
        assert response.json()["status"] == "OK"


class TestSensorThresholdRelationship:
    """Tests for sensor-threshold relationships."""

    def test_get_thresholds_by_sensor(self, client):
        """Test getting thresholds for a specific sensor."""
        # Create asset and two sensors
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
        
        # Create rules
        client.post("/thresholds", json={
            "sensor_id": sensor1_id,
            "name": "Rule 1",
        })
        client.post("/thresholds", json={
            "sensor_id": sensor1_id,
            "name": "Rule 2",
        })
        client.post("/thresholds", json={
            "sensor_id": sensor2_id,
            "name": "Rule 3",
        })
        
        # Get rules for sensor 1
        response = client.get(f"/thresholds/sensor/{sensor1_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    def test_delete_sensor_cascades_to_rules(self, client):
        """Test that deleting a sensor deletes its threshold rules."""
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
        
        # Create rule
        rule_response = client.post("/thresholds", json={
            "sensor_id": sensor_id,
            "name": "Rule",
        })
        rule_id = rule_response.json()["id"]
        
        # Delete sensor
        client.delete(f"/sensors/{sensor_id}")
        
        # Verify rule is deleted
        response = client.get(f"/thresholds/{rule_id}")
        assert response.status_code == 404