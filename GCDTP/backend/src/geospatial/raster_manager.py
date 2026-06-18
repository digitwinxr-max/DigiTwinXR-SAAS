"""
Raster Manager

Manages raster datasets.
"""

import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RasterDataset:
    """Raster dataset."""
    id: str
    name: str
    file_path: str
    storage_object_id: str
    width: int
    height: int
    bands: int
    driver: str
    crs: str
    bounds: str
    status: str
    owner_organization_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)


class RasterManager:
    """
    Manages raster datasets.
    """
    
    def __init__(self):
        self._datasets: Dict[str, RasterDataset] = {}
    
    def register_dataset(
        self,
        name: str,
        file_path: str,
        storage_object_id: str,
        width: int,
        height: int,
        bands: int,
        driver: str,
        crs: str,
        bounds: str,
        owner_organization_id: str
    ) -> RasterDataset:
        """Register a raster dataset."""
        dataset_id = str(uuid.uuid4())
        
        dataset = RasterDataset(
            id=dataset_id,
            name=name,
            file_path=file_path,
            storage_object_id=storage_object_id,
            width=width,
            height=height,
            bands=bands,
            driver=driver,
            crs=crs,
            bounds=bounds,
            status="ready",
            owner_organization_id=owner_organization_id
        )
        
        self._datasets[dataset_id] = dataset
        return dataset
    
    def get_dataset(self, dataset_id: str) -> Optional[RasterDataset]:
        """Get a dataset."""
        return self._datasets.get(dataset_id)
    
    def get_dataset_by_name(self, name: str) -> Optional[RasterDataset]:
        """Get dataset by name."""
        for dataset in self._datasets.values():
            if dataset.name == name:
                return dataset
        return None
    
    def list_datasets(self) -> List[RasterDataset]:
        """List all datasets."""
        return list(self._datasets.values())
    
    def delete_dataset(self, dataset_id: str) -> bool:
        """Delete a dataset."""
        if dataset_id in self._datasets:
            del self._datasets[dataset_id]
            return True
        return False
