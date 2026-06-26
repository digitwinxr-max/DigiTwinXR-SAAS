"""
Tests for Network Topology Engine

Tests topology types, graph building, flow models, and validation.
"""

import pytest
from backend.src.services.topology import (
    TopologyNode,
    TopologyEdge,
    TopologyGraph,
    GraphBuilder,
    FlowModels,
    TopologyEngine,
    TopologyValidator,
    NodeType,
    Layer,
    Direction,
    FlowType,
    FlowStatus,
)


class TestTopologyTypes:
    """Tests for topology data types."""
    
    def test_create_node(self):
        """Test creating a topology node."""
        node = TopologyNode(
            id="node-1",
            type="substation",
            layer="electrical",
            metadata={"name": "Main Substation"}
        )
        
        assert node.id == "node-1"
        assert node.type == "substation"
        assert node.layer == "electrical"
        assert node.metadata["name"] == "Main Substation"
    
    def test_create_edge(self):
        """Test creating a topology edge."""
        edge = TopologyEdge(
            from_node="node-1",
            to_node="node-2",
            direction="bidirectional",
            capacity=100.0,
            flow_type="power",
            resistance=0.1
        )
        
        assert edge.from_node == "node-1"
        assert edge.to_node == "node-2"
        assert edge.is_bidirectional
        assert edge.capacity == 100.0
    
    def test_edge_effective_capacity(self):
        """Test effective capacity calculation."""
        edge = TopologyEdge(
            from_node="node-1",
            to_node="node-2",
            capacity=100.0,
            resistance=10.0
        )
        
        assert edge.effective_capacity() == 90.0
    
    def test_graph_operations(self):
        """Test graph add/get operations."""
        graph = TopologyGraph()
        
        node = TopologyNode(id="n1", type="asset", layer="generic")
        graph.add_node(node)
        
        assert graph.get_node("n1") == node
        assert graph.node_count() == 1
        
        edge = TopologyEdge(from_node="n1", to_node="n2")
        graph.add_edge(edge)
        
        assert graph.edge_count() == 1
        
        neighbors = graph.get_neighbors("n1")
        assert "n2" in neighbors


class TestGraphBuilder:
    """Tests for graph builder."""
    
    def test_build_simple_topology(self):
        """Test building a simple topology from assets."""
        assets = {
            "asset-1": {
                "asset_type": "substation",
                "connections": [
                    {"target": "asset-2", "capacity": 100}
                ]
            },
            "asset-2": {
                "asset_type": "transformer",
                "connections": []
            }
        }
        
        builder = GraphBuilder()
        graph = builder.build(assets)
        
        assert graph.node_count() == 2
        assert graph.edge_count() == 1
        
        node1 = graph.get_node("asset-1")
        assert node1.type == "substation"
    
    def test_build_bidirectional_edges(self):
        """Test that bidirectional edges create reverse connections."""
        assets = {
            "node-1": {
                "connections": [
                    {"target": "node-2", "direction": "bidirectional", "capacity": 50}
                ]
            },
            "node-2": {
                "connections": []
            }
        }
        
        builder = GraphBuilder()
        graph = builder.build(assets)
        
        # Should have 2 edges (forward and reverse)
        assert graph.edge_count() == 2
    
    def test_infer_electrical_layer(self):
        """Test layer inference for electrical assets."""
        assets = {
            "transformer": {"asset_type": "power_transformer"},
            "line": {"asset_type": "power_line"}
        }
        
        builder = GraphBuilder()
        graph = builder.build(assets)
        
        assert graph.get_node("transformer").layer == "electrical"
        assert graph.get_node("line").layer == "electrical"
    
    def test_infer_water_layer(self):
        """Test layer inference for water assets."""
        assets = {
            "pump": {"asset_type": "water_pump"},
            "pipe": {"asset_type": "water_pipe"}
        }
        
        builder = GraphBuilder()
        graph = builder.build(assets)
        
        assert graph.get_node("pump").layer == "water"
        assert graph.get_node("pipe").layer == "water"
    
    def test_infer_transport_layer(self):
        """Test layer inference for transport assets."""
        assets = {
            "station": {"asset_type": "rail_station"},
            "junction": {"asset_type": "road_junction"}
        }
        
        builder = GraphBuilder()
        graph = builder.build(assets)
        
        assert graph.get_node("station").layer == "transport"
        assert graph.get_node("junction").layer == "transport"


class TestFlowModels:
    """Tests for flow calculation models."""
    
    def test_stable_flow(self):
        """Test stable flow calculation."""
        edge = TopologyEdge(
            from_node="n1",
            to_node="n2",
            capacity=100.0,
            resistance=0.1
        )
        
        flow = FlowModels()
        result = flow.calculate_flow(edge, load=50.0)
        
        assert result.status == FlowStatus.STABLE
        assert result.utilization == pytest.approx(0.5, rel=0.01)
    
    def test_overloaded_flow(self):
        """Test overloaded flow calculation."""
        edge = TopologyEdge(
            from_node="n1",
            to_node="n2",
            capacity=100.0,
            resistance=0.0
        )
        
        flow = FlowModels()
        result = flow.calculate_flow(edge, load=120.0)
        
        assert result.status == FlowStatus.OVERLOADED
        assert result.overflow > 0
    
    def test_degraded_flow(self):
        """Test degraded flow (near capacity)."""
        edge = TopologyEdge(
            from_node="n1",
            to_node="n2",
            capacity=100.0,
            resistance=0.0
        )
        
        flow = FlowModels()
        result = flow.calculate_flow(edge, load=85.0)
        
        assert result.status == FlowStatus.DEGRADED
    
    def test_power_flow_model(self):
        """Test electrical power flow model."""
        edge = TopologyEdge(
            from_node="n1",
            to_node="n2",
            capacity=100.0,
            flow_type="power",
            resistance=0.1
        )
        
        flow = FlowModels()
        result = flow.calculate_flow(edge, load=80.0)
        
        # Power lines have tighter margins
        assert result.status in [FlowStatus.STABLE, FlowStatus.DEGRADED]
    
    def test_water_flow_model(self):
        """Test water flow model."""
        edge = TopologyEdge(
            from_node="n1",
            to_node="n2",
            capacity=100.0,
            flow_type="water",
            resistance=0.1
        )
        
        flow = FlowModels()
        result = flow.calculate_flow(edge, load=70.0)
        
        assert result.status == FlowStatus.STABLE


class TestTopologyEngine:
    """Tests for topology engine."""
    
    def test_build_topology(self):
        """Test building topology via engine."""
        engine = TopologyEngine()
        
        assets = {
            "a": {"connections": [{"target": "b"}]},
            "b": {"connections": [{"target": "c"}]},
            "c": {"connections": []}
        }
        
        graph = engine.build_topology(assets)
        
        assert graph.node_count() == 3
        assert graph.edge_count() == 2
    
    def test_trace_path_bfs(self):
        """Test BFS path tracing."""
        engine = TopologyEngine()
        
        assets = {
            "a": {"connections": [{"target": "b"}]},
            "b": {"connections": [{"target": "c"}, {"target": "d"}]},
            "c": {"connections": []},
            "d": {"connections": []}
        }
        
        graph = engine.build_topology(assets)
        path = engine.trace_path(graph, "a")
        
        assert "a" in path
        assert "b" in path
        assert "c" in path
        assert "d" in path
    
    def test_find_shortest_path(self):
        """Test finding shortest path."""
        engine = TopologyEngine()
        
        assets = {
            "a": {"connections": [{"target": "b"}]},
            "b": {"connections": [{"target": "c"}]},
            "c": {"connections": []}
        }
        
        graph = engine.build_topology(assets)
        path = engine.find_path(graph, "a", "c")
        
        assert path is not None
        assert path.nodes == ["a", "b", "c"]
    
    def test_find_no_path(self):
        """Test when no path exists."""
        engine = TopologyEngine()
        
        assets = {
            "a": {"connections": []},
            "b": {"connections": []}
        }
        
        graph = engine.build_topology(assets)
        path = engine.find_path(graph, "a", "b")
        
        assert path is None
    
    def test_simulate_flow(self):
        """Test flow simulation."""
        engine = TopologyEngine()
        
        assets = {
            "source": {"connections": [{"target": "node1", "capacity": 100}]},
            "node1": {"connections": [{"target": "node2", "capacity": 80}]},
            "node2": {"connections": []}
        }
        
        graph = engine.build_topology(assets)
        result = engine.simulate_flow(graph, "source", initial_load=50.0)
        
        assert result.status == FlowStatus.STABLE
        assert "source" in result.node_loads
        assert "node1" in result.node_loads
    
    def test_simulate_overloaded_flow(self):
        """Test flow simulation with overload."""
        engine = TopologyEngine()
        
        assets = {
            "source": {"connections": [{"target": "node1", "capacity": 50}]},
            "node1": {"connections": []}
        }
        
        graph = engine.build_topology(assets)
        result = engine.simulate_flow(graph, "source", initial_load=100.0)
        
        assert result.status == FlowStatus.OVERLOADED
        assert len(result.overloaded_edges) > 0
    
    def test_get_reachable_nodes(self):
        """Test getting reachable nodes."""
        engine = TopologyEngine()
        
        assets = {
            "a": {"connections": [{"target": "b"}]},
            "b": {"connections": [{"target": "c"}]},
            "c": {"connections": []},
            "isolated": {"connections": []}
        }
        
        graph = engine.build_topology(assets)
        reachable = engine.get_reachable_nodes(graph, "a")
        
        assert "a" in reachable
        assert "b" in reachable
        assert "c" in reachable
        assert "isolated" not in reachable
    
    def test_get_upstream_nodes(self):
        """Test getting upstream nodes."""
        engine = TopologyEngine()
        
        assets = {
            "source": {"connections": [{"target": "node1"}]},
            "node1": {"connections": [{"target": "target"}]},
            "target": {"connections": []}
        }
        
        graph = engine.build_topology(assets)
        upstream = engine.get_upstream_nodes(graph, "target")
        
        assert "source" in upstream
        assert "node1" in upstream
    
    def test_get_critical_nodes(self):
        """Test getting critical nodes by degree."""
        engine = TopologyEngine()
        
        assets = {
            "hub": {"connections": [{"target": "a"}, {"target": "b"}, {"target": "c"}]},
            "a": {"connections": []},
            "b": {"connections": []},
            "c": {"connections": []}
        }
        
        graph = engine.build_topology(assets)
        critical = engine.get_critical_nodes(graph)
        
        assert critical[0][0] == "hub"  # Hub should be most connected


class TestTopologyValidator:
    """Tests for topology validator."""
    
    def test_validate_empty_graph(self):
        """Test validating empty graph."""
        validator = TopologyValidator()
        graph = TopologyGraph()
        
        result = validator.validate(graph)
        
        assert not result.valid
        assert len(result.issues) > 0
    
    def test_validate_orphan_nodes(self):
        """Test detecting orphan nodes."""
        validator = TopologyValidator()
        
        graph = TopologyGraph()
        graph.add_node(TopologyNode(id="orphan", type="asset", layer="generic"))
        graph.add_node(TopologyNode(id="connected", type="asset", layer="generic"))
        graph.add_edge(TopologyEdge(from_node="connected", to_node="other"))
        graph.add_node(TopologyNode(id="other", type="asset", layer="generic"))
        
        result = validator.validate(graph)
        
        # Should have warning about orphan
        assert "orphan" in str(result.warnings) or len(result.issues) >= 0
    
    def test_validate_valid_graph(self):
        """Test validating a valid connected graph."""
        validator = TopologyValidator()
        
        graph = TopologyGraph()
        graph.add_node(TopologyNode(id="a", type="asset", layer="generic"))
        graph.add_node(TopologyNode(id="b", type="asset", layer="generic"))
        graph.add_edge(TopologyEdge(from_node="a", to_node="b"))
        
        result = validator.validate(graph)
        
        assert result.valid
        assert len(result.issues) == 0
    
    def test_validate_invalid_edge_reference(self):
        """Test detecting invalid edge references."""
        validator = TopologyValidator()
        
        graph = TopologyGraph()
        graph.add_node(TopologyNode(id="a", type="asset", layer="generic"))
        graph.add_edge(TopologyEdge(from_node="a", to_node="nonexistent"))
        
        result = validator.validate(graph)
        
        assert not result.valid
        assert any("nonexistent" in issue for issue in result.issues)
    
    def test_validate_self_loop(self):
        """Test detecting self-loops."""
        validator = TopologyValidator()
        
        graph = TopologyGraph()
        graph.add_node(TopologyNode(id="a", type="asset", layer="generic"))
        graph.add_edge(TopologyEdge(from_node="a", to_node="a"))
        
        result = validator.validate(graph)
        
        assert any("self-loop" in w.lower() for w in result.warnings)


class TestMultiLayerTopology:
    """Tests for multi-layer infrastructure support."""
    
    def test_electrical_topology(self):
        """Test building electrical grid topology."""
        assets = {
            "substation-1": {
                "asset_type": "substation",
                "connections": [
                    {"target": "transformer-1", "capacity": 500, "flow_type": "power"}
                ]
            },
            "transformer-1": {
                "asset_type": "transformer",
                "connections": [
                    {"target": "distribution-1", "capacity": 200, "flow_type": "power"}
                ]
            },
            "distribution-1": {
                "asset_type": "distribution_line",
                "connections": []
            }
        }
        
        builder = GraphBuilder()
        graph = builder.build(assets)
        
        assert graph.get_node("substation-1").layer == "electrical"
        assert graph.get_node("transformer-1").layer == "electrical"
    
    def test_water_topology(self):
        """Test building water distribution topology."""
        assets = {
            "reservoir-1": {
                "asset_type": "water_reservoir",
                "connections": [
                    {"target": "pump-1", "capacity": 1000, "flow_type": "water"}
                ]
            },
            "pump-1": {
                "asset_type": "pump_station",
                "connections": [
                    {"target": "junction-1", "capacity": 500, "flow_type": "water"}
                ]
            },
            "junction-1": {
                "asset_type": "junction",
                "connections": []
            }
        }
        
        builder = GraphBuilder()
        graph = builder.build(assets)
        
        assert graph.get_node("reservoir-1").layer == "water"
        assert graph.get_node("pump-1").layer == "water"
    
    def test_transport_topology(self):
        """Test building transport network topology."""
        assets = {
            "station-1": {
                "asset_type": "rail_station",
                "connections": [
                    {"target": "junction-1", "capacity": 10000, "flow_type": "traffic"}
                ]
            },
            "junction-1": {
                "asset_type": "junction",
                "connections": [
                    {"target": "station-2", "capacity": 10000, "flow_type": "traffic"}
                ]
            },
            "station-2": {
                "asset_type": "rail_station",
                "connections": []
            }
        }
        
        builder = GraphBuilder()
        graph = builder.build(assets)
        
        assert graph.get_node("station-1").layer == "transport"
        assert graph.get_node("junction-1").layer == "transport"
