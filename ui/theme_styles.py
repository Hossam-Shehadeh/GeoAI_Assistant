"""
Theme Styles - Dark theme from spatial-projects with enhancements
"""

DARK_THEME_STYLES = """
    QDockWidget {
        background-color: #0a0a0a;
        color: #ededed;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    }
    
    QTabWidget::pane {
        border: 1px solid #282c34;
        background-color: #21252b;
        border-radius: 8px;
    }
    
    QTabBar::tab {
        background-color: #282c34;
        color: #abb2bf;
        padding: 12px 25px;
        margin-right: 4px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        font-size: 13px;
        font-weight: 500;
        min-width: 120px;
    }
    
    QTabBar::tab:selected {
        background-color: #21252b;
        color: #e6e6e6;
        border-bottom: 2px solid #61afef;
    }
    
    QTabBar::tab:hover {
        background-color: #3e4451;
        color: #e6e6e6;
    }
    
    QLabel {
        color: #e6e6e6;
        font-size: 13px;
    }
    
    QLabel#mainHeader {
        font-size: 24px;
        font-weight: 700;
        color: #61afef;
        margin: 8px 0;
    }

    QLabel#mainSubtitle {
        color: #abb2bf;
        font-size: 13px;
    }

    QLabel.cardTitle {
        font-size: 15px;
        font-weight: 600;
        color: #e6e6e6;
    }

    QLabel.tabTitle {
        font-size: 20px;
        font-weight: 700;
        color: #e6e6e6;
    }
    
    QTextEdit, QLineEdit {
        background-color: #282c34;
        border: 1px solid #3e4451;
        border-radius: 6px;
        padding: 10px;
        color: #e6e6e6;
        font-size: 13px;
        selection-background-color: #61afef;
    }
    
    QTextEdit:focus, QLineEdit:focus {
        border: 1px solid #61afef;
        outline: none;
    }
    
    QComboBox {
        background-color: #282c34;
        border: 1px solid #3e4451;
        border-radius: 6px;
        padding: 8px 12px;
        color: #e6e6e6;
        font-size: 13px;
        min-height: 24px;
    }
    
    QComboBox:hover {
        border-color: #61afef;
    }
    
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    
    QComboBox::down-arrow {
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid #abb2bf;
        margin-right: 5px;
    }
    
    QComboBox QAbstractItemView {
        background-color: #21252b;
        border: 1px solid #282c34;
        selection-background-color: #61afef;
        color: #e6e6e6;
        padding: 4px;
    }
    
    QPushButton {
        background-color: #282c34;
        border: 1px solid #3e4451;
        border-radius: 6px;
        padding: 10px 16px;
        color: #e6e6e6;
        font-size: 13px;
        font-weight: 500;
        min-height: 20px;
    }
    
    QPushButton:hover {
        background-color: #3e4451;
        border-color: #61afef;
    }
    
    QPushButton:pressed {
        background-color: #4b5262;
    }
    
    QPushButton.primary {
        background-color: #61afef;
        border: 1px solid #528bff;
        color: white;
    }
    
    QPushButton.primary:hover {
        background-color: #528bff;
    }
    
    QPushButton.success {
        background-color: #98c379;
        border: 1px solid #85ad68;
        color: white;
    }
    
    QPushButton.success:hover {
        background-color: #85ad68;
    }
    
    QPushButton.warning {
        background-color: #e5c07b;
        border: 1px solid #ccab6c;
        color: white;
    }
    
    QPushButton.warning:hover {
        background-color: #ccab6c;
    }
    
    QTableWidget {
        background-color: #282c34;
        border: 1px solid #3e4451;
        border-radius: 6px;
        gridline-color: #3e4451;
        color: #e6e6e6;
    }
    
    QTableWidget::item {
        padding: 8px;
        border-bottom: 1px solid #3e4451;
    }
    
    QTableWidget::item:selected {
        background-color: #61afef;
        color: white;
    }
    
    QHeaderView::section {
        background-color: #21252b;
        color: #abb2bf;
        padding: 8px;
        border: none;
        border-bottom: 1px solid #3e4451;
        font-weight: 600;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    QProgressBar {
        background-color: #282c34;
        border: 1px solid #3e4451;
        border-radius: 4px;
        text-align: center;
        color: #e6e6e6;
        height: 6px;
    }
    
    QProgressBar::chunk {
        background-color: #61afef;
        border-radius: 3px;
    }
    
    QCheckBox {
        color: #e6e6e6;
        spacing: 8px;
    }
    
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 1px solid #3e4451;
        background-color: #282c34;
    }
    
    QCheckBox::indicator:checked {
        background-color: #61afef;
        border-color: #61afef;
    }
    
    QScrollBar:vertical {
        background-color: #21252b;
        width: 12px;
        margin: 0px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #3e4451;
        border-radius: 6px;
        min-height: 30px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #61afef;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    QGroupBox {
        background-color: #282c34;
        border: 1px solid #3e4451;
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 24px;
        font-weight: 600;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 8px;
        color: #e6e6e6;
    }
    
    QMessageBox {
        background-color: #21252b;
        color: #e6e6e6;
        font-size: 13px;
    }
    
    QMessageBox QLabel {
        color: #e6e6e6;
    }
    
    QMessageBox QPushButton {
        background-color: #61afef;
        color: #e6e6e6;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
    }
    
    QMessageBox QPushButton:hover {
        background-color: #528bff;
    }
    
    QTextEdit#sqlOutput, QTextEdit#modelCodeOutput, QTextEdit#errorSqlInput {
        background-color: #1e2227;
        color: #98c379;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    }

    QTextEdit#errorSqlInput {
        color: #e06c75;
    }

    QLabel#statusLabel.error {
        color: #e06c75;
    }

    QLabel#statusLabel.success {
        color: #98c379;
    }

    QLabel#statusLabel.warning {
        color: #e5c07b;
    }
"""

