"""Performance tests for TimescaleDB hypertable.

These tests verify that the TimescaleDB hypertable performs well
with large datasets and time-series queries.
"""
import pytest
import time
from datetime import datetime, timedelta


class TestTimescalePerformance:
    """Performance tests for TimescaleDB hypertable."""

    def test_insert_1000_measurements(self, client):
        """Test inserting 1000 measurements and verify performance."""
        # Create asset and sensor
        asset_response = client.post("/assets", json={
            "name": "Performance Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        sensor_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Performance Test Sensor",
            "sensor_type": "temperature",
            "unit": "°C",
        })
        sensor_id = sensor_response.json()["id"]
        
        # Measure time to insert 1000 measurements
        start_time = time.time()
        
        for i in range(1000):
            client.post("/measurements", json={
                "sensor_id": sensor_id,
                "value": 20.0 + (i % 50),  # Vary values
                "quality": "good",
            })
        
        insert_time = time.time() - start_time
        
        # Should complete in reasonable time (adjust based on hardware)
        # Typically 1000 inserts should take less than 30 seconds
        assert insert_time < 60, f"Insert took {insert_time:.2f}s, expected < 60s"
        
        # Verify all measurements were created
        response = client.get(f"/measurements?sensor_id={sensor_id}")
        data = response.json()
        assert data["total"] == 1000

    def test_query_last_100_per_sensor(self, client):
        """Test querying last 100 measurements per sensor with multiple sensors."""
        # Create asset
        asset_response = client.post("/assets", json={
            "name": "Multi-Sensor Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        # Create 5 sensors
        sensor_ids = []
        for i in range(5):
            sensor_response = client.post("/sensors", json={
                "asset_id": asset_id,
                "name": f"Sensor {i}",
                "sensor_type": "temperature",
            })
            sensor_ids.append(sensor_response.json()["id"])
        
        # Insert 200 measurements per sensor (1000 total)
        for sensor_id in sensor_ids:
            for j in range(200):
                client.post("/measurements", json={
                    "sensor_id": sensor_id,
                    "value": 20.0 + j,
                    "quality": "good",
                })
        
        # Measure query time for last 100 per sensor
        start_time = time.time()
        
        for sensor_id in sensor_ids:
            response = client.get(f"/sensors/{sensor_id}/measurements?limit=100")
            data = response.json()
            # Should return exactly 100
            assert len(data["items"]) == 100
            # Total should be 200
            assert data["total"] == 200
        
        query_time = time.time() - start_time
        
        # 5 queries should complete quickly
        assert query_time < 10, f"Query took {query_time:.2f}s, expected < 10s"

    def test_time_range_filtering_performance(self, client):
        """Test time range filtering with large dataset."""
        # Create asset and sensor
        asset_response = client.post("/assets", json={
            "name": "Time Range Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        sensor_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Time Range Sensor",
            "sensor_type": "temperature",
        })
        sensor_id = sensor_response.json()["id"]
        
        # Create measurements spread over time
        now = datetime.utcnow()
        for i in range(500):
            # Each measurement is 1 hour apart
            timestamp = (now - timedelta(hours=i)).isoformat()
            client.post("/measurements", json={
                "sensor_id": sensor_id,
                "value": 20.0 + i,
                "quality": "good",
            })
        
        # Query last 24 hours
        yesterday = (now - timedelta(hours=24)).isoformat()
        
        start_time = time.time()
        response = client.get(
            f"/measurements?sensor_id={sensor_id}&start_time={yesterday}&limit=100"
        )
        query_time = time.time() - start_time
        
        data = response.json()
        # Should return measurements from last 24 hours
        assert query_time < 5, f"Time range query took {query_time:.2f}s, expected < 5s"
        assert len(data["items"]) <= 24  # At most 24 hours worth

    def test_hypertable_compatibility(self, client):
        """Test that all existing API endpoints work with hypertable."""
        # Create asset and sensor
        asset_response = client.post("/assets", json={
            "name": "Compatibility Test Asset",
            "asset_type": "sensor",
        })
        asset_id = asset_response.json()["id"]
        
        sensor_response = client.post("/sensors", json={
            "asset_id": asset_id,
            "name": "Compatibility Sensor",
            "sensor_type": "pressure",
            "unit": "kPa",
        })
        sensor_id = sensor_response.json()["id"]
        
        # Test POST /measurements
        measurement_response = client.post("/measurements", json={
            "sensor_id": sensor_id,
            "value": 101.325,
            "quality": "good",
        })
        assert measurement_response.status_code == 201
        measurement_id = measurement_response.json()["id"]
        
        # Test GET /measurements
        response = client.get("/measurements")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        
        # Test GET /measurements/{id}
        response = client.get(f"/measurements/{measurement_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["value"] == 101.325
        
        # Test GET /sensors/{id}/measurements
        response = client.get(f"/sensors/{sensor_id}/measurements")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        
        # Test DELETE /measurements/{id}
        response = client.delete(f"/measurements/{measurement_id}")
        assert response.status_code == 204
        
        # Verify deleted
        response = client.get(f"/measurements/{measurement_id}")
        assert response.status_code == 404
