"""
Ollama API Routes

Health checks, model registry, and lifecycle management.
NO autonomous execution, NO prompting.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from .client import OllamaClient, get_ollama_client, OllamaStatus, ModelStatus
from .models import (
    MODEL_REGISTRY, 
    ModelMetadata, 
    ModelFamily, 
    Quantization,
    get_model,
    get_models_by_family,
    get_models_by_capability,
    list_all_models
)

router = APIRouter(prefix="/ollama", tags=["ollama"])


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: Optional[str]
    endpoint: str
    latency_ms: float
    timestamp: datetime
    error: Optional[str] = None


class ModelMetadataResponse(BaseModel):
    """Model metadata response."""
    name: str
    family: str
    size_params: str
    context_window: int
    quantization: str
    gpu_layers: Optional[int]
    min_ram_gb: float
    min_vram_gb: float
    description: str
    capabilities: List[str]
    tags: List[str]
    
    @classmethod
    def from_metadata(cls, metadata: ModelMetadata) -> "ModelMetadataResponse":
        return cls(
            name=metadata.name,
            family=metadata.family.value,
            size_params=metadata.size_params,
            context_window=metadata.context_window,
            quantization=metadata.quantization.value,
            gpu_layers=metadata.gpu_layers,
            min_ram_gb=metadata.min_ram_gb,
            min_vram_gb=metadata.min_vram_gb,
            description=metadata.description,
            capabilities=metadata.capabilities,
            tags=metadata.tags
        )


class ModelLoadStatusResponse(BaseModel):
    """Model load status response."""
    name: str
    status: str
    size: Optional[str] = None
    loaded_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    error: Optional[str] = None


class RequirementValidationRequest(BaseModel):
    """Requirement validation request."""
    model_name: str
    available_ram_gb: float
    available_vram_gb: float


class RequirementValidationResponse(BaseModel):
    """Requirement validation response."""
    can_run: bool
    error: Optional[str] = None


@router.get("/health", response_model=HealthResponse)
async def get_health():
    """
    Get Ollama service health status.
    
    Returns health information including:
    - Service status (healthy/degraded/unavailable)
    - Ollama version
    - Endpoint
    - Latency
    """
    client = get_ollama_client()
    health = await client.health_check()
    
    return HealthResponse(
        status=health.status.value,
        version=health.version,
        endpoint=health.endpoint,
        latency_ms=health.latency_ms,
        timestamp=health.timestamp,
        error=health.error
    )


@router.get("/models", response_model=List[ModelMetadataResponse])
async def get_registered_models(
    family: Optional[str] = Query(None, description="Filter by model family"),
    capability: Optional[str] = Query(None, description="Filter by capability")
):
    """
    Get list of registered models in the model registry.
    
    Can filter by:
    - family: qwen, deepseek, gemma, llama
    - capability: chat, code, reasoning, vision, etc.
    """
    models = list_all_models()
    
    if family:
        family_enum = ModelFamily(family.lower())
        models = [m for m in models if m.family == family_enum]
    
    if capability:
        models = [m for m in models if capability in m.capabilities]
    
    return [ModelMetadataResponse.from_metadata(m) for m in models]


@router.get("/models/{model_name}", response_model=ModelMetadataResponse)
async def get_model_by_name(model_name: str):
    """
    Get metadata for a specific model.
    """
    metadata = get_model(model_name)
    if not metadata:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
    
    return ModelMetadataResponse.from_metadata(metadata)


@router.get("/models/family/{family}", response_model=List[ModelMetadataResponse])
async def get_models_by_family_endpoint(family: str):
    """
    Get all models in a specific family.
    """
    try:
        family_enum = ModelFamily(family.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid family: {family}. Valid: qwen, deepseek, gemma, llama"
        )
    
    models = get_models_by_family(family_enum)
    return [ModelMetadataResponse.from_metadata(m) for m in models]


@router.get("/models/capability/{capability}", response_model=List[ModelMetadataResponse])
async def get_models_by_capability_endpoint(capability: str):
    """
    Get all models with a specific capability.
    """
    models = get_models_by_capability(capability)
    return [ModelMetadataResponse.from_metadata(m) for m in models]


@router.get("/local", response_model=List[str])
async def get_local_models():
    """
    Get list of models available locally in Ollama.
    """
    client = get_ollama_client()
    models = await client.list_local_models()
    return models


@router.get("/local/{model_name}/info")
async def get_local_model_info(model_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a locally loaded model.
    """
    client = get_ollama_client()
    info = await client.get_model_info(model_name)
    
    if not info:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found locally")
    
    return info


@router.post("/models/{model_name}/load", response_model=ModelLoadStatusResponse)
async def load_model(model_name: str):
    """
    Load a model into memory.
    
    Note: This is model lifecycle management only.
    No autonomous execution occurs.
    """
    client = get_ollama_client()
    
    # Check if model exists in registry
    if not get_model(model_name):
        raise HTTPException(
            status_code=404, 
            detail=f"Model {model_name} not found in registry"
        )
    
    status = await client.load_model(model_name)
    
    return ModelLoadStatusResponse(
        name=status.name,
        status=status.status.value,
        size=status.size,
        loaded_at=status.loaded_at,
        last_used=status.last_used,
        error=status.error
    )


@router.delete("/models/{model_name}/load")
async def unload_model(model_name: str):
    """
    Unload a model from memory.
    
    Note: This is model lifecycle management only.
    """
    client = get_ollama_client()
    success = await client.unload_model(model_name)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to unload model")
    
    return {"message": f"Model {model_name} unloaded", "success": True}


@router.get("/loaded", response_model=List[ModelLoadStatusResponse])
async def get_loaded_models():
    """
    Get list of currently loaded models.
    """
    client = get_ollama_client()
    models = await client.get_loaded_models()
    
    return [
        ModelLoadStatusResponse(
            name=m.name,
            status=m.status.value,
            size=m.size,
            loaded_at=m.loaded_at,
            last_used=m.last_used,
            error=m.error
        )
        for m in models
    ]


@router.post("/validate-requirements", response_model=RequirementValidationResponse)
async def validate_model_requirements(request: RequirementValidationRequest):
    """
    Validate if a model can run with available resources.
    
    Checks:
    - Available RAM against model requirements
    - Available VRAM against GPU requirements
    """
    client = get_ollama_client()
    can_run, error = client.validate_model_requirements(
        request.model_name,
        request.available_ram_gb,
        request.available_vram_gb
    )
    
    return RequirementValidationResponse(can_run=can_run, error=error)


@router.get("/quantizations", response_model=List[str])
async def get_quantization_levels():
    """
    Get list of available quantization levels.
    """
    return [q.value for q in Quantization]


@router.get("/families", response_model=List[str])
async def get_model_families():
    """
    Get list of available model families.
    """
    return [f.value for f in ModelFamily]
