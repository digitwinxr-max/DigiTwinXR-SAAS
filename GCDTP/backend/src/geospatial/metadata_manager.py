"""
Geospatial Metadata Manager

Manages geospatial dataset metadata.
"""

import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RasterMetadata:
    """Raster metadata."""
    id: str
    raster_dataset_id: str
    band_index: int
    band_name: str
    band_description: str
    statistics: Dict
    histogram: Dict
    color_interpretation: str
    nodata_value: float
    min_value: float
    max_value: float
    mean_value: float
    stddev_value: float
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SpatialIndex:
    """Spatial index metadata."""
    id: str
    dataset_id: str
    dataset_type: str
    index_type: str
    index_name: str
    is_active: bool


class GeospatialMetadataManager:
    """
    Manages geospatial metadata.
    """
    
    def __init__(self):
        self._raster_metadata: Dict[str, RasterMetadata] = {}
        self._spatial_indexes: Dict[str, SpatialIndex] = {}
    
    def register_raster_metadata(
        self,
        raster_dataset_id: str,
        band_index: int,
        band_name: str,
        band_description: str,
        statistics: Dict,
        histogram: Dict,
        color_interpretation: str,
        nodata_value: float,
        min_value: float,
        max_value: float,
        mean_value: float,
        stddev_value: float
    ) -> RasterMetadata:
        """Register raster metadata."""
        metadata_id = str(uuid.uuid4())
        
        metadata = RasterMetadata(
            id=metadata_id,
            raster_dataset_id=raster_dataset_id,
            band_index=band_index,
            band_name=band_name,
            band_description=band_description,
            statistics=statistics,
            histogram=histogram,
            color_interpretation=color_interpretation,
            nodata_value=nodata_value,
            min_value=min_value,
            max_value=max_value,
            mean_value=mean_value,
            stddev_value=stddev_value
        )
        
        self._raster_metadata[metadata_id] = metadata
        return metadata
    
    def get_raster_metadata(self, raster_dataset_id: str) -> List[RasterMetadata]:
        """Get metadata for a raster dataset."""
        return [
            m for m in self._raster_metadata.values()
            if m.raster_dataset_id == raster_dataset_id
        ]
    
    def register_spatial_index(
        self,
        dataset_id: str,
        dataset_type: str,
        index_type: str,
        index_name: str
    ) -> SpatialIndex:
        """Register a spatial index."""
        index_id = str(uuid.uuid4())
        
        index = SpatialIndex(
            id=index_id,
            dataset_id=dataset_id,
            dataset_type=dataset_type,
            index_type=index_type,
            index_name=index_name,
            is_active=True
        )
        
        self._spatial_indexes[index_id] = index
        return index
    
    def get_spatial_index(self, dataset_id: str) -> Optional[SpatialIndex]:
        """Get spatial index for a dataset."""
        for index in self._spatial_indexes.values():
            if index.dataset_id == dataset_id and index.is_active:
                return index
        return None
    
    def activate_index(self, index_id: str) -> bool:
        """Activate a spatial index."""
        index = self._spatial_indexes.get(index_id)
        if index:
            index.is_active = True
            return True
        return False
    
    def deactivate_index(self, index_id: str) -> bool:
        """Deactivate a spatial index."""
        index = self._spatial_indexes.get(index_id)
        if index:
            index.is_active = False
            return True
        return False
