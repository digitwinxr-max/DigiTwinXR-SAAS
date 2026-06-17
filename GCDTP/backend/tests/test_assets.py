"""Unit tests for Asset CRUD operations."""
import pytest


class TestCreateAsset:
    """Tests for POST /assets endpoint."""

    def test_create_asset_success(self, client):
        """Test successful asset creation."""
        payload = {
            "name": "Test Asset",
            "asset_type": "sensor",
            "description": "Test description",
            "longitude": 10.5,
            "latitude": 20.5,
            "status": "active",
        }
        response = client.post("/assets", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Asset"
        assert data["asset_type"] == "sensor"
        assert data["status"] == "active"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_asset_minimal(self, client):
        """Test asset creation with minimal required fields."""
        payload = {
            "name": "Minimal Asset",
            "asset_type": "device",
        }
        response = client.post("/assets", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Asset"
        assert data["status"] == "active"

    def test_create_asset_missing_name(self, client):
        """Test asset creation fails without name."""
        payload = {
            "asset_type": "sensor",
        }
        response = client.post("/assets", json=payload)
        assert response.status_code == 422

    def test_create_asset_missing_type(self, client):
        """Test asset creation fails without asset_type."""
        payload = {
            "name": "Test Asset",
        }
        response = client.post("/assets", json=payload)
        assert response.status_code == 422


class TestGetAssets:
    """Tests for GET /assets endpoint."""

    def test_get_assets_empty(self, client):
        """Test getting assets when none exist."""
        response = client.get("/assets")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_get_assets_with_data(self, client):
        """Test getting assets after creating some."""
        # Create assets
        for i in range(3):
            client.post("/assets", json={
                "name": f"Asset {i}",
                "asset_type": "sensor",
            })
        
        response = client.get("/assets")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 3

    def test_get_assets_pagination(self, client):
        """Test assets pagination."""
        # Create 5 assets
        for i in range(5):
            client.post("/assets", json={
                "name": f"Asset {i}",
                "asset_type": "sensor",
            })
        
        response = client.get("/assets?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5


class TestGetAsset:
    """Tests for GET /assets/{id} endpoint."""

    def test_get_asset_success(self, client):
        """Test getting a single asset by ID."""
        # Create asset
        create_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
        })
        asset_id = create_response.json()["id"]
        
        # Get asset
        response = client.get(f"/assets/{asset_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Asset"
        assert data["id"] == asset_id

    def test_get_asset_not_found(self, client):
        """Test getting non-existent asset."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/assets/{fake_id}")
        assert response.status_code == 404


class TestUpdateAsset:
    """Tests for PUT /assets/{id} endpoint."""

    def test_update_asset_success(self, client):
        """Test updating an asset."""
        # Create asset
        create_response = client.post("/assets", json={
            "name": "Original Name",
            "asset_type": "sensor",
            "status": "active",
        })
        asset_id = create_response.json()["id"]
        
        # Update asset
        response = client.put(f"/assets/{asset_id}", json={
            "name": "Updated Name",
            "status": "inactive",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["status"] == "inactive"
        assert data["asset_type"] == "sensor"

    def test_update_asset_partial(self, client):
        """Test partial update of an asset."""
        # Create asset
        create_response = client.post("/assets", json={
            "name": "Test Asset",
            "asset_type": "sensor",
            "longitude": 10.0,
        })
        asset_id = create_response.json()["id"]
        
        # Update only name
        response = client.put(f"/assets/{asset_id}", json={
            "name": "New Name",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["longitude"] == 10.0

    def test_update_asset_not_found(self, client):
        """Test updating non-existent asset."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.put(f"/assets/{fake_id}", json={"name": "Test"})
        assert response.status_code == 404


class TestDeleteAsset:
    """Tests for DELETE /assets/{id} endpoint."""

    def test_delete_asset_success(self, client):
        """Test deleting an asset."""
        # Create asset
        create_response = client.post("/assets", json={
            "name": "To Delete",
            "asset_type": "sensor",
        })
        asset_id = create_response.json()["id"]
        
        # Delete asset
        response = client.delete(f"/assets/{asset_id}")
        assert response.status_code == 204
        
        # Verify deleted
        get_response = client.get(f"/assets/{asset_id}")
        assert get_response.status_code == 404

    def test_delete_asset_not_found(self, client):
        """Test deleting non-existent asset."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.delete(f"/assets/{fake_id}")
        assert response.status_code == 404

    def test_delete_allows_recreation(self, client):
        """Test that deleting allows creating asset with same data."""
        # Create asset
        create_response = client.post("/assets", json={
            "name": "Recreate Test",
            "asset_type": "sensor",
        })
        asset_id = create_response.json()["id"]
        
        # Delete it
        client.delete(f"/assets/{asset_id}")
        
        # Create new asset with same data
        response = client.post("/assets", json={
            "name": "Recreate Test",
            "asset_type": "sensor",
        })
        assert response.status_code == 201


class TestGeometryCreation:
    """Tests for geometry creation in asset service."""

    def test_create_point(self):
        """Test create_point helper function."""
        from src.services.asset_service import AssetService
        
        point = AssetService.create_point(longitude=-122.4194, latitude=37.7749)
        # Either returns WKTElement or dict depending on PostGIS availability
        if isinstance(point, dict):
            assert point["type"] == "Point"
            assert point["coordinates"] == [-122.4194, 37.7749]
        else:
            # WKTElement
            assert "POINT" in str(point)
            assert "-122.4194" in str(point)
            assert "37.7749" in str(point)

    def test_create_asset_with_coordinates(self, client):
        """Test asset creation with coordinates populates geometry."""
        payload = {
            "name": "Spatial Asset",
            "asset_type": "sensor",
            "longitude": -122.4194,
            "latitude": 37.7749,
        }
        response = client.post("/assets", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["longitude"] == -122.4194
        assert data["latitude"] == 37.7749

    def test_create_asset_without_coordinates(self, client):
        """Test asset creation without coordinates."""
        payload = {
            "name": "Non-spatial Asset",
            "asset_type": "sensor",
        }
        response = client.post("/assets", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["longitude"] is None
        assert data["latitude"] is None


class TestCoordinateUpdates:
    """Tests for coordinate update functionality."""

    def test_update_coordinates(self, client):
        """Test updating coordinates on existing asset."""
        # Create asset without coordinates
        create_response = client.post("/assets", json={
            "name": "Update Coordinates Test",
            "asset_type": "sensor",
        })
        asset_id = create_response.json()["id"]
        
        # Update with coordinates
        response = client.put(f"/assets/{asset_id}", json={
            "longitude": -74.0060,
            "latitude": 40.7128,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["longitude"] == -74.0060
        assert data["latitude"] == 40.7128

    def test_update_geometry_on_coordinate_change(self, client):
        """Test that geometry updates when coordinates change."""
        # Create asset with coordinates
        create_response = client.post("/assets", json={
            "name": "Geometry Update Test",
            "asset_type": "sensor",
            "longitude": 0.0,
            "latitude": 0.0,
        })
        asset_id = create_response.json()["id"]
        
        # Update coordinates
        response = client.put(f"/assets/{asset_id}", json={
            "longitude": 90.0,
            "latitude": 45.0,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["longitude"] == 90.0
        assert data["latitude"] == 45.0

    def test_clear_coordinates(self, client):
        """Test clearing coordinates sets them to null."""
        # Create asset with coordinates
        create_response = client.post("/assets", json={
            "name": "Clear Coordinates Test",
            "asset_type": "sensor",
            "longitude": 10.0,
            "latitude": 20.0,
        })
        asset_id = create_response.json()["id"]
        
        # Update to clear coordinates
        response = client.put(f"/assets/{asset_id}", json={
            "longitude": None,
            "latitude": None,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["longitude"] is None
        assert data["latitude"] is None


class TestGeoJSONEndpoint:
    """Tests for GET /assets/geojson endpoint."""

    def test_geojson_empty(self, client):
        """Test GeoJSON endpoint with no assets."""
        response = client.get("/assets/geojson")
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "FeatureCollection"
        assert data["features"] == []

    def test_geojson_single_asset(self, client):
        """Test GeoJSON endpoint with single asset."""
        # Create asset with coordinates
        client.post("/assets", json={
            "name": "GeoJSON Test Asset",
            "asset_type": "sensor",
            "longitude": -122.4194,
            "latitude": 37.7749,
            "status": "active",
        })
        
        response = client.get("/assets/geojson")
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 1
        
        feature = data["features"][0]
        assert feature["type"] == "Feature"
        assert "id" in feature
        assert feature["geometry"]["type"] == "Point"
        assert feature["geometry"]["coordinates"] == [-122.4194, 37.7749]
        assert feature["properties"]["name"] == "GeoJSON Test Asset"
        assert feature["properties"]["asset_type"] == "sensor"
        assert feature["properties"]["status"] == "active"

    def test_geojson_multiple_assets(self, client):
        """Test GeoJSON endpoint with multiple assets."""
        # Create assets with coordinates
        for i in range(3):
            client.post("/assets", json={
                "name": f"Asset {i}",
                "asset_type": "sensor",
                "longitude": float(i * 10),
                "latitude": float(i * 5),
            })
        
        response = client.get("/assets/geojson")
        assert response.status_code == 200
        data = response.json()
        assert len(data["features"]) == 3

    def test_geojson_asset_without_coordinates(self, client):
        """Test GeoJSON endpoint with asset that has no coordinates."""
        # Create asset without coordinates
        client.post("/assets", json={
            "name": "No Coordinates Asset",
            "asset_type": "sensor",
        })
        
        response = client.get("/assets/geojson")
        assert response.status_code == 200
        data = response.json()
        assert len(data["features"]) == 1
        feature = data["features"][0]
        assert feature["geometry"] is None
        assert feature["properties"]["name"] == "No Coordinates Asset"

    def test_geojson_feature_properties(self, client):
        """Test GeoJSON feature contains correct properties."""
        # Create asset
        client.post("/assets", json={
            "name": "Properties Test",
            "asset_type": "device",
            "longitude": 10.0,
            "latitude": 20.0,
            "status": "maintenance",
        })
        
        response = client.get("/assets/geojson")
        data = response.json()
        feature = data["features"][0]
        
        # Verify properties
        props = feature["properties"]
        assert "name" in props
        assert "asset_type" in props
        assert "status" in props
        assert "description" not in props  # description not in geojson
        assert "id" not in props  # id is at feature level
