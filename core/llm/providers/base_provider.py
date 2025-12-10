"""
Base Provider - Abstract base class for all LLM providers
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from ..interfaces import ILLMProvider


class BaseProvider(ILLMProvider):
    """Base implementation for all providers"""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        self.api_key = api_key
        self.config = kwargs
    
    @abstractmethod
    def query(self, prompt: str, system_prompt: str = None, 
              model: str = None, **kwargs) -> str:
        """Execute a query"""
        pass
    
    def is_available(self) -> bool:
        """Check if provider is available"""
        return self.api_key is not None
    
    @abstractmethod
    def get_models(self) -> list:
        """Get available models"""
        pass

