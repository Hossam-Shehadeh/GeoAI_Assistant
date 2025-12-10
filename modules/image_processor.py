from PIL import Image
import os
import time
from typing import Dict
from dotenv import load_dotenv
from qgis.core import QgsMessageLog, Qgis

# Load environment variables
PLUGIN_DIR = os.path.dirname(os.path.dirname(__file__))
env_path = os.path.join(PLUGIN_DIR, ".env")
load_dotenv(env_path)


class ImageProcessor:
    """Process Model Builder images and convert to code using Azure Computer Vision"""
    
    def __init__(self, llm_handler):
        self.llm = llm_handler
        self.azure_client = None
        self._initialize_azure_client()
    
    def _initialize_azure_client(self):
        """Initialize Azure Computer Vision client from .env"""
        try:
            from azure.cognitiveservices.vision.computervision import ComputerVisionClient
            from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
            from msrest.authentication import CognitiveServicesCredentials
        except ImportError as e:
            error_msg = (
                f"Azure Computer Vision SDK not installed: {str(e)}\n\n"
                "Please install using QGIS Python:\n"
                "1. Open QGIS Python Console (Plugins → Python Console)\n"
                "2. Run: import sys; print(sys.executable)\n"
                "3. Install packages: /path/to/qgis/python3 -m pip install azure-cognitiveservices-vision-computervision msrest\n"
                "4. Restart QGIS"
            )
            QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Critical)
            return
        
        try:
            # Reload .env file to get latest credentials
            load_dotenv(env_path, override=True)
            
            endpoint = os.getenv("AZURE_VISION_ENDPOINT")
            subscription_key = os.getenv("AZURE_VISION_SUBSCRIPTION_KEY")
            
            # Log what we found (without exposing the key)
            QgsMessageLog.logMessage(
                f"Loading Azure credentials from: {env_path}",
                "GeoAI",
                Qgis.Info
            )
            
            if not endpoint:
                QgsMessageLog.logMessage(
                    f"AZURE_VISION_ENDPOINT not found in .env file at {env_path}",
                    "GeoAI",
                    Qgis.Warning
                )
            if not subscription_key:
                QgsMessageLog.logMessage(
                    "AZURE_VISION_SUBSCRIPTION_KEY not found in .env file",
                    "GeoAI",
                    Qgis.Warning
                )
            
            if not endpoint or not subscription_key:
                error_msg = (
                    f"Azure Computer Vision credentials not found in .env file.\n"
                    f"File path: {env_path}\n"
                    f"Endpoint found: {bool(endpoint)}\n"
                    f"Key found: {bool(subscription_key)}\n\n"
                    "Please configure in Settings tab:\n"
                    "1. Go to Settings tab\n"
                    "2. Enter Azure endpoint and subscription key\n"
                    "3. Click 'Save Azure Credentials'\n"
                    "4. Restart QGIS"
                )
                QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Warning)
                return
            
            # Strip any whitespace
            endpoint = endpoint.strip()
            subscription_key = subscription_key.strip()
            
            # Create client
            self.azure_client = ComputerVisionClient(
                endpoint,
                CognitiveServicesCredentials(subscription_key)
            )
            self.VisualFeatureTypes = VisualFeatureTypes
            
            QgsMessageLog.logMessage(
                f"Azure Computer Vision client initialized successfully",
                "GeoAI",
                Qgis.Info
            )
            QgsMessageLog.logMessage(
                f"Endpoint: {endpoint}",
                "GeoAI",
                Qgis.Info
            )
            
        except Exception as e:
            error_msg = f"Error initializing Azure client: {str(e)}"
            QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Critical)
            import traceback
            QgsMessageLog.logMessage(traceback.format_exc(), "GeoAI", Qgis.Critical)
    
    def reload_azure_client(self):
        """Reload Azure client (useful after updating credentials)"""
        QgsMessageLog.logMessage("Reloading Azure Computer Vision client...", "GeoAI", Qgis.Info)
        self.azure_client = None
        
        # Force reload .env file
        load_dotenv(env_path, override=True)
        
        self._initialize_azure_client()
        
        if self.azure_client:
            QgsMessageLog.logMessage("Azure client reloaded successfully", "GeoAI", Qgis.Info)
        else:
            QgsMessageLog.logMessage("Azure client reload failed - check logs above", "GeoAI", Qgis.Warning)
        
        return self.azure_client is not None
    
    def analyze_image_with_azure(self, image_path: str) -> Dict:
        """
        Analyze image using Azure Computer Vision to extract description, shapes, and colors
        
        Args:
            image_path: Path to image file
        """
        if not self.azure_client:
            error_msg = "Azure Computer Vision client not initialized. Check .env file."
            QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Warning)
            return {"error": error_msg}
        
        if not os.path.exists(image_path):
            error_msg = f"Image file not found: {image_path}"
            QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Warning)
            return {"error": error_msg}
        
        try:
            QgsMessageLog.logMessage(f"Starting Azure analysis for: {image_path}", "GeoAI", Qgis.Info)
            
            # Analyze image with all features including color
            with open(image_path, "rb") as image_stream:
                QgsMessageLog.logMessage("Sending image to Azure for analysis...", "GeoAI", Qgis.Info)
                analysis = self.azure_client.analyze_image_in_stream(
                    image_stream,
                    visual_features=[
                        self.VisualFeatureTypes.description,
                        self.VisualFeatureTypes.objects,
                        self.VisualFeatureTypes.tags,
                        self.VisualFeatureTypes.brands,
                        self.VisualFeatureTypes.categories,
                        self.VisualFeatureTypes.color,  # Color detection
                        self.VisualFeatureTypes.image_type,  # Image type
                    ]
                )
                QgsMessageLog.logMessage("Azure analysis completed", "GeoAI", Qgis.Info)
            
            # OCR (text detection)
            QgsMessageLog.logMessage("Starting OCR text detection...", "GeoAI", Qgis.Info)
            with open(image_path, "rb") as image_stream:
                ocr_result = self.azure_client.read_in_stream(image_stream, raw=True)
            
            operation_location = ocr_result.headers["Operation-Location"]
            operation_id = operation_location.split("/")[-1]
            
            # Wait for OCR to complete
            max_attempts = 30
            attempt = 0
            while attempt < max_attempts:
                result = self.azure_client.get_read_result(operation_id)
                if result.status not in ["notStarted", "running"]:
                    QgsMessageLog.logMessage(f"OCR completed with status: {result.status}", "GeoAI", Qgis.Info)
                    break
                attempt += 1
                time.sleep(1)
            
            if attempt >= max_attempts:
                QgsMessageLog.logMessage("OCR timed out", "GeoAI", Qgis.Warning)
                result = None
            
            # Generate comprehensive description
            description = self._generate_full_description(analysis, result)
            QgsMessageLog.logMessage(f"Generated description length: {len(description)} characters", "GeoAI", Qgis.Info)
            
            return {
                "success": True,
                "description": description,
                "analysis": analysis,
                "text_result": result
            }
            
        except Exception as e:
            error_msg = f"Azure vision analysis error: {str(e)}"
            QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Critical)
            import traceback
            QgsMessageLog.logMessage(traceback.format_exc(), "GeoAI", Qgis.Critical)
            return {"error": error_msg}
    
    def _generate_full_description(self, analysis, text_result=None) -> str:
        """Generate full textual description from Azure analysis including shapes and colors"""
        parts = []
        
        # Main caption with confidence
        if analysis.description.captions:
            caption = analysis.description.captions[0]
            parts.append(f"IMAGE SUMMARY: {caption.text}")
            if hasattr(caption, 'confidence'):
                parts.append(f"Confidence: {caption.confidence:.2%}")
        
        # OCR text - Most important for code generation
        if text_result and text_result.status == "succeeded":
            text_lines = []
            for page in text_result.analyze_result.read_results:
                for line in page.lines:
                    if line.text and line.text.strip():
                        text_lines.append(line.text.strip())
            
            if text_lines:
                parts.append("")
                parts.append("DETECTED TEXT IN IMAGE:")
                parts.append("-" * 60)
                for i, line_text in enumerate(text_lines[:20], 1):  # First 20 lines
                    parts.append(f"{i}. {line_text}")
                if len(text_lines) > 20:
                    parts.append(f"... and {len(text_lines) - 20} more lines")
                parts.append("-" * 60)
        
        # Objects (shapes and items) - Important for diagrams
        if analysis.objects:
            parts.append("")
            parts.append("DETECTED OBJECTS/SHAPES:")
            for i, obj in enumerate(analysis.objects[:15], 1):  # top 15 objects
                obj_info = f"{i}. {obj.object_property}"
                if hasattr(obj, 'confidence'):
                    obj_info += f" (confidence: {obj.confidence:.2%})"
                if hasattr(obj, 'rectangle') and obj.rectangle:
                    rect = obj.rectangle
                    obj_info += f" at position ({rect.x}, {rect.y}, {rect.w}x{rect.h})"
                parts.append(obj_info)
        
        # Tags - Context information
        if analysis.tags:
            parts.append("")
            parts.append("IMAGE TAGS (context):")
            tag_list = []
            for tag in analysis.tags[:20]:  # top 20 tags
                tag_name = tag.name
                if hasattr(tag, 'confidence'):
                    tag_name += f" ({tag.confidence:.2%})"
                tag_list.append(tag_name)
            parts.append(", ".join(tag_list))
        
        # Categories
        if analysis.categories:
            parts.append("")
            parts.append("IMAGE CATEGORIES:")
            for cat in analysis.categories[:5]:
                cat_info = cat.name
                if hasattr(cat, 'score'):
                    cat_info += f" (score: {cat.score:.2f})"
                parts.append(f"- {cat_info}")
        
        # Color information - Less important but useful
        if hasattr(analysis, 'color') and analysis.color:
            color_info = []
            if analysis.color.dominant_colors:
                color_info.append(f"Dominant: {', '.join(analysis.color.dominant_colors)}")
            if analysis.color.accent_color:
                color_info.append(f"Accent: {analysis.color.accent_color}")
            if analysis.color.is_bw_img:
                color_info.append("Black & white image")
            if color_info:
                parts.append("")
                parts.append("COLOR ANALYSIS: " + " | ".join(color_info))
        
        return "\n".join(parts)
    
    def process_model_image(self, image_path: str, output_type: str = 'sql', model_provider: str = 'ollama', model_name: str = 'phi3') -> Dict:
        """
        Process model builder screenshot and convert to code
        
        Args:
            image_path: Path to model builder screenshot
            output_type: 'sql', 'python', or 'both'
            model_provider: 'ollama', 'openrouter', or other LLM provider
            model_name: Model name (e.g., 'phi3', 'mistral-7b-instruct')
        """
        QgsMessageLog.logMessage(
            f"Processing image: {image_path} | Type: {output_type} | Provider: {model_provider} | Model: {model_name}",
            "GeoAI",
            Qgis.Info
        )
        
        if not os.path.exists(image_path):
            error_msg = f"Image file not found: {image_path}"
            QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Critical)
            return {"error": error_msg}
        
        # Validate image
        try:
            img = Image.open(image_path)
            img.verify()
            QgsMessageLog.logMessage(f"Image validated: {img.size[0]}x{img.size[1]} pixels", "GeoAI", Qgis.Info)
        except Exception as e:
            error_msg = f"Invalid image file: {str(e)}"
            QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Critical)
            return {"error": error_msg}
        
        # Step 1: Check Azure first, then fallback to LLM direct processing
        azure_available = False
        azure_description = None
        
        # Try to use Azure Computer Vision first
        if self.azure_client:
            QgsMessageLog.logMessage("Step 1: Checking Azure Computer Vision availability...", "GeoAI", Qgis.Info)
            azure_result = self.analyze_image_with_azure(image_path)
            
            if "error" not in azure_result and azure_result.get("description"):
                # Azure succeeded
                azure_available = True
                azure_description = azure_result.get("description", "")
                QgsMessageLog.logMessage(
                    f"✅ Azure Computer Vision analysis successful ({len(azure_description)} chars)",
                    "GeoAI",
                    Qgis.Info
                )
                QgsMessageLog.logMessage(f"Azure description preview: {azure_description[:200]}...", "GeoAI", Qgis.Info)
            else:
                # Azure failed - log but continue to fallback
                error_info = azure_result.get('error', 'Unknown error')
                QgsMessageLog.logMessage(
                    f"⚠️ Azure Computer Vision failed: {error_info}. Falling back to LLM direct processing...",
                    "GeoAI",
                    Qgis.Warning
                )
        else:
            # Try to reload Azure client
            QgsMessageLog.logMessage("Azure client not initialized, attempting to reload...", "GeoAI", Qgis.Info)
            self.reload_azure_client()
            
            if self.azure_client:
                # Retry Azure after reload
                azure_result = self.analyze_image_with_azure(image_path)
                if "error" not in azure_result and azure_result.get("description"):
                    azure_available = True
                    azure_description = azure_result.get("description", "")
                    QgsMessageLog.logMessage(
                        f"✅ Azure Computer Vision analysis successful after reload ({len(azure_description)} chars)",
                        "GeoAI",
                        Qgis.Info
                    )
                else:
                    QgsMessageLog.logMessage(
                        "⚠️ Azure still not available after reload. Using LLM fallback...",
                        "GeoAI",
                        Qgis.Warning
                    )
            else:
                QgsMessageLog.logMessage(
                    "⚠️ Azure Computer Vision not configured. Using LLM direct image processing...",
                    "GeoAI",
                    Qgis.Info
                )
        
        # Step 2: Generate code using either Azure description or LLM direct processing
        result = None
        
        if azure_available and azure_description:
            # PREFERRED: Use Azure description to generate code with selected model
            QgsMessageLog.logMessage(
                f"✅ Step 2: Generating {output_type} code from Azure description using {model_provider}/{model_name}...",
                "GeoAI",
                Qgis.Info
            )
            QgsMessageLog.logMessage(
                f"Azure description length: {len(azure_description)} chars | Preview: {azure_description[:200]}...",
                "GeoAI",
                Qgis.Info
            )
            QgsMessageLog.logMessage(
                f"Using selected model '{model_name}' (not vision model) - Azure already analyzed the image",
                "GeoAI",
                Qgis.Info
            )
            
            try:
                result = self.llm.generate_code_from_image_description(
                    azure_description,
                    output_type,
                    model_provider,
                    model_name  # Use selected model, not vision model
                )
                
                # Add Azure info to result
                if isinstance(result, dict):
                    result["analysis_method"] = "azure_computer_vision"
                    result["azure_description"] = azure_description
                
                QgsMessageLog.logMessage(
                    f"✅ Code generation completed using {model_provider}/{model_name}. Result keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}",
                    "GeoAI",
                    Qgis.Info
                )
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                QgsMessageLog.logMessage(
                    f"❌ Exception during code generation: {str(e)}\n{error_trace}",
                    "GeoAI",
                    Qgis.Critical
                )
                result = {
                    "error": f"Code generation failed: {str(e)}",
                    "code": "",
                    "explanation": "",
                    "type": output_type,
                    "success": False,
                    "analysis_method": "azure_computer_vision",
                    "azure_description": azure_description
                }
        
        if not azure_available or not azure_description or not result:
            # Fallback: Use LLM to process image directly (only if Azure not available)
            QgsMessageLog.logMessage(
                f"⚠️ Step 2: Azure not available. Using LLM direct image processing ({model_provider}/{model_name}) as fallback...",
                "GeoAI",
                Qgis.Warning
            )
            QgsMessageLog.logMessage(
                "💡 For better results, configure Azure Computer Vision in Settings tab",
                "GeoAI",
                Qgis.Info
            )
            QgsMessageLog.logMessage(
                "Note: LLM direct processing requires vision-capable model",
                "GeoAI",
                Qgis.Info
            )
            
            # Check if LLM supports vision (only needed for fallback)
            try:
                # For fallback, we need a vision-capable model
                # But we'll try with the selected model first
                result = self.llm.analyze_image_to_code(
                    image_path,
                    output_type,
                    model_provider,
                    model_name  # Try selected model first
                )
            except Exception as e:
                error_msg = (
                    f"LLM direct image processing failed: {str(e)}\n\n"
                    "This may happen if:\n"
                    "1. The selected LLM provider doesn't support vision/image processing\n"
                    "2. The model doesn't support images\n"
                    "3. API key is missing or invalid\n\n"
                    "Try:\n"
                    "1. Configure Azure Computer Vision in Settings tab\n"
                    "2. Use a vision-capable LLM (OpenAI GPT-4o, Claude, Google Gemini)\n"
                    "3. Check your API keys in Settings"
                )
                QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Critical)
                return {"error": error_msg}
        
        if "error" in result:
            error_msg = f"Code generation failed: {result.get('error')}"
            QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Critical)
            return result
        
        # Parse and structure the response
        # LLM direct processing returns {"code": "...", "type": "...", "extracted_info": "..."}
        # Azure path uses generate_code_from_image_description which needs structuring
        structured = None
        if azure_available and azure_description:
            structured = self._structure_code_output(result)
            structured["azure_description"] = azure_description
            structured["analysis_method"] = "azure_computer_vision"
            
            # Ensure code is extracted - if structured output has no code, use raw
            if not structured.get("sql_code") and not structured.get("python_code"):
                raw_code = result.get("code", "") or result.get("explanation", "") or structured.get("raw_response", "")
                if raw_code:
                    # Try to extract code blocks from raw
                    import re
                    sql_blocks = re.findall(r'```sql\n?(.*?)\n?```', raw_code, re.DOTALL)
                    python_blocks = re.findall(r'```python\n?(.*?)\n?```', raw_code, re.DOTALL)
                    
                    if sql_blocks:
                        structured["sql_code"] = '\n\n'.join(sql_blocks).strip()
                    elif python_blocks:
                        structured["python_code"] = '\n\n'.join(python_blocks).strip()
                    else:
                        # No code blocks, use raw content
                        if output_type.lower() == "sql":
                            structured["sql_code"] = raw_code.strip()
                        elif output_type.lower() == "python":
                            structured["python_code"] = raw_code.strip()
                        else:
                            structured["sql_code"] = raw_code.strip()
                    
                    QgsMessageLog.logMessage(
                        f"Extracted code from raw response: {len(raw_code)} chars",
                        "GeoAI",
                        Qgis.Info
                    )
        else:
            # LLM direct path - already has code, just format it
            code = result.get("code", "")
            code_type = result.get("type", output_type).lower()
            
            structured = {
                "success": True,
                "analysis_method": "llm_direct",
                "azure_description": None
            }
            
            # Set code in appropriate field
            if code_type == "sql":
                structured["sql_code"] = code
                structured["python_code"] = None
            elif code_type == "python":
                structured["sql_code"] = None
                structured["python_code"] = code
            else:
                # Default to sql_code for output_type
                if output_type.lower() == "sql":
                    structured["sql_code"] = code
                    structured["python_code"] = None
                elif output_type.lower() == "python":
                    structured["sql_code"] = None
                    structured["python_code"] = code
                else:
                    structured["sql_code"] = code
                    structured["python_code"] = None
            
            structured["raw_response"] = code
            structured["extracted_info"] = result.get("extracted_info", "")
        
        # Log success with detailed info
        has_sql = structured.get("sql_code") is not None
        has_python = structured.get("python_code") is not None
        sql_len = len(structured.get("sql_code", "")) if structured.get("sql_code") else 0
        python_len = len(structured.get("python_code", "")) if structured.get("python_code") else 0
        raw_len = len(structured.get("raw_response", "")) if structured.get("raw_response") else 0
        
        QgsMessageLog.logMessage(
            f"Image processing completed successfully | "
            f"Method: {structured.get('analysis_method', 'unknown')} | "
            f"SQL: {has_sql} ({sql_len} chars) | "
            f"Python: {has_python} ({python_len} chars) | "
            f"Raw response: {raw_len} chars",
            "GeoAI",
            Qgis.Info
        )
        
        # Ensure at least one code field has content
        if not has_sql and not has_python and raw_len > 0:
            # Fallback: put raw response in appropriate field
            QgsMessageLog.logMessage(
                "No structured code found, using raw_response as fallback",
                "GeoAI",
                Qgis.Warning
            )
            if output_type.lower() == "sql":
                structured["sql_code"] = structured.get("raw_response", "")
            elif output_type.lower() == "python":
                structured["python_code"] = structured.get("raw_response", "")
            else:
                structured["sql_code"] = structured.get("raw_response", "")
        
        return structured
    
    def _clean_code(self, code: str) -> str:
        """Clean extracted code by removing markdown, comments, and formatting"""
        import re
        
        if not code:
            return ""
        
        # Remove markdown code blocks if still present
        code = re.sub(r'```sql\s*\n?(.*?)\n?```', r'\1', code, flags=re.DOTALL | re.IGNORECASE)
        code = re.sub(r'```python\s*\n?(.*?)\n?```', r'\1', code, flags=re.DOTALL | re.IGNORECASE)
        code = re.sub(r'```\s*\n?(.*?)\n?```', r'\1', code, flags=re.DOTALL)
        
        # Remove Python-style triple quotes
        code = re.sub(r'"""[\s\S]*?"""', '', code)
        code = re.sub(r"'''[\s\S]*?'''", '', code)
        
        # Remove markdown headers and formatting
        code = re.sub(r'^#+\s*.*?(Analysis Method|Azure|LLM|Generated Code|Computer Vision).*?$', '', code, flags=re.MULTILINE | re.IGNORECASE)
        code = re.sub(r'^=+\s*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'^-+\s*$', '', code, flags=re.MULTILINE)
        
        # Remove lines that are just markdown formatting or headers
        lines = code.split('\n')
        cleaned_lines = []
        skip_next_empty = False
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines after headers
            if skip_next_empty and not stripped:
                skip_next_empty = False
                continue
            
            # Skip markdown-style headers and separators
            if stripped.startswith('#') and any(keyword in stripped for keyword in ['Analysis', 'Method', 'Azure', 'LLM', 'Generated', 'Computer', 'Vision']):
                skip_next_empty = True
                continue
            if stripped in ['=', '-', '=' * 60, '-' * 60]:
                continue
            if stripped.startswith('📋') or stripped.startswith('💻') or stripped.startswith('✅') or stripped.startswith('⚠️'):
                continue
            
            cleaned_lines.append(line)
        
        code = '\n'.join(cleaned_lines)
        
        # Clean up multiple blank lines
        code = re.sub(r'\n{3,}', '\n\n', code)
        
        return code.strip()
    
    def _structure_code_output(self, raw_result: Dict) -> Dict:
        """Structure the code output from LLM"""
        
        code_content = raw_result.get('code', '') or raw_result.get('explanation', '') or raw_result.get('sql', '')
        
        if not code_content:
            return {
                "success": True,
                "explanation": "",
                "sql_code": None,
                "python_code": None,
                "raw_response": ""
            }
        
        # Extract code blocks - more flexible patterns
        import re
        
        # Try multiple patterns for code blocks
        sql_blocks = re.findall(r'```sql\s*\n?(.*?)\n?```', code_content, re.DOTALL | re.IGNORECASE)
        python_blocks = re.findall(r'```python\s*\n?(.*?)\n?```', code_content, re.DOTALL | re.IGNORECASE)
        
        # Also try without language tag
        if not sql_blocks and not python_blocks:
            generic_blocks = re.findall(r'```\s*\n?(.*?)\n?```', code_content, re.DOTALL)
            if generic_blocks:
                # Check content to determine type
                for block in generic_blocks:
                    block_clean = block.strip()
                    if 'SELECT' in block_clean.upper() or 'CREATE' in block_clean.upper() or 'FROM' in block_clean.upper():
                        sql_blocks.append(block_clean)
                    elif 'def ' in block_clean or 'import ' in block_clean or 'class ' in block_clean:
                        python_blocks.append(block_clean)
        
        # If no code blocks found, try to extract any code-like content
        if not sql_blocks and not python_blocks:
            # Look for any code-like patterns in the full content
            content_upper = code_content.upper()
            if 'SELECT' in content_upper or 'CREATE' in content_upper or 'INSERT' in content_upper or 'UPDATE' in content_upper:
                sql_blocks = [code_content]
            elif 'def ' in code_content or 'import ' in code_content or 'class ' in code_content:
                python_blocks = [code_content]
            else:
                # Default: treat as SQL if it looks like code
                if any(keyword in content_upper for keyword in ['SELECT', 'FROM', 'WHERE', 'CREATE', 'INSERT']):
                    sql_blocks = [code_content]
                elif any(keyword in code_content for keyword in ['def ', 'import ', 'class ', 'print(']):
                    python_blocks = [code_content]
        
        # Clean extracted code
        sql_code = self._clean_code('\n\n'.join(sql_blocks).strip()) if sql_blocks else None
        python_code = self._clean_code('\n\n'.join(python_blocks).strip()) if python_blocks else None
        
        return {
            "success": True,
            "explanation": code_content,
            "sql_code": sql_code,
            "python_code": python_code,
            "raw_response": code_content
        }