"""
RAG Routes

FastAPI routes for RAG Engine API.
These are audit records only - NO operational writes.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException

from ..schemas.rag import (
    RAGQueryRequest,
    RAGQueryResponse,
    RAGHistoryResponse,
    RAGHistoryItem,
    RAGSourcesResponse,
    RAGSource,
    RAGModelsResponse,
    RAGModelInfo
)
from ..services.rag_service import rag_service


router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/query", response_model=RAGQueryResponse)
async def query_rag(request: RAGQueryRequest):
    """
    Query the RAG engine.
    
    Retrieves context from all engines and generates answer.
    This is READ ONLY - no operational modifications.
    
    Returns:
    - Query ID
    - Generated answer
    - Sources used
    - Confidence score
    """
    # Set provider if specified
    if request.model != "template":
        rag_service.set_provider(request.model)
    
    # Retrieve context from all engines
    context_chunks = rag_service.retrieve_context(
        entity_type=request.entity_type,
        entity_id=request.entity_id,
        query=request.query,
        include_semantic=True,
        include_health=True,
        include_events=True,
        include_timeline=True,
        include_logbook=True,
        include_knowledge=True
    )
    
    # Answer query
    answer_result = rag_service.answer_query(request, context_chunks)
    
    # Store for audit
    query_id = rag_service.store_query(request, context_chunks, answer_result)
    
    # Get chunks for response
    chunks = rag_service.get_chunks(query_id)
    
    # Build sources response
    sources = [
        RAGSource(
            source_type=c.source_type.value if hasattr(c.source_type, 'value') else c.source_type,
            source_id=c.source_id,
            content=c.content,
            relevance_score=c.relevance_score,
            chunk_id=c.id
        )
        for c in chunks
    ]
    
    # Count by type
    by_type = {}
    for s in sources:
        stype = s.source_type
        by_type[stype] = by_type.get(stype, 0) + 1
    
    return RAGQueryResponse(
        query_id=query_id,
        query=request.query,
        answer=answer_result["answer"],
        model_name=answer_result["model"],
        confidence=answer_result["confidence"],
        sources=sources,
        context_summary=by_type
    )


@router.get("/history/{session_id}", response_model=RAGHistoryResponse)
async def get_history(session_id: str):
    """
    Get RAG query history for a session.
    """
    history = rag_service.get_history(session_id)
    
    items = [
        RAGHistoryItem(
            query_id=h["query_id"],
            query=h["query"],
            answer_preview=h["answer_preview"],
            model_name=h["model_name"],
            created_at=h["created_at"],
            chunk_count=h["chunk_count"]
        )
        for h in history
    ]
    
    return RAGHistoryResponse(
        session_id=session_id,
        queries=items,
        total_queries=len(items)
    )


@router.get("/sources/{query_id}", response_model=RAGSourcesResponse)
async def get_sources(query_id: str):
    """
    Get sources used for a query.
    """
    query = rag_service.get_query(query_id)
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    
    chunks = rag_service.get_chunks(query_id)
    
    sources = [
        RAGSource(
            source_type=c.source_type.value if hasattr(c.source_type, 'value') else c.source_type,
            source_id=c.source_id,
            content=c.content,
            relevance_score=c.relevance_score,
            chunk_id=c.id
        )
        for c in chunks
    ]
    
    by_type = {}
    for s in sources:
        stype = s.source_type
        by_type[stype] = by_type.get(stype, 0) + 1
    
    return RAGSourcesResponse(
        query_id=query_id,
        sources=sources,
        total_chunks=len(sources),
        by_type=by_type
    )


@router.get("/context/{query_id}")
async def get_context(query_id: str):
    """
    Get full context for a query.
    """
    query = rag_service.get_query(query_id)
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    
    chunks = rag_service.get_chunks(query_id)
    answer = rag_service.get_answer(query_id)
    
    return {
        "query": query.to_dict(),
        "chunks": [c.to_dict() for c in chunks],
        "answer": answer.to_dict() if answer else None
    }


@router.get("/models", response_model=RAGModelsResponse)
async def get_models():
    """
    Get available and future LLM models.
    """
    models = rag_service.get_available_models()
    
    model_infos = [
        RAGModelInfo(
            name=m["name"],
            status=m["status"],
            description=m["description"],
            provider=m.get("provider")
        )
        for m in models
    ]
    
    return RAGModelsResponse(
        current="template",
        available_models=model_infos
    )


@router.get("/retrieve")
async def retrieve_context(
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    query: Optional[str] = None,
    include_semantic: bool = True,
    include_health: bool = True,
    include_events: bool = True,
    include_timeline: bool = True,
    include_logbook: bool = True,
    include_knowledge: bool = True
):
    """
    Retrieve context without answering.
    
    Useful for pre-fetching context.
    """
    chunks = rag_service.retrieve_context(
        entity_type=entity_type,
        entity_id=entity_id,
        query=query,
        include_semantic=include_semantic,
        include_health=include_health,
        include_events=include_events,
        include_timeline=include_timeline,
        include_logbook=include_logbook,
        include_knowledge=include_knowledge
    )
    
    by_source = {}
    for chunk in chunks:
        stype = chunk.get("source_type", "unknown")
        if stype not in by_source:
            by_source[stype] = []
        by_source[stype].append(chunk.get("source_id"))
    
    return {
        "chunks": chunks,
        "by_source": by_source,
        "total_chunks": len(chunks)
    }
