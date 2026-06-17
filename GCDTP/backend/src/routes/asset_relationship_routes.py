"""API routes for Asset Relationships."""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.asset_relationship_service import AssetRelationshipService
from ..schemas.asset_relationship import (
    AssetRelationshipCreate,
    AssetRelationshipResponse,
    AssetRelationshipListResponse,
    AssetRelationshipGraphResponse,
    AssetRelationshipCreateResponse,
    AssetRelationshipDeleteResponse,
    RELATIONSHIP_TYPE_INFO,
    RelationshipType,
)

router = APIRouter(prefix="/relationships", tags=["relationships"])


def get_service(db: Session = Depends(get_db)) -> AssetRelationshipService:
    """Dependency for getting the service."""
    return AssetRelationshipService(db)


@router.post("", response_model=AssetRelationshipCreateResponse, status_code=201)
def create_relationship(
    relationship_data: AssetRelationshipCreate,
    service: AssetRelationshipService = Depends(get_service),
):
    """Create a new asset relationship.
    
    Creates a directed relationship between two assets.
    Cannot create self-referencing relationships.
    Cannot create duplicate relationships.
    """
    # Check for self-reference
    if relationship_data.parent_asset_id == relationship_data.child_asset_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot create self-referencing relationship"
        )
    
    try:
        relationship = service.create_relationship(relationship_data)
        
        # Get asset names for response
        from ..services.asset_service import AssetService
        asset_service = AssetService(db)
        
        parent = asset_service.get_asset(relationship.parent_asset_id)
        child = asset_service.get_asset(relationship.child_asset_id)
        
        response = AssetRelationshipResponse(
            id=relationship.id,
            parent_asset_id=relationship.parent_asset_id,
            child_asset_id=relationship.child_asset_id,
            relationship_type=relationship.relationship_type,
            created_at=relationship.created_at,
            parent_asset_name=parent.name if parent else None,
            child_asset_name=child.name if child else None,
        )
        
        return AssetRelationshipCreateResponse(relationship=response)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=AssetRelationshipListResponse)
def list_relationships(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    parent_asset_id: Optional[UUID] = Query(None, description="Filter by parent asset"),
    child_asset_id: Optional[UUID] = Query(None, description="Filter by child asset"),
    relationship_type: Optional[str] = Query(None, description="Filter by type"),
    service: AssetRelationshipService = Depends(get_service),
):
    """List all asset relationships with optional filters."""
    relationships, total = service.get_relationships(
        skip=skip,
        limit=limit,
        parent_asset_id=parent_asset_id,
        child_asset_id=child_asset_id,
        relationship_type=relationship_type,
    )
    
    # Get asset names
    from ..services.asset_service import AssetService
    asset_service = AssetService(db)
    
    items = []
    for rel in relationships:
        parent = asset_service.get_asset(rel.parent_asset_id)
        child = asset_service.get_asset(rel.child_asset_id)
        
        items.append(AssetRelationshipResponse(
            id=rel.id,
            parent_asset_id=rel.parent_asset_id,
            child_asset_id=rel.child_asset_id,
            relationship_type=rel.relationship_type,
            created_at=rel.created_at,
            parent_asset_name=parent.name if parent else None,
            child_asset_name=child.name if child else None,
        ))
    
    pages = (total + limit - 1) // limit if limit > 0 else 0
    
    return AssetRelationshipListResponse(
        items=items,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit,
        pages=pages,
    )


@router.delete("/{relationship_id}", response_model=AssetRelationshipDeleteResponse)
def delete_relationship(
    relationship_id: UUID,
    service: AssetRelationshipService = Depends(get_service),
):
    """Delete an asset relationship."""
    deleted = service.delete_relationship(relationship_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Relationship not found")
    
    return AssetRelationshipDeleteResponse(id=relationship_id)


@router.get("/types", response_model=list)
def list_relationship_types():
    """List all available relationship types with descriptions."""
    return [
        {
            "type": info.type.value,
            "description": info.description,
            "inverse_type": info.inverse_type.value if info.inverse_type else None,
        }
        for info in RELATIONSHIP_TYPE_INFO.values()
    ]


@router.get("/graph/{asset_id}", response_model=AssetRelationshipGraphResponse)
def get_asset_graph(
    asset_id: UUID,
    direction: str = Query("down", regex="^(up|down|both)$", description="Graph direction"),
    max_depth: int = Query(10, ge=1, le=100, description="Maximum graph depth"),
    service: AssetRelationshipService = Depends(get_service),
):
    """Get the relationship graph for an asset.
    
    Returns a hierarchical structure showing:
    - Children (assets this asset contains/monitors/etc.)
    - Parents (assets that contain/monitor/etc. this asset)
    - Health status at each node
    """
    try:
        return service.get_graph(
            asset_id=asset_id,
            direction=direction,
            max_depth=max_depth,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/children/{asset_id}")
def get_children(
    asset_id: UUID,
    relationship_type: Optional[str] = Query(None, description="Filter by type"),
    service: AssetRelationshipService = Depends(get_service),
):
    """Get all children (direct descendants) of an asset."""
    return service.get_children(asset_id, relationship_type)


@router.get("/parents/{asset_id}")
def get_parents(
    asset_id: UUID,
    relationship_type: Optional[str] = Query(None, description="Filter by type"),
    service: AssetRelationshipService = Depends(get_service),
):
    """Get all parents (direct ancestors) of an asset."""
    return service.get_parents(asset_id, relationship_type)


@router.get("/{relationship_id}", response_model=AssetRelationshipResponse)
def get_relationship(
    relationship_id: UUID,
    service: AssetRelationshipService = Depends(get_service),
):
    """Get a specific relationship by ID."""
    relationship = service.get_relationship(relationship_id)
    
    if not relationship:
        raise HTTPException(status_code=404, detail="Relationship not found")
    
    from ..services.asset_service import AssetService
    asset_service = AssetService(db)
    
    parent = asset_service.get_asset(relationship.parent_asset_id)
    child = asset_service.get_asset(relationship.child_asset_id)
    
    return AssetRelationshipResponse(
        id=relationship.id,
        parent_asset_id=relationship.parent_asset_id,
        child_asset_id=relationship.child_asset_id,
        relationship_type=relationship.relationship_type,
        created_at=relationship.created_at,
        parent_asset_name=parent.name if parent else None,
        child_asset_name=child.name if child else None,
    )