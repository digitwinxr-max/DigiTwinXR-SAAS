"""
Template LLM Provider

Deterministic template-based response generator.
This is a placeholder until LLM integration.
"""

from typing import List, Dict, Any
from collections import defaultdict

from .llm_provider import LLMProvider


class TemplateProvider(LLMProvider):
    """
    Template-based LLM Provider.
    
    Uses deterministic templates to generate responses.
    This is a placeholder until LLM integration.
    
    NOTE: This is NOT OpenAI, Claude, or any real LLM.
    """
    
    def __init__(self):
        self._templates = self._build_templates()
    
    def name(self) -> str:
        """Return provider name."""
        return "template"
    
    def is_available(self) -> bool:
        """Template provider is always available."""
        return True
    
    def generate(
        self,
        context: List[Dict[str, Any]],
        query: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate response using templates.
        
        Args:
            context: List of context chunks
            query: User query
            
        Returns:
            Dict with answer, confidence, and sources
        """
        query_lower = query.lower()
        sources = [c.get("source_id") for c in context if c.get("source_id")]
        
        # Determine query type
        query_type = self._classify_query(query_lower)
        
        # Build answer based on query type and context
        answer = self._build_answer(query_type, query_lower, context)
        
        # Calculate confidence based on context coverage
        confidence = self._calculate_confidence(query_type, context)
        
        return {
            "answer": answer,
            "confidence": confidence,
            "sources": sources,
            "model": self.name()
        }
    
    def _classify_query(self, query: str) -> str:
        """Classify query type."""
        if any(word in query for word in ["health", "status", "condition"]):
            return "health"
        if any(word in query for word in ["event", "alert", "warning", "critical"]):
            return "events"
        if any(word in query for word in ["timeline", "history", "before", "after"]):
            return "timeline"
        if any(word in query for word in ["logbook", "note", "observation", "operator"]):
            return "logbook"
        if any(word in query for word in ["knowledge", "document", "sop", "manual", "lesson"]):
            return "knowledge"
        if any(word in query for word in ["semantic", "relationship", "related", "dependency"]):
            return "semantic"
        if any(word in query for word in ["asset", "substation", "transformer", "sensor"]):
            return "asset"
        return "general"
    
    def _build_answer(
        self,
        query_type: str,
        query: str,
        context: List[Dict[str, Any]]
    ) -> str:
        """Build answer from context."""
        # Group context by source type
        by_type = defaultdict(list)
        for chunk in context:
            by_type[chunk.get("source_type", "unknown")].append(chunk)
        
        parts = []
        
        if query_type == "health" and by_type.get("health"):
            parts.append(self._summarize_health(by_type["health"]))
        elif query_type == "events" and by_type.get("event"):
            parts.append(self._summarize_events(by_type["event"]))
        elif query_type == "timeline" and by_type.get("timeline"):
            parts.append(self._summarize_timeline(by_type["timeline"]))
        elif query_type == "logbook" and by_type.get("logbook"):
            parts.append(self._summarize_logbook(by_type["logbook"]))
        elif query_type == "knowledge" and by_type.get("knowledge"):
            parts.append(self._summarize_knowledge(by_type["knowledge"]))
        elif query_type == "semantic" and by_type.get("semantic"):
            parts.append(self._summarize_semantic(by_type["semantic"]))
        elif query_type == "asset" and by_type.get("asset"):
            parts.append(self._summarize_asset(by_type["asset"]))
        
        # If no specific match, provide general summary
        if not parts:
            parts.append(self._general_summary(context))
        
        return " ".join(parts)
    
    def _summarize_health(self, chunks: List[Dict[str, Any]]) -> str:
        """Summarize health context."""
        if not chunks:
            return "No health information available."
        
        scores = []
        statuses = []
        for chunk in chunks:
            content = chunk.get("content", "")
            if "health_score" in content or "95" in content or "90" in content:
                scores.append(content)
            if "status" in content.lower():
                statuses.append(content)
        
        parts = ["Based on Health Engine data:"]
        
        if scores:
            parts.append(f"Health score information: {scores[0][:100]}")
        if statuses:
            parts.append(f"Status: {statuses[0][:100]}")
        
        return " ".join(parts)
    
    def _summarize_events(self, chunks: List[Dict[str, Any]]) -> str:
        """Summarize events context."""
        if not chunks:
            return "No events found."
        
        critical = sum(1 for c in chunks if "critical" in c.get("content", "").lower())
        warning = sum(1 for c in chunks if "warning" in c.get("content", "").lower())
        
        parts = [f"Found {len(chunks)} event(s):"]
        if critical > 0:
            parts.append(f"{critical} critical, {warning} warning.")
        else:
            parts.append(f"{warning} warning events.")
        
        return " ".join(parts)
    
    def _summarize_timeline(self, chunks: List[Dict[str, Any]]) -> str:
        """Summarize timeline context."""
        if not chunks:
            return "No timeline data available."
        
        parts = [f"Timeline contains {len(chunks)} snapshot(s):"]
        
        for chunk in chunks[:3]:
            content = chunk.get("content", "")[:80]
            if content:
                parts.append(f"- {content}...")
        
        return " ".join(parts)
    
    def _summarize_logbook(self, chunks: List[Dict[str, Any]]) -> str:
        """Summarize logbook context."""
        if not chunks:
            return "No logbook entries found."
        
        parts = [f"Found {len(chunks)} logbook entry/entries:"]
        
        for chunk in chunks[:2]:
            content = chunk.get("content", "")[:80]
            if content:
                parts.append(f"- {content}...")
        
        return " ".join(parts)
    
    def _summarize_knowledge(self, chunks: List[Dict[str, Any]]) -> str:
        """Summarize knowledge context."""
        if not chunks:
            return "No related documents found."
        
        types = defaultdict(int)
        for chunk in chunks:
            content = chunk.get("content", "").lower()
            for doc_type in ["manual", "sop", "troubleshooting", "lesson"]:
                if doc_type in content:
                    types[doc_type] += 1
        
        parts = [f"Found {len(chunks)} related document(s):"]
        for dtype, count in types.items():
            parts.append(f"{count} {dtype}(s)")
        
        return " ".join(parts)
    
    def _summarize_semantic(self, chunks: List[Dict[str, Any]]) -> str:
        """Summarize semantic context."""
        if not chunks:
            return "No semantic relationships found."
        
        parts = [f"Found {len(chunks)} relationship(s):"]
        
        for chunk in chunks[:3]:
            content = chunk.get("content", "")[:60]
            if content:
                parts.append(f"- {content}...")
        
        return " ".join(parts)
    
    def _summarize_asset(self, chunks: List[Dict[str, Any]]) -> str:
        """Summarize asset context."""
        if not chunks:
            return "No asset information available."
        
        content = chunks[0].get("content", "")[:150]
        return f"Asset information: {content}"
    
    def _general_summary(self, context: List[Dict[str, Any]]) -> str:
        """Provide general summary."""
        if not context:
            return "I don't have enough context to answer this question. Please provide more specific query or entity context."
        
        types = defaultdict(int)
        for chunk in context:
            types[chunk.get("source_type", "unknown")] += 1
        
        parts = ["Based on available context:"]
        for stype, count in types.items():
            parts.append(f"{count} {stype} source(s)")
        
        return " ".join(parts)
    
    def _calculate_confidence(self, query_type: str, context: List[Dict[str, Any]]) -> float:
        """Calculate confidence score."""
        if not context:
            return 0.1
        
        # Check if we have relevant context for query type
        by_type = defaultdict(int)
        for chunk in context:
            by_type[chunk.get("source_type", "unknown")] += 1
        
        # Base confidence from context amount
        base_confidence = min(len(context) / 5.0, 0.8)
        
        # Boost if relevant context exists
        type_mapping = {
            "health": "health",
            "events": "event",
            "timeline": "timeline",
            "logbook": "logbook",
            "knowledge": "knowledge",
            "semantic": "semantic",
            "asset": "asset"
        }
        
        relevant_type = type_mapping.get(query_type)
        if relevant_type and by_type.get(relevant_type, 0) > 0:
            base_confidence = min(base_confidence + 0.15, 0.95)
        
        return round(base_confidence, 2)
    
    def _build_templates(self) -> Dict[str, str]:
        """Build response templates."""
        return {
            "health": "Based on Health Engine data: {health_summary}",
            "events": "Based on Event Engine data: {events_summary}",
            "timeline": "Based on Timeline Engine data: {timeline_summary}",
            "logbook": "Based on Logbook Engine data: {logbook_summary}",
            "knowledge": "Based on Knowledge Repository data: {knowledge_summary}",
            "semantic": "Based on Semantic Layer data: {semantic_summary}",
            "asset": "Based on Asset Engine data: {asset_summary}",
            "general": "Based on available context: {general_summary}"
        }
