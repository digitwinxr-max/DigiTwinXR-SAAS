"""
Copilot Schemas

Pydantic schemas for Cognitive Copilot API.
This is read-only AI context - NO LLM integration yet.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# Session Schemas
class CopilotSessionCreate(BaseModel):
    """Schema for creating a copilot session."""
    session_name: str


class CopilotSessionResponse(BaseModel):
    """Schema for copilot session response."""
    id: str
    session_name: str
    created_at: datetime
    last_activity_at: datetime
    message_count: int = 0

    class Config:
        from_attributes = True


# Message Schemas
class CopilotMessageResponse(BaseModel):
    """Schema for copilot message response."""
    id: str
    session_id: str
    role: str
    message: str
    context_data: Optional[Dict[str, Any]] = None
    timestamp: datetime

    class Config:
        from_attributes = True


# Query Schemas
class CopilotQuery(BaseModel):
    """Schema for copilot query."""
    session_id: str
    query: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None


# Answer Schemas
class CopilotAnswer(BaseModel):
    """Schema for copilot answer."""
    answer: str
    context_used: List[str] = []
    sources: List[str] = []
    suggestions: List[str] = []


# Context Bundle Schemas
class ContextBundle(BaseModel):
    """Schema for context bundle."""
    entity_type: str
    entity_id: str
    asset: Optional[Dict[str, Any]] = None
    health: Optional[Dict[str, Any]] = None
    sensors: List[Dict[str, Any]] = []
    events: List[Dict[str, Any]] = []
    measurements: List[Dict[str, Any]] = []
    relationships: List[Dict[str, Any]] = []
    semantic: Optional[Dict[str, Any]] = None
    timeline: List[Dict[str, Any]] = []
    logbook: List[Dict[str, Any]] = []
    knowledge: List[Dict[str, Any]] = []
    summary: str = ""


# History Schemas
class SessionHistory(BaseModel):
    """Schema for session history."""
    session_id: str
    messages: List[CopilotMessageResponse]


# Summary Schemas
class AssetSummary(BaseModel):
    """Schema for asset summary."""
    asset_id: str
    name: str
    status: str
    health_score: Optional[float] = None
    active_events: int = 0
    sensor_count: int = 0
    description: str = ""


class HealthSummary(BaseModel):
    """Schema for health summary."""
    asset_id: str
    health_status: str
    health_score: float
    dependency_penalty: float = 0.0
    factors: List[str] = []


class EventSummary(BaseModel):
    """Schema for event summary."""
    event_id: str
    message: str
    severity: str
    timestamp: datetime
    asset_id: Optional[str] = None


class TimelineSummary(BaseModel):
    """Schema for timeline summary."""
    timestamp: datetime
    total_snapshots: int
    events: List[str] = []
    health_changes: List[str] = []


class LogbookSummary(BaseModel):
    """Schema for logbook summary."""
    entries: List[Dict[str, Any]] = []
    total_entries: int = 0


class KnowledgeSummary(BaseModel):
    """Schema for knowledge summary."""
    documents: List[Dict[str, Any]] = []
    related_count: int = 0


# Response Schemas
class ContextResponse(BaseModel):
    """Schema for context response."""
    entity_type: str
    entity_id: str
    bundle: ContextBundle


class QueryResponse(BaseModel):
    """Schema for query response."""
    query: str
    answer: CopilotAnswer
    context: ContextBundle
