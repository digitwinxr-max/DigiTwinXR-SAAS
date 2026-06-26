"""
LangGraph API Routes

Graph, node, and checkpoint metadata management.
NO autonomous execution.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from .graphs import (
    GraphRegistry,
    NodeRegistry,
    EdgeRegistry,
    GraphDefinition,
    NodeMetadata,
    EdgeMetadata,
    GraphMetadata,
    NodeType,
    get_graph,
    list_graphs,
    get_node,
    list_nodes,
    get_edge_set,
    list_edge_sets,
)
from .checkpoints import (
    CheckpointRegistry,
    CheckpointMetadata,
    CheckpointStatus,
    get_checkpoint_registry,
)

router = APIRouter(prefix="/langgraph", tags=["langgraph"])


# Response Models

class GraphListResponse(BaseModel):
    graphs: List[GraphMetadata]


class NodeResponse(BaseModel):
    name: str
    description: str
    node_type: str
    input_schema: Optional[Dict[str, Any]]
    output_schema: Optional[Dict[str, Any]]
    requires_tools: bool
    requires_memory: bool
    is_critical: bool


class EdgeResponse(BaseModel):
    source: str
    target: str
    edge_type: str
    condition: Optional[str]
    description: Optional[str]


class GraphDetailResponse(BaseModel):
    metadata: GraphMetadata
    nodes: List[NodeResponse]
    edges: List[EdgeResponse]
    state_schema: str


class CheckpointResponse(BaseModel):
    checkpoint_id: str
    graph_name: str
    session_id: str
    step: int
    created_at: datetime
    status: str
    size_bytes: Optional[int]
    error: Optional[str]
    parent_id: Optional[str]
    tags: List[str]


class CheckpointCreateRequest(BaseModel):
    checkpoint_id: str
    graph_name: str
    session_id: str
    step: int
    state: Dict[str, Any]
    parent_id: Optional[str] = None
    tags: Optional[List[str]] = None


# Graph Routes

@router.get("/graphs", response_model=GraphListResponse)
async def get_graphs():
    """
    List all registered graphs.
    """
    graphs = list_graphs()
    return GraphListResponse(graphs=graphs)


@router.get("/graphs/{graph_name}", response_model=GraphDetailResponse)
async def get_graph_detail(graph_name: str):
    """
    Get detailed graph definition.
    """
    graph = get_graph(graph_name)
    if not graph:
        raise HTTPException(status_code=404, detail=f"Graph {graph_name} not found")
    
    nodes = [
        NodeResponse(
            name=n.name,
            description=n.description,
            node_type=n.node_type.value,
            input_schema=n.input_schema,
            output_schema=n.output_schema,
            requires_tools=n.requires_tools,
            requires_memory=n.requires_memory,
            is_critical=n.is_critical
        )
        for n in graph.metadata.nodes
    ]
    
    edges = [
        EdgeResponse(
            source=e.source,
            target=e.target,
            edge_type=e.edge_type.value,
            condition=e.condition,
            description=e.description
        )
        for e in graph.edges
    ]
    
    return GraphDetailResponse(
        metadata=graph.metadata,
        nodes=nodes,
        edges=edges,
        state_schema=graph.state_schema.__name__
    )


# Node Routes

@router.get("/nodes", response_model=List[NodeResponse])
async def get_nodes(
    node_type: Optional[str] = Query(None, description="Filter by node type")
):
    """
    List all available nodes.
    """
    ntype = NodeType(node_type) if node_type else None
    nodes = list_nodes(ntype)
    
    return [
        NodeResponse(
            name=n.name,
            description=n.description,
            node_type=n.node_type.value,
            input_schema=n.input_schema,
            output_schema=n.output_schema,
            requires_tools=n.requires_tools,
            requires_memory=n.requires_memory,
            is_critical=n.is_critical
        )
        for n in nodes
    ]


@router.get("/nodes/{node_name}", response_model=NodeResponse)
async def get_node_detail(node_name: str):
    """
    Get node metadata.
    """
    node = get_node(node_name)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node {node_name} not found")
    
    return NodeResponse(
        name=node.name,
        description=node.description,
        node_type=node.node_type.value,
        input_schema=node.input_schema,
        output_schema=node.output_schema,
        requires_tools=node.requires_tools,
        requires_memory=node.requires_memory,
        is_critical=node.is_critical
    )


@router.get("/nodes/types", response_model=List[str])
async def get_node_types():
    """
    Get all node types.
    """
    return [nt.value for nt in NodeType]


# Edge Routes

@router.get("/edges/sets", response_model=List[str])
async def get_edge_sets():
    """
    List predefined edge sets.
    """
    return list_edge_sets()


@router.get("/edges/sets/{set_name}", response_model=List[EdgeResponse])
async def get_edge_set_detail(set_name: str):
    """
    Get edge set details.
    """
    edges = get_edge_set(set_name)
    if not edges:
        raise HTTPException(status_code=404, detail=f"Edge set {set_name} not found")
    
    return [
        EdgeResponse(
            source=e.source,
            target=e.target,
            edge_type=e.edge_type.value,
            condition=e.condition,
            description=e.description
        )
        for e in edges
    ]


# Checkpoint Routes

@router.post("/checkpoints")
async def create_checkpoint(request: CheckpointCreateRequest):
    """
    Create a checkpoint.
    
    Note: This only creates metadata. Actual state persistence
    must be handled by the application.
    """
    registry = get_checkpoint_registry()
    
    checkpoint = registry.create_checkpoint(
        checkpoint_id=request.checkpoint_id,
        graph_name=request.graph_name,
        session_id=request.session_id,
        step=request.step,
        state=request.state,
        parent_id=request.parent_id,
        tags=request.tags
    )
    
    return CheckpointResponse(
        checkpoint_id=checkpoint.checkpoint_id,
        graph_name=checkpoint.graph_name,
        session_id=checkpoint.session_id,
        step=checkpoint.step,
        created_at=checkpoint.created_at,
        status=checkpoint.status.value,
        size_bytes=checkpoint.size_bytes,
        error=checkpoint.error,
        parent_id=checkpoint.parent_id,
        tags=checkpoint.tags
    )


@router.post("/checkpoints/{checkpoint_id}/saved")
async def mark_checkpoint_saved(
    checkpoint_id: str,
    size_bytes: Optional[int] = None
):
    """
    Mark a checkpoint as saved.
    """
    registry = get_checkpoint_registry()
    
    try:
        checkpoint = registry.mark_saved(checkpoint_id, size_bytes)
        return CheckpointResponse(
            checkpoint_id=checkpoint.checkpoint_id,
            graph_name=checkpoint.graph_name,
            session_id=checkpoint.session_id,
            step=checkpoint.step,
            created_at=checkpoint.created_at,
            status=checkpoint.status.value,
            size_bytes=checkpoint.size_bytes,
            error=checkpoint.error,
            parent_id=checkpoint.parent_id,
            tags=checkpoint.tags
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/checkpoints/{checkpoint_id}/restored")
async def mark_checkpoint_restored(checkpoint_id: str):
    """
    Mark a checkpoint as restored.
    """
    registry = get_checkpoint_registry()
    
    try:
        checkpoint = registry.mark_restored(checkpoint_id)
        return CheckpointResponse(
            checkpoint_id=checkpoint.checkpoint_id,
            graph_name=checkpoint.graph_name,
            session_id=checkpoint.session_id,
            step=checkpoint.step,
            created_at=checkpoint.created_at,
            status=checkpoint.status.value,
            size_bytes=checkpoint.size_bytes,
            error=checkpoint.error,
            parent_id=checkpoint.parent_id,
            tags=checkpoint.tags
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/checkpoints", response_model=List[CheckpointResponse])
async def list_checkpoints(
    session_id: Optional[str] = Query(None),
    graph_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    """
    List checkpoints with optional filters.
    """
    registry = get_checkpoint_registry()
    checkpoint_status = CheckpointStatus(status) if status else None
    
    checkpoints = registry.list_checkpoints(
        session_id=session_id,
        graph_name=graph_name,
        status=checkpoint_status
    )
    
    return [
        CheckpointResponse(
            checkpoint_id=c.checkpoint_id,
            graph_name=c.graph_name,
            session_id=c.session_id,
            step=c.step,
            created_at=c.created_at,
            status=c.status.value,
            size_bytes=c.size_bytes,
            error=c.error,
            parent_id=c.parent_id,
            tags=c.tags
        )
        for c in checkpoints
    ]


@router.get("/checkpoints/latest")
async def get_latest_checkpoint(
    session_id: str,
    graph_name: Optional[str] = None
):
    """
    Get the latest checkpoint for a session.
    """
    registry = get_checkpoint_registry()
    checkpoint = registry.get_latest(session_id, graph_name)
    
    if not checkpoint:
        raise HTTPException(status_code=404, detail="No checkpoint found")
    
    return CheckpointResponse(
        checkpoint_id=checkpoint.checkpoint_id,
        graph_name=checkpoint.graph_name,
        session_id=checkpoint.session_id,
        step=checkpoint.step,
        created_at=checkpoint.created_at,
        status=checkpoint.status.value,
        size_bytes=checkpoint.size_bytes,
        error=checkpoint.error,
        parent_id=checkpoint.parent_id,
        tags=checkpoint.tags
    )


@router.get("/checkpoints/{checkpoint_id}/lineage")
async def get_checkpoint_lineage(checkpoint_id: str):
    """
    Get the lineage of a checkpoint.
    """
    registry = get_checkpoint_registry()
    lineage = registry.get_lineage(checkpoint_id)
    
    return [
        CheckpointResponse(
            checkpoint_id=c.checkpoint_id,
            graph_name=c.graph_name,
            session_id=c.session_id,
            step=c.step,
            created_at=c.created_at,
            status=c.status.value,
            size_bytes=c.size_bytes,
            error=c.error,
            parent_id=c.parent_id,
            tags=c.tags
        )
        for c in lineage
    ]


@router.delete("/checkpoints/{checkpoint_id}")
async def delete_checkpoint(checkpoint_id: str):
    """
    Delete a checkpoint.
    """
    registry = get_checkpoint_registry()
    registry.delete_checkpoint(checkpoint_id)
    return {"message": f"Checkpoint {checkpoint_id} deleted"}
