"""Learning Feedback Service"""
from typing import Optional, Any
from datetime import datetime


class FeedbackService:
    """
    Feedback processing service.
    """
    
    def __init__(self, memory=None):
        self._memory = memory
    
    def process_feedback(
        self,
        feedback_id: str,
        source: str,
        target_type: str,
        target_id: str,
        feedback_type: str,
        rating: Optional[float] = None,
        comment: Optional[str] = None,
        corrected_value: Optional[Any] = None
    ):
        """Process human feedback."""
        from .memory import HumanFeedback, get_learning_memory
        
        memory = self._memory or get_learning_memory()
        
        feedback = HumanFeedback(
            feedback_id=feedback_id,
            timestamp=datetime.now(),
            source=source,
            target_type=target_type,
            target_id=target_id,
            feedback_type=feedback_type,
            rating=rating,
            comment=comment,
            corrected_value=corrected_value
        )
        
        return memory.add_feedback(feedback)


_service: Optional[FeedbackService] = None


def get_feedback_service() -> FeedbackService:
    """Get or create feedback service singleton."""
    global _service
    if _service is None:
        _service = FeedbackService()
    return _service
