"""
Cross-Domain Fusion Engine

Fuses data from multiple domains.
Human-supervised only.
NO self execution.
"""

import logging
from typing import Dict, List, Optional, Any

from .schemas import (
    DomainSource,
    SourceQuery,
    DomainResult,
    FusionQuery,
    FusedResult,
)


logger = logging.getLogger(__name__)


class FusionEngine:
    """
    Cross-domain fusion engine.
    
    Fuses data from:
    - RAG
    - Graph
    - Timeline
    - Video
    - Events
    - Sensors
    
    LIMITATIONS:
    - Human supervision required
    - NO self execution
    """
    
    def __init__(self):
        self._domain_handlers: Dict[DomainSource, Any] = {}
    
    def register_domain_handler(self, domain: DomainSource, handler: Any):
        """Register a domain handler."""
        self._domain_handlers[domain] = handler
    
    def query_domain(
        self,
        domain: DomainSource,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> DomainResult:
        """
        Query a specific domain.
        
        Args:
            domain: Domain to query
            query: Query string
            filters: Optional filters
            limit: Maximum results
        
        Returns:
            DomainResult with domain data
        """
        handler = self._domain_handlers.get(domain)
        
        if handler:
            data = handler(query, filters, limit)
        else:
            # Default empty response
            data = []
        
        return DomainResult(
            domain=domain,
            data=data,
            relevance_scores=[1.0] * len(data),
            metadata={"source": domain.value}
        )
    
    def fuse(
        self,
        query: FusionQuery
    ) -> FusedResult:
        """
        Fuse results from multiple domains.
        
        Args:
            query: Fusion query with domains
        
        Returns:
            FusedResult with combined context
        """
        results_by_domain: Dict[DomainSource, DomainResult] = {}
        
        # Query each domain
        for domain in query.domains:
            result = self.query_domain(
                domain,
                query.query,
                limit=query.max_results_per_domain
            )
            results_by_domain[domain] = result
        
        # Fuse context
        fused_context = self._build_context(results_by_domain)
        
        # Calculate confidence
        confidence = self._calculate_confidence(results_by_domain)
        
        return FusedResult(
            query=query.query,
            results_by_domain=results_by_domain,
            fused_context=fused_context,
            confidence=confidence,
            requires_review=True
        )
    
    def _build_context(
        self,
        results_by_domain: Dict[DomainSource, DomainResult]
    ) -> str:
        """Build fused context string."""
        context_parts = []
        
        for domain, result in results_by_domain.items():
            if result.data:
                context_parts.append(f"[{domain.value.upper()}]")
                for item in result.data[:3]:
                    if isinstance(item, dict):
                        context_parts.append(f"  - {item.get('content', str(item))}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def _calculate_confidence(
        self,
        results_by_domain: Dict[DomainSource, DomainResult]
    ) -> float:
        """Calculate fused confidence score."""
        if not results_by_domain:
            return 0.0
        
        total = 0.0
        count = 0
        
        for result in results_by_domain.values():
            if result.relevance_scores:
                avg = sum(result.relevance_scores) / len(result.relevance_scores)
                total += avg
                count += 1
        
        return total / count if count > 0 else 0.0


# Singleton instance
_engine: Optional[FusionEngine] = None


def get_fusion_engine() -> FusionEngine:
    """Get or create fusion engine singleton."""
    global _engine
    if _engine is None:
        _engine = FusionEngine()
    return _engine
