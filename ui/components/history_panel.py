"""
History Panel - Query history with search, favorites, and tags
"""

from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLineEdit, QPushButton, QLabel, QTextEdit, QSplitter, QCheckBox
)
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsMessageLog, Qgis


class HistoryPanel(QWidget):
    """Query history panel with advanced features"""
    
    def __init__(self, iface, config):
        super().__init__()
        self.iface = iface
        self.config = config
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search history...")
        search_layout.addWidget(self.search_input)
        
        filter_btn = QPushButton("Filter")
        search_layout.addWidget(filter_btn)
        
        layout.addLayout(search_layout)
        
        # Splitter for history list and details
        splitter = QSplitter(Qt.Horizontal)
        
        # History list
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #3e4451;
            }
            QListWidget::item:selected {
                background-color: #61afef;
            }
        """)
        splitter.addWidget(self.history_list)
        
        # Details panel
        details_widget = QWidget()
        details_layout = QVBoxLayout()
        details_widget.setLayout(details_layout)
        
        # Query details
        self.query_details = QTextEdit()
        self.query_details.setReadOnly(True)
        self.query_details.setPlaceholderText("Select a query from history to view details")
        details_layout.addWidget(QLabel("Query Details:"))
        details_layout.addWidget(self.query_details)
        
        # Action buttons
        action_layout = QHBoxLayout()
        self.favorite_btn = QPushButton("⭐ Favorite")
        self.reuse_btn = QPushButton("♻️ Reuse")
        self.delete_btn = QPushButton("🗑️ Delete")
        action_layout.addWidget(self.favorite_btn)
        action_layout.addWidget(self.reuse_btn)
        action_layout.addWidget(self.delete_btn)
        details_layout.addLayout(action_layout)
        
        splitter.addWidget(details_widget)
        splitter.setSizes([300, 500])
        
        layout.addWidget(splitter)
        
        # Connect signals
        self.history_list.currentItemChanged.connect(self.on_item_selected)
        self.favorite_btn.clicked.connect(self.toggle_favorite)
        self.reuse_btn.clicked.connect(self.reuse_query)
        self.delete_btn.clicked.connect(self.delete_query)
    
    def on_item_selected(self, item):
        """Handle history item selection"""
        if item:
            # TODO: Load query details
            self.query_details.setText(f"Query: {item.text()}\n\nDetails will be loaded...")
    
    def toggle_favorite(self):
        """Toggle favorite status"""
        QgsMessageLog.logMessage("Toggling favorite", "GeoAI Pro", Qgis.Info)
    
    def reuse_query(self):
        """Reuse selected query"""
        QgsMessageLog.logMessage("Reusing query", "GeoAI Pro", Qgis.Info)
    
    def delete_query(self):
        """Delete selected query"""
        QgsMessageLog.logMessage("Deleting query", "GeoAI Pro", Qgis.Info)

