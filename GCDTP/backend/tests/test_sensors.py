"""Unit tests for Sensor CRUD operations."""
import pytest


class TestCreateSensor:
    """Tests for POST /sensors endpoint."""

    def test_create_sensor_success(self, client):
        """Test successful sensor creation."""
        # First create an asset
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        # Create sensor
        payload = {
            "asset_id": asset_id,
            "name": "Temperature Sensor",
            "sensor_type": "temperature",
            "unit": "°C",
            "description": "Temperature monitoring",
            "status": "active",
        }
        response = client.post("/sensors", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Temperature Sensor"
        assert data["sensor_type"] == "temperature"
        assert data["unit"] == "°C"
        assert data["status"] == "active"
        assert data["asset_id"] == asset_id
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_sensor_minimal(self, client):
        """Test sensor creation with minimal required fields."""
        # Create asset
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        # Create sensor with minimal fields
        payload = {
            "asset_id": asset_id,
            "name": "Minimal Sensor",
            "sensor_type": "pressure",
        }
        response = client.post("/sensors", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Sensor"
        assert data["status"] == "active"

    def test_create_sensor_missing_asset(self, client):
        """Test sensor creation fails without asset."""
        payload = {
            "name": "Test Sensor",
            "sensor_type": "temperature",
        }
        response = client.post("/sensors", json=payload)
        assert response.status_code == 422

    def test_create_sensor_invalid_asset(self, client):
        """Test sensor creation fails with non-existent asset."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        payload = {
            "asset_id": fake_id,
            "name": "Test Sensor",
            "sensor_type": "temperature",
        }
        response = client.post("/sensors", json=payload)
        assert response.status_code == 404


class TestGetSensors:
    """Tests for GET /sensors endpoint."""

    def test_get_sensors_empty(self, client):
        """Test getting sensors when none exist."""
        response = client.get("/sensors")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_get_sensors_with_data(self, client):
        """Test getting sensors after creating some."""
        # Create asset
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        # Create sensors
        for i in range(3):
            client.post("/sensors", json={
                "asset_id": asset_id,
                "name": f"Sensor {i}",
                "sensor_type": "temperature",
            })
        
        response = client.get("/sensors")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 3


class TestGetSensor:
    """Tests for GET /sensors/{id} endpoint."""

    def test_get_sensor_success(self, client):
        """Test getting a single sensor by ID."""
        # Create asset and sensor
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        sensor_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Test Sensor",
            "sensor_type": "temperature",
        })
        sensor_id = sensor_response.json()["id"]
        
        # Get sensor
        response = client.get(f"/sensors/{sensor_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Sensor"
        assert data["id"] == sensor_id

    def test_get_sensor_not_found(self, client):
        """Test getting non-existent sensor."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/sensors/{fake_id}")
        assert response.status_code == 404


class TestUpdateSensor:
    """Tests for PUT /sensors/{id} endpoint."""

    def test_update_sensor_success(self, client):
        """Test updating a sensor."""
        # Create asset and sensor
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        sensor_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Original Name",
            "sensor_type": "temperature",
            "status": "active",
        })
        sensor_id = sensor_response.json()["id"]
        
        # Update sensor
        response = client.put(f"/sensors/{sensor_id}", json={
            "name": "Updated Name",
            "status": "maintenance",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["status"] == "maintenance"
        assert data["sensor_type"] == "temperature"

    def test_update_sensor_not_found(self, client):
        """Test updating non-existent sensor."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.put(f"/sensors/{fake_id}", json={"name": "Test"})
        assert response.status_code == 404


class TestDeleteSensor:
    """Tests for DELETE /sensors/{id} endpoint."""

    def test_delete_sensor_success(self, client):
        """Test deleting a sensor."""
        # Create asset and sensor
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        sensor_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "To Delete",
            "sensor_type": "temperature",
        })
        sensor_id = sensor_response.json()["id"]
        
        # Delete sensor
        response = client.delete(f"/sensors/{sensor_id}")
        assert response.status_code == 204
        
        # Verify deleted
        get_response = client.get(f"/sensors/{sensor_id}")
        assert get_response.status_code == 404

    def test_delete_sensor_not_found(self, client):
        """Test deleting non-existent sensor."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.delete(f"/sensors/{fake_id}")
        assert response.status_code == 404


class TestAssetSensorRelationship:
    """Tests for sensor-to-asset relationships."""

    def test_get_sensors_by_asset(self, client):
        """Test getting sensors for a specific asset."""
        # Create two assets
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
        
        # Create sensors for asset 1
        for i in range(2):
            client.post("/sensors", json={
                "asset_id": asset1_id,
                "name": f"Sensor for Asset 1-{i}",
                "sensor_type": "temperature",
            })
        
        # Create sensor for asset 2
        client.post("/sensors", json={
            "asset_id": asset2_id,
            "name": "Sensor for Asset 2",
            "sensor_type": "humidity",
        })
        
        # Get sensors for asset 1
        response = client.get(f"/assets/{asset1_id}/sensors")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2

    def test_delete_asset_cascades_to_sensors(self, client):
        """Test that deleting an asset deletes its sensors."""
        # Create asset with sensor
        asset_response = client.post("/assets", json={
            "name": "Asset with Sensor",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        sensor_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Orphaned Sensor",
            "sensor_type": "temperature",
        })
        sensor_id = sensor_response.json()["id"]
        
        # Delete asset
        client.delete(f"/assets/{asset_id}")
        
        # Verify sensor is deleted
        response = client.get(f"/sensors/{sensor_id}")
        assert response.status_code == 404

    def test_sensor_belongs_to_correct_asset(self, client):
        """Test sensor has correct asset_id."""
        # Create two assets
        asset1_response = client.post("/assets", json={
            "name": "Asset 1",
            "asset_type": "sensor",
        })
        asset1_id = asset1_response.json()["id"]
        
        # Create sensor for asset 1
        sensor_response = client.post("/sensors", json={
            "asset_id": asset1_id,
            "name": "Sensor",
            "sensor_type": "temperature",
        })
        sensor_id = sensor_response.json()["id"]
        
        # Verify sensor belongs to asset 1
        response = client.get(f"/sensors/{sensor_id}")
        data = response.json()
        assert data["asset_id"] == asset1_id


class TestSensorTypes:
    """Tests for different sensor types."""

    def test_all_sensor_types(self, client):
        """Test creating sensors with all supported types."""
        sensor_types = [
            "temperature",
            "pressure",
            "humidity",
            "vibration",
            "flow",
            "voltage",
        ]
        
        # Create asset
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        for sensor_type in sensor_types:
            response = client.post("/sensors", json={
                "asset_id": asset_id,
                "name": f"{sensor_type.capitalize()} Sensor",
                "sensor_type": sensor_type,
            })
            assert response.status_code == 201
            data = response.json()
            assert data["sensor_type"] == sensor_type


class TestSensorStatuses:
    """Tests for different sensor statuses."""

    def test_all_statuses(self, client):
        """Test creating sensors with all supported statuses."""
        statuses = ["active", "inactive", "maintenance"]
        
        # Create asset
        asset_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        for status in statuses:
            response = client.post("/sensors", json={
                "asset_id": asset_id,
                "name": f"{status.capitalize()} Sensor",
                "sensor_type": "temperature",
                "status": status,
            })
            assert response.status_code == 201
            data = response.json()
            assert data["status"] == status
