"""
Cognitive Twin Schemas

Pydantic schemas for Cognitive Twin Engine.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


# Cognitive Session Schemas
class CognitiveSessionCreate(BaseModel):
    """Schema for creating a session."""
    name: str
    description: Optional[str] = None
    asset_id: Optional[str] = None
    user_id: Optional[str] = None


class CognitiveSessionResponse(BaseModel):
    """Schema for session response."""
    id: str
    name: str
    description: Optional[str] = None
    asset_id: Optional[str] = None
    user_id: Optional[str] = None
    context_summary: Optional[str] = None
    query_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CognitiveSessionsListResponse(BaseModel):
    """Schema for sessions list."""
    sessions: List[CognitiveSessionResponse]
    total: int


# Cognitive Query Schemas
class CognitiveQueryCreate(BaseModel):
    """Schema for creating a query."""
    question: str
    asset_id: Optional[str] = None


class CognitiveQueryResponse(BaseModel):
    """Schema for query response."""
    id: str
    session_id: str
    question: str
    answer: Optional[str] = None
    confidence: float
    explanation: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CognitiveQueryWithContextResponse(BaseModel):
    """Schema for query with context."""
    query: CognitiveQueryResponse
    context: List["ContextSourceResponse"]


# Context Source Schemas
class ContextSourceResponse(BaseModel):
    """Schema for context source."""
    id: str
    source_type: str
    reference_id: Optional[str] = None
    weight: float
    summary: str
    detail: Optional[str] = None
    relevance_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RankedSourceResponse(BaseModel):
    """Schema for ranked source."""
    source_type: str
    total_weight: float
    context_count: int
    rank: int


class MergedContextResponse(BaseModel):
    """Schema for merged context."""
    source_type: str
    combined_summary: str
    total_weight: float
    context_count: int


# Confidence Schemas
class ConfidenceResponse(BaseModel):
    """Schema for confidence analysis."""
    overall_confidence: float
    coverage_score: float
    weight_score: float
    diversity_score: float
    relevance_score: float
    context_count: int
    unique_sources: int


# Insight Schemas
class InsightResponse(BaseModel):
    """Schema for insight."""
    source_type: str
    insight: str
    confidence: float
    evidence: List[str] = []


class InsightsListResponse(BaseModel):
    """Schema for insights list."""
    insights: List[InsightResponse]
    total: int


# Explanation Schemas
class ExplanationResponse(BaseModel):
    """Schema for explanation."""
    topic: str
    explanation: str
    confidence: float
    sources: List[str] = []
    related_context: List[ContextSourceResponse] = []


class ExplanationsListResponse(BaseModel):
    """Schema for explanations list."""
    explanations: List[ExplanationResponse]
    total: int


# Graph Schemas
class GraphNode(BaseModel):
    """Schema for graph node."""
    id: str
    label: str
    type: str
    properties: Dict[str, Any] = {}


class GraphEdge(BaseModel):
    """Schema for graph edge."""
    source: str
    target: str
    label: str
    weight: float


class InsightGraphResponse(BaseModel):
    """Schema for insight graph."""
    nodes: List[GraphNode]
    edges: List[GraphEdge]


# History Schemas
class HistoryItem(BaseModel):
    """Schema for history item."""
    query_id: str
    question: str
    answer: Optional[str]
    confidence: float
    context_count: int
    created_at: datetime


class HistoryResponse(BaseModel):
    """Schema for history."""
    session_id: str
    items: List[HistoryItem]
    total: int


# Update forward references
CognitiveQueryWithContextResponse.model_rebuild()
