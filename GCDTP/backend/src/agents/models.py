"""
Agent Models

Agent registry models.
NO execution, workflow control, or asset modification.
Human approval mandatory for all actions.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AgentType(str, Enum):
    """Agent types."""
    RAG = "rag"
    GRAPH = "graph"
    EXPLAINABILITY = "explainability"
    DECISION = "decision"
    VIDEO = "video"


class AgentStatus(str, Enum):
    """Agent status."""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"


@dataclass
class AgentCapability:
    """Agent capability."""
    name: str
    description: str
    requires_approval: bool = True


@dataclass
class AgentMetadata:
    """Agent metadata."""
    agent_id: str
    name: str
    agent_type: AgentType
    description: str
    capabilities: List[AgentCapability]
    version: str
    status: AgentStatus
    created_at: datetime
    updated_at: datetime


@dataclass
class AgentInvocation:
    """Agent invocation record."""
    invocation_id: str
    agent_id: str
    capability: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]]
    status: str
    requested_at: datetime
    completed_at: Optional[datetime]
    approved_by: Optional[str]
    approved_at: Optional[datetime]


class AgentRegistry:
    """
    Agent registry.
    
    ALLOWED:
    - Agent metadata storage
    - Capability registration
    - Invocation records
    - Human approval workflow
    
    FORBIDDEN:
    - Execution
    - Workflow control
    - Asset modification
    """
    
    def __init__(self):
        self._agents: Dict[str, AgentMetadata] = {}
        self._invocations: Dict[str, AgentInvocation] = {}
    
    def register_agent(self, agent: AgentMetadata) -> AgentMetadata:
        """Register an agent."""
        self._agents[agent.agent_id] = agent
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[AgentMetadata]:
        """Get agent by ID."""
        return self._agents.get(agent_id)
    
    def list_agents(self, agent_type: Optional[AgentType] = None) -> List[AgentMetadata]:
        """List agents."""
        agents = list(self._agents.values())
        if agent_type:
            agents = [a for a in agents if a.agent_type == agent_type]
        return agents
    
    def record_invocation(
        self,
        invocation: AgentInvocation
    ) -> AgentInvocation:
        """Record an agent invocation."""
        self._invocations[invocation.invocation_id] = invocation
        return invocation
    
    def approve_invocation(
        self,
        invocation_id: str,
        approved_by: str
    ) -> Optional[AgentInvocation]:
        """Approve an invocation."""
        invocation = self._invocations.get(invocation_id)
        if invocation:
            invocation.approved_by = approved_by
            invocation.approved_at = datetime.now()
        return invocation
    
    def list_invocations(
        self,
        agent_id: Optional[str] = None,
        pending_only: bool = False
    ) -> List[AgentInvocation]:
        """List invocations."""
        invocations = list(self._invocations.values())
        if agent_id:
            invocations = [i for i in invocations if i.agent_id == agent_id]
        if pending_only:
            invocations = [i for i in invocations if i.approved_by is None]
        return invocations


# Singleton instance
_registry: Optional[AgentRegistry] = None


def get_agent_registry() -> AgentRegistry:
    """Get or create agent registry singleton."""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry
