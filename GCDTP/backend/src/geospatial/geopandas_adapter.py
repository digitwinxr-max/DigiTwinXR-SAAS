"""
GeoPandas Adapter

Provides GeoPandas-based vector analysis, spatial joins, and geometry operations.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
import geopandas as gpd
from shapely.geometry import shape
from shapely.ops import unary_union

logger = logging.getLogger(__name__)


@dataclass
class VectorDatasetInfo:
    """Vector dataset information."""
    name: str
    geometry_type: str
    crs: str
    feature_count: int
    bounds: Tuple[float, float, float, float]


class GeoPandasAdapter:
    """
    GeoPandas adapter for vector operations.

    Features:
    - Vector analysis
    - Spatial joins
    - Geometry operations
    """

    def __init__(self):
        self._datasets: Dict[str, gpd.GeoDataFrame] = {}

    def read_vector(self, file_path: str) -> Optional[VectorDatasetInfo]:
        """Read a vector dataset."""
        try:
            gdf = gpd.read_file(file_path)
            self._datasets[file_path] = gdf
            
            # Get geometry type (most common)
            geom_types = gdf.geometry.geom_type.value_counts()
            geometry_type = geom_types.index[0] if len(geom_types) > 0 else "Unknown"
            
            return VectorDatasetInfo(
                name=file_path.split('/')[-1],
                geometry_type=geometry_type,
                crs=str(gdf.crs) if gdf.crs else "EPSG:4326",
                feature_count=len(gdf),
                bounds=tuple(gdf.total_bounds) if len(gdf) > 0 else (0, 0, 0, 0)
            )
        except Exception as e:
            logger.error(f"Error reading vector file {file_path}: {e}")
            return None

    def spatial_join(
        self,
        left_path: str,
        right_path: str,
        how: str = "inner",
        predicate: str = "intersects"
    ) -> Optional[gpd.GeoDataFrame]:
        """Perform spatial join."""
        try:
            left_gdf = self._datasets.get(left_path) or gpd.read_file(left_path)
            right_gdf = self._datasets.get(right_path) or gpd.read_file(right_path)
            
            # Ensure CRS matches
            if left_gdf.crs != right_gdf.crs:
                right_gdf = right_gdf.to_crs(left_gdf.crs)
            
            result = gpd.sjoin(left_gdf, right_gdf, how=how, predicate=predicate)
            return result
            
        except Exception as e:
            logger.error(f"Error performing spatial join: {e}")
            return None

    def buffer(
        self,
        file_path: str,
        distance: float,
        resolution: int = 16
    ) -> Optional[gpd.GeoDataFrame]:
        """Create buffer around geometries."""
        try:
            gdf = self._datasets.get(file_path) or gpd.read_file(file_path)
            
            # Create buffer with specified distance and resolution
            buffered = gdf.geometry.buffer(distance, resolution=resolution)
            result = gdf.copy()
            result.geometry = buffered
            return result
            
        except Exception as e:
            logger.error(f"Error creating buffer: {e}")
            return None

    def dissolve(
        self,
        file_path: str,
        by_column: str
    ) -> Optional[gpd.GeoDataFrame]:
        """Dissolve geometries by column."""
        try:
            gdf = self._datasets.get(file_path) or gpd.read_file(file_path)
            
            if by_column not in gdf.columns:
                logger.error(f"Column {by_column} not found in dataset")
                return None
            
            dissolved = gdf.dissolve(by=by_column)
            return dissolved
            
        except Exception as e:
            logger.error(f"Error dissolving geometries: {e}")
            return None

    def overlay(
        self,
        layer1_path: str,
        layer2_path: str,
        how: str = "intersection"
    ) -> Optional[gpd.GeoDataFrame]:
        """Perform overlay operation."""
        try:
            gdf1 = self._datasets.get(layer1_path) or gpd.read_file(layer1_path)
            gdf2 = self._datasets.get(layer2_path) or gpd.read_file(layer2_path)
            
            # Ensure CRS matches
            if gdf1.crs != gdf2.crs:
                gdf2 = gdf2.to_crs(gdf1.crs)
            
            result = gpd.overlay(gdf1, gdf2, how=how)
            return result
            
        except Exception as e:
            logger.error(f"Error performing overlay: {e}")
            return None

    def simplify(
        self,
        file_path: str,
        tolerance: float
    ) -> Optional[gpd.GeoDataFrame]:
        """Simplify geometries."""
        try:
            gdf = self._datasets.get(file_path) or gpd.read_file(file_path)
            
            simplified = gdf.geometry.simplify(tolerance, preserve_topology=True)
            result = gdf.copy()
            result.geometry = simplified
            return result
            
        except Exception as e:
            logger.error(f"Error simplifying geometries: {e}")
            return None

    def clip(
        self,
        source_path: str,
        clip_path: str
    ) -> Optional[gpd.GeoDataFrame]:
        """Clip geometries."""
        try:
            source_gdf = self._datasets.get(source_path) or gpd.read_file(source_path)
            clip_gdf = self._datasets.get(clip_path) or gpd.read_file(clip_path)
            
            # Ensure CRS matches
            if source_gdf.crs != clip_gdf.crs:
                source_gdf = source_gdf.to_crs(clip_gdf.crs)
            
            clipped = gpd.clip(source_gdf, clip_gdf)
            return clipped
            
        except Exception as e:
            logger.error(f"Error clipping geometries: {e}")
            return None

    def get_centroid(self, file_path: str) -> Optional[gpd.GeoDataFrame]:
        """Get centroids of geometries."""
        try:
            gdf = self._datasets.get(file_path) or gpd.read_file(file_path)
            
            centroids = gdf.geometry.centroid
            result = gdf.copy()
            result.geometry = centroids
            return result
            
        except Exception as e:
            logger.error(f"Error calculating centroids: {e}")
            return None

    def get_boundary(self, file_path: str) -> Optional[gpd.GeoDataFrame]:
        """Get boundaries of geometries."""
        try:
            gdf = self._datasets.get(file_path) or gpd.read_file(file_path)
            
            boundaries = gdf.geometry.boundary
            result = gdf.copy()
            result.geometry = boundaries
            return result
            
        except Exception as e:
            logger.error(f"Error getting boundaries: {e}")
            return None

    def get_convex_hull(self, file_path: str) -> Optional[gpd.GeoDataFrame]:
        """Get convex hull of geometries."""
        try:
            gdf = self._datasets.get(file_path) or gpd.read_file(file_path)
            
            hulls = gdf.geometry.convex_hull
            result = gdf.copy()
            result.geometry = hulls
            return result
            
        except Exception as e:
            logger.error(f"Error getting convex hulls: {e}")
            return None

    def calculate_area(self, file_path: str) -> List[float]:
        """Calculate areas of geometries in square meters (if CRS is projected) or degrees (if not)."""
        try:
            gdf = self._datasets.get(file_path) or gpd.read_file(file_path)
            
            # Calculate area (returns values in CRS units)
            areas = gdf.geometry.area.tolist()
            return areas
            
        except Exception as e:
            logger.error(f"Error calculating areas: {e}")
            return []

    def calculate_length(self, file_path: str) -> List[float]:
        """Calculate lengths of line geometries in CRS units."""
        try:
            gdf = self._datasets.get(file_path) or gpd.read_file(file_path)
            
            # Only works for line geometries
            lengths = gdf.geometry.length.tolist()
            return lengths
            
        except Exception as e:
            logger.error(f"Error calculating lengths: {e}")
            return []

    def get_supported_formats(self) -> List[str]:
        """Get list of supported formats."""
        return [
            "ESRI Shapefile", "GeoJSON", "GPKG", "GML",
            "KML", "DXF", "GeoPackage"
        ]
