"""
Structured logging system
"""

import logging
from pathlib import Path
from qgis.core import QgsMessageLog, Qgis


class QGISLogHandler(logging.Handler):
    """Custom handler that logs to QGIS message log"""
    
    def emit(self, record):
        log_entry = self.format(record)
        level = Qgis.Info
        if record.levelno >= logging.ERROR:
            level = Qgis.Critical
        elif record.levelno >= logging.WARNING:
            level = Qgis.Warning
        
        QgsMessageLog.logMessage(log_entry, "GeoAI Pro", level)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # QGIS handler
        qgis_handler = QGISLogHandler()
        qgis_handler.setFormatter(
            logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(qgis_handler)
    
    return logger

