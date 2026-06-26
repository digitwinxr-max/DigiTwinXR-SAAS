"""
Reasoning Session Engine

Human-driven reasoning session management.
NO autonomous execution - human approval required for all actions.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4


class SessionStatus(str, Enum):
    """Session status."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    """Reasoning step status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    SKIPPED = "skipped"


@dataclass
class ReasoningStep:
    """A single reasoning step."""
    step_id: str
    description: str
    status: StepStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    evidence: List[str] = field(default_factory=list)
    conclusion: Optional[str] = None
    confidence: Optional[float] = None
    requires_approval: bool = True


@dataclass
class InferenceRecord:
    """Record of an inference."""
    record_id: str
    premise: str
    conclusion: str
    confidence: float
    timestamp: datetime
    source: str = "inference"


@dataclass
class ConversationContext:
    """Conversation context for a session."""
    session_id: str
    user_intent: str
    entities: List[Dict[str, Any]] = field(default_factory=list)
    relevant_history: List[str] = field(default_factory=list)
    context_summary: Optional[str] = None


@dataclass
class SessionState:
    """State of a reasoning session."""
    session_id: str
    status: SessionStatus
    created_at: datetime
    updated_at: datetime
    current_step: int
    steps: List[ReasoningStep]
    inference_history: List[InferenceRecord]
    context: ConversationContext
    final_conclusion: Optional[str] = None
    confidence: Optional[float] = None


class ReasoningSession:
    """
    Reasoning session for human-driven inference.
    
    Key constraints:
    - Human approval required for all steps
    - No autonomous execution
    """
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or str(uuid4())
        self._state: Optional[SessionState] = None
    
    def create(self, user_intent: str, entities: Optional[List[Dict[str, Any]]] = None) -> SessionState:
        """Create a new reasoning session."""
        self._state = SessionState(
            session_id=self.session_id,
            status=SessionStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            current_step=0,
            steps=[],
            inference_history=[],
            context=ConversationContext(
                session_id=self.session_id,
                user_intent=user_intent,
                entities=entities or [],
                relevant_history=[],
                context_summary=None
            )
        )
        return self._state
    
    def get_state(self) -> Optional[SessionState]:
        """Get current session state."""
        return self._state
    
    def add_step(self, description: str, evidence: Optional[List[str]] = None,
                 conclusion: Optional[str] = None, confidence: Optional[float] = None) -> ReasoningStep:
        """Add a reasoning step."""
        if not self._state:
            raise ValueError("Session not created")
        
        step = ReasoningStep(
            step_id=str(uuid4()),
            description=description,
            status=StepStatus.PENDING,
            created_at=datetime.now(),
            evidence=evidence or [],
            conclusion=conclusion,
            confidence=confidence,
            requires_approval=True
        )
        
        self._state.steps.append(step)
        self._state.current_step = len(self._state.steps)
        self._state.updated_at = datetime.now()
        return step
    
    def approve_step(self, step_id: str) -> ReasoningStep:
        """Approve a reasoning step."""
        if not self._state:
            raise ValueError("Session not created")
        step = self._find_step(step_id)
        if not step:
            raise ValueError(f"Step {step_id} not found")
        step.status = StepStatus.COMPLETED
        step.completed_at = datetime.now()
        self._state.updated_at = datetime.now()
        return step
    
    def reject_step(self, step_id: str) -> ReasoningStep:
        """Reject a reasoning step."""
        if not self._state:
            raise ValueError("Session not created")
        step = self._find_step(step_id)
        if not step:
            raise ValueError(f"Step {step_id} not found")
        step.status = StepStatus.REJECTED
        step.completed_at = datetime.now()
        self._state.updated_at = datetime.now()
        return step
    
    def add_inference(self, premise: str, conclusion: str, confidence: float, source: str = "inference") -> InferenceRecord:
        """Add an inference record."""
        if not self._state:
            raise ValueError("Session not created")
        record = InferenceRecord(
            record_id=str(uuid4()),
            premise=premise,
            conclusion=conclusion,
            confidence=confidence,
            timestamp=datetime.now(),
            source=source
        )
        self._state.inference_history.append(record)
        self._state.updated_at = datetime.now()
        return record
    
    def set_conclusion(self, conclusion: str, confidence: float) -> None:
        """Set the final conclusion."""
        if not self._state:
            raise ValueError("Session not created")
        self._state.final_conclusion = conclusion
        self._state.confidence = confidence
        self._state.status = SessionStatus.COMPLETED
        self._state.updated_at = datetime.now()
    
    def _find_step(self, step_id: str) -> Optional[ReasoningStep]:
        """Find a step by ID."""
        if not self._state:
            return None
        for step in self._state.steps:
            if step.step_id == step_id:
                return step
        return None


class ReasoningSessionManager:
    """Manager for reasoning sessions."""
    
    def __init__(self):
        self._sessions: Dict[str, ReasoningSession] = {}
    
    def create_session(self, user_intent: str, entities: Optional[List[Dict[str, Any]]] = None) -> ReasoningSession:
        """Create a new reasoning session."""
        session = ReasoningSession()
        session.create(user_intent, entities)
        self._sessions[session.session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[ReasoningSession]:
        """Get a session by ID."""
        return self._sessions.get(session_id)
    
    def list_sessions(self) -> List[SessionState]:
        """List all sessions."""
        return [s.get_state() for s in self._sessions.values() if s.get_state() is not None]
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False


_manager: Optional[ReasoningSessionManager] = None


def get_reasoning_manager() -> ReasoningSessionManager:
    """Get or create reasoning manager singleton."""
    global _manager
    if _manager is None:
        _manager = ReasoningSessionManager()
    return _manager
