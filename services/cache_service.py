"""
Cache Service - Intelligent query result caching
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, Optional
from ..infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class CacheService:
    """Service for caching query results"""
    
    def __init__(self, config):
        self.config = config
        self.cache_dir = Path(config.plugin_dir) / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        self.max_size = config.get("max_cache_size", 100)
    
    def _get_key(self, prompt: str) -> str:
        """Generate cache key from prompt"""
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def get(self, prompt: str) -> Optional[Dict]:
        """Get cached result"""
        key = self._get_key(prompt)
        cache_file = self.cache_dir / f"{key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error reading cache: {e}")
        
        return None
    
    def set(self, prompt: str, result: Dict):
        """Cache result"""
        key = self._get_key(prompt)
        cache_file = self.cache_dir / f"{key}.json"
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(result, f)
        except Exception as e:
            logger.warning(f"Error writing cache: {e}")
    
    def clear(self):
        """Clear all cache"""
        for file in self.cache_dir.glob("*.json"):
            file.unlink()
        logger.info("Cache cleared")

