"""
Agent Definition Model

Represents an AI Agent definition.
Agents propose actions - humans approve.
"""

import uuid
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


class AgentType(str, Enum):
    """Types of agents."""
    DIAGNOSTIC = "diagnostic_agent"
    MAINTENANCE = "maintenance_agent"
    RECOVERY = "recovery_agent"
    KNOWLEDGE = "knowledge_agent"
    TIMELINE = "timeline_agent"


@dataclass
class AgentDefinition:
    """
    Agent definition.
    
    Agents propose actions based on context.
    Humans must approve all actions before execution.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: Optional[str] = None
    agent_type: AgentType = AgentType.DIAGNOSTIC
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "agent_type": self.agent_type.value if isinstance(self.agent_type, Enum) else self.agent_type,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentDefinition":
        """Create from dictionary."""
        agent_type = data.get("agent_type")
        if isinstance(agent_type, str):
            agent_type = AgentType(agent_type)
        
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description"),
            agent_type=agent_type or AgentType.DIAGNOSTIC,
            enabled=data.get("enabled", True),
            created_at=created_at or datetime.utcnow()
        )
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get agent capabilities."""
        return {
            "analyze_context": True,
            "propose_actions": True,
            "create_recommendations": True,
            "invoke_rag": True,
            "access_knowledge": True in [
                self.agent_type == AgentType.KNOWLEDGE,
                self.agent_type == AgentType.DIAGNOSTIC
            ],
            "read_timelines": self.agent_type == AgentType.TIMELINE,
            "inspect_health": self.agent_type == AgentType.DIAGNOSTIC,
            "create_events": False,
            "modify_health": False,
            "alter_measurements": False,
            "execute_automatically": False,
            "close_work_orders": False,
            "control_assets": False,
            "send_notifications": False
        }
    
    def get_type_display_name(self) -> str:
        """Get human-readable type name."""
        names = {
            AgentType.DIAGNOSTIC: "Diagnostic Agent",
            AgentType.MAINTENANCE: "Maintenance Agent",
            AgentType.RECOVERY: "Recovery Agent",
            AgentType.KNOWLEDGE: "Knowledge Agent",
            AgentType.TIMELINE: "Timeline Agent"
        }
        return names.get(self.agent_type, "Agent")
