"""
Geospatial Module

Provides advanced GIS analytics capabilities:
- GDAL adapter
- Rasterio adapter
- GeoPandas adapter
- Raster management
- Vector management
- Coordinate transformation
- Terrain analysis
- Raster analysis
- Spatial analysis

Components:
- GDALAdapter
- RasterioAdapter
- GeoPandasAdapter
- RasterManager
- VectorManager
- CoordinateTransformEngine
- TerrainAnalysisEngine
- RasterAnalysisEngine
- SpatialAnalysisEngine
- GeospatialMetadataManager
- GeospatialValidator
"""

from .gdal_adapter import GDALAdapter, GDALDatasetInfo, GDALBandInfo
from .rasterio_adapter import RasterioAdapter, RasterWindow, RasterProfile
from .geopandas_adapter import GeoPandasAdapter, VectorDatasetInfo
from .raster_manager import RasterManager, RasterDataset
from .vector_manager import VectorManager, VectorDataset
from .coordinate_transform_engine import CoordinateTransformEngine, CoordinateSystem
from .terrain_analysis_engine import (
    TerrainAnalysisEngine,
    TerrainModel,
    SlopeResult,
    AspectResult
)
from .raster_analysis_engine import RasterAnalysisEngine, RasterStatistics, RasterHistogram
from .spatial_analysis_engine import SpatialAnalysisEngine, NearestNeighborResult, BufferResult
from .metadata_manager import GeospatialMetadataManager, RasterMetadata, SpatialIndex
from .geospatial_validator import GeospatialValidator


__all__ = [
    # GDAL Adapter
    "GDALAdapter",
    "GDALDatasetInfo",
    "GDALBandInfo",
    # Rasterio Adapter
    "RasterioAdapter",
    "RasterWindow",
    "RasterProfile",
    # GeoPandas Adapter
    "GeoPandasAdapter",
    "VectorDatasetInfo",
    # Managers
    "RasterManager",
    "RasterDataset",
    "VectorManager",
    "VectorDataset",
    # Engines
    "CoordinateTransformEngine",
    "CoordinateSystem",
    "TerrainAnalysisEngine",
    "TerrainModel",
    "SlopeResult",
    "AspectResult",
    "RasterAnalysisEngine",
    "RasterStatistics",
    "RasterHistogram",
    "SpatialAnalysisEngine",
    "NearestNeighborResult",
    "BufferResult",
    # Metadata
    "GeospatialMetadataManager",
    "RasterMetadata",
    "SpatialIndex",
    # Validator
    "GeospatialValidator",
]
