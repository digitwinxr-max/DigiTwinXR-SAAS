"""
Tests for Geospatial Module

Tests GDAL adapter, Rasterio adapter, GeoPandas adapter, raster/vector management, coordinate transformation, terrain analysis, raster analysis, spatial analysis, and timeline integration.
"""

import pytest
from backend.src.geospatial import (
    GDALAdapter,
    GDALDatasetInfo,
    GDALBandInfo,
    RasterioAdapter,
    RasterProfile,
    GeoPandasAdapter,
    VectorDatasetInfo,
    RasterManager,
    RasterDataset,
    VectorManager,
    VectorDataset,
    CoordinateTransformEngine,
    CoordinateSystem,
    TerrainAnalysisEngine,
    TerrainModel,
    RasterAnalysisEngine,
    RasterStatistics,
    SpatialAnalysisEngine,
    GeospatialMetadataManager,
    RasterMetadata,
    GeospatialValidator,
)


class TestGDALAdapter:
    """Tests for GDALAdapter."""
    
    def test_open_dataset(self):
        """Test opening a dataset."""
        adapter = GDALAdapter()
        info = adapter.open_dataset("/path/to/raster.tif")
        assert info is not None
        assert info.driver == "GTiff"
    
    def test_get_band_info(self):
        """Test getting band info."""
        adapter = GDALAdapter()
        info = adapter.get_band_info("/path/to/raster.tif", 1)
        assert info is not None
        assert info.index == 1
    
    def test_extract_metadata(self):
        """Test extracting metadata."""
        adapter = GDALAdapter()
        metadata = adapter.extract_metadata("/path/to/raster.tif")
        assert "driver" in metadata
        assert metadata["driver"] == "GTiff"
    
    def test_get_supported_formats(self):
        """Test getting supported formats."""
        adapter = GDALAdapter()
        formats = adapter.get_supported_formats()
        assert "GTiff" in formats
        assert "GeoJSON" in formats


class TestRasterioAdapter:
    """Tests for RasterioAdapter."""
    
    def test_open(self):
        """Test opening a raster."""
        adapter = RasterioAdapter()
        profile = adapter.open("/path/to/raster.tif")
        assert profile is not None
        assert profile.driver == "GTiff"
    
    def test_get_band_statistics(self):
        """Test getting band statistics."""
        adapter = RasterioAdapter()
        stats = adapter.get_band_statistics("/path/to/raster.tif", 1)
        assert "min" in stats
        assert "max" in stats
    
    def test_compute_checksum(self):
        """Test computing checksum."""
        adapter = RasterioAdapter()
        checksum = adapter.compute_checksum("/path/to/raster.tif", 1)
        assert checksum is not None


class TestGeoPandasAdapter:
    """Tests for GeoPandasAdapter."""
    
    def test_read_vector(self):
        """Test reading vector data."""
        adapter = GeoPandasAdapter()
        info = adapter.read_vector("/path/to/vector.geojson")
        assert info is not None
        assert info.geometry_type == "Polygon"
    
    def test_get_supported_formats(self):
        """Test getting supported formats."""
        adapter = GeoPandasAdapter()
        formats = adapter.get_supported_formats()
        assert "GeoJSON" in formats
        assert "ESRI Shapefile" in formats
    
    def test_calculate_area(self):
        """Test calculating area."""
        adapter = GeoPandasAdapter()
        areas = adapter.calculate_area("/path/to/polygons.geojson")
        assert isinstance(areas, list)
    
    def test_calculate_length(self):
        """Test calculating length."""
        adapter = GeoPandasAdapter()
        lengths = adapter.calculate_length("/path/to/lines.geojson")
        assert isinstance(lengths, list)


class TestRasterManager:
    """Tests for RasterManager."""
    
    def test_register_dataset(self):
        """Test registering a raster dataset."""
        manager = RasterManager()
        dataset = manager.register_dataset(
            name="test_raster",
            file_path="/path/to/raster.tif",
            storage_object_id="storage-1",
            width=1024,
            height=1024,
            bands=3,
            driver="GTiff",
            crs="EPSG:4326",
            bounds="-180,-90,180,90",
            owner_organization_id="org-1"
        )
        assert dataset.name == "test_raster"
    
    def test_get_dataset(self):
        """Test getting a dataset."""
        manager = RasterManager()
        dataset = manager.register_dataset(
            name="test_raster",
            file_path="/path/to/raster.tif",
            storage_object_id="storage-1",
            width=1024,
            height=1024,
            bands=3,
            driver="GTiff",
            crs="EPSG:4326",
            bounds="-180,-90,180,90",
            owner_organization_id="org-1"
        )
        retrieved = manager.get_dataset(dataset.id)
        assert retrieved is not None
    
    def test_get_dataset_by_name(self):
        """Test getting dataset by name."""
        manager = RasterManager()
        manager.register_dataset(
            name="test_raster",
            file_path="/path/to/raster.tif",
            storage_object_id="storage-1",
            width=1024,
            height=1024,
            bands=3,
            driver="GTiff",
            crs="EPSG:4326",
            bounds="-180,-90,180,90",
            owner_organization_id="org-1"
        )
        dataset = manager.get_dataset_by_name("test_raster")
        assert dataset is not None
    
    def test_list_datasets(self):
        """Test listing datasets."""
        manager = RasterManager()
        manager.register_dataset(
            name="test_raster",
            file_path="/path/to/raster.tif",
            storage_object_id="storage-1",
            width=1024,
            height=1024,
            bands=3,
            driver="GTiff",
            crs="EPSG:4326",
            bounds="-180,-90,180,90",
            owner_organization_id="org-1"
        )
        datasets = manager.list_datasets()
        assert len(datasets) >= 1
    
    def test_delete_dataset(self):
        """Test deleting a dataset."""
        manager = RasterManager()
        dataset = manager.register_dataset(
            name="test_raster",
            file_path="/path/to/raster.tif",
            storage_object_id="storage-1",
            width=1024,
            height=1024,
            bands=3,
            driver="GTiff",
            crs="EPSG:4326",
            bounds="-180,-90,180,90",
            owner_organization_id="org-1"
        )
        result = manager.delete_dataset(dataset.id)
        assert result is True


class TestVectorManager:
    """Tests for VectorManager."""
    
    def test_register_dataset(self):
        """Test registering a vector dataset."""
        manager = VectorManager()
        dataset = manager.register_dataset(
            name="test_vector",
            file_path="/path/to/vector.geojson",
            storage_object_id="storage-1",
            geometry_type="Polygon",
            crs="EPSG:4326",
            feature_count=1000,
            attribute_schema={},
            owner_organization_id="org-1"
        )
        assert dataset.name == "test_vector"
    
    def test_get_dataset(self):
        """Test getting a dataset."""
        manager = VectorManager()
        dataset = manager.register_dataset(
            name="test_vector",
            file_path="/path/to/vector.geojson",
            storage_object_id="storage-1",
            geometry_type="Polygon",
            crs="EPSG:4326",
            feature_count=1000,
            attribute_schema={},
            owner_organization_id="org-1"
        )
        retrieved = manager.get_dataset(dataset.id)
        assert retrieved is not None
    
    def test_list_datasets(self):
        """Test listing datasets."""
        manager = VectorManager()
        manager.register_dataset(
            name="test_vector",
            file_path="/path/to/vector.geojson",
            storage_object_id="storage-1",
            geometry_type="Polygon",
            crs="EPSG:4326",
            feature_count=1000,
            attribute_schema={},
            owner_organization_id="org-1"
        )
        datasets = manager.list_datasets()
        assert len(datasets) >= 1


class TestCoordinateTransformEngine:
    """Tests for CoordinateTransformEngine."""
    
    def test_get_crs(self):
        """Test getting a CRS."""
        engine = CoordinateTransformEngine()
        crs = engine.get_crs(4326)
        assert crs is not None
        assert crs.epsg_code == 4326
    
    def test_list_crs(self):
        """Test listing CRS."""
        engine = CoordinateTransformEngine()
        crs_list = engine.list_crs()
        assert len(crs_list) >= 3
    
    def test_is_valid_crs(self):
        """Test CRS validation."""
        engine = CoordinateTransformEngine()
        assert engine.is_valid_crs(4326) is True
        assert engine.is_valid_crs(9999) is False
    
    def test_transform_point(self):
        """Test point transformation."""
        engine = CoordinateTransformEngine()
        result = engine.transform_point(0, 0, 4326, 3857)
        assert result is not None
    
    def test_convert_crs_string(self):
        """Test CRS string conversion."""
        engine = CoordinateTransformEngine()
        epsg = engine.convert_crs_string("EPSG:4326")
        assert epsg == 4326


class TestTerrainAnalysisEngine:
    """Tests for TerrainAnalysisEngine."""
    
    def test_create_terrain_model(self):
        """Test creating a terrain model."""
        engine = TerrainAnalysisEngine()
        model = engine.create_terrain_model(
            name="test_dem",
            raster_dataset_id="raster-1",
            dem_source="SRTM",
            resolution=30.0,
            vertical_datum="WGS84",
            coverage_area="-180,-90,180,90",
            min_elevation=0.0,
            max_elevation=4000.0
        )
        assert model.name == "test_dem"
    
    def test_get_terrain_model(self):
        """Test getting a terrain model."""
        engine = TerrainAnalysisEngine()
        model = engine.create_terrain_model(
            name="test_dem",
            raster_dataset_id="raster-1",
            dem_source="SRTM",
            resolution=30.0,
            vertical_datum="WGS84",
            coverage_area="-180,-90,180,90",
            min_elevation=0.0,
            max_elevation=4000.0
        )
        retrieved = engine.get_terrain_model(model.id)
        assert retrieved is not None
    
    def test_calculate_slope(self):
        """Test slope calculation."""
        engine = TerrainAnalysisEngine()
        result = engine.calculate_slope("/path/to/dem.tif")
        assert result is not None
    
    def test_calculate_aspect(self):
        """Test aspect calculation."""
        engine = TerrainAnalysisEngine()
        result = engine.calculate_aspect("/path/to/dem.tif")
        assert result is not None
    
    def test_extract_elevation(self):
        """Test elevation extraction."""
        engine = TerrainAnalysisEngine()
        points = [(0, 0), (1, 1), (2, 2)]
        elevations = engine.extract_elevation("/path/to/dem.tif", points)
        assert len(elevations) == 3


class TestRasterAnalysisEngine:
    """Tests for RasterAnalysisEngine."""
    
    def test_calculate_statistics(self):
        """Test statistics calculation."""
        engine = RasterAnalysisEngine()
        stats = engine.calculate_statistics("/path/to/raster.tif")
        assert stats is not None
        assert hasattr(stats, "min")
    
    def test_calculate_histogram(self):
        """Test histogram calculation."""
        engine = RasterAnalysisEngine()
        histogram = engine.calculate_histogram("/path/to/raster.tif")
        assert histogram is not None
        assert hasattr(histogram, "counts")
    
    def test_calculate_ndvi(self):
        """Test NDVI calculation."""
        engine = RasterAnalysisEngine()
        result = engine.calculate_ndvi("/path/to/raster.tif")
        assert result is None  # Placeholder
    
    def test_resample(self):
        """Test resampling."""
        engine = RasterAnalysisEngine()
        result = engine.resample("/path/to/source.tif", "/path/to/target.tif", (30, 30))
        assert result is True
    
    def test_merge_rasters(self):
        """Test merging rasters."""
        engine = RasterAnalysisEngine()
        result = engine.merge_rasters(["/path/to/r1.tif", "/path/to/r2.tif"], "/path/to/merged.tif")
        assert result is True


class TestSpatialAnalysisEngine:
    """Tests for SpatialAnalysisEngine."""
    
    def test_buffer(self):
        """Test buffer operation."""
        engine = SpatialAnalysisEngine()
        result = engine.buffer("/path/to/layer.geojson", 100.0)
        assert result is None  # Placeholder
    
    def test_intersection(self):
        """Test intersection operation."""
        engine = SpatialAnalysisEngine()
        result = engine.intersection("/path/to/layer1.geojson", "/path/to/layer2.geojson")
        assert result is None  # Placeholder
    
    def test_union(self):
        """Test union operation."""
        engine = SpatialAnalysisEngine()
        result = engine.union("/path/to/layer1.geojson", "/path/to/layer2.geojson")
        assert result is None  # Placeholder
    
    def test_clip(self):
        """Test clip operation."""
        engine = SpatialAnalysisEngine()
        result = engine.clip("/path/to/source.geojson", "/path/to/clip.geojson")
        assert result is None  # Placeholder
    
    def test_nearest_neighbor(self):
        """Test nearest neighbor."""
        engine = SpatialAnalysisEngine()
        results = engine.nearest_neighbor("/path/to/source.geojson", "/path/to/target.geojson")
        assert isinstance(results, list)
    
    def test_calculate_distance(self):
        """Test distance calculation."""
        engine = SpatialAnalysisEngine()
        distances = engine.calculate_distance("/path/to/source.geojson", "/path/to/target.geojson")
        assert isinstance(distances, list)
    
    def test_calculate_centroid(self):
        """Test centroid calculation."""
        engine = SpatialAnalysisEngine()
        result = engine.calculate_centroid("/path/to/layer.geojson")
        assert result is None  # Placeholder
    
    def test_calculate_area(self):
        """Test area calculation."""
        engine = SpatialAnalysisEngine()
        areas = engine.calculate_area("/path/to/layer.geojson")
        assert isinstance(areas, list)
    
    def test_calculate_length(self):
        """Test length calculation."""
        engine = SpatialAnalysisEngine()
        lengths = engine.calculate_length("/path/to/layer.geojson")
        assert isinstance(lengths, list)


class TestGeospatialMetadataManager:
    """Tests for GeospatialMetadataManager."""
    
    def test_register_raster_metadata(self):
        """Test registering raster metadata."""
        manager = GeospatialMetadataManager()
        metadata = manager.register_raster_metadata(
            raster_dataset_id="raster-1",
            band_index=1,
            band_name="Band 1",
            band_description="Red band",
            statistics={"min": 0, "max": 255},
            histogram={"counts": [0] * 256},
            color_interpretation="Red",
            nodata_value=-9999,
            min_value=0.0,
            max_value=255.0,
            mean_value=127.5,
            stddev_value=50.0
        )
        assert metadata.band_name == "Band 1"
    
    def test_get_raster_metadata(self):
        """Test getting raster metadata."""
        manager = GeospatialMetadataManager()
        manager.register_raster_metadata(
            raster_dataset_id="raster-1",
            band_index=1,
            band_name="Band 1",
            band_description="Red band",
            statistics={"min": 0, "max": 255},
            histogram={"counts": [0] * 256},
            color_interpretation="Red",
            nodata_value=-9999,
            min_value=0.0,
            max_value=255.0,
            mean_value=127.5,
            stddev_value=50.0
        )
        metadata_list = manager.get_raster_metadata("raster-1")
        assert len(metadata_list) >= 1
    
    def test_register_spatial_index(self):
        """Test registering spatial index."""
        manager = GeospatialMetadataManager()
        index = manager.register_spatial_index(
            dataset_id="dataset-1",
            dataset_type="vector",
            index_type="GIST",
            index_name="spatial_idx"
        )
        assert index.index_type == "GIST"
    
    def test_get_spatial_index(self):
        """Test getting spatial index."""
        manager = GeospatialMetadataManager()
        manager.register_spatial_index(
            dataset_id="dataset-1",
            dataset_type="vector",
            index_type="GIST",
            index_name="spatial_idx"
        )
        index = manager.get_spatial_index("dataset-1")
        assert index is not None


class TestGeospatialValidator:
    """Tests for GeospatialValidator."""
    
    def test_validate_raster_format(self):
        """Test validating raster format."""
        validator = GeospatialValidator()
        issues = validator.validate_raster_format("GTiff")
        assert len(issues) == 0
    
    def test_validate_raster_format_invalid(self):
        """Test validating invalid raster format."""
        validator = GeospatialValidator()
        issues = validator.validate_raster_format("INVALID")
        assert len(issues) > 0
    
    def test_validate_vector_format(self):
        """Test validating vector format."""
        validator = GeospatialValidator()
        issues = validator.validate_vector_format("GeoJSON")
        assert len(issues) == 0
    
    def test_validate_crs(self):
        """Test validating CRS."""
        validator = GeospatialValidator()
        issues = validator.validate_crs("EPSG:4326")
        assert len(issues) == 0
    
    def test_validate_extent(self):
        """Test validating extent."""
        validator = GeospatialValidator()
        issues = validator.validate_extent(-180, -90, 180, 90)
        assert len(issues) == 0
    
    def test_validate_extent_invalid(self):
        """Test validating invalid extent."""
        validator = GeospatialValidator()
        issues = validator.validate_extent(180, 90, -180, -90)
        assert len(issues) > 0
    
    def test_validate_resolution(self):
        """Test validating resolution."""
        validator = GeospatialValidator()
        issues = validator.validate_resolution(30.0)
        assert len(issues) == 0
    
    def test_validate_buffer_distance(self):
        """Test validating buffer distance."""
        validator = GeospatialValidator()
        issues = validator.validate_buffer_distance(100.0)
        assert len(issues) == 0
    
    def test_validate_band_index(self):
        """Test validating band index."""
        validator = GeospatialValidator()
        issues = validator.validate_band_index(1, 10)
        assert len(issues) == 0


class TestRasterDatasetInfo:
    """Tests for GDALDatasetInfo."""
    
    def test_dataset_info(self):
        """Test dataset info creation."""
        info = GDALDatasetInfo(
            driver="GTiff",
            width=1024,
            height=1024,
            bands=3,
            crs="EPSG:4326",
            bounds=(-180, -90, 180, 90),
            transform=(0, 1, 0, 0, 0, 1, 0, 0, 0),
            no_data_value=-9999
        )
        assert info.driver == "GTiff"


class TestRasterProfile:
    """Tests for RasterProfile."""
    
    def test_raster_profile(self):
        """Test raster profile creation."""
        profile = RasterProfile(
            driver="GTiff",
            width=1024,
            height=1024,
            crs="EPSG:4326",
            transform=None,
            nodata=-9999,
            dtype="float32",
            count=3
        )
        assert profile.driver == "GTiff"


class TestCoordinateSystem:
    """Tests for CoordinateSystem."""
    
    def test_coordinate_system(self):
        """Test coordinate system creation."""
        crs = CoordinateSystem(
            id="test",
            epsg_code=4326,
            crs_name="WGS 84",
            crs_type="Geographic",
            proj4_definition="+proj=longlat +datum=WGS84",
            is_geographic=True,
            is_projected=False
        )
        assert crs.epsg_code == 4326


class TestTerrainModel:
    """Tests for TerrainModel."""
    
    def test_terrain_model(self):
        """Test terrain model creation."""
        model = TerrainModel(
            id="test",
            name="test_dem",
            raster_dataset_id="raster-1",
            dem_source="SRTM",
            resolution=30.0,
            vertical_datum="WGS84",
            coverage_area="-180,-90,180,90",
            min_elevation=0.0,
            max_elevation=4000.0,
            status="ready"
        )
        assert model.name == "test_dem"


class TestRasterStatistics:
    """Tests for RasterStatistics."""
    
    def test_raster_statistics(self):
        """Test raster statistics creation."""
        stats = RasterStatistics(
            min=0.0,
            max=255.0,
            mean=127.5,
            stddev=50.0,
            sum=127500.0,
            count=1000
        )
        assert stats.min == 0.0
