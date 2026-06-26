"""
Document Indexer

Pure Python search and indexing for documents.
No external search engine dependencies.
"""

from typing import Dict, List, Optional, Set
from datetime import datetime
from backend.src.services.documents.document_types import (
    Document,
    DocumentIndex,
    DocumentFilter,
    DocumentSearchResult,
    DocumentType,
    DocumentStatus,
)


class DocumentIndexer:
    """
    Pure Python document indexer.
    
    Features:
    - In-memory indexing
    - Full-text search on title/description
    - Tag-based filtering
    - Asset/work order filtering
    - Type filtering
    - Date range filtering
    - Relevance scoring
    """
    
    def __init__(self):
        self._index: Dict[str, DocumentIndex] = {}
        self._title_index: Dict[str, Set[str]] = {}  # word -> document_ids
        self._description_index: Dict[str, Set[str]] = {}
        self._tag_index: Dict[str, Set[str]] = {}  # tag -> document_ids
        self._type_index: Dict[str, Set[str]] = {}  # type -> document_ids
        self._asset_index: Dict[str, Set[str]] = {}  # asset_id -> document_ids
        self._work_order_index: Dict[str, Set[str]] = {}  # work_order_id -> document_ids
    
    def index_document(self, document: Document, tags: Optional[List[str]] = None) -> None:
        """
        Index a document.
        
        Args:
            document: Document to index
            tags: Document tags
        """
        # Create index entry
        index_entry = DocumentIndex(
            document_id=document.id,
            title=document.title,
            description=document.description,
            document_type=document.document_type.value,
            tags=tags or [],
            asset_id=document.asset_id,
            work_order_id=document.work_order_id,
            status=document.status.value,
            created_at=document.created_at,
            updated_at=document.updated_at
        )
        
        self._index[document.id] = index_entry
        
        # Index title words
        self._index_text(document.title, self._title_index, document.id)
        
        # Index description words
        self._index_text(document.description, self._description_index, document.id)
        
        # Index tags
        for tag in (tags or []):
            self._add_to_index(self._tag_index, tag.lower(), document.id)
        
        # Index by type
        self._add_to_index(self._type_index, document.document_type.value, document.id)
        
        # Index by asset
        if document.asset_id:
            self._add_to_index(self._asset_index, document.asset_id, document.id)
        
        # Index by work order
        if document.work_order_id:
            self._add_to_index(self._work_order_index, document.work_order_id, document.id)
    
    def update_document(self, document: Document, tags: Optional[List[str]] = None) -> None:
        """
        Update a document in the index.
        
        Args:
            document: Document to update
            tags: Updated tags
        """
        # Remove old entry
        if document.id in self._index:
            old_entry = self._index[document.id]
            
            # Remove from title index
            self._remove_from_index(self._title_index, old_entry.title, document.id)
            
            # Remove from description index
            self._remove_from_index(self._description_index, old_entry.description, document.id)
            
            # Remove old tags
            for tag in old_entry.tags:
                self._remove_from_index(self._tag_index, tag.lower(), document.id)
            
            # Remove from type index
            self._remove_from_index(self._type_index, old_entry.document_type, document.id)
            
            # Remove from asset index
            if old_entry.asset_id:
                self._remove_from_index(self._asset_index, old_entry.asset_id, document.id)
            
            # Remove from work order index
            if old_entry.work_order_id:
                self._remove_from_index(self._work_order_index, old_entry.work_order_id, document.id)
        
        # Re-index
        self.index_document(document, tags)
    
    def remove_document(self, document_id: str) -> None:
        """
        Remove a document from the index.
        
        Args:
            document_id: ID of document to remove
        """
        if document_id not in self._index:
            return
        
        entry = self._index[document_id]
        
        # Remove from all indexes
        self._remove_from_index(self._title_index, entry.title, document_id)
        self._remove_from_index(self._description_index, entry.description, document_id)
        
        for tag in entry.tags:
            self._remove_from_index(self._tag_index, tag.lower(), document_id)
        
        self._remove_from_index(self._type_index, entry.document_type, document_id)
        
        if entry.asset_id:
            self._remove_from_index(self._asset_index, entry.asset_id, document_id)
        
        if entry.work_order_id:
            self._remove_from_index(self._work_order_index, entry.work_order_id, document_id)
        
        # Remove from main index
        del self._index[document_id]
    
    def search(self, filter: DocumentFilter) -> List[DocumentSearchResult]:
        """
        Search documents.
        
        Args:
            filter: Search filter
            
        Returns:
            List of matching documents with scores
        """
        results: List[DocumentSearchResult] = []
        
        for doc_id, index_entry in self._index.items():
            # Apply filters
            if not index_entry.matches(filter):
                continue
            
            # Skip archived/deleted unless requested
            if index_entry.status == DocumentStatus.DELETED.value and not filter.include_deleted:
                continue
            
            if index_entry.status == DocumentStatus.ARCHIVED.value and not filter.include_archived:
                continue
            
            # Calculate relevance score
            score = self._calculate_score(index_entry, filter)
            
            if score > 0:
                # Create document from index
                document = self._create_document_from_index(index_entry)
                results.append(DocumentSearchResult(
                    document=document,
                    score=score,
                    matched_fields=self._get_matched_fields(index_entry, filter)
                ))
        
        # Sort by score descending
        results.sort(key=lambda r: r.score, reverse=True)
        
        # Apply pagination
        return results[filter.offset:filter.offset + filter.limit]
    
    def search_by_text(self, text: str, limit: int = 100) -> List[DocumentSearchResult]:
        """
        Full-text search.
        
        Args:
            text: Search text
            filter: Additional filter
            
        Returns:
            List of matching documents
        """
        filter = DocumentFilter(search_text=text, limit=limit)
        return self.search(filter)
    
    def search_by_tag(self, tag: str) -> List[Document]:
        """Search documents by tag."""
        filter = DocumentFilter(tags=[tag])
        results = self.search(filter)
        return [r.document for r in results]
    
    def search_by_asset(self, asset_id: str) -> List[Document]:
        """Search documents by asset."""
        filter = DocumentFilter(asset_id=asset_id)
        results = self.search(filter)
        return [r.document for r in results]
    
    def search_by_work_order(self, work_order_id: str) -> List[Document]:
        """Search documents by work order."""
        filter = DocumentFilter(work_order_id=work_order_id)
        results = self.search(filter)
        return [r.document for r in results]
    
    def search_by_type(self, document_type: DocumentType) -> List[Document]:
        """Search documents by type."""
        filter = DocumentFilter(document_types=[document_type])
        results = self.search(filter)
        return [r.document for r in results]
    
    def get_all_tags(self) -> List[str]:
        """Get all unique tags."""
        return list(self._tag_index.keys())
    
    def get_tag_counts(self) -> Dict[str, int]:
        """Get tag usage counts."""
        return {tag: len(doc_ids) for tag, doc_ids in self._tag_index.items()}
    
    def get_document_count(self) -> int:
        """Get total indexed document count."""
        return len(self._index)
    
    def clear(self) -> None:
        """Clear the entire index."""
        self._index.clear()
        self._title_index.clear()
        self._description_index.clear()
        self._tag_index.clear()
        self._type_index.clear()
        self._asset_index.clear()
        self._work_order_index.clear()
    
    # =========================================================================
    # Internal Methods
    # =========================================================================
    
    def _index_text(self, text: str, index: Dict[str, Set[str]], doc_id: str) -> None:
        """Index words from text."""
        words = self._tokenize(text)
        for word in words:
            self._add_to_index(index, word, doc_id)
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        if not text:
            return []
        
        # Simple tokenization: lowercase, split on non-alphanumeric
        import re
        words = re.findall(r'\w+', text.lower())
        
        # Filter short words
        return [w for w in words if len(w) >= 2]
    
    def _add_to_index(self, index: Dict[str, Set[str]], key: str, doc_id: str) -> None:
        """Add document to index entry."""
        key_lower = key.lower()
        if key_lower not in index:
            index[key_lower] = set()
        index[key_lower].add(doc_id)
    
    def _remove_from_index(self, index: Dict[str, Set[str]], text: str, doc_id: str) -> None:
        """Remove document from index entry."""
        words = self._tokenize(text)
        for word in words:
            if word in index:
                index[word].discard(doc_id)
                if not index[word]:
                    del index[word]
    
    def _calculate_score(self, index_entry: DocumentIndex, filter: DocumentFilter) -> float:
        """Calculate relevance score."""
        score = 0.0
        
        # Text match score
        if filter.search_text:
            search_words = self._tokenize(filter.search_text)
            
            # Title match (highest weight)
            title_words = self._tokenize(index_entry.title)
            title_matches = sum(1 for w in search_words if w in title_words)
            score += title_matches * 3.0
            
            # Description match (medium weight)
            desc_words = self._tokenize(index_entry.description)
            desc_matches = sum(1 for w in search_words if w in desc_words)
            score += desc_matches * 1.0
        
        # Tag match score
        if filter.tags:
            matching_tags = sum(1 for t in filter.tags if t.lower() in [tag.lower() for tag in index_entry.tags])
            score += matching_tags * 2.0
        
        # Type match bonus
        if filter.document_types:
            if any(t.value == index_entry.document_type for t in filter.document_types):
                score += 1.0
        
        # Status match bonus
        if filter.statuses:
            if any(s.value == index_entry.status for s in filter.statuses):
                score += 0.5
        
        # Recency bonus (newer documents score higher)
        days_old = (datetime.utcnow() - index_entry.updated_at).days
        if days_old < 7:
            score += 2.0
        elif days_old < 30:
            score += 1.0
        elif days_old < 90:
            score += 0.5
        
        return score
    
    def _get_matched_fields(self, index_entry: DocumentIndex, filter: DocumentFilter) -> List[str]:
        """Get list of matched fields."""
        matched = []
        
        if filter.search_text:
            search_words = self._tokenize(filter.search_text)
            
            if any(w in self._tokenize(index_entry.title) for w in search_words):
                matched.append("title")
            
            if any(w in self._tokenize(index_entry.description) for w in search_words):
                matched.append("description")
        
        if filter.tags:
            if any(t.lower() in [tag.lower() for tag in index_entry.tags] for t in filter.tags):
                matched.append("tags")
        
        if filter.document_types:
            if any(t.value == index_entry.document_type for t in filter.document_types):
                matched.append("document_type")
        
        return matched
    
    def _create_document_from_index(self, index_entry: DocumentIndex) -> Document:
        """Create a Document from an index entry."""
        return Document(
            id=index_entry.document_id,
            title=index_entry.title,
            description=index_entry.description,
            document_type=DocumentType(index_entry.document_type),
            asset_id=index_entry.asset_id,
            work_order_id=index_entry.work_order_id,
            status=DocumentStatus(index_entry.status),
            created_at=index_entry.created_at,
            updated_at=index_entry.updated_at
        )
