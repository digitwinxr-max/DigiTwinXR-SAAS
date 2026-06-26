"""
Neo4j Graph Intelligence Module

Graph analytics layer for FastAPI.
PostgreSQL remains authoritative for business logic.
Neo4j provides graph projection and analytics only.

Components:
- Neo4j Client
- Graph Projection Manager
- Graph Sync Engine
- Graph Query Engine
- Centrality Engine
- Dependency Engine
- Path Analysis Engine
"""

from .graph_types import (
    ProjectionStatus,
    EntityType,
    CentralityType,
    PathType,
    ChainType,
    GraphNode,
    GraphRelationship,
    CentralityScore,
    PathAnalysis,
    DependencyChain,
    ProjectionJob,
    GraphSnapshot,
    QueryResult,
    SyncRecord,
    NeighborhoodResult,
    SubgraphResult,
)

from .neo4j_client import Neo4jClient, Neo4jClientError, CypherBuilder
from .graph_projection_manager import GraphProjectionManager
from .graph_sync_engine import GraphSyncEngine
from .graph_query_engine import GraphQueryEngine
from .centrality_engine import CentralityEngine, CentralityAnalyzer
from .dependency_engine import DependencyEngine
from .path_analysis_engine import PathAnalysisEngine, PathAnalyzer
from .graph_validator import GraphValidator


__all__ = [
    # Enums
    "ProjectionStatus",
    "EntityType",
    "CentralityType",
    "PathType",
    "ChainType",
    # Types
    "GraphNode",
    "GraphRelationship",
    "CentralityScore",
    "PathAnalysis",
    "DependencyChain",
    "ProjectionJob",
    "GraphSnapshot",
    "QueryResult",
    "SyncRecord",
    "NeighborhoodResult",
    "SubgraphResult",
    # Client
    "Neo4jClient",
    "Neo4jClientError",
    "CypherBuilder",
    # Managers
    "GraphProjectionManager",
    "GraphSyncEngine",
    "GraphQueryEngine",
    # Engines
    "CentralityEngine",
    "CentralityAnalyzer",
    "DependencyEngine",
    "PathAnalysisEngine",
    "PathAnalyzer",
    # Validators
    "GraphValidator",
]
