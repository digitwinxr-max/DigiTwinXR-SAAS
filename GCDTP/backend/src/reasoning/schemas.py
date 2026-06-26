"""
Reasoning Schemas

Cross-domain reasoning schemas.
Human-supervised only.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class DomainSource(str, Enum):
    """Data source domains."""
    RAG = "rag"
    GRAPH = "graph"
    TIMELINE = "timeline"
    VIDEO = "video"
    EVENTS = "events"
    SENSORS = "sensors"


@dataclass
class SourceQuery:
    """Query for a specific domain."""
    domain: DomainSource
    query: str
    filters: Dict[str, Any] = field(default_factory=dict)
    limit: int = 10


@dataclass
class DomainResult:
    """Result from a domain query."""
    domain: DomainSource
    data: List[Dict[str, Any]]
    relevance_scores: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FusionQuery:
    """Query for cross-domain reasoning."""
    query: str
    domains: List[DomainSource]
    max_results_per_domain: int = 10


@dataclass
class FusedResult:
    """Fused result from multiple domains."""
    query: str
    results_by_domain: Dict[DomainSource, DomainResult]
    fused_context: str
    confidence: float
    requires_review: bool = True
