"""
GeoAI Assistant Pro - Advanced QGIS Plugin Entry Point
Enterprise-grade AI-powered geospatial assistant with ALL features
"""

import os
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsMessageLog, Qgis

from .modules.llm_handler import LLMHandler
from .modules.sql_executor import SQLExecutor
from .modules.image_processor import ImageProcessor
from .modules.error_fixer import ErrorFixer
from .modules.smart_assistant import SmartAssistant
from .ui.main_window import MainWindow
from .infrastructure.config.config_manager import ConfigManager
from .infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class GeoAIAssistant:
    """QGIS Plugin Implementation - Advanced Version with ALL Features"""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        
        # Initialize components
        self.actions = []
        self.menu = '&GeoAI Assistant Pro'
        self.toolbar = self.iface.addToolBar('GeoAI Assistant Pro')
        self.toolbar.setObjectName('GeoAIAssistantPro')
        
        # Main window
        self.main_window = None
        
        # Configuration
        self.config = ConfigManager()
        
        # Initialize modules
        self.llm_handler = None
        self.sql_executor = None
        self.image_processor = None
        self.error_fixer = None
        self.smart_assistant = None
        
        logger.info("GeoAI Assistant Pro initialized")

    def initGui(self):
        """Create the menu entries and toolbar icons"""
        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        
        # Main action
        self.add_action(
            icon_path,
            text='Open GeoAI Assistant Pro',
            callback=self.run,
            parent=self.iface.mainWindow(),
            add_to_toolbar=True
        )
        
        # SQL Generator Action
        self.add_action(
            icon_path,
            text='SQL Generator',
            callback=self.open_sql_generator,
            parent=self.iface.mainWindow()
        )
        
        # Model Builder Converter
        self.add_action(
            icon_path,
            text='Model Builder to Code',
            callback=self.open_model_converter,
            parent=self.iface.mainWindow()
        )
        
        logger.info("Plugin GUI initialized")

    def add_action(self, icon_path, text, callback, parent=None, add_to_toolbar=False):
        """Add a toolbar icon and menu item"""
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        
        if add_to_toolbar:
            self.toolbar.addAction(action)
        
        self.iface.addPluginToMenu(self.menu, action)
        self.actions.append(action)
        
        return action

    def initialize_modules(self):
        """Initialize all AI modules"""
        try:
            self.llm_handler = LLMHandler()
            self.sql_executor = SQLExecutor(self.iface)
            self.image_processor = ImageProcessor(self.llm_handler)
            self.error_fixer = ErrorFixer(self.llm_handler, self.sql_executor)
            self.smart_assistant = SmartAssistant(self.llm_handler, self.iface, self.sql_executor)
            
            logger.info("GeoAI Assistant Pro modules initialized successfully")
            QgsMessageLog.logMessage(
                'GeoAI Assistant Pro modules initialized successfully',
                'GeoAI Pro',
                Qgis.Info
            )
        except Exception as e:
            logger.error(f"Error initializing modules: {e}")
            QgsMessageLog.logMessage(
                f'Error initializing modules: {str(e)}',
                'GeoAI Pro',
                Qgis.Critical
            )

    def run(self):
        """Run method that performs all the real work"""
        # Initialize modules if not already done
        if self.llm_handler is None:
            self.initialize_modules()
        
        if self.main_window is None:
            self.main_window = MainWindow(
                self.iface, 
                self.config,
                self.llm_handler,
                self.sql_executor,
                self.image_processor,
                self.error_fixer,
                self.smart_assistant
            )
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.main_window)
        
        self.main_window.show()
        logger.info("Main window opened")

    def open_sql_generator(self):
        """Open SQL Generator tab"""
        self.run()
        if self.main_window:
            self.main_window.switch_to_tab(0)

    def open_model_converter(self):
        """Open Model Builder Converter tab"""
        self.run()
        if self.main_window:
            # Find model converter tab index
            for i in range(self.main_window.tabs.count()):
                if "Model" in self.main_window.tabs.tabText(i):
                    self.main_window.switch_to_tab(i)
                    break

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI"""
        for action in self.actions:
            self.iface.removePluginMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)
        
        if self.main_window:
            self.iface.removeDockWidget(self.main_window)
            self.main_window.deleteLater()
            self.main_window = None
        
        del self.toolbar
        logger.info("Plugin unloaded")
