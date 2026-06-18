"""
Metadata Manager

Manages object metadata.
"""

import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ObjectMetadata:
    """Object metadata entry."""
    id: str
    object_id: str
    key: str
    value: str
    value_type: str = "string"


class MetadataManager:
    """
    Manages object metadata.
    
    Tracks:
    - asset references
    - document references
    - work order references
    - organization references
    - content type
    - size
    - checksums
    - owner
    - tags
    """
    
    def __init__(self):
        self._metadata: Dict[str, ObjectMetadata] = {}
        self._object_index: Dict[str, List[str]] = {}  # object_id -> metadata_ids
    
    def add_metadata(
        self,
        object_id: str,
        key: str,
        value: str,
        value_type: str = "string"
    ) -> ObjectMetadata:
        """Add metadata to an object."""
        metadata_id = str(uuid.uuid4())
        
        metadata = ObjectMetadata(
            id=metadata_id,
            object_id=object_id,
            key=key,
            value=value,
            value_type=value_type
        )
        
        self._metadata[metadata_id] = metadata
        
        if object_id not in self._object_index:
            self._object_index[object_id] = []
        self._object_index[object_id].append(metadata_id)
        
        return metadata
    
    def get_metadata(self, metadata_id: str) -> Optional[ObjectMetadata]:
        """Get metadata by ID."""
        return self._metadata.get(metadata_id)
    
    def get_object_metadata(self, object_id: str) -> List[ObjectMetadata]:
        """Get all metadata for an object."""
        metadata_ids = self._object_index.get(object_id, [])
        return [self._metadata[mid] for mid in metadata_ids if mid in self._metadata]
    
    def get_metadata_value(self, object_id: str, key: str) -> Optional[str]:
        """Get metadata value by key."""
        for metadata in self.get_object_metadata(object_id):
            if metadata.key == key:
                return metadata.value
        return None
    
    def update_metadata(
        self,
        metadata_id: str,
        value: str
    ) -> bool:
        """Update metadata value."""
        metadata = self._metadata.get(metadata_id)
        if metadata:
            metadata.value = value
            return True
        return False
    
    def delete_metadata(self, metadata_id: str) -> bool:
        """Delete metadata."""
        metadata = self._metadata.get(metadata_id)
        if metadata:
            object_id = metadata.object_id
            if object_id in self._object_index:
                self._object_index[object_id].remove(metadata_id)
            del self._metadata[metadata_id]
            return True
        return False
    
    def add_asset_reference(self, object_id: str, asset_id: str) -> ObjectMetadata:
        """Add asset reference."""
        return self.add_metadata(object_id, "asset_id", asset_id)
    
    def add_document_reference(self, object_id: str, document_id: str) -> ObjectMetadata:
        """Add document reference."""
        return self.add_metadata(object_id, "document_id", document_id)
    
    def add_work_order_reference(self, object_id: str, work_order_id: str) -> ObjectMetadata:
        """Add work order reference."""
        return self.add_metadata(object_id, "work_order_id", work_order_id)
    
    def add_tag(self, object_id: str, tag: str) -> ObjectMetadata:
        """Add tag to object."""
        return self.add_metadata(object_id, f"tag:{tag}", tag, "array")
    
    def get_tags(self, object_id: str) -> List[str]:
        """Get all tags for an object."""
        tags = []
        for metadata in self.get_object_metadata(object_id):
            if metadata.key.startswith("tag:"):
                tags.append(metadata.value)
        return tags
