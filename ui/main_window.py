"""
Main Window - Creative Modern UI with ALL Features from Main Version
"""

from qgis.PyQt.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QLabel, QPushButton, QFrame, QStackedWidget,
    QSplitter, QListWidget, QListWidgetItem, QToolButton
)
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtGui import QIcon, QFont
from qgis.core import QgsMessageLog, Qgis

from .components.model_selector import ModelSelector
from .components.query_editor import QueryEditor
from .components.history_panel import HistoryPanel
from .components.analytics_dashboard import AnalyticsDashboard
from .components.batch_processor import BatchProcessor
from .components.template_manager import TemplateManager
from .components.model_converter import ModelConverter
from .components.smart_assistant import SmartAssistantPanel
from .components.error_fixer import ErrorFixerPanel
from .components.data_analysis import DataAnalysisPanel
from .components.settings_panel import SettingsPanel
from .themes.theme_manager import ThemeManager
from ..infrastructure.config.config_manager import ConfigManager
from ..infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class MainWindow(QDockWidget):
    """Creative main application window with ALL features"""
    
    def __init__(self, iface, config, llm_handler=None, sql_executor=None,
                 image_processor=None, error_fixer=None, smart_assistant=None):
        super().__init__("GeoAI Assistant Pro", iface.mainWindow())
        self.iface = iface
        self.config = config
        
        # Store modules
        self.llm_handler = llm_handler
        self.sql_executor = sql_executor
        self.image_processor = image_processor
        self.error_fixer = error_fixer
        self.smart_assistant = smart_assistant
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        self.theme_manager.apply_theme(self.config.get("theme", "dark"))
        
        self.setup_ui()
        QgsMessageLog.logMessage("GeoAI Assistant Pro window initialized", "GeoAI Pro", Qgis.Info)
    
    def setup_ui(self):
        """Setup the creative modern UI with ALL features"""
        main_widget = QWidget()
        self.setWidget(main_widget)
        
        # Main layout with sidebar
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_widget.setLayout(main_layout)
        
        # Left Sidebar
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Main content area
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_widget.setLayout(content_layout)
        
        # Top bar with model selector and actions
        top_bar = self.create_top_bar()
        content_layout.addWidget(top_bar)
        
        # Tab widget for main content - ALL TABS from main version
        self.tabs = QTabWidget()
        self.tabs.setObjectName("mainTabs")
        content_layout.addWidget(self.tabs)
        
        # Create ALL tabs from main version
        self.query_editor = QueryEditor(self.iface, self.config, self, 
                                       self.llm_handler, self.sql_executor, self.error_fixer)
        self.tabs.addTab(self.query_editor, "🔍 SQL Generator")
        
        self.model_converter = ModelConverter(self.iface, self.config, self,
                                             self.image_processor, self.llm_handler)
        self.tabs.addTab(self.model_converter, "🖼️ Model Converter")
        
        self.smart_assistant_panel = SmartAssistantPanel(self.iface, self.config, self,
                                                        self.smart_assistant)
        self.tabs.addTab(self.smart_assistant_panel, "💡 Smart Assistant")
        
        self.error_fixer_panel = ErrorFixerPanel(self.iface, self.config, self,
                                                self.error_fixer, self.sql_executor)
        self.tabs.addTab(self.error_fixer_panel, "🔧 Error Fixer")
        
        self.data_analysis = DataAnalysisPanel(self.iface, self.config, self,
                                              self.llm_handler, self.sql_executor)
        self.tabs.addTab(self.data_analysis, "📊 Data Analysis")
        
        # Pro-specific tabs
        self.history_panel = HistoryPanel(self.iface, self.config)
        self.tabs.addTab(self.history_panel, "📜 History")
        
        self.batch_processor = BatchProcessor(self.iface, self.config, 
                                             self.llm_handler, self.sql_executor)
        self.tabs.addTab(self.batch_processor, "⚡ Batch Process")
        
        self.template_manager = TemplateManager(self.iface, self.config)
        self.tabs.addTab(self.template_manager, "📝 Templates")
        
        self.analytics_dashboard = AnalyticsDashboard(self.iface, self.config)
        self.tabs.addTab(self.analytics_dashboard, "📈 Analytics")
        
        # Settings tab
        self.settings_panel = SettingsPanel(self.iface, self.config, self,
                                          self.image_processor)
        self.tabs.addTab(self.settings_panel, "⚙️ Settings")
        
        main_layout.addWidget(content_widget, 1)
        
        # Apply theme
        self.theme_manager.apply_to_widget(self)
    
    def switch_to_tab(self, index):
        """Switch to a specific tab"""
        if 0 <= index < self.tabs.count():
            self.tabs.setCurrentIndex(index)
    
    def create_sidebar(self):
        """Create modern sidebar navigation"""
        sidebar = QWidget()
        sidebar.setFixedWidth(250)
        sidebar.setObjectName("sidebar")
        sidebar.setStyleSheet("""
            QWidget#sidebar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e, stop:1 #16213e);
                border-right: 2px solid #0f3460;
            }
            QListWidget {
                background: transparent;
                border: none;
                color: #e6e6e6;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 12px 20px;
                border-radius: 8px;
                margin: 4px 8px;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #61afef, stop:1 #528bff);
                color: white;
                font-weight: 600;
            }
            QListWidget::item:hover {
                background-color: rgba(97, 175, 239, 0.3);
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        sidebar.setLayout(layout)
        
        # Logo/Header
        header = QLabel("⚡ GeoAI Pro")
        header.setStyleSheet("""
            QLabel {
                color: #61afef;
                font-size: 24px;
                font-weight: 700;
                padding: 20px;
                background: rgba(97, 175, 239, 0.1);
                border-bottom: 2px solid #0f3460;
            }
        """)
        layout.addWidget(header)
        
        # Navigation - ALL features
        nav_list = QListWidget()
        nav_items = [
            "🔍 SQL Generator",
            "🖼️ Model Converter",
            "💡 Smart Assistant",
            "🔧 Error Fixer",
            "📊 Data Analysis",
            "📜 Query History",
            "⚡ Batch Process",
            "📝 Templates",
            "📈 Analytics",
            "⚙️ Settings"
        ]
        for item in nav_items:
            nav_list.addItem(QListWidgetItem(item))
        
        nav_list.currentRowChanged.connect(self.on_nav_changed)
        layout.addWidget(nav_list)
        
        # Quick stats at bottom
        stats_widget = QWidget()
        stats_widget.setStyleSheet("""
            QWidget {
                background: rgba(15, 52, 96, 0.5);
                border-top: 2px solid #0f3460;
                padding: 15px;
            }
            QLabel {
                color: #abb2bf;
                font-size: 11px;
            }
        """)
        stats_layout = QVBoxLayout()
        stats_widget.setLayout(stats_layout)
        
        stats_label = QLabel("📈 Quick Stats")
        stats_label.setStyleSheet("color: #61afef; font-weight: 600;")
        stats_layout.addWidget(stats_label)
        
        self.queries_today = QLabel("Queries Today: 0")
        stats_layout.addWidget(self.queries_today)
        
        self.success_rate = QLabel("Success Rate: 100%")
        stats_layout.addWidget(self.success_rate)
        
        layout.addWidget(stats_widget)
        
        return sidebar
    
    def create_top_bar(self):
        """Create top bar with model selector and quick actions"""
        top_bar = QWidget()
        top_bar.setObjectName("topBar")
        top_bar.setStyleSheet("""
            QWidget#topBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #21252b, stop:1 #282c34);
                border-radius: 12px;
                padding: 12px;
                margin-bottom: 10px;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        top_bar.setLayout(layout)
        
        # Model selector
        self.model_selector = ModelSelector(self.config, self.llm_handler)
        # Set LLM handler if available
        if self.llm_handler:
            self.model_selector.set_llm_handler(self.llm_handler)
        layout.addWidget(self.model_selector)
        
        layout.addStretch()
        
        # Quick action buttons
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setObjectName("quickAction")
        refresh_btn.clicked.connect(self.refresh_all)
        layout.addWidget(refresh_btn)
        
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.setObjectName("quickAction")
        settings_btn.clicked.connect(lambda: self.switch_to_tab(self.tabs.count() - 1))
        layout.addWidget(settings_btn)
        
        # Apply button styles
        top_bar.setStyleSheet(top_bar.styleSheet() + """
            QPushButton#quickAction {
                background-color: #3e4451;
                border: 1px solid #61afef;
                border-radius: 6px;
                padding: 8px 16px;
                color: #e6e6e6;
                font-size: 12px;
            }
            QPushButton#quickAction:hover {
                background-color: #61afef;
                color: white;
            }
        """)
        
        return top_bar
    
    def on_nav_changed(self, index):
        """Handle sidebar navigation"""
        self.tabs.setCurrentIndex(index)
    
    def refresh_all(self):
        """Refresh all components"""
        QgsMessageLog.logMessage("Refreshing all components", "GeoAI Pro", Qgis.Info)
        # TODO: Implement refresh logic
