"""
Logbook Schemas

Pydantic schemas for digital logbook API.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# Logbook Entry Schemas
class LogbookEntryBase(BaseModel):
    """Base logbook entry schema."""
    title: str
    entry_type: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    severity: str = "info"
    content: str
    author: str
    timeline_snapshot_id: Optional[str] = None


class LogbookEntryCreate(LogbookEntryBase):
    """Schema for creating a logbook entry."""
    timestamp: Optional[datetime] = None


class LogbookEntryResponse(LogbookEntryBase):
    """Schema for logbook entry response."""
    id: str
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class LogbookEntryWithSummary(LogbookEntryResponse):
    """Schema for entry with generated summary."""
    summary: str


# List Schemas
class LogbookListResponse(BaseModel):
    """Schema for logbook list response."""
    total: int
    entries: List[LogbookEntryResponse]
    limit: int
    offset: int


# Search Schemas
class LogbookSearchQuery(BaseModel):
    """Schema for logbook search query."""
    query: Optional[str] = None
    entry_type: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    severity: Optional[str] = None
    author: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


# Summary Schemas
class SeveritySummary(BaseModel):
    """Summary by severity."""
    info: int = 0
    warning: int = 0
    critical: int = 0


class TypeSummary(BaseModel):
    """Summary by entry type."""
    observation: int = 0
    incident: int = 0
    maintenance: int = 0
    inspection: int = 0
    investigation: int = 0
    annotation: int = 0


class AuthorSummary(BaseModel):
    """Summary by author."""
    author: str
    count: int


class LogbookSummaryResponse(BaseModel):
    """Schema for logbook summary response."""
    total_entries: int
    by_severity: SeveritySummary
    by_type: TypeSummary
    by_author: List[AuthorSummary]
    latest_entry: Optional[LogbookEntryResponse] = None
    oldest_entry: Optional[LogbookEntryResponse] = None


# History Schemas
class EntityHistoryResponse(BaseModel):
    """Schema for entity history response."""
    entity_type: str
    entity_id: str
    total_entries: int
    entries: List[LogbookEntryResponse]


class IncidentHistoryResponse(BaseModel):
    """Schema for incident history response."""
    total_incidents: int
    by_severity: SeveritySummary
    incidents: List[LogbookEntryResponse]


# Filter Schemas
class LogbookFilters(BaseModel):
    """Schema for logbook filters."""
    entry_types: Optional[List[str]] = None
    severities: Optional[List[str]] = None
    authors: Optional[List[str]] = None
    entity_types: Optional[List[str]] = None
