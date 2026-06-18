"""
Semantic Schemas

Pydantic schemas for semantic layer API.
"""

from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field


# Entity Schemas
class SemanticEntityBase(BaseModel):
    """Base semantic entity schema."""
    entity_type: str
    entity_id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    ontology_class: Optional[str] = None


class SemanticEntityCreate(SemanticEntityBase):
    """Schema for creating a semantic entity."""
    pass


class SemanticEntityUpdate(BaseModel):
    """Schema for updating a semantic entity."""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    ontology_class: Optional[str] = None


class SemanticEntityResponse(SemanticEntityBase):
    """Schema for semantic entity response."""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SemanticEntityWithTags(SemanticEntityResponse):
    """Schema for entity with tags."""
    tags: List[dict] = []


# Tag Schemas
class SemanticTagBase(BaseModel):
    """Base semantic tag schema."""
    tag_name: str
    tag_value: str


class SemanticTagCreate(SemanticTagBase):
    """Schema for creating a semantic tag."""
    entity_id: str


class SemanticTagUpdate(BaseModel):
    """Schema for updating a semantic tag."""
    tag_value: Optional[str] = None


class SemanticTagResponse(SemanticTagBase):
    """Schema for semantic tag response."""
    id: str
    entity_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Relationship Schemas
class SemanticRelationshipBase(BaseModel):
    """Base semantic relationship schema."""
    relationship_type: str


class SemanticRelationshipCreate(SemanticRelationshipBase):
    """Schema for creating a semantic relationship."""
    source_entity_id: str
    target_entity_id: str


class SemanticRelationshipUpdate(BaseModel):
    """Schema for updating a semantic relationship."""
    relationship_type: Optional[str] = None


class SemanticRelationshipResponse(SemanticRelationshipBase):
    """Schema for semantic relationship response."""
    id: str
    source_entity_id: str
    target_entity_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Search Schemas
class SemanticSearchQuery(BaseModel):
    """Schema for semantic search query."""
    entity_type: Optional[str] = None
    category: Optional[str] = None
    ontology_class: Optional[str] = None
    tag_name: Optional[str] = None
    tag_value: Optional[str] = None
    query: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


class SemanticSearchResult(BaseModel):
    """Schema for a single search result."""
    entity: SemanticEntityWithTags
    relevance_score: float = 1.0


class SemanticSearchResponse(BaseModel):
    """Schema for semantic search response."""
    total: int
    limit: int
    offset: int
    results: List[SemanticSearchResult]


# Context Schemas
class SemanticContextAsset(BaseModel):
    """Asset in semantic context."""
    id: str
    name: str
    category: Optional[str] = None
    ontology_class: Optional[str] = None
    tags: List[dict] = []


class SemanticContextSensors(BaseModel):
    """Sensors in semantic context."""
    entities: List[SemanticEntityWithTags] = []
    count: int = 0


class SemanticContextEvents(BaseModel):
    """Events in semantic context."""
    entities: List[SemanticEntityWithTags] = []
    count: int = 0


class SemanticContextHealth(BaseModel):
    """Health records in semantic context."""
    entities: List[SemanticEntityWithTags] = []
    count: int = 0


class SemanticContextDocuments(BaseModel):
    """Documents in semantic context."""
    entities: List[SemanticEntityWithTags] = []
    count: int = 0


class SemanticContextTimeline(BaseModel):
    """Timeline entries in semantic context."""
    entities: List[SemanticEntityWithTags] = []
    count: int = 0


class SemanticContextWorkOrders(BaseModel):
    """Work orders in semantic context."""
    entities: List[SemanticEntityWithTags] = []
    count: int = 0


class SemanticContextResponse(BaseModel):
    """Schema for semantic context response."""
    entity: SemanticEntityWithTags
    asset: Optional[SemanticContextAsset] = None
    sensors: SemanticContextSensors = SemanticContextSensors()
    events: SemanticContextEvents = SemanticContextEvents()
    health: SemanticContextHealth = SemanticContextHealth()
    documents: SemanticContextDocuments = SemanticContextDocuments()
    timeline_entries: SemanticContextTimeline = SemanticContextTimeline()
    work_orders: SemanticContextWorkOrders = SemanticContextWorkOrders()
    relationships: List[SemanticRelationshipResponse] = []


# Graph Schemas
class GraphNode(BaseModel):
    """Node in semantic graph."""
    id: str
    name: str
    entity_type: str
    category: Optional[str] = None
    ontology_class: Optional[str] = None
    tags: List[dict] = []


class GraphEdge(BaseModel):
    """Edge in semantic graph."""
    source: str
    target: str
    relationship_type: str


class SemanticGraphResponse(BaseModel):
    """Schema for semantic graph response."""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    total_nodes: int
    total_edges: int


# Tag Summary Schema
class TagSummary(BaseModel):
    """Schema for tag summary."""
    tag_name: str
    entity_count: int
    total_tags: int


class TagSummaryResponse(BaseModel):
    """Schema for tag summary response."""
    tags: List[TagSummary]
    total: int
