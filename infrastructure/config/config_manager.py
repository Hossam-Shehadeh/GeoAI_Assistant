"""
Configuration Manager - Centralized configuration management
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv


class ConfigManager:
    """Manages plugin configuration"""
    
    def __init__(self):
        self.plugin_dir = Path(__file__).parent.parent.parent.parent
        self.config_dir = self.plugin_dir / "config"
        self.config_file = self.config_dir / "settings.json"
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
        
        # Load environment variables
        env_file = self.plugin_dir / ".env"
        if env_file.exists():
            load_dotenv(env_file)
        
        # Load settings
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return self._default_settings()
        return self._default_settings()
    
    def _default_settings(self) -> Dict[str, Any]:
        """Default settings"""
        return {
            "llm_provider": "ollama",
            "llm_model": "phi3",
            "theme": "dark",
            "auto_save_history": True,
            "cache_enabled": True,
            "max_history_items": 1000
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.settings[key] = value
        self._save_settings()
    
    def _save_settings(self) -> None:
        """Save settings to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable"""
        return os.getenv(key, default)

