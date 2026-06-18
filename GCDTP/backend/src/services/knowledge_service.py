"""
Knowledge Repository Service

Provides structured knowledge organization.
This is pure metadata aggregation - NO AI, NO embeddings.
"""

from typing import Optional, List, Dict, Any
from collections import defaultdict

from ..models.knowledge_document import KnowledgeDocument, DocumentType
from ..models.knowledge_reference import KnowledgeReference, RelationshipType
from ..schemas.knowledge import (
    KnowledgeDocumentCreate,
    KnowledgeSearchQuery,
    GraphNode,
    GraphEdge
)


class KnowledgeService:
    """
    Service for knowledge repository operations.
    
    This service provides:
    - Document CRUD (metadata only)
    - Document search
    - Relationship management
    - Knowledge graph building
    
    NO AI, NO embeddings, NO inference.
    """
    
    def __init__(self):
        # In-memory document storage
        self._documents: Dict[str, KnowledgeDocument] = {}
        # Index by category
        self._by_category: Dict[str, List[str]] = defaultdict(list)
        # Index by type
        self._by_type: Dict[str, List[str]] = defaultdict(list)
        # References storage
        self._references: Dict[str, KnowledgeReference] = {}
        # Index by source
        self._by_source: Dict[str, List[str]] = defaultdict(list)
        # Index by target
        self._by_target: Dict[str, List[str]] = defaultdict(list)
    
    def create_document(self, data: KnowledgeDocumentCreate) -> KnowledgeDocument:
        """
        Create a new knowledge document.
        
        Args:
            data: Document data
            
        Returns:
            Created KnowledgeDocument
        """
        doc = KnowledgeDocument(
            title=data.title,
            document_type=DocumentType(data.document_type),
            category=data.category,
            source=data.source,
            author=data.author,
            summary=data.summary,
            tags=data.tags or [],
            external_url=data.external_url
        )
        
        self._documents[doc.id] = doc
        
        # Update indexes
        self._by_category[doc.category].append(doc.id)
        self._by_type[doc.document_type.value].append(doc.id)
        
        return doc
    
    def get_document(self, doc_id: str) -> Optional[KnowledgeDocument]:
        """Get a document by ID."""
        return self._documents.get(doc_id)
    
    def list_documents(
        self,
        category: Optional[str] = None,
        document_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[KnowledgeDocument]:
        """
        List documents with optional filters.
        
        Args:
            category: Filter by category
            document_type: Filter by type
            limit: Max results
            offset: Result offset
            
        Returns:
            List of documents
        """
        results = list(self._documents.values())
        
        if category:
            results = [d for d in results if d.category == category]
        
        if document_type:
            results = [d for d in results if d.document_type.value == document_type]
        
        # Sort by created_at descending
        results.sort(key=lambda d: d.created_at, reverse=True)
        
        return results[offset:offset + limit]
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document and its references.
        
        Args:
            doc_id: Document ID
            
        Returns:
            True if deleted
        """
        if doc_id not in self._documents:
            return False
        
        # Remove from indexes
        doc = self._documents[doc_id]
        self._by_category[doc.category].remove(doc_id)
        self._by_type[doc.document_type.value].remove(doc_id)
        
        # Remove references
        refs_to_delete = [
            ref_id for ref_id, ref in self._references.items()
            if ref.source_document_id == doc_id or ref.target_document_id == doc_id
        ]
        for ref_id in refs_to_delete:
            self._remove_reference(ref_id)
        
        del self._documents[doc_id]
        return True
    
    def create_reference(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str
    ) -> Optional[KnowledgeReference]:
        """
        Create a relationship between documents.
        
        Args:
            source_id: Source document ID
            target_id: Target document ID
            relationship_type: Type of relationship
            
        Returns:
            Created KnowledgeReference or None
        """
        if source_id not in self._documents or target_id not in self._documents:
            return None
        
        if source_id == target_id:
            return None
        
        ref = KnowledgeReference(
            source_document_id=source_id,
            target_document_id=target_id,
            relationship_type=RelationshipType(relationship_type)
        )
        
        self._references[ref.id] = ref
        self._by_source[source_id].append(ref.id)
        self._by_target[target_id].append(ref.id)
        
        return ref
    
    def _remove_reference(self, ref_id: str) -> None:
        """Remove a reference."""
        if ref_id not in self._references:
            return
        
        ref = self._references[ref_id]
        self._by_source[ref.source_document_id].remove(ref_id)
        self._by_target[ref.target_document_id].remove(ref_id)
        del self._references[ref_id]
    
    def get_references(self, doc_id: str) -> List[KnowledgeReference]:
        """Get all references for a document."""
        ref_ids = set(self._by_source.get(doc_id, []) + self._by_target.get(doc_id, []))
        return [self._references[rid] for rid in ref_ids if rid in self._references]
    
    def search_documents(self, query: KnowledgeSearchQuery) -> List[KnowledgeDocument]:
        """
        Search documents.
        
        Args:
            query: Search parameters
            
        Returns:
            List of matching documents
        """
        results = list(self._documents.values())
        
        # Text search
        if query.query:
            query_lower = query.query.lower()
            results = [
                d for d in results
                if query_lower in d.title.lower() or
                   (d.summary and query_lower in d.summary.lower())
            ]
        
        # Apply filters
        if query.category:
            results = [d for d in results if d.category == query.category]
        
        if query.document_type:
            results = [d for d in results if d.document_type.value == query.document_type]
        
        if query.tags:
            results = [
                d for d in results
                if any(tag in d.tags for tag in query.tags)
            ]
        
        if query.author:
            results = [d for d in results if query.author in d.author]
        
        # Sort by created_at descending
        results.sort(key=lambda d: d.created_at, reverse=True)
        
        return results[offset:offset + limit]
    
    def get_category_summary(self) -> List[Dict[str, Any]]:
        """
        Get summary by category.
        
        Returns:
            List of category summaries
        """
        summary = defaultdict(lambda: {"count": 0, "types": defaultdict(int)})
        
        for doc in self._documents.values():
            summary[doc.category]["count"] += 1
            summary[doc.category]["types"][doc.document_type.value] += 1
        
        return [
            {
                "category": cat,
                "document_count": data["count"],
                "types": dict(data["types"])
            }
            for cat, data in summary.items()
        ]
    
    def build_knowledge_graph(
        self,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Build knowledge graph.
        
        Args:
            limit: Max nodes to include
            
        Returns:
            Graph structure
        """
        nodes = []
        edges = []
        
        # Add nodes
        docs = list(self._documents.values())[:limit]
        for doc in docs:
            nodes.append(GraphNode(
                id=doc.id,
                title=doc.title,
                document_type=doc.document_type.value,
                category=doc.category,
                tags=doc.tags
            ))
        
        # Add edges
        for ref in self._references.values():
            if ref.source_document_id in self._documents and ref.target_document_id in self._documents:
                edges.append(GraphEdge(
                    source=ref.source_document_id,
                    target=ref.target_document_id,
                    relationship_type=ref.relationship_type.value
                ))
        
        return {
            "nodes": [n.dict() for n in nodes],
            "edges": [e.dict() for e in edges],
            "total_nodes": len(nodes),
            "total_edges": len(edges)
        }
    
    def get_related_documents(self, doc_id: str) -> List[Dict[str, Any]]:
        """
        Get related documents.
        
        Args:
            doc_id: Document ID
            
        Returns:
            List of related document info
        """
        doc = self._documents.get(doc_id)
        if not doc:
            return []
        
        refs = self.get_references(doc_id)
        related = []
        
        for ref in refs:
            target_id = ref.target_document_id if ref.source_document_id == doc_id else ref.source_document_id
            target = self._documents.get(target_id)
            
            if target:
                related.append({
                    "id": target.id,
                    "title": target.title,
                    "document_type": target.document_type.value,
                    "category": target.category,
                    "relationship_type": ref.relationship_type.value
                })
        
        return related


# Global instance
knowledge_service = KnowledgeService()
