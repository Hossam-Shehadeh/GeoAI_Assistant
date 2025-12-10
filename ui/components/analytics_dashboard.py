"""
Analytics Dashboard - Performance metrics and usage statistics
"""

from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
)
from qgis.core import QgsMessageLog, Qgis


class AnalyticsDashboard(QWidget):
    """Analytics dashboard with metrics and charts"""
    
    def __init__(self, iface, config):
        super().__init__()
        self.iface = iface
        self.config = config
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title = QLabel("📊 Analytics Dashboard")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #61afef;")
        layout.addWidget(title)
        
        # Metrics grid
        metrics_grid = QGridLayout()
        
        # Metric cards
        metrics = [
            ("Total Queries", "1,234", "#61afef"),
            ("Success Rate", "98.5%", "#98c379"),
            ("Avg Response", "2.3s", "#e5c07b"),
            ("Cost Today", "$0.45", "#e06c75")
        ]
        
        for i, (label, value, color) in enumerate(metrics):
            card = self.create_metric_card(label, value, color)
            metrics_grid.addWidget(card, i // 2, i % 2)
        
        layout.addLayout(metrics_grid)
        
        # Charts placeholder
        charts_label = QLabel("📈 Charts and graphs will be displayed here")
        charts_label.setStyleSheet("padding: 40px; color: #abb2bf;")
        layout.addWidget(charts_label)
    
    def create_metric_card(self, label, value, color):
        """Create a metric card"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #282c34;
                border: 2px solid {color};
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        
        layout = QVBoxLayout()
        card.setLayout(layout)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 32px; font-weight: 700; color: {color};")
        layout.addWidget(value_label)
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet("font-size: 14px; color: #abb2bf;")
        layout.addWidget(label_widget)
        
        return card

