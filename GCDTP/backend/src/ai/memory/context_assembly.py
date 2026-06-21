"""
Context Assembly Engine

Multi-source context assembly and fusion.
Deterministic - NO AI execution.
"""

from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict
import hashlib


class SourceType(str, Enum):
    """Context source types."""
    RAG = "rag"
    COGNITIVE_GRAPH = "cognitive_graph"
    TIMELINE = "timeline"
    EVENTS = "events"
    ASSETS = "assets"
    SENSORS = "sensors"
    DOCUMENTS = "documents"
    USER_INPUT = "user_input"


class ConflictResolution(str, Enum):
    """Conflict resolution strategies."""
    LATEST = "latest"
    MOST_RELEVANT = "most_relevant"
    MAJORITY = "majority"
    MANUAL = "manual"


@dataclass
class ContextSource:
    """Context source information."""
    source_type: SourceType
    source_id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    relevance_score: float = 1.0


@dataclass
class ContextItem:
    """Assembled context item."""
    key: str
    value: Any
    sources: List[ContextSource]
    confidence: float
    conflicts: List[ContextSource] = field(default_factory=list)


@dataclass
class AssembledContext:
    """Assembled context result."""
    items: List[ContextItem]
    assembled_at: datetime
    sources_used: Set[SourceType]
    conflicts_resolved: int
    conflicts_unresolved: List[ContextItem] = field(default_factory=list)
    raw_context: Dict[str, List[ContextSource]] = field(default_factory=dict)


@dataclass
class AssemblyConfig:
    """Context assembly configuration."""
    sources: List[SourceType]
    weights: Dict[SourceType, float]
    conflict_resolution: ConflictResolution
    max_context_items: int = 20
    min_relevance_score: float = 0.3
    merge_similar: bool = True
    similarity_threshold: float = 0.8


class ContextAssemblyEngine:
    """
    Context Assembly Engine.
    
    Assembles context from multiple sources deterministically.
    NO AI inference - only deterministic merging.
    """
    
    def __init__(self):
        self.weights: Dict[SourceType, float] = {
            SourceType.USER_INPUT: 1.0,
            SourceType.COGNITIVE_GRAPH: 0.9,
            SourceType.RAG: 0.8,
            SourceType.TIMELINE: 0.7,
            SourceType.EVENTS: 0.7,
            SourceType.ASSETS: 0.6,
            SourceType.SENSORS: 0.6,
            SourceType.DOCUMENTS: 0.5,
        }
    
    def assemble(
        self,
        sources: List[ContextSource],
        config: Optional[AssemblyConfig] = None
    ) -> AssembledContext:
        """
        Assemble context from multiple sources.
        
        Deterministic assembly - no AI inference.
        """
        if config is None:
            config = AssemblyConfig(
                sources=list(self.weights.keys()),
                weights=self.weights,
                conflict_resolution=ConflictResolution.LATEST
            )
        
        # Group sources by key
        keyed_sources: Dict[str, List[ContextSource]] = defaultdict(list)
        
        for source in sources:
            key = self._normalize_key(source.content)
            keyed_sources[key].append(source)
        
        # Process each key
        items: List[ContextItem] = []
        conflicts_unresolved: List[ContextItem] = []
        raw_context: Dict[str, List[ContextSource]] = dict(keyed_sources)
        
        for key, source_list in keyed_sources.items():
            # Calculate weighted relevance
            weighted_score = self._calculate_weighted_score(
                source_list,
                config.weights
            )
            
            # Check if meets minimum threshold
            if weighted_score < config.min_relevance_score:
                continue
            
            # Check for conflicts
            unique_values = self._find_unique_values(source_list)
            
            item = ContextItem(
                key=key,
                value=source_list[0].content,  # Default to first
                sources=source_list,
                confidence=weighted_score,
                conflicts=[]
            )
            
            # Resolve conflicts
            if len(unique_values) > 1:
                resolved, conflict_sources = self._resolve_conflicts(
                    source_list,
                    unique_values,
                    config.conflict_resolution
                )
                
                if resolved is not None:
                    item.value = resolved
                else:
                    conflicts_unresolved.append(item)
                    item.conflicts = conflict_sources
        
            items.append(item)
        
        # Sort by confidence
        items.sort(key=lambda x: x.confidence, reverse=True)
        
        # Limit items
        if len(items) > config.max_context_items:
            items = items[:config.max_context_items]
        
        # Collect sources used
        sources_used = set(s.source_type for s in sources)
        
        return AssembledContext(
            items=items,
            assembled_at=datetime.now(),
            sources_used=sources_used,
            conflicts_resolved=len(items) - len(conflicts_unresolved),
            conflicts_unresolved=conflicts_unresolved,
            raw_context=raw_context
        )
    
    def _normalize_key(self, content: str) -> str:
        """Normalize content to create a key."""
        # Simple normalization: lowercase and hash
        normalized = content.lower().strip()
        
        # For longer content, use first N words
        words = normalized.split()
        if len(words) > 10:
            key_content = ' '.join(words[:10])
        else:
            key_content = normalized
        
        return hashlib.md5(key_content.encode()).hexdigest()[:16]
    
    def _calculate_weighted_score(
        self,
        sources: List[ContextSource],
        weights: Dict[SourceType, float]
    ) -> float:
        """Calculate weighted relevance score."""
        if not sources:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        for source in sources:
            weight = weights.get(source.source_type, 0.5)
            score = source.relevance_score * weight
            total_score += score
            total_weight += weight
        
        return total_score / len(sources) if total_weight > 0 else 0.0
    
    def _find_unique_values(
        self,
        sources: List[ContextSource]
    ) -> Dict[str, List[ContextSource]]:
        """Find unique values in sources."""
        values: Dict[str, List[ContextSource]] = defaultdict(list)
        
        for source in sources:
            values[source.content].append(source)
        
        return dict(values)
    
    def _resolve_conflicts(
        self,
        sources: List[ContextSource],
        unique_values: Dict[str, List[ContextSource]],
        strategy: ConflictResolution
    ) -> Tuple[Optional[str], List[ContextSource]]:
        """
        Resolve conflicts between sources.
        
        Deterministic resolution based on strategy.
        """
        conflict_sources: List[ContextSource] = []
        for value, srcs in unique_values.items():
            conflict_sources.extend(srcs)
        
        if strategy == ConflictResolution.LATEST:
            # Use most recent value
            most_recent = max(sources, key=lambda s: s.timestamp)
            return most_recent.content, conflict_sources
        
        elif strategy == ConflictResolution.MOST_RELEVANT:
            # Use highest relevance score
            most_relevant = max(sources, key=lambda s: s.relevance_score)
            return most_relevant.content, conflict_sources
        
        elif strategy == ConflictResolution.MAJORITY:
            # Use value with most sources
            most_common = max(
                unique_values.items(),
                key=lambda x: len(x[1])
            )
            return most_common[0], conflict_sources
        
        elif strategy == ConflictResolution.MANUAL:
            # Cannot resolve automatically
            return None, conflict_sources
        
        return sources[0].content, conflict_sources
    
    def merge_similar_items(
        self,
        items: List[ContextItem],
        threshold: float = 0.8
    ) -> List[ContextItem]:
        """
        Merge similar context items.
        
        Deterministic similarity based on content.
        """
        if not items:
            return items
        
        merged: List[ContextItem] = []
        used: Set[int] = set()
        
        for i, item in enumerate(items):
            if i in used:
                continue
            
            similar: List[ContextItem] = [item]
            
            for j, other in enumerate(items[i + 1:], start=i + 1):
                if j in used:
                    continue
                
                similarity = self._calculate_similarity(
                    item.value,
                    other.value
                )
                
                if similarity >= threshold:
                    similar.append(other)
                    used.add(j)
            
            # Merge similar items
            if len(similar) > 1:
                merged_item = self._merge_items(similar)
                merged.append(merged_item)
            else:
                merged.append(item)
            
            used.add(i)
        
        return merged
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate deterministic similarity between texts."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _merge_items(self, items: List[ContextItem]) -> ContextItem:
        """Merge multiple context items."""
        all_sources: List[ContextSource] = []
        for item in items:
            all_sources.extend(item.sources)
        
        # Use highest confidence value
        best_item = max(items, key=lambda x: x.confidence)
        
        # Average confidence
        avg_confidence = sum(i.confidence for i in items) / len(items)
        
        return ContextItem(
            key=best_item.key,
            value=best_item.value,
            sources=all_sources,
            confidence=avg_confidence,
            conflicts=[]
        )
    
    def to_context_string(
        self,
        context: AssembledContext,
        include_sources: bool = True,
        include_confidence: bool = True
    ) -> str:
        """Convert assembled context to string."""
        parts = []
        
        for item in context.items:
            if include_confidence:
                parts.append(f"[Confidence: {item.confidence:.2f}] {item.value}")
            else:
                parts.append(item.value)
            
            if include_sources:
                source_names = [s.source_type.value for s in item.sources]
                parts.append(f"  Sources: {', '.join(source_names)}")
            
            if item.conflicts:
                parts.append(f"  ⚠️ Conflicts: {len(item.conflicts)} unresolved")
        
        if context.conflicts_unresolved:
            parts.append("\n⚠️ Unresolved Conflicts:")
            for item in context.conflicts_unresolved:
                parts.append(f"  - {item.value}")
        
        return "\n".join(parts)


# Singleton instance
_engine: Optional[ContextAssemblyEngine] = None


def get_context_assembly_engine() -> ContextAssemblyEngine:
    """Get or create context assembly engine singleton."""
    global _engine
    if _engine is None:
        _engine = ContextAssemblyEngine()
    return _engine
