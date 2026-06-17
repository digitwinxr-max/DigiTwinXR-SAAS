"""
Tests for Routing, Flow, and Resilience Engines

Tests path discovery, flow allocation, and resilience scoring.
"""

import pytest
from backend.src.services.topology import TopologyGraph, TopologyNode, TopologyEdge
from backend.src.services.routing import (
    RoutingEngine,
    FlowEngine,
    ResilienceEngine,
    CostModels,
    Route,
    FlowAllocation,
    RouteStatus,
)


class TestCostModels:
    """Tests for cost model calculations."""
    
    def test_base_cost(self):
        """Test base cost calculation."""
        edge = TopologyEdge(
            from_node="a",
            to_node="b",
            capacity=100.0,
            resistance=0.1
        )
        
        cost_model = CostModels()
        cost = cost_model.compute_cost(edge)
        
        assert cost > 0
    
    def test_resistance_increases_cost(self):
        """Test that resistance increases cost."""
        edge_low_res = TopologyEdge(
            from_node="a",
            to_node="b",
            capacity=100.0,
            resistance=0.1
        )
        
        edge_high_res = TopologyEdge(
            from_node="a",
            to_node="b",
            capacity=100.0,
            resistance=0.5
        )
        
        cost_model = CostModels()
        cost_low = cost_model.compute_cost(edge_low_res)
        cost_high = cost_model.compute_cost(edge_high_res)
        
        assert cost_high > cost_low
    
    def test_low_capacity_increases_cost(self):
        """Test that low capacity increases cost."""
        edge_high_cap = TopologyEdge(
            from_node="a",
            to_node="b",
            capacity=1000.0,
            resistance=0.1
        )
        
        edge_low_cap = TopologyEdge(
            from_node="a",
            to_node="b",
            capacity=10.0,
            resistance=0.1
        )
        
        cost_model = CostModels()
        cost_high = cost_model.compute_cost(edge_high_cap)
        cost_low = cost_model.compute_cost(edge_low_cap)
        
        assert cost_low > cost_high
    
    def test_domain_factors(self):
        """Test domain-specific cost factors."""
        edge = TopologyEdge(
            from_node="a",
            to_node="b",
            capacity=100.0,
            resistance=0.1
        )
        
        cost_model = CostModels()
        
        cost_electrical = cost_model.compute_cost(edge, domain="electrical")
        cost_transport = cost_model.compute_cost(edge, domain="transport")
        
        # Electrical should be more expensive
        assert cost_electrical > cost_transport
    
    def test_load_factor(self):
        """Test load-based cost increase."""
        edge = TopologyEdge(
            from_node="a",
            to_node="b",
            capacity=100.0,
            resistance=0.1
        )
        
        cost_model = CostModels()
        
        cost_no_load = cost_model.compute_cost(edge, current_load=0)
        cost_high_load = cost_model.compute_cost(edge, current_load=90)
        
        assert cost_high_load > cost_no_load


class TestRoutingEngine:
    """Tests for routing engine."""
    
    @pytest.fixture
    def simple_graph(self):
        """Create a simple test graph."""
        graph = TopologyGraph()
        
        # Create nodes
        for node_id in ["a", "b", "c", "d"]:
            graph.add_node(TopologyNode(id=node_id))
        
        # Create edges
        graph.add_edge(TopologyEdge(from_node="a", to_node="b", capacity=100))
        graph.add_edge(TopologyEdge(from_node="b", to_node="c", capacity=100))
        graph.add_edge(TopologyEdge(from_node="a", to_node="c", capacity=50))
        graph.add_edge(TopologyEdge(from_node="c", to_node="d", capacity=100))
        graph.add_edge(TopologyEdge(from_node="b", to_node="d", capacity=50))
        
        return graph
    
    def test_find_shortest_path(self, simple_graph):
        """Test finding shortest path."""
        engine = RoutingEngine()
        
        route = engine.find_shortest_path(simple_graph, "a", "d")
        
        assert route is not None
        assert "a" in route.path
        assert "d" in route.path
        assert route.is_valid
    
    def test_find_path_not_exists(self, simple_graph):
        """Test when path doesn't exist."""
        engine = RoutingEngine()
        
        # Add isolated node
        simple_graph.add_node(TopologyNode(id="isolated"))
        
        route = engine.find_shortest_path(simple_graph, "isolated", "a")
        
        assert route is None
    
    def test_path_cost(self, simple_graph):
        """Test that path cost is calculated."""
        engine = RoutingEngine()
        
        route = engine.find_shortest_path(simple_graph, "a", "d")
        
        assert route.total_cost > 0
    
    def test_path_capacity(self, simple_graph):
        """Test that path capacity is bottleneck."""
        engine = RoutingEngine()
        
        route = engine.find_shortest_path(simple_graph, "a", "d")
        
        # Should be limited by lowest capacity edge (50)
        assert route.total_capacity <= 50
    
    def test_find_all_paths(self, simple_graph):
        """Test finding multiple paths."""
        engine = RoutingEngine()
        
        routes = engine.find_all_paths(simple_graph, "a", "d", max_paths=5)
        
        assert len(routes) >= 1
    
    def test_route_with_max_hops(self, simple_graph):
        """Test path finding with hop limit."""
        engine = RoutingEngine()
        
        route = engine.find_shortest_path(simple_graph, "a", "d", max_hops=10)
        
        assert route is not None
        assert route.hop_count <= 10


class TestFlowEngine:
    """Tests for flow engine."""
    
    def test_allocate_flow(self):
        """Test flow allocation on a route."""
        route = Route(
            path=["a", "b", "c"],
            total_cost=5.0,
            total_capacity=100.0
        )
        
        engine = FlowEngine()
        dist = engine.allocate_flow(route, total_load=100.0)
        
        assert dist.total_load == 100.0
        assert len(dist.allocations) == 2  # 2 edges for 3 nodes
    
    def test_detect_overload(self):
        """Test overload detection."""
        allocations = [
            FlowAllocation(
                edge_id="a->b",
                from_node="a",
                to_node="b",
                load=100.0,
                utilization=1.5,
                capacity=100.0
            ),
            FlowAllocation(
                edge_id="b->c",
                from_node="b",
                to_node="c",
                load=50.0,
                utilization=0.5,
                capacity=100.0
            )
        ]
        
        engine = FlowEngine()
        overloaded = engine.detect_overload(allocations)
        
        assert len(overloaded) == 1
        assert overloaded[0].edge_id == "a->b"
    
    def test_detect_degraded(self):
        """Test degraded edge detection."""
        allocations = [
            FlowAllocation(
                edge_id="a->b",
                from_node="a",
                to_node="b",
                load=85.0,
                utilization=0.85,
                capacity=100.0
            )
        ]
        
        engine = FlowEngine()
        degraded = engine.detect_degraded(allocations)
        
        assert len(degraded) == 1
    
    def test_equal_distribution(self):
        """Test equal load distribution."""
        routes = [
            Route(path=["a", "b"], total_cost=1.0, total_capacity=100.0),
            Route(path=["a", "c"], total_cost=1.0, total_capacity=100.0)
        ]
        
        engine = FlowEngine()
        distributions = engine.allocate_multi_path_flow(routes, 100.0, "equal")
        
        assert len(distributions) == 2
        # Total load should be distributed
        total_allocated = sum(d.total_load for d in distributions)
        assert total_allocated == 100.0
    
    def test_capacity_distribution(self):
        """Test capacity-based distribution."""
        routes = [
            Route(path=["a", "b"], total_cost=1.0, total_capacity=100.0),
            Route(path=["a", "c"], total_cost=1.0, total_capacity=50.0)
        ]
        
        engine = FlowEngine()
        distributions = engine.allocate_multi_path_flow(routes, 150.0, "capacity")
        
        assert len(distributions) == 2
        # Higher capacity route should get more load
        loads = [d.total_load for d in distributions]
        assert loads[0] > loads[1]


class TestResilienceEngine:
    """Tests for resilience engine."""
    
    @pytest.fixture
    def test_graph(self):
        """Create a test graph."""
        graph = TopologyGraph()
        
        for node_id in ["a", "b", "c", "d"]:
            graph.add_node(TopologyNode(id=node_id))
        
        # Add edges
        graph.add_edge(TopologyEdge(from_node="a", to_node="b", capacity=100))
        graph.add_edge(TopologyEdge(from_node="b", to_node="c", capacity=100))
        graph.add_edge(TopologyEdge(from_node="a", to_node="c", capacity=50))
        graph.add_edge(TopologyEdge(from_node="c", to_node="d", capacity=100))
        
        return graph
    
    def test_compute_resilience_score(self, test_graph):
        """Test resilience score calculation."""
        route = Route(
            path=["a", "b", "c"],
            total_cost=5.0,
            total_capacity=100.0
        )
        
        engine = ResilienceEngine()
        metrics = engine.compute_resilience_score(test_graph, route)
        
        assert metrics.resilience_score >= 0
        assert metrics.resilience_score <= 1
        assert metrics.redundancy_paths >= 0
    
    def test_find_critical_nodes(self, test_graph):
        """Test critical node identification."""
        engine = ResilienceEngine()
        critical = engine.find_critical_nodes(test_graph)
        
        assert isinstance(critical, list)
    
    def test_find_critical_edges(self, test_graph):
        """Test critical edge identification."""
        engine = ResilienceEngine()
        critical = engine.find_critical_edges(test_graph)
        
        assert isinstance(critical, list)
    
    def test_evaluate_route_alternatives(self, test_graph):
        """Test evaluating alternative routes."""
        engine = ResilienceEngine()
        results = engine.evaluate_route_alternatives(
            test_graph,
            "a",
            "d",
            max_alternatives=3
        )
        
        assert isinstance(results, dict)


class TestRouteTypes:
    """Tests for routing type classes."""
    
    def test_route_properties(self):
        """Test Route class properties."""
        route = Route(
            path=["a", "b", "c", "d"],
            total_cost=10.0,
            total_capacity=50.0,
            total_resistance=0.5
        )
        
        assert route.hop_count == 3
        assert route.average_capacity == pytest.approx(16.67, rel=0.01)
        assert route.cost_per_hop == pytest.approx(3.33, rel=0.01)
    
    def test_route_to_dict(self):
        """Test Route serialization."""
        route = Route(
            path=["a", "b"],
            total_cost=5.0,
            total_capacity=100.0
        )
        
        data = route.to_dict()
        
        assert "path" in data
        assert "total_cost" in data
        assert data["hop_count"] == 1
    
    def test_flow_allocation_status(self):
        """Test FlowAllocation status calculation."""
        allocation = FlowAllocation(
            edge_id="a->b",
            from_node="a",
            to_node="b",
            load=110.0,
            utilization=1.1,
            capacity=100.0
        )
        
        assert allocation.status == RouteStatus.OVERLOADED
        assert allocation.overflow > 0


class TestIntegration:
    """Integration tests for routing module."""
    
    @pytest.fixture
    def network_graph(self):
        """Create a network graph for integration tests."""
        graph = TopologyGraph()
        
        # Create network: source -> a -> b -> c -> sink
        #                         \-> d -> sink
        
        nodes = ["source", "a", "b", "c", "d", "sink"]
        for node_id in nodes:
            graph.add_node(TopologyNode(id=node_id))
        
        # Main path
        graph.add_edge(TopologyEdge(
            from_node="source", to_node="a", capacity=200
        ))
        graph.add_edge(TopologyEdge(
            from_node="a", to_node="b", capacity=150
        ))
        graph.add_edge(TopologyEdge(
            from_node="b", to_node="c", capacity=100
        ))
        graph.add_edge(TopologyEdge(
            from_node="c", to_node="sink", capacity=100
        ))
        
        # Alternative path
        graph.add_edge(TopologyEdge(
            from_node="a", to_node="d", capacity=80
        ))
        graph.add_edge(TopologyEdge(
            from_node="d", to_node="sink", capacity=80
        ))
        
        return graph
    
    def test_full_routing_workflow(self, network_graph):
        """Test complete routing workflow."""
        # Step 1: Find route
        routing = RoutingEngine()
        route = routing.find_shortest_path(network_graph, "source", "sink")
        
        assert route is not None
        assert route.is_valid
        
        # Step 2: Allocate flow
        flow = FlowEngine()
        distribution = flow.allocate_flow(route, total_load=50.0)
        
        assert distribution.total_load == 50.0
        assert len(distribution.allocations) > 0
        
        # Step 3: Check resilience
        resilience = ResilienceEngine()
        metrics = resilience.compute_resilience_score(network_graph, route)
        
        assert metrics.resilience_score >= 0
    
    def test_multi_path_flow(self, network_graph):
        """Test multi-path flow distribution."""
        routing = RoutingEngine()
        flow = FlowEngine()
        
        # Find multiple routes
        routes = routing.find_all_paths(
            network_graph,
            "source",
            "sink",
            max_paths=3
        )
        
        assert len(routes) >= 1
        
        # Allocate across routes
        distributions = flow.allocate_multi_path_flow(
            routes,
            total_load=100.0,
            strategy="capacity"
        )
        
        assert len(distributions) > 0
    
    def test_network_resilience(self, network_graph):
        """Test network-wide resilience analysis."""
        resilience = ResilienceEngine()
        
        result = resilience.compute_network_resilience(network_graph)
        
        assert result.overall_score >= 0
        assert result.overall_score <= 1
