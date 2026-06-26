"""
Spatial Analysis Engine

Provides spatial analysis operations on vector data using Shapely.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
import geopandas as gpd
from shapely.geometry import shape, Point, LineString, Polygon
from shapely.ops import unary_union
import json

logger = logging.getLogger(__name__)


@dataclass
class NearestNeighborResult:
    """Nearest neighbor result."""
    source_feature_id: str
    target_feature_id: str
    distance: float


@dataclass
class BufferResult:
    """Buffer operation result."""
    source_layer: str
    distance: float
    result_features: List[str]


class SpatialAnalysisEngine:
    """
    Spatial analysis engine using Shapely and GeoPandas.

    Features:
    - Buffer analysis
    - Intersections
    - Overlay operations
    - Nearest neighbor
    - Distance analysis
    """

    def __init__(self):
        self._datasets: Dict[str, gpd.GeoDataFrame] = {}
        self._results: Dict[str, Any] = {}

    def _load_dataset(self, layer_path: str) -> Optional[gpd.GeoDataFrame]:
        """Load a dataset from path or cache."""
        if layer_path not in self._datasets:
            try:
                self._datasets[layer_path] = gpd.read_file(layer_path)
            except Exception as e:
                logger.error(f"Error loading dataset {layer_path}: {e}")
                return None
        return self._datasets[layer_path]

    def buffer(
        self,
        layer_path: str,
        distance: float,
        resolution: int = 16
    ) -> Optional[gpd.GeoDataFrame]:
        """Create buffer around features."""
        try:
            gdf = self._load_dataset(layer_path)
            if gdf is None:
                return None
            
            # Create buffer around all geometries
            buffered = gdf.geometry.buffer(distance, resolution=resolution)
            result = gdf.copy()
            result.geometry = buffered
            result["buffer_distance"] = distance
            
            self._results[f"buffer_{layer_path}"] = result
            return result
            
        except Exception as e:
            logger.error(f"Error creating buffer: {e}")
            return None

    def intersection(
        self,
        layer1_path: str,
        layer2_path: str
    ) -> Optional[gpd.GeoDataFrame]:
        """Perform intersection operation."""
        try:
            gdf1 = self._load_dataset(layer1_path)
            gdf2 = self._load_dataset(layer2_path)
            
            if gdf1 is None or gdf2 is None:
                return None
            
            # Ensure CRS matches
            if gdf1.crs != gdf2.crs:
                gdf2 = gdf2.to_crs(gdf1.crs)
            
            # Perform intersection using overlay
            result = gpd.overlay(gdf1, gdf2, how='intersection')
            return result
            
        except Exception as e:
            logger.error(f"Error performing intersection: {e}")
            return None

    def union(
        self,
        layer1_path: str,
        layer2_path: str
    ) -> Optional[gpd.GeoDataFrame]:
        """Perform union operation."""
        try:
            gdf1 = self._load_dataset(layer1_path)
            gdf2 = self._load_dataset(layer2_path)
            
            if gdf1 is None or gdf2 is None:
                return None
            
            # Ensure CRS matches
            if gdf1.crs != gdf2.crs:
                gdf2 = gdf2.to_crs(gdf1.crs)
            
            # Perform union using overlay
            result = gpd.overlay(gdf1, gdf2, how='union')
            return result
            
        except Exception as e:
            logger.error(f"Error performing union: {e}")
            return None

    def difference(
        self,
        layer1_path: str,
        layer2_path: str
    ) -> Optional[gpd.GeoDataFrame]:
        """Perform difference operation."""
        try:
            gdf1 = self._load_dataset(layer1_path)
            gdf2 = self._load_dataset(layer2_path)
            
            if gdf1 is None or gdf2 is None:
                return None
            
            # Ensure CRS matches
            if gdf1.crs != gdf2.crs:
                gdf2 = gdf2.to_crs(gdf1.crs)
            
            # Perform difference using overlay
            result = gpd.overlay(gdf1, gdf2, how='difference')
            return result
            
        except Exception as e:
            logger.error(f"Error performing difference: {e}")
            return None

    def symmetric_difference(
        self,
        layer1_path: str,
        layer2_path: str
    ) -> Optional[gpd.GeoDataFrame]:
        """Perform symmetric difference."""
        try:
            gdf1 = self._load_dataset(layer1_path)
            gdf2 = self._load_dataset(layer2_path)
            
            if gdf1 is None or gdf2 is None:
                return None
            
            # Ensure CRS matches
            if gdf1.crs != gdf2.crs:
                gdf2 = gdf2.to_crs(gdf1.crs)
            
            # Perform symmetric difference using overlay
            result = gpd.overlay(gdf1, gdf2, how='symmetric_difference')
            return result
            
        except Exception as e:
            logger.error(f"Error performing symmetric difference: {e}")
            return None

    def clip(
        self,
        source_path: str,
        clip_path: str
    ) -> Optional[gpd.GeoDataFrame]:
        """Clip source layer with clip layer."""
        try:
            source_gdf = self._load_dataset(source_path)
            clip_gdf = self._load_dataset(clip_path)
            
            if source_gdf is None or clip_gdf is None:
                return None
            
            # Ensure CRS matches
            if source_gdf.crs != clip_gdf.crs:
                source_gdf = source_gdf.to_crs(clip_gdf.crs)
            
            # Perform clip
            result = gpd.clip(source_gdf, clip_gdf)
            return result
            
        except Exception as e:
            logger.error(f"Error clipping: {e}")
            return None

    def erase(
        self,
        source_path: str,
        erase_path: str
    ) -> Optional[gpd.GeoDataFrame]:
        """Erase features from source."""
        # Same as difference
        return self.difference(source_path, erase_path)

    def update(
        self,
        source_path: str,
        update_path: str
    ) -> Optional[gpd.GeoDataFrame]:
        """Update source with update layer."""
        try:
            source_gdf = self._load_dataset(source_path)
            update_gdf = self._load_dataset(update_path)
            
            if source_gdf is None or update_gdf is None:
                return None
            
            # Ensure CRS matches
            if source_gdf.crs != update_gdf.crs:
                update_gdf = update_gdf.to_crs(source_gdf.crs)
            
            # Get all geometries from update layer
            update_geoms = list(update_gdf.geometry)
            
            # For each update geometry, replace intersecting source geometry
            result = source_gdf.copy()
            for i, geom in enumerate(result.geometry):
                for update_geom in update_geoms:
                    if geom.intersects(update_geom):
                        result.at[i, 'geometry'] = update_geom
            
            return result
            
        except Exception as e:
            logger.error(f"Error updating geometries: {e}")
            return None

    def identify(
        self,
        source_path: str,
        identify_path: str
    ) -> List[Dict]:
        """Identify features that intersect."""
        try:
            source_gdf = self._load_dataset(source_path)
            identify_gdf = self._load_dataset(identify_path)
            
            if source_gdf is None or identify_gdf is None:
                return []
            
            results = []
            for idx, row in source_gdf.iterrows():
                for id_idx, id_row in identify_gdf.iterrows():
                    if row.geometry.intersects(id_row.geometry):
                        intersection = row.geometry.intersection(id_row.geometry)
                        results.append({
                            "source_id": idx,
                            "identify_id": id_idx,
                            "intersects": True,
                            "intersection_area": intersection.area if hasattr(intersection, 'area') else None
                        })
            
            return results
            
        except Exception as e:
            logger.error(f"Error identifying intersections: {e}")
            return []

    def nearest_neighbor(
        self,
        source_path: str,
        target_path: str,
        max_distance: float = 0
    ) -> List[NearestNeighborResult]:
        """Find nearest neighbor features."""
        try:
            source_gdf = self._load_dataset(source_path)
            target_gdf = self._load_dataset(target_path)
            
            if source_gdf is None or target_gdf is None:
                return []
            
            results = []
            for idx, row in source_gdf.iterrows():
                min_dist = float('inf')
                nearest_id = None
                
                source_centroid = row.geometry.centroid
                
                for t_idx, t_row in target_gdf.iterrows():
                    dist = source_centroid.distance(t_row.geometry.centroid)
                    if dist < min_dist:
                        min_dist = dist
                        nearest_id = t_idx
                
                if max_distance == 0 or min_dist <= max_distance:
                    results.append(NearestNeighborResult(
                        source_feature_id=str(idx),
                        target_feature_id=str(nearest_id),
                        distance=min_dist
                    ))
            
            return results
            
        except Exception as e:
            logger.error(f"Error finding nearest neighbors: {e}")
            return []

    def calculate_distance(
        self,
        source_path: str,
        target_path: str
    ) -> List[float]:
        """Calculate distances between features."""
        try:
            source_gdf = self._load_dataset(source_path)
            target_gdf = self._load_dataset(target_path)
            
            if source_gdf is None or target_gdf is None:
                return []
            
            distances = []
            for idx, row in source_gdf.iterrows():
                source_centroid = row.geometry.centroid
                for t_idx, t_row in target_gdf.iterrows():
                    dist = source_centroid.distance(t_row.geometry.centroid)
                    distances.append(dist)
            
            return distances
            
        except Exception as e:
            logger.error(f"Error calculating distances: {e}")
            return []

    def calculate_centroid(self, layer_path: str) -> Optional[gpd.GeoDataFrame]:
        """Calculate centroids of features."""
        try:
            gdf = self._load_dataset(layer_path)
            if gdf is None:
                return None
            
            result = gdf.copy()
            result.geometry = gdf.geometry.centroid
            result["centroid_x"] = result.geometry.x
            result["centroid_y"] = result.geometry.y
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating centroids: {e}")
            return None

    def calculate_boundary(self, layer_path: str) -> Optional[gpd.GeoDataFrame]:
        """Calculate boundaries of features."""
        try:
            gdf = self._load_dataset(layer_path)
            if gdf is None:
                return None
            
            result = gdf.copy()
            result.geometry = gdf.geometry.boundary
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating boundaries: {e}")
            return None

    def calculate_area(self, layer_path: str) -> List[float]:
        """Calculate areas of features."""
        try:
            gdf = self._load_dataset(layer_path)
            if gdf is None:
                return []
            
            return gdf.geometry.area.tolist()
            
        except Exception as e:
            logger.error(f"Error calculating areas: {e}")
            return []

    def calculate_length(self, layer_path: str) -> List[float]:
        """Calculate lengths of features."""
        try:
            gdf = self._load_dataset(layer_path)
            if gdf is None:
                return []
            
            return gdf.geometry.length.tolist()
            
        except Exception as e:
            logger.error(f"Error calculating lengths: {e}")
            return []

    def spatial_join(
        self,
        source_path: str,
        target_path: str,
        join_type: str = "one_to_one",
        predicate: str = "intersects"
    ) -> Optional[gpd.GeoDataFrame]:
        """Perform spatial join."""
        try:
            source_gdf = self._load_dataset(source_path)
            target_gdf = self._load_dataset(target_path)
            
            if source_gdf is None or target_gdf is None:
                return None
            
            # Ensure CRS matches
            if source_gdf.crs != target_gdf.crs:
                target_gdf = target_gdf.to_crs(source_gdf.crs)
            
            # Map join type
            how_map = {
                "one_to_one": "one_to_one",
                "one_to_many": "one_to_many",
                "many_to_one": "many_to_one",
                "inner": "inner",
                "left": "left",
                "right": "right"
            }
            how = how_map.get(join_type, "inner")
            
            result = gpd.sjoin(source_gdf, target_gdf, how=how, predicate=predicate)
            return result
            
        except Exception as e:
            logger.error(f"Error performing spatial join: {e}")
            return None

    def aggregate_polygons(
        self,
        layer_path: str,
        tolerance: float
    ) -> Optional[gpd.GeoDataFrame]:
        """Aggregate polygons using dissolve with tolerance."""
        try:
            gdf = self._load_dataset(layer_path)
            if gdf is None:
                return None
            
            # Dissolve all polygons into one
            dissolved = gdf.dissolve()
            
            # Simplify if tolerance > 0
            if tolerance > 0:
                dissolved.geometry = dissolved.geometry.simplify(tolerance, preserve_topology=True)
            
            return dissolved
            
        except Exception as e:
            logger.error(f"Error aggregating polygons: {e}")
            return None
