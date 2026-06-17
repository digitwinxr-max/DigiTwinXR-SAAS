"""Unit tests for Measurement CRUD operations."""
import pytest
from datetime import datetime, timedelta


class TestCreateMeasurement:
    """Tests for POST /measurements endpoint."""

    def test_create_measurement_success(self, client):
        """Test successful measurement creation."""
        # Create asset and sensor first
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
        
        # Create measurement
        payload = {
            "sensor_id": sensor_id,
            "value": 25.5,
            "quality": "good",
        }
        response = client.post("/measurements", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["value"] == 25.5
        assert data["quality"] == "good"
        assert data["sensor_id"] == sensor_id
        assert "id" in data
        assert "timestamp" in data
        assert "created_at" in data

    def test_create_measurement_minimal(self, client):
        """Test measurement creation with minimal fields."""
        # Create asset and sensor
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        sensor_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Pressure Sensor",
            "sensor_type": "pressure",
        })
        sensor_id = sensor_response.json()["id"]
        
        # Create measurement with default quality
        payload = {
            "sensor_id": sensor_id,
            "value": 101.325,
        }
        response = client.post("/measurements", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["value"] == 101.325
        assert data["quality"] == "good"

    def test_create_measurement_missing_sensor(self, client):
        """Test measurement creation fails without sensor."""
        payload = {
            "value": 25.5,
        }
        response = client.post("/measurements", json=payload)
        assert response.status_code == 422

    def test_create_measurement_invalid_sensor(self, client):
        """Test measurement creation fails with non-existent sensor."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        payload = {
            "sensor_id": fake_id,
            "value": 25.5,
        }
        response = client.post("/measurements", json=payload)
        assert response.status_code == 404


class TestGetMeasurements:
    """Tests for GET /measurements endpoint."""

    def test_get_measurements_empty(self, client):
        """Test getting measurements when none exist."""
        response = client.get("/measurements")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_get_measurements_with_data(self, client):
        """Test getting measurements after creating some."""
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
        
        # Create measurements
        for i in range(3):
            client.post("/measurements", json={
                "sensor_id": sensor_id,
                "value": 20.0 + i,
            })
        
        response = client.get("/measurements")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 3

    def test_get_measurements_pagination(self, client):
        """Test measurement pagination."""
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
        
        # Create 5 measurements
        for i in range(5):
            client.post("/measurements", json={
                "sensor_id": sensor_id,
                "value": i,
            })
        
        # Get with limit
        response = client.get("/measurements?limit=2")
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5


class TestGetMeasurement:
    """Tests for GET /measurements/{id} endpoint."""

    def test_get_measurement_success(self, client):
        """Test getting a single measurement by ID."""
        # Create asset, sensor, and measurement
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
        
        measurement_response = client.post("/measurements", json={
            "sensor_id": sensor_id,
            "value": 25.5,
            "quality": "good",
        })
        measurement_id = measurement_response.json()["id"]
        
        # Get measurement
        response = client.get(f"/measurements/{measurement_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["value"] == 25.5
        assert data["id"] == measurement_id

    def test_get_measurement_not_found(self, client):
        """Test getting non-existent measurement."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/measurements/{fake_id}")
        assert response.status_code == 404


class TestDeleteMeasurement:
    """Tests for DELETE /measurements/{id} endpoint."""

    def test_delete_measurement_success(self, client):
        """Test deleting a measurement."""
        # Create asset, sensor, and measurement
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
        
        measurement_response = client.post("/measurements", json={
            "sensor_id": sensor_id,
            "value": 25.5,
        })
        measurement_id = measurement_response.json()["id"]
        
        # Delete measurement
        response = client.delete(f"/measurements/{measurement_id}")
        assert response.status_code == 204
        
        # Verify deleted
        get_response = client.get(f"/measurements/{measurement_id}")
        assert get_response.status_code == 404

    def test_delete_measurement_not_found(self, client):
        """Test deleting non-existent measurement."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.delete(f"/measurements/{fake_id}")
        assert response.status_code == 404


class TestTimeRangeFiltering:
    """Tests for time range filtering."""

    def test_filter_by_start_time(self, client):
        """Test filtering measurements by start time."""
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
        
        # Create measurement
        client.post("/measurements", json={
            "sensor_id": sensor_id,
            "value": 25.0,
        })
        
        # Filter with future start time (should return nothing)
        future_time = (datetime.utcnow() + timedelta(days=1)).isoformat()
        response = client.get(f"/measurements?start_time={future_time}")
        data = response.json()
        assert data["total"] == 0

    def test_filter_by_sensor_id(self, client):
        """Test filtering measurements by sensor ID."""
        # Create two assets and sensors
        asset1_response = client.post("/assets", json={
            "name": "Asset 1",
            "asset_type": "sensor",
        })
        asset1_id = asset1_response.json()["id"]
        
        asset2_response = client.post("/assets", json={
            "name": "Asset 2",
            "asset_type": "sensor",
        })
        asset2_id = asset2_response.json()["id"]
        
        sensor1_response = client.post("/sensors", json={
            "asset_id": asset1_id,
            "name": "Sensor 1",
            "sensor_type": "temperature",
        })
        sensor1_id = sensor1_response.json()["id"]
        
        sensor2_response = client.post("/sensors", json={
            "asset_id": asset2_id,
            "name": "Sensor 2",
            "sensor_type": "pressure",
        })
        sensor2_id = sensor2_response.json()["id"]
        
        # Create measurements for each sensor
        client.post("/measurements", json={
            "sensor_id": sensor1_id,
            "value": 25.0,
        })
        client.post("/measurements", json={
            "sensor_id": sensor1_id,
            "value": 26.0,
        })
        client.post("/measurements", json={
            "sensor_id": sensor2_id,
            "value": 101.0,
        })
        
        # Filter by sensor 1
        response = client.get(f"/measurements?sensor_id={sensor1_id}")
        data = response.json()
        assert data["total"] == 2


class TestSensorMeasurementRelationship:
    """Tests for sensor-measurement relationships."""

    def test_get_measurements_by_sensor(self, client):
        """Test getting measurements for a specific sensor."""
        # Create asset and two sensors
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        sensor1_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Temperature Sensor",
            "sensor_type": "temperature",
        })
        sensor1_id = sensor1_response.json()["id"]
        
        sensor2_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Pressure Sensor",
            "sensor_type": "pressure",
        })
        sensor2_id = sensor2_response.json()["id"]
        
        # Create measurements
        for i in range(3):
            client.post("/measurements", json={
                "sensor_id": sensor1_id,
                "value": 20.0 + i,
            })
        
        client.post("/measurements", json={
            "sensor_id": sensor2_id,
            "value": 100.0,
        })
        
        # Get measurements for sensor 1
        response = client.get(f"/sensors/{sensor1_id}/measurements")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        
        # Get measurements for sensor 2
        response = client.get(f"/sensors/{sensor2_id}/measurements")
        data = response.json()
        assert data["total"] == 1

    def test_delete_sensor_cascades_to_measurements(self, client):
        """Test that deleting a sensor deletes its measurements."""
        # Create asset, sensor, and measurement
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
        
        measurement_response = client.post("/measurements", json={
            "sensor_id": sensor_id,
            "value": 25.5,
        })
        measurement_id = measurement_response.json()["id"]
        
        # Delete sensor
        client.delete(f"/sensors/{sensor_id}")
        
        # Verify measurement is deleted
        response = client.get(f"/measurements/{measurement_id}")
        assert response.status_code == 404


class TestMeasurementQuality:
    """Tests for measurement quality values."""

    def test_all_quality_values(self, client):
        """Test creating measurements with all quality values."""
        qualities = ["good", "uncertain", "bad"]
        
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
        
        for quality in qualities:
            response = client.post("/measurements", json={
                "sensor_id": sensor_id,
                "value": 25.0,
                "quality": quality,
            })
            assert response.status_code == 201
            data = response.json()
            assert data["quality"] == quality
