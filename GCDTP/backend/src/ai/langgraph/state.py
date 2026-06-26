"""
LangGraph State Definitions

State schema for cognitive orchestration graphs.
NO autonomous execution - only state definitions.
"""

from typing import TypedDict, List, Optional, Dict, Any, Literal, Annotated
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class NodeType(str, Enum):
    """Node types in the orchestration graph."""
    RETRIEVAL = "retrieval"
    REASONING = "reasoning"
    CONTEXT = "context"
    MEMORY = "memory"
    TOOL = "tool"
    CONDITIONAL = "conditional"
    OUTPUT = "output"


class EdgeType(str, Enum):
    """Edge types in the orchestration graph."""
    SEQUENTIAL = "sequential"
    CONDITIONAL = "conditional"
    FEEDBACK = "feedback"
    FALLBACK = "fallback"


@dataclass
class NodeMetadata:
    """Metadata for a node."""
    name: str
    description: str
    node_type: NodeType
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    requires_tools: bool = False
    requires_memory: bool = False
    is_critical: bool = False


@dataclass
class EdgeMetadata:
    """Metadata for an edge."""
    source: str
    target: str
    edge_type: EdgeType
    condition: Optional[str] = None
    description: Optional[str] = None


@dataclass
class GraphMetadata:
    """Metadata for a complete graph."""
    name: str
    description: str
    version: str
    nodes: List[NodeMetadata] = field(default_factory=list)
    edges: List[EdgeMetadata] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class AgentState(TypedDict):
    """
    Core agent state for all orchestration graphs.
    
    This defines the state schema only - no execution logic.
    """
    # User input
    query: str
    session_id: str
    
    # Context
    context: Dict[str, Any]
    retrieved_documents: List[Dict[str, Any]]
    
    # Reasoning
    reasoning_steps: List[Dict[str, Any]]
    current_step: int
    
    # Memory
    short_term_memory: List[Dict[str, Any]]
    long_term_memory: Dict[str, Any]
    
    # Output
    response: Optional[str]
    confidence: Optional[float]
    citations: List[Dict[str, Any]]
    
    # Control
    should_continue: bool
    error: Optional[str]


class RAGState(TypedDict):
    """
    RAG (Retrieval Augmented Generation) state.
    
    State for retrieval-augmented workflows.
    """
    query: str
    session_id: str
    
    # Retrieval
    retrieved_documents: List[Dict[str, Any]]
    relevant_chunks: List[Dict[str, Any]]
    retrieval_scores: List[float]
    
    # Generation
    context: str
    response: Optional[str]
    
    # Feedback
    relevance_scores: List[float]
    needs_rewrite: bool
    
    # Control
    iteration: int
    max_iterations: int


class ReasoningState(TypedDict):
    """
    Reasoning state for step-by-step reasoning.
    
    State for chain-of-thought reasoning workflows.
    """
    problem: str
    session_id: str
    
    # Steps
    steps: List[Dict[str, Any]]
    current_step: int
    
    # Evidence
    evidence: List[Dict[str, Any]]
    assumptions: List[str]
    
    # Conclusion
    conclusion: Optional[str]
    confidence: Optional[float]
    
    # Control
    should_continue: bool
    max_steps: int


class ContextAssemblyState(TypedDict):
    """
    Context assembly state for multi-source context.
    
    State for assembling context from multiple sources.
    """
    query: str
    session_id: str
    
    # Sources
    sources: Dict[str, List[Dict[str, Any]]]
    source_weights: Dict[str, float]
    
    # Assembly
    assembled_context: Optional[str]
    conflicting_info: List[Dict[str, Any]]
    
    # Output
    response: Optional[str]
    evidence_chain: List[Dict[str, Any]]
    
    # Control
    assembled: bool


class CognitiveGraphState(TypedDict):
    """
    Cognitive graph state for knowledge graph reasoning.
    
    State for knowledge graph-based reasoning.
    """
    query: str
    session_id: str
    
    # Graph traversal
    current_node: Optional[str]
    visited_nodes: List[str]
    path: List[str]
    
    # Relationships
    relevant_edges: List[Dict[str, Any]]
    relationship_types: List[str]
    
    # Inference
    inferred_facts: List[Dict[str, Any]]
    confidence_scores: Dict[str, float]
    
    # Output
    conclusion: Optional[str]
    explanation: Optional[str]
    
    # Control
    max_depth: int
    current_depth: int


class CopilotState(TypedDict):
    """
    Copilot state for human-supervised assistance.
    
    State for the copilot assistant.
    
    CONSTRAINTS:
    - Human must approve all actions
    - No autonomous execution
    - All suggestions must be presented for review
    """
    user_intent: str
    session_id: str
    
    # Understanding
    intent_classification: Optional[str]
    entities: List[Dict[str, Any]]
    
    # Suggestions (presented to human for approval)
    suggestions: List[Dict[str, Any]]
    selected_suggestions: List[str]
    
    # Actions (require human approval)
    proposed_actions: List[Dict[str, Any]]
    approved_actions: List[Dict[str, Any]]
    rejected_actions: List[Dict[str, Any]]
    
    # Response
    response: Optional[str]
    explanation: Optional[str]
    
    # Control
    requires_approval: bool
    human_approved: bool
