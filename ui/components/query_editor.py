"""
Query Editor Component - Enhanced SQL generation with modern UI
"""

from qgis.PyQt.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QTableWidget,
    QMessageBox,
    QFrame,
    QSplitter,
    QComboBox,
    QCheckBox,
    QTableWidgetItem,
)
from qgis.PyQt.QtCore import Qt, QThread, pyqtSignal
from qgis.core import QgsMessageLog, Qgis


class QueryEditor(QWidget):
    """Enhanced query editor with modern features"""

    def __init__(
        self,
        iface,
        config,
        main_window,
        llm_handler=None,
        sql_executor=None,
        error_fixer=None,
    ):
        super().__init__()
        self.iface = iface
        self.config = config
        self.main_window = main_window
        self.llm_handler = llm_handler
        self.sql_executor = sql_executor
        self.error_fixer = error_fixer
        self.setup_ui()

    def setup_ui(self):
        """Setup enhanced UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        self.setLayout(layout)

        # Quick actions bar
        actions_bar = QHBoxLayout()

        # Quick templates
        template_combo = QComboBox()
        template_combo.addItems(
            [
                "Select template...",
                "📍 Find features near...",
                "📊 Aggregate by category",
                "🔍 Filter by attribute",
                "📐 Calculate geometry",
                "🔗 Join tables",
            ]
        )
        template_combo.currentTextChanged.connect(self.apply_template)
        actions_bar.addWidget(QLabel("Quick Start:"))
        actions_bar.addWidget(template_combo)
        actions_bar.addStretch()

        layout.addLayout(actions_bar)

        # Main splitter for all sections (vertical)
        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.setChildrenCollapsible(False)

        # Input section
        input_widget = QWidget()
        input_layout = QVBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_widget.setLayout(input_layout)

        input_header = QHBoxLayout()
        input_header.addWidget(QLabel("💬 Describe Your Query:"))
        input_header.addStretch()

        # AI suggestions button
        suggest_btn = QPushButton("✨ Get Suggestions")
        suggest_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #98c379;
                color: white;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #85ad68;
            }
        """
        )
        suggest_btn.clicked.connect(self.get_suggestions)
        input_header.addWidget(suggest_btn)

        input_layout.addLayout(input_header)

        self.input = QTextEdit()
        self.input.setPlaceholderText(
            "Example: Find all buildings within 500 meters of parks\n"
            "Example: Calculate total area by category\n"
            "Example: Select points that intersect with selected polygon"
        )
        self.input.setMinimumHeight(80)
        input_layout.addWidget(self.input)

        main_splitter.addWidget(input_widget)

        # Output section
        output_widget = QWidget()
        output_layout = QVBoxLayout()
        output_layout.setContentsMargins(0, 0, 0, 0)
        output_widget.setLayout(output_layout)

        output_header = QHBoxLayout()
        output_header.addWidget(QLabel("📝 SQL Query:"))
        output_header.addStretch()

        # Direct SQL mode toggle
        self.direct_mode_check = QCheckBox("✏️ Direct SQL Mode")
        self.direct_mode_check.setToolTip(
            "Enable to write and execute SQL directly without AI generation"
        )
        self.direct_mode_check.toggled.connect(self.toggle_direct_mode)
        output_header.addWidget(self.direct_mode_check)

        # Copy button
        copy_btn = QPushButton("📋 Copy")
        copy_btn.clicked.connect(self.copy_sql)
        output_header.addWidget(copy_btn)

        output_layout.addLayout(output_header)

        self.sql_output = QTextEdit()
        self.sql_output.setObjectName("sqlOutput")
        self.sql_output.setReadOnly(True)
        self.sql_output.setPlaceholderText(
            "-- AI-generated SQL will appear here\n"
            "-- Or enable 'Direct SQL Mode' to write your own SQL\n\n"
            "-- Example:\n"
            "SELECT * FROM your_table LIMIT 10;"
        )
        self.sql_output.setMinimumHeight(120)
        output_layout.addWidget(self.sql_output, 1)  # Stretch factor 1

        # Action buttons
        button_layout = QHBoxLayout()

        self.generate_btn = QPushButton("🚀 Generate SQL")
        self.generate_btn.setObjectName("primary")
        self.generate_btn.clicked.connect(self.generate_sql)
        button_layout.addWidget(self.generate_btn)

        self.execute_btn = QPushButton("▶️ Execute")
        self.execute_btn.setObjectName("success")
        self.execute_btn.clicked.connect(self.execute_sql)
        self.execute_btn.setEnabled(True)  # Always enabled for direct SQL mode
        button_layout.addWidget(self.execute_btn)

        self.auto_fix_btn = QPushButton("🔧 Auto-Fix")
        self.auto_fix_btn.setObjectName("warning")
        self.auto_fix_btn.clicked.connect(self.auto_fix)
        button_layout.addWidget(self.auto_fix_btn)

        output_layout.addLayout(button_layout)

        main_splitter.addWidget(output_widget)

        # Results section as part of splitter
        results_widget = QWidget()
        results_layout = QVBoxLayout()
        results_layout.setContentsMargins(0, 0, 0, 0)
        results_widget.setLayout(results_layout)

        results_label = QLabel("📊 Results:")
        results_label.setStyleSheet("font-weight: 600;")
        results_layout.addWidget(results_label)

        self.results_table = QTableWidget()
        self.results_table.setMinimumHeight(100)
        results_layout.addWidget(self.results_table, 1)  # Stretch factor 1

        main_splitter.addWidget(results_widget)

        # Set initial splitter sizes (input: 150, sql: 200, results: 250)
        main_splitter.setSizes([150, 250, 300])
        main_splitter.setStretchFactor(0, 1)  # Input can stretch
        main_splitter.setStretchFactor(1, 2)  # SQL output stretches more
        main_splitter.setStretchFactor(2, 3)  # Results stretches most

        layout.addWidget(main_splitter, 1)  # Splitter takes all available space

        # Status label for feedback
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(
            "color: #98c379; font-size: 12px; padding: 8px;"
        )
        layout.addWidget(self.status_label)

    def apply_template(self, template):
        """Apply quick template"""
        if template == "Select template...":
            return

        templates = {
            "📍 Find features near...": "Find all features within {distance} meters of {target_layer}",
            "📊 Aggregate by category": "Calculate total {metric} grouped by {category_field}",
            "🔍 Filter by attribute": "Select all features where {field} {operator} {value}",
            "📐 Calculate geometry": "Calculate {geometry_property} for all features",
            "🔗 Join tables": "Join {table1} with {table2} on {join_field}",
        }

        if template in templates:
            self.input.setText(templates[template])

    def toggle_direct_mode(self, enabled):
        """Toggle direct SQL mode"""
        self.sql_output.setReadOnly(not enabled)
        if enabled:
            self.sql_output.setStyleSheet(
                """
                QTextEdit {
                    background-color: #1e1e2e;
                    color: #cdd6f4;
                    border: 2px solid #89b4fa;
                    border-radius: 6px;
                    padding: 8px;
                    font-family: 'Consolas', 'Courier New', monospace;
                }
            """
            )
            self.sql_output.setPlaceholderText(
                "-- Write your SQL query here directly\n"
                "-- Example:\n"
                "SELECT * FROM your_table LIMIT 10;\n\n"
                "-- You can run CREATE, INSERT, UPDATE, DELETE, etc."
            )
            self.status_label.setText(
                "✏️ Direct SQL Mode - Write your SQL and click Execute"
            )
            self.status_label.setStyleSheet(
                "color: #89b4fa; font-size: 12px; padding: 8px;"
            )
        else:
            self.sql_output.setStyleSheet("")
            self.sql_output.setPlaceholderText(
                "-- AI-generated SQL will appear here\n"
                "-- Or enable 'Direct SQL Mode' to write your own SQL"
            )
            self.status_label.setText("Ready")
            self.status_label.setStyleSheet(
                "color: #98c379; font-size: 12px; padding: 8px;"
            )

    def get_suggestions(self):
        """Get AI suggestions"""
        QgsMessageLog.logMessage("Getting AI suggestions", "GeoAI Pro", Qgis.Info)
        # TODO: Implement suggestions

    def generate_sql(self):
        """Generate SQL"""
        prompt = self.input.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Warning", "Please enter a description")
            return

        if not self.llm_handler or not self.sql_executor:
            QMessageBox.critical(
                self, "Error", "LLM handler or SQL executor not initialized"
            )
            return

        provider = self.main_window.model_selector.get_provider()
        model = self.main_window.model_selector.get_model()

        QgsMessageLog.logMessage(
            f"Generating SQL with {provider}/{model}", "GeoAI Pro", Qgis.Info
        )

        # Get context
        context = self.sql_executor.get_context()

        # Generate SQL
        result = self.llm_handler.generate_sql(prompt, context, provider, model)

        if "error" in result:
            QMessageBox.critical(self, "Error", result["error"])
            self.sql_output.setText(f"ERROR: {result['error']}")
        else:
            sql = result.get("sql", "")
            self.sql_output.setText(sql)
            self.execute_btn.setEnabled(True)

    def clean_sql(self, sql: str) -> str:
        """Clean SQL by removing markdown code blocks, comments, and non-SQL content"""
        import re

        # Remove markdown code blocks (```sql ... ```)
        sql = re.sub(
            r"```sql\s*\n?(.*?)\n?```", r"\1", sql, flags=re.DOTALL | re.IGNORECASE
        )
        sql = re.sub(r"```\s*\n?(.*?)\n?```", r"\1", sql, flags=re.DOTALL)

        # Remove Python-style triple quotes
        sql = re.sub(r'"""[\s\S]*?"""', "", sql)
        sql = re.sub(r"'''[\s\S]*?'''", "", sql)

        # Remove lines that are just comments or headers
        lines = sql.split("\n")
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            # Skip empty lines, comment-only lines, and markdown headers
            if not line:
                continue
            if line.startswith("#") and (
                "Analysis Method" in line
                or "Azure" in line
                or "LLM" in line
                or "Generated Code" in line
            ):
                continue
            if line.startswith("//") or line.startswith("--") and len(line) < 5:
                continue
            # Keep the line
            cleaned_lines.append(line)

        sql = "\n".join(cleaned_lines)

        # Remove any remaining markdown formatting
        sql = re.sub(r"^#+\s*", "", sql, flags=re.MULTILINE)
        sql = re.sub(r"^=\s*$", "", sql, flags=re.MULTILINE)
        sql = re.sub(r"^-+\s*$", "", sql, flags=re.MULTILINE)

        return sql.strip()

    def execute_sql(self):
        """Execute SQL"""
        sql = self.sql_output.toPlainText().strip()
        if not sql:
            QMessageBox.warning(self, "Warning", "No SQL to execute")
            return

        if not self.sql_executor:
            QMessageBox.critical(self, "Error", "SQL executor not initialized")
            return

        # Clean SQL before execution
        cleaned_sql = self.clean_sql(sql)

        if not cleaned_sql:
            QMessageBox.warning(
                self,
                "Warning",
                "No valid SQL found after cleaning. Please check the SQL output.",
            )
            return

        QgsMessageLog.logMessage(
            f"Executing SQL (cleaned: {len(cleaned_sql)} chars)", "GeoAI Pro", Qgis.Info
        )

        # Log original vs cleaned for debugging
        if sql != cleaned_sql:
            QgsMessageLog.logMessage(
                f"SQL cleaned: removed {len(sql) - len(cleaned_sql)} characters of non-SQL content",
                "GeoAI Pro",
                Qgis.Info,
            )

        # Run in thread
        from qgis.PyQt.QtCore import QThread, pyqtSignal

        class ExecuteWorker(QThread):
            finished = pyqtSignal(dict)
            error = pyqtSignal(str)

            def __init__(self, sql_executor, sql):
                super().__init__()
                self.sql_executor = sql_executor
                self.sql = sql

            def run(self):
                try:
                    result = self.sql_executor.execute_sql(self.sql)
                    self.finished.emit(result)
                except Exception as e:
                    self.error.emit(str(e))

        self.execute_worker = ExecuteWorker(self.sql_executor, cleaned_sql)
        self.execute_worker.finished.connect(self.on_sql_executed)
        self.execute_worker.error.connect(self.on_execute_error)
        self.execute_worker.start()

        self.execute_btn.setEnabled(False)
        self.status_label.setText("Executing SQL...")

    def on_sql_executed(self, result):
        """Handle SQL execution result"""
        self.execute_btn.setEnabled(True)

        if "error" in result:
            QMessageBox.critical(self, "Error", result["error"])
            self.status_label.setText(f"Error: {result['error']}")
            self.status_label.setStyleSheet(
                "color: #e06c75; font-size: 12px; padding: 8px;"
            )
        else:
            rows = result.get("rows", [])
            self.display_results(rows)
            row_count = len(rows) if rows else 0
            self.status_label.setText(f"Query executed: {row_count} rows")
            self.status_label.setStyleSheet(
                "color: #98c379; font-size: 12px; padding: 8px;"
            )
            QgsMessageLog.logMessage(
                f"SQL executed: {row_count} rows", "GeoAI Pro", Qgis.Info
            )

    def on_execute_error(self, error_msg):
        """Handle execution error"""
        self.execute_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", error_msg)
        self.status_label.setText(f"Error: {error_msg}")
        self.status_label.setStyleSheet(
            "color: #e06c75; font-size: 12px; padding: 8px;"
        )

    def display_results(self, rows):
        """Display results in table"""
        if not rows:
            self.results_table.setRowCount(0)
            self.results_table.setColumnCount(0)
            return

        # Get column names
        columns = list(rows[0].keys())

        # Setup table
        self.results_table.setColumnCount(len(columns))
        self.results_table.setRowCount(len(rows))
        self.results_table.setHorizontalHeaderLabels(columns)

        # Fill table
        for row_idx, row_data in enumerate(rows):
            for col_idx, col_name in enumerate(columns):
                value = str(row_data.get(col_name, ""))
                self.results_table.setItem(row_idx, col_idx, QTableWidgetItem(value))

        self.results_table.resizeColumnsToContents()

    def auto_fix(self):
        """Auto-fix SQL errors"""
        sql = self.sql_output.toPlainText().strip()
        if not sql:
            QMessageBox.warning(self, "Warning", "No SQL to fix")
            return

        if not self.error_fixer or not self.sql_executor:
            QMessageBox.critical(
                self, "Error", "Error fixer or SQL executor not initialized"
            )
            return

        QgsMessageLog.logMessage("Auto-fixing SQL", "GeoAI Pro", Qgis.Info)

        # Try to execute first to get error
        result = self.sql_executor.execute_sql(sql)

        if "error" not in result:
            QMessageBox.information(self, "Info", "SQL appears to be valid!")
            return

        error_msg = result.get("error", "Unknown error")
        provider = self.main_window.model_selector.get_provider()
        model = self.main_window.model_selector.get_model()
        context = self.sql_executor.get_context()

        # Run in thread
        class FixWorker(QThread):
            finished = pyqtSignal(dict)
            error = pyqtSignal(str)

            def __init__(self, error_fixer, sql, error_msg, context, provider, model):
                super().__init__()
                self.error_fixer = error_fixer
                self.sql = sql
                self.error_msg = error_msg
                self.context = context
                self.provider = provider
                self.model = model

            def run(self):
                try:
                    result = self.error_fixer.fix_sql_error(
                        self.sql,
                        self.error_msg,
                        self.context,
                        self.provider,
                        self.model,
                    )
                    self.finished.emit(result)
                except Exception as e:
                    self.error.emit(str(e))

        self.fix_worker = FixWorker(
            self.error_fixer, sql, error_msg, context, provider, model
        )
        self.fix_worker.finished.connect(self.on_fix_complete)
        self.fix_worker.error.connect(self.on_fix_error)
        self.fix_worker.start()

        self.auto_fix_btn.setEnabled(False)
        self.status_label.setText("Fixing SQL...")
        self.status_label.setStyleSheet(
            "color: #e5c07b; font-size: 12px; padding: 8px;"
        )

    def on_fix_complete(self, result):
        """Handle fix result"""
        self.auto_fix_btn.setEnabled(True)

        if "error" in result:
            QMessageBox.critical(self, "Error", result["error"])
            self.status_label.setText(f"Error: {result['error']}")
            self.status_label.setStyleSheet(
                "color: #e06c75; font-size: 12px; padding: 8px;"
            )
        else:
            fixed_sql = result.get("sql", "")
            self.sql_output.setText(fixed_sql)
            self.status_label.setText("SQL fixed successfully")
            self.status_label.setStyleSheet(
                "color: #98c379; font-size: 12px; padding: 8px;"
            )
            QgsMessageLog.logMessage("SQL fixed", "GeoAI Pro", Qgis.Info)

    def on_fix_error(self, error_msg):
        """Handle fix error"""
        self.auto_fix_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", error_msg)
        self.status_label.setText(f"Error: {error_msg}")
        self.status_label.setStyleSheet(
            "color: #e06c75; font-size: 12px; padding: 8px;"
        )

    def copy_sql(self):
        """Copy SQL to clipboard"""
        from qgis.PyQt.QtWidgets import QApplication

        QApplication.clipboard().setText(self.sql_output.toPlainText())
        QgsMessageLog.logMessage("SQL copied to clipboard", "GeoAI Pro", Qgis.Info)
