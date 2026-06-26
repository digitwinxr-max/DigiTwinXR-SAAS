"""
Snapshot Manager

Manages state snapshots for timeline replay and restore.
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from backend.src.services.timeline.timeline_types import (
    TimelineSnapshot,
    TopologySnapshot,
    AssetState,
    FlowState,
    ResilienceState,
)


class SnapshotManager:
    """
    Manages state snapshots for the timeline.
    
    Handles capture, restore, listing, comparison, and pruning.
    """
    
    def __init__(self):
        self.snapshots: Dict[str, TimelineSnapshot] = {}
        self._snapshot_counter = 0
    
    def capture_snapshot(
        self,
        snapshot_id: Optional[str] = None,
        graph: Optional[Any] = None,
        asset_states: Optional[Dict[str, AssetState]] = None,
        flow_states: Optional[List[FlowState]] = None,
        resilience_state: Optional[ResilienceState] = None,
        context: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> TimelineSnapshot:
        """
        Capture a snapshot of current state.
        
        Args:
            snapshot_id: Optional snapshot ID (auto-generated if not provided)
            graph: Current topology graph
            asset_states: Current asset states
            flow_states: Current flow states
            resilience_state: Current resilience metrics
            context: Simulation context
            metadata: Additional metadata
            
        Returns:
            Created TimelineSnapshot
        """
        self._snapshot_counter += 1
        snap_id = snapshot_id or f"snapshot-{self._snapshot_counter:06d}"
        
        # Capture graph snapshot
        graph_snapshot = None
        if graph:
            graph_snapshot = {
                "nodes": {k: v.to_dict() for k, v in graph.nodes.items()} if hasattr(graph, 'nodes') else {},
                "edges": [e.to_dict() for e in graph.edges] if hasattr(graph, 'edges') else [],
            }
        
        snapshot = TimelineSnapshot(
            snapshot_id=snap_id,
            timestamp=datetime.utcnow(),
            graph_snapshot=graph_snapshot,
            asset_states=asset_states or {},
            flow_states=flow_states or [],
            resilience_state=resilience_state,
            context=context or {},
            metadata=metadata or {}
        )
        
        self.snapshots[snap_id] = snapshot
        return snapshot
    
    def capture_topology_snapshot(
        self,
        snapshot_id: Optional[str] = None,
        graph: Optional[Any] = None,
        asset_states: Optional[Dict[str, AssetState]] = None,
        flow_states: Optional[List[FlowState]] = None,
        resilience_state: Optional[ResilienceState] = None,
    ) -> TopologySnapshot:
        """
        Capture a topology-specific snapshot.
        
        Args:
            snapshot_id: Optional snapshot ID
            graph: Current topology graph
            asset_states: Current asset states
            flow_states: Current flow states
            resilience_state: Current resilience metrics
            
        Returns:
            Created TopologySnapshot
        """
        self._snapshot_counter += 1
        snap_id = snapshot_id or f"topo-{self._snapshot_counter:06d}"
        
        # Capture nodes
        nodes = {}
        if graph and hasattr(graph, 'nodes'):
            for node_id, node in graph.nodes.items():
                nodes[node_id] = node.to_dict() if hasattr(node, 'to_dict') else {}
        
        # Capture edges
        edges = []
        if graph and hasattr(graph, 'edges'):
            for edge in graph.edges:
                edges.append(edge.to_dict() if hasattr(edge, 'to_dict') else {})
        
        return TopologySnapshot(
            snapshot_id=snap_id,
            timestamp=datetime.utcnow(),
            nodes=nodes,
            edges=edges,
            asset_states=asset_states or {},
            flow_states=flow_states or [],
            resilience_state=resilience_state,
        )
    
    def restore_snapshot(self, snapshot_id: str) -> Optional[TimelineSnapshot]:
        """
        Restore a snapshot by ID.
        
        Args:
            snapshot_id: ID of snapshot to restore
            
        Returns:
            TimelineSnapshot or None if not found
        """
        return self.snapshots.get(snapshot_id)
    
    def list_snapshots(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[TimelineSnapshot]:
        """
        List snapshots with optional filtering.
        
        Args:
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number to return
            
        Returns:
            List of TimelineSnapshots
        """
        filtered = []
        
        for snapshot in self.snapshots.values():
            # Time filter
            if start_time and snapshot.timestamp < start_time:
                continue
            if end_time and snapshot.timestamp > end_time:
                continue
            
            filtered.append(snapshot)
        
        # Sort by timestamp descending
        filtered.sort(key=lambda s: s.timestamp, reverse=True)
        
        return filtered[:limit]
    
    def compare_snapshots(
        self,
        snapshot_id_a: str,
        snapshot_id_b: str
    ) -> Optional[Dict]:
        """
        Compare two snapshots.
        
        Args:
            snapshot_id_a: First snapshot ID
            snapshot_id_b: Second snapshot ID
            
        Returns:
            Comparison result or None
        """
        snap_a = self.snapshots.get(snapshot_id_a)
        snap_b = self.snapshots.get(snapshot_id_b)
        
        if not snap_a or not snap_b:
            return None
        
        # Basic comparison
        return {
            "snapshot_a": snap_a.snapshot_id,
            "snapshot_b": snap_b.snapshot_id,
            "timestamp_a": snap_a.timestamp.isoformat(),
            "timestamp_b": snap_b.timestamp.isoformat(),
            "time_delta_seconds": (snap_b.timestamp - snap_a.timestamp).total_seconds(),
        }
    
    def prune_snapshots(
        self,
        keep_count: int = 10,
        older_than: Optional[datetime] = None
    ) -> List[str]:
        """
        Prune old snapshots.
        
        Args:
            keep_count: Number of recent snapshots to keep
            older_than: Delete snapshots older than this
            
        Returns:
            List of deleted snapshot IDs
        """
        deleted = []
        
        # Get sorted snapshots
        sorted_snaps = sorted(
            self.snapshots.items(),
            key=lambda x: x[1].timestamp,
            reverse=True
        )
        
        # Keep recent snapshots
        to_keep_ids = {snap_id for snap_id, _ in sorted_snaps[:keep_count]}
        
        # Find snapshots to delete
        for snap_id, snapshot in list(self.snapshots.items()):
            should_delete = False
            
            # Check if in keep list
            if snap_id not in to_keep_ids:
                # Check older_than
                if older_than and snapshot.timestamp < older_than:
                    should_delete = True
                elif not older_than:
                    # Delete all not in keep list
                    should_delete = True
            
            if should_delete:
                del self.snapshots[snap_id]
                deleted.append(snap_id)
        
        return deleted
    
    def get_snapshot_stats(self) -> Dict:
        """Get snapshot statistics."""
        if not self.snapshots:
            return {
                "total_snapshots": 0,
                "oldest": None,
                "newest": None,
            }
        
        timestamps = [s.timestamp for s in self.snapshots.values()]
        
        return {
            "total_snapshots": len(self.snapshots),
            "oldest": min(timestamps).isoformat(),
            "newest": max(timestamps).isoformat(),
        }
    
    def clear_snapshots(self) -> None:
        """Clear all snapshots."""
        self.snapshots.clear()
        self._snapshot_counter = 0
    
    def export_snapshot(self, snapshot_id: str) -> Optional[Dict]:
        """Export a snapshot to dictionary."""
        snapshot = self.snapshots.get(snapshot_id)
        if snapshot:
            return snapshot.to_dict()
        return None
    
    def import_snapshot(self, data: Dict) -> TimelineSnapshot:
        """Import a snapshot from dictionary."""
        snapshot = TimelineSnapshot(
            snapshot_id=data["snapshot_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            graph_snapshot=data.get("graph_snapshot"),
            asset_states={
                k: AssetState(**v) for k, v in data.get("asset_states", {}).items()
            },
            flow_states=[
                FlowState(**f) for f in data.get("flow_states", [])
            ],
            resilience_state=ResilienceState(**data["resilience_state"]) if data.get("resilience_state") else None,
            context=data.get("context", {}),
            metadata=data.get("metadata", {}),
        )
        
        self.snapshots[snapshot.snapshot_id] = snapshot
        return snapshot
    
    def create_asset_state(
        self,
        asset_id: str,
        status: str,
        health: float,
        load: float,
        capacity: float,
        metadata: Optional[Dict] = None
    ) -> AssetState:
        """Create an asset state."""
        return AssetState(
            asset_id=asset_id,
            status=status,
            health=health,
            load=load,
            capacity=capacity,
            metadata=metadata or {}
        )
    
    def create_flow_state(
        self,
        route_id: str,
        source: str,
        destination: str,
        path: List[str],
        load: float,
        utilization: float,
        status: str
    ) -> FlowState:
        """Create a flow state."""
        return FlowState(
            route_id=route_id,
            source=source,
            destination=destination,
            path=path,
            load=load,
            utilization=utilization,
            status=status
        )
    
    def create_resilience_state(
        self,
        network_score: float,
        critical_nodes: List[str],
        critical_edges: List[str],
        bottlenecks: Optional[List[str]] = None
    ) -> ResilienceState:
        """Create a resilience state."""
        return ResilienceState(
            timestamp=datetime.utcnow(),
            network_score=network_score,
            critical_nodes=critical_nodes,
            critical_edges=critical_edges,
            bottlenecks=bottlenecks or []
        )
