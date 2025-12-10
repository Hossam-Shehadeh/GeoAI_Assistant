"""
Theme Manager - Advanced theme system with animations
"""

from qgis.PyQt.QtWidgets import QWidget
from qgis.PyQt.QtCore import QPropertyAnimation, QEasingCurve


class ThemeManager:
    """Manages UI themes with animations"""
    
    CREATIVE_DARK_THEME = """
        QDockWidget {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #0a0a0a, stop:1 #1a1a2e);
            color: #ededed;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
        }
        
        QTabWidget::pane {
            border: 2px solid #16213e;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #21252b, stop:1 #282c34);
            border-radius: 12px;
        }
        
        QTabBar::tab {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #282c34, stop:1 #21252b);
            color: #abb2bf;
            padding: 14px 28px;
            margin-right: 6px;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            font-size: 14px;
            font-weight: 500;
            min-width: 140px;
        }
        
        QTabBar::tab:selected {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #61afef, stop:1 #528bff);
            color: white;
            border-bottom: 3px solid #61afef;
            font-weight: 600;
        }
        
        QTabBar::tab:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #3e4451, stop:1 #2d3139);
            color: #e6e6e6;
        }
        
        QTextEdit, QLineEdit {
            background-color: #1e2227;
            border: 2px solid #3e4451;
            border-radius: 8px;
            padding: 12px;
            color: #e6e6e6;
            font-size: 14px;
            selection-background-color: #61afef;
        }
        
        QTextEdit:focus, QLineEdit:focus {
            border: 2px solid #61afef;
            background-color: #252932;
            box-shadow: 0 0 10px rgba(97, 175, 239, 0.3);
        }
        
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #3e4451, stop:1 #282c34);
            border: 2px solid #61afef;
            border-radius: 8px;
            padding: 12px 24px;
            color: #e6e6e6;
            font-size: 14px;
            font-weight: 600;
            min-height: 40px;
        }
        
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #61afef, stop:1 #528bff);
            color: white;
            border-color: #528bff;
            transform: translateY(-2px);
        }
        
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #528bff, stop:1 #61afef);
            transform: translateY(0px);
        }
        
        QPushButton#primary {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #61afef, stop:1 #528bff);
            border: none;
            color: white;
        }
        
        QPushButton#success {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #98c379, stop:1 #85ad68);
            border: none;
            color: white;
        }
        
        QPushButton#warning {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #e5c07b, stop:1 #ccab6c);
            border: none;
            color: white;
        }
        
        QTableWidget {
            background-color: #1e2227;
            border: 2px solid #3e4451;
            border-radius: 8px;
            gridline-color: #3e4451;
            color: #e6e6e6;
            alternate-background-color: #252932;
        }
        
        QTableWidget::item {
            padding: 10px;
            border-bottom: 1px solid #3e4451;
        }
        
        QTableWidget::item:selected {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #61afef, stop:1 #528bff);
            color: white;
        }
        
        QProgressBar {
            background-color: #1e2227;
            border: 2px solid #3e4451;
            border-radius: 8px;
            text-align: center;
            color: #e6e6e6;
            height: 8px;
        }
        
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #61afef, stop:1 #528bff);
            border-radius: 6px;
        }
        
        QTextEdit#sqlOutput {
            background-color: #0d1117;
            color: #58a6ff;
            font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
            font-size: 13px;
            border: 2px solid #21262d;
            border-radius: 8px;
        }
    """
    
    def __init__(self):
        self.current_theme = "dark"
    
    def apply_theme(self, theme_name: str):
        """Apply theme by name"""
        self.current_theme = theme_name
    
    def apply_to_widget(self, widget: QWidget):
        """Apply current theme to widget"""
        if self.current_theme == "dark":
            widget.setStyleSheet(self.CREATIVE_DARK_THEME)
        else:
            # Light theme would go here
            widget.setStyleSheet(self.CREATIVE_DARK_THEME)
