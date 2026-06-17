"""API routes for Failure Propagation."""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.failure_propagation_service import FailurePropagationService
from ..schemas.propagated_event import (
    PropagatedEventResponse,
    PropagatedEventListResponse,
    ImpactChainResponse,
    PROPAGATION_TYPE_INFO,
)

router = APIRouter(prefix="/propagation", tags=["propagation"])


def get_service(db: Session = Depends(get_db)) -> FailurePropagationService:
    """Dependency for getting the service."""
    return FailurePropagationService(db)


@router.get("/event/{event_id}", response_model=PropagatedEventListResponse)
def get_event_propagation(
    event_id: UUID,
    service: FailurePropagationService = Depends(get_service),
):
    """Get all propagation records for an event."""
    propagations = service.get_event_propagation(event_id)
    
    items = []
    for prop in propagations:
        from ..services.asset_service import AssetService
        asset_service = AssetService(db)
        
        source_asset = asset_service.get_asset(prop.source_asset_id)
        affected_asset = asset_service.get_asset(prop.affected_asset_id)
        
        from ..models.event import Event
        source_event = db.query(Event).filter(Event.id == prop.source_event_id).first()
        
        items.append(PropagatedEventResponse(
            id=prop.id,
            source_event_id=prop.source_event_id,
            source_asset_id=prop.source_asset_id,
            affected_asset_id=prop.affected_asset_id,
            propagation_type=prop.propagation_type,
            severity=prop.severity,
            depth=prop.depth,
            created_at=prop.created_at,
            source_asset_name=source_asset.name if source_asset else None,
            affected_asset_name=affected_asset.name if affected_asset else None,
            source_event_message=source_event.message if source_event else None,
        ))
    
    return PropagatedEventListResponse(
        items=items,
        total=len(items),
        page=1,
        page_size=len(items),
        pages=1,
    )


@router.get("/asset/{asset_id}")
def get_asset_impacts(
    asset_id: UUID,
    service: FailurePropagationService = Depends(get_service),
):
    """Get all propagation impacts on an asset."""
    impacts = service.get_asset_impacts(asset_id)
    return impacts


@router.get("/chain/{asset_id}")
def get_impact_chain(
    asset_id: UUID,
    event_id: Optional[UUID] = Query(None, description="Optional specific event ID"),
    max_depth: int = Query(10, ge=1, le=100, description="Maximum depth"),
    service: FailurePropagationService = Depends(get_service),
):
    """Get the impact chain starting from an asset.
    
    If event_id is provided, shows propagation from that specific event.
    Otherwise, shows all propagations starting from this asset.
    """
    if event_id:
        try:
            return service.build_impact_chain(event_id, max_depth)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    
    # Get all propagations from this asset
    from ..models.propagated_event import PropagatedEvent
    propagations = service.db.query(PropagatedEvent).filter(
        PropagatedEvent.source_asset_id == asset_id
    ).order_by(PropagatedEvent.created_at.desc()).all()
    
    if not propagations:
        raise HTTPException(
            status_code=404,
            detail="No propagations found from this asset"
        )
    
    # Build chains for each event
    chains = []
    seen_events = set()
    
    for prop in propagations:
        if prop.source_event_id not in seen_events:
            seen_events.add(prop.source_event_id)
            try:
                chain = service.build_impact_chain(prop.source_event_id, max_depth)
                chains.append(chain)
            except ValueError:
                continue
    
    return {
        "asset_id": asset_id,
        "chains": chains,
        "total_chains": len(chains),
    }


@router.get("/impacts", response_model=PropagatedEventListResponse)
def list_impacts(
    skip: int = Query(0, ge=0, description="Skip count"),
    limit: int = Query(100, ge=1, le=1000, description="Limit count"),
    min_depth: Optional[int] = Query(None, ge=1, description="Minimum depth"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    service: FailurePropagationService = Depends(get_service),
):
    """List all propagation impacts."""
    impacts, total = service.get_all_impacts(
        skip=skip,
        limit=limit,
        min_depth=min_depth,
        severity=severity,
    )
    
    items = []
    for impact in impacts:
        items.append(PropagatedEventResponse(
            id=impact['id'],
            source_event_id=impact['source_event_id'],
            source_asset_id=impact['source_asset_id'],
            affected_asset_id=impact['affected_asset_id'],
            propagation_type=impact['propagation_type'],
            severity=impact['severity'],
            depth=impact['depth'],
            created_at=impact['created_at'],
            source_asset_name=impact.get('source_asset_name'),
            affected_asset_name=impact.get('affected_asset_name'),
            source_event_message=impact.get('event_message'),
        ))
    
    pages = (total + limit - 1) // limit if limit > 0 else 0
    
    return PropagatedEventListResponse(
        items=items,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit,
        pages=pages,
    )


@router.get("/types")
def list_propagation_types():
    """List all available propagation types."""
    return [
        {
            "type": info.type.value,
            "description": info.description,
            "direction": info.direction,
        }
        for info in PROPAGATION_TYPE_INFO.values()
    ]


@router.post("/propagate/{event_id}")
def manual_propagate(
    event_id: UUID,
    max_depth: int = Query(3, ge=1, le=10, description="Maximum depth"),
    service: FailurePropagationService = Depends(get_service),
):
    """Manually trigger propagation for an event.
    
    This is useful for reprocessing events or testing.
    """
    try:
        count, assets = service.propagate_event(event_id, max_depth)
        return {
            "propagated_count": count,
            "affected_assets": assets,
            "message": f"Propagated to {count} assets",
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))