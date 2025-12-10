"""
LLM Data Models
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class ProviderType(Enum):
    """LLM Provider types"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"
    HUGGINGFACE = "huggingface"


@dataclass
class LLMModel:
    """LLM Model information"""
    name: str
    provider: ProviderType
    is_vision: bool = False
    max_tokens: int = 4000
    cost_per_token: float = 0.0


@dataclass
class QueryRequest:
    """Query request model"""
    prompt: str
    system_prompt: Optional[str] = None
    provider: Optional[ProviderType] = None
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000


@dataclass
class QueryResponse:
    """Query response model"""
    content: str
    provider: ProviderType
    model: str
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    response_time: Optional[float] = None
    success: bool = True
    error: Optional[str] = None

