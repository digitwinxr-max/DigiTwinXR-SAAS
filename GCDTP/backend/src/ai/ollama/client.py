"""
Ollama Client Service

Local inference runtime client for Ollama.
Health checks, model lifecycle, connectivity only.
NO autonomous execution, NO prompting logic.
"""

import httpx
import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import asyncio

from .models import MODEL_REGISTRY, ModelMetadata, Quantization

logger = logging.getLogger(__name__)


class OllamaStatus(str, Enum):
    """Ollama service status."""
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


class ModelStatus(str, Enum):
    """Model loading status."""
    NOT_LOADED = "not_loaded"
    LOADING = "loading"
    LOADED = "loaded"
    FAILED = "failed"


@dataclass
class HealthStatus:
    """Ollama health status."""
    status: OllamaStatus
    version: Optional[str]
    endpoint: str
    latency_ms: float
    timestamp: datetime
    error: Optional[str] = None


@dataclass
class ModelLoadStatus:
    """Model loading status info."""
    name: str
    status: ModelStatus
    size: Optional[str] = None
    loaded_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    error: Optional[str] = None


class OllamaClient:
    """
    Ollama client for local inference.
    
    Features:
    - Health checks
    - Model lifecycle management
    - Connectivity validation
    
    Limitations:
    - NO prompting
    - NO autonomous execution
    - NO agent behavior
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        timeout: float = 30.0
    ):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Ollama API base URL
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        self._loaded_models: Dict[str, ModelLoadStatus] = {}
        self._health_cache: Optional[HealthStatus] = None
        self._health_cache_time: Optional[datetime] = None
        self._cache_ttl_seconds: int = 30
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout
            )
        return self._client
    
    async def close(self):
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    async def health_check(self, use_cache: bool = True) -> HealthStatus:
        """
        Check Ollama service health.
        
        Args:
            use_cache: Use cached result if recent
            
        Returns:
            HealthStatus with service health info
        """
        # Check cache
        if use_cache and self._health_cache:
            cache_age = (datetime.now() - self._health_cache_time).total_seconds()
            if cache_age < self._cache_ttl_seconds:
                return self._health_cache
        
        start_time = datetime.now()
        
        try:
            client = await self._get_client()
            response = await client.get("/api/health")
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            if response.status_code == 200:
                data = response.json()
                status = OllamaStatus.HEALTHY if latency_ms < 1000 else OllamaStatus.DEGRADED
                
                self._health_cache = HealthStatus(
                    status=status,
                    version=data.get("version"),
                    endpoint=self.base_url,
                    latency_ms=latency_ms,
                    timestamp=datetime.now()
                )
                return self._health_cache
            else:
                return HealthStatus(
                    status=OllamaStatus.UNAVAILABLE,
                    version=None,
                    endpoint=self.base_url,
                    latency_ms=latency_ms,
                    timestamp=datetime.now(),
                    error=f"HTTP {response.status_code}"
                )
                
        except httpx.ConnectError as e:
            return HealthStatus(
                status=OllamaStatus.UNAVAILABLE,
                version=None,
                endpoint=self.base_url,
                latency_ms=(datetime.now() - start_time).total_seconds() * 1000,
                timestamp=datetime.now(),
                error=f"Connection failed: {str(e)}"
            )
        except httpx.TimeoutException as e:
            return HealthStatus(
                status=OllamaStatus.UNAVAILABLE,
                version=None,
                endpoint=self.base_url,
                latency_ms=self.timeout * 1000,
                timestamp=datetime.now(),
                error=f"Timeout: {str(e)}"
            )
        except Exception as e:
            return HealthStatus(
                status=OllamaStatus.UNKNOWN,
                version=None,
                endpoint=self.base_url,
                latency_ms=(datetime.now() - start_time).total_seconds() * 1000,
                timestamp=datetime.now(),
                error=str(e)
            )
    
    async def list_local_models(self) -> List[str]:
        """
        List locally available models.
        
        Returns:
            List of model names available locally
        """
        try:
            client = await self._get_client()
            response = await client.get("/api/tags")
            
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
            return []
            
        except Exception as e:
            logger.error(f"Failed to list local models: {e}")
            return []
    
    async def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get model information.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model information dict or None
        """
        try:
            client = await self._get_client()
            response = await client.post("/api/show", json={"name": model_name})
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            logger.error(f"Failed to get model info for {model_name}: {e}")
            return None
    
    async def pull_model(self, model_name: str) -> bool:
        """
        Pull a model from Ollama registry.
        
        Args:
            model_name: Name of the model to pull
            
        Returns:
            True if successful
        """
        try:
            client = await self._get_client()
            
            # Start pull request
            async with client.stream("POST", "/api/pull", json={"name": model_name}) as response:
                if response.status_code == 200:
                    # Update model status
                    self._loaded_models[model_name] = ModelLoadStatus(
                        name=model_name,
                        status=ModelStatus.LOADED,
                        loaded_at=datetime.now()
                    )
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            self._loaded_models[model_name] = ModelLoadStatus(
                name=model_name,
                status=ModelStatus.FAILED,
                error=str(e)
            )
            return False
    
    async def load_model(self, model_name: str) -> ModelLoadStatus:
        """
        Load a model into memory.
        
        Args:
            model_name: Name of the model to load
            
        Returns:
            ModelLoadStatus with loading result
        """
        # Check if already loaded
        if model_name in self._loaded_models:
            status = self._loaded_models[model_name]
            if status.status == ModelStatus.LOADED:
                status.last_used = datetime.now()
                return status
        
        self._loaded_models[model_name] = ModelLoadStatus(
            name=model_name,
            status=ModelStatus.LOADING
        )
        
        try:
            client = await self._get_client()
            
            # Send generate request to load model
            response = await client.post("/api/generate", json={
                "model": model_name,
                "prompt": "",
                "stream": False
            })
            
            if response.status_code == 200:
                self._loaded_models[model_name] = ModelLoadStatus(
                    name=model_name,
                    status=ModelStatus.LOADED,
                    loaded_at=datetime.now(),
                    last_used=datetime.now()
                )
            else:
                self._loaded_models[model_name] = ModelLoadStatus(
                    name=model_name,
                    status=ModelStatus.FAILED,
                    error=f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            self._loaded_models[model_name] = ModelLoadStatus(
                name=model_name,
                status=ModelStatus.FAILED,
                error=str(e)
            )
        
        return self._loaded_models[model_name]
    
    async def unload_model(self, model_name: str) -> bool:
        """
        Unload a model from memory.
        
        Args:
            model_name: Name of the model to unload
            
        Returns:
            True if successful
        """
        # Remove from loaded models
        if model_name in self._loaded_models:
            del self._loaded_models[model_name]
        
        return True
    
    async def get_loaded_models(self) -> List[ModelLoadStatus]:
        """
        Get list of currently loaded models.
        
        Returns:
            List of loaded model statuses
        """
        return list(self._loaded_models.values())
    
    def get_model_metadata(self, model_name: str) -> Optional[ModelMetadata]:
        """
        Get metadata for a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            ModelMetadata or None if not found
        """
        return MODEL_REGISTRY.get(model_name)
    
    def validate_model_requirements(
        self,
        model_name: str,
        available_ram_gb: float,
        available_vram_gb: float
    ) -> tuple[bool, Optional[str]]:
        """
        Validate if model can run with available resources.
        
        Args:
            model_name: Name of the model
            available_ram_gb: Available RAM in GB
            available_vram_gb: Available VRAM in GB
            
        Returns:
            Tuple of (can_run, error_message)
        """
        metadata = self.get_model_metadata(model_name)
        if not metadata:
            return False, f"Model {model_name} not found in registry"
        
        if available_ram_gb < metadata.min_ram_gb:
            return False, f"Insufficient RAM: {available_ram_gb}GB < {metadata.min_ram_gb}GB required"
        
        if metadata.min_vram_gb > 0 and available_vram_gb < metadata.min_vram_gb:
            return False, f"Insufficient VRAM: {available_vram_gb}GB < {metadata.min_vram_gb}GB required"
        
        return True, None
    
    async def generate_embeddings(
        self,
        model_name: str,
        prompt: str
    ) -> Optional[List[float]]:
        """
        Generate embeddings for a prompt.
        
        Note: This is connectivity-only. Actual embedding generation
        happens on Ollama server. No autonomous execution.
        
        Args:
            model_name: Name of the embedding model
            prompt: Text to embed
            
        Returns:
            List of embedding values or None
        """
        try:
            client = await self._get_client()
            response = await client.post("/api/embeddings", json={
                "model": model_name,
                "prompt": prompt
            })
            
            if response.status_code == 200:
                data = response.json()
                return data.get("embedding")
            return None
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            return None


# Singleton instance for application use
_client: Optional[OllamaClient] = None


def get_ollama_client(base_url: str = "http://localhost:11434") -> OllamaClient:
    """Get or create Ollama client singleton."""
    global _client
    if _client is None:
        _client = OllamaClient(base_url)
    return _client
