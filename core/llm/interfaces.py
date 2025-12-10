"""
LLM Provider Interfaces - Abstract base classes for all providers
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class ILLMProvider(ABC):
    """Interface for all LLM providers"""
    
    @abstractmethod
    def query(self, prompt: str, system_prompt: str = None, 
              model: str = None, **kwargs) -> str:
        """Execute a query with the provider"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available"""
        pass
    
    @abstractmethod
    def get_models(self) -> List[str]:
        """Get available models for this provider"""
        pass


class ILLMProviderFactory(ABC):
    """Factory interface for creating providers"""
    
    @abstractmethod
    def create_provider(self, provider_name: str) -> ILLMProvider:
        """Create a provider instance"""
        pass

