"""
Graph Builder

Builds TopologyGraph from raw asset data.
Converts asset-centric data into topology-centric representation.
"""

from typing import Dict, List, Optional, Any
from .topology_types import (
    TopologyGraph,
    TopologyNode,
    TopologyEdge,
    NodeType,
    Layer,
    Direction,
    FlowType,
)


class GraphBuilder:
    """
    Builds infrastructure topology graphs from raw asset data.
    
    Transforms asset-centric models into topology-centric representations
    with nodes, edges, directionality, capacity, and resistance.
    """
    
    def build(self, raw_assets: Dict[str, Dict]) -> TopologyGraph:
        """
        Build a complete topology graph from raw assets.
        
        Args:
            raw_assets: Dictionary mapping asset_id -> asset data
            
        Returns:
            TopologyGraph with nodes and edges
        """
        graph = TopologyGraph()
        
        # Phase 1: Create nodes from assets
        for asset_id, asset_data in raw_assets.items():
            node = self._create_node(asset_id, asset_data)
            graph.add_node(node)
        
        # Phase 2: Create edges from relationships
        for asset_id, asset_data in raw_assets.items():
            edges = self._create_edges(asset_id, asset_data, raw_assets)
            for edge in edges:
                graph.add_edge(edge)
        
        return graph
    
    def _create_node(self, asset_id: str, asset_data: Dict) -> TopologyNode:
        """
        Create a TopologyNode from raw asset data.
        
        Args:
            asset_id: Unique identifier
            asset_data: Asset properties
            
        Returns:
            TopologyNode instance
        """
        # Determine node type
        node_type = self._infer_node_type(asset_data)
        
        # Determine layer
        layer = self._infer_layer(asset_data)
        
        # Extract position if available
        position = None
        if "location" in asset_data:
            position = {
                "x": asset_data["location"].get("x"),
                "y": asset_data["location"].get("y"),
            }
        
        # Extract capacity if available
        capacity = asset_data.get("capacity")
        
        return TopologyNode(
            id=asset_id,
            type=node_type,
            layer=layer,
            metadata=asset_data,
            capacity=capacity,
            position=position,
        )
    
    def _create_edges(
        self,
        asset_id: str,
        asset_data: Dict,
        all_assets: Dict[str, Dict]
    ) -> List[TopologyEdge]:
        """
        Create TopologyEdge instances from asset connections.
        
        Args:
            asset_id: Source asset ID
            asset_data: Source asset data
            all_assets: All assets for validation
            
        Returns:
            List of TopologyEdge instances
        """
        edges = []
        connections = asset_data.get("connections", [])
        
        for conn in connections:
            target_id = conn.get("target")
            
            # Validate target exists
            if target_id not in all_assets:
                continue
            
            edge = TopologyEdge(
                from_node=asset_id,
                to_node=target_id,
                direction=conn.get("direction", Direction.UNIDIRECTIONAL.value),
                capacity=conn.get("capacity", 1.0),
                flow_type=conn.get("flow_type", FlowType.GENERIC.value),
                resistance=conn.get("resistance", 0.1),
                length=conn.get("length"),
            )
            edges.append(edge)
            
            # For bidirectional connections, create reverse edge
            if conn.get("direction") == Direction.BIDIRECTIONAL.value:
                reverse_edge = TopologyEdge(
                    from_node=target_id,
                    to_node=asset_id,
                    direction=Direction.BIDIRECTIONAL.value,
                    capacity=conn.get("capacity", 1.0),
                    flow_type=conn.get("flow_type", FlowType.GENERIC.value),
                    resistance=conn.get("resistance", 0.1),
                    length=conn.get("length"),
                )
                edges.append(reverse_edge)
        
        return edges
    
    def _infer_node_type(self, asset_data: Dict) -> str:
        """
        Infer node type from asset data.
        
        Args:
            asset_data: Asset properties
            
        Returns:
            Node type string
        """
        # Check explicit type
        if "node_type" in asset_data:
            return asset_data["node_type"]
        
        # Infer from asset_type
        asset_type = asset_data.get("asset_type", "").lower()
        
        type_mapping = {
            "substation": NodeType.SUBSTATION.value,
            "pump": NodeType.PUMP.value,
            "pump_station": NodeType.PUMP.value,
            "junction": NodeType.JUNCTION.value,
            "station": NodeType.STATION.value,
            "generator": NodeType.GENERATOR.value,
            "power_generator": NodeType.GENERATOR.value,
            "consumer": NodeType.CONSUMER.value,
            "customer": NodeType.CONSUMER.value,
            "reservoir": NodeType.RESERVOIR.value,
            "water_reservoir": NodeType.RESERVOIR.value,
            "valve": NodeType.VALVE.value,
            "intersection": NodeType.CROSSING.value,
            "crossing": NodeType.CROSSING.value,
        }
        
        for key, node_type in type_mapping.items():
            if key in asset_type:
                return node_type
        
        return NodeType.ASSET.value
    
    def _infer_layer(self, asset_data: Dict) -> str:
        """
        Infer infrastructure layer from asset data.
        
        Args:
            asset_data: Asset properties
            
        Returns:
            Layer string
        """
        # Check explicit layer
        if "layer" in asset_data:
            return asset_data["layer"]
        
        # Infer from asset_type or domain
        asset_type = asset_data.get("asset_type", "").lower()
        domain = asset_data.get("domain", "").lower()
        
        # Electrical keywords
        electrical_keywords = ["power", "electric", "transformer", "grid", "line", "cable"]
        if any(k in asset_type for k in electrical_keywords) or "electrical" in domain:
            return Layer.ELECTRICAL.value
        
        # Water keywords
        water_keywords = ["water", "pump", "pipe", "reservoir", "valve", "sewer"]
        if any(k in asset_type for k in water_keywords) or "water" in domain:
            return Layer.WATER.value
        
        # Transport keywords
        transport_keywords = ["road", "rail", "track", "station", "junction", "intersection"]
        if any(k in asset_type for k in transport_keywords) or "transport" in domain:
            return Layer.TRANSPORT.value
        
        return Layer.GENERIC.value
    
    def build_from_relationships(
        self,
        assets: List[Dict],
        relationships: List[Dict]
    ) -> TopologyGraph:
        """
        Build topology from separate asset and relationship lists.
        
        Args:
            assets: List of asset dictionaries
            relationships: List of relationship dictionaries
            
        Returns:
            TopologyGraph with nodes and edges
        """
        # Index assets by ID
        asset_dict = {a["id"]: a for a in assets}
        
        # Add empty connections list
        for asset_id in asset_dict:
            if "connections" not in asset_dict[asset_id]:
                asset_dict[asset_id]["connections"] = []
        
        # Add relationships as connections
        for rel in relationships:
            source = rel.get("source_asset_id") or rel.get("from")
            target = rel.get("target_asset_id") or rel.get("to")
            
            if source and target and source in asset_dict:
                connection = {
                    "target": target,
                    "direction": rel.get("direction", "unidirectional"),
                    "capacity": rel.get("capacity", 1.0),
                    "flow_type": rel.get("flow_type", "generic"),
                    "resistance": rel.get("resistance", 0.1),
                }
                asset_dict[source].setdefault("connections", []).append(connection)
        
        return self.build(asset_dict)
    
    def merge_graphs(self, graphs: List[TopologyGraph]) -> TopologyGraph:
        """
        Merge multiple topology graphs.
        
        Args:
            graphs: List of TopologyGraph instances
            
        Returns:
            Merged TopologyGraph
        """
        merged = TopologyGraph()
        
        for graph in graphs:
            # Merge nodes
            for node_id, node in graph.nodes.items():
                if node_id not in merged.nodes:
                    merged.add_node(node)
            
            # Merge edges
            existing_edges = set()
            for edge in merged.edges:
                existing_edges.add((edge.from_node, edge.to_node))
            
            for edge in graph.edges:
                edge_key = (edge.from_node, edge.to_node)
                if edge_key not in existing_edges:
                    merged.add_edge(edge)
        
        return merged
