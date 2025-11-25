"""
LLM client abstract base class / protocol.
"""
from typing import Iterable, Protocol, runtime_checkable


@runtime_checkable
class LLMClient(Protocol):
    """Protocol for LLM client implementations."""
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text synchronously.
        
        Args:
            prompt: The prompt to send to the LLM.
            **kwargs: Additional parameters (model, temperature, etc.)
            
        Returns:
            Generated text response.
        """
        ...
    
    def generate_stream(self, prompt: str, **kwargs) -> Iterable[str]:
        """
        Generate text with streaming output.
        
        Args:
            prompt: The prompt to send to the LLM.
            **kwargs: Additional parameters (model, temperature, etc.)
            
        Yields:
            Text chunks as they are generated.
        """
        ...
