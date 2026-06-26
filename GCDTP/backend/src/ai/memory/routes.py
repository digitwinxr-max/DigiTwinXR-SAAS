"""
Context Memory API Routes

RAG, Cognitive Graph, and Context Assembly endpoints.
NO autonomous execution.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from .rag import (
    RAGEngine,
    RAGQuery,
    RAGResponse,
    RetrievalStrategy,
    Document,
    Chunk,
)
from .cognitive_graph import (
    CognitiveGraph,
    EntityType,
    RelationshipType,
    Entity,
    Relationship,
    GraphQuery,
)
from .context_assembly import (
    ContextAssemblyEngine,
    SourceType,
    ConflictResolution,
    ContextSource,
    AssemblyConfig,
)


router = APIRouter(prefix="/context", tags=["context"])


# RAG Routes

class DocumentCreate(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any] = {}


class ChunkCreate(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    chunk_index: int
    metadata: Dict[str, Any] = {}


class RAGQueryRequest(BaseModel):
    query: str
    strategy: str = "hybrid"
    top_k: int = 5
    min_score: float = 0.5
    filters: Optional[Dict[str, Any]] = None


class RetrievalResultResponse(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    score: float
    rank: int
    source: str


class RAGResponseModel(BaseModel):
    query: str
    results: List[RetrievalResultResponse]
    total_chunks: int
    retrieval_time_ms: float


# Cognitive Graph Routes

class EntityCreate(BaseModel):
    id: str
    type: str
    name: str
    properties: Dict[str, Any] = {}


class RelationshipCreate(BaseModel):
    id: str
    source_id: str
    target_id: str
    type: str
    weight: float = 1.0
    properties: Dict[str, Any] = {}


class GraphQueryRequest(BaseModel):
    start_id: str
    relation_types: List[str] = []
    max_depth: int = 3
    entity_types: List[str] = []
    direction: str = "both"


# Context Assembly Routes

class ContextSourceCreate(BaseModel):
    source_type: str
    source_id: str
    content: str
    metadata: Dict[str, Any] = {}


class AssemblyConfigRequest(BaseModel):
    sources: List[str]
    weights: Dict[str, float] = {}
    conflict_resolution: str = "latest"
    max_context_items: int = 20
    min_relevance_score: float = 0.3


# Initialize engines
rag_engine = RAGEngine()
cognitive_graph = CognitiveGraph()
context_engine = ContextAssemblyEngine()


# RAG Endpoints

@router.post("/rag/documents")
async def add_document(request: DocumentCreate):
    """Add a document to RAG index."""
    doc = Document(
        id=request.id,
        content=request.content,
        metadata=request.metadata
    )
    chunk_ids = rag_engine.add_document(doc)
    return {"document_id": request.id, "chunk_ids": chunk_ids}


@router.post("/rag/chunks")
async def add_chunk(request: ChunkCreate):
    """Add a chunk to RAG index."""
    rag_engine.add_chunk(
        chunk_id=request.chunk_id,
        document_id=request.document_id,
        content=request.content,
        chunk_index=request.chunk_index,
        metadata=request.metadata
    )
    return {"chunk_id": request.chunk_id}


@router.post("/rag/retrieve", response_model=RAGResponseModel)
async def retrieve(request: RAGQueryRequest):
    """Retrieve relevant chunks."""
    try:
        strategy = RetrievalStrategy(request.strategy)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid strategy")
    
    query = RAGQuery(
        query_text=request.query,
        strategy=strategy,
        top_k=request.top_k,
        min_score=request.min_score,
        filters=request.filters
    )
    
    response = rag_engine.retrieve(query)
    
    return RAGResponseModel(
        query=response.query,
        results=[
            RetrievalResultResponse(
                chunk_id=r.chunk.id,
                document_id=r.chunk.document_id,
                content=r.chunk.content,
                score=r.score,
                rank=r.rank,
                source=r.source
            )
            for r in response.results
        ],
        total_chunks=response.total_chunks,
        retrieval_time_ms=response.retrieval_time_ms
    )


@router.get("/rag/chunks/{chunk_id}")
async def get_chunk(chunk_id: str):
    """Get a chunk by ID."""
    chunk = rag_engine.get_chunk(chunk_id)
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return {
        "id": chunk.id,
        "document_id": chunk.document_id,
        "content": chunk.content,
        "metadata": chunk.metadata
    }


@router.delete("/rag/chunks/{chunk_id}")
async def delete_chunk(chunk_id: str):
    """Delete a chunk."""
    success = rag_engine.delete_chunk(chunk_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return {"message": "Chunk deleted"}


# Cognitive Graph Endpoints

@router.post("/graph/entities")
async def add_entity(request: EntityCreate):
    """Add an entity to the graph."""
    try:
        entity_type = EntityType(request.type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid entity type")
    
    entity = cognitive_graph.add_entity(
        entity_id=request.id,
        entity_type=entity_type,
        name=request.name,
        properties=request.properties
    )
    return {"id": entity.id, "type": entity.type.value, "name": entity.name}


@router.post("/graph/relationships")
async def add_relationship(request: RelationshipCreate):
    """Add a relationship to the graph."""
    try:
        rel_type = RelationshipType(request.type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid relationship type")
    
    relationship = cognitive_graph.add_relationship(
        relationship_id=request.id,
        source_id=request.source_id,
        target_id=request.target_id,
        relationship_type=rel_type,
        weight=request.weight,
        properties=request.properties
    )
    
    if not relationship:
        raise HTTPException(status_code=400, detail="Entities not found")
    
    return {"id": relationship.id, "type": relationship.type.value}


@router.get("/graph/entities/{entity_id}")
async def get_entity(entity_id: str):
    """Get an entity by ID."""
    entity = cognitive_graph.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return {
        "id": entity.id,
        "type": entity.type.value,
        "name": entity.name,
        "properties": entity.properties
    }


@router.get("/graph/entities/type/{entity_type}")
async def get_entities_by_type(entity_type: str):
    """Get entities by type."""
    try:
        etype = EntityType(entity_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid entity type")
    
    entities = cognitive_graph.get_entities_by_type(etype)
    return [
        {
            "id": e.id,
            "type": e.type.value,
            "name": e.name,
            "properties": e.properties
        }
        for e in entities
    ]


@router.post("/graph/traverse")
async def traverse_graph(request: GraphQueryRequest):
    """Traverse the graph."""
    try:
        rel_types = [RelationshipType(t) for t in request.relation_types]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid relationship type")
    
    try:
        ent_types = [EntityType(t) for t in request.entity_types]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid entity type")
    
    query = GraphQuery(
        start_id=request.start_id,
        relation_types=rel_types,
        max_depth=request.max_depth,
        entity_types=ent_types,
        direction=request.direction
    )
    
    result = cognitive_graph.traverse(query)
    
    return {
        "entities": [
            {"id": e.id, "type": e.type.value, "name": e.name}
            for e in result.entities
        ],
        "relationships": [
            {
                "id": r.id,
                "source_id": r.source_id,
                "target_id": r.target_id,
                "type": r.type.value
            }
            for r in result.relationships
        ],
        "paths": result.paths,
        "depth": result.depth
    }


@router.delete("/graph/entities/{entity_id}")
async def delete_entity(entity_id: str):
    """Delete an entity."""
    success = cognitive_graph.delete_entity(entity_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entity not found")
    return {"message": "Entity deleted"}


# Context Assembly Endpoints

@router.post("/assemble")
async def assemble_context(
    sources: List[ContextSourceCreate],
    config: Optional[AssemblyConfigRequest] = None
):
    """Assemble context from multiple sources."""
    context_sources = [
        ContextSource(
            source_type=SourceType(s.source_type),
            source_id=s.source_id,
            content=s.content,
            metadata=s.metadata
        )
        for s in sources
    ]
    
    if config:
        try:
            assembly_config = AssemblyConfig(
                sources=[SourceType(s) for s in config.sources],
                weights={SourceType(k): v for k, v in config.weights.items()},
                conflict_resolution=ConflictResolution(config.conflict_resolution),
                max_context_items=config.max_context_items,
                min_relevance_score=config.min_relevance_score
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid config")
    else:
        assembly_config = None
    
    result = context_engine.assemble(context_sources, assembly_config)
    
    return {
        "items": [
            {
                "key": item.key,
                "value": item.value,
                "confidence": item.confidence,
                "source_count": len(item.sources)
            }
            for item in result.items
        ],
        "assembled_at": result.assembled_at.isoformat(),
        "sources_used": [s.value for s in result.sources_used],
        "conflicts_resolved": result.conflicts_resolved,
        "conflicts_unresolved": len(result.conflicts_unresolved)
    }


@router.get("/graph/export")
async def export_graph():
    """Export the cognitive graph."""
    return cognitive_graph.to_dict()
