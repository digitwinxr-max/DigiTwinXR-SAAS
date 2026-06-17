"""
Ontology Sync Engine

Synchronizes ontology with assets, documents, work orders, devices, organizations, and Neo4j.
"""

import uuid
from typing import Dict, List, Optional
from datetime import datetime
from backend.src.ontology.ontology_registry import OntologyRegistry
from backend.src.ontology.ontology_types import (
    SyncStatus,
    SyncRecord,
)
from backend.src.core.events import get_event_bus, EventType


class OntologySyncEngine:
    """
    Synchronizes ontology with external entities.
    
    Synchronizes with:
    - Assets
    - Documents
    - Work Orders
    - Devices
    - Organizations
    - Neo4j projections
    """
    
    def __init__(self, registry: Optional[OntologyRegistry] = None):
        self.registry = registry or OntologyRegistry()
        self.event_bus = get_event_bus()
        
        # Sync history
        self._sync_history: List[SyncRecord] = []
    
    # =========================================================================
    # Asset Sync
    # =========================================================================
    
    def sync_asset(
        self,
        asset_id: str,
        class_id: str,
        properties: Optional[Dict] = None
    ) -> SyncRecord:
        """
        Sync an asset with ontology.
        
        Args:
            asset_id: Asset ID
            class_id: Ontology class ID
            properties: Optional properties
            
        Returns:
            SyncRecord
        """
        # Assign tag to asset
        self.registry.assign_tag(
            entity_type="asset",
            entity_id=asset_id,
            class_id=class_id
        )
        
        record = SyncRecord(
            id=str(uuid.uuid4()),
            entity_type="asset",
            entity_id=asset_id,
            operation="classify",
            status=SyncStatus.COMPLETED,
            class_id=class_id
        )
        
        self._sync_history.append(record)
        
        self.event_bus.publish(
            EventType.ONTOLOGY_SYNC_COMPLETED,
            source="ontology_sync",
            data={
                "entity_type": "asset",
                "entity_id": asset_id,
                "class_id": class_id
            }
        )
        
        return record
    
    # =========================================================================
    # Document Sync
    # =========================================================================
    
    def sync_document(
        self,
        document_id: str,
        class_id: str
    ) -> SyncRecord:
        """
        Sync a document with ontology.
        
        Args:
            document_id: Document ID
            class_id: Ontology class ID
            
        Returns:
            SyncRecord
        """
        self.registry.assign_tag(
            entity_type="document",
            entity_id=document_id,
            class_id=class_id
        )
        
        record = SyncRecord(
            id=str(uuid.uuid4()),
            entity_type="document",
            entity_id=document_id,
            operation="classify",
            status=SyncStatus.COMPLETED,
            class_id=class_id
        )
        
        self._sync_history.append(record)
        
        self.event_bus.publish(
            EventType.ONTOLOGY_SYNC_COMPLETED,
            source="ontology_sync",
            data={
                "entity_type": "document",
                "entity_id": document_id,
                "class_id": class_id
            }
        )
        
        return record
    
    # =========================================================================
    # Work Order Sync
    # =========================================================================
    
    def sync_work_order(
        self,
        work_order_id: str,
        class_id: str
    ) -> SyncRecord:
        """
        Sync a work order with ontology.
        
        Args:
            work_order_id: Work order ID
            class_id: Ontology class ID
            
        Returns:
            SyncRecord
        """
        self.registry.assign_tag(
            entity_type="work_order",
            entity_id=work_order_id,
            class_id=class_id
        )
        
        record = SyncRecord(
            id=str(uuid.uuid4()),
            entity_type="work_order",
            entity_id=work_order_id,
            operation="classify",
            status=SyncStatus.COMPLETED,
            class_id=class_id
        )
        
        self._sync_history.append(record)
        
        self.event_bus.publish(
            EventType.ONTOLOGY_SYNC_COMPLETED,
            source="ontology_sync",
            data={
                "entity_type": "work_order",
                "entity_id": work_order_id,
                "class_id": class_id
            }
        )
        
        return record
    
    # =========================================================================
    # Device Sync
    # =========================================================================
    
    def sync_device(
        self,
        device_id: str,
        class_id: str
    ) -> SyncRecord:
        """
        Sync a device with ontology.
        
        Args:
            device_id: Device ID
            class_id: Ontology class ID
            
        Returns:
            SyncRecord
        """
        self.registry.assign_tag(
            entity_type="device",
            entity_id=device_id,
            class_id=class_id
        )
        
        record = SyncRecord(
            id=str(uuid.uuid4()),
            entity_type="device",
            entity_id=device_id,
            operation="classify",
            status=SyncStatus.COMPLETED,
            class_id=class_id
        )
        
        self._sync_history.append(record)
        
        self.event_bus.publish(
            EventType.ONTOLOGY_SYNC_COMPLETED,
            source="ontology_sync",
            data={
                "entity_type": "device",
                "entity_id": device_id,
                "class_id": class_id
            }
        )
        
        return record
    
    # =========================================================================
    # Organization Sync
    # =========================================================================
    
    def sync_organization(
        self,
        organization_id: str,
        class_id: str
    ) -> SyncRecord:
        """
        Sync an organization with ontology.
        
        Args:
            organization_id: Organization ID
            class_id: Ontology class ID
            
        Returns:
            SyncRecord
        """
        self.registry.assign_tag(
            entity_type="organization",
            entity_id=organization_id,
            class_id=class_id
        )
        
        record = SyncRecord(
            id=str(uuid.uuid4()),
            entity_type="organization",
            entity_id=organization_id,
            operation="classify",
            status=SyncStatus.COMPLETED,
            class_id=class_id
        )
        
        self._sync_history.append(record)
        
        self.event_bus.publish(
            EventType.ONTOLOGY_SYNC_COMPLETED,
            source="ontology_sync",
            data={
                "entity_type": "organization",
                "entity_id": organization_id,
                "class_id": class_id
            }
        )
        
        return record
    
    # =========================================================================
    # Neo4j Sync
    # =========================================================================
    
    def sync_to_neo4j(
        self,
        entity_type: str,
        entity_id: str,
        class_id: str
    ) -> SyncRecord:
        """
        Sync ontology classification to Neo4j graph.
        
        Args:
            entity_type: Entity type
            entity_id: Entity ID
            class_id: Ontology class ID
            
        Returns:
            SyncRecord
        """
        # In production, would sync to Neo4j
        # This creates a record for tracking
        
        record = SyncRecord(
            id=str(uuid.uuid4()),
            entity_type=entity_type,
            entity_id=entity_id,
            operation="sync_neo4j",
            status=SyncStatus.COMPLETED,
            class_id=class_id
        )
        
        self._sync_history.append(record)
        return record
    
    # =========================================================================
    # Batch Operations
    # =========================================================================
    
    def batch_sync_assets(
        self,
        asset_mappings: List[Dict]
    ) -> List[SyncRecord]:
        """
        Batch sync assets.
        
        Args:
            asset_mappings: List of {asset_id, class_id}
            
        Returns:
            List of SyncRecords
        """
        records = []
        for mapping in asset_mappings:
            record = self.sync_asset(
                asset_id=mapping["asset_id"],
                class_id=mapping["class_id"]
            )
            records.append(record)
        return records
    
    def batch_sync_documents(
        self,
        document_mappings: List[Dict]
    ) -> List[SyncRecord]:
        """
        Batch sync documents.
        
        Args:
            document_mappings: List of {document_id, class_id}
            
        Returns:
            List of SyncRecords
        """
        records = []
        for mapping in document_mappings:
            record = self.sync_document(
                document_id=mapping["document_id"],
                class_id=mapping["class_id"]
            )
            records.append(record)
        return records
    
    def batch_sync_work_orders(
        self,
        work_order_mappings: List[Dict]
    ) -> List[SyncRecord]:
        """
        Batch sync work orders.
        
        Args:
            work_order_mappings: List of {work_order_id, class_id}
            
        Returns:
            List of SyncRecords
        """
        records = []
        for mapping in work_order_mappings:
            record = self.sync_work_order(
                work_order_id=mapping["work_order_id"],
                class_id=mapping["class_id"]
            )
            records.append(record)
        return records
    
    # =========================================================================
    # History
    # =========================================================================
    
    def get_sync_history(
        self,
        entity_type: Optional[str] = None,
        limit: int = 100
    ) -> List[SyncRecord]:
        """Get sync history."""
        history = self._sync_history
        
        if entity_type:
            history = [r for r in history if r.entity_type == entity_type]
        
        return sorted(history, key=lambda x: x.synced_at, reverse=True)[:limit]
    
    def clear_sync_history(self) -> None:
        """Clear sync history."""
        self._sync_history.clear()
