"""
Data Analysis Panel - Advanced data analysis features
"""

from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, 
    QLabel, QComboBox, QMessageBox
)
from qgis.PyQt.QtCore import QThread, pyqtSignal
from qgis.core import QgsMessageLog, Qgis


class DataAnalysisPanel(QWidget):
    """Data analysis panel"""
    
    def __init__(self, iface, config, main_window, llm_handler, sql_executor):
        super().__init__()
        self.iface = iface
        self.config = config
        self.main_window = main_window
        self.llm_handler = llm_handler
        self.sql_executor = sql_executor
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title = QLabel("📊 Data Analysis")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #61afef;")
        layout.addWidget(title)
        
        desc = QLabel("Perform advanced analysis on your geospatial data.")
        desc.setStyleSheet("color: #abb2bf;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Quick analysis buttons
        quick_label = QLabel("Quick Analysis:")
        layout.addWidget(quick_label)
        
        quick_layout = QHBoxLayout()
        spatial_btn = QPushButton("📍 Spatial Analysis")
        spatial_btn.clicked.connect(lambda: self.quick_analysis("spatial"))
        quick_layout.addWidget(spatial_btn)
        
        attribute_btn = QPushButton("📋 Attribute Analysis")
        attribute_btn.clicked.connect(lambda: self.quick_analysis("attribute"))
        quick_layout.addWidget(attribute_btn)
        
        layout.addLayout(quick_layout)
        
        # Custom analysis
        custom_label = QLabel("Custom Analysis:")
        layout.addWidget(custom_label)
        
        self.analysis_prompt = QTextEdit()
        self.analysis_prompt.setPlaceholderText(
            "Example: What is the average area of buildings by district?\n"
            "Example: Show me a density map of points\n"
            "Example: Find outliers in the population data"
        )
        self.analysis_prompt.setMaximumHeight(100)
        layout.addWidget(self.analysis_prompt)
        
        analyze_btn = QPushButton("🔍 Analyze")
        analyze_btn.setObjectName("primary")
        analyze_btn.clicked.connect(self.custom_analysis)
        layout.addWidget(analyze_btn)
        
        # Results
        results_label = QLabel("Analysis Results:")
        layout.addWidget(results_label)
        
        self.analysis_results = QTextEdit()
        self.analysis_results.setReadOnly(True)
        layout.addWidget(self.analysis_results)
    
    def quick_analysis(self, analysis_type):
        """Perform quick analysis"""
        try:
            QgsMessageLog.logMessage(f"Quick {analysis_type} analysis", "GeoAI Pro", Qgis.Info)
            self.analysis_results.setText("Analyzing... Please wait.")
            
            if not self.llm_handler or not self.sql_executor:
                self.analysis_results.setText("ERROR: LLM handler or SQL executor not available")
                return
            
            # Get context
            context = self.sql_executor.get_context()
            
            # Build prompt based on analysis type
            if analysis_type == "spatial":
                prompt = "Perform a spatial analysis on the current data. Include spatial statistics, relationships, and patterns."
            else:  # attribute
                prompt = "Perform an attribute analysis on the current data. Include statistics, distributions, and summaries."
            
            # Get model from main window
            if not hasattr(self.main_window, 'model_selector'):
                self.analysis_results.setText("ERROR: Model selector not available")
                return
            
            provider = self.main_window.model_selector.get_provider()
            model = self.main_window.model_selector.get_model()
            
            # Generate SQL for analysis
            sql_result = self.llm_handler.generate_sql(prompt, context, provider, model)
            
            if sql_result.get("error"):
                self.analysis_results.setText(f"ERROR: {sql_result['error']}")
                return
            
            sql = sql_result.get("sql", "")
            explanation = sql_result.get("explanation", "")
            
            # Execute SQL if available
            if sql:
                exec_result = self.sql_executor.execute_sql(sql)
                if exec_result.get("error"):
                    result_text = f"SQL Query:\n{sql}\n\nError: {exec_result['error']}"
                else:
                    rows = exec_result.get("rows", [])
                    if rows:
                        # Format results
                        result_text = f"SQL Query:\n{sql}\n\nResults:\n"
                        if len(rows) > 0:
                            # Show column headers
                            headers = list(rows[0].keys())
                            result_text += "\t".join(headers) + "\n"
                            result_text += "-" * 50 + "\n"
                            # Show first 20 rows
                            for row in rows[:20]:
                                values = [str(row.get(h, "")) for h in headers]
                                result_text += "\t".join(values) + "\n"
                            if len(rows) > 20:
                                result_text += f"\n... and {len(rows) - 20} more rows"
                    else:
                        result_text = f"SQL Query:\n{sql}\n\nNo results returned."
                    
                    if explanation:
                        result_text += f"\n\nExplanation:\n{explanation}"
            else:
                result_text = explanation or "No analysis generated."
            
            self.analysis_results.setText(result_text)
            
        except Exception as e:
            import traceback
            error_msg = f"ERROR: {str(e)}\n{traceback.format_exc()}"
            QgsMessageLog.logMessage(error_msg, "GeoAI Pro", Qgis.Critical)
            self.analysis_results.setText(error_msg)
    
    def custom_analysis(self):
        """Perform custom analysis"""
        try:
            prompt = self.analysis_prompt.toPlainText().strip()
            if not prompt:
                QMessageBox.warning(self, "Warning", "Please enter an analysis query")
                return
            
            QgsMessageLog.logMessage("Custom analysis requested", "GeoAI Pro", Qgis.Info)
            self.analysis_results.setText("Analyzing... Please wait.")
            
            if not self.llm_handler or not self.sql_executor:
                self.analysis_results.setText("ERROR: LLM handler or SQL executor not available")
                return
            
            # Get context
            context = self.sql_executor.get_context()
            
            # Get model from main window
            if not hasattr(self.main_window, 'model_selector'):
                self.analysis_results.setText("ERROR: Model selector not available")
                return
            
            provider = self.main_window.model_selector.get_provider()
            model = self.main_window.model_selector.get_model()
            
            # Generate SQL for analysis
            sql_result = self.llm_handler.generate_sql(prompt, context, provider, model)
            
            if sql_result.get("error"):
                self.analysis_results.setText(f"ERROR: {sql_result['error']}")
                return
            
            sql = sql_result.get("sql", "")
            explanation = sql_result.get("explanation", "")
            
            # Execute SQL if available
            if sql:
                exec_result = self.sql_executor.execute_sql(sql)
                if exec_result.get("error"):
                    result_text = f"SQL Query:\n{sql}\n\nError: {exec_result['error']}"
                else:
                    rows = exec_result.get("rows", [])
                    if rows:
                        # Format results
                        result_text = f"SQL Query:\n{sql}\n\nResults:\n"
                        if len(rows) > 0:
                            # Show column headers
                            headers = list(rows[0].keys())
                            result_text += "\t".join(headers) + "\n"
                            result_text += "-" * 50 + "\n"
                            # Show first 20 rows
                            for row in rows[:20]:
                                values = [str(row.get(h, "")) for h in headers]
                                result_text += "\t".join(values) + "\n"
                            if len(rows) > 20:
                                result_text += f"\n... and {len(rows) - 20} more rows"
                    else:
                        result_text = f"SQL Query:\n{sql}\n\nNo results returned."
                    
                    if explanation:
                        result_text += f"\n\nExplanation:\n{explanation}"
            else:
                result_text = explanation or "No analysis generated."
            
            self.analysis_results.setText(result_text)
            
        except Exception as e:
            import traceback
            error_msg = f"ERROR: {str(e)}\n{traceback.format_exc()}"
            QgsMessageLog.logMessage(error_msg, "GeoAI Pro", Qgis.Critical)
            self.analysis_results.setText(error_msg)

