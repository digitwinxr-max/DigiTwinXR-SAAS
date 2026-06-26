"""
Semantic Routes

FastAPI routes for semantic layer API.
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query

from ..schemas.semantic import (
    SemanticEntityCreate,
    SemanticEntityUpdate,
    SemanticEntityResponse,
    SemanticEntityWithTags,
    SemanticTagCreate,
    SemanticTagResponse,
    SemanticRelationshipCreate,
    SemanticRelationshipResponse,
    SemanticSearchQuery,
    SemanticSearchResponse,
    SemanticSearchResult,
    SemanticContextResponse,
    SemanticGraphResponse,
    TagSummaryResponse,
    TagSummary,
)
from ..services.semantic_service import semantic_service


router = APIRouter(prefix="/semantic", tags=["semantic"])


# Entity Routes
@router.post("/entities", response_model=SemanticEntityResponse)
async def create_entity(data: SemanticEntityCreate):
    """Create a new semantic entity."""
    entity = semantic_service.create_entity(data)
    return entity.to_dict()


@router.get("/entities", response_model=List[SemanticEntityResponse])
async def list_entities(
    entity_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    ontology_class: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """List semantic entities with optional filters."""
    entities = semantic_service.list_entities(
        entity_type=entity_type,
        category=category,
        ontology_class=ontology_class,
        limit=limit,
        offset=offset
    )
    return [e.to_dict() for e in entities]


@router.get("/entity/{entity_id}", response_model=SemanticEntityWithTags)
async def get_entity(entity_id: str):
    """Get a semantic entity by ID."""
    entity = semantic_service.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    tags = semantic_service.get_tags(entity_id)
    tags_dict = [{"tag_name": t.tag_name, "tag_value": t.tag_value} for t in tags]
    
    return {
        **entity.to_dict(),
        "tags": tags_dict
    }


@router.put("/entity/{entity_id}", response_model=SemanticEntityResponse)
async def update_entity(entity_id: str, data: SemanticEntityUpdate):
    """Update a semantic entity."""
    entity = semantic_service.update_entity(entity_id, data)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity.to_dict()


@router.delete("/entity/{entity_id}")
async def delete_entity(entity_id: str):
    """Delete a semantic entity."""
    success = semantic_service.delete_entity(entity_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entity not found")
    return {"message": "Entity deleted successfully"}


# Tag Routes
@router.post("/tags", response_model=SemanticTagResponse)
async def create_tag(data: SemanticTagCreate):
    """Create a new semantic tag."""
    tag = semantic_service.create_tag(data)
    if not tag:
        raise HTTPException(status_code=404, detail="Entity not found")
    return tag.to_dict()


@router.get("/tags/{entity_id}", response_model=List[SemanticTagResponse])
async def get_tags(entity_id: str):
    """Get all tags for an entity."""
    tags = semantic_service.get_tags(entity_id)
    return [t.to_dict() for t in tags]


@router.delete("/tag/{tag_id}")
async def delete_tag(tag_id: str):
    """Delete a semantic tag."""
    success = semantic_service.delete_tag(tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tag not found")
    return {"message": "Tag deleted successfully"}


# Relationship Routes
@router.post("/relationships", response_model=SemanticRelationshipResponse)
async def create_relationship(data: SemanticRelationshipCreate):
    """Create a new semantic relationship."""
    relationship = semantic_service.create_relationship(data)
    if not relationship:
        raise HTTPException(status_code=404, detail="Entity not found")
    return relationship.to_dict()


@router.get("/relationships/{entity_id}", response_model=List[SemanticRelationshipResponse])
async def get_relationships(entity_id: str):
    """Get all relationships for an entity."""
    relationships = semantic_service.get_relationships(entity_id)
    return [r.to_dict() for r in relationships]


@router.delete("/relationship/{relationship_id}")
async def delete_relationship(relationship_id: str):
    """Delete a semantic relationship."""
    success = semantic_service.delete_relationship(relationship_id)
    if not success:
        raise HTTPException(status_code=404, detail="Relationship not found")
    return {"message": "Relationship deleted successfully"}


# Search Routes
@router.get("/search", response_model=SemanticSearchResponse)
async def search_semantic(
    entity_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    ontology_class: Optional[str] = Query(None),
    tag_name: Optional[str] = Query(None),
    tag_value: Optional[str] = Query(None),
    query: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """
    Search semantic entities.
    
    NO AI, NO embeddings, NO vector search.
    Pure filter-based search only.
    """
    search_query = SemanticSearchQuery(
        entity_type=entity_type,
        category=category,
        ontology_class=ontology_class,
        tag_name=tag_name,
        tag_value=tag_value,
        query=query,
        limit=limit,
        offset=offset
    )
    
    entities = semantic_service.search(search_query)
    
    results = []
    for entity in entities:
        tags = semantic_service.get_tags(entity.id)
        tags_dict = [{"tag_name": t.tag_name, "tag_value": t.tag_value} for t in tags]
        
        results.append(SemanticSearchResult(
            entity={
                **entity.to_dict(),
                "tags": tags_dict
            },
            relevance_score=1.0
        ))
    
    return SemanticSearchResponse(
        total=len(results),
        limit=limit,
        offset=offset,
        results=results
    )


# Context Routes
@router.get("/context/{entity_type}/{entity_id}", response_model=SemanticContextResponse)
async def get_context(entity_type: str, entity_id: str):
    """
    Get semantic context for an entity.
    
    Returns aggregated information about related entities.
    NO AI, NO inference. Pure aggregation only.
    """
    context = semantic_service.build_context(entity_type, entity_id)
    if not context:
        raise HTTPException(status_code=404, detail="Entity not found")
    return context


# Graph Routes
@router.get("/graph", response_model=SemanticGraphResponse)
async def get_graph(limit: int = Query(500, ge=1, le=1000)):
    """
    Get semantic graph.
    
    Returns nodes and edges for graph visualization.
    NO AI, NO inference. Pure aggregation only.
    """
    graph = semantic_service.build_graph(limit=limit)
    return graph


# Tag Summary Routes
@router.get("/tags/summary", response_model=TagSummaryResponse)
async def get_tag_summary():
    """Get summary of all tags."""
    # Get all tags grouped by tag_name
    tag_summary: dict = {}
    
    for entity in semantic_service._entities.values():
        tags = semantic_service.get_tags(entity.id)
        for tag in tags:
            if tag.tag_name not in tag_summary:
                tag_summary[tag.tag_name] = {"entities": set(), "count": 0}
            tag_summary[tag.tag_name]["entities"].add(entity.id)
            tag_summary[tag.tag_name]["count"] += 1
    
    tags = [
        TagSummary(
            tag_name=name,
            entity_count=len(data["entities"]),
            total_tags=data["count"]
        )
        for name, data in tag_summary.items()
    ]
    
    tags.sort(key=lambda t: t.entity_count, reverse=True)
    
    return TagSummaryResponse(tags=tags, total=len(tags))
