"""
LangGraph Graph Definitions

Graph definitions for orchestration workflows.
NO autonomous execution - only graph structure definitions.
"""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime

from .state import (
    NodeMetadata,
    EdgeMetadata,
    GraphMetadata,
    NodeType,
    EdgeType,
    AgentState,
    RAGState,
    ReasoningState,
    ContextAssemblyState,
    CognitiveGraphState,
    CopilotState,
)


@dataclass
class GraphDefinition:
    """
    Complete graph definition with metadata.
    
    This defines the graph structure only - no execution.
    """
    metadata: GraphMetadata
    nodes: Dict[str, NodeMetadata] = field(default_factory=dict)
    edges: List[EdgeMetadata] = field(default_factory=list)
    conditional_edges: Dict[str, List[tuple]] = field(default_factory=dict)
    
    # State schema
    state_schema: type = AgentState


class NodeRegistry:
    """
    Registry of available nodes for graph construction.
    
    Contains metadata about nodes but NOT implementations.
    """
    
    NODES: Dict[str, NodeMetadata] = {
        # Retrieval nodes
        "vector_retrieve": NodeMetadata(
            name="vector_retrieve",
            description="Retrieve documents from vector store",
            node_type=NodeType.RETRIEVAL,
            requires_tools=True,
            requires_memory=False
        ),
        "keyword_retrieve": NodeMetadata(
            name="keyword_retrieve",
            description="Retrieve documents by keyword search",
            node_type=NodeType.RETRIEVAL,
            requires_tools=True,
            requires_memory=False
        ),
        "hybrid_retrieve": NodeMetadata(
            name="hybrid_retrieve",
            description="Hybrid vector and keyword retrieval",
            node_type=NodeType.RETRIEVAL,
            requires_tools=True,
            requires_memory=False
        ),
        "rerank": NodeMetadata(
            name="rerank",
            description="Rerank retrieved documents",
            node_type=NodeType.RETRIEVAL,
            requires_tools=False,
            requires_memory=False
        ),
        
        # Reasoning nodes
        "analyze_query": NodeMetadata(
            name="analyze_query",
            description="Analyze and decompose query",
            node_type=NodeType.REASONING,
            requires_tools=False,
            requires_memory=False
        ),
        "synthesize": NodeMetadata(
            name="synthesize",
            description="Synthesize response from context",
            node_type=NodeType.REASONING,
            requires_tools=False,
            requires_memory=False
        ),
        "chain_of_thought": NodeMetadata(
            name="chain_of_thought",
            description="Step-by-step reasoning",
            node_type=NodeType.REASONING,
            requires_tools=False,
            requires_memory=False
        ),
        "validate": NodeMetadata(
            name="validate",
            description="Validate response against constraints",
            node_type=NodeType.REASONING,
            requires_tools=False,
            requires_memory=False
        ),
        
        # Context nodes
        "assemble_context": NodeMetadata(
            name="assemble_context",
            description="Assemble context from multiple sources",
            node_type=NodeType.CONTEXT,
            requires_tools=False,
            requires_memory=False
        ),
        "resolve_conflicts": NodeMetadata(
            name="resolve_conflicts",
            description="Resolve conflicting information",
            node_type=NodeType.CONTEXT,
            requires_tools=False,
            requires_memory=False
        ),
        "rank_context": NodeMetadata(
            name="rank_context",
            description="Rank context by relevance",
            node_type=NodeType.CONTEXT,
            requires_tools=False,
            requires_memory=False
        ),
        
        # Memory nodes
        "store_memory": NodeMetadata(
            name="store_memory",
            description="Store information in memory",
            node_type=NodeType.MEMORY,
            requires_tools=False,
            requires_memory=True
        ),
        "recall_memory": NodeMetadata(
            name="recall_memory",
            description="Recall relevant memories",
            node_type=NodeType.MEMORY,
            requires_tools=False,
            requires_memory=True
        ),
        "forget_memory": NodeMetadata(
            name="forget_memory",
            description="Forget old or irrelevant memories",
            node_type=NodeType.MEMORY,
            requires_tools=False,
            requires_memory=True
        ),
        
        # Tool nodes
        "execute_tool": NodeMetadata(
            name="execute_tool",
            description="Execute a tool",
            node_type=NodeType.TOOL,
            requires_tools=True,
            requires_memory=False,
            is_critical=True
        ),
        "plan_tool_use": NodeMetadata(
            name="plan_tool_use",
            description="Plan tool usage",
            node_type=NodeType.TOOL,
            requires_tools=True,
            requires_memory=False
        ),
        
        # Conditional nodes
        "route_query": NodeMetadata(
            name="route_query",
            description="Route query based on type",
            node_type=NodeType.CONDITIONAL,
            requires_tools=False,
            requires_memory=False
        ),
        "check_relevance": NodeMetadata(
            name="check_relevance",
            description="Check context relevance",
            node_type=NodeType.CONDITIONAL,
            requires_tools=False,
            requires_memory=False
        ),
        "should_continue": NodeMetadata(
            name="should_continue",
            description="Check if should continue iteration",
            node_type=NodeType.CONDITIONAL,
            requires_tools=False,
            requires_memory=False
        ),
        
        # Output nodes
        "format_response": NodeMetadata(
            name="format_response",
            description="Format final response",
            node_type=NodeType.OUTPUT,
            requires_tools=False,
            requires_memory=False
        ),
        "generate_citations": NodeMetadata(
            name="generate_citations",
            description="Generate citations for response",
            node_type=NodeType.OUTPUT,
            requires_tools=False,
            requires_memory=False
        ),
        "log_interaction": NodeMetadata(
            name="log_interaction",
            description="Log interaction to history",
            node_type=NodeType.OUTPUT,
            requires_tools=False,
            requires_memory=True
        ),
    }
    
    @classmethod
    def get_node(cls, name: str) -> Optional[NodeMetadata]:
        """Get node metadata by name."""
        return cls.NODES.get(name)
    
    @classmethod
    def list_nodes(cls, node_type: Optional[NodeType] = None) -> List[NodeMetadata]:
        """List all nodes, optionally filtered by type."""
        if node_type:
            return [n for n in cls.NODES.values() if n.node_type == node_type]
        return list(cls.NODES.values())
    
    @classmethod
    def list_node_names(cls) -> List[str]:
        """List all node names."""
        return list(cls.NODES.keys())


class EdgeRegistry:
    """
    Registry of predefined edges for common graph patterns.
    
    Contains edge definitions but NOT implementations.
    """
    
    EDGES: Dict[str, List[EdgeMetadata]] = {
        "retrieval_pipeline": [
            EdgeMetadata(
                source="keyword_retrieve",
                target="rerank",
                edge_type=EdgeType.SEQUENTIAL,
                description="Rerank keyword results"
            ),
            EdgeMetadata(
                source="rerank",
                target="assemble_context",
                edge_type=EdgeType.SEQUENTIAL,
                description="Assemble context from reranked docs"
            ),
        ],
        "reasoning_pipeline": [
            EdgeMetadata(
                source="analyze_query",
                target="chain_of_thought",
                edge_type=EdgeType.SEQUENTIAL,
                description="Analyze then reason"
            ),
            EdgeMetadata(
                source="chain_of_thought",
                target="validate",
                edge_type=EdgeType.SEQUENTIAL,
                description="Reason then validate"
            ),
        ],
        "feedback_loop": [
            EdgeMetadata(
                source="validate",
                target="analyze_query",
                edge_type=EdgeType.FEEDBACK,
                condition="invalid",
                description="Loop back on validation failure"
            ),
            EdgeMetadata(
                source="validate",
                target="format_response",
                edge_type=EdgeType.SEQUENTIAL,
                condition="valid",
                description="Proceed on validation success"
            ),
        ],
        "copilot_workflow": [
            EdgeMetadata(
                source="analyze_query",
                target="route_query",
                edge_type=EdgeType.SEQUENTIAL,
                description="Analyze then route"
            ),
            EdgeMetadata(
                source="route_query",
                target="synthesize",
                edge_type=EdgeType.SEQUENTIAL,
                description="Route to synthesis"
            ),
            EdgeMetadata(
                source="synthesize",
                target="format_response",
                edge_type=EdgeType.SEQUENTIAL,
                description="Synthesize to format"
            ),
        ],
    }
    
    @classmethod
    def get_edge_set(cls, name: str) -> List[EdgeMetadata]:
        """Get a predefined edge set."""
        return cls.EDGES.get(name, [])
    
    @classmethod
    def list_edge_sets(cls) -> List[str]:
        """List all predefined edge sets."""
        return list(cls.EDGES.keys())


class GraphRegistry:
    """
    Registry of predefined graph configurations.
    
    Contains graph metadata and structure but NOT implementations.
    """
    
    GRAPHS: Dict[str, GraphDefinition] = {}
    
    @classmethod
    def register_graph(cls, definition: GraphDefinition) -> None:
        """Register a graph definition."""
        cls.GRAPHS[definition.metadata.name] = definition
    
    @classmethod
    def get_graph(cls, name: str) -> Optional[GraphDefinition]:
        """Get a graph definition by name."""
        return cls.GRAPHS.get(name)
    
    @classmethod
    def list_graphs(cls) -> List[GraphMetadata]:
        """List all registered graphs."""
        return [g.metadata for g in cls.GRAPHS.values()]


# Predefined Graph Definitions

# RAG Graph
GraphRegistry.register_graph(GraphDefinition(
    metadata=GraphMetadata(
        name="rag",
        description="Retrieval Augmented Generation graph",
        version="1.0.0",
        nodes=[
            NodeRegistry.get_node("vector_retrieve"),
            NodeRegistry.get_node("keyword_retrieve"),
            NodeRegistry.get_node("rerank"),
            NodeRegistry.get_node("assemble_context"),
            NodeRegistry.get_node("synthesize"),
            NodeRegistry.get_node("should_continue"),
            NodeRegistry.get_node("format_response"),
            NodeRegistry.get_node("generate_citations"),
        ],
        edges=[
            EdgeMetadata("vector_retrieve", "rerank", EdgeType.SEQUENTIAL),
            EdgeMetadata("keyword_retrieve", "rerank", EdgeType.SEQUENTIAL),
            EdgeMetadata("rerank", "assemble_context", EdgeType.SEQUENTIAL),
            EdgeMetadata("assemble_context", "synthesize", EdgeType.SEQUENTIAL),
            EdgeMetadata("synthesize", "should_continue", EdgeType.SEQUENTIAL),
            EdgeMetadata("should_continue", "vector_retrieve", EdgeType.FEEDBACK, "continue"),
            EdgeMetadata("should_continue", "format_response", EdgeType.SEQUENTIAL, "stop"),
            EdgeMetadata("format_response", "generate_citations", EdgeType.SEQUENTIAL),
            EdgeMetadata("generate_citations", "log_interaction", EdgeType.SEQUENTIAL),
        ]
    ),
    state_schema=RAGState
))

# Reasoning Graph
GraphRegistry.register_graph(GraphDefinition(
    metadata=GraphMetadata(
        name="reasoning",
        description="Step-by-step reasoning graph",
        version="1.0.0",
        nodes=[
            NodeRegistry.get_node("analyze_query"),
            NodeRegistry.get_node("chain_of_thought"),
            NodeRegistry.get_node("validate"),
            NodeRegistry.get_node("should_continue"),
            NodeRegistry.get_node("format_response"),
        ],
        edges=[
            EdgeMetadata("analyze_query", "chain_of_thought", EdgeType.SEQUENTIAL),
            EdgeMetadata("chain_of_thought", "validate", EdgeType.SEQUENTIAL),
            EdgeMetadata("validate", "should_continue", EdgeType.SEQUENTIAL),
            EdgeMetadata("should_continue", "chain_of_thought", EdgeType.FEEDBACK, "continue"),
            EdgeMetadata("should_continue", "format_response", EdgeType.SEQUENTIAL, "stop"),
        ]
    ),
    state_schema=ReasoningState
))

# Copilot Graph
GraphRegistry.register_graph(GraphDefinition(
    metadata=GraphMetadata(
        name="copilot",
        description="Human-supervised copilot graph",
        version="1.0.0",
        nodes=[
            NodeRegistry.get_node("analyze_query"),
            NodeRegistry.get_node("route_query"),
            NodeRegistry.get_node("recall_memory"),
            NodeRegistry.get_node("assemble_context"),
            NodeRegistry.get_node("synthesize"),
            NodeRegistry.get_node("format_response"),
            NodeRegistry.get_node("log_interaction"),
        ],
        edges=[
            EdgeMetadata("analyze_query", "route_query", EdgeType.SEQUENTIAL),
            EdgeMetadata("route_query", "recall_memory", EdgeType.SEQUENTIAL, "memory"),
            EdgeMetadata("route_query", "assemble_context", EdgeType.SEQUENTIAL, "context"),
            EdgeMetadata("recall_memory", "assemble_context", EdgeType.SEQUENTIAL),
            EdgeMetadata("assemble_context", "synthesize", EdgeType.SEQUENTIAL),
            EdgeMetadata("synthesize", "format_response", EdgeType.SEQUENTIAL),
            EdgeMetadata("format_response", "log_interaction", EdgeType.SEQUENTIAL),
        ]
    ),
    state_schema=CopilotState
))

# Context Assembly Graph
GraphRegistry.register_graph(GraphDefinition(
    metadata=GraphMetadata(
        name="context_assembly",
        description="Multi-source context assembly graph",
        version="1.0.0",
        nodes=[
            NodeRegistry.get_node("vector_retrieve"),
            NodeRegistry.get_node("keyword_retrieve"),
            NodeRegistry.get_node("recall_memory"),
            NodeRegistry.get_node("rank_context"),
            NodeRegistry.get_node("resolve_conflicts"),
            NodeRegistry.get_node("assemble_context"),
        ],
        edges=[
            EdgeMetadata("vector_retrieve", "rank_context", EdgeType.SEQUENTIAL),
            EdgeMetadata("keyword_retrieve", "rank_context", EdgeType.SEQUENTIAL),
            EdgeMetadata("recall_memory", "rank_context", EdgeType.SEQUENTIAL),
            EdgeMetadata("rank_context", "resolve_conflicts", EdgeType.SEQUENTIAL),
            EdgeMetadata("resolve_conflicts", "assemble_context", EdgeType.SEQUENTIAL),
        ]
    ),
    state_schema=ContextAssemblyState
))


def get_graph(name: str) -> Optional[GraphDefinition]:
    """Get a graph definition by name."""
    return GraphRegistry.get_graph(name)


def list_graphs() -> List[GraphMetadata]:
    """List all registered graphs."""
    return GraphRegistry.list_graphs()


def get_node(name: str) -> Optional[NodeMetadata]:
    """Get node metadata by name."""
    return NodeRegistry.get_node(name)


def list_nodes(node_type: Optional[NodeType] = None) -> List[NodeMetadata]:
    """List all nodes."""
    return NodeRegistry.list_nodes(node_type)


def get_edge_set(name: str) -> List[EdgeMetadata]:
    """Get a predefined edge set."""
    return EdgeRegistry.get_edge_set(name)


def list_edge_sets() -> List[str]:
    """List all predefined edge sets."""
    return EdgeRegistry.list_edge_sets()
