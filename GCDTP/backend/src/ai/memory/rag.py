"""
RAG (Retrieval Augmented Generation) Foundation

Deterministic retrieval infrastructure.
NO autonomous execution - retrieval only.
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib


class RetrievalStrategy(str, Enum):
    """Retrieval strategy types."""
    VECTOR = "vector"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    BM25 = "bm25"


@dataclass
class Document:
    """Document for RAG."""
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Chunk:
    """Document chunk."""
    id: str
    document_id: str
    content: str
    chunk_index: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    start_char: int = 0
    end_char: int = 0


@dataclass
class RetrievalResult:
    """Retrieval result."""
    chunk: Chunk
    score: float
    rank: int
    source: str = "vector"


@dataclass
class RAGQuery:
    """RAG query."""
    query_text: str
    strategy: RetrievalStrategy = RetrievalStrategy.HYBRID
    top_k: int = 5
    min_score: float = 0.5
    filters: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None


@dataclass
class RAGResponse:
    """RAG response."""
    query: str
    results: List[RetrievalResult]
    total_chunks: int
    retrieval_time_ms: float
    context: Optional[str] = None


class VectorStore:
    """
    Vector store interface for embeddings.
    
    This is a deterministic storage interface - no AI execution.
    """
    
    def __init__(self):
        self._vectors: Dict[str, List[float]] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
    
    def add(self, chunk_id: str, embedding: List[float], metadata: Dict[str, Any]) -> bool:
        """Add embedding to store."""
        self._vectors[chunk_id] = embedding
        self._metadata[chunk_id] = metadata
        return True
    
    def get(self, chunk_id: str) -> Optional[List[float]]:
        """Get embedding by ID."""
        return self._vectors.get(chunk_id)
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        min_score: float = 0.0
    ) -> List[Tuple[str, float]]:
        """
        Search for similar embeddings.
        
        Note: This is deterministic similarity search.
        """
        results = []
        
        for chunk_id, embedding in self._vectors.items():
            score = self._cosine_similarity(query_embedding, embedding)
            if score >= min_score:
                results.append((chunk_id, score))
        
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:top_k]
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity."""
        if len(a) != len(b):
            return 0.0
        
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def delete(self, chunk_id: str) -> bool:
        """Delete embedding."""
        if chunk_id in self._vectors:
            del self._vectors[chunk_id]
            del self._metadata[chunk_id]
            return True
        return False
    
    def count(self) -> int:
        """Count embeddings."""
        return len(self._vectors)


class KeywordIndex:
    """
    Keyword index for text search.
    
    Deterministic TF-IDF based indexing.
    """
    
    def __init__(self):
        self._documents: Dict[str, str] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._index: Dict[str, Dict[str, int]] = {}  # term -> doc_id -> count
    
    def add(self, chunk_id: str, content: str, metadata: Dict[str, Any]) -> bool:
        """Add document to index."""
        self._documents[chunk_id] = content
        self._metadata[chunk_id] = metadata
        
        # Tokenize and build inverted index
        tokens = self._tokenize(content)
        self._index_chunk(chunk_id, tokens)
        
        return True
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        return text.lower().split()
    
    def _index_chunk(self, chunk_id: str, tokens: List[str]) -> None:
        """Index a chunk."""
        token_counts: Dict[str, int] = {}
        for token in tokens:
            token_counts[token] = token_counts.get(token, 0) + 1
        
        for token, count in token_counts.items():
            if token not in self._index:
                self._index[token] = {}
            self._index[token][chunk_id] = count
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.0
    ) -> List[Tuple[str, float]]:
        """
        Search for matching documents.
        
        Deterministic TF-IDF scoring.
        """
        tokens = self._tokenize(query)
        
        # Calculate scores
        scores: Dict[str, float] = {}
        for token in tokens:
            if token in self._index:
                for chunk_id, count in self._index[token].items():
                    if chunk_id not in scores:
                        scores[chunk_id] = 0
                    scores[chunk_id] += count
        
        # Normalize by document length
        for chunk_id in scores:
            doc_len = len(self._documents.get(chunk_id, "").split())
            if doc_len > 0:
                scores[chunk_id] /= doc_len
        
        # Convert to list and filter
        results = [(k, v) for k, v in scores.items() if v >= min_score]
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:top_k]
    
    def delete(self, chunk_id: str) -> bool:
        """Delete document."""
        if chunk_id in self._documents:
            del self._documents[chunk_id]
            del self._metadata[chunk_id]
            
            # Remove from inverted index
            for token in self._index:
                if chunk_id in self._index[token]:
                    del self._index[token][chunk_id]
            
            return True
        return False


class RAGEngine:
    """
    RAG Engine for retrieval.
    
    Deterministic retrieval - no AI execution.
    """
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.keyword_index = KeywordIndex()
        self.chunks: Dict[str, Chunk] = {}
    
    def add_chunk(
        self,
        chunk_id: str,
        document_id: str,
        content: str,
        chunk_index: int,
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[List[float]] = None,
        start_char: int = 0,
        end_char: int = 0
    ) -> bool:
        """Add a chunk to the index."""
        chunk = Chunk(
            id=chunk_id,
            document_id=document_id,
            content=content,
            chunk_index=chunk_index,
            metadata=metadata or {},
            embedding=embedding,
            start_char=start_char,
            end_char=end_char
        )
        
        self.chunks[chunk_id] = chunk
        
        # Add to vector store
        if embedding:
            self.vector_store.add(chunk_id, embedding, metadata or {})
        
        # Add to keyword index
        self.keyword_index.add(chunk_id, content, metadata or {})
        
        return True
    
    def add_document(
        self,
        document: Document,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ) -> List[str]:
        """Add a document, chunked automatically."""
        chunk_ids = []
        
        # Simple chunking
        start = 0
        chunk_index = 0
        
        while start < len(document.content):
            end = min(start + chunk_size, len(document.content))
            chunk_content = document.content[start:end]
            
            chunk_id = f"{document.id}_chunk_{chunk_index}"
            
            self.add_chunk(
                chunk_id=chunk_id,
                document_id=document.id,
                content=chunk_content,
                chunk_index=chunk_index,
                metadata=document.metadata,
                embedding=document.embedding,  # Would need model for real embeddings
                start_char=start,
                end_char=end
            )
            
            chunk_ids.append(chunk_id)
            chunk_index += 1
            start = end - chunk_overlap
        
        return chunk_ids
    
    def retrieve(self, query: RAGQuery) -> RAGResponse:
        """
        Retrieve relevant chunks.
        
        Deterministic retrieval based on strategy.
        """
        start_time = datetime.now()
        results: List[RetrievalResult] = []
        
        if query.strategy == RetrievalStrategy.VECTOR:
            results = self._vector_search(query)
        elif query.strategy == RetrievalStrategy.KEYWORD:
            results = self._keyword_search(query)
        elif query.strategy == RetrievalStrategy.HYBRID:
            results = self._hybrid_search(query)
        elif query.strategy == RetrievalStrategy.BM25:
            results = self._keyword_search(query)  # BM25 approximation
        
        # Apply filters
        if query.filters:
            results = self._apply_filters(results, query.filters)
        
        # Assign ranks
        for i, result in enumerate(results):
            result.rank = i + 1
        
        # Build context
        context = self._build_context(results, query.top_k)
        
        retrieval_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return RAGResponse(
            query=query.query_text,
            results=results,
            total_chunks=len(self.chunks),
            retrieval_time_ms=retrieval_time,
            context=context
        )
    
    def _vector_search(self, query: RAGQuery) -> List[RetrievalResult]:
        """Vector similarity search."""
        results = []
        
        # For demo, use random embedding
        # In production, would use actual embedding model
        query_embedding = self._generate_demo_embedding(query.query_text)
        
        vector_results = self.vector_store.search(
            query_embedding,
            top_k=query.top_k,
            min_score=query.min_score
        )
        
        for chunk_id, score in vector_results:
            chunk = self.chunks.get(chunk_id)
            if chunk:
                results.append(RetrievalResult(
                    chunk=chunk,
                    score=score,
                    rank=0,
                    source="vector"
                ))
        
        return results
    
    def _keyword_search(self, query: RAGQuery) -> List[RetrievalResult]:
        """Keyword search."""
        results = []
        
        keyword_results = self.keyword_index.search(
            query.query_text,
            top_k=query.top_k,
            min_score=query.min_score
        )
        
        for chunk_id, score in keyword_results:
            chunk = self.chunks.get(chunk_id)
            if chunk:
                results.append(RetrievalResult(
                    chunk=chunk,
                    score=score,
                    rank=0,
                    source="keyword"
                ))
        
        return results
    
    def _hybrid_search(self, query: RAGQuery) -> List[RetrievalResult]:
        """Hybrid search combining vector and keyword."""
        vector_results = self._vector_search(query)
        keyword_results = self._keyword_search(query)
        
        # Combine and rerank
        combined: Dict[str, RetrievalResult] = {}
        
        for result in vector_results:
            combined[result.chunk.id] = result
        
        for result in keyword_results:
            if result.chunk.id in combined:
                # Average scores
                avg_score = (combined[result.chunk.id].score + result.score) / 2
                combined[result.chunk.id].score = avg_score
            else:
                combined[result.chunk.id] = result
        
        # Sort by combined score
        results = list(combined.values())
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results[:query.top_k]
    
    def _apply_filters(
        self,
        results: List[RetrievalResult],
        filters: Dict[str, Any]
    ) -> List[RetrievalResult]:
        """Apply metadata filters."""
        filtered = []
        
        for result in results:
            matches = True
            for key, value in filters.items():
                if key in result.chunk.metadata:
                    if result.chunk.metadata[key] != value:
                        matches = False
                        break
            
            if matches:
                filtered.append(result)
        
        return filtered
    
    def _build_context(
        self,
        results: List[RetrievalResult],
        max_chunks: int
    ) -> str:
        """Build context string from chunks."""
        context_parts = []
        
        for result in results[:max_chunks]:
            context_parts.append(f"[Source {result.rank}]: {result.chunk.content}")
        
        return "\n\n".join(context_parts)
    
    def _generate_demo_embedding(self, text: str) -> List[float]:
        """Generate deterministic demo embedding based on text hash."""
        import struct
        
        # Create deterministic pseudo-embedding from text
        hash_bytes = hashlib.md5(text.encode()).digest()
        embedding = list(struct.unpack('f' * 16, hash_bytes[:64].ljust(64, b'\x00')))
        
        # Normalize
        norm = sum(x * x for x in embedding) ** 0.5
        if norm > 0:
            embedding = [x / norm for x in embedding]
        
        return embedding
    
    def get_chunk(self, chunk_id: str) -> Optional[Chunk]:
        """Get chunk by ID."""
        return self.chunks.get(chunk_id)
    
    def get_document_chunks(self, document_id: str) -> List[Chunk]:
        """Get all chunks for a document."""
        return [
            c for c in self.chunks.values()
            if c.document_id == document_id
        ]
    
    def delete_chunk(self, chunk_id: str) -> bool:
        """Delete a chunk."""
        if chunk_id in self.chunks:
            del self.chunks[chunk_id]
            self.vector_store.delete(chunk_id)
            self.keyword_index.delete(chunk_id)
            return True
        return False
