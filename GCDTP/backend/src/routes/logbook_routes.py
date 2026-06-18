"""
Logbook Routes

FastAPI routes for digital logbook API.
Entries are append-only - no edits or deletes.
"""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query

from ..schemas.logbook import (
    LogbookEntryCreate,
    LogbookEntryResponse,
    LogbookEntryWithSummary,
    LogbookListResponse,
    LogbookSearchQuery,
    LogbookSummaryResponse,
    EntityHistoryResponse,
    IncidentHistoryResponse,
)
from ..services.logbook_service import logbook_service


router = APIRouter(prefix="/logbook", tags=["logbook"])


# Entry Routes
@router.post("", response_model=LogbookEntryResponse)
async def create_entry(data: LogbookEntryCreate):
    """
    Create a new logbook entry.
    
    This is the ONLY write operation.
    Entries are immutable once created.
    NO edits, NO deletes.
    """
    entry = logbook_service.create_entry(data)
    return entry.to_dict()


@router.get("", response_model=LogbookListResponse)
async def list_entries(
    entry_type: Optional[str] = Query(None, description="Filter by entry type"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    author: Optional[str] = Query(None, description="Filter by author"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """
    List logbook entries with filters.
    
    Entries are returned in reverse chronological order.
    """
    entries = logbook_service.list_entries(
        entry_type=entry_type,
        severity=severity,
        author=author,
        limit=limit,
        offset=offset
    )
    
    return LogbookListResponse(
        total=len(entries),
        entries=[e.to_dict() for e in entries],
        limit=limit,
        offset=offset
    )


@router.get("/search", response_model=LogbookListResponse)
async def search_entries(
    query: Optional[str] = Query(None, description="Text search query"),
    entry_type: Optional[str] = Query(None, description="Filter by entry type"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[str] = Query(None, description="Filter by entity ID"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    author: Optional[str] = Query(None, description="Filter by author"),
    start_time: Optional[datetime] = Query(None, description="Start of time range"),
    end_time: Optional[datetime] = Query(None, description="End of time range"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """
    Search logbook entries.
    
    Supports text search and multiple filters.
    """
    search_query = LogbookSearchQuery(
        query=query,
        entry_type=entry_type,
        entity_type=entity_type,
        entity_id=entity_id,
        severity=severity,
        author=author,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset
    )
    
    entries = logbook_service.search_entries(search_query)
    
    return LogbookListResponse(
        total=len(entries),
        entries=[e.to_dict() for e in entries],
        limit=limit,
        offset=offset
    )


@router.get("/{entry_id}", response_model=LogbookEntryWithSummary)
async def get_entry(entry_id: str):
    """
    Get a specific logbook entry.
    
    Returns entry with generated summary.
    """
    entry = logbook_service.get_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    return {
        **entry.to_dict(),
        "summary": entry.summary()
    }


# Entity Routes
@router.get("/entity/{entity_type}/{entity_id}", response_model=EntityHistoryResponse)
async def get_entity_history(entity_type: str, entity_id: str):
    """
    Get all logbook entries for an entity.
    
    Returns chronological history of all entries.
    """
    entries = logbook_service.get_by_entity(entity_type, entity_id)
    
    return EntityHistoryResponse(
        entity_type=entity_type,
        entity_id=entity_id,
        total_entries=len(entries),
        entries=[e.to_dict() for e in entries]
    )


@router.get("/history/{entity_type}/{entity_id}", response_model=EntityHistoryResponse)
async def build_entity_history(entity_type: str, entity_id: str):
    """
    Build complete history for an entity.
    
    Includes direct entries and related entries through timeline.
    """
    entries = logbook_service.build_asset_history(entity_type, entity_id)
    
    return EntityHistoryResponse(
        entity_type=entity_type,
        entity_id=entity_id,
        total_entries=len(entries),
        entries=[e.to_dict() for e in entries]
    )


# Type Routes
@router.get("/type/{entry_type}", response_model=LogbookListResponse)
async def get_entries_by_type(
    entry_type: str,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """
    Get entries by type.
    
    Types: observation, incident, maintenance, inspection, investigation, annotation
    """
    entries = logbook_service.get_by_type(entry_type)
    
    return LogbookListResponse(
        total=len(entries),
        entries=[e.to_dict() for e in entries[offset:offset + limit]],
        limit=limit,
        offset=offset
    )


# Severity Routes
@router.get("/severity/{severity}", response_model=LogbookListResponse)
async def get_entries_by_severity(
    severity: str,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """
    Get entries by severity.
    
    Severities: info, warning, critical
    """
    entries = logbook_service.get_by_severity(severity)
    
    return LogbookListResponse(
        total=len(entries),
        entries=[e.to_dict() for e in entries[offset:offset + limit]],
        limit=limit,
        offset=offset
    )


# Incident Routes
@router.get("/incidents/history", response_model=IncidentHistoryResponse)
async def get_incident_history(
    start_time: Optional[datetime] = Query(None, description="Start of range"),
    end_time: Optional[datetime] = Query(None, description="End of range")
):
    """
    Get incident history.
    
    Returns all incident entries within time range.
    """
    incidents = logbook_service.build_incident_history(start_time, end_time)
    
    # Count by severity
    by_severity = {"info": 0, "warning": 0, "critical": 0}
    for entry in incidents:
        by_severity[entry.severity.value] = by_severity.get(entry.severity.value, 0) + 1
    
    return IncidentHistoryResponse(
        total_incidents=len(incidents),
        by_severity=by_severity,
        incidents=[e.to_dict() for e in incidents]
    )


# Timeline Integration
@router.get("/timeline/{timeline_snapshot_id}", response_model=LogbookListResponse)
async def get_entries_by_timeline(
    timeline_snapshot_id: str,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """
    Get logbook entries linked to a timeline snapshot.
    
    Allows viewing relevant entries when replaying timeline.
    """
    entries = logbook_service.get_by_timeline(timeline_snapshot_id)
    
    return LogbookListResponse(
        total=len(entries),
        entries=[e.to_dict() for e in entries[offset:offset + limit]],
        limit=limit,
        offset=offset
    )


# Summary Routes
@router.get("/summary", response_model=LogbookSummaryResponse)
async def get_summary():
    """
    Get logbook summary statistics.
    
    Returns counts by severity, type, and author.
    """
    summary = logbook_service.get_summary()
    return summary


# Author Routes
@router.get("/author/{author}", response_model=LogbookListResponse)
async def get_entries_by_author(
    author: str,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """
    Get entries by author.
    
    Returns all entries created by the specified author.
    """
    entries = logbook_service.list_entries(author=author, limit=limit, offset=offset)
    
    return LogbookListResponse(
        total=len(entries),
        entries=[e.to_dict() for e in entries],
        limit=limit,
        offset=offset
    )
