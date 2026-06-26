"""
AI Intelligence Foundation

Infrastructure for local inference and model management.
NO autonomous execution, NO agents.
"""

from .ollama import (
    MODEL_REGISTRY,
    OllamaClient,
    OllamaStatus,
    ModelStatus,
    HealthStatus,
    ModelMetadata,
    ModelFamily,
    Quantization,
    get_ollama_client,
    ollama_router,
)


__all__ = [
    "MODEL_REGISTRY",
    "OllamaClient",
    "OllamaStatus",
    "ModelStatus",
    "HealthStatus",
    "ModelMetadata",
    "ModelFamily",
    "Quantization",
    "get_ollama_client",
    "ollama_router",
]
