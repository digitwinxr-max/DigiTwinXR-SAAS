"""
Ollama Integration Layer

Local inference runtime with model registry and health checks.
NO autonomous execution, NO prompting logic.
"""

from .models import (
    MODEL_REGISTRY,
    ModelMetadata,
    ModelFamily,
    Quantization,
    get_model,
    get_models_by_family,
    get_models_by_capability,
    list_all_models,
)

from .client import (
    OllamaClient,
    OllamaStatus,
    ModelStatus,
    HealthStatus,
    ModelLoadStatus,
    get_ollama_client,
)

from .routes import router as ollama_router


__all__ = [
    # Models
    "MODEL_REGISTRY",
    "ModelMetadata",
    "ModelFamily",
    "Quantization",
    "get_model",
    "get_models_by_family",
    "get_models_by_capability",
    "list_all_models",
    # Client
    "OllamaClient",
    "OllamaStatus",
    "ModelStatus",
    "HealthStatus",
    "ModelLoadStatus",
    "get_ollama_client",
    # Routes
    "ollama_router",
]
