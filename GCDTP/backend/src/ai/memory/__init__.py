"""
Context Memory Layer

RAG, Cognitive Graph, and Context Assembly Engine.
Deterministic - NO AI execution.
"""

from .rag import (
    RAGEngine,
    RAGQuery,
    RAGResponse,
    RetrievalStrategy,
    Document,
    Chunk,
    RetrievalResult,
    VectorStore,
    KeywordIndex,
)

from .cognitive_graph import (
    CognitiveGraph,
    EntityType,
    RelationshipType,
    Entity,
    Relationship,
    GraphQuery,
    GraphResult,
    InferenceResult,
    get_cognitive_graph,
)

from .context_assembly import (
    ContextAssemblyEngine,
    SourceType,
    ConflictResolution,
    ContextSource,
    ContextItem,
    AssembledContext,
    AssemblyConfig,
    get_context_assembly_engine,
)

from .routes import router as context_router


__all__ = [
    # RAG
    "RAGEngine",
    "RAGQuery",
    "RAGResponse",
    "RetrievalStrategy",
    "Document",
    "Chunk",
    "RetrievalResult",
    "VectorStore",
    "KeywordIndex",
    # Cognitive Graph
    "CognitiveGraph",
    "EntityType",
    "RelationshipType",
    "Entity",
    "Relationship",
    "GraphQuery",
    "GraphResult",
    "InferenceResult",
    "get_cognitive_graph",
    # Context Assembly
    "ContextAssemblyEngine",
    "SourceType",
    "ConflictResolution",
    "ContextSource",
    "ContextItem",
    "AssembledContext",
    "AssemblyConfig",
    "get_context_assembly_engine",
    # Routes
    "context_router",
]
