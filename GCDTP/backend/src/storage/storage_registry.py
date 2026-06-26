"""
Storage Registry

Manages storage references and tracking.
"""

import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

from .storage_types import ReferenceType


@dataclass
class StorageReference:
    """Storage reference."""
    id: str
    registry_key: str
    object_id: str
    reference_type: ReferenceType
    reference_id: str
    owner_organization_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)


class StorageRegistry:
    """
    Manages storage references.
    
    Tracks:
    - Buckets
    - Objects
    - Statuses
    - Owners
    - Versions
    - References
    """
    
    def __init__(self):
        self._references: Dict[str, StorageReference] = {}
        self._object_index: Dict[str, List[str]] = {}  # object_id -> reference_ids
        self._type_index: Dict[ReferenceType, List[str]] = {}  # type -> reference_ids
        self._org_index: Dict[str, List[str]] = {}  # org_id -> reference_ids
    
    def register_reference(
        self,
        object_id: str,
        reference_type: ReferenceType,
        reference_id: str,
        owner_organization_id: str
    ) -> StorageReference:
        """Register a storage reference."""
        ref_id = str(uuid.uuid4())
        registry_key = f"{reference_type.value}:{reference_id}"
        
        reference = StorageReference(
            id=ref_id,
            registry_key=registry_key,
            object_id=object_id,
            reference_type=reference_type,
            reference_id=reference_id,
            owner_organization_id=owner_organization_id
        )
        
        self._references[ref_id] = reference
        
        # Update indexes
        if object_id not in self._object_index:
            self._object_index[object_id] = []
        self._object_index[object_id].append(ref_id)
        
        if reference_type not in self._type_index:
            self._type_index[reference_type] = []
        self._type_index[reference_type].append(ref_id)
        
        if owner_organization_id not in self._org_index:
            self._org_index[owner_organization_id] = []
        self._org_index[owner_organization_id].append(ref_id)
        
        return reference
    
    def get_reference(self, ref_id: str) -> Optional[StorageReference]:
        """Get a reference."""
        return self._references.get(ref_id)
    
    def get_object_references(self, object_id: str) -> List[StorageReference]:
        """Get all references for an object."""
        ref_ids = self._object_index.get(object_id, [])
        return [self._references[rid] for rid in ref_ids if rid in self._references]
    
    def get_references_by_type(self, reference_type: ReferenceType) -> List[StorageReference]:
        """Get references by type."""
        ref_ids = self._type_index.get(reference_type, [])
        return [self._references[rid] for rid in ref_ids if rid in self._references]
    
    def get_references_by_reference_id(self, reference_type: ReferenceType, reference_id: str) -> List[StorageReference]:
        """Get references by reference ID."""
        return [
            ref for ref in self.get_references_by_type(reference_type)
            if ref.reference_id == reference_id
        ]
    
    def get_organization_references(self, org_id: str) -> List[StorageReference]:
        """Get all references for an organization."""
        ref_ids = self._org_index.get(org_id, [])
        return [self._references[rid] for rid in ref_ids if rid in self._references]
    
    def delete_reference(self, ref_id: str) -> bool:
        """Delete a reference."""
        reference = self._references.get(ref_id)
        if not reference:
            return False
        
        # Remove from indexes
        if reference.object_id in self._object_index:
            self._object_index[reference.object_id].remove(ref_id)
        
        if reference.reference_type in self._type_index:
            self._type_index[reference.reference_type].remove(ref_id)
        
        if reference.owner_organization_id in self._org_index:
            self._org_index[reference.owner_organization_id].remove(ref_id)
        
        del self._references[ref_id]
        return True
    
    def get_object_id_for_reference(self, reference_type: ReferenceType, reference_id: str) -> Optional[str]:
        """Get object ID for a reference."""
        refs = self.get_references_by_reference_id(reference_type, reference_id)
        if refs:
            return refs[0].object_id
        return None
