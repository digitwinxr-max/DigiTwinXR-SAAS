"""
Human-Supervised Copilot Layer

Capabilities restricted to READ-ONLY operations.
FORBIDDEN: Execution, modification, triggering, autonomous actions.
"""

from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod


class CapabilityType(str, Enum):
    """Allowed capability types - READ ONLY."""
    ASK = "ask"
    EXPLAIN = "explain"
    SUMMARIZE = "summarize"
    RECOMMEND = "recommend"
    SEARCH = "search"


class ActionType(str, Enum):
    """Action types - ALL FORBIDDEN."""
    EXECUTE_WORKFLOW = "execute_workflow"
    CREATE_WORK_ORDER = "create_work_order"
    MODIFY_ASSET = "modify_asset"
    TRIGGER_EVENT = "trigger_event"
    SELF_HEAL = "self_heal"
    AUTONOMOUS_AGENT = "autonomous_agent"


@dataclass
class CopilotCapability:
    """A copilot capability."""
    capability_type: CapabilityType
    description: str
    examples: List[str]
    requires_context: bool = True


@dataclass
class CopilotResponse:
    """Response from copilot capability."""
    capability: CapabilityType
    content: str
    suggestions: List[str] = field(default_factory=list)
    citations: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ForbiddenAction:
    """A forbidden action attempt."""
    action_type: ActionType
    rejected_at: datetime
    reason: str


class BaseCopilotCapability(ABC):
    """Base class for copilot capabilities."""
    
    @abstractmethod
    def execute(self, query: str, context: Dict[str, Any]) -> CopilotResponse:
        """Execute the capability."""
        pass


class AskCapability(BaseCopilotCapability):
    """Ask questions about the system."""
    
    def execute(self, query: str, context: Dict[str, Any]) -> CopilotResponse:
        """Answer questions."""
        # Read-only query execution
        return CopilotResponse(
            capability=CapabilityType.ASK,
            content=f"Answer to: {query}",
            suggestions=[],
            citations=[]
        )


class ExplainCapability(BaseCopilotCapability):
    """Explain decisions and context."""
    
    def execute(self, query: str, context: Dict[str, Any]) -> CopilotResponse:
        """Provide explanations."""
        # Read-only explanation
        return CopilotResponse(
            capability=CapabilityType.EXPLAIN,
            content=f"Explanation of: {query}",
            suggestions=[],
            citations=[]
        )


class SummarizeCapability(BaseCopilotCapability):
    """Summarize context and data."""
    
    def execute(self, query: str, context: Dict[str, Any]) -> CopilotResponse:
        """Summarize information."""
        # Read-only summarization
        return CopilotResponse(
            capability=CapabilityType.SUMMARIZE,
            content=f"Summary of: {query}",
            suggestions=[],
            citations=[]
        )


class RecommendCapability(BaseCopilotCapability):
    """Produce recommendations (not execute)."""
    
    def execute(self, query: str, context: Dict[str, Any]) -> CopilotResponse:
        """Generate recommendations."""
        # Read-only recommendations only
        return CopilotResponse(
            capability=CapabilityType.RECOMMEND,
            content=f"Recommendations for: {query}",
            suggestions=["Review recommendation 1", "Review recommendation 2"],
            citations=[]
        )


class CopilotCapabilityRegistry:
    """
    Registry of allowed copilot capabilities.
    
    Capabilities are READ-ONLY only.
    """
    
    CAPABILITIES: Dict[CapabilityType, BaseCopilotCapability] = {
        CapabilityType.ASK: AskCapability(),
        CapabilityType.EXPLAIN: ExplainCapability(),
        CapabilityType.SUMMARIZE: SummarizeCapability(),
        CapabilityType.RECOMMEND: RecommendCapability(),
    }
    
    FORBIDDEN_ACTIONS: List[ActionType] = [
        ActionType.EXECUTE_WORKFLOW,
        ActionType.CREATE_WORK_ORDER,
        ActionType.MODIFY_ASSET,
        ActionType.TRIGGER_EVENT,
        ActionType.SELF_HEAL,
        ActionType.AUTONOMOUS_AGENT,
    ]
    
    @classmethod
    def get_capability(cls, capability: CapabilityType) -> Optional[BaseCopilotCapability]:
        """Get a capability."""
        return cls.CAPABILITIES.get(capability)
    
    @classmethod
    def is_forbidden(cls, action_type: ActionType) -> bool:
        """Check if an action is forbidden."""
        return action_type in cls.FORBIDDEN_ACTIONS
    
    @classmethod
    def list_capabilities(cls) -> List[CopilotCapability]:
        """List all available capabilities."""
        return [
            CopilotCapability(
                capability_type=cap,
                description=f"{cap.value} capability",
                examples=[f"Example {cap.value} query"]
            )
            for cap in cls.CAPABILITIES.keys()
        ]


class CopilotLayer:
    """
    Human-Supervised Copilot Layer.
    
    CONSTRAINTS:
    ✓ ALLOWED: Ask, Explain, Summarize, Recommend (READ-ONLY)
    ✗ FORBIDDEN: Execute, Create, Modify, Trigger, Self-heal, Autonomous
    
    All recommendations must be reviewed by humans before action.
    """
    
    def __init__(self):
        self.registry = CopilotCapabilityRegistry()
        self._forbidden_actions: List[ForbiddenAction] = []
    
    def execute_capability(
        self,
        capability: CapabilityType,
        query: str,
        context: Dict[str, Any]
    ) -> CopilotResponse:
        """Execute a copilot capability."""
        cap = self.registry.get_capability(capability)
        if not cap:
            raise ValueError(f"Unknown capability: {capability}")
        
        return cap.execute(query, context)
    
    def attempt_forbidden_action(self, action: ActionType, details: Dict[str, Any]) -> ForbiddenAction:
        """
        Attempt a forbidden action (will be rejected).
        
        This is a safety mechanism - forbidden actions are logged and rejected.
        """
        forbidden = ForbiddenAction(
            action_type=action,
            rejected_at=datetime.now(),
            reason=f"Forbidden action: {action.value}. All actions require human approval."
        )
        self._forbidden_actions.append(forbidden)
        return forbidden
    
    def get_forbidden_attempts(self) -> List[ForbiddenAction]:
        """Get all forbidden action attempts."""
        return self._forbidden_actions


# Singleton instance
_copilot: Optional[CopilotLayer] = None


def get_copilot_layer() -> CopilotLayer:
    """Get or create copilot layer singleton."""
    global _copilot
    if _copilot is None:
        _copilot = CopilotLayer()
    return _copilot
