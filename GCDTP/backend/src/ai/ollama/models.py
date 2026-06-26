"""
Ollama Model Registry

Model metadata definitions for supported models.
This module contains ONLY metadata - no prompting or execution.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


class Quantization(str, Enum):
    """Quantization levels for models."""
    Q2_K = "q2_k"
    Q3_K_M = "q3_k_m"
    Q4_0 = "q4_0"
    Q4_K_M = "q4_k_m"
    Q5_0 = "q5_0"
    Q5_K_M = "q5_k_m"
    Q6_K = "q6_k"
    Q8_0 = "q8_0"
    F16 = "f16"
    F32 = "f32"


class ModelFamily(str, Enum):
    """Supported model families."""
    QWEN = "qwen"
    DEEPSEEK = "deepseek"
    GEMMA = "gemma"
    LLAMA = "llama"


@dataclass
class ModelMetadata:
    """Model metadata containing all information about a model."""
    name: str
    family: ModelFamily
    size_params: str  # e.g., "0.5B", "1.5B", "7B", "14B", "70B"
    context_window: int  # Token context window
    quantization: Quantization
    gpu_layers: Optional[int] = None  # Layers to offload to GPU
    min_ram_gb: float = 8.0  # Minimum RAM required in GB
    min_vram_gb: float = 0.0  # Minimum VRAM required in GB
    description: str = ""
    capabilities: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    version: str = "latest"
    created_at: Optional[datetime] = None


# Model Registry - All supported models with metadata
MODEL_REGISTRY: Dict[str, ModelMetadata] = {
    # Qwen3 Models
    "qwen3:0.6b": ModelMetadata(
        name="qwen3:0.6b",
        family=ModelFamily.QWEN,
        size_params="0.6B",
        context_window=32000,
        quantization=Quantization.Q4_K_M,
        gpu_layers=0,
        min_ram_gb=1.0,
        min_vram_gb=0.0,
        description="Qwen3 0.6B parameter model - lightweight",
        capabilities=["chat", "code", "reasoning"],
        tags=["lightweight", "fast"]
    ),
    "qwen3:1.5b": ModelMetadata(
        name="qwen3:1.5b",
        family=ModelFamily.QWEN,
        size_params="1.5B",
        context_window=32000,
        quantization=Quantization.Q4_K_M,
        gpu_layers=0,
        min_ram_gb=2.0,
        min_vram_gb=0.0,
        description="Qwen3 1.5B parameter model",
        capabilities=["chat", "code", "reasoning"],
        tags=["lightweight", "fast"]
    ),
    "qwen3:4b": ModelMetadata(
        name="qwen3:4b",
        family=ModelFamily.QWEN,
        size_params="4B",
        context_window=32000,
        quantization=Quantization.Q4_K_M,
        gpu_layers=12,
        min_ram_gb=6.0,
        min_vram_gb=2.0,
        description="Qwen3 4B parameter model - balanced",
        capabilities=["chat", "code", "reasoning", "math"],
        tags=["balanced"]
    ),
    "qwen3:8b": ModelMetadata(
        name="qwen3:8b",
        family=ModelFamily.QWEN,
        size_params="8B",
        context_window=32000,
        quantization=Quantization.Q4_K_M,
        gpu_layers=20,
        min_ram_gb=10.0,
        min_vram_gb=6.0,
        description="Qwen3 8B parameter model - recommended",
        capabilities=["chat", "code", "reasoning", "math", "multilingual"],
        tags=["recommended", "balanced"]
    ),
    "qwen3:14b": ModelMetadata(
        name="qwen3:14b",
        family=ModelFamily.QWEN,
        size_params="14B",
        context_window=32000,
        quantization=Quantization.Q4_K_M,
        gpu_layers=35,
        min_ram_gb=16.0,
        min_vram_gb=10.0,
        description="Qwen3 14B parameter model - high quality",
        capabilities=["chat", "code", "reasoning", "math", "multilingual", "long-context"],
        tags=["high-quality"]
    ),
    "qwen3:32b": ModelMetadata(
        name="qwen3:32b",
        family=ModelFamily.QWEN,
        size_params="32B",
        context_window=32000,
        quantization=Quantization.Q4_K_M,
        gpu_layers=80,
        min_ram_gb=32.0,
        min_vram_gb=24.0,
        description="Qwen3 32B parameter model - premium",
        capabilities=["chat", "code", "reasoning", "math", "multilingual", "long-context", "agent"],
        tags=["premium"]
    ),
    
    # DeepSeek Models
    "deepseek-r1:1.5b": ModelMetadata(
        name="deepseek-r1:1.5b",
        family=ModelFamily.DEEPSEEK,
        size_params="1.5B",
        context_window=64000,
        quantization=Quantization.Q4_K_M,
        gpu_layers=0,
        min_ram_gb=2.0,
        min_vram_gb=0.0,
        description="DeepSeek R1 1.5B - reasoning optimized",
        capabilities=["reasoning", "math", "code"],
        tags=["reasoning", "fast"]
    ),
    "deepseek-r1:7b": ModelMetadata(
        name="deepseek-r1:7b",
        family=ModelFamily.DEEPSEEK,
        size_params="7B",
        context_window=128000,
        quantization=Quantization.Q4_K_M,
        gpu_layers=20,
        min_ram_gb=8.0,
        min_vram_gb=6.0,
        description="DeepSeek R1 7B - recommended reasoning",
        capabilities=["reasoning", "math", "code", "long-context"],
        tags=["reasoning", "recommended"]
    ),
    "deepseek-r1:14b": ModelMetadata(
        name="deepseek-r1:14b",
        family=ModelFamily.DEEPSEEK,
        size_params="14B",
        context_window=128000,
        quantization=Quantization.Q4_K_M,
        gpu_layers=35,
        min_ram_gb=16.0,
        min_vram_gb=10.0,
        description="DeepSeek R1 14B - high quality reasoning",
        capabilities=["reasoning", "math", "code", "long-context"],
        tags=["reasoning", "high-quality"]
    ),
    "deepseek-r1:32b": ModelMetadata(
        name="deepseek-r1:32b",
        family=ModelFamily.DEEPSEEK,
        size_params="32B",
        context_window=128000,
        quantization=Quantization.Q4_K_M,
        gpu_layers=80,
        min_ram_gb=32.0,
        min_vram_gb=24.0,
        description="DeepSeek R1 32B - premium reasoning",
        capabilities=["reasoning", "math", "code", "long-context", "agent"],
        tags=["reasoning", "premium"]
    ),
    "deepseek-coder:1.5b": ModelMetadata(
        name="deepseek-coder:1.5b",
        family=ModelFamily.DEEPSEEK,
        size_params="1.5B",
        context_window=16000,
        quantization=Quantization.Q4_K_M,
        gpu_layers=0,
        min_ram_gb=2.0,
        min_vram_gb=0.0,
        description="DeepSeek Coder 1.5B - code specialized",
        capabilities=["code", "completion"],
        tags=["code", "fast"]
    ),
    "deepseek-coder:7b": ModelMetadata(
        name="deepseek-coder:7b",
        family=ModelFamily.DEEPSEEK,
        size_params="7B",
        context_window=16000,
        quantization=Quantization.Q4_K_M,
        gpu_layers=20,
        min_ram_gb=8.0,
        min_vram_gb=6.0,
        description="DeepSeek Coder 7B - code recommended",
        capabilities=["code", "completion", "review"],
        tags=["code", "recommended"]
    ),
    
    # Gemma Models
    "gemma:2b": ModelMetadata(
        name="gemma:2b",
        family=ModelFamily.GEMMA,
        size_params="2B",
        context_window=8000,
        quantization=Quantization.Q4_K_M,
        gpu_layers=0,
        min_ram_gb=3.0,
        min_vram_gb=0.0,
        description="Gemma 2B - lightweight Google model",
        capabilities=["chat", "instruction-following"],
        tags=["lightweight", "fast", "google"]
    ),
    "gemma:7b": ModelMetadata(
        name="gemma:7b",
        family=ModelFamily.GEMMA,
        size_params="7B",
        context_window=8000,
        quantization=Quantization.Q4_K_M,
        gpu_layers=20,
        min_ram_gb=8.0,
        min_vram_gb=6.0,
        description="Gemma 7B - balanced Google model",
        capabilities=["chat", "instruction-following", "reasoning"],
        tags=["balanced", "google"]
    ),
    "gemma3:4b": ModelMetadata(
        name="gemma3:4b",
        family=ModelFamily.GEMMA,
        size_params="4B",
        context_window=32000,
        quantization=Quantization.Q4_K_M,
        gpu_layers=12,
        min_ram_gb=6.0,
        min_vram_gb=4.0,
        description="Gemma 3 4B - extended context",
        capabilities=["chat", "instruction-following", "reasoning", "multilingual"],
        tags=["extended-context", "google"]
    ),
    "gemma3:12b": ModelMetadata(
        name="gemma3:12b",
        family=ModelFamily.GEMMA,
        size_params="12B",
        context_window=32000,
        quantization=Quantization.Q4_K_M,
        gpu_layers=30,
        min_ram_gb=14.0,
        min_vram_gb=10.0,
        description="Gemma 3 12B - high quality",
        capabilities=["chat", "instruction-following", "reasoning", "multilingual", "vision"],
        tags=["high-quality", "vision", "google"]
    ),
    
    # Llama Models
    "llama3:8b": ModelMetadata(
        name="llama3:8b",
        family=ModelFamily.LLAMA,
        size_params="8B",
        context_window=8192,
        quantization=Quantization.Q4_K_M,
        gpu_layers=20,
        min_ram_gb=10.0,
        min_vram_gb=6.0,
        description="Llama 3 8B - Meta foundation",
        capabilities=["chat", "instruction-following", "reasoning"],
        tags=["foundation", "meta"]
    ),
    "llama3.1:8b": ModelMetadata(
        name="llama3.1:8b",
        family=ModelFamily.LLAMA,
        size_params="8B",
        context_window=128000,
        quantization=Quantization.Q4_K_M,
        gpu_layers=20,
        min_ram_gb=10.0,
        min_vram_gb=6.0,
        description="Llama 3.1 8B - extended context",
        capabilities=["chat", "instruction-following", "reasoning", "long-context"],
        tags=["extended-context", "meta"]
    ),
    "llama3.2:3b": ModelMetadata(
        name="llama3.2:3b",
        family=ModelFamily.LLAMA,
        size_params="3B",
        context_window=128000,
        quantization=Quantization.Q4_K_M,
        gpu_layers=0,
        min_ram_gb=4.0,
        min_vram_gb=0.0,
        description="Llama 3.2 3B - lightweight vision",
        capabilities=["chat", "instruction-following", "vision"],
        tags=["vision", "lightweight", "meta"]
    ),
    "llama3.2:11b-vision": ModelMetadata(
        name="llama3.2:11b-vision",
        family=ModelFamily.LLAMA,
        size_params="11B",
        context_window=128000,
        quantization=Quantization.Q4_K_M,
        gpu_layers=30,
        min_ram_gb=14.0,
        min_vram_gb=10.0,
        description="Llama 3.2 11B Vision - vision model",
        capabilities=["chat", "instruction-following", "vision", "reasoning"],
        tags=["vision", "high-quality", "meta"]
    ),
    "llama3.1:70b": ModelMetadata(
        name="llama3.1:70b",
        family=ModelFamily.LLAMA,
        size_params="70B",
        context_window=128000,
        quantization=Quantization.Q4_K_M,
        gpu_layers=80,
        min_ram_gb=64.0,
        min_vram_gb=48.0,
        description="Llama 3.1 70B - premium quality",
        capabilities=["chat", "instruction-following", "reasoning", "long-context", "agent"],
        tags=["premium", "high-quality", "meta"]
    ),
}


def get_model(name: str) -> Optional[ModelMetadata]:
    """Get model metadata by name."""
    return MODEL_REGISTRY.get(name)


def get_models_by_family(family: ModelFamily) -> List[ModelMetadata]:
    """Get all models in a family."""
    return [m for m in MODEL_REGISTRY.values() if m.family == family]


def get_models_by_capability(capability: str) -> List[ModelMetadata]:
    """Get all models supporting a capability."""
    return [m for m in MODEL_REGISTRY.values() if capability in m.capabilities]


def list_all_models() -> List[ModelMetadata]:
    """List all registered models."""
    return list(MODEL_REGISTRY.values())
