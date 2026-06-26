"""
Graph Sync Engine

Synchronizes data from PostgreSQL to Neo4j.
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from backend.src.integrations.neo4j.neo4j_client import Neo4jClient
from backend.src.integrations.neo4j.graph_types import (
    EntityType,
    ProjectionStatus,
    SyncRecord,
    GraphNode,
    GraphRelationship,
)


class GraphSyncEngine:
    """
    Syncs PostgreSQL data to Neo4j.
    
    Responsibilities:
    - Node synchronization
    - Relationship synchronization
    - Sync history tracking
    - Conflict resolution
    """
    
    def __init__(self, client: Optional[Neo4jClient] = None):
        self.client = client or Neo4jClient()
        
        # Sync history
        self._sync_history: List[SyncRecord] = []
    
    def close(self):
        """Close resources."""
        self.client.close()
    
    # =========================================================================
    # Node Sync
    # =========================================================================
    
    def sync_asset_node(
        self,
        asset_data: Dict[str, Any]
    ) -> SyncRecord:
        """
        Sync an asset to a graph node.
        
        Args:
            asset_data: Asset data from PostgreSQL
            
        Returns:
            SyncRecord
        """
        node_id = f"asset_{asset_data['id']}"
        
        # Create node in Neo4j
        self.client.create_node("Asset", {
            "id": str(asset_data['id']),
            "name": asset_data.get('name', ''),
            "asset_type": asset_data.get('asset_type', ''),
            "status": asset_data.get('status', ''),
            "latitude": asset_data.get('latitude'),
            "longitude": asset_data.get('longitude'),
        })
        
        record = SyncRecord(
            id=str(uuid.uuid4()),
            entity_type=EntityType.ASSET,
            entity_id=str(asset_data['id']),
            operation="upsert",
            status=ProjectionStatus.COMPLETED,
            node_id=node_id
        )
        
        self._sync_history.append(record)
        return record
    
    def sync_work_order_node(
        self,
        work_order_data: Dict[str, Any]
    ) -> SyncRecord:
        """
        Sync a work order to a graph node.
        
        Args:
            work_order_data: Work order data
            
        Returns:
            SyncRecord
        """
        node_id = f"work_order_{work_order_data['id']}"
        
        self.client.create_node("WorkOrder", {
            "id": str(work_order_data['id']),
            "title": work_order_data.get('title', ''),
            "status": work_order_data.get('status', ''),
            "priority": work_order_data.get('priority', ''),
        })
        
        record = SyncRecord(
            id=str(uuid.uuid4()),
            entity_type=EntityType.WORK_ORDER,
            entity_id=str(work_order_data['id']),
            operation="upsert",
            status=ProjectionStatus.COMPLETED,
            node_id=node_id
        )
        
        self._sync_history.append(record)
        return record
    
    def sync_document_node(
        self,
        document_data: Dict[str, Any]
    ) -> SyncRecord:
        """
        Sync a document to a graph node.
        
        Args:
            document_data: Document data
            
        Returns:
            SyncRecord
        """
        node_id = f"document_{document_data['id']}"
        
        self.client.create_node("Document", {
            "id": str(document_data['id']),
            "name": document_data.get('name', ''),
            "document_type": document_data.get('document_type', ''),
            "version": document_data.get('version', '1.0'),
        })
        
        record = SyncRecord(
            id=str(uuid.uuid4()),
            entity_type=EntityType.DOCUMENT,
            entity_id=str(document_data['id']),
            operation="upsert",
            status=ProjectionStatus.COMPLETED,
            node_id=node_id
        )
        
        self._sync_history.append(record)
        return record
    
    def sync_device_node(
        self,
        device_data: Dict[str, Any]
    ) -> SyncRecord:
        """
        Sync a device to a graph node.
        
        Args:
            device_data: Device data
            
        Returns:
            SyncRecord
        """
        node_id = f"device_{device_data['id']}"
        
        self.client.create_node("Device", {
            "id": str(device_data['id']),
            "name": device_data.get('name', ''),
            "device_type": device_data.get('device_type', ''),
            "status": device_data.get('status', ''),
        })
        
        record = SyncRecord(
            id=str(uuid.uuid4()),
            entity_type=EntityType.DEVICE,
            entity_id=str(device_data['id']),
            operation="upsert",
            status=ProjectionStatus.COMPLETED,
            node_id=node_id
        )
        
        self._sync_history.append(record)
        return record
    
    # =========================================================================
    # Relationship Sync
    # =========================================================================
    
    def sync_relationship(
        self,
        source_id: str,
        source_type: EntityType,
        target_id: str,
        target_type: EntityType,
        rel_type: str,
        properties: Optional[Dict] = None
    ) -> SyncRecord:
        """
        Sync a relationship.
        
        Args:
            source_id: Source entity ID
            source_type: Source entity type
            target_id: Target entity ID
            target_type: Target entity type
            rel_type: Relationship type
            properties: Optional properties
            
        Returns:
            SyncRecord
        """
        neo4j_source_id = f"{source_type.value}_{source_id}"
        neo4j_target_id = f"{target_type.value}_{target_id}"
        
        self.client.create_relationship(
            source_id=neo4j_source_id,
            target_id=neo4j_target_id,
            rel_type=rel_type.upper(),
            properties=properties
        )
        
        record = SyncRecord(
            id=str(uuid.uuid4()),
            entity_type=EntityType.RELATIONSHIP,
            entity_id=f"{source_id}_{rel_type}_{target_id}",
            operation="upsert",
            status=ProjectionStatus.COMPLETED
        )
        
        self._sync_history.append(record)
        return record
    
    # =========================================================================
    # Batch Operations
    # =========================================================================
    
    def batch_sync_assets(
        self,
        assets: List[Dict[str, Any]]
    ) -> List[SyncRecord]:
        """
        Batch sync assets.
        
        Args:
            assets: List of asset data
            
        Returns:
            List of SyncRecords
        """
        records = []
        for asset in assets:
            records.append(self.sync_asset_node(asset))
        return records
    
    def batch_sync_work_orders(
        self,
        work_orders: List[Dict[str, Any]]
    ) -> List[SyncRecord]:
        """
        Batch sync work orders.
        
        Args:
            work_orders: List of work order data
            
        Returns:
            List of SyncRecords
        """
        records = []
        for wo in work_orders:
            records.append(self.sync_work_order_node(wo))
        return records
    
    def batch_sync_documents(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[SyncRecord]:
        """
        Batch sync documents.
        
        Args:
            documents: List of document data
            
        Returns:
            List of SyncRecords
        """
        records = []
        for doc in documents:
            records.append(self.sync_document_node(doc))
        return records
    
    def batch_sync_devices(
        self,
        devices: List[Dict[str, Any]]
    ) -> List[SyncRecord]:
        """
        Batch sync devices.
        
        Args:
            devices: List of device data
            
        Returns:
            List of SyncRecords
        """
        records = []
        for device in devices:
            records.append(self.sync_device_node(device))
        return records
    
    # =========================================================================
    # History
    # =========================================================================
    
    def get_sync_history(
        self,
        entity_type: Optional[EntityType] = None,
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
