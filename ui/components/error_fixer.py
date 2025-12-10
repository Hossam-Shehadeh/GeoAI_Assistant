"""
Error Fixer Panel - Automatic SQL error fixing
"""

from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, 
    QLabel, QMessageBox, QTableWidget, QLineEdit
)
from qgis.PyQt.QtCore import QThread, pyqtSignal
from qgis.core import QgsMessageLog, Qgis


class WorkerThread(QThread):
    """Worker thread for error fixing"""
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
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class ErrorFixerPanel(QWidget):
    """Error fixer panel"""
    
    def __init__(self, iface, config, main_window, error_fixer, sql_executor):
        super().__init__()
        self.iface = iface
        self.config = config
        self.main_window = main_window
        self.error_fixer = error_fixer
        self.sql_executor = sql_executor
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title = QLabel("🔧 SQL Error Fixer")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #61afef;")
        layout.addWidget(title)
        
        desc = QLabel("Paste a SQL query with an error and get it automatically fixed.")
        desc.setStyleSheet("color: #abb2bf;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # SQL input
        input_label = QLabel("SQL Query with Error:")
        layout.addWidget(input_label)
        
        self.sql_input = QTextEdit()
        self.sql_input.setPlaceholderText("Paste your SQL query here...")
        layout.addWidget(self.sql_input)
        
        # Error message
        error_label = QLabel("Error Message (optional):")
        layout.addWidget(error_label)
        
        self.error_input = QLineEdit()
        self.error_input.setPlaceholderText("Paste the error message here (optional)...")
        layout.addWidget(self.error_input)
        
        # Fix button
        self.fix_btn = QPushButton("🔧 Fix SQL Error")
        self.fix_btn.setObjectName("warning")
        self.fix_btn.clicked.connect(self.fix_error)
        layout.addWidget(self.fix_btn)
        
        # Fixed SQL output
        output_label = QLabel("Fixed SQL:")
        layout.addWidget(output_label)
        
        self.fixed_sql_output = QTextEdit()
        self.fixed_sql_output.setObjectName("sqlOutput")
        self.fixed_sql_output.setReadOnly(True)
        layout.addWidget(self.fixed_sql_output)
        
        # Action buttons
        action_layout = QHBoxLayout()
        copy_btn = QPushButton("📋 Copy Fixed SQL")
        copy_btn.clicked.connect(self.copy_fixed_sql)
        action_layout.addWidget(copy_btn)
        
        execute_btn = QPushButton("▶️ Execute Fixed SQL")
        execute_btn.setObjectName("success")
        execute_btn.clicked.connect(self.execute_fixed_sql)
        action_layout.addWidget(execute_btn)
        
        layout.addLayout(action_layout)
        
        # Results
        results_label = QLabel("Execution Results:")
        layout.addWidget(results_label)
        
        self.results_table = QTableWidget()
        layout.addWidget(self.results_table)
    
    def fix_error(self):
        """Fix SQL error"""
        sql = self.sql_input.toPlainText().strip()
        if not sql:
            QMessageBox.warning(self, "Warning", "Please enter a SQL query")
            return
        
        if not self.error_fixer:
            QMessageBox.critical(self, "Error", "Error fixer not initialized")
            return
        
        error_msg = self.error_input.text().strip()
        provider = self.main_window.model_selector.get_provider()
        model = self.main_window.model_selector.get_model()
        
        # Get context
        context = self.sql_executor.get_context() if self.sql_executor else {}
        
        # Run in thread
        self.worker = WorkerThread(
            self.error_fixer.fix_sql_error,
            sql,
            error_msg,
            context,
            provider,
            model
        )
        self.worker.finished.connect(self.on_fix_complete)
        self.worker.error.connect(self.on_error)
        self.worker.start()
        
        self.fix_btn.setEnabled(False)
        QgsMessageLog.logMessage("Fixing SQL error", "GeoAI Pro", Qgis.Info)
    
    def on_fix_complete(self, result):
        """Handle fix result"""
        self.fix_btn.setEnabled(True)
        
        if "error" in result:
            QMessageBox.critical(self, "Error", result["error"])
            self.fixed_sql_output.setText(f"ERROR: {result['error']}")
        else:
            fixed_sql = result.get("sql", "")
            explanation = result.get("explanation", "")
            self.fixed_sql_output.setText(fixed_sql)
            if explanation:
                self.fixed_sql_output.append(f"\n\n-- Explanation: {explanation}")
            QgsMessageLog.logMessage("SQL error fixed", "GeoAI Pro", Qgis.Info)
    
    def on_error(self, error_msg):
        """Handle error"""
        self.fix_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", error_msg)
        self.fixed_sql_output.setText(f"ERROR: {error_msg}")
    
    def copy_fixed_sql(self):
        """Copy fixed SQL to clipboard"""
        from qgis.PyQt.QtWidgets import QApplication
        QApplication.clipboard().setText(self.fixed_sql_output.toPlainText())
        QMessageBox.information(self, "Copied", "Fixed SQL copied to clipboard")
    
    def execute_fixed_sql(self):
        """Execute fixed SQL"""
        sql = self.fixed_sql_output.toPlainText().strip()
        if not sql:
            QMessageBox.warning(self, "Warning", "No fixed SQL to execute")
            return
        
        if not self.sql_executor:
            QMessageBox.critical(self, "Error", "SQL executor not initialized")
            return
        
        # Execute SQL
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
        
        self.execute_worker = ExecuteWorker(self.sql_executor, sql)
        self.execute_worker.finished.connect(self.on_execute_complete)
        self.execute_worker.error.connect(self.on_execute_error)
        self.execute_worker.start()
        
        self.execute_btn.setEnabled(False)
        QgsMessageLog.logMessage("Executing fixed SQL", "GeoAI Pro", Qgis.Info)
    
    def on_execute_complete(self, result):
        """Handle execution result"""
        self.execute_btn.setEnabled(True)
        
        if "error" in result:
            QMessageBox.critical(self, "Error", result["error"])
        else:
            rows = result.get("rows", [])
            self.display_results(rows)
            row_count = len(rows) if rows else 0
            QMessageBox.information(self, "Success", f"Query executed: {row_count} rows")
            QgsMessageLog.logMessage(f"Fixed SQL executed: {row_count} rows", "GeoAI Pro", Qgis.Info)
    
    def on_execute_error(self, error_msg):
        """Handle execution error"""
        self.execute_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", error_msg)
    
    def display_results(self, rows):
        """Display results in table"""
        if not rows:
            self.results_table.setRowCount(0)
            self.results_table.setColumnCount(0)
            return
        
        from qgis.PyQt.QtWidgets import QTableWidgetItem
        
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

