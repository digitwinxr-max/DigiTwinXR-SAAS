"""
Learning Memory

Learning memory and feedback records.
NO self modification, NO self coding.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class HumanFeedback:
    """Human feedback record."""
    feedback_id: str
    timestamp: datetime
    source: str
    target_type: str
    target_id: str
    feedback_type: str
    rating: Optional[float]
    comment: Optional[str]
    corrected_value: Optional[Any]


@dataclass
class ConfidenceUpdate:
    """Confidence update record."""
    update_id: str
    timestamp: datetime
    entity_type: str
    entity_id: str
    old_confidence: float
    new_confidence: float
    reason: str
    approved_by: Optional[str]


@dataclass
class KnowledgeHistory:
    """Knowledge history record."""
    history_id: str
    timestamp: datetime
    action: str
    entity_type: str
    entity_id: str
    old_value: Optional[Any]
    new_value: Optional[Any]
    source: str


class LearningMemory:
    """
    Learning memory for the digital twin.
    
    Features:
    - Human feedback storage
    - Confidence updates
    - Knowledge history
    
    LIMITATIONS:
    - NO self modification
    - NO self coding
    """
    
    def __init__(self):
        self._feedback: Dict[str, HumanFeedback] = {}
        self._confidence_updates: Dict[str, ConfidenceUpdate] = {}
        self._history: Dict[str, KnowledgeHistory] = {}
    
    def add_feedback(self, feedback: HumanFeedback) -> HumanFeedback:
        """Add human feedback."""
        self._feedback[feedback.feedback_id] = feedback
        return feedback
    
    def get_feedback(self, feedback_id: str) -> Optional[HumanFeedback]:
        """Get feedback by ID."""
        return self._feedback.get(feedback_id)
    
    def list_feedback(
        self,
        target_id: Optional[str] = None,
        feedback_type: Optional[str] = None
    ) -> List[HumanFeedback]:
        """List feedback with filters."""
        feedback = list(self._feedback.values())
        if target_id:
            feedback = [f for f in feedback if f.target_id == target_id]
        if feedback_type:
            feedback = [f for f in feedback if f.feedback_type == feedback_type]
        return sorted(feedback, key=lambda f: f.timestamp, reverse=True)
    
    def add_confidence_update(self, update: ConfidenceUpdate) -> ConfidenceUpdate:
        """Add confidence update."""
        self._confidence_updates[update.update_id] = update
        return update
    
    def get_confidence(self, entity_type: str, entity_id: str) -> Optional[float]:
        """Get current confidence for an entity."""
        updates = [
            u for u in self._confidence_updates.values()
            if u.entity_type == entity_type and u.entity_id == entity_id
        ]
        if updates:
            latest = max(updates, key=lambda u: u.timestamp)
            return latest.new_confidence
        return None
    
    def add_history(self, history: KnowledgeHistory) -> KnowledgeHistory:
        """Add knowledge history."""
        self._history[history.history_id] = history
        return history
    
    def get_history(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None
    ) -> List[KnowledgeHistory]:
        """Get knowledge history."""
        history = list(self._history.values())
        if entity_type:
            history = [h for h in history if h.entity_type == entity_type]
        if entity_id:
            history = [h for h in history if h.entity_id == entity_id]
        return sorted(history, key=lambda h: h.timestamp, reverse=True)


_memory: Optional[LearningMemory] = None


def get_learning_memory() -> LearningMemory:
    """Get or create learning memory singleton."""
    global _memory
    if _memory is None:
        _memory = LearningMemory()
    return _memory
