"""
Ollama Provider Implementation
"""

import requests
from typing import List
from .base_provider import BaseProvider


class OllamaProvider(BaseProvider):
    """Ollama local LLM provider"""
    
    def __init__(self, base_url: str = "http://localhost:11434", **kwargs):
        super().__init__(**kwargs)
        self.base_url = base_url
        self.default_model = kwargs.get("default_model", "phi3")
    
    def query(self, prompt: str, system_prompt: str = None, 
              model: str = None, **kwargs) -> str:
        """Query Ollama API"""
        if model is None:
            model = self.default_model
        
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        if system_prompt:
            payload["system"] = system_prompt
        
        response = requests.post(url, json=payload, timeout=120)
        if response.status_code != 200:
            raise Exception(f"Ollama error: {response.text}")
        
        return response.json().get("response", "").strip()
    
    def is_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_models(self) -> List[str]:
        """Get available Ollama models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [m.get("name", "") for m in models if m.get("name")]
        except Exception:
            pass
        return ["phi3", "mistral", "llama2", "llama3"]

