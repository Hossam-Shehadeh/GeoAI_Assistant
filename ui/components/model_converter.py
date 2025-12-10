"""
Model Converter Component - Image to Code conversion with Azure CV
"""

from qgis.PyQt.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QFileDialog,
    QLineEdit,
    QComboBox,
    QScrollArea,
    QMessageBox,
    QTabWidget,
    QSplitter,
    QGroupBox,
    QCheckBox,
    QSpinBox,
)
from qgis.PyQt.QtCore import Qt, QThread, pyqtSignal
from qgis.PyQt.QtGui import QPixmap, QFont, QTextCharFormat, QColor, QSyntaxHighlighter, QTextDocument
from qgis.core import QgsMessageLog, Qgis, QgsRasterLayer, QgsProject
import os
import requests


class WorkerThread(QThread):
    """Worker thread for image processing"""

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
            # Log result structure before emitting
            if isinstance(result, dict):
                QgsMessageLog.logMessage(
                    f"Worker thread result: keys={list(result.keys())}, "
                    f"has_error={bool(result.get('error'))}, "
                    f"has_sql={bool(result.get('sql_code'))}, "
                    f"has_python={bool(result.get('python_code'))}",
                    "GeoAI Pro",
                    Qgis.Info,
                )
            else:
                QgsMessageLog.logMessage(
                    f"Worker thread result is not a dict: {type(result)}",
                    "GeoAI Pro",
                    Qgis.Warning,
                )
            self.finished.emit(
                result
                if isinstance(result, dict)
                else {"error": f"Invalid result type: {type(result)}"}
            )
        except Exception as e:
            import traceback

            error_trace = traceback.format_exc()
            QgsMessageLog.logMessage(
                f"Worker thread error: {str(e)}\n{error_trace}",
                "GeoAI Pro",
                Qgis.Critical,
            )
            self.error.emit(str(e))


class ModelConverter(QWidget):
    """Model converter with Azure Computer Vision"""

    def __init__(self, iface, config, main_window, image_processor, llm_handler):
        super().__init__()
        self.iface = iface
        self.config = config
        self.main_window = main_window
        self.image_processor = image_processor
        self.llm_handler = llm_handler
        self.image_path = None
        self.setup_ui()

    def setup_ui(self):
        """Setup UI"""
        # Create main scroll area for the entire widget
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Create main widget
        main_widget = QWidget()
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        main_scroll.setWidget(main_widget)
        
        # Set main scroll as the widget's layout
        outer_layout = QVBoxLayout()
        self.setLayout(outer_layout)
        outer_layout.addWidget(main_scroll)

        # Title
        title = QLabel("🖼️ Model Builder Converter")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #61afef;")
        layout.addWidget(title)

        desc = QLabel(
            "Upload a screenshot of your QGIS Model Builder and convert it to executable code."
        )
        desc.setStyleSheet("color: #abb2bf;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Image selection
        file_layout = QHBoxLayout()
        self.image_path_input = QLineEdit()
        self.image_path_input.setPlaceholderText("No image selected...")
        self.image_path_input.setReadOnly(True)
        file_layout.addWidget(self.image_path_input)

        browse_btn = QPushButton("📁 Browse")
        browse_btn.clicked.connect(self.browse_image)
        file_layout.addWidget(browse_btn)

        layout.addLayout(file_layout)

        # Image preview (make it smaller to leave room for output)
        preview_label = QLabel("Image Preview:")
        layout.addWidget(preview_label)

        self.image_preview_scroll = QScrollArea()
        self.image_preview_scroll.setWidgetResizable(True)
        self.image_preview_scroll.setMinimumHeight(150)  # Reduced from 200
        self.image_preview_scroll.setMaximumHeight(200)  # Reduced from 300

        self.image_preview_label = QLabel()
        self.image_preview_label.setAlignment(Qt.AlignCenter)
        self.image_preview_label.setText("No image selected")
        self.image_preview_label.setStyleSheet(
            """
            border: 2px dashed #3e4451;
            background-color: #1e2227;
            border-radius: 8px;
            color: #abb2bf;
        """
        )
        self.image_preview_scroll.setWidget(self.image_preview_label)
        layout.addWidget(self.image_preview_scroll)

        # Add to QGIS button
        add_to_qgis_btn = QPushButton("➕ Add Image to QGIS Map")
        add_to_qgis_btn.clicked.connect(self.add_image_to_qgis)
        layout.addWidget(add_to_qgis_btn)

        # Conversion type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Convert to:"))
        self.conversion_type = QComboBox()
        self.conversion_type.addItems(["SQL", "Python", "Both"])
        type_layout.addWidget(self.conversion_type)
        type_layout.addStretch()
        layout.addLayout(type_layout)

        # Convert button
        self.convert_btn = QPushButton("🔄 Convert to Code")
        self.convert_btn.setObjectName("primary")
        self.convert_btn.setEnabled(True)
        self.convert_btn.setCursor(Qt.PointingHandCursor)
        self.convert_btn.clicked.connect(self.convert_model_image)
        layout.addWidget(self.convert_btn)

        # Output section with tabs and flexible layout
        output_group = QGroupBox("📊 Generated Output")
        output_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3e4451;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        output_layout = QVBoxLayout()
        output_group.setLayout(output_layout)
        
        # Create tab widget for flexible output display
        self.output_tabs = QTabWidget()
        self.output_tabs.setTabsClosable(False)
        self.output_tabs.setMinimumHeight(300)  # Ensure minimum height
        self.output_tabs.setMaximumHeight(1000)  # Allow expansion
        
        # SQL Output Tab
        self.sql_output = QTextEdit()
        self.sql_output.setObjectName("sqlOutput")
        self.sql_output.setFont(QFont("Courier New", 11))
        self.sql_output.setReadOnly(True)
        self.sql_output.setMinimumHeight(250)  # Ensure visible height
        self.sql_output.setStyleSheet("""
            QTextEdit {
                background-color: #1e2227;
                color: #abb2bf;
                border: 1px solid #3e4451;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        self.output_tabs.addTab(self.sql_output, "📝 SQL Code")
        
        # Python Output Tab
        self.python_output = QTextEdit()
        self.python_output.setObjectName("pythonOutput")
        self.python_output.setFont(QFont("Courier New", 11))
        self.python_output.setReadOnly(True)
        self.python_output.setMinimumHeight(250)  # Ensure visible height
        self.python_output.setStyleSheet("""
            QTextEdit {
                background-color: #1e2227;
                color: #abb2bf;
                border: 1px solid #3e4451;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        self.output_tabs.addTab(self.python_output, "🐍 Python Code")
        
        # Analysis Tab (for Azure description, etc.)
        self.analysis_output = QTextEdit()
        self.analysis_output.setObjectName("analysisOutput")
        self.analysis_output.setFont(QFont("Arial", 10))
        self.analysis_output.setReadOnly(True)
        self.analysis_output.setMinimumHeight(250)  # Ensure visible height
        self.analysis_output.setStyleSheet("""
            QTextEdit {
                background-color: #1e2227;
                color: #98c379;
                border: 1px solid #3e4451;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        self.output_tabs.addTab(self.analysis_output, "🔍 Analysis")
        
        # Combined/All Tab (shows everything)
        self.combined_output = QTextEdit()
        self.combined_output.setObjectName("combinedOutput")
        self.combined_output.setFont(QFont("Courier New", 10))
        self.combined_output.setReadOnly(True)
        self.combined_output.setMinimumHeight(250)  # Ensure visible height
        self.combined_output.setStyleSheet("""
            QTextEdit {
                background-color: #1e2227;
                color: #abb2bf;
                border: 1px solid #3e4451;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        self.output_tabs.addTab(self.combined_output, "📋 All Output")
        
        # Make output group expandable and visible
        output_group.setMinimumHeight(350)  # Ensure group is visible
        
        output_layout.addWidget(self.output_tabs)
        
        # Output options
        options_layout = QHBoxLayout()
        
        # Font size control
        options_layout.addWidget(QLabel("Font Size:"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setMinimum(8)
        self.font_size_spin.setMaximum(20)
        self.font_size_spin.setValue(11)
        self.font_size_spin.valueChanged.connect(self.update_font_size)
        options_layout.addWidget(self.font_size_spin)
        
        options_layout.addStretch()
        
        # Word wrap toggle
        self.word_wrap_check = QCheckBox("Word Wrap")
        self.word_wrap_check.setChecked(True)
        self.word_wrap_check.toggled.connect(self.toggle_word_wrap)
        options_layout.addWidget(self.word_wrap_check)
        
        # Line numbers toggle
        self.line_numbers_check = QCheckBox("Show Line Numbers")
        self.line_numbers_check.setChecked(False)
        options_layout.addWidget(self.line_numbers_check)
        
        output_layout.addLayout(options_layout)
        
        # Add output group with stretch to push it up and make it prominent
        layout.addWidget(output_group, stretch=2)  # Give it more priority (2x stretch)
        
        # Add a spacer at the end to push output up
        layout.addStretch()
        
        # Action buttons with more options
        action_layout = QHBoxLayout()
        
        copy_btn = QPushButton("📋 Copy")
        copy_btn.setToolTip("Copy current tab's content to clipboard")
        copy_btn.clicked.connect(self.copy_code)
        action_layout.addWidget(copy_btn)
        
        copy_all_btn = QPushButton("📋 Copy All")
        copy_all_btn.setToolTip("Copy all output to clipboard")
        copy_all_btn.clicked.connect(self.copy_all_code)
        action_layout.addWidget(copy_all_btn)
        
        save_btn = QPushButton("💾 Save")
        save_btn.setToolTip("Save current tab's content to file")
        save_btn.clicked.connect(self.save_code)
        action_layout.addWidget(save_btn)
        
        save_all_btn = QPushButton("💾 Save All")
        save_all_btn.setToolTip("Save all output to separate files")
        save_all_btn.clicked.connect(self.save_all_code)
        action_layout.addWidget(save_all_btn)
        
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.setToolTip("Clear all output")
        clear_btn.clicked.connect(self.clear_output)
        action_layout.addWidget(clear_btn)
        
        action_layout.addStretch()
        
        layout.addLayout(action_layout)
        
        # Keep old reference for backward compatibility
        self.model_code_output = self.combined_output

    def browse_image(self):
        """Browse for image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Model Builder Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)",
        )

        if file_path:
            self.image_path = file_path
            self.image_path_input.setText(file_path)
            self.display_image_preview(file_path)

    def display_image_preview(self, file_path):
        """Display image preview"""
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            # Scale to fit
            scaled_pixmap = pixmap.scaled(
                400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.image_preview_label.setPixmap(scaled_pixmap)
        else:
            self.image_preview_label.setText("Failed to load image")

    def add_image_to_qgis(self):
        """Add image to QGIS map"""
        if not self.image_path:
            QMessageBox.warning(self, "Warning", "No image selected")
            return

        try:
            layer = QgsRasterLayer(self.image_path, "Model Builder Image")
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)
                QgsMessageLog.logMessage("Image added to QGIS", "GeoAI Pro", Qgis.Info)
                QMessageBox.information(self, "Success", "Image added to QGIS map")
            else:
                QMessageBox.critical(
                    self, "Error", "Failed to load image as raster layer"
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error adding image: {str(e)}")

    def convert_model_image(self):
        """Convert model image to code"""
        if not self.image_path:
            QMessageBox.warning(self, "Warning", "Please select an image first")
            return

        if not self.image_processor:
            QMessageBox.critical(self, "Error", "Image processor not initialized")
            return

        output_type = self.conversion_type.currentText().lower()
        if output_type == "both":
            output_type = "sql"  # Default, can be enhanced

        provider = self.main_window.model_selector.get_provider()
        
        # IMPORTANT: Use the SELECTED model (not vision model)
        # Azure Computer Vision will analyze the image first,
        # then the selected model generates code from the description
        model = self.main_window.model_selector.get_model()
        
        QgsMessageLog.logMessage(
            f"Image conversion workflow: Azure CV → {provider}/{model}",
            "GeoAI Pro",
            Qgis.Info,
        )
        QgsMessageLog.logMessage(
            f"Step 1: Azure will analyze the image\n"
            f"Step 2: {provider}/{model} will generate code from Azure description",
            "GeoAI Pro",
            Qgis.Info,
        )

        # Run in thread
        self.worker = WorkerThread(
            self.image_processor.process_model_image,
            self.image_path,
            output_type,
            provider,
            model,
        )
        self.worker.finished.connect(self.on_conversion_complete)
        self.worker.error.connect(self.on_conversion_error)
        self.worker.start()

        QgsMessageLog.logMessage(
            f"Starting image conversion with {provider}/{model}", "GeoAI Pro", Qgis.Info
        )

    def on_conversion_complete(self, result):
        """Handle conversion result"""
        # Debug: Log the result structure
        QgsMessageLog.logMessage(
            f"Conversion result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}",
            "GeoAI Pro",
            Qgis.Info,
        )

        if "error" in result:
            error_msg = result["error"]
            QMessageBox.critical(self, "Conversion Failed", error_msg)
            error_text = f"# ❌ ERROR: {error_msg}\n\n# Please check:\n# 1. Image is clear and readable\n# 2. Azure/LLM configuration is correct\n# 3. Check Log Messages for details"
            self.sql_output.setText(error_text)
            self.python_output.setText(error_text)
            self.analysis_output.setText(f"Error: {error_msg}")
            self.combined_output.setText(error_text)
        else:
            # Get code (prioritize sql_code or python_code, fallback to code)
            code = (
                result.get("sql_code")
                or result.get("python_code")
                or result.get("code", "")
                or result.get("raw_response", "")
            )

            # Debug: Log what we found
            QgsMessageLog.logMessage(
                f"Code extraction - sql_code: {bool(result.get('sql_code'))}, "
                f"python_code: {bool(result.get('python_code'))}, "
                f"code: {bool(result.get('code'))}, "
                f"raw_response: {bool(result.get('raw_response'))}, "
                f"final code length: {len(code) if code else 0}",
                "GeoAI Pro",
                Qgis.Info,
            )

            # If still no code, check explanation and all possible fields
            if not code:
                code = result.get("explanation", "") or result.get("extracted_info", "")
                # Try to get from structured fields
                if not code:
                    # Check if result has nested structure
                    if isinstance(result, dict):
                        for key in result.keys():
                            if (
                                "code" in key.lower()
                                or "sql" in key.lower()
                                or "python" in key.lower()
                            ):
                                potential_code = result.get(key)
                                if (
                                    potential_code
                                    and isinstance(potential_code, str)
                                    and len(potential_code.strip()) > 0
                                ):
                                    code = potential_code
                                    QgsMessageLog.logMessage(
                                        f"Found code in field: {key}",
                                        "GeoAI Pro",
                                        Qgis.Info,
                                    )
                                    break

            # Build meaningful output
            output_parts = []

            # Add method info
            method = result.get("analysis_method", "unknown")
            if method == "azure_computer_vision":
                output_parts.append("# ✅ Analysis Method: Azure Computer Vision + LLM")
                output_parts.append(
                    "# Azure analyzed the image, then LLM generated code"
                )
                output_parts.append("")

                # Add Azure description for context
                azure_desc = result.get("azure_description", "")
                if azure_desc:
                    output_parts.append("# 📋 Azure Computer Vision Analysis:")
                    output_parts.append("# " + "=" * 60)
                    # Format description with line breaks
                    desc_lines = azure_desc.split("\n")
                    for line in desc_lines[:15]:  # First 15 lines
                        if line.strip():
                            output_parts.append(f"# {line.strip()}")
                    if len(desc_lines) > 15:
                        output_parts.append(
                            f"# ... ({len(desc_lines) - 15} more lines)"
                        )
                    output_parts.append("# " + "=" * 60)
                    output_parts.append("")
                    output_parts.append("# 💻 Generated Code:")
                    output_parts.append("")

            elif method == "llm_direct":
                output_parts.append("# ⚠️ Analysis Method: LLM Direct Processing")
                output_parts.append(
                    "# Note: Azure Computer Vision not available - using LLM fallback"
                )
                output_parts.append(
                    "# For better results, configure Azure in Settings tab"
                )
                output_parts.append("")

                # Add extracted info if available
                extracted_info = result.get("extracted_info", "")
                if extracted_info:
                    output_parts.append("# 📋 LLM Image Analysis:")
                    output_parts.append("# " + "=" * 60)
                    info_lines = extracted_info.split("\n")
                    for line in info_lines[:10]:  # First 10 lines
                        if line.strip():
                            output_parts.append(f"# {line.strip()}")
                    if len(info_lines) > 10:
                        output_parts.append(
                            f"# ... ({len(info_lines) - 10} more lines)"
                        )
                    output_parts.append("# " + "=" * 60)
                    output_parts.append("")
                    output_parts.append("# 💻 Generated Code:")
                    output_parts.append("")

            # Add the actual code
            if code and len(code.strip()) > 0:
                output_parts.append(code)
            else:
                # Show debug info if no code
                output_parts.append("# ⚠️ No code generated.")
                output_parts.append("#")
                output_parts.append("# Debug Information:")
                output_parts.append(
                    f"# Result keys: {', '.join(result.keys()) if isinstance(result, dict) else 'N/A'}"
                )
                if result.get("raw_response"):
                    output_parts.append(
                        f"# Raw response length: {len(result.get('raw_response', ''))}"
                    )
                if result.get("explanation"):
                    output_parts.append(
                        f"# Explanation length: {len(result.get('explanation', ''))}"
                    )
                output_parts.append("#")
                output_parts.append("# Please try:")
                output_parts.append("# 1. Check the image is clear and readable")
                output_parts.append("# 2. Try a different image")
                output_parts.append("# 3. Check Log Messages for more details")

                # Also show raw response if available for debugging
                if result.get("raw_response"):
                    output_parts.append("")
                    output_parts.append("# Raw Response:")
                    output_parts.append(
                        result.get("raw_response", "")[:500]
                    )  # First 500 chars

            # Combine all parts
            final_output = "\n".join(output_parts)
            
            # Update outputs based on type
            sql_code = result.get("sql_code", "")
            python_code = result.get("python_code", "")
            
            # Update SQL tab
            if sql_code:
                self.sql_output.setText(sql_code)
                self.output_tabs.setTabText(0, f"📝 SQL Code ({len(sql_code)} chars)")
            else:
                self.sql_output.setText("# No SQL code generated")
                self.output_tabs.setTabText(0, "📝 SQL Code")
            
            # Update Python tab
            if python_code:
                self.python_output.setText(python_code)
                self.output_tabs.setTabText(1, f"🐍 Python Code ({len(python_code)} chars)")
            else:
                self.python_output.setText("# No Python code generated")
                self.output_tabs.setTabText(1, "🐍 Python Code")
            
            # Update Analysis tab
            analysis_text = []
            if result.get("azure_description"):
                analysis_text.append("=== Azure Computer Vision Analysis ===\n")
                analysis_text.append(result.get("azure_description", ""))
            if result.get("extracted_info"):
                if analysis_text:
                    analysis_text.append("\n\n=== LLM Image Analysis ===\n")
                analysis_text.append(result.get("extracted_info", ""))
            if result.get("explanation"):
                if analysis_text:
                    analysis_text.append("\n\n=== Explanation ===\n")
                analysis_text.append(result.get("explanation", ""))
            
            if analysis_text:
                self.analysis_output.setText("\n".join(analysis_text))
                self.output_tabs.setTabText(2, f"🔍 Analysis ({len(''.join(analysis_text))} chars)")
            else:
                self.analysis_output.setText("# No analysis information available")
                self.output_tabs.setTabText(2, "🔍 Analysis")
            
            # Update Combined tab (all output)
            self.combined_output.setText(final_output)
            self.combined_output.moveCursor(self.combined_output.textCursor().Start)  # Scroll to top
            self.output_tabs.setTabText(3, f"📋 All Output ({len(final_output)} chars)")
            
            # Switch to appropriate tab based on output type
            if output_type == "sql" and sql_code:
                self.output_tabs.setCurrentIndex(0)
                self.sql_output.moveCursor(self.sql_output.textCursor().Start)  # Scroll to top
            elif output_type == "python" and python_code:
                self.output_tabs.setCurrentIndex(1)
                self.python_output.moveCursor(self.python_output.textCursor().Start)  # Scroll to top
            else:
                self.output_tabs.setCurrentIndex(3)  # Show combined by default
                self.combined_output.moveCursor(self.combined_output.textCursor().Start)  # Scroll to top
            
            # Ensure output area is visible - scroll to it
            QgsMessageLog.logMessage(
                "Output generated - output area should be visible",
                "GeoAI Pro",
                Qgis.Info
            )

            # Always log the final output length
            QgsMessageLog.logMessage(
                f"Final output set in UI - Length: {len(final_output)} chars",
                "GeoAI Pro",
                Qgis.Info,
            )

            # Log method used and code status
            if method == "azure_computer_vision":
                code_len = len(code) if code else 0
                QgsMessageLog.logMessage(
                    f"Conversion completed using Azure Computer Vision + LLM | Code length: {code_len} chars",
                    "GeoAI Pro",
                    Qgis.Info,
                )
            elif method == "llm_direct":
                code_len = len(code) if code else 0
                QgsMessageLog.logMessage(
                    f"Conversion completed using LLM direct processing (Azure fallback) | Code length: {code_len} chars",
                    "GeoAI Pro",
                    Qgis.Info,
                )
            else:
                QgsMessageLog.logMessage("Conversion completed", "GeoAI Pro", Qgis.Info)

            # Show success message if code was generated
            if code and len(code.strip()) > 0:
                QMessageBox.information(
                    self,
                    "Conversion Successful",
                    f"Code generated successfully using {method.replace('_', ' ').title()}!\n\n"
                    f"Code length: {len(code)} characters",
                )

    def on_conversion_error(self, error_msg):
        """Handle conversion error"""
        QMessageBox.critical(self, "Error", error_msg)
        error_text = f"# ❌ ERROR: {error_msg}\n\n# Please check:\n# 1. Image is clear and readable\n# 2. Azure/LLM configuration is correct\n# 3. Check Log Messages for details"
        self.sql_output.setText(error_text)
        self.python_output.setText(error_text)
        self.analysis_output.setText(f"Error: {error_msg}")
        self.combined_output.setText(error_text)

    def copy_code(self):
        """Copy current tab's code to clipboard"""
        from qgis.PyQt.QtWidgets import QApplication
        
        current_widget = self.output_tabs.currentWidget()
        if current_widget:
            QApplication.clipboard().setText(current_widget.toPlainText())
            tab_name = self.output_tabs.tabText(self.output_tabs.currentIndex())
            QMessageBox.information(self, "Copied", f"{tab_name} copied to clipboard")
    
    def copy_all_code(self):
        """Copy all output to clipboard"""
        from qgis.PyQt.QtWidgets import QApplication
        
        all_output = []
        all_output.append("=== SQL Code ===\n")
        all_output.append(self.sql_output.toPlainText())
        all_output.append("\n\n=== Python Code ===\n")
        all_output.append(self.python_output.toPlainText())
        all_output.append("\n\n=== Analysis ===\n")
        all_output.append(self.analysis_output.toPlainText())
        
        QApplication.clipboard().setText("\n".join(all_output))
        QMessageBox.information(self, "Copied", "All output copied to clipboard")

    def save_code(self):
        """Save current tab's code to file"""
        current_widget = self.output_tabs.currentWidget()
        if not current_widget:
            return
        
        current_index = self.output_tabs.currentIndex()
        default_ext = ".sql" if current_index == 0 else ".py" if current_index == 1 else ".txt"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Code",
            f"model_output{default_ext}",
            "SQL Files (*.sql);;Python Files (*.py);;Text Files (*.txt);;All Files (*.*)",
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(current_widget.toPlainText())
                QMessageBox.information(self, "Saved", f"Code saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
    
    def save_all_code(self):
        """Save all output to separate files"""
        base_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save All Output (choose base filename)",
            "model_output",
            "All Files (*.*)",
        )
        
        if not base_path:
            return
        
        # Remove extension if present
        import os
        base_name = os.path.splitext(base_path)[0]
        
        files_saved = []
        try:
            # Save SQL
            if self.sql_output.toPlainText().strip() and not self.sql_output.toPlainText().startswith("# No"):
                sql_path = f"{base_name}_sql.sql"
                with open(sql_path, "w", encoding="utf-8") as f:
                    f.write(self.sql_output.toPlainText())
                files_saved.append(sql_path)
            
            # Save Python
            if self.python_output.toPlainText().strip() and not self.python_output.toPlainText().startswith("# No"):
                py_path = f"{base_name}_python.py"
                with open(py_path, "w", encoding="utf-8") as f:
                    f.write(self.python_output.toPlainText())
                files_saved.append(py_path)
            
            # Save Analysis
            if self.analysis_output.toPlainText().strip() and not self.analysis_output.toPlainText().startswith("# No"):
                analysis_path = f"{base_name}_analysis.txt"
                with open(analysis_path, "w", encoding="utf-8") as f:
                    f.write(self.analysis_output.toPlainText())
                files_saved.append(analysis_path)
            
            # Save Combined
            combined_path = f"{base_name}_all.txt"
            with open(combined_path, "w", encoding="utf-8") as f:
                f.write(self.combined_output.toPlainText())
            files_saved.append(combined_path)
            
            if files_saved:
                QMessageBox.information(
                    self, 
                    "Saved", 
                    f"Saved {len(files_saved)} file(s):\n" + "\n".join(files_saved)
                )
            else:
                QMessageBox.warning(self, "Warning", "No content to save")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
    
    def clear_output(self):
        """Clear all output"""
        reply = QMessageBox.question(
            self,
            "Clear Output",
            "Are you sure you want to clear all output?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.sql_output.clear()
            self.python_output.clear()
            self.analysis_output.clear()
            self.combined_output.clear()
            self.output_tabs.setTabText(0, "📝 SQL Code")
            self.output_tabs.setTabText(1, "🐍 Python Code")
            self.output_tabs.setTabText(2, "🔍 Analysis")
            self.output_tabs.setTabText(3, "📋 All Output")
    
    def update_font_size(self, size):
        """Update font size for all output widgets"""
        font = QFont("Courier New", size)
        self.sql_output.setFont(font)
        self.python_output.setFont(font)
        self.combined_output.setFont(font)
        
        analysis_font = QFont("Arial", size)
        self.analysis_output.setFont(analysis_font)
    
    def toggle_word_wrap(self, enabled):
        """Toggle word wrap for all output widgets"""
        wrap_mode = QTextEdit.WidgetWidth if enabled else QTextEdit.NoWrap
        self.sql_output.setLineWrapMode(wrap_mode)
        self.python_output.setLineWrapMode(wrap_mode)
        self.analysis_output.setLineWrapMode(wrap_mode)
        self.combined_output.setLineWrapMode(wrap_mode)
