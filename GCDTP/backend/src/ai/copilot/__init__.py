"""
Human-Supervised Copilot Layer

READ-ONLY operations: Ask, Explain, Summarize, Recommend.
FORBIDDEN: Execute, Create, Modify, Trigger, Self-heal, Autonomous.
"""

from .capability import (
    CapabilityType,
    ActionType,
    CopilotCapability,
    CopilotResponse,
    ForbiddenAction,
    BaseCopilotCapability,
    CopilotCapabilityRegistry,
    CopilotLayer,
    get_copilot_layer,
)
from .routes import router as copilot_router


__all__ = [
    "CapabilityType",
    "ActionType",
    "CopilotCapability",
    "CopilotResponse",
    "ForbiddenAction",
    "BaseCopilotCapability",
    "CopilotCapabilityRegistry",
    "CopilotLayer",
    "get_copilot_layer",
    "copilot_router",
]
