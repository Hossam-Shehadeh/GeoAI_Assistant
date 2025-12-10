"""
History Service - Query history management
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from ..infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class HistoryService:
    """Service for managing query history"""
    
    def __init__(self, config):
        self.config = config
        self.history_file = Path(config.plugin_dir) / "history.json"
        self.max_items = config.get("max_history_items", 1000)
        self.history = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        """Load history from file"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading history: {e}")
        return []
    
    def _save_history(self):
        """Save history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history[-self.max_items:], f, indent=2)
        except Exception as e:
            logger.warning(f"Error saving history: {e}")
    
    def save_query(self, prompt: str, sql: str, result: Dict):
        """Save query to history"""
        entry = {
            "id": len(self.history),
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "sql": sql,
            "result": result,
            "favorite": False,
            "tags": []
        }
        self.history.append(entry)
        self._save_history()
        logger.info(f"Saved query to history: {entry['id']}")
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get query history"""
        if limit:
            return self.history[-limit:]
        return self.history
    
    def search_history(self, query: str) -> List[Dict]:
        """Search history"""
        query_lower = query.lower()
        return [
            entry for entry in self.history
            if query_lower in entry.get("prompt", "").lower() or
               query_lower in entry.get("sql", "").lower()
        ]
    
    def toggle_favorite(self, entry_id: int):
        """Toggle favorite status"""
        for entry in self.history:
            if entry.get("id") == entry_id:
                entry["favorite"] = not entry.get("favorite", False)
                self._save_history()
                return

