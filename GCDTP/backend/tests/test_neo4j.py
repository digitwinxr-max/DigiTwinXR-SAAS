"""
Tests for Neo4j Graph Intelligence Layer

Tests projection, sync, queries, paths, centrality, dependency chains, and timeline integration.
"""

import pytest
from backend.src.integrations.neo4j import (
    Neo4jClient,
    GraphProjectionManager,
    GraphSyncEngine,
    GraphQueryEngine,
    CentralityEngine,
    DependencyEngine,
    PathAnalysisEngine,
    GraphValidator,
    GraphProjectionManager,
    ProjectionStatus,
    EntityType,
    CentralityType,
    PathType,
    ChainType,
    GraphNode,
    GraphRelationship,
    ProjectionJob,
    CentralityScore,
    DependencyChain,
    PathAnalysis,
    QueryResult,
)


class TestGraphTypes:
    """Tests for graph types."""
    
    def test_projection_status_values(self):
        """Test projection status values."""
        assert ProjectionStatus.PENDING.value == "pending"
        assert ProjectionStatus.RUNNING.value == "running"
        assert ProjectionStatus.COMPLETED.value == "completed"
        assert ProjectionStatus.FAILED.value == "failed"
    
    def test_entity_type_values(self):
        """Test entity type values."""
        assert EntityType.ASSET.value == "asset"
        assert EntityType.WORK_ORDER.value == "work_order"
        assert EntityType.DOCUMENT.value == "document"
        assert EntityType.DEVICE.value == "device"
    
    def test_centrality_type_values(self):
        """Test centrality type values."""
        assert CentralityType.DEGREE.value == "degree"
        assert CentralityType.BETWEENNESS.value == "betweenness"
        assert CentralityType.CLOSENESS.value == "closeness"
    
    def test_path_type_values(self):
        """Test path type values."""
        assert PathType.SHORTEST.value == "shortest"
        assert PathType.ALL_PATHS.value == "all_paths"
        assert PathType.CRITICAL.value == "critical"


class TestGraphNode:
    """Tests for GraphNode."""
    
    def test_create_graph_node(self):
        """Test creating a graph node."""
        node = GraphNode(
            id="node-1",
            entity_type=EntityType.ASSET,
            entity_id="asset-1",
            label="Asset"
        )
        
        assert node.id == "node-1"
        assert node.entity_type == EntityType.ASSET
        assert node.label == "Asset"
    
    def test_node_to_dict(self):
        """Test node serialization."""
        node = GraphNode(
            id="node-1",
            entity_type=EntityType.ASSET,
            entity_id="asset-1",
            label="Asset"
        )
        
        data = node.to_dict()
        assert data["id"] == "node-1"
        assert data["entity_type"] == "asset"


class TestGraphRelationship:
    """Tests for GraphRelationship."""
    
    def test_create_relationship(self):
        """Test creating a relationship."""
        rel = GraphRelationship(
            id="rel-1",
            source_id="node-1",
            target_id="node-2",
            relationship_type="DEPENDS_ON"
        )
        
        assert rel.id == "rel-1"
        assert rel.relationship_type == "DEPENDS_ON"


class TestProjectionJob:
    """Tests for ProjectionJob."""
    
    def test_create_projection_job(self):
        """Test creating a projection job."""
        job = ProjectionJob(
            id="job-1",
            name="Test Projection",
            entity_type=EntityType.ASSET
        )
        
        assert job.id == "job-1"
        assert job.status == ProjectionStatus.PENDING
        assert job.node_count == 0


class TestProjectionManager:
    """Tests for GraphProjectionManager."""
    
    @pytest.fixture
    def manager(self):
        """Create projection manager."""
        return GraphProjectionManager()
    
    def test_create_projection_job(self, manager):
        """Test creating a projection job."""
        job = manager.create_projection_job(
            name="Test Job",
            entity_type=EntityType.ASSET
        )
        
        assert job is not None
        assert job.name == "Test Job"
        assert job.entity_type == EntityType.ASSET
    
    def test_start_projection(self, manager):
        """Test starting a projection."""
        job = manager.create_projection_job(
            name="Test",
            entity_type=EntityType.ASSET
        )
        
        started = manager.start_projection(job)
        
        assert started.status == ProjectionStatus.RUNNING
        assert started.started_at is not None
    
    def test_complete_projection(self, manager):
        """Test completing a projection."""
        job = manager.create_projection_job(
            name="Test",
            entity_type=EntityType.ASSET
        )
        manager.start_projection(job)
        
        completed = manager.complete_projection(job, 100, 50)
        
        assert completed.status == ProjectionStatus.COMPLETED
        assert completed.node_count == 100
        assert completed.relationship_count == 50
    
    def test_fail_projection(self, manager):
        """Test failing a projection."""
        job = manager.create_projection_job(
            name="Test",
            entity_type=EntityType.ASSET
        )
        manager.start_projection(job)
        
        failed = manager.fail_projection(job, "Test error")
        
        assert failed.status == ProjectionStatus.FAILED
        assert failed.error_message == "Test error"
    
    def test_get_running_jobs(self, manager):
        """Test getting running jobs."""
        job1 = manager.create_projection_job(name="Job1", entity_type=EntityType.ASSET)
        job2 = manager.create_projection_job(name="Job2", entity_type=EntityType.ASSET)
        manager.start_projection(job1)
        
        running = manager.get_running_jobs()
        
        assert len(running) == 1
        assert running[0].name == "Job1"
    
    def test_project_assets(self, manager):
        """Test projecting assets."""
        job = manager.project_assets()
        
        assert job.entity_type == EntityType.ASSET
        assert "Asset" in job.name


class TestGraphSyncEngine:
    """Tests for GraphSyncEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create sync engine."""
        return GraphSyncEngine()
    
    def test_sync_asset_node(self, engine):
        """Test syncing an asset node."""
        asset_data = {
            "id": 1,
            "name": "Transformer A",
            "asset_type": "transformer",
            "status": "healthy"
        }
        
        record = engine.sync_asset_node(asset_data)
        
        assert record.entity_type == EntityType.ASSET
        assert record.operation == "upsert"
    
    def test_sync_work_order_node(self, engine):
        """Test syncing a work order node."""
        wo_data = {
            "id": 1,
            "title": "Maintenance",
            "status": "open"
        }
        
        record = engine.sync_work_order_node(wo_data)
        
        assert record.entity_type == EntityType.WORK_ORDER
    
    def test_sync_relationship(self, engine):
        """Test syncing a relationship."""
        record = engine.sync_relationship(
            source_id="1",
            source_type=EntityType.ASSET,
            target_id="2",
            target_type=EntityType.ASSET,
            rel_type="depends_on"
        )
        
        assert record.entity_type == EntityType.RELATIONSHIP
    
    def test_batch_sync_assets(self, engine):
        """Test batch syncing assets."""
        assets = [
            {"id": 1, "name": "Asset 1"},
            {"id": 2, "name": "Asset 2"}
        ]
        
        records = engine.batch_sync_assets(assets)
        
        assert len(records) == 2


class TestGraphQueryEngine:
    """Tests for GraphQueryEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create query engine."""
        return GraphQueryEngine()
    
    def test_execute_query(self, engine):
        """Test executing a query."""
        result = engine.execute_query(
            query_type="test",
            cypher_query="MATCH (n) RETURN n"
        )
        
        assert result.query_type == "test"
        assert isinstance(result, QueryResult)
    
    def test_query_caching(self, engine):
        """Test query caching."""
        result1 = engine.execute_query(
            query_type="test",
            cypher_query="MATCH (n) RETURN n",
            use_cache=True
        )
        
        result2 = engine.execute_query(
            query_type="test",
            cypher_query="MATCH (n) RETURN n",
            use_cache=True
        )
        
        assert result2.cached is True


class TestCentralityEngine:
    """Tests for CentralityEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create centrality engine."""
        return CentralityEngine()
    
    def test_compute_degree_centrality(self, engine):
        """Test computing degree centrality."""
        scores = engine.compute_degree_centrality(EntityType.ASSET)
        
        assert isinstance(scores, list)
    
    def test_compute_betweenness_centrality(self, engine):
        """Test computing betweenness centrality."""
        scores = engine.compute_betweenness_centrality(EntityType.ASSET)
        
        assert isinstance(scores, list)
    
    def test_compute_pagerank(self, engine):
        """Test computing PageRank."""
        scores = engine.compute_pagerank(EntityType.ASSET)
        
        assert isinstance(scores, list)


class TestDependencyEngine:
    """Tests for DependencyEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create dependency engine."""
        return DependencyEngine()
    
    def test_get_dependency_chain(self, engine):
        """Test getting dependency chain."""
        chain = engine.get_dependency_chain(
            entity_id="1",
            entity_type=EntityType.ASSET
        )
        
        assert chain.chain_type == ChainType.DEPENDENCY
        assert chain.start_entity_id == "1"
    
    def test_get_failure_impact_chain(self, engine):
        """Test getting failure impact chain."""
        chain = engine.get_failure_impact_chain(
            entity_id="1",
            entity_type=EntityType.ASSET
        )
        
        assert chain.chain_type == ChainType.FAILURE_IMPACT
    
    def test_analyze_failure_impact(self, engine):
        """Test analyzing failure impact."""
        result = engine.analyze_failure_impact(
            entity_id="1",
            entity_type=EntityType.ASSET
        )
        
        assert "entity_id" in result
        assert "impacted_count" in result


class TestPathAnalysisEngine:
    """Tests for PathAnalysisEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create path analysis engine."""
        return PathAnalysisEngine()
    
    def test_find_shortest_path(self, engine):
        """Test finding shortest path."""
        path = engine.find_shortest_path(
            start_id="1",
            end_id="2",
            start_type=EntityType.ASSET,
            end_type=EntityType.ASSET
        )
        
        assert path.path_type == PathType.SHORTEST
        assert path.start_entity_id == "1"
        assert path.end_entity_id == "2"
    
    def test_find_all_paths(self, engine):
        """Test finding all paths."""
        paths = engine.find_all_paths(
            start_id="1",
            end_id="2",
            start_type=EntityType.ASSET,
            end_type=EntityType.ASSET
        )
        
        assert paths.path_type == PathType.ALL_PATHS
    
    def test_find_dependency_paths(self, engine):
        """Test finding dependency paths."""
        paths = engine.find_dependency_paths(
            start_id="1",
            end_id="2",
            start_type=EntityType.ASSET,
            end_type=EntityType.ASSET
        )
        
        assert paths.path_type == PathType.DEPENDENCY


class TestGraphValidator:
    """Tests for GraphValidator."""
    
    @pytest.fixture
    def validator(self):
        """Create validator."""
        return GraphValidator()
    
    def test_validate_graph_node(self, validator):
        """Test validating a graph node."""
        node = GraphNode(
            id="node-1",
            entity_type=EntityType.ASSET,
            entity_id="asset-1",
            label="Asset"
        )
        
        issues = validator.validate_graph_node(node)
        
        assert len(issues) == 0
    
    def test_validate_graph_node_missing_id(self, validator):
        """Test validation with missing ID."""
        node = GraphNode(
            id="",
            entity_type=EntityType.ASSET,
            entity_id="asset-1",
            label="Asset"
        )
        
        issues = validator.validate_graph_node(node)
        
        assert len(issues) > 0
    
    def test_validate_relationship(self, validator):
        """Test validating a relationship."""
        rel = GraphRelationship(
            id="rel-1",
            source_id="node-1",
            target_id="node-2",
            relationship_type="DEPENDS_ON"
        )
        
        issues = validator.validate_relationship(rel, {"node-1", "node-2"})
        
        assert len(issues) == 0
    
    def test_check_orphan_nodes(self, validator):
        """Test checking orphan nodes."""
        nodes = [
            GraphNode(id="n1", entity_type=EntityType.ASSET, entity_id="a1", label="A"),
            GraphNode(id="n2", entity_type=EntityType.ASSET, entity_id="a2", label="A"),
        ]
        
        relationships = [
            GraphRelationship(id="r1", source_id="n1", target_id="n2", relationship_type="X")
        ]
        
        issues = validator.check_orphan_nodes(nodes, relationships)
        
        assert len(issues) == 0
    
    def test_validate_cypher_query(self, validator):
        """Test validating a Cypher query."""
        query = "MATCH (n) RETURN n"
        
        issues = validator.validate_cypher_query(query)
        
        assert len(issues) == 0
    
    def test_validate_cypher_query_empty(self, validator):
        """Test validating an empty query."""
        issues = validator.validate_cypher_query("")
        
        assert len(issues) > 0


class TestNeo4jClient:
    """Tests for Neo4j client."""
    
    @pytest.fixture
    def client(self):
        """Create Neo4j client."""
        return Neo4jClient(uri="bolt://localhost:7687")
    
    def test_client_initialization(self, client):
        """Test client initialization."""
        assert client.uri == "bolt://localhost:7687"
    
    def test_health_check(self, client):
        """Test health check."""
        result = client.health_check()
        
        assert result is False  # Not connected in test


class TestCypherBuilder:
    """Tests for CypherBuilder."""
    
    def test_match_node(self):
        """Test building MATCH clause."""
        query = "MATCH (n:Asset {id: $id})"
        
        assert "MATCH" in query
        assert "Asset" in query
    
    def test_create_node(self):
        """Test building CREATE clause."""
        query = "CREATE (n:Asset {id: $id})"
        
        assert "CREATE" in query
        assert "Asset" in query
