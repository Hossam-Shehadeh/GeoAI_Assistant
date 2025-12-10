"""
Smart Assistant Panel - Intelligent QGIS suggestions
"""

from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, 
    QLabel, QComboBox, QMessageBox
)
from qgis.PyQt.QtCore import QThread, pyqtSignal
from qgis.core import QgsMessageLog, Qgis


class WorkerThread(QThread):
    """Worker thread for smart assistant"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            # Convert list to dict if needed (get_suggestions returns List[str])
            if isinstance(result, list):
                result = {"suggestions": result, "type": "list"}
            # Ensure result is a dict
            if not isinstance(result, dict):
                result = {"suggestions": str(result), "type": "string"}
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class SmartAssistantPanel(QWidget):
    """Smart assistant panel"""
    
    def __init__(self, iface, config, main_window, smart_assistant):
        super().__init__()
        self.iface = iface
        self.config = config
        self.main_window = main_window
        self.smart_assistant = smart_assistant
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title = QLabel("💡 Smart Assistant")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #61afef;")
        layout.addWidget(title)
        
        desc = QLabel("Get intelligent suggestions for your QGIS project and layers.")
        desc.setStyleSheet("color: #abb2bf;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Analysis type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Analysis Type:"))
        self.analysis_type = QComboBox()
        self.analysis_type.addItems([
            "Project Overview",
            "Selected Layer",
            "All Layers",
            "Custom Query"
        ])
        type_layout.addWidget(self.analysis_type)
        type_layout.addStretch()
        layout.addLayout(type_layout)
        
        # Get suggestions button
        suggest_btn = QPushButton("✨ Get Suggestions")
        suggest_btn.setObjectName("primary")
        suggest_btn.clicked.connect(self.get_suggestions)
        layout.addWidget(suggest_btn)
        
        # Suggestions output
        output_label = QLabel("Suggestions:")
        layout.addWidget(output_label)
        
        self.suggestions_output = QTextEdit()
        self.suggestions_output.setReadOnly(True)
        layout.addWidget(self.suggestions_output)
    
    def get_suggestions(self):
        """Get smart suggestions"""
        try:
            if not self.smart_assistant:
                QMessageBox.critical(self, "Error", "Smart assistant not initialized")
                return
            
            if not hasattr(self.main_window, 'model_selector'):
                QMessageBox.critical(self, "Error", "Model selector not available")
                return
            
            provider = self.main_window.model_selector.get_provider()
            model = self.main_window.model_selector.get_model()
            
            # Run in thread
            self.worker = WorkerThread(
                self.smart_assistant.get_suggestions,
                provider,
                model
            )
            self.worker.finished.connect(self.on_suggestions_received)
            self.worker.error.connect(self.on_error)
            self.worker.start()
            
            QgsMessageLog.logMessage(
                f"Getting smart suggestions with {provider}/{model}", 
                "GeoAI Pro", 
                Qgis.Info
            )
        except Exception as e:
            import traceback
            error_msg = f"Error starting smart assistant: {str(e)}\n{traceback.format_exc()}"
            QgsMessageLog.logMessage(error_msg, "GeoAI Pro", Qgis.Critical)
            QMessageBox.critical(self, "Error", f"Failed to get suggestions:\n{str(e)}")
            self.suggestions_output.setText(f"ERROR: {str(e)}")
    
    def on_suggestions_received(self, result):
        """Handle suggestions result"""
        if not isinstance(result, dict):
            # Fallback: convert to dict
            result = {"suggestions": str(result), "type": "string"}
        
        if "error" in result:
            QMessageBox.critical(self, "Error", result["error"])
            self.suggestions_output.setText(f"ERROR: {result['error']}")
        else:
            suggestions = result.get("suggestions", "")
            # If suggestions is a list, format it
            if isinstance(suggestions, list):
                suggestions_text = "\n".join([f"• {s}" for s in suggestions])
                self.suggestions_output.setText(suggestions_text)
            else:
                self.suggestions_output.setText(str(suggestions))
            QgsMessageLog.logMessage("Suggestions received", "GeoAI Pro", Qgis.Info)
    
    def on_error(self, error_msg):
        """Handle error"""
        QMessageBox.critical(self, "Error", error_msg)
        self.suggestions_output.setText(f"ERROR: {error_msg}")

