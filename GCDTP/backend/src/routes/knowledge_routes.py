"""
Knowledge Routes

FastAPI routes for knowledge repository API.
This is metadata only - NO AI, NO embeddings.
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query

from ..schemas.knowledge import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentUpdate,
    KnowledgeDocumentResponse,
    KnowledgeReferenceCreate,
    KnowledgeReferenceResponse,
    KnowledgeSearchResponse,
    KnowledgeGraphResponse,
    CategoryResponse,
    CategorySummary,
    RelatedDocumentsResponse,
    DocumentListResponse
)
from ..services.knowledge_service import knowledge_service


router = APIRouter(prefix="/knowledge", tags=["knowledge"])


# Document Routes
@router.post("/documents", response_model=KnowledgeDocumentResponse)
async def create_document(data: KnowledgeDocumentCreate):
    """
    Create a new knowledge document.
    
    Documents are metadata only - NO AI, NO embeddings.
    """
    doc = knowledge_service.create_document(data)
    return doc.to_dict()


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    category: Optional[str] = Query(None, description="Filter by category"),
    document_type: Optional[str] = Query(None, description="Filter by type"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """
    List knowledge documents.
    
    Supports filtering by category and type.
    """
    docs = knowledge_service.list_documents(
        category=category,
        document_type=document_type,
        limit=limit,
        offset=offset
    )
    
    return DocumentListResponse(
        total=len(docs),
        documents=[d.to_dict() for d in docs],
        limit=limit,
        offset=offset
    )


@router.get("/document/{doc_id}", response_model=KnowledgeDocumentResponse)
async def get_document(doc_id: str):
    """
    Get a specific knowledge document.
    """
    doc = knowledge_service.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc.to_dict()


@router.delete("/document/{doc_id}")
async def delete_document(doc_id: str):
    """
    Delete a knowledge document.
    
    Also deletes all references to/from this document.
    """
    success = knowledge_service.delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "deleted", "id": doc_id}


# Reference Routes
@router.post("/references", response_model=KnowledgeReferenceResponse)
async def create_reference(data: KnowledgeReferenceCreate):
    """
    Create a relationship between documents.
    
    Defines knowledge graph structure.
    """
    ref = knowledge_service.create_reference(
        source_id=data.source_document_id,
        target_id=data.target_document_id,
        relationship_type=data.relationship_type
    )
    
    if not ref:
        raise HTTPException(status_code=400, detail="Invalid document IDs or same document")
    
    return ref.to_dict()


@router.get("/references/{doc_id}", response_model=List[KnowledgeReferenceResponse])
async def get_references(doc_id: str):
    """
    Get all references for a document.
    """
    refs = knowledge_service.get_references(doc_id)
    return [r.to_dict() for r in refs]


# Search Routes
@router.get("/search", response_model=KnowledgeSearchResponse)
async def search_documents(
    query: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    document_type: Optional[str] = Query(None, description="Filter by type"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    author: Optional[str] = Query(None, description="Filter by author"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """
    Search knowledge documents.
    
    Supports text search and multiple filters.
    """
    from ..schemas.knowledge import KnowledgeSearchQuery
    
    search_query = KnowledgeSearchQuery(
        query=query,
        category=category,
        document_type=document_type,
        tags=tags.split(",") if tags else None,
        author=author,
        limit=limit,
        offset=offset
    )
    
    docs = knowledge_service.search_documents(search_query)
    
    return KnowledgeSearchResponse(
        total=len(docs),
        documents=[d.to_dict() for d in docs]
    )


# Category Routes
@router.get("/categories", response_model=CategoryResponse)
async def get_categories():
    """
    Get category summary.
    
    Returns document counts by category.
    """
    summary = knowledge_service.get_category_summary()
    
    categories = [
        CategorySummary(
            category=s["category"],
            document_count=s["document_count"]
        )
        for s in summary
    ]
    
    total = sum(c.document_count for c in categories)
    
    return CategoryResponse(
        categories=categories,
        total_documents=total
    )


# Graph Routes
@router.get("/graph", response_model=KnowledgeGraphResponse)
async def get_knowledge_graph(
    limit: int = Query(100, ge=1, le=500, description="Max nodes to include")
):
    """
    Get knowledge graph.
    
    Returns nodes and edges for visualization.
    """
    graph = knowledge_service.build_knowledge_graph(limit)
    return graph


# Related Documents Routes
@router.get("/related/{doc_id}", response_model=RelatedDocumentsResponse)
async def get_related_documents(doc_id: str):
    """
    Get related documents.
    
    Returns documents connected through references.
    """
    doc = knowledge_service.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    related = knowledge_service.get_related_documents(doc_id)
    
    return RelatedDocumentsResponse(
        document_id=doc_id,
        document_title=doc.title,
        related_documents=related
    )
