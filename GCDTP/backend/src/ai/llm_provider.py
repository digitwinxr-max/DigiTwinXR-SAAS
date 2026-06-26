"""
LLM Provider Interface

Abstract interface for LLM providers.
This enables future integration with OpenAI, Claude, Gemini, etc.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class LLMProvider(ABC):
    """
    Abstract LLM Provider interface.
    
    Implementations should provide:
    - generate(): Generate response from context
    - name(): Provider name
    
    Future implementations:
    - OpenAIProvider
    - ClaudeProvider
    - GeminiProvider
    - LocalProvider
    """
    
    @abstractmethod
    def generate(
        self,
        context: List[Dict[str, Any]],
        query: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate response from context.
        
        Args:
            context: List of context chunks with source information
            query: User query
            **kwargs: Additional provider-specific options
            
        Returns:
            Dict containing:
            - answer: Generated response
            - confidence: Confidence score (0-1)
            - sources: List of source IDs used
        """
        pass
    
    @abstractmethod
    def name(self) -> str:
        """Return provider name."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available."""
        pass


class GenerationOptions:
    """Options for generation."""
    max_tokens: int = 1000
    temperature: float = 0.7
    top_p: float = 0.9
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
