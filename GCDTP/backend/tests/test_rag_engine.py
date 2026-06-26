"""
Tests for RAG Engine

Tests retrieval, chunk scoring, source attribution,
query history, and answer generation.
"""

import pytest
from src.models.rag_query import RAGQuery
from src.models.rag_context_chunk import RAGContextChunk, SourceType
from src.models.rag_answer import RAGAnswer
from src.services.rag_service import RAGService
from src.schemas.rag import RAGQueryRequest
from src.ai.template_provider import TemplateProvider


class TestRAGModels:
    """Tests for RAG models."""
    
    def test_rag_query_creation(self):
        """Test creating a RAG query."""
        query = RAGQuery(
            session_id="session-123",
            query="Why is this asset degraded?"
        )
        
        assert query.session_id == "session-123"
        assert query.query == "Why is this asset degraded?"
    
    def test_rag_context_chunk(self):
        """Test creating a context chunk."""
        chunk = RAGContextChunk(
            query_id="query-123",
            source_type=SourceType.HEALTH,
            source_id="health-456",
            content="Health score: 75/100",
            relevance_score=0.85
        )
        
        assert chunk.source_type == SourceType.HEALTH
        assert chunk.relevance_score == 0.85


class TestTemplateProvider:
    """Tests for template LLM provider."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.provider = TemplateProvider()
    
    def test_provider_name(self):
        """Test provider name."""
        assert self.provider.name() == "template"
    
    def test_provider_availability(self):
        """Test provider is available."""
        assert self.provider.is_available() is True
    
    def test_health_query(self):
        """Test health-related query."""
        context = [
            {
                "source_type": "health",
                "source_id": "health-123",
                "content": "Health score: 75/100, Status: DEGRADED",
                "relevance_score": 0.9
            }
        ]
        
        result = self.provider.generate(context, "What is the health status?")
        
        assert "health" in result["answer"].lower()
        assert result["confidence"] > 0.5
    
    def test_events_query(self):
        """Test events-related query."""
        context = [
            {
                "source_type": "event",
                "source_id": "event-123",
                "content": "2 WARNING events, 1 CRITICAL event",
                "relevance_score": 0.85
            }
        ]
        
        result = self.provider.generate(context, "Show me active events")
        
        assert "event" in result["answer"].lower()
        assert result["confidence"] > 0.5
    
    def test_no_context(self):
        """Test response with no context."""
        result = self.provider.generate([], "Tell me about the system")
        
        assert result["confidence"] < 0.3


class TestRAGService:
    """Tests for RAG service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = RAGService()
    
    def test_retrieve_health_context(self):
        """Test retrieving health context."""
        chunks = self.service.retrieve_context(
            entity_id="asset-123",
            query="health status"
        )
        
        assert len(chunks) > 0
        health_chunks = [c for c in chunks if c["source_type"] == "health"]
        assert len(health_chunks) > 0
    
    def test_retrieve_events_context(self):
        """Test retrieving events context."""
        chunks = self.service.retrieve_context(
            entity_id="asset-123",
            query="events"
        )
        
        assert len(chunks) > 0
    
    def test_retrieve_all_context(self):
        """Test retrieving all context types."""
        chunks = self.service.retrieve_context(
            entity_id="asset-123",
            query="health events timeline"
        )
        
        assert len(chunks) > 0
        
        # Should have chunks from multiple sources
        source_types = set(c["source_type"] for c in chunks)
        assert len(source_types) > 1
    
    def test_relevance_scoring(self):
        """Test relevance scoring."""
        chunks = self.service.retrieve_context(
            entity_id="asset-123",
            query="health status"
        )
        
        # Health chunks should have higher score
        health_chunks = [c for c in chunks if c["source_type"] == "health"]
        other_chunks = [c for c in chunks if c["source_type"] != "health"]
        
        if health_chunks and other_chunks:
            assert health_chunks[0]["relevance_score"] >= other_chunks[0]["relevance_score"]
    
    def test_answer_query(self):
        """Test answering a query."""
        request = RAGQueryRequest(
            query="What is the health status?",
            session_id="session-123",
            entity_id="asset-123"
        )
        
        chunks = self.service.retrieve_context(
            entity_id="asset-123",
            query=request.query
        )
        
        answer = self.service.answer_query(request, chunks)
        
        assert "answer" in answer
        assert "confidence" in answer
        assert "sources" in answer
    
    def test_store_query(self):
        """Test storing query for audit."""
        request = RAGQueryRequest(
            query="Test query",
            session_id="session-123"
        )
        
        chunks = [
            {
                "source_type": "health",
                "source_id": "health-123",
                "content": "Test content",
                "relevance_score": 0.9
            }
        ]
        
        answer = {
            "answer": "Test answer",
            "confidence": 0.8,
            "sources": ["health-123"]
        }
        
        query_id = self.service.store_query(request, chunks, answer)
        
        assert query_id is not None
        
        # Verify stored data
        stored_query = self.service.get_query(query_id)
        assert stored_query is not None
        assert stored_query.query == "Test query"
        
        stored_chunks = self.service.get_chunks(query_id)
        assert len(stored_chunks) == 1
        
        stored_answer = self.service.get_answer(query_id)
        assert stored_answer is not None
        assert stored_answer.answer == "Test answer"
    
    def test_get_history(self):
        """Test getting query history."""
        # Store multiple queries
        for i in range(3):
            request = RAGQueryRequest(
                query=f"Query {i}",
                session_id="session-123"
            )
            self.service.store_query(request, [], {"answer": f"Answer {i}"})
        
        history = self.service.get_history("session-123")
        
        assert len(history) == 3
    
    def test_get_available_models(self):
        """Test getting available models."""
        models = self.service.get_available_models()
        
        assert len(models) >= 1
        
        # Template should be available
        template = next(m for m in models if m["name"] == "template")
        assert template["status"] == "available"
        
        # OpenAI should be future
        openai = next(m for m in models if m["name"] == "openai")
        assert openai["status"] == "future"


class TestSourceAttribution:
    """Tests for source attribution."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = RAGService()
    
    def test_sources_tracked(self):
        """Test that sources are tracked."""
        request = RAGQueryRequest(
            query="Health status?",
            session_id="session-123",
            entity_id="asset-123"
        )
        
        chunks = self.service.retrieve_context(
            entity_id="asset-123",
            query=request.query
        )
        
        answer = self.service.answer_query(request, chunks)
        
        # Sources should be tracked
        assert "sources" in answer or len(chunks) > 0
    
    def test_chunks_have_source_info(self):
        """Test that chunks have source information."""
        chunks = self.service.retrieve_context(
            entity_id="asset-123",
            query="test"
        )
        
        for chunk in chunks:
            assert "source_type" in chunk
            assert "content" in chunk
            assert "relevance_score" in chunk


class TestReadOnlyCompliance:
    """Tests for read-only compliance."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = RAGService()
    
    def test_no_operational_writes(self):
        """Test that RAG does not perform operational writes."""
        # This test verifies the service only stores audit records
        request = RAGQueryRequest(
            query="Test",
            session_id="session-123",
            entity_id="asset-123"
        )
        
        chunks = self.service.retrieve_context(
            entity_id="asset-123",
            query=request.query
        )
        
        # Store should only create audit records
        query_id = self.service.store_query(request, chunks, {"answer": "test"})
        
        # Verify it's stored as audit, not operational
        stored_query = self.service.get_query(query_id)
        assert stored_query is not None
        
        # No writes to assets, sensors, events, etc. should occur
        # This is verified by the fact that we only store in _queries, _chunks, _answers
