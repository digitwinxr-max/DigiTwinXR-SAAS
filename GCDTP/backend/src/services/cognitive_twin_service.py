"""
Cognitive Twin Service

Convergence layer - aggregates context from all platform engines.
ADVISORY ONLY - NO automation, NO autonomous decisions.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from collections import defaultdict

from ..models.cognitive_session import CognitiveSession
from ..models.cognitive_query import CognitiveQuery
from ..models.cognitive_context import CognitiveContext, SourceType
from ..schemas.cognitive import (
    CognitiveSessionCreate,
    CognitiveSessionResponse,
    CognitiveQueryCreate,
    CognitiveQueryResponse,
    CognitiveQueryWithContextResponse,
    ContextSourceResponse,
    RankedSourceResponse,
    MergedContextResponse,
    ConfidenceResponse,
    InsightResponse,
    InsightsListResponse,
    ExplanationResponse,
    ExplanationsListResponse,
    GraphNode,
    GraphEdge,
    InsightGraphResponse,
    HistoryItem,
    HistoryResponse
)


class CognitiveTwinService:
    """
    Cognitive Twin Service.
    
    Convergence layer that aggregates context from all platform engines:
    - Semantic Layer
    - Timeline Replay
    - Digital Logbook
    - Knowledge Repository
    - RAG Engine
    - Predictive Maintenance
    - Root Cause Analysis
    - Agent Framework
    - Health Engine
    - Event Engine
    
    IMPORTANT:
    - ADVISORY ONLY - explains, does not act
    - NO autonomous decisions
    - NO actions or automation
    - Humans remain in control
    """
    
    def __init__(self):
        # In-memory storage
        self._sessions: Dict[str, CognitiveSession] = {}
        self._queries: Dict[str, CognitiveQuery] = {}
        self._context: Dict[str, List[CognitiveContext]] = defaultdict(list)
        
        # Session index
        self._sessions_by_asset: Dict[str, List[str]] = defaultdict(list)
        self._sessions_by_user: Dict[str, List[str]] = defaultdict(list)
    
    def create_session(self, data: CognitiveSessionCreate) -> CognitiveSession:
        """Create a new cognitive session."""
        session = CognitiveSession(
            name=data.name,
            description=data.description,
            asset_id=data.asset_id,
            user_id=data.user_id,
            query_count=0
        )
        
        self._sessions[session.id] = session
        
        # Index by asset
        if data.asset_id:
            self._sessions_by_asset[data.asset_id].append(session.id)
        
        # Index by user
        if data.user_id:
            self._sessions_by_user[data.user_id].append(session.id)
        
        return session
    
    def get_session(self, session_id: str) -> Optional[CognitiveSession]:
        """Get session by ID."""
        return self._sessions.get(session_id)
    
    def get_sessions(self, limit: int = 20) -> List[CognitiveSession]:
        """Get all sessions, sorted by creation date."""
        sessions = sorted(
            self._sessions.values(),
            key=lambda s: s.created_at,
            reverse=True
        )
        return sessions[:limit]
    
    def ask_question(
        self,
        session_id: str,
        question: str,
        asset_id: Optional[str] = None
    ) -> Tuple[CognitiveQuery, List[CognitiveContext]]:
        """
        Ask a question to the Cognitive Twin.
        
        Retrieves context from all platform engines and generates
        an explanation based on deterministic templates.
        """
        # Get or create session
        session = self._sessions.get(session_id)
        if not session:
            session = self.create_session(CognitiveSessionCreate(
                name=f"Session {len(self._sessions) + 1}",
                asset_id=asset_id
            ))
        
        # Create query
        query = CognitiveQuery(
            session_id=session.id,
            question=question
        )
        
        # Retrieve context from all sources
        contexts = self.retrieve_context(question, asset_id or session.asset_id)
        
        # Add context to query
        for ctx in contexts:
            ctx.query_id = query.id
            self._context[query.id].append(ctx)
        
        # Calculate confidence
        confidence, _ = self.calculate_confidence(contexts)
        query.confidence = confidence
        
        # Generate answer and explanation
        answer, explanation = self.generate_answer(question, contexts)
        query.answer = answer
        query.explanation = explanation
        
        # Store query
        self._queries[query.id] = query
        
        # Update session
        session.increment_query_count()
        session.context_summary = self.summarize_context(contexts)
        
        return query, contexts
    
    def retrieve_context(
        self,
        question: str,
        asset_id: Optional[str] = None
    ) -> List[CognitiveContext]:
        """
        Retrieve context from all platform engines.
        
        This is a deterministic retrieval process:
        - Semantic layer for entity relationships
        - Timeline for historical events
        - Logbook for operational notes
        - Knowledge repository for documented information
        - RAG for similar queries
        - Predictive maintenance for health predictions
        - Root cause analysis for failure explanations
        """
        contexts = []
        
        # Semantic Layer context
        semantic = self._get_semantic_context(question, asset_id)
        contexts.extend(semantic)
        
        # Timeline context
        timeline = self._get_timeline_context(question, asset_id)
        contexts.extend(timeline)
        
        # Logbook context
        logbook = self._get_logbook_context(question, asset_id)
        contexts.extend(logbook)
        
        # Knowledge context
        knowledge = self._get_knowledge_context(question)
        contexts.extend(knowledge)
        
        # RAG context
        rag = self._get_rag_context(question, asset_id)
        contexts.extend(rag)
        
        # Prediction context
        prediction = self._get_prediction_context(asset_id)
        contexts.extend(prediction)
        
        # Root cause context
        root_cause = self._get_root_cause_context(asset_id)
        contexts.extend(root_cause)
        
        # Agent context
        agent = self._get_agent_context(asset_id)
        contexts.extend(agent)
        
        # Health context
        health = self._get_health_context(asset_id)
        contexts.extend(health)
        
        # Event context
        events = self._get_event_context(question, asset_id)
        contexts.extend(events)
        
        # Rank and merge
        contexts = self.merge_context(contexts)
        contexts = self.rank_sources(contexts)
        
        return contexts
    
    def merge_context(
        self,
        contexts: List[CognitiveContext]
    ) -> List[CognitiveContext]:
        """Merge contexts from the same source type."""
        merged: Dict[str, List[CognitiveContext]] = defaultdict(list)
        
        for ctx in contexts:
            key = ctx.source_type.value if isinstance(ctx.source_type, SourceType) else ctx.source_type
            merged[key].append(ctx)
        
        result = []
        for source_type, ctxs in merged.items():
            # Combine weights
            total_weight = sum(c.weight for c in ctxs)
            avg_relevance = sum(c.relevance_score or 0 for c in ctxs) / len(ctxs) if ctxs else 0
            
            # Use highest relevance context as base
            base = max(ctxs, key=lambda c: c.relevance_score or 0)
            
            merged_ctx = CognitiveContext(
                query_id=base.query_id,
                source_type=SourceType(base.source_type.value) if isinstance(base.source_type, SourceType) else base.source_type,
                reference_id=base.reference_id,
                weight=min(total_weight, 1.0),
                summary=base.summary,
                detail=f"Merged {len(ctxs)} contexts from {source_type}",
                relevance_score=avg_relevance
            )
            result.append(merged_ctx)
        
        return result
    
    def rank_sources(
        self,
        contexts: List[CognitiveContext]
    ) -> List[CognitiveContext]:
        """Rank context sources by weight and relevance."""
        return sorted(
            contexts,
            key=lambda c: (c.weight, c.relevance_score or 0),
            reverse=True
        )
    
    def calculate_confidence(
        self,
        contexts: List[CognitiveContext]
    ) -> Tuple[float, ConfidenceResponse]:
        """
        Calculate confidence from context metrics.
        
        Formula:
        - Coverage: up to 40%
        - Weight: up to 30%
        - Diversity: up to 15%
        - Relevance: up to 15%
        """
        if not contexts:
            return 0.0, ConfidenceResponse(
                overall_confidence=0.0,
                coverage_score=0.0,
                weight_score=0.0,
                diversity_score=0.0,
                relevance_score=0.0,
                context_count=0,
                unique_sources=0
            )
        
        context_count = len(contexts)
        avg_weight = sum(c.weight for c in contexts) / context_count
        unique_sources = len(set(
            c.source_type.value if isinstance(c.source_type, SourceType) else c.source_type
            for c in contexts
        ))
        avg_relevance = sum(c.relevance_score or 0 for c in contexts) / context_count
        
        # Coverage: more context = higher confidence
        coverage_score = min(context_count * 0.05, 0.4)
        
        # Weight: higher weights = higher confidence
        weight_score = min(avg_weight * 0.3, 0.3)
        
        # Diversity: more source types = higher confidence
        diversity_score = min(unique_sources * 0.05, 0.15)
        
        # Relevance: higher relevance = higher confidence
        relevance_score = min(avg_relevance * 0.15, 0.15)
        
        overall = coverage_score + weight_score + diversity_score + relevance_score
        overall = max(0, min(1, overall))
        
        confidence = ConfidenceResponse(
            overall_confidence=overall,
            coverage_score=coverage_score,
            weight_score=weight_score,
            diversity_score=diversity_score,
            relevance_score=relevance_score,
            context_count=context_count,
            unique_sources=unique_sources
        )
        
        return overall, confidence
    
    def generate_answer(
        self,
        question: str,
        contexts: List[CognitiveContext]
    ) -> Tuple[str, str]:
        """
        Generate answer from context using deterministic templates.
        
        NO autonomous reasoning, NO LLM.
        """
        if not contexts:
            return (
                "I don't have enough context to answer this question.",
                "No relevant information found in platform engines."
            )
        
        # Build explanation from contexts
        sources = self._summarize_sources(contexts)
        
        # Use template-based answer
        answer = f"Based on analysis of {len(contexts)} context sources: {sources}"
        
        explanation = self.generate_explanation(question, contexts)
        
        return answer, explanation
    
    def generate_explanation(
        self,
        question: str,
        contexts: List[CognitiveContext]
    ) -> str:
        """Generate explanation from context."""
        if not contexts:
            return "No context available for explanation."
        
        # Group by source type
        by_source = defaultdict(list)
        for ctx in contexts:
            st = ctx.source_type.value if isinstance(ctx.source_type, SourceType) else ctx.source_type
            by_source[st].append(ctx)
        
        lines = ["This explanation is based on the following context sources:"]
        
        for source_type, ctxs in sorted(by_source.items()):
            summaries = [c.summary[:80] + "..." if len(c.summary) > 80 else c.summary for c in ctxs[:2]]
            lines.append(f"\n{source_type.upper()}:")
            for s in summaries:
                lines.append(f"  - {s}")
        
        return "\n".join(lines)
    
    def _summarize_sources(self, contexts: List[CognitiveContext]) -> str:
        """Summarize context sources."""
        by_source = defaultdict(list)
        for ctx in contexts:
            st = ctx.source_type.value if isinstance(ctx.source_type, SourceType) else ctx.source_type
            by_source[st].append(ctx)
        
        parts = []
        for source, ctxs in sorted(by_source.items(), key=lambda x: -len(x[1])):
            parts.append(f"{len(ctxs)} from {source}")
        
        return ", ".join(parts)
    
    # Context retrieval methods (simulated)
    def _get_semantic_context(self, question: str, asset_id: Optional[str]) -> List[CognitiveContext]:
        return self._simulate_context(SourceType.SEMANTIC, question, asset_id, 2)
    
    def _get_timeline_context(self, question: str, asset_id: Optional[str]) -> List[CognitiveContext]:
        return self._simulate_context(SourceType.TIMELINE, question, asset_id, 2)
    
    def _get_logbook_context(self, question: str, asset_id: Optional[str]) -> List[CognitiveContext]:
        return self._simulate_context(SourceType.LOGBOOK, question, asset_id, 1)
    
    def _get_knowledge_context(self, question: str) -> List[CognitiveContext]:
        return self._simulate_context(SourceType.KNOWLEDGE, question, None, 1)
    
    def _get_rag_context(self, question: str, asset_id: Optional[str]) -> List[CognitiveContext]:
        return self._simulate_context(SourceType.RAG, question, asset_id, 2)
    
    def _get_prediction_context(self, asset_id: Optional[str]) -> List[CognitiveContext]:
        if not asset_id:
            return []
        return [CognitiveContext(
            source_type=SourceType.PREDICTION,
            weight=0.6,
            summary="Predicted health: 85% with moderate failure risk",
            relevance_score=0.7
        )]
    
    def _get_root_cause_context(self, asset_id: Optional[str]) -> List[CognitiveContext]:
        if not asset_id:
            return []
        return [CognitiveContext(
            source_type=SourceType.ROOT_CAUSE,
            weight=0.5,
            summary="Root cause identified: measurement anomalies in past 30 days",
            relevance_score=0.6
        )]
    
    def _get_agent_context(self, asset_id: Optional[str]) -> List[CognitiveContext]:
        if not asset_id:
            return []
        return [CognitiveContext(
            source_type=SourceType.AGENT,
            weight=0.4,
            summary="Diagnostic agent completed analysis - pending human review",
            relevance_score=0.5
        )]
    
    def _get_health_context(self, asset_id: Optional[str]) -> List[CognitiveContext]:
        if not asset_id:
            return []
        return [CognitiveContext(
            source_type=SourceType.HEALTH,
            weight=0.7,
            summary="Current health score: 78%, trending downward",
            relevance_score=0.8
        )]
    
    def _get_event_context(self, question: str, asset_id: Optional[str]) -> List[CognitiveContext]:
        return self._simulate_context(SourceType.EVENT, question, asset_id, 1)
    
    def _simulate_context(
        self,
        source_type: SourceType,
        question: str,
        asset_id: Optional[str],
        count: int
    ) -> List[CognitiveContext]:
        """Simulate context retrieval."""
        contexts = []
        for i in range(count):
            weight = 0.3 + (i * 0.2)
            contexts.append(CognitiveContext(
                source_type=source_type,
                weight=min(weight, 1.0),
                summary=f"Context from {source_type.value} for: {question[:50]}...",
                relevance_score=0.5 + (i * 0.1)
            ))
        return contexts
    
    def summarize_context(self, contexts: List[CognitiveContext]) -> str:
        """Summarize context for session."""
        if not contexts:
            return "No context"
        
        sources = [c.source_type.value if isinstance(c.source_type, SourceType) else c.source_type for c in contexts]
        unique = set(sources)
        
        return f"Context from {len(unique)} sources: {', '.join(sorted(unique))}"
    
    def get_query(self, query_id: str) -> Optional[CognitiveQuery]:
        """Get query by ID."""
        return self._queries.get(query_id)
    
    def get_query_context(self, query_id: str) -> List[CognitiveContext]:
        """Get context for a query."""
        return self._context.get(query_id, [])
    
    def get_session_history(self, session_id: str) -> List[HistoryItem]:
        """Get query history for a session."""
        queries = [
            q for q in self._queries.values()
            if q.session_id == session_id
        ]
        queries.sort(key=lambda q: q.created_at, reverse=True)
        
        return [
            HistoryItem(
                query_id=q.id,
                question=q.question,
                answer=q.answer,
                confidence=q.confidence,
                context_count=len(self._context.get(q.id, [])),
                created_at=q.created_at
            )
            for q in queries
        ]
    
    def get_insights(self, limit: int = 20) -> InsightsListResponse:
        """Get recent insights."""
        all_contexts = []
        for contexts in self._context.values():
            all_contexts.extend(contexts)
        
        # Rank by relevance
        ranked = sorted(all_contexts, key=lambda c: c.relevance_score or 0, reverse=True)
        
        insights = [
            InsightResponse(
                source_type=c.source_type.value if isinstance(c.source_type, SourceType) else c.source_type,
                insight=c.summary[:200],
                confidence=c.weight,
                evidence=[c.detail or c.summary]
            )
            for c in ranked[:limit]
        ]
        
        return InsightsListResponse(insights=insights, total=len(insights))
    
    def get_explanations(self, limit: int = 20) -> ExplanationsListResponse:
        """Get recent explanations."""
        explanations = []
        
        for query in sorted(self._queries.values(), key=lambda q: q.created_at, reverse=True)[:limit]:
            if query.explanation:
                explanations.append(ExplanationResponse(
                    topic=query.question[:50],
                    explanation=query.explanation,
                    confidence=query.confidence,
                    sources=[c.source_type.value for c in self._context.get(query.id, [])],
                    related_context=[
                        ContextSourceResponse(
                            id=c.id,
                            source_type=c.source_type.value if isinstance(c.source_type, SourceType) else c.source_type,
                            weight=c.weight,
                            summary=c.summary,
                            relevance_score=c.relevance_score,
                            created_at=c.created_at
                        )
                        for c in self._context.get(query.id, [])[:5]
                    ]
                ))
        
        return ExplanationsListResponse(explanations=explanations, total=len(explanations))
    
    def get_confidence(self, query_id: str) -> Optional[ConfidenceResponse]:
        """Get confidence for a query."""
        query = self._queries.get(query_id)
        if not query:
            return None
        
        contexts = self._context.get(query_id, [])
        _, confidence = self.calculate_confidence(contexts)
        
        return confidence
    
    def build_insight_graph(self, query_id: str) -> InsightGraphResponse:
        """Build insight graph for a query."""
        contexts = self._context.get(query_id, [])
        
        nodes = []
        edges = []
        
        # Central node
        nodes.append(GraphNode(
            id="center",
            label="Query",
            type="query",
            properties={}
        ))
        
        # Source nodes
        for ctx in contexts:
            source_type = ctx.source_type.value if isinstance(ctx.source_type, SourceType) else ctx.source_type
            node_id = f"source_{source_type}"
            
            if not any(n.id == node_id for n in nodes):
                nodes.append(GraphNode(
                    id=node_id,
                    label=source_type,
                    type="source",
                    properties={"weight": ctx.weight}
                ))
                
                edges.append(GraphEdge(
                    source="center",
                    target=node_id,
                    label="provides context",
                    weight=ctx.weight
                ))
        
        return InsightGraphResponse(nodes=nodes, edges=edges)


# Global instance
cognitive_twin_service = CognitiveTwinService()
