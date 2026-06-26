"""
RAG Schemas

Pydantic schemas for RAG Engine API.
These are audit records only - NO operational writes.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# Request Schemas
class RAGQueryRequest(BaseModel):
    """Schema for RAG query request."""
    query: str = Field(..., description="User query")
    session_id: Optional[str] = Field(None, description="Copilot session ID")
    entity_type: Optional[str] = Field(None, description="Entity type to focus on")
    entity_id: Optional[str] = Field(None, description="Entity ID to focus on")
    model: str = Field(default="template", description="LLM model to use")
    max_chunks: int = Field(default=10, ge=1, le=50, description="Max context chunks")


# Context Chunk Schemas
class RAGContextChunkResponse(BaseModel):
    """Schema for RAG context chunk response."""
    id: str
    source_type: str
    source_id: Optional[str] = None
    content: str
    relevance_score: float
    created_at: datetime

    class Config:
        from_attributes = True


# Answer Schemas
class RAGAnswerResponse(BaseModel):
    """Schema for RAG answer response."""
    id: str
    answer: str
    model_name: str
    confidence: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Source Schemas
class RAGSource(BaseModel):
    """Schema for a RAG source."""
    source_type: str
    source_id: Optional[str] = None
    content: str
    relevance_score: float
    chunk_id: str


class RAGSourcesResponse(BaseModel):
    """Schema for RAG sources response."""
    query_id: str
    sources: List[RAGSource]
    total_chunks: int
    by_type: Dict[str, int]


# Session Schemas
class RAGSessionResponse(BaseModel):
    """Schema for RAG session summary."""
    session_id: str
    query_count: int
    chunk_count: int
    answer_count: int
    last_query_at: Optional[datetime] = None


# Full Query Response
class RAGQueryResponse(BaseModel):
    """Schema for full RAG query response."""
    query_id: str
    query: str
    answer: str
    model_name: str
    confidence: Optional[float] = None
    sources: List[RAGSource]
    context_summary: Dict[str, int]


# History Schemas
class RAGHistoryItem(BaseModel):
    """Schema for RAG history item."""
    query_id: str
    query: str
    answer_preview: str
    model_name: str
    created_at: datetime
    chunk_count: int


class RAGHistoryResponse(BaseModel):
    """Schema for RAG history response."""
    session_id: str
    queries: List[RAGHistoryItem]
    total_queries: int


# Model Info Schemas
class RAGModelInfo(BaseModel):
    """Schema for LLM model information."""
    name: str
    status: str  # available, future, unavailable
    description: str
    provider: Optional[str] = None


class RAGModelsResponse(BaseModel):
    """Schema for available models response."""
    current: str
    available_models: List[RAGModelInfo]


# Context Retrieval Schemas
class ContextRetrievalRequest(BaseModel):
    """Schema for context retrieval request."""
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    query: Optional[str] = None
    include_semantic: bool = True
    include_health: bool = True
    include_events: bool = True
    include_timeline: bool = True
    include_logbook: bool = True
    include_knowledge: bool = True


class ContextRetrievalResponse(BaseModel):
    """Schema for context retrieval response."""
    chunks: List[RAGContextChunkResponse]
    by_source: Dict[str, List[str]]
    total_chunks: int
