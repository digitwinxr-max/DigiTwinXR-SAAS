"""
Diff Engine

Compares two snapshots and produces detailed change reports.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from backend.src.services.timeline.timeline_types import (
    DiffResult,
    DiffType,
    TimelineSnapshot,
    TopologySnapshot,
)


class DiffEngine:
    """
    Engine for comparing snapshots and generating change reports.
    
    Produces detailed diff results showing:
    - Added nodes/edges
    - Removed nodes/edges
    - Changed properties
    """
    
    def __init__(self):
        self.tolerance = 0.0001  # Tolerance for floating point comparison
    
    def diff_snapshots(
        self,
        snapshot_a: TimelineSnapshot,
        snapshot_b: TimelineSnapshot
    ) -> DiffResult:
        """
        Diff two timeline snapshots.
        
        Args:
            snapshot_a: First snapshot (before)
            snapshot_b: Second snapshot (after)
            
        Returns:
            DiffResult with detailed changes
        """
        result = DiffResult(
            snapshot_a_id=snapshot_a.snapshot_id,
            snapshot_b_id=snapshot_b.snapshot_id,
            timestamp_a=snapshot_a.timestamp,
            timestamp_b=snapshot_b.timestamp
        )
        
        # Diff nodes
        self._diff_nodes(snapshot_a, snapshot_b, result)
        
        # Diff edges
        self._diff_edges(snapshot_a, snapshot_b, result)
        
        # Diff asset states
        self._diff_asset_states(snapshot_a, snapshot_b, result)
        
        # Diff flow states
        self._diff_flow_states(snapshot_a, snapshot_b, result)
        
        # Generate summary
        result.summary = self._generate_summary(result)
        
        return result
    
    def diff_topology_snapshots(
        self,
        snapshot_a: TopologySnapshot,
        snapshot_b: TopologySnapshot
    ) -> DiffResult:
        """
        Diff two topology snapshots.
        
        Args:
            snapshot_a: First topology snapshot
            snapshot_b: Second topology snapshot
            
        Returns:
            DiffResult with detailed changes
        """
        result = DiffResult(
            snapshot_a_id=snapshot_a.snapshot_id,
            snapshot_b_id=snapshot_b.snapshot_id,
            timestamp_a=snapshot_a.timestamp,
            timestamp_b=snapshot_b.timestamp
        )
        
        # Diff nodes
        self._diff_topology_nodes(snapshot_a, snapshot_b, result)
        
        # Diff edges
        self._diff_topology_edges(snapshot_a, snapshot_b, result)
        
        # Generate summary
        result.summary = self._generate_summary(result)
        
        return result
    
    def diff_context(
        self,
        context_a: Dict,
        context_b: Dict
    ) -> Dict[str, Any]:
        """
        Diff two context dictionaries.
        
        Args:
            context_a: First context
            context_b: Second context
            
        Returns:
            Dictionary with context changes
        """
        changes = {
            "added": {},
            "removed": {},
            "changed": {}
        }
        
        # Find added and changed
        for key, value in context_b.items():
            if key not in context_a:
                changes["added"][key] = value
            elif context_a[key] != value:
                changes["changed"][key] = {
                    "from": context_a[key],
                    "to": value
                }
        
        # Find removed
        for key in context_a:
            if key not in context_b:
                changes["removed"][key] = context_a[key]
        
        return changes
    
    def generate_change_report(self, diff_result: DiffResult) -> str:
        """
        Generate a human-readable change report.
        
        Args:
            diff_result: Result from diff_snapshots
            
        Returns:
            Formatted change report string
        """
        lines = []
        lines.append("=" * 60)
        lines.append("SNAPSHOT DIFF REPORT")
        lines.append("=" * 60)
        lines.append(f"Before: {diff_result.snapshot_a_id}")
        lines.append(f"After:  {diff_result.snapshot_b_id}")
        lines.append(f"Time:   {diff_result.timestamp_a.isoformat()} -> {diff_result.timestamp_b.isoformat()}")
        lines.append("")
        
        # Summary
        lines.append(f"Total Changes: {diff_result.total_changes}")
        lines.append("")
        
        # Nodes
        if diff_result.nodes_added:
            lines.append(f"Nodes Added ({len(diff_result.nodes_added)}):")
            for node_id in diff_result.nodes_added[:10]:
                lines.append(f"  + {node_id}")
            if len(diff_result.nodes_added) > 10:
                lines.append(f"  ... and {len(diff_result.nodes_added) - 10} more")
            lines.append("")
        
        if diff_result.nodes_removed:
            lines.append(f"Nodes Removed ({len(diff_result.nodes_removed)}):")
            for node_id in diff_result.nodes_removed[:10]:
                lines.append(f"  - {node_id}")
            if len(diff_result.nodes_removed) > 10:
                lines.append(f"  ... and {len(diff_result.nodes_removed) - 10} more")
            lines.append("")
        
        if diff_result.nodes_changed:
            lines.append(f"Nodes Changed ({len(diff_result.nodes_changed)}):")
            for node_id, changes in list(diff_result.nodes_changed.items())[:10]:
                lines.append(f"  ~ {node_id}:")
                for prop, (old_val, new_val) in changes.items():
                    lines.append(f"      {prop}: {old_val} -> {new_val}")
            if len(diff_result.nodes_changed) > 10:
                lines.append(f"  ... and {len(diff_result.nodes_changed) - 10} more")
            lines.append("")
        
        # Edges
        if diff_result.edges_added:
            lines.append(f"Edges Added ({len(diff_result.edges_added)}):")
            for edge in diff_result.edges_added[:10]:
                lines.append(f"  + {edge.get('from_node', '?')} -> {edge.get('to_node', '?')}")
            lines.append("")
        
        if diff_result.edges_removed:
            lines.append(f"Edges Removed ({len(diff_result.edges_removed)}):")
            for edge in diff_result.edges_removed[:10]:
                lines.append(f"  - {edge.get('from_node', '?')} -> {edge.get('to_node', '?')}")
            lines.append("")
        
        # Asset states
        if diff_result.asset_states_changed:
            lines.append(f"Asset States Changed ({len(diff_result.asset_states_changed)}):")
            for asset_id, changes in list(diff_result.asset_states_changed.items())[:10]:
                lines.append(f"  ~ {asset_id}:")
                for prop, (old_val, new_val) in changes.items():
                    lines.append(f"      {prop}: {old_val} -> {new_val}")
            lines.append("")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    # =========================================================================
    # Internal Diff Methods
    # =========================================================================
    
    def _diff_nodes(
        self,
        snapshot_a: TimelineSnapshot,
        snapshot_b: TimelineSnapshot,
        result: DiffResult
    ) -> None:
        """Diff nodes between snapshots."""
        nodes_a = set(snapshot_a.graph_snapshot.get("nodes", {}).keys()) if snapshot_a.graph_snapshot else set()
        nodes_b = set(snapshot_b.graph_snapshot.get("nodes", {}).keys()) if snapshot_b.graph_snapshot else set()
        
        # Added nodes
        result.nodes_added = list(nodes_b - nodes_a)
        
        # Removed nodes
        result.nodes_removed = list(nodes_a - nodes_b)
        
        # Changed nodes
        common_nodes = nodes_a & nodes_b
        for node_id in common_nodes:
            node_a = snapshot_a.graph_snapshot["nodes"].get(node_id, {})
            node_b = snapshot_b.graph_snapshot["nodes"].get(node_id, {})
            
            changes = {}
            for key in set(node_a.keys()) | set(node_b.keys()):
                val_a = node_a.get(key)
                val_b = node_b.get(key)
                
                if val_a != val_b:
                    # Check for numeric tolerance
                    if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                        if abs(val_a - val_b) > self.tolerance:
                            changes[key] = (val_a, val_b)
                    else:
                        changes[key] = (val_a, val_b)
            
            if changes:
                result.nodes_changed[node_id] = changes
    
    def _diff_edges(
        self,
        snapshot_a: TimelineSnapshot,
        snapshot_b: TimelineSnapshot,
        result: DiffResult
    ) -> None:
        """Diff edges between snapshots."""
        edges_a = snapshot_a.graph_snapshot.get("edges", []) if snapshot_a.graph_snapshot else []
        edges_b = snapshot_b.graph_snapshot.get("edges", []) if snapshot_b.graph_snapshot else []
        
        # Create edge keys for comparison
        def edge_key(e):
            return (e.get("from_node"), e.get("to_node"))
        
        edges_a_keys = {edge_key(e) for e in edges_a}
        edges_b_keys = {edge_key(e) for e in edges_b}
        
        # Added edges
        result.edges_added = [e for e in edges_b if edge_key(e) in (edges_b_keys - edges_a_keys)]
        
        # Removed edges
        result.edges_removed = [e for e in edges_a if edge_key(e) in (edges_a_keys - edges_b_keys)]
    
    def _diff_topology_nodes(
        self,
        snapshot_a: TopologySnapshot,
        snapshot_b: TopologySnapshot,
        result: DiffResult
    ) -> None:
        """Diff topology nodes."""
        nodes_a = set(snapshot_a.nodes.keys())
        nodes_b = set(snapshot_b.nodes.keys())
        
        result.nodes_added = list(nodes_b - nodes_a)
        result.nodes_removed = list(nodes_a - nodes_b)
        
        common = nodes_a & nodes_b
        for node_id in common:
            node_a = snapshot_a.nodes.get(node_id, {})
            node_b = snapshot_b.nodes.get(node_id, {})
            
            changes = {}
            for key in set(node_a.keys()) | set(node_b.keys()):
                if node_a.get(key) != node_b.get(key):
                    changes[key] = (node_a.get(key), node_b.get(key))
            
            if changes:
                result.nodes_changed[node_id] = changes
    
    def _diff_topology_edges(
        self,
        snapshot_a: TopologySnapshot,
        snapshot_b: TopologySnapshot,
        result: DiffResult
    ) -> None:
        """Diff topology edges."""
        edges_a = {(e.get("from_node"), e.get("to_node")) for e in snapshot_a.edges}
        edges_b = {(e.get("from_node"), e.get("to_node")) for e in snapshot_b.edges}
        
        added_keys = edges_b - edges_a
        removed_keys = edges_a - edges_b
        
        result.edges_added = [e for e in snapshot_b.edges if (e.get("from_node"), e.get("to_node")) in added_keys]
        result.edges_removed = [e for e in snapshot_a.edges if (e.get("from_node"), e.get("to_node")) in removed_keys]
    
    def _diff_asset_states(
        self,
        snapshot_a: TimelineSnapshot,
        snapshot_b: TimelineSnapshot,
        result: DiffResult
    ) -> None:
        """Diff asset states."""
        assets_a = set(snapshot_a.asset_states.keys())
        assets_b = set(snapshot_b.asset_states.keys())
        
        common = assets_a & assets_b
        
        for asset_id in common:
            state_a = snapshot_a.asset_states[asset_id]
            state_b = snapshot_b.asset_states[asset_id]
            
            changes = {}
            
            # Compare state fields
            for field in ["status", "health", "load", "capacity"]:
                val_a = getattr(state_a, field, None)
                val_b = getattr(state_b, field, None)
                
                if val_a != val_b:
                    # Check numeric tolerance
                    if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                        if abs(val_a - val_b) > self.tolerance:
                            changes[field] = (val_a, val_b)
                    else:
                        changes[field] = (val_a, val_b)
            
            if changes:
                result.asset_states_changed[asset_id] = changes
    
    def _diff_flow_states(
        self,
        snapshot_a: TimelineSnapshot,
        snapshot_b: TimelineSnapshot,
        result: DiffResult
    ) -> None:
        """Diff flow states."""
        flows_a = {(f.route_id, f.source, f.destination) for f in snapshot_a.flow_states}
        flows_b = {(f.route_id, f.source, f.destination) for f in snapshot_b.flow_states}
        
        common = flows_a & flows_b
        
        changes = []
        for route_key in common:
            flow_a = next((f for f in snapshot_a.flow_states if (f.route_id, f.source, f.destination) == route_key), None)
            flow_b = next((f for f in snapshot_b.flow_states if (f.route_id, f.source, f.destination) == route_key), None)
            
            if flow_a and flow_b:
                flow_changes = {}
                for field in ["load", "utilization", "status"]:
                    val_a = getattr(flow_a, field, None)
                    val_b = getattr(flow_b, field, None)
                    
                    if val_a != val_b:
                        flow_changes[field] = (val_a, val_b)
                
                if flow_changes:
                    changes.append({
                        "route_id": route_key[0],
                        "changes": flow_changes
                    })
        
        result.flow_states_changed = changes
    
    def _generate_summary(self, result: DiffResult) -> str:
        """Generate a summary string."""
        parts = []
        
        if result.nodes_added:
            parts.append(f"{len(result.nodes_added)} nodes added")
        if result.nodes_removed:
            parts.append(f"{len(result.nodes_removed)} nodes removed")
        if result.nodes_changed:
            parts.append(f"{len(result.nodes_changed)} nodes changed")
        if result.edges_added:
            parts.append(f"{len(result.edges_added)} edges added")
        if result.edges_removed:
            parts.append(f"{len(result.edges_removed)} edges removed")
        if result.asset_states_changed:
            parts.append(f"{len(result.asset_states_changed)} asset states changed")
        
        if not parts:
            return "No changes detected"
        
        return "; ".join(parts)
