"""
Knowledge Schemas

Pydantic schemas for knowledge repository API.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# Document Schemas
class KnowledgeDocumentBase(BaseModel):
    """Base knowledge document schema."""
    title: str
    document_type: str
    category: str
    source: Optional[str] = None
    author: str
    summary: Optional[str] = None
    tags: List[str] = []
    external_url: Optional[str] = None


class KnowledgeDocumentCreate(KnowledgeDocumentBase):
    """Schema for creating a knowledge document."""
    pass


class KnowledgeDocumentUpdate(BaseModel):
    """Schema for updating a knowledge document."""
    title: Optional[str] = None
    document_type: Optional[str] = None
    category: Optional[str] = None
    source: Optional[str] = None
    author: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    external_url: Optional[str] = None


class KnowledgeDocumentResponse(KnowledgeDocumentBase):
    """Schema for knowledge document response."""
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class KnowledgeDocumentWithRefs(KnowledgeDocumentResponse):
    """Document with reference counts."""
    incoming_refs: int = 0
    outgoing_refs: int = 0


# Reference Schemas
class KnowledgeReferenceBase(BaseModel):
    """Base knowledge reference schema."""
    source_document_id: str
    target_document_id: str
    relationship_type: str


class KnowledgeReferenceCreate(KnowledgeReferenceBase):
    """Schema for creating a knowledge reference."""
    pass


class KnowledgeReferenceResponse(KnowledgeReferenceBase):
    """Schema for knowledge reference response."""
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Search Schemas
class KnowledgeSearchQuery(BaseModel):
    """Schema for knowledge search."""
    query: Optional[str] = None
    category: Optional[str] = None
    document_type: Optional[str] = None
    tags: Optional[List[str]] = None
    author: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


class KnowledgeSearchResponse(BaseModel):
    """Schema for knowledge search response."""
    total: int
    documents: List[KnowledgeDocumentResponse]


# Category Schemas
class CategorySummary(BaseModel):
    """Summary for a category."""
    category: str
    document_count: int


class CategoryResponse(BaseModel):
    """Schema for category list response."""
    categories: List[CategorySummary]
    total_documents: int


# Graph Schemas
class GraphNode(BaseModel):
    """Node in knowledge graph."""
    id: str
    title: str
    document_type: str
    category: str
    tags: List[str] = []


class GraphEdge(BaseModel):
    """Edge in knowledge graph."""
    source: str
    target: str
    relationship_type: str


class KnowledgeGraphResponse(BaseModel):
    """Schema for knowledge graph response."""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    total_nodes: int
    total_edges: int


# Related Documents Schemas
class RelatedDocument(BaseModel):
    """Related document info."""
    id: str
    title: str
    document_type: str
    category: str
    relationship_type: str


class RelatedDocumentsResponse(BaseModel):
    """Schema for related documents response."""
    document_id: str
    document_title: str
    related_documents: List[RelatedDocument]


# List Schemas
class DocumentListResponse(BaseModel):
    """Schema for document list response."""
    total: int
    documents: List[KnowledgeDocumentResponse]
    limit: int
    offset: int
