"""
Query Service - Orchestrates SQL generation and execution
"""

from typing import Dict, Optional
from qgis.core import QgsMessageLog, Qgis
from ..infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class QueryService:
    """Service for query operations"""
    
    def __init__(self, llm_handler, sql_executor, cache_service=None, history_service=None):
        self.llm_handler = llm_handler
        self.sql_executor = sql_executor
        self.cache_service = cache_service
        self.history_service = history_service
    
    def generate_and_execute(self, prompt: str, provider: str, model: str, 
                            use_cache: bool = True) -> Dict:
        """Generate SQL and execute it"""
        # Check cache first
        if use_cache and self.cache_service:
            cached = self.cache_service.get(prompt)
            if cached:
                logger.info("Using cached query result")
                return cached
        
        # Generate SQL
        context = self.sql_executor.get_context()
        result = self.llm_handler.generate_sql(prompt, context, provider, model)
        
        if "error" in result:
            return result
        
        # Save to history
        if self.history_service:
            self.history_service.save_query(prompt, result.get("sql", ""), result)
        
        # Cache result
        if use_cache and self.cache_service:
            self.cache_service.set(prompt, result)
        
        return result

