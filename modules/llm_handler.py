"""
Unified LLM Handler - Supports multiple providers with dynamic model selection
Supports: OpenAI, OpenRouter, Anthropic, Google Gemini, Ollama, HuggingFace
"""

import os
import re
import base64
import requests
from typing import Dict, List, Optional
from qgis.core import QgsMessageLog, Qgis
from dotenv import load_dotenv

PLUGIN_DIR = os.path.dirname(os.path.dirname(__file__))
env_path = os.path.join(PLUGIN_DIR, ".env")
load_dotenv(env_path)


class LLMHandler:
    """Unified handler for all LLM interactions with multiple providers."""

    def __init__(self):
        """Initialize LLM client based on selected provider (.env)"""
        plugin_dir = os.path.dirname(os.path.dirname(__file__))
        load_dotenv(os.path.join(plugin_dir, ".env"))

        self.provider = os.getenv("LLM_PROVIDER", "ollama").lower()
        self.client = None
        self.api_url = None
        self.text_model = os.getenv("LLM_MODEL_TEXT")
        self.vision_model = os.getenv("LLM_MODEL_VISION")
        self.api_key = None
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

        # Initialize provider-specific clients
        if self.provider == "openai":
            import openai

            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY not found in .env")
            self.client = openai.OpenAI(api_key=self.api_key)
            if not self.text_model:
                self.text_model = "gpt-4o-mini"
            if not self.vision_model:
                self.vision_model = "gpt-4o"

        elif self.provider == "openrouter":
            import openai

            self.api_key = os.getenv("OPENROUTER_API_KEY")
            if not self.api_key:
                raise ValueError("OPENROUTER_API_KEY not found in .env")
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": os.getenv(
                        "OPENROUTER_SITE_URL", "https://qgis.local"
                    ),
                    "X-Title": os.getenv("OPENROUTER_APP_NAME", "GeoAI Assistant"),
                },
            )
            if not self.text_model:
                self.text_model = "mistralai/mistral-7b-instruct"
            if not self.vision_model:
                self.vision_model = "openai/gpt-4o"

        elif self.provider == "anthropic":
            import anthropic

            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in .env")
            self.client = anthropic.Anthropic(api_key=self.api_key)
            if not self.text_model:
                self.text_model = "claude-3-5-sonnet-20241022"
            if not self.vision_model:
                self.vision_model = "claude-3-5-sonnet-20241022"

        elif self.provider == "google":
            try:
                import google.generativeai as genai

                self.api_key = os.getenv("GOOGLE_API_KEY")
                if not self.api_key:
                    raise ValueError("GOOGLE_API_KEY not found in .env")
                genai.configure(api_key=self.api_key)
                self.client = genai
                if not self.text_model:
                    self.text_model = "models/gemini-pro-latest"
                if not self.vision_model:
                    self.vision_model = "models/gemini-2.5-flash-image"
            except ImportError:
                QgsMessageLog.logMessage(
                    "Google Generative AI SDK not installed. Install with: pip install google-generativeai",
                    "GeoAI",
                    Qgis.Warning,
                )
                raise ValueError("Google Generative AI SDK not installed")

        elif self.provider == "ollama":
            self.ollama_base_url = os.getenv(
                "OLLAMA_BASE_URL", "http://localhost:11434"
            )
            if not self.text_model:
                self.text_model = "phi3"
            if not self.vision_model:
                self.vision_model = "phi3"
            self.client = None

        elif self.provider == "huggingface":
            self.api_key = os.getenv("HF_API_KEY")
            if not self.api_key:
                raise ValueError("HF_API_KEY not found in .env")
            if not self.text_model:
                self.text_model = "HuggingFaceH4/zephyr-7b-beta"
            if not self.vision_model:
                self.vision_model = ""
            self.api_url = (
                f"https://api-inference.huggingface.co/models/{self.text_model}"
            )
            self.client = None

        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _ollama_query(
        self,
        prompt: str,
        system_prompt: str = "",
        model: str = None,
        images: Optional[List[str]] = None,
    ) -> str:
        """Call Ollama API"""
        if model is None:
            model = self.text_model

        url = f"{self.ollama_base_url}/api/generate"
        payload = {"model": model, "prompt": prompt, "stream": False}
        if system_prompt:
            payload["system"] = system_prompt
        if images:
            payload["images"] = images

        QgsMessageLog.logMessage(
            f"Calling Ollama API: {url} | Model: {model} | Prompt length: {len(prompt)} chars",
            "GeoAI",
            Qgis.Info,
        )

        try:
            QgsMessageLog.logMessage(
                "Sending request to Ollama (timeout: 180s)...", "GeoAI", Qgis.Info
            )
            response = requests.post(
                url, json=payload, timeout=180
            )  # Increased timeout to 180s

            QgsMessageLog.logMessage(
                f"Ollama response status: {response.status_code}", "GeoAI", Qgis.Info
            )

            if response.status_code != 200:
                error_text = response.text[:500]  # Limit error text
                QgsMessageLog.logMessage(
                    f"Ollama error response: {error_text}", "GeoAI", Qgis.Critical
                )
                raise Exception(
                    f"Ollama error (status {response.status_code}): {error_text}"
                )

            data = response.json()
            result = data.get("response", "").strip()

            if result:
                QgsMessageLog.logMessage(
                    f"Ollama response received: {len(result)} characters",
                    "GeoAI",
                    Qgis.Info,
                )
            else:
                QgsMessageLog.logMessage(
                    "Ollama returned empty response", "GeoAI", Qgis.Warning
                )

            return result

        except requests.exceptions.Timeout:
            error_msg = f"Ollama request timed out after 180 seconds. Model {model} may be too slow or not responding."
            QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Critical)
            raise Exception(error_msg)
        except requests.exceptions.ConnectionError:
            error_msg = f"Could not connect to Ollama at {self.ollama_base_url}. Make sure Ollama is running."
            QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Critical)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Ollama connection error: {str(e)}"
            QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Critical)
            raise Exception(error_msg)

    def _hf_query(self, prompt: str) -> str:
        """Call Hugging Face Inference API"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post(
            self.api_url,
            headers=headers,
            json={"inputs": prompt},
            timeout=120,
        )
        if response.status_code != 200:
            raise Exception(f"Hugging Face error: {response.text}")
        data = response.json()
        if isinstance(data, list) and len(data) and "generated_text" in data[0]:
            return data[0]["generated_text"]
        return str(data)

    def _query_with_provider(
        self,
        prompt: str,
        system_prompt: str = None,
        model_provider: str = None,
        model_name: str = None,
    ) -> str:
        """Generic query method that supports dynamic provider/model selection"""
        provider = model_provider.lower() if model_provider else self.provider
        model = model_name if model_name else self.text_model

        if provider == "ollama":
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            return self._ollama_query(full_prompt, "", model)

        elif provider == "openrouter":
            import openai

            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY not found in .env")
            client = openai.OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": os.getenv(
                        "OPENROUTER_SITE_URL", "https://qgis.local"
                    ),
                    "X-Title": os.getenv("OPENROUTER_APP_NAME", "GeoAI Assistant"),
                },
            )
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(model=model, messages=messages)
            return response.choices[0].message.content

        elif provider == "openai":
            import openai

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in .env")
            client = openai.OpenAI(api_key=api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(model=model, messages=messages)
            return response.choices[0].message.content

        elif provider == "anthropic":
            import anthropic

            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in .env")
            client = anthropic.Anthropic(api_key=api_key)

            system_msg = system_prompt if system_prompt else ""
            response = client.messages.create(
                model=model,
                max_tokens=4000,
                system=system_msg,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text

        elif provider == "google":
            try:
                import google.generativeai as genai
                import time
                
                # Try to import Google API exceptions (may not always be available)
                try:
                    from google.api_core import exceptions as google_exceptions
                except ImportError:
                    google_exceptions = None

                api_key = os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    raise ValueError("GOOGLE_API_KEY not found in .env")
                genai.configure(api_key=api_key)
                model_instance = genai.GenerativeModel(model)
                
                # Configure safety settings to be most permissive
                # Use proper enum values from Google API
                try:
                    from google.generativeai.types import HarmCategory, HarmBlockThreshold
                    safety_settings = [
                        {
                            "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                            "threshold": HarmBlockThreshold.BLOCK_NONE,
                        },
                        {
                            "category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                            "threshold": HarmBlockThreshold.BLOCK_NONE,
                        },
                        {
                            "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
                            "threshold": HarmBlockThreshold.BLOCK_NONE,
                        },
                        {
                            "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                            "threshold": HarmBlockThreshold.BLOCK_NONE,
                        },
                    ]
                except ImportError:
                    # Fallback to string format if enums not available
                    safety_settings = [
                        {
                            "category": "HARM_CATEGORY_HATE_SPEECH",
                            "threshold": "BLOCK_NONE",
                        },
                        {
                            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            "threshold": "BLOCK_NONE",
                        },
                        {
                            "category": "HARM_CATEGORY_HARASSMENT",
                            "threshold": "BLOCK_NONE",
                        },
                        {
                            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                            "threshold": "BLOCK_NONE",
                        },
                    ]
                
                # Retry logic for quota/rate limit errors
                max_retries = 3
                retry_delay = 5  # Start with 5 seconds
                
                for attempt in range(max_retries):
                    try:
                        response = model_instance.generate_content(
                            [system_prompt, prompt] if system_prompt else [prompt],
                            generation_config=genai.types.GenerationConfig(
                                temperature=0.7, top_p=0.0, top_k=1, max_output_tokens=2000
                            ),
                            safety_settings=safety_settings,
                        )
                        try:
                            return response.text
                        except ValueError as ve:
                            # Check if it's a safety blocking issue
                            if hasattr(response, 'prompt_feedback'):
                                safety_feedback = response.prompt_feedback.safety_ratings
                                block_reason = "Content blocked due to safety policies."
                                if safety_feedback:
                                    block_reason += f" Feedback: {safety_feedback}"
                                
                                # Try to get partial response if available
                                if hasattr(response, 'candidates') and response.candidates:
                                    candidate = response.candidates[0]
                                    if hasattr(candidate, 'content') and candidate.content:
                                        # Sometimes we can get the response despite blocking
                                        try:
                                            return candidate.content.parts[0].text
                                        except (AttributeError, IndexError, KeyError):
                                            pass
                                
                                QgsMessageLog.logMessage(
                                    f"⚠️ Gemini API Blocked: {block_reason}",
                                    "GeoAI",
                                    Qgis.Warning
                                )
                                
                                # Try automatic fallback to a different model
                                if model == "models/gemini-2.5-pro" and attempt < max_retries - 1:
                                    QgsMessageLog.logMessage(
                                        "🔄 Auto-fallback: Trying gemini-2.5-flash instead...",
                                        "GeoAI",
                                        Qgis.Info
                                    )
                                    # Switch to flash model
                                    model = "models/gemini-2.5-flash"
                                    model_instance = genai.GenerativeModel(model)
                                    continue
                                
                                # If this is the last attempt, provide helpful error
                                if attempt == max_retries - 1:
                                    # Check if we already tried flash model
                                    tried_flash = original_model != model and "flash" in model
                                    
                                    if tried_flash:
                                        error_msg = (
                                            f"❌ Google Gemini blocked the response (even with flash model).\n\n"
                                            f"RECOMMENDED SOLUTIONS:\n"
                                            f"1. ⭐ Use Ollama provider (no restrictions, local)\n"
                                            f"2. Switch to OpenAI or Anthropic provider\n"
                                            f"3. Rephrase query with more neutral language\n"
                                            f"4. Break query into smaller, simpler parts\n\n"
                                            f"Note: Google has hard-coded safety filters that cannot be disabled,\n"
                                            f"even with BLOCK_NONE settings. This is a Google API limitation."
                                        )
                                    else:
                                        error_msg = (
                                            f"❌ Google Gemini blocked the response.\n\n"
                                            f"QUICK FIX:\n"
                                            f"1. ⭐ Switch to 'gemini-2.5-flash' model (less strict)\n"
                                            f"   → Select in model dropdown\n\n"
                                            f"OTHER OPTIONS:\n"
                                            f"2. Use Ollama provider (no restrictions)\n"
                                            f"3. Switch to OpenAI or Anthropic\n"
                                            f"4. Rephrase query with neutral language\n\n"
                                            f"Note: Safety settings are already most permissive.\n"
                                            f"Google has hard-coded filters that cannot be disabled."
                                        )
                                    raise ValueError(error_msg)
                                
                                # Retry with current model
                                continue
                            else:
                                # Not a safety issue, re-raise
                                raise ve
                    
                    except Exception as quota_error:
                        error_str = str(quota_error).lower()
                        
                        # Check if it's a quota/rate limit error
                        is_quota_error = False
                        if google_exceptions and isinstance(quota_error, google_exceptions.ResourceExhausted):
                            is_quota_error = True
                        elif "quota" in error_str or "429" in str(quota_error) or "rate limit" in error_str:
                            is_quota_error = True
                        
                        if is_quota_error:
                            # Extract retry delay from error if available
                            retry_seconds = retry_delay
                            if "retry in" in error_str or "retry_delay" in error_str:
                                match = re.search(r'retry in ([\d.]+)s?', error_str)
                                if match:
                                    retry_seconds = max(int(float(match.group(1))), 5)
                            
                            if attempt < max_retries - 1:
                                QgsMessageLog.logMessage(
                                    f"⚠️ Google API quota exceeded (attempt {attempt + 1}/{max_retries}). "
                                    f"Retrying in {retry_seconds} seconds...",
                                    "GeoAI",
                                    Qgis.Warning
                                )
                                time.sleep(retry_seconds)
                                retry_delay *= 2  # Exponential backoff
                                continue
                            else:
                                # Final attempt failed
                                error_msg = (
                                    f"❌ Google Gemini API quota exceeded for model '{model}'.\n\n"
                                    f"SOLUTIONS:\n"
                                    f"1. Wait {retry_seconds} seconds and try again\n"
                                    f"2. Switch to a different model:\n"
                                    f"   - models/gemini-2.5-flash (faster, better free tier)\n"
                                    f"   - models/gemini-pro-latest (alternative)\n"
                                    f"3. Switch to a different provider (Ollama, OpenAI, etc.)\n"
                                    f"4. Upgrade your Google API plan\n\n"
                                    f"Free tier limits: https://ai.google.dev/gemini-api/docs/rate-limits"
                                )
                                QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Critical)
                                raise ValueError(error_msg)
                        else:
                            # Not a quota error, re-raise immediately
                            raise
                            
            except ImportError:
                QgsMessageLog.logMessage(
                    "Google Generative AI SDK not installed. Install with: pip install google-generativeai",
                    "GeoAI",
                    Qgis.Warning,
                )
                raise ValueError("Google Generative AI SDK not installed")

        elif provider == "huggingface":
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            return self._hf_query(full_prompt)

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def generate_sql(
        self,
        prompt: str,
        context: Dict,
        model_provider: str = None,
        model_name: str = None,
    ) -> Dict:
        """Generate SQL from natural language prompt."""
        system_prompt = self._build_sql_system_prompt(context)

        QgsMessageLog.logMessage(
            f"LLM Context (generate_sql): {context}", "GeoAI", Qgis.Info
        )

        try:
            content = self._query_with_provider(
                prompt, system_prompt, model_provider, model_name
            )
            return self._parse_sql_response(content)

        except Exception as e:
            QgsMessageLog.logMessage(f"LLM Error: {str(e)}", "GeoAI", Qgis.Critical)
            return {"error": str(e)}

    def fix_sql_error(
        self,
        sql: str,
        error: str,
        context: Dict,
        model_provider: str = None,
        model_name: str = None,
    ) -> Dict:
        """Fix SQL query that produced an error"""
        # Build field list separately to avoid f-string backslash issue
        fields_list = []
        for layer_name, fields in context.get("table_fields", {}).items():
            quoted_fields = [f'"{field}"' for field in fields]
            fields_list.append(f"  - {layer_name}: {', '.join(quoted_fields)}")

        fields_text = "\n".join(fields_list) if fields_list else ""
        newline = "\n"

        prompt = (
            f"Fix this SQL query that produced an error:{newline}{newline}"
            f"SQL:{newline}```sql{newline}{sql}{newline}```{newline}{newline}Error:{newline}{error}{newline}{newline}"
            f"Context:{newline}Database: {context.get('db_type','Unknown')}{newline}"
            f"Tables: {', '.join(context.get('tables', []))}{newline}"
            f"All Layer Fields (use exact casing with double quotes):{newline}"
            f"{fields_text}{newline}"
        )
        system_prompt = (
            "You are a SQL expert specializing in geospatial databases (PostGIS, SpatiaLite). "
            'Fix SQL errors and explain the solution. IMPORTANT: All column names must use their exact casing and be wrapped in double quotes (e.g., SELECT "Name" FROM table).'
        )

        try:
            content = self._query_with_provider(
                prompt, system_prompt, model_provider, model_name
            )
            return self._parse_sql_response(content)
        except Exception as e:
            return {"error": str(e)}

    def analyze_image_to_code(
        self,
        image_path: str,
        conversion_type: str,
        model_provider: str = None,
        model_name: str = None,
    ) -> Dict:
        """Analyze Model Builder image and convert to code - supports direct image analysis"""
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        extraction_prompt = (
            "Analyze this QGIS Model Builder diagram. List all:\n"
            "1. Input layers/data sources\n"
            "2. Processing steps/algorithms\n"
            "3. Parameters and settings\n"
            "4. Output layers\n"
            "5. Connections between steps\n"
            "Provide detailed, structured information."
        )

        provider = model_provider.lower() if model_provider else self.provider
        model = model_name if model_name else self.vision_model

        try:
            if provider == "anthropic":
                r = self.client.messages.create(
                    model=model,
                    max_tokens=4000,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/png",
                                        "data": image_data,
                                    },
                                },
                                {"type": "text", "text": extraction_prompt},
                            ],
                        }
                    ],
                )
                extracted_info = r.content[0].text
            elif provider == "openai":
                r = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": extraction_prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{image_data}",
                                    },
                                },
                            ],
                        }
                    ],
                )
                extracted_info = r.choices[0].message.content
            elif provider == "google":
                import google.generativeai as genai

                # Configure safety settings to be most permissive
                try:
                    from google.generativeai.types import HarmCategory, HarmBlockThreshold
                    safety_settings = [
                        {
                            "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                            "threshold": HarmBlockThreshold.BLOCK_NONE,
                        },
                        {
                            "category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                            "threshold": HarmBlockThreshold.BLOCK_NONE,
                        },
                        {
                            "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
                            "threshold": HarmBlockThreshold.BLOCK_NONE,
                        },
                        {
                            "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                            "threshold": HarmBlockThreshold.BLOCK_NONE,
                        },
                    ]
                except ImportError:
                    # Fallback to string format
                    safety_settings = [
                        {
                            "category": "HARM_CATEGORY_HATE_SPEECH",
                            "threshold": "BLOCK_NONE",
                        },
                        {
                            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            "threshold": "BLOCK_NONE",
                        },
                        {
                            "category": "HARM_CATEGORY_HARASSMENT",
                            "threshold": "BLOCK_NONE",
                        },
                        {
                            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                            "threshold": "BLOCK_NONE",
                        },
                    ]

                model_instance = self.client.GenerativeModel(model)
                response = model_instance.generate_content(
                    [extraction_prompt, genai.upload_file(image_path)],
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.4, top_p=0.0, top_k=1, max_output_tokens=3000
                    ),
                    safety_settings=safety_settings,
                )
                try:
                    extracted_info = response.text
                except ValueError:
                    # Try to get partial response
                    if hasattr(response, 'candidates') and response.candidates:
                        candidate = response.candidates[0]
                        if hasattr(candidate, 'content') and candidate.content:
                            try:
                                extracted_info = candidate.content.parts[0].text
                            except (AttributeError, IndexError, KeyError):
                                pass
                    
                    if 'extracted_info' not in locals() or not extracted_info:
                        safety_feedback = response.prompt_feedback.safety_ratings if hasattr(response, 'prompt_feedback') else None
                        block_reason = "Content blocked due to safety policies."
                        if safety_feedback:
                            block_reason += f" Feedback: {safety_feedback}"
                        QgsMessageLog.logMessage(
                            f"⚠️ Gemini API Blocked (Vision): {block_reason}",
                            "GeoAI",
                            Qgis.Warning,
                        )
                        return {"error": f"AI response blocked (Vision): {block_reason}"}
            elif provider == "ollama":
                extracted_info = self._ollama_query(
                    extraction_prompt, images=[image_data], model=model
                )
            else:
                return {
                    "error": f"Image analysis not supported for {provider}. Use Anthropic, OpenAI, or Google."
                }

            # Step 2: Convert extracted info to code using text model
            code_prompt = (
                f"Based on this QGIS Model Builder analysis, generate {conversion_type} code:\n\n"
                f"{extracted_info}\n\n"
                f"Generate clean, executable {conversion_type} code with comments."
            )

            code_result = self.generate_sql(code_prompt, {}, model_provider, model_name)

            return {
                "code": (
                    code_result.get("sql", "")
                    if conversion_type.lower() == "sql"
                    else extracted_info
                ),
                "type": conversion_type,
                "extracted_info": extracted_info,
            }

        except Exception as e:
            return {"error": str(e)}

    def generate_code_from_image_description(
        self,
        description: str,
        output_type: str = "sql",
        model_provider: str = "ollama",
        model_name: str = "phi3",
    ) -> Dict:
        """Generate code from Azure Computer Vision image description"""
        system_prompt = (
            "You are an expert in geospatial programming and QGIS Model Builder. "
            "Your task is to analyze the image description and generate working, executable code. "
            "Focus on the DETECTED TEXT and OBJECTS to understand what the image shows. "
            "Generate clean, well-commented code that implements the workflow or analysis described."
        )

        prompt = f"""Analyze this Azure Computer Vision image description and generate {output_type.upper()} code.

{description}

TASK: Generate {output_type.upper()} code based on the image analysis above.

REQUIREMENTS:
1. Use the DETECTED TEXT to understand what the image contains
2. Use DETECTED OBJECTS to understand the structure/diagram
3. Generate working, executable {output_type} code
4. Include clear comments explaining each step
5. If the image shows a QGIS Model Builder workflow, convert it to equivalent {output_type} code
6. If the image shows SQL queries or code, extract and format it properly
7. If the image shows a map or analysis, generate code to perform that analysis

OUTPUT FORMAT:
- Start with a comment explaining what the code does
- Then provide the {output_type} code
- Use proper syntax and formatting
- Include error handling if appropriate

Generate the code now:"""

        try:
            QgsMessageLog.logMessage(
                f"Calling LLM to generate {output_type} code (provider: {model_provider}, model: {model_name})",
                "GeoAI",
                Qgis.Info,
            )

            content = self._query_with_provider(
                prompt, system_prompt, model_provider, model_name
            )

            if not content or len(content.strip()) == 0:
                QgsMessageLog.logMessage(
                    "LLM returned empty response", "GeoAI", Qgis.Warning
                )
                return {
                    "error": "LLM returned empty response. Please try again or use a different model.",
                    "code": "",
                    "explanation": "",
                    "type": output_type,
                    "success": False,
                }

            QgsMessageLog.logMessage(
                f"LLM generated code successfully ({len(content)} characters)",
                "GeoAI",
                Qgis.Info,
            )

            return {
                "code": content,
                "explanation": content,
                "type": output_type,
                "success": True,
            }
        except Exception as e:
            import traceback

            error_trace = traceback.format_exc()
            QgsMessageLog.logMessage(
                f"Error generating code from description: {str(e)}\n{error_trace}",
                "GeoAI",
                Qgis.Critical,
            )
            return {
                "error": f"Code generation failed: {str(e)}",
                "code": "",
                "explanation": "",
                "type": output_type,
                "success": False,
            }

    def get_smart_suggestions(
        self,
        context: Dict,
        prompt: str = None,
        model_provider: str = None,
        model_name: str = None,
    ) -> List[str]:
        """Generate intelligent, layer-specific QGIS operations"""

        active_layer_name = context.get("active_layer", "Unknown")
        layers_info = context.get("layers", [])
        crs = context.get("crs", "Unknown")
        db_type = context.get("db_type", "Unknown")
        project_analysis = context.get("project_analysis", {})
        target_layer_info = context.get("target_layer_info")

        system_message_parts = [
            "You are an expert GIS analyst and QGIS user. Provide insightful and actionable suggestions.",
            f"Current Project CRS: {crs}",
            f"Database Type: {db_type}",
        ]

        if project_analysis:
            system_message_parts.append(
                f"Project Summary: Total Layers={project_analysis.get('total_layers')}, "
                f"Vector Layers={project_analysis.get('vector_layers')}, "
                f"Total Features={project_analysis.get('total_features')}"
            )

        if target_layer_info:
            layer_name = target_layer_info.get("name")
            fields = target_layer_info.get("fields", [])
            fields_formatted = ", ".join([f'"{f}"' for f in fields])
            geometry_type = target_layer_info.get("geometry_type", "Unknown")
            feature_count = target_layer_info.get("feature_count", 0)

            system_message_parts.append(f"Active Layer for Analysis: {layer_name}")
            system_message_parts.append(f"Geometry Type: {geometry_type}")
            system_message_parts.append(f"Feature Count: {feature_count}")
            system_message_parts.append(
                f"Available Fields (use exact casing with double quotes): {fields_formatted}"
            )

        elif active_layer_name and layers_info:
            active_info = None
            for layer in layers_info:
                if layer.get("name") == active_layer_name:
                    active_info = layer
                    break
            if active_info:
                fields = active_info.get("fields", [])
                fields_formatted = ", ".join([f'"{f}"' for f in fields])
                system_message_parts.append(f"Active Layer: {active_layer_name}")
                system_message_parts.append(
                    f"Available Fields (use exact casing with double quotes): {fields_formatted}"
                )

        system_prompt = (
            "\n".join(system_message_parts)
            + '\n\nIMPORTANT: Use column names exactly as provided and wrapped in double quotes (e.g., SELECT "Name" FROM table). Provide explanations and code blocks for SQL or Python where appropriate. Format output clearly with headings.'
        )

        if prompt is None:
            prompt = (
                "Given the current QGIS project context, suggest 5 intelligent and practical QGIS operations. "
                "Focus on general project improvements, common geospatial analyses, or data management tasks. "
                "For each suggestion, provide a short title, a brief explanation, and relevant SQL or Python code examples."
            )

        try:
            content = self._query_with_provider(
                prompt, system_prompt, model_provider, model_name
            )

            if not content:
                return ["AI did not return any suggestions."]

            if "suggest 5 intelligent and practical QGIS operations" in prompt.lower():
                suggestions = re.split(r"\n\n(?:\d+\.\s)?", content)
                suggestions = [s.strip() for s in suggestions if s.strip()][:5]
                return suggestions if suggestions else [content]
            else:
                return [content]

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error getting suggestions: {str(e)}", "GeoAI", Qgis.Critical
            )
            return [f"Error getting suggestions: {str(e)}"]

    def _build_sql_system_prompt(self, context: Dict) -> str:
        """Build system prompt with proper column formatting"""
        tables_info = []
        table_names_list = []
        table_formatting_info = []
        
        for table_name, fields in context.get("table_fields", {}).items():
            # Determine if table name needs quotes (mixed case or special chars)
            table_needs_quotes = table_name != table_name.lower() or not table_name.replace('_', '').isalnum()
            table_format = f'"{table_name}"' if table_needs_quotes else table_name
            table_names_list.append(table_format)
            
            # Format columns - only quote if mixed case
            fields_formatted = []
            for field in fields:
                if field != field.lower() or not field.replace('_', '').isalnum():
                    fields_formatted.append(f'"{field}"')
                else:
                    fields_formatted.append(field)
            
            fields_str = ", ".join(fields_formatted)
            tables_info.append(f"{table_format}: {fields_str}")
            table_formatting_info.append(f"  - {table_format} (columns: {fields_str})")

        # Check if we have any tables loaded
        has_tables = len(table_names_list) > 0

        if has_tables:
            tables_info_str = "\n".join(tables_info)
            available_tables = ", ".join(table_names_list)
            table_formatting_str = "\n".join(table_formatting_info)
            
            # Detect geometry column name (usually 'geom' not 'geometry')
            geom_column_examples = []
            for table_name_raw, fields in context.get("table_fields", {}).items():
                # Get formatted table name (with or without quotes)
                table_needs_quotes = table_name_raw != table_name_raw.lower() or not table_name_raw.replace('_', '').isalnum()
                table_name_formatted = f'"{table_name_raw}"' if table_needs_quotes else table_name_raw
                
                for field in fields:
                    if 'geom' in field.lower() and 'geometry' not in field.lower():
                        # Format field name (with or without quotes)
                        field_needs_quotes = field != field.lower() or not field.replace('_', '').isalnum()
                        field_formatted = f'"{field}"' if field_needs_quotes else field
                        geom_column_examples.append(f"  - {table_name_formatted}.{field_formatted}")
                        break
            
            geom_column_note = ""
            if geom_column_examples:
                geom_column_note = "\n=== GEOMETRY COLUMN ===\n"
                geom_column_note += "IMPORTANT: The geometry column is typically 'geom' NOT 'geometry'.\n"
                geom_column_note += "Examples from your database:\n"
                geom_column_note += "\n".join(geom_column_examples[:3]) + "\n"
                geom_column_note += "Always use 'geom' for geometry operations unless the column is explicitly named 'geometry'.\n\n"
            
            return (
                "You are an expert in geospatial SQL (PostGIS, SpatiaLite). Generate precise, EXECUTABLE SQL queries that will run successfully on the user's database.\n"
                f"Database Type: {context.get('db_type','PostgreSQL/PostGIS')}\n"
                f"CRS: {context.get('crs','EPSG:4326')}\n\n"
                "=== ⚠️ CRITICAL RULES - READ CAREFULLY ⚠️ ===\n"
                f"ONLY USE THESE DATABASE TABLES: {available_tables}\n"
                "DO NOT invent or guess table names.\n"
                "DO NOT use QGIS layer names (e.g., 'Example11/Buildings.shp') - these are NOT database table names.\n"
                "DO NOT use file paths or file extensions (e.g., '.shp', '/', '\\') in table names.\n"
                "ONLY use the exact database table names listed above (e.g., 'buildings', 'roads', 'landuse').\n"
                "If user asks about a table not in the list, respond: 'Table not found. Available tables are: [list them]'\n"
                "If user mentions a QGIS layer name that looks like a file path, map it to the actual database table name.\n"
                "Example: 'Example11/Buildings.shp' → 'buildings' (check AVAILABLE TABLES above)\n"
                "ALL queries MUST be executable - test your syntax mentally before generating.\n\n"
                "=== 🔴 STRICT COLUMN NAME RULES - MANDATORY 🔴 ===\n"
                "YOU MUST USE ONLY THE EXACT COLUMN NAMES LISTED BELOW.\n"
                "NEVER guess, assume, or invent column names.\n"
                "NEVER use column names that are NOT in the AVAILABLE TABLES list below.\n"
                "If a user requests a column that is NOT in the list:\n"
                "  1. First, check if a similar column exists (case-insensitive match)\n"
                "  2. If found, use the EXACT name from the list (with correct case and quotes)\n"
                "  3. If NOT found, generate a query to discover columns: SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'table_name';\n"
                "  4. Or inform the user: 'Column [name] not found. Available columns for [table] are: [list from AVAILABLE TABLES]'\n\n"
                "=== AVAILABLE TABLES AND COLUMNS (USE ONLY THESE) ===\n"
                f"{tables_info_str}\n\n"
                f"{geom_column_note}"
                "=== SQL FORMATTING RULES ===\n"
                "1. TABLE NAMES:\n"
                "   - Lowercase table names (e.g., 'buildings'): Use WITHOUT quotes: FROM buildings\n"
                "   - Mixed-case table names (e.g., 'Buildings'): Use WITH quotes: FROM \"Buildings\"\n"
                "   - Check the exact table name format in AVAILABLE TABLES above\n\n"
                "2. COLUMN NAMES (STRICT - SAVE AND REMEMBER - NO QUOTES FOR LOWERCASE):\n"
                "   - You MUST use ONLY the exact column names from AVAILABLE TABLES above\n"
                "   - SAVE and REMEMBER all column names from AVAILABLE TABLES for future queries\n"
                "   - CRITICAL: If column name in AVAILABLE TABLES is lowercase (e.g., 'id', 'geom', 'area', 'owner', 'type'):\n"
                "     * Use WITHOUT quotes: SELECT id, area, owner, type, geom\n"
                "     * NEVER use quotes for lowercase columns: WRONG: SELECT \"id\", \"area\" - CORRECT: SELECT id, area\n"
                "   - If column name in AVAILABLE TABLES is mixed-case (e.g., 'OWNER', 'TYPE'):\n"
                "     * Use WITH quotes: SELECT \"OWNER\", \"TYPE\"\n"
                "   - IMPORTANT: 99% of PostgreSQL columns are lowercase - ALWAYS use WITHOUT quotes\n"
                "   - If a column name is requested but NOT in AVAILABLE TABLES, DO NOT use it\n"
                "   - Instead, generate a discovery query or inform the user the column doesn't exist\n"
                "   - Example: If AVAILABLE TABLES shows 'area', 'owner', 'type' (lowercase), use: SELECT area, owner, type\n"
                "   - Example: NEVER write SELECT \"area\" - write SELECT area (lowercase = no quotes)\n"
                "   - Example: NEVER write SELECT \"id\" - write SELECT id (lowercase = no quotes)\n"
                "   - REMEMBER: Once you see column names in AVAILABLE TABLES, use them consistently in all future queries\n"
                "   - ALWAYS check AVAILABLE TABLES above before writing any column name\n\n"
                "3. GEOMETRY COLUMN:\n"
                "   - Use 'geom' NOT 'geometry' unless the column is explicitly named 'geometry' in AVAILABLE TABLES\n"
                "   - Check AVAILABLE TABLES to see the exact geometry column name\n"
                "   - If 'geom' is lowercase in AVAILABLE TABLES, use WITHOUT quotes: SELECT geom\n"
                "   - Example: SELECT geom FROM buildings (not SELECT geometry FROM buildings, not SELECT \"geom\")\n\n"
                "4. QUERY STRUCTURE:\n"
                "   - Put SQL in ```sql ... ``` block\n"
                "   - Use proper PostgreSQL/PostGIS syntax\n"
                "   - Include LIMIT clause for large result sets\n"
                "   - DO NOT add comments after semicolon (-- comments)\n"
                "   - DO NOT add explanations in the SQL code itself\n"
                "   - Generate ONLY the SQL query, nothing else\n"
                "   - Test that the query will execute successfully\n\n"
                "=== EXAMPLES ===\n"
                "CORRECT (using exact lowercase column names WITHOUT quotes - MOST COMMON - 99% OF CASES):\n"
                "```sql\n"
                "SELECT id, area, owner, type, geom\n"
                "FROM buildings\n"
                "WHERE area > 1000\n"
                "LIMIT 10;\n"
                "```\n"
                "(This is correct if 'area', 'owner', 'type', 'geom' are lowercase in AVAILABLE TABLES for 'buildings')\n"
                "NOTE: All lowercase columns = NO QUOTES. This is the standard PostgreSQL format.\n\n"
                "WRONG (using quotes for lowercase columns - DO NOT DO THIS):\n"
                "```sql\n"
                "SELECT \"id\", \"area\", \"owner\", \"type\", geom\n"
                "FROM \"buildings\"\n"
                "WHERE \"area\" > 1000;\n"
                "```\n"
                "This is WRONG because lowercase columns and table names should NOT have quotes.\n\n"
                "CORRECT (simple query - what user wants):\n"
                "```sql\n"
                "SELECT id, address, area, owner\n"
                "FROM buildings;\n"
                "```\n"
                "Simple, clean, no quotes, no comments, just the SQL.\n\n"
                "CORRECT (using exact mixed-case column names from AVAILABLE TABLES - LESS COMMON):\n"
                "```sql\n"
                "SELECT id, \"OWNER\", \"TYPE\", \"AREA\", geom\n"
                "FROM buildings\n"
                "WHERE \"AREA\" > 1000\n"
                "LIMIT 10;\n"
                "```\n"
                "(This is correct ONLY if 'OWNER', 'TYPE', 'AREA' are mixed-case in AVAILABLE TABLES for 'buildings')\n\n"
                "CORRECT (all lowercase columns from AVAILABLE TABLES):\n"
                "```sql\n"
                "SELECT id, name, geom\n"
                "FROM cities\n"
                "WHERE population > 10000;\n"
                "```\n"
                "(This is correct ONLY if 'name', 'population' are in AVAILABLE TABLES for 'cities')\n\n"
                "INCORRECT (using column NOT in AVAILABLE TABLES or wrong format):\n"
                "```sql\n"
                "SELECT \"id\", \"area\" FROM buildings;  -- WRONG: lowercase columns should NOT have quotes\n"
                "SELECT id, \"OWNER\" FROM buildings;  -- WRONG if 'OWNER' is not in AVAILABLE TABLES (check if it's 'owner' lowercase)\n"
                "SELECT geometry FROM buildings;  -- WRONG: should be 'geom' (check AVAILABLE TABLES)\n"
                "SELECT id, area, geom FROM \"buildings\";  -- WRONG: lowercase table should NOT have quotes\n"
                "```\n\n"
                "CORRECT (when column not found, generate discovery query):\n"
                "```sql\n"
                "SELECT column_name, data_type\n"
                "FROM information_schema.columns\n"
                "WHERE table_schema = 'public' AND table_name = 'buildings'\n"
                "ORDER BY ordinal_position;\n"
                "```\n\n"
                "=== FINAL CHECK - MANDATORY BEFORE GENERATING SQL ===\n"
                "Before generating ANY SQL query, you MUST:\n"
                "1. ✅ Look at AVAILABLE TABLES above and find the exact table name (usually lowercase like 'buildings')\n"
                "2. ✅ Verify table name matches EXACTLY (case-sensitive) from AVAILABLE TABLES\n"
                "3. ✅ NEVER use QGIS layer names (e.g., 'Example11/Buildings.shp', 'Example11_Buildings') - use database table names only\n"
                "4. ✅ If user mentions a layer name, map it to the actual database table from AVAILABLE TABLES\n"
                "5. ✅ Look at AVAILABLE TABLES above and find the exact column names for that table\n"
                "6. ✅ Verify EVERY column name matches EXACTLY (case-sensitive) from AVAILABLE TABLES\n"
                "7. ✅ If column is lowercase in AVAILABLE TABLES, use WITHOUT quotes (e.g., area NOT \"area\")\n"
                "8. ✅ If column is mixed-case in AVAILABLE TABLES, use WITH quotes (e.g., \"OWNER\")\n"
                "9. ✅ Check geometry column name from AVAILABLE TABLES (usually 'geom' lowercase, no quotes)\n"
                "10. ✅ If a requested column is NOT in AVAILABLE TABLES, generate discovery query OR inform user\n"
                "11. ✅ Verify query syntax is valid PostgreSQL/PostGIS\n"
                "12. ✅ Ensure query will execute successfully without errors\n\n"
                "=== REMEMBER AND SAVE ===\n"
                "1. SAVE all column names from AVAILABLE TABLES - remember them for all future queries\n"
                "2. Use the EXACT column names from AVAILABLE TABLES (case-sensitive)\n"
                "3. CRITICAL RULE: Lowercase columns = NO QUOTES, Mixed-case columns = WITH QUOTES\n"
                "4. If you use a column name that is NOT in AVAILABLE TABLES, the query WILL FAIL\n"
                "5. If you use quotes for lowercase columns (e.g., \"area\"), the query WILL FAIL\n"
                "6. If you use a QGIS layer name instead of a database table name, the query WILL FAIL\n"
                "7. Always check AVAILABLE TABLES first. When in doubt, generate a discovery query\n"
                "8. Database table names are simple identifiers (e.g., 'buildings'), NOT file paths (e.g., 'Example11/Buildings.shp')\n"
                "9. Most PostgreSQL columns are lowercase - ALWAYS use them WITHOUT quotes (e.g., area, owner, type, geom)\n"
                "10. Once you see column names in AVAILABLE TABLES, use them consistently - SAVE them in your memory\n"
                "11. Before writing any SQL, STOP and check AVAILABLE TABLES above for exact column names\n\n"
            )
        else:
            # No tables loaded - always return the discovery query
            return (
                "You are an expert in geospatial SQL (PostGIS, SpatiaLite).\n"
                f"Database Type: {context.get('db_type','PostgreSQL/PostGIS')}\n\n"
                "=== NO TABLES DETECTED ===\n"
                "There are no tables loaded in QGIS. Before answering ANY query, you MUST first provide the SQL to discover available tables.\n\n"
                "ALWAYS respond with this SQL first:\n"
                "```sql\n"
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;\n"
                "```\n\n"
                "After running this query, the user will know what tables exist and can ask more specific questions.\n"
                "Do NOT invent or guess table names. Always provide the discovery query above first.\n"
            )

    def _parse_sql_response(self, content: str) -> Dict:
        """Parse SQL from LLM response and clean it"""
        QgsMessageLog.logMessage(
            f"Raw LLM content for SQL parsing: {content}", "GeoAI", Qgis.Info
        )

        sql = ""
        explanation = content

        # Try multiple markdown code block patterns
        patterns = [
            r"```sql\s*\n(.*?)\n```",  # Standard ```sql\n...\n```
            r"```sql\n(.*?)\n```",     # Without space
            r"```sql(.*?)```",          # Without newlines
            r"```\s*sql\s*\n(.*?)\n```",  # With spaces
        ]
        
        for pattern in patterns:
            sql_match = re.search(pattern, content, re.DOTALL)
            if sql_match:
                sql = sql_match.group(1).strip()
                pre_sql_content = content[: sql_match.start()].strip()
                post_sql_content = content[sql_match.end() :].strip()

                if pre_sql_content and post_sql_content:
                    explanation = f"{pre_sql_content}\n\n{post_sql_content}"
                elif pre_sql_content:
                    explanation = pre_sql_content
                elif post_sql_content:
                    explanation = post_sql_content
                else:
                    explanation = ""
                break

        # If no SQL block found, try Python block
        if not sql:
            python_match = re.search(r"```python\s*\n(.*?)\n```", content, re.DOTALL)
            if python_match:
                sql = python_match.group(1).strip()
                explanation = content
            else:
                # Try to find SQL statements without code blocks
                lines = content.split("\n")
                sql_candidates = []
                for line in lines:
                    stripped = line.strip()
                    # Skip lines with curly braces (likely formatting artifacts)
                    if "{" in stripped or "}" in stripped:
                        continue
                    if stripped.upper().startswith(
                        (
                            "SELECT",
                            "INSERT",
                            "UPDATE",
                            "DELETE",
                            "CREATE",
                            "ALTER",
                            "DROP",
                            "WITH",  # CTE
                        )
                    ):
                        sql_candidates.append(line)

                if sql_candidates:
                    sql = "\n".join(sql_candidates)
                    remaining_lines = [
                        line for line in lines if line not in sql_candidates
                    ]
                    explanation = "\n".join(remaining_lines).strip()

        # Clean SQL: Remove any stray curly braces, unnecessary quotes, and comments
        if sql:
            sql_lines = sql.split("\n")
            cleaned_lines = []
            for line in sql_lines:
                stripped = line.strip()
                # Skip lines that are only curly braces or formatting artifacts
                if stripped in ["{", "}", "{}", "{ }"]:
                    continue
                # Skip lines that are clearly markdown formatting
                if stripped.startswith("{") and stripped.endswith("}") and len(stripped) < 10:
                    # Very short lines with just braces are likely formatting
                    if "SELECT" not in stripped.upper() and "FROM" not in stripped.upper() and "JSON" not in stripped.upper():
                        continue
                # Remove SQL comments (-- ...)
                if "--" in line:
                    # Keep the SQL part, remove comment
                    comment_pos = line.find("--")
                    line = line[:comment_pos].rstrip()
                cleaned_lines.append(line)
            
            sql = "\n".join(cleaned_lines).strip()
            
            # Post-process: Remove unnecessary quotes from lowercase identifiers
            # This fixes cases where LLM adds quotes to lowercase column/table names
            # Pattern: "lowercase_identifier" -> lowercase_identifier (only for simple lowercase identifiers)
            # But preserve quotes for mixed-case or special characters
            def remove_unnecessary_quotes(match):
                quoted = match.group(1)
                # If it's a simple lowercase identifier, remove quotes
                if quoted.islower() and quoted.replace('_', '').isalnum():
                    return quoted
                # Otherwise keep quotes (mixed-case or special chars)
                return f'"{quoted}"'
            
            # Remove quotes from lowercase table names: "buildings" -> buildings
            sql = re.sub(r'"([a-z_][a-z0-9_]*)"', remove_unnecessary_quotes, sql)
            
            # Remove quotes from lowercase column names in SELECT, WHERE, etc.
            # But be careful not to break string literals
            # Pattern: Match quoted identifiers that are lowercase
            # This is a simplified approach - a full SQL parser would be better
            sql = re.sub(r'\b"([a-z_][a-z0-9_]*)"\b', r'\1', sql)
            
            # Fix common syntax errors
            # Fix: 1nerous -> 1000 (common LLM typo)
            sql = re.sub(r'\b(\d+)nerous\b', r'\1000', sql, flags=re.IGNORECASE)
            # Fix: area > 1 -> area > 1000 (if it's clearly a typo)
            sql = re.sub(r'\barea\s*>\s*1\s*;', 'area > 1000;', sql, flags=re.IGNORECASE)
            
            QgsMessageLog.logMessage(
                f"Cleaned SQL: {sql[:200]}...", "GeoAI", Qgis.Info
            )
            
            # Remove standalone curly braces on their own lines (formatting artifacts)
            # But preserve braces that are part of JSON functions or valid SQL
            sql = re.sub(r'^\s*\{\s*$', '', sql, flags=re.MULTILINE)  # Remove lines with only {
            sql = re.sub(r'^\s*\}\s*$', '', sql, flags=re.MULTILINE)  # Remove lines with only }
            sql = re.sub(r'\n\s*\n', '\n', sql)  # Remove empty lines
            sql = sql.strip()

        if not explanation.strip() and content.strip():
            explanation = content.strip()

        QgsMessageLog.logMessage(f"Parsed SQL: {sql[:200]}...", "GeoAI", Qgis.Info)
        QgsMessageLog.logMessage(
            f"Parsed Explanation: {explanation[:200]}...", "GeoAI", Qgis.Info
        )

        return {
            "sql": sql,
            "explanation": explanation,
            "success": bool(sql.strip() or explanation.strip()),
        }
