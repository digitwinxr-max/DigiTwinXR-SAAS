"""
Vector Manager

Manages vector datasets.
"""

import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class VectorDataset:
    """Vector dataset."""
    id: str
    name: str
    file_path: str
    storage_object_id: str
    geometry_type: str
    crs: str
    feature_count: int
    attribute_schema: Dict
    status: str
    owner_organization_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)


class VectorManager:
    """
    Manages vector datasets.
    """
    
    def __init__(self):
        self._datasets: Dict[str, VectorDataset] = {}
    
    def register_dataset(
        self,
        name: str,
        file_path: str,
        storage_object_id: str,
        geometry_type: str,
        crs: str,
        feature_count: int,
        attribute_schema: Dict,
        owner_organization_id: str
    ) -> VectorDataset:
        """Register a vector dataset."""
        dataset_id = str(uuid.uuid4())
        
        dataset = VectorDataset(
            id=dataset_id,
            name=name,
            file_path=file_path,
            storage_object_id=storage_object_id,
            geometry_type=geometry_type,
            crs=crs,
            feature_count=feature_count,
            attribute_schema=attribute_schema,
            status="ready",
            owner_organization_id=owner_organization_id
        )
        
        self._datasets[dataset_id] = dataset
        return dataset
    
    def get_dataset(self, dataset_id: str) -> Optional[VectorDataset]:
        """Get a dataset."""
        return self._datasets.get(dataset_id)
    
    def get_dataset_by_name(self, name: str) -> Optional[VectorDataset]:
        """Get dataset by name."""
        for dataset in self._datasets.values():
            if dataset.name == name:
                return dataset
        return None
    
    def list_datasets(self) -> List[VectorDataset]:
        """List all datasets."""
        return list(self._datasets.values())
    
    def delete_dataset(self, dataset_id: str) -> bool:
        """Delete a dataset."""
        if dataset_id in self._datasets:
            del self._datasets[dataset_id]
            return True
        return False
