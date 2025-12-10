"""
Settings Panel - Configuration and settings
"""

from qgis.PyQt.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QMessageBox,
    QGroupBox,
    QFormLayout,
    QSpinBox,
)
from qgis.core import QgsMessageLog, Qgis
import os


class SettingsPanel(QWidget):
    """Settings panel"""

    def __init__(self, iface, config, main_window, image_processor):
        super().__init__()
        self.iface = iface
        self.config = config
        self.main_window = main_window
        self.image_processor = image_processor
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Title
        title = QLabel("⚙️ Settings")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #61afef;")
        layout.addWidget(title)

        # PostgreSQL Database Configuration
        db_group = QGroupBox("🗄️ PostgreSQL Database")
        db_group.setStyleSheet("QGroupBox { font-weight: bold; padding-top: 10px; }")
        db_layout = QFormLayout()

        self.db_host_input = QLineEdit()
        self.db_host_input.setPlaceholderText("localhost")
        db_layout.addRow("Host:", self.db_host_input)

        self.db_port_input = QSpinBox()
        self.db_port_input.setRange(1, 65535)
        self.db_port_input.setValue(5432)
        db_layout.addRow("Port:", self.db_port_input)

        self.db_name_input = QLineEdit()
        self.db_name_input.setPlaceholderText("your_database_name")
        db_layout.addRow("Database:", self.db_name_input)

        self.db_user_input = QLineEdit()
        self.db_user_input.setPlaceholderText("postgres")
        db_layout.addRow("Username:", self.db_user_input)

        self.db_password_input = QLineEdit()
        self.db_password_input.setEchoMode(QLineEdit.Password)
        self.db_password_input.setPlaceholderText("Enter database password...")
        db_layout.addRow("Password:", self.db_password_input)

        db_group.setLayout(db_layout)
        layout.addWidget(db_group)

        # Database buttons
        db_btn_layout = QHBoxLayout()
        save_db_btn = QPushButton("💾 Save Database Settings")
        save_db_btn.setObjectName("primary")
        save_db_btn.clicked.connect(self.save_database_settings)
        db_btn_layout.addWidget(save_db_btn)

        test_db_btn = QPushButton("🔌 Test Connection")
        test_db_btn.clicked.connect(self.test_database_connection)
        db_btn_layout.addWidget(test_db_btn)
        layout.addLayout(db_btn_layout)

        layout.addWidget(QLabel(""))  # Spacer

        # Azure Computer Vision Configuration
        azure_label = QLabel("<b>Azure Computer Vision API:</b>")
        layout.addWidget(azure_label)

        layout.addWidget(QLabel("Endpoint URL:"))
        self.azure_endpoint_input = QLineEdit()
        self.azure_endpoint_input.setPlaceholderText(
            "https://your-endpoint.cognitiveservices.azure.com/"
        )
        layout.addWidget(self.azure_endpoint_input)

        layout.addWidget(QLabel("Subscription Key:"))
        self.azure_key_input = QLineEdit()
        self.azure_key_input.setEchoMode(QLineEdit.Password)
        self.azure_key_input.setPlaceholderText("Enter your Azure subscription key...")
        layout.addWidget(self.azure_key_input)

        save_azure_btn = QPushButton("💾 Save Azure Credentials")
        save_azure_btn.setObjectName("primary")
        save_azure_btn.clicked.connect(self.save_azure_credentials)
        layout.addWidget(save_azure_btn)

        layout.addWidget(QLabel(""))  # Spacer

        # LLM Provider Configuration
        api_label = QLabel("<b>LLM Provider Configuration:</b>")
        layout.addWidget(api_label)

        layout.addWidget(QLabel("API Key (if required):"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText(
            "Enter your API key (not needed for Ollama)..."
        )
        layout.addWidget(self.api_key_input)

        save_api_btn = QPushButton("💾 Save API Key")
        save_api_btn.clicked.connect(self.save_api_key)
        layout.addWidget(save_api_btn)

        layout.addStretch()

    def load_settings(self):
        """Load settings from .env file"""
        plugin_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        env_file = os.path.join(plugin_dir, ".env")

        if os.path.exists(env_file):
            try:
                with open(env_file, "r") as f:
                    for line in f:
                        if line.strip() and not line.startswith("#"):
                            if "=" in line:
                                key, value = line.strip().split("=", 1)
                                # Database settings
                                if key == "DB_HOST":
                                    self.db_host_input.setText(value)
                                elif key == "DB_PORT":
                                    try:
                                        self.db_port_input.setValue(int(value))
                                    except ValueError:
                                        pass
                                elif key == "DB_NAME":
                                    self.db_name_input.setText(value)
                                elif key == "DB_USER":
                                    self.db_user_input.setText(value)
                                elif key == "DB_PASSWORD":
                                    self.db_password_input.setText(value)
                                # Azure settings
                                elif (
                                    "AZURE_ENDPOINT" in key
                                    or "AZURE_VISION_ENDPOINT" in key
                                ):
                                    self.azure_endpoint_input.setText(value)
                                elif (
                                    "AZURE_KEY" in key
                                    or "AZURE_SUBSCRIPTION_KEY" in key
                                ):
                                    self.azure_key_input.setText(value)
            except Exception as e:
                QgsMessageLog.logMessage(
                    f"Error loading settings: {e}", "GeoAI Pro", Qgis.Warning
                )

    def save_database_settings(self):
        """Save database settings to .env file"""
        host = self.db_host_input.text().strip() or "localhost"
        port = str(self.db_port_input.value())
        db_name = self.db_name_input.text().strip()
        user = self.db_user_input.text().strip()
        password = self.db_password_input.text().strip()

        if not db_name or not user:
            QMessageBox.warning(
                self, "Warning", "Please enter at least database name and username"
            )
            return

        plugin_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        env_file = os.path.join(plugin_dir, ".env")

        try:
            # Read existing .env
            env_vars = {}
            if os.path.exists(env_file):
                with open(env_file, "r") as f:
                    for line in f:
                        if line.strip() and not line.startswith("#") and "=" in line:
                            k, v = line.strip().split("=", 1)
                            env_vars[k] = v

            # Update database settings
            env_vars["DB_HOST"] = host
            env_vars["DB_PORT"] = port
            env_vars["DB_NAME"] = db_name
            env_vars["DB_USER"] = user
            env_vars["DB_PASSWORD"] = password

            # Write back
            with open(env_file, "w") as f:
                for k, v in env_vars.items():
                    f.write(f"{k}={v}\n")

            QMessageBox.information(
                self, "Success", "Database settings saved successfully!"
            )
            QgsMessageLog.logMessage("Database settings saved", "GeoAI Pro", Qgis.Info)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")

    def test_database_connection(self):
        """Test database connection"""
        from qgis.PyQt.QtSql import QSqlDatabase

        host = self.db_host_input.text().strip() or "localhost"
        port = self.db_port_input.value()
        db_name = self.db_name_input.text().strip()
        user = self.db_user_input.text().strip()
        password = self.db_password_input.text().strip()

        if not db_name or not user:
            QMessageBox.warning(
                self, "Warning", "Please enter database name and username"
            )
            return

        connection_name = "GeoAI_Test_Connection"
        try:
            if QSqlDatabase.contains(connection_name):
                QSqlDatabase.removeDatabase(connection_name)

            db = QSqlDatabase.addDatabase("QPSQL", connection_name)
            db.setHostName(host)
            db.setPort(port)
            db.setDatabaseName(db_name)
            db.setUserName(user)
            db.setPassword(password)

            if db.open():
                QMessageBox.information(
                    self, "Success", "✅ Database connection successful!"
                )
                db.close()
            else:
                QMessageBox.critical(
                    self, "Error", f"❌ Connection failed: {db.lastError().text()}"
                )

            QSqlDatabase.removeDatabase(connection_name)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Connection error: {str(e)}")

    def save_azure_credentials(self):
        """Save Azure credentials to .env file"""
        endpoint = self.azure_endpoint_input.text().strip()
        key = self.azure_key_input.text().strip()

        if not endpoint or not key:
            QMessageBox.warning(self, "Warning", "Please enter both endpoint and key")
            return

        plugin_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        env_file = os.path.join(plugin_dir, ".env")

        try:
            # Read existing .env
            env_vars = {}
            if os.path.exists(env_file):
                with open(env_file, "r") as f:
                    for line in f:
                        if line.strip() and not line.startswith("#") and "=" in line:
                            k, v = line.strip().split("=", 1)
                            env_vars[k] = v

            # Update Azure credentials (using names expected by image_processor.py)
            env_vars["AZURE_VISION_ENDPOINT"] = endpoint
            env_vars["AZURE_VISION_SUBSCRIPTION_KEY"] = key
            # Also save with alternative names for compatibility
            env_vars["AZURE_COMPUTER_VISION_ENDPOINT"] = endpoint
            env_vars["AZURE_COMPUTER_VISION_SUBSCRIPTION_KEY"] = key

            # Write back
            with open(env_file, "w") as f:
                for k, v in env_vars.items():
                    f.write(f"{k}={v}\n")

            # Reload Azure client
            if self.image_processor:
                self.image_processor.reload_azure_client()

            QMessageBox.information(
                self, "Success", "Azure credentials saved successfully!"
            )
            QgsMessageLog.logMessage("Azure credentials saved", "GeoAI Pro", Qgis.Info)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save credentials: {str(e)}")

    def save_api_key(self):
        """Save API key to .env file"""
        api_key = self.api_key_input.text().strip()

        if not api_key:
            QMessageBox.warning(self, "Warning", "Please enter an API key")
            return

        QMessageBox.information(
            self,
            "Info",
            "API key saving will be implemented based on selected provider",
        )
        QgsMessageLog.logMessage("API key save requested", "GeoAI Pro", Qgis.Info)
