"""
Model Selector Component - Enhanced with provider status and health
"""

from qgis.PyQt.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QComboBox, QPushButton
)
from qgis.PyQt.QtCore import pyqtSignal, QThread, QTimer
from qgis.PyQt.QtGui import QColor
from qgis.core import QgsMessageLog, Qgis
import os


class ModelTester(QThread):
    """Thread to test model availability with timeout"""
    model_tested = pyqtSignal(str, bool, str)  # model_name, is_working, error_message
    
    def __init__(self, llm_handler, provider, model, timeout=10):
        super().__init__()
        self.llm_handler = llm_handler
        self.provider = provider
        self.model = model
        self.timeout = timeout
    
    def run(self):
        """Test if model works with timeout"""
        try:
            # Simple test prompt
            test_prompt = "OK"
            
            # For Google, check API key first
            if self.provider == "google":
                api_key = os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    self.model_tested.emit(self.model, False, "API key not found")
                    return
                # Use minimal prompt for Google
                test_prompt = "OK"
            
            result = self.llm_handler._query_with_provider(
                test_prompt,
                system_prompt=None,
                model_provider=self.provider,
                model_name=self.model
            )
            
            if result and len(result) > 0:
                self.model_tested.emit(self.model, True, "")
            else:
                self.model_tested.emit(self.model, False, "Empty response")
        except Exception as e:
            error_msg = str(e)
            # Don't fail on quota errors - model works but quota exceeded
            if "quota" in error_msg.lower() or "429" in error_msg:
                self.model_tested.emit(self.model, True, "Quota exceeded (model works)")
            elif "timeout" in error_msg.lower():
                self.model_tested.emit(self.model, False, "Test timeout")
            else:
                self.model_tested.emit(self.model, False, error_msg)


class ModelSelector(QWidget):
    """Enhanced model selector with provider health and model validation"""
    
    provider_changed = pyqtSignal(str)
    model_changed = pyqtSignal(str)
    
    def __init__(self, config, llm_handler=None):
        super().__init__()
        self.config = config
        self.llm_handler = llm_handler
        self.model_status = {}  # Track which models work: {model_name: (is_working, error)}
        self.testers = []  # Keep track of test threads
        self.setup_ui()
    
    def set_llm_handler(self, llm_handler):
        """Set LLM handler for testing"""
        self.llm_handler = llm_handler
    
    def setup_ui(self):
        """Setup UI"""
        layout = QHBoxLayout()
        layout.setSpacing(12)
        self.setLayout(layout)
        
        # Provider selector with icon
        layout.addWidget(QLabel("🤖 Provider:"))
        self.provider_combo = QComboBox()
        self.provider_combo.addItems([
            "Ollama", "OpenAI", "Anthropic", "Google", 
            "OpenRouter", "HuggingFace"
        ])
        self.provider_combo.setCurrentText(
            self.config.get("llm_provider", "Ollama").title()
        )
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        layout.addWidget(self.provider_combo)
        
        # Status indicator
        self.status_indicator = QLabel("🟢")
        self.status_indicator.setToolTip("Provider status")
        layout.addWidget(self.status_indicator)
        
        # Model selector
        layout.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self.update_models()
        self.model_combo.setCurrentText(
            self.config.get("llm_model", "phi3")
        )
        self.model_combo.currentTextChanged.connect(
            lambda x: self.model_changed.emit(x)
        )
        layout.addWidget(self.model_combo)
        
        # Test connection button
        self.test_btn = QPushButton("🔌 Test")
        self.test_btn.setMaximumWidth(60)
        self.test_btn.clicked.connect(self.test_connection)
        layout.addWidget(self.test_btn)
        
        layout.addStretch()
    
    def on_provider_changed(self, provider):
        """Handle provider change"""
        provider_lower = provider.lower()
        
        # Update models first (synchronous, fast)
        self.update_models()
        
        # Emit signal
        self.provider_changed.emit(provider_lower)
        
        # Check provider health (synchronous, fast - just checks env vars)
        self.check_provider_health()
        
        # For Google, skip all testing and mark as ready immediately
        if provider_lower == "google":
            # Immediately mark all models as available
            for i in range(self.model_combo.count()):
                model = self.model_combo.itemText(i)
                key = f"{provider_lower}:{model}"
                self.model_status[key] = (True, "Available (not tested)")
            
            # Update UI immediately
            self.apply_model_status()
            
            QgsMessageLog.logMessage(
                "Google provider selected - models available (use Test button to verify)",
                "GeoAI Pro",
                Qgis.Info
            )
            return  # Exit early, no testing
        
        # For other providers, test models (async, non-blocking)
        if self.llm_handler:
            # Use QTimer.singleShot to test models after UI updates
            QTimer.singleShot(500, self.test_all_models)  # Test after 500ms
    
    def update_models(self):
        """Update available models"""
        provider = self.provider_combo.currentText().lower()
        
        models = {
            "ollama": ["phi3", "mistral", "llama2", "llama3", "codellama", "llava"],
            "openai": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
            "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229"],
            "google": ["models/gemini-pro-latest", "models/gemini-2.5-pro", "models/gemini-2.5-flash"],
            "openrouter": ["mistralai/mistral-7b-instruct", "openai/gpt-4o-mini"],
            "huggingface": ["HuggingFaceH4/zephyr-7b-beta", "mistralai/Mistral-7B-Instruct-v0.2"]
        }
        
        self.model_combo.clear()
        models_list = models.get(provider, ["phi3"])
        
        # Add models and mark as untested initially
        for model in models_list:
            self.model_combo.addItem(model)
            # Set as enabled by default, will be disabled if test fails
            self.model_combo.setItemData(
                self.model_combo.count() - 1, 
                True, 
                role=0x0100  # UserRole - enabled
            )
        
        # If we have status for models, apply it
        self.apply_model_status()
    
    def apply_model_status(self):
        """Apply model status to combo box items"""
        provider = self.provider_combo.currentText().lower()
        
        for i in range(self.model_combo.count()):
            model = self.model_combo.itemText(i)
            key = f"{provider}:{model}"
            
            # Get the item from the model
            item = self.model_combo.model().item(i)
            if not item:
                continue
            
            if key in self.model_status:
                is_working, error = self.model_status[key]
                
                if not is_working:
                    # Disable the item
                    item.setEnabled(False)
                    # Add indicator to tooltip
                    tooltip = f"❌ Not available: {error[:50] if error else 'Unknown error'}"
                    item.setToolTip(tooltip)
                    # Gray out the text
                    item.setForeground(QColor(128, 128, 128))  # Gray color
                else:
                    # Enable the item
                    item.setEnabled(True)
                    if error and "quota" in error.lower():
                        tooltip = f"⚠️ Works but quota exceeded"
                        item.setToolTip(tooltip)
                    else:
                        tooltip = f"✅ Available"
                        item.setToolTip(tooltip)
                    # Reset text color to default (black/white depending on theme)
                    item.setForeground(QColor())  # Default color
            else:
                # Not tested yet, enable by default
                item.setEnabled(True)
                item.setToolTip("🔄 Testing...")
                item.setForeground(QColor())  # Default color
    
    def test_all_models(self):
        """Test all models for current provider"""
        if not self.llm_handler:
            return
        
        provider = self.provider_combo.currentText().lower()
        
        # Skip automatic testing for Google (can be slow/hang)
        # User can manually test if needed
        if provider == "google":
            QgsMessageLog.logMessage(
                "Skipping automatic model testing for Google (use Test button to verify)",
                "GeoAI Pro",
                Qgis.Info
            )
            # Mark all models as available by default for Google
            for i in range(self.model_combo.count()):
                model = self.model_combo.itemText(i)
                key = f"{provider}:{model}"
                self.model_status[key] = (True, "Not tested (use Test button)")
            self.apply_model_status()
            return
        
        # Cancel any existing testers
        for tester in self.testers:
            if tester.isRunning():
                tester.terminate()
                tester.wait(1000)  # Wait up to 1 second
        self.testers.clear()
        
        # Test each model with shorter timeout for cloud providers
        timeout = 15 if provider in ["openai", "anthropic", "openrouter"] else 10
        
        # Test each model
        for i in range(self.model_combo.count()):
            model = self.model_combo.itemText(i)
            
            # Create tester thread with timeout
            tester = ModelTester(self.llm_handler, provider, model, timeout=timeout)
            tester.model_tested.connect(self.on_model_tested)
            tester.finished.connect(tester.deleteLater)
            self.testers.append(tester)
            tester.start()
            
            # Update UI to show testing
            item = self.model_combo.model().item(i)
            if item:
                item.setToolTip("🔄 Testing...")
        
        # Set a timeout to mark as failed if still testing after timeout
        QTimer.singleShot((timeout + 5) * 1000, self.mark_timeout_models)
    
    def mark_timeout_models(self):
        """Mark models that are still testing as timeout"""
        provider = self.provider_combo.currentText().lower()
        for i in range(self.model_combo.count()):
            model = self.model_combo.itemText(i)
            key = f"{provider}:{model}"
            if key not in self.model_status:
                # Still testing, mark as timeout
                self.model_status[key] = (False, "Test timeout")
                self.apply_model_status()
    
    def on_model_tested(self, model_name, is_working, error_message):
        """Handle model test result"""
        provider = self.provider_combo.currentText().lower()
        key = f"{provider}:{model_name}"
        
        # Store status
        self.model_status[key] = (is_working, error_message)
        
        # Update UI
        self.apply_model_status()
        
        # Log result
        status = "✅" if is_working else "❌"
        QgsMessageLog.logMessage(
            f"{status} Model {model_name} ({provider}): {'Working' if is_working else error_message}",
            "GeoAI Pro",
            Qgis.Info if is_working else Qgis.Warning
        )
    
    def check_provider_health(self):
        """Check provider health status"""
        provider = self.provider_combo.currentText().lower()
        
        # Check if provider is configured
        if provider == "ollama":
            self.status_indicator.setText("🟢")
            self.status_indicator.setToolTip("Ollama (local)")
        elif provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.status_indicator.setText("🟢")
                self.status_indicator.setToolTip("OpenAI configured")
            else:
                self.status_indicator.setText("🔴")
                self.status_indicator.setToolTip("OpenAI API key not found")
        elif provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.status_indicator.setText("🟢")
                self.status_indicator.setToolTip("Anthropic configured")
            else:
                self.status_indicator.setText("🔴")
                self.status_indicator.setToolTip("Anthropic API key not found")
        elif provider == "google":
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                self.status_indicator.setText("🟢")
                self.status_indicator.setToolTip("Google configured")
            else:
                self.status_indicator.setText("🔴")
                self.status_indicator.setToolTip("Google API key not found")
        elif provider == "openrouter":
            api_key = os.getenv("OPENROUTER_API_KEY")
            if api_key:
                self.status_indicator.setText("🟢")
                self.status_indicator.setToolTip("OpenRouter configured")
            else:
                self.status_indicator.setText("🔴")
                self.status_indicator.setToolTip("OpenRouter API key not found")
        elif provider == "huggingface":
            api_key = os.getenv("HUGGINGFACE_API_KEY")
            if api_key:
                self.status_indicator.setText("🟢")
                self.status_indicator.setToolTip("HuggingFace configured")
            else:
                self.status_indicator.setText("🔴")
                self.status_indicator.setToolTip("HuggingFace API key not found")
    
    def test_connection(self):
        """Test connection to provider and selected model"""
        provider = self.provider_combo.currentText()
        model = self.model_combo.currentText()
        
        if not self.llm_handler:
            QgsMessageLog.logMessage(
                "LLM handler not available for testing", 
                "GeoAI Pro", 
                Qgis.Warning
            )
            return
        
        QgsMessageLog.logMessage(
            f"Testing connection to {provider}/{model}", 
            "GeoAI Pro", 
            Qgis.Info
        )
        
        self.status_indicator.setText("🟡")
        self.test_btn.setEnabled(False)
        
        # Test the selected model
        tester = ModelTester(self.llm_handler, provider.lower(), model)
        tester.model_tested.connect(self.on_single_test_complete)
        tester.finished.connect(tester.deleteLater)
        tester.start()
    
    def on_single_test_complete(self, model_name, is_working, error_message):
        """Handle single model test completion"""
        self.test_btn.setEnabled(True)
        
        if is_working:
            self.status_indicator.setText("🟢")
            QgsMessageLog.logMessage(
                f"✅ {model_name} is working", 
                "GeoAI Pro", 
                Qgis.Success
            )
        else:
            self.status_indicator.setText("🔴")
            QgsMessageLog.logMessage(
                f"❌ {model_name} failed: {error_message}", 
                "GeoAI Pro", 
                Qgis.Warning
            )
    
    def get_provider(self) -> str:
        """Get selected provider"""
        return self.provider_combo.currentText().lower()
    
    def get_model(self) -> str:
        """Get selected model"""
        return self.model_combo.currentText()
