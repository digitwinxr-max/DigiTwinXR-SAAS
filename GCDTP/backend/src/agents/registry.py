"""
Agent Registry Service

Agent registry service.
NO execution, workflow control, or asset modification.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from .models import (
    AgentRegistry,
    get_agent_registry,
    AgentType,
    AgentStatus,
    AgentMetadata,
    AgentCapability,
    AgentInvocation,
)


class AgentRegistryService:
    """
    Agent registry service.
    
    Features:
    - Agent metadata storage
    - Capability registration
    - Invocation records
    - Human approval workflow
    
    LIMITATIONS:
    - NO execution
    - NO workflow control
    - NO asset modification
    """
    
    def __init__(self, registry: Optional[AgentRegistry] = None):
        self.registry = registry or get_agent_registry()
        self._register_default_agents()
    
    def _register_default_agents(self):
        """Register default agents."""
        agents = [
            AgentMetadata(
                agent_id="rag_agent",
                name="RAG Agent",
                agent_type=AgentType.RAG,
                description="Retrieval Augmented Generation agent",
                capabilities=[
                    AgentCapability("search", "Search knowledge base", True),
                    AgentCapability("summarize", "Summarize documents", True),
                ],
                version="1.0.0",
                status=AgentStatus.IDLE,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            AgentMetadata(
                agent_id="graph_agent",
                name="Graph Agent",
                agent_type=AgentType.GRAPH,
                description="Knowledge graph reasoning agent",
                capabilities=[
                    AgentCapability("query", "Query knowledge graph", True),
                    AgentCapability("infer", "Infer relationships", True),
                ],
                version="1.0.0",
                status=AgentStatus.IDLE,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            AgentMetadata(
                agent_id="explainability_agent",
                name="Explainability Agent",
                agent_type=AgentType.EXPLAINABILITY,
                description="Decision explanation agent",
                capabilities=[
                    AgentCapability("explain", "Explain decisions", True),
                    AgentCapability("trace", "Trace reasoning", True),
                ],
                version="1.0.0",
                status=AgentStatus.IDLE,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            AgentMetadata(
                agent_id="decision_agent",
                name="Decision Agent",
                agent_type=AgentType.DECISION,
                description="Decision support agent",
                capabilities=[
                    AgentCapability("recommend", "Generate recommendations", True),
                    AgentCapability("compare", "Compare options", True),
                ],
                version="1.0.0",
                status=AgentStatus.IDLE,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            AgentMetadata(
                agent_id="video_agent",
                name="Video Agent",
                agent_type=AgentType.VIDEO,
                description="Video analytics agent",
                capabilities=[
                    AgentCapability("analyze", "Analyze video", True),
                    AgentCapability("detect", "Detect objects", True),
                ],
                version="1.0.0",
                status=AgentStatus.IDLE,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
        ]
        
        for agent in agents:
            if not self.registry.get_agent(agent.agent_id):
                self.registry.register_agent(agent)
    
    def request_invocation(
        self,
        agent_id: str,
        capability: str,
        input_data: Dict[str, Any]
    ) -> Optional[AgentInvocation]:
        """Request an agent invocation (requires approval)."""
        agent = self.registry.get_agent(agent_id)
        if not agent:
            return None
        
        invocation = AgentInvocation(
            invocation_id=f"inv_{datetime.now().timestamp()}",
            agent_id=agent_id,
            capability=capability,
            input_data=input_data,
            output_data=None,
            status="pending",
            requested_at=datetime.now(),
            completed_at=None,
            approved_by=None,
            approved_at=None
        )
        
        return self.registry.record_invocation(invocation)


_service: Optional[AgentRegistryService] = None


def get_agent_service() -> AgentRegistryService:
    """Get or create agent service singleton."""
    global _service
    if _service is None:
        _service = AgentRegistryService()
    return _service
