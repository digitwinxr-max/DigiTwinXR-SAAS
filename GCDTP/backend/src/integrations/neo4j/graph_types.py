"""
Graph Types

Core data types for Neo4j graph intelligence.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from enum import Enum


class ProjectionStatus(str, Enum):
    """Projection job status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EntityType(str, Enum):
    """Graph entity type."""
    ASSET = "asset"
    RELATIONSHIP = "relationship"
    WORK_ORDER = "work_order"
    DOCUMENT = "document"
    DEVICE = "device"
    USER = "user"
    ORGANIZATION = "organization"
    TIMELINE_EVENT = "timeline_event"


class CentralityType(str, Enum):
    """Centrality calculation type."""
    DEGREE = "degree"
    BETWEENNESS = "betweenness"
    CLOSENESS = "closeness"
    EIGENVECTOR = "eigenvector"
    PAGERANK = "pagerank"


class PathType(str, Enum):
    """Path analysis type."""
    SHORTEST = "shortest"
    ALL_PATHS = "all_paths"
    CRITICAL = "critical"
    DEPENDENCY = "dependency"
    REDUNDANCY = "redundancy"


class ChainType(str, Enum):
    """Dependency chain type."""
    FAILURE_IMPACT = "failure_impact"
    CASCADE = "cascade"
    DEPENDENCY = "dependency"


@dataclass
class GraphNode:
    """
    Graph node representation.
    """
    id: str
    entity_type: EntityType
    entity_id: str
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "entity_type": self.entity_type.value,
            "entity_id": self.entity_id,
            "label": self.label,
            "properties": self.properties,
        }


@dataclass
class GraphRelationship:
    """
    Graph relationship representation.
    """
    id: str
    source_id: str
    target_id: str
    relationship_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type,
            "properties": self.properties,
        }


@dataclass
class CentralityScore:
    """
    Centrality score for an entity.
    """
    id: str
    entity_type: EntityType
    entity_id: str
    centrality_type: CentralityType
    score: float
    rank: int = 0
    snapshot_id: Optional[str] = None
    computed_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "entity_type": self.entity_type.value,
            "entity_id": self.entity_id,
            "centrality_type": self.centrality_type.value,
            "score": self.score,
            "rank": self.rank,
        }


@dataclass
class PathAnalysis:
    """
    Path analysis result.
    """
    path_type: PathType
    start_entity_id: str
    end_entity_id: str
    path_length: int
    paths: List[List[GraphNode]] = field(default_factory=list)
    total_cost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "path_type": self.path_type.value,
            "start_entity_id": self.start_entity_id,
            "end_entity_id": self.end_entity_id,
            "path_length": self.path_length,
            "path_count": len(self.paths),
            "total_cost": self.total_cost,
        }


@dataclass
class DependencyChain:
    """
    Dependency chain representation.
    """
    id: str
    chain_type: ChainType
    start_entity_id: str
    end_entity_id: Optional[str] = None
    chain_data: List[Dict] = field(default_factory=list)
    chain_length: int = 0
    snapshot_id: Optional[str] = None
    computed_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "chain_type": self.chain_type.value,
            "start_entity_id": self.start_entity_id,
            "end_entity_id": self.end_entity_id,
            "chain_length": self.chain_length,
            "chain_data": self.chain_data,
        }


@dataclass
class ProjectionJob:
    """
    Graph projection job.
    """
    id: str
    name: str
    entity_type: EntityType
    status: ProjectionStatus = ProjectionStatus.PENDING
    filters: Dict[str, Any] = field(default_factory=dict)
    options: Dict[str, Any] = field(default_factory=dict)
    node_count: int = 0
    relationship_count: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: str = ""
    created_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "entity_type": self.entity_type.value,
            "status": self.status.value,
            "node_count": self.node_count,
            "relationship_count": self.relationship_count,
        }


@dataclass
class GraphSnapshot:
    """
    Graph snapshot.
    """
    id: str
    name: str
    entity_type: Optional[EntityType] = None
    filter_criteria: Dict[str, Any] = field(default_factory=dict)
    node_count: int = 0
    relationship_count: int = 0
    created_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "entity_type": self.entity_type.value if self.entity_type else None,
            "node_count": self.node_count,
            "relationship_count": self.relationship_count,
            "is_active": self.is_active,
        }


@dataclass
class QueryResult:
    """
    Graph query result.
    """
    query_type: str
    nodes: List[GraphNode] = field(default_factory=list)
    relationships: List[GraphRelationship] = field(default_factory=list)
    execution_time_ms: int = 0
    result_count: int = 0
    cached: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "query_type": self.query_type,
            "node_count": len(self.nodes),
            "relationship_count": len(self.relationships),
            "execution_time_ms": self.execution_time_ms,
            "result_count": self.result_count,
            "cached": self.cached,
        }


@dataclass
class SyncRecord:
    """
    Graph sync record.
    """
    id: str
    entity_type: EntityType
    entity_id: str
    operation: str
    status: ProjectionStatus
    node_id: Optional[str] = None
    relationship_id: Optional[str] = None
    error_message: str = ""
    synced_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "entity_type": self.entity_type.value,
            "entity_id": self.entity_id,
            "operation": self.operation,
            "status": self.status.value,
        }


@dataclass
class NeighborhoodResult:
    """Result of neighborhood query."""
    center_node: GraphNode
    neighbors: List[GraphNode] = field(default_factory=list)
    relationships: List[GraphRelationship] = field(default_factory=list)
    depth: int = 1
    
    def to_dict(self) -> Dict:
        return {
            "center_entity_id": self.center_node.entity_id,
            "neighbor_count": len(self.neighbors),
            "depth": self.depth,
        }


@dataclass
class SubgraphResult:
    """Result of subgraph extraction."""
    nodes: List[GraphNode] = field(default_factory=list)
    relationships: List[GraphRelationship] = field(default_factory=list)
    boundary_nodes: List[GraphNode] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "node_count": len(self.nodes),
            "relationship_count": len(self.relationships),
            "boundary_count": len(self.boundary_nodes),
        }
