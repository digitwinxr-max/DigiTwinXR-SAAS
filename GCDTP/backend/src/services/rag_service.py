"""
RAG Service

Retrieval-Augmented Generation service.
Retrieves context from all platform engines and generates answers.
This is read-only - NO operational writes.
"""

from typing import Optional, List, Dict, Any
from collections import defaultdict

from ..models.rag_query import RAGQuery
from ..models.rag_context_chunk import RAGContextChunk, SourceType
from ..models.rag_answer import RAGAnswer
from ..schemas.rag import (
    RAGQueryRequest,
    RAGContextChunkResponse,
    RAGAnswerResponse,
    RAGSourcesResponse,
    RAGSource
)
from ..ai.template_provider import TemplateProvider


class RAGService:
    """
    RAG (Retrieval-Augmented Generation) Service.
    
    Retrieves context from:
    - Semantic Layer (entity relationships)
    - Health Engine (health scores, penalties)
    - Event Engine (active events)
    - Timeline Engine (historical states)
    - Logbook Engine (operator notes)
    - Knowledge Repository (manuals, SOPs)
    
    Generates answers using:
    - TemplateProvider (current)
    - OpenAIProvider (future)
    - ClaudeProvider (future)
    
    IMPORTANT:
    - This is READ ONLY - no operational modifications
    - This is AUDIT ONLY - records queries and answers
    """
    
    def __init__(self):
        # In-memory storage for audit
        self._queries: Dict[str, RAGQuery] = {}
        self._chunks: Dict[str, RAGContextChunk] = {}
        self._answers: Dict[str, RAGAnswer] = {}
        
        # Index by query
        self._chunks_by_query: Dict[str, List[str]] = defaultdict(list)
        
        # LLM Providers
        self._providers = {
            "template": TemplateProvider()
        }
        
        # Current provider
        self._current_provider = "template"
    
    def get_available_models(self) -> List[Dict[str, str]]:
        """Get available and future models."""
        return [
            {
                "name": "template",
                "status": "available",
                "description": "Template-based response generation (placeholder)",
                "provider": "internal"
            },
            {
                "name": "openai",
                "status": "future",
                "description": "OpenAI GPT integration (not implemented)",
                "provider": "openai"
            },
            {
                "name": "claude",
                "status": "future",
                "description": "Claude AI integration (not implemented)",
                "provider": "anthropic"
            },
            {
                "name": "gemini",
                "status": "future",
                "description": "Google Gemini integration (not implemented)",
                "provider": "google"
            },
            {
                "name": "local",
                "status": "future",
                "description": "Local LLM integration (not implemented)",
                "provider": "local"
            }
        ]
    
    def set_provider(self, provider_name: str) -> bool:
        """Set current LLM provider."""
        if provider_name in self._providers:
            self._current_provider = provider_name
            return True
        return False
    
    def retrieve_context(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        query: Optional[str] = None,
        include_semantic: bool = True,
        include_health: bool = True,
        include_events: bool = True,
        include_timeline: bool = True,
        include_logbook: bool = True,
        include_knowledge: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve context from all engines.
        
        Args:
            entity_type: Entity type to focus on
            entity_id: Entity ID to focus on
            query: Optional query for relevance scoring
            include_*: Flags for which engines to query
            
        Returns:
            List of context chunks with relevance scores
        """
        chunks = []
        
        if include_health:
            chunks.extend(self._retrieve_health_context(entity_type, entity_id, query))
        
        if include_events:
            chunks.extend(self._retrieve_events_context(entity_type, entity_id, query))
        
        if include_semantic:
            chunks.extend(self._retrieve_semantic_context(entity_type, entity_id, query))
        
        if include_timeline:
            chunks.extend(self._retrieve_timeline_context(entity_type, entity_id, query))
        
        if include_logbook:
            chunks.extend(self._retrieve_logbook_context(entity_type, entity_id, query))
        
        if include_knowledge:
            chunks.extend(self._retrieve_knowledge_context(entity_type, entity_id, query))
        
        # Sort by relevance score
        chunks.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return chunks[:20]  # Limit to top 20 chunks
    
    def _retrieve_health_context(
        self,
        entity_type: Optional[str],
        entity_id: Optional[str],
        query: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Retrieve health context."""
        chunks = []
        
        # Check if query mentions health
        query_lower = (query or "").lower()
        health_relevant = any(
            word in query_lower for word in ["health", "status", "condition", "score", "degraded", "critical"]
        )
        
        if entity_id:
            # Simulate health retrieval (in real implementation, call Health Engine)
            chunk = {
                "source_type": "health",
                "source_id": f"health-{entity_id}",
                "content": f"Health status for {entity_id}: Score 85/100, Status HEALTHY, Dependency penalty: 5%",
                "relevance_score": 0.9 if health_relevant else 0.3
            }
            chunks.append(chunk)
        
        return chunks
    
    def _retrieve_events_context(
        self,
        entity_type: Optional[str],
        entity_id: Optional[str],
        query: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Retrieve events context."""
        chunks = []
        
        # Check if query mentions events
        query_lower = (query or "").lower()
        event_relevant = any(
            word in query_lower for word in ["event", "alert", "warning", "critical", "issue", "problem"]
        )
        
        if entity_id:
            # Simulate events retrieval
            chunk = {
                "source_type": "event",
                "source_id": f"event-{entity_id}",
                "content": f"Active events for {entity_id}: 2 warnings, 0 critical",
                "relevance_score": 0.85 if event_relevant else 0.25
            }
            chunks.append(chunk)
        
        return chunks
    
    def _retrieve_semantic_context(
        self,
        entity_type: Optional[str],
        entity_id: Optional[str],
        query: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Retrieve semantic context."""
        chunks = []
        
        # Check if query mentions relationships
        query_lower = (query or "").lower()
        semantic_relevant = any(
            word in query_lower for word in ["related", "dependency", "connection", "relationship", "depends"]
        )
        
        if entity_id:
            # Simulate semantic retrieval
            chunk = {
                "source_type": "semantic",
                "source_id": f"semantic-{entity_id}",
                "content": f"Semantic relationships for {entity_id}: Connected to parent systems, has 3 dependencies",
                "relevance_score": 0.8 if semantic_relevant else 0.2
            }
            chunks.append(chunk)
        
        return chunks
    
    def _retrieve_timeline_context(
        self,
        entity_type: Optional[str],
        entity_id: Optional[str],
        query: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Retrieve timeline context."""
        chunks = []
        
        # Check if query mentions history/timeline
        query_lower = (query or "").lower()
        timeline_relevant = any(
            word in query_lower for word in ["timeline", "history", "before", "after", "past", "when"]
        )
        
        if entity_id:
            # Simulate timeline retrieval
            chunk = {
                "source_type": "timeline",
                "source_id": f"timeline-{entity_id}",
                "content": f"Timeline for {entity_id}: Last state change 2 hours ago, 24 snapshots in past 24 hours",
                "relevance_score": 0.75 if timeline_relevant else 0.15
            }
            chunks.append(chunk)
        
        return chunks
    
    def _retrieve_logbook_context(
        self,
        entity_type: Optional[str],
        entity_id: Optional[str],
        query: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Retrieve logbook context."""
        chunks = []
        
        # Check if query mentions notes/logbook
        query_lower = (query or "").lower()
        logbook_relevant = any(
            word in query_lower for word in ["note", "logbook", "observation", "operator", "comment", "remark"]
        )
        
        if entity_id:
            # Simulate logbook retrieval
            chunk = {
                "source_type": "logbook",
                "source_id": f"logbook-{entity_id}",
                "content": f"Logbook entries for {entity_id}: 5 entries in past week, last by operator on duty",
                "relevance_score": 0.7 if logbook_relevant else 0.1
            }
            chunks.append(chunk)
        
        return chunks
    
    def _retrieve_knowledge_context(
        self,
        entity_type: Optional[str],
        entity_id: Optional[str],
        query: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Retrieve knowledge context."""
        chunks = []
        
        # Check if query mentions documents/knowledge
        query_lower = (query or "").lower()
        knowledge_relevant = any(
            word in query_lower for word in ["document", "sop", "manual", "knowledge", "lesson", "troubleshoot"]
        )
        
        if entity_id or knowledge_relevant:
            # Simulate knowledge retrieval
            chunk = {
                "source_type": "knowledge",
                "source_id": f"knowledge-{entity_id}",
                "content": f"Knowledge for {entity_id}: 2 related SOPs, 1 troubleshooting guide, 0 lessons learned",
                "relevance_score": 0.65 if knowledge_relevant else 0.1
            }
            chunks.append(chunk)
        
        return chunks
    
    def build_context(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Build context for LLM from retrieved chunks.
        
        Args:
            chunks: List of context chunks
            
        Returns:
            Formatted context for LLM
        """
        return [
            {
                "source_type": c.get("source_type", "unknown"),
                "source_id": c.get("source_id"),
                "content": c.get("content", ""),
                "relevance_score": c.get("relevance_score", 0.0)
            }
            for c in chunks
        ]
    
    def answer_query(
        self,
        request: RAGQueryRequest,
        context_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Answer query using RAG.
        
        Args:
            request: Query request
            context_chunks: Retrieved context chunks
            
        Returns:
            Answer with sources and confidence
        """
        # Get provider
        provider = self._providers.get(self._current_provider)
        if not provider:
            provider = self._providers["template"]
        
        # Build context for LLM
        llm_context = self.build_context(context_chunks)
        
        # Generate answer
        result = provider.generate(llm_context, request.query)
        
        return {
            "answer": result.get("answer", ""),
            "confidence": result.get("confidence", 0.5),
            "sources": result.get("sources", []),
            "model": result.get("model", self._current_provider),
            "chunks_used": len(context_chunks)
        }
    
    def store_query(
        self,
        request: RAGQueryRequest,
        context_chunks: List[Dict[str, Any]],
        answer: Dict[str, Any]
    ) -> str:
        """
        Store query for audit purposes.
        
        Args:
            request: Query request
            context_chunks: Retrieved chunks
            answer: Generated answer
            
        Returns:
            Query ID
        """
        # Store query
        query = RAGQuery(
            session_id=request.session_id,
            query=request.query
        )
        self._queries[query.id] = query
        
        # Store chunks
        for chunk in context_chunks:
            rag_chunk = RAGContextChunk(
                query_id=query.id,
                source_type=SourceType(chunk.get("source_type", "unknown")),
                source_id=chunk.get("source_id"),
                content=chunk.get("content", ""),
                relevance_score=chunk.get("relevance_score", 0.0)
            )
            self._chunks[rag_chunk.id] = rag_chunk
            self._chunks_by_query[query.id].append(rag_chunk.id)
        
        # Store answer
        rag_answer = RAGAnswer(
            query_id=query.id,
            answer=answer.get("answer", ""),
            model_name=answer.get("model", "template"),
            confidence=answer.get("confidence")
        )
        self._answers[rag_answer.id] = rag_answer
        
        return query.id
    
    def get_query(self, query_id: str) -> Optional[RAGQuery]:
        """Get query by ID."""
        return self._queries.get(query_id)
    
    def get_chunks(self, query_id: str) -> List[RAGContextChunk]:
        """Get chunks for a query."""
        chunk_ids = self._chunks_by_query.get(query_id, [])
        return [self._chunks[cid] for cid in chunk_ids if cid in self._chunks]
    
    def get_answer(self, query_id: str) -> Optional[RAGAnswer]:
        """Get answer for a query."""
        for answer in self._answers.values():
            if answer.query_id == query_id:
                return answer
        return None
    
    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get query history for a session."""
        history = []
        
        for query in self._queries.values():
            if query.session_id == session_id:
                answer = self.get_answer(query.id)
                chunks = self.get_chunks(query.id)
                
                history.append({
                    "query_id": query.id,
                    "query": query.query,
                    "answer_preview": answer.answer[:100] + "..." if answer and len(answer.answer) > 100 else (answer.answer if answer else ""),
                    "model_name": answer.model_name if answer else "unknown",
                    "created_at": query.created_at,
                    "chunk_count": len(chunks)
                })
        
        # Sort by created_at descending
        history.sort(key=lambda x: x["created_at"], reverse=True)
        
        return history


# Global instance
rag_service = RAGService()
