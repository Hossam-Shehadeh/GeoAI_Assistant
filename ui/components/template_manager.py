"""
Template Manager - Create and manage custom prompt templates
"""

from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QTextEdit, QLineEdit, QSplitter
)
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsMessageLog, Qgis


class TemplateManager(QWidget):
    """Template management interface"""
    
    def __init__(self, iface, config):
        super().__init__()
        self.iface = iface
        self.config = config
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title and actions
        header_layout = QHBoxLayout()
        title = QLabel("📝 Template Manager")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #61afef;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        new_btn = QPushButton("➕ New Template")
        new_btn.clicked.connect(self.create_template)
        header_layout.addWidget(new_btn)
        
        layout.addLayout(header_layout)
        
        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Template list
        self.template_list = QListWidget()
        self.template_list.addItems(["Default SQL Template", "Spatial Analysis", "Data Cleaning"])
        splitter.addWidget(self.template_list)
        
        # Template editor
        editor_widget = QWidget()
        editor_layout = QVBoxLayout()
        editor_widget.setLayout(editor_layout)
        
        editor_layout.addWidget(QLabel("Template Name:"))
        self.template_name = QLineEdit()
        editor_layout.addWidget(self.template_name)
        
        editor_layout.addWidget(QLabel("Template Content:"))
        self.template_content = QTextEdit()
        self.template_content.setPlaceholderText(
            "Enter template with variables like {layer_name}, {operation}, etc.\n\n"
            "Example:\n"
            "Generate SQL to {operation} on layer {layer_name}\n"
            "Filter by: {filter_condition}"
        )
        editor_layout.addWidget(self.template_content)
        
        # Save button
        save_btn = QPushButton("💾 Save Template")
        save_btn.clicked.connect(self.save_template)
        editor_layout.addWidget(save_btn)
        
        splitter.addWidget(editor_widget)
        splitter.setSizes([200, 600])
        
        layout.addWidget(splitter)
    
    def create_template(self):
        """Create new template"""
        self.template_name.clear()
        self.template_content.clear()
        QgsMessageLog.logMessage("Creating new template", "GeoAI Pro", Qgis.Info)
    
    def save_template(self):
        """Save template"""
        name = self.template_name.text()
        content = self.template_content.toPlainText()
        if name and content:
            QgsMessageLog.logMessage(f"Saving template: {name}", "GeoAI Pro", Qgis.Info)
            # TODO: Save to storage

