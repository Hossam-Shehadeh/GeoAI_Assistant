# GeoAI Assistant Pro - Complete Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Installation & Setup](#installation--setup)
3. [Configuration](#configuration)
4. [Features & Modules](#features--modules)
5. [User Interface](#user-interface)
6. [Usage Examples](#usage-examples)
7. [API Reference](#api-reference)
8. [Architecture](#architecture)
9. [Troubleshooting](#troubleshooting)
10. [Advanced Topics](#advanced-topics)

---

## Introduction

### What is GeoAI Assistant Pro?

GeoAI Assistant Pro is an enterprise-grade QGIS plugin that integrates artificial intelligence capabilities to enhance geospatial workflows. It provides intelligent SQL generation, automatic error fixing, image-to-code conversion, and advanced analysis tools.

### Key Benefits

- **Time Savings**: Generate SQL queries in seconds instead of minutes
- **Error Reduction**: Automatic error detection and fixing
- **Accessibility**: Natural language interface for complex operations
- **Efficiency**: Batch processing and template management
- **Intelligence**: AI-powered suggestions and recommendations

### System Requirements

- **QGIS**: Version 3.0 or higher
- **Python**: 3.9+ (included with QGIS)
- **Operating System**: Windows, macOS, or Linux
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: 100MB free space
- **Internet**: Required for cloud-based LLM providers (optional for Ollama)

---

## Installation & Setup

### Step-by-Step Installation

#### 1. Download Plugin

**Option A: Manual Installation**
1. Download the plugin folder
2. Extract to QGIS plugins directory:
   ```
   macOS: ~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/
   Windows: C:\Users\YourName\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\
   Linux: ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
   ```

**Option B: Git Clone**
```bash
cd ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins/
git clone <repository-url> GeoAI_Assistant_Pro
```

#### 2. Enable Plugin

1. Open QGIS
2. Go to `Plugins → Manage and Install Plugins`
3. Search for "GeoAI Assistant Pro"
4. Check the box to enable
5. Click "Close"

#### 3. Install Dependencies

**Azure Computer Vision SDK** (for Model Converter):
```bash
# Find QGIS Python path
# In QGIS: Plugins → Python Console
# Run: import sys; print(sys.executable)

# Install Azure SDK
/path/to/qgis/python3 -m pip install azure-cognitiveservices-vision-computervision msrest
```

**LLM Provider Libraries** (as needed):
```bash
# OpenAI
pip install openai

# Anthropic
pip install anthropic

# Google
pip install google-generativeai

# Ollama (download from https://ollama.ai)
```

#### 4. Restart QGIS

Close and reopen QGIS to ensure all modules load correctly.

### Verification

1. Check toolbar for GeoAI Assistant Pro icon
2. Open plugin (click icon or menu)
3. Verify all 10 tabs are visible
4. Check Log Messages for initialization messages

---

## Configuration

### Azure Computer Vision Setup

**Required for**: Model Converter (image analysis)

**Steps**:
1. Create Azure account: https://azure.microsoft.com/free/
2. Create Computer Vision resource in Azure Portal
3. Get Endpoint URL and Subscription Key
4. Configure in plugin Settings tab

**Detailed Guide**: See [AZURE_SETUP.md](AZURE_SETUP.md)

### LLM Provider Configuration

#### OpenAI

1. Get API key from https://platform.openai.com/api-keys
2. Add to `.env`:
   ```env
   OPENAI_API_KEY=sk-your-key-here
   ```
3. Select OpenAI in model selector

#### Anthropic (Claude)

1. Get API key from https://console.anthropic.com/
2. Add to `.env`:
   ```env
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```
3. Select Anthropic in model selector

#### Google Gemini

1. Get API key from https://makersuite.google.com/app/apikey
2. Add to `.env`:
   ```env
   GOOGLE_API_KEY=your-google-key-here
   ```
3. Install SDK: `pip install google-generativeai`

#### Ollama (Local)

1. Install Ollama: https://ollama.ai
2. Start Ollama: `ollama serve`
3. Pull models: `ollama pull phi3`
4. No API key needed
5. Select Ollama in model selector

#### OpenRouter

1. Get API key from https://openrouter.ai/keys
2. Add to `.env`:
   ```env
   OPENROUTER_API_KEY=your-key-here
   ```
3. Select OpenRouter in model selector

### Environment File (.env)

Create `.env` file in plugin directory:

```env
# Azure Computer Vision
AZURE_VISION_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com/
AZURE_VISION_SUBSCRIPTION_KEY=your-subscription-key

# LLM Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
OPENROUTER_API_KEY=...
HUGGINGFACE_API_KEY=...

# Ollama (if custom URL)
OLLAMA_BASE_URL=http://localhost:11434
```

---

## Features & Modules

### Module 1: LLM Handler

**Purpose**: Unified interface for multiple LLM providers

**Supported Providers**:
- OpenAI (GPT-4, GPT-4o, GPT-3.5-turbo)
- Anthropic (Claude 3.5 Sonnet, Claude 3 Opus)
- Google (Gemini Pro, Gemini 2.5 Flash)
- Ollama (Local models: phi3, mistral, llama, etc.)
- OpenRouter (100+ models)
- HuggingFace (Open-source models)

**Key Methods**:
- `generate_sql(prompt, context, provider, model)` - Generate SQL from natural language
- `generate_code_from_image_description(description, output_type, provider, model)` - Generate code from Azure description
- `analyze_image_to_code(image_path, conversion_type, provider, model)` - Direct image analysis
- `fix_sql_error(sql, error_msg, context, provider, model)` - Fix SQL errors

**Usage Example**:
```python
from modules.llm_handler import LLMHandler

llm = LLMHandler()
result = llm.generate_sql(
    "Find buildings near parks",
    {"layers": ["buildings", "parks"]},
    "ollama",
    "phi3"
)
```

### Module 2: SQL Executor

**Purpose**: Execute SQL queries on various data sources

**Supported Databases**:
- PostgreSQL/PostGIS
- SpatiaLite
- GeoPackage
- Shapefile (attribute queries)

**Key Methods**:
- `execute_sql(sql, layer_name)` - Execute SQL query
- `get_context()` - Get current QGIS context (layers, CRS, etc.)

**Features**:
- Automatic layer detection
- Spatial operation support
- Result table generation
- Error handling

### Module 3: Image Processor

**Purpose**: Analyze images and convert to code

**Analysis Methods**:
1. **Azure Computer Vision** (preferred):
   - OCR text extraction
   - Object detection
   - Shape recognition
   - Color analysis
   - Category classification

2. **LLM Direct Processing** (fallback):
   - Direct image analysis by vision-capable LLMs
   - Works without Azure
   - Supports OpenAI GPT-4o, Claude, Google Gemini

**Key Methods**:
- `process_model_image(image_path, output_type, model_provider, model_name)` - Main processing method
- `analyze_image_with_azure(image_path)` - Azure analysis
- `_generate_full_description(analysis, text_result)` - Generate description

**Workflow**:
1. Check Azure availability
2. If available, use Azure for analysis
3. If not, fallback to LLM direct processing
4. Generate code from analysis
5. Return structured result

### Module 4: Error Fixer

**Purpose**: Automatically detect and fix SQL errors

**Error Types Supported**:
- Syntax errors (typos, missing keywords)
- Type mismatches
- Invalid table/column names
- Logical errors
- Missing clauses

**Key Methods**:
- `fix_sql_error(sql, error_msg, context, provider, model)` - Fix SQL error

**Process**:
1. Detect error from SQL execution
2. Analyze error message
3. Use LLM to generate fix
4. Provide explanation
5. Return fixed SQL

### Module 5: Smart Assistant

**Purpose**: Provide intelligent suggestions for QGIS workflows

**Analysis Types**:
- **Project Overview**: Analyze entire QGIS project
- **Selected Layer**: Analyze currently selected layer
- **All Layers**: Analyze all loaded layers
- **Custom Query**: Answer specific questions

**Key Methods**:
- `get_suggestions(analysis_type, context, provider, model)` - Get suggestions

**Output**:
- Actionable recommendations
- Relevant QGIS operations
- Best practices
- Optimization tips

### Module 6: Query Validator

**Purpose**: Validate SQL before execution

**Validation Checks**:
- Syntax correctness
- Table/column existence
- Type compatibility
- Performance warnings

---

## User Interface

### Main Window Layout

```
┌─────────────────────────────────────────────────────────┐
│  Sidebar          │  Top Bar (Model Selector)            │
│  Navigation       │  Quick Actions                       │
│                   │                                       │
│  - SQL Generator  │  ┌─────────────────────────────────┐ │
│  - Model Converter│  │  Tab Content Area                │ │
│  - Smart Assistant│  │                                 │ │
│  - Error Fixer    │  │  [Component UI]                 │ │
│  - Data Analysis  │  │                                 │ │
│  - History        │  │                                 │ │
│  - Batch Process  │  │                                 │ │
│  - Templates      │  │                                 │ │
│  - Analytics      │  │                                 │ │
│  - Settings       │  │                                 │ │
│                   │  └─────────────────────────────────┘ │
│  Quick Stats      │                                       │
└─────────────────────────────────────────────────────────┘
```

### Component Details

#### SQL Generator Component

**Layout**:
- Input text area (natural language)
- Quick templates dropdown
- Generate button
- SQL output area (read-only)
- Action buttons (Execute, Auto-Fix, Copy)
- Results table

**Features**:
- Context-aware generation
- Template selection
- SQL cleaning before execution
- Result visualization

#### Model Converter Component

**Layout**:
- File browser
- Image preview area
- Conversion type selector
- Convert button
- Code output area
- Action buttons (Copy, Save)

**Features**:
- Image preview with zoom
- Azure/LLM method indicator
- Analysis description display
- Code formatting

#### Settings Panel Component

**Layout**:
- Azure credentials section
- LLM API keys section
- Save buttons
- Status indicators

**Features**:
- Secure password fields
- Auto-load from .env
- Validation
- Success/error messages

---

## Usage Examples

### Example 1: Basic SQL Generation

**Scenario**: Find all buildings within 500 meters of parks

**Steps**:
1. Open SQL Generator tab
2. Type: `Find all buildings within 500 meters of parks`
3. Select model: Ollama/phi3
4. Click "Generate SQL"
5. Review generated SQL
6. Click "Execute"
7. View results in table

**Expected SQL**:
```sql
SELECT b.*
FROM buildings b
WHERE EXISTS (
    SELECT 1
    FROM parks p
    WHERE ST_DWithin(b.geometry, p.geometry, 500)
);
```

### Example 2: Image to Code Conversion

**Scenario**: Convert QGIS Model Builder workflow to SQL

**Steps**:
1. Take screenshot of Model Builder
2. Open Model Converter tab
3. Browse and select image
4. Select "SQL" as output type
5. Click "Convert to Code"
6. Wait for processing (30-60 seconds)
7. Review generated code
8. Copy or save code

**Expected Output**:
- Azure analysis description
- Generated SQL code
- Comments explaining the code

### Example 3: Error Fixing

**Scenario**: Fix SQL syntax error

**Input SQL** (with error):
```sql
SELECT * FORM mytable WHERE id = 1
```

**Steps**:
1. Open Error Fixer tab
2. Paste SQL with error
3. Click "Fix Error"
4. Review fixed SQL and explanation
5. Execute fixed SQL

**Fixed SQL**:
```sql
SELECT * FROM mytable WHERE id = 1
```

**Explanation**: Changed "FORM" to "FROM" (typo correction)

### Example 4: Batch Processing

**Scenario**: Process multiple similar queries

**Steps**:
1. Open Batch Processor tab
2. Add multiple queries:
   - `Find buildings near parks`
   - `Find buildings near schools`
   - `Find buildings near hospitals`
3. Click "Process All"
4. Monitor progress
5. Review results for each query

### Example 5: Template Usage

**Scenario**: Create reusable query template

**Steps**:
1. Open Template Manager tab
2. Create new template:
   - Name: "Find features near"
   - Query: `SELECT * FROM {table} WHERE ST_DWithin(geometry, (SELECT geometry FROM {target_table} WHERE name = '{target_name}'), {distance})`
3. Save template
4. Use template with different values:
   - table: buildings
   - target_table: parks
   - target_name: Central Park
   - distance: 500

---

## API Reference

### LLMHandler Class

#### Methods

**`generate_sql(prompt, context, provider, model)`**
- **Parameters**:
  - `prompt` (str): Natural language query description
  - `context` (dict): QGIS context (layers, CRS, etc.)
  - `provider` (str): LLM provider name
  - `model` (str): Model name
- **Returns**: `dict` with `sql` key or `error` key

**`generate_code_from_image_description(description, output_type, provider, model)`**
- **Parameters**:
  - `description` (str): Azure Computer Vision description
  - `output_type` (str): 'sql' or 'python'
  - `provider` (str): LLM provider
  - `model` (str): Model name
- **Returns**: `dict` with `code` key

**`analyze_image_to_code(image_path, conversion_type, provider, model)`**
- **Parameters**:
  - `image_path` (str): Path to image file
  - `conversion_type` (str): 'sql' or 'python'
  - `provider` (str): LLM provider (must support vision)
  - `model` (str): Vision-capable model name
- **Returns**: `dict` with `code` and `extracted_info` keys

### SQLExecutor Class

#### Methods

**`execute_sql(sql, layer_name)`**
- **Parameters**:
  - `sql` (str): SQL query to execute
  - `layer_name` (str, optional): Specific layer name
- **Returns**: `dict` with `rows` (list) or `error` (str)

**`get_context()`**
- **Returns**: `dict` with QGIS context information

### ImageProcessor Class

#### Methods

**`process_model_image(image_path, output_type, model_provider, model_name)`**
- **Parameters**:
  - `image_path` (str): Path to image
  - `output_type` (str): 'sql' or 'python'
  - `model_provider` (str): LLM provider
  - `model_name` (str): Model name
- **Returns**: `dict` with structured code output

**`analyze_image_with_azure(image_path)`**
- **Parameters**:
  - `image_path` (str): Path to image
- **Returns**: `dict` with `description` and analysis data

**`reload_azure_client()`**
- Reloads Azure client after credential update
- **Returns**: `bool` (success status)

### ErrorFixer Class

#### Methods

**`fix_sql_error(sql, error_msg, context, provider, model)`**
- **Parameters**:
  - `sql` (str): SQL with error
  - `error_msg` (str): Error message from execution
  - `context` (dict): QGIS context
  - `provider` (str): LLM provider
  - `model` (str): Model name
- **Returns**: `dict` with `sql` (fixed) and `explanation`

---

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface Layer                  │
│  (Main Window, Components, Themes)                      │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                   Service Layer                          │
│  (Query Service, History Service, Cache Service)        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                   Module Layer                           │
│  (LLM Handler, SQL Executor, Image Processor, etc.)     │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Infrastructure Layer                        │
│  (Config Manager, Logger)                                │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

**SQL Generation Flow**:
```
User Input → Query Editor → LLM Handler → Provider API → Response → 
SQL Executor → Database → Results → Query Editor → Display
```

**Image Conversion Flow**:
```
Image Upload → Model Converter → Image Processor → 
[Azure Analysis OR LLM Direct] → LLM Handler → 
Code Generation → Model Converter → Display
```

### Design Patterns

1. **Service-Oriented Architecture**: Business logic separated into services
2. **Provider Pattern**: Pluggable LLM providers
3. **Factory Pattern**: Dynamic module initialization
4. **Observer Pattern**: Event-driven UI updates
5. **Strategy Pattern**: Different analysis strategies (Azure vs LLM)

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: Plugin Won't Load

**Symptoms**: Error when enabling plugin

**Diagnosis**:
1. Check Log Messages for specific error
2. Verify Python syntax is correct
3. Check all imports are available

**Solutions**:
- Fix syntax errors
- Install missing dependencies
- Clear `__pycache__` folders
- Restart QGIS

#### Issue: Azure Not Working

**Symptoms**: Model Converter fails with Azure errors

**Diagnosis**:
1. Check Azure credentials in Settings
2. Verify `.env` file exists
3. Test Azure endpoint accessibility

**Solutions**:
- Re-enter Azure credentials
- Check endpoint URL format
- Verify subscription key is valid
- Plugin will auto-fallback to LLM

#### Issue: SQL Generation Fails

**Symptoms**: No SQL generated or timeout errors

**Diagnosis**:
1. Check LLM provider configuration
2. Verify API keys
3. Check internet connection
4. Review Log Messages

**Solutions**:
- Configure LLM provider correctly
- Check API key validity
- Try different model
- Use local Ollama if internet issues

#### Issue: Code Not Displaying

**Symptoms**: Conversion completes but no code shown

**Diagnosis**:
1. Check Log Messages for code extraction
2. Verify result structure
3. Check output box visibility

**Solutions**:
- Check Log Messages for details
- Verify code was generated
- Try different image
- Check raw_response field

### Debug Mode

Enable detailed logging:
1. Open QGIS Log Messages panel
2. Filter by "GeoAI Pro" or "GeoAI"
3. Set log level to "All"
4. Review all messages during operation

### Performance Optimization

**Tips**:
- Use local Ollama for faster responses
- Cache frequently used queries
- Batch process multiple queries
- Use templates for repeated operations
- Optimize Azure usage (avoid rate limits)

---

## Advanced Topics

### Custom LLM Provider

To add a custom LLM provider:

1. Create provider class in `core/llm/providers/`
2. Inherit from `BaseProvider`
3. Implement required methods
4. Register in `LLMHandler`

### Extending Functionality

**Adding New Components**:
1. Create component in `ui/components/`
2. Inherit from `QWidget`
3. Add to `MainWindow` tabs
4. Register in sidebar navigation

**Adding New Services**:
1. Create service in `services/`
2. Implement business logic
3. Register in service layer
4. Use in components

### Integration with Other Plugins

The plugin can be integrated with other QGIS plugins:
- Access via `iface` object
- Use QGIS API for layer operations
- Share data through QGIS project

### Performance Tuning

**Optimization Strategies**:
- Use connection pooling for databases
- Implement query caching
- Batch API requests
- Use async operations where possible
- Optimize image processing

---

## Best Practices

### SQL Generation

1. **Be Specific**: Provide clear, detailed descriptions
2. **Include Context**: Mention layer names and relationships
3. **Specify Operations**: Clearly state spatial operations needed
4. **Review Before Execute**: Always review generated SQL
5. **Use Templates**: Create templates for common queries

### Image Conversion

1. **Clear Images**: Use high-quality screenshots
2. **Complete Workflows**: Include entire Model Builder diagram
3. **Good Lighting**: Ensure text is readable
4. **Proper Format**: Use PNG or JPG format
5. **Test Results**: Verify generated code works

### Error Handling

1. **Check Logs**: Always check Log Messages for errors
2. **Verify Input**: Ensure SQL/input is valid before processing
3. **Use Auto-Fix**: Let Error Fixer handle common errors
4. **Review Fixes**: Always review auto-fixed code
5. **Report Issues**: Report persistent errors

### Security

1. **Protect API Keys**: Never share `.env` files
2. **Use Environment Variables**: Store secrets in `.env`
3. **Rotate Keys**: Regularly update API keys
4. **Monitor Usage**: Check API usage regularly
5. **Limit Access**: Restrict plugin access if needed

---

## Appendix

### A. Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `AZURE_VISION_ENDPOINT` | Azure Computer Vision endpoint URL | For Model Converter |
| `AZURE_VISION_SUBSCRIPTION_KEY` | Azure subscription key | For Model Converter |
| `OPENAI_API_KEY` | OpenAI API key | For OpenAI provider |
| `ANTHROPIC_API_KEY` | Anthropic API key | For Claude provider |
| `GOOGLE_API_KEY` | Google API key | For Gemini provider |
| `OPENROUTER_API_KEY` | OpenRouter API key | For OpenRouter provider |
| `HUGGINGFACE_API_KEY` | HuggingFace API key | For HuggingFace provider |
| `OLLAMA_BASE_URL` | Ollama server URL | For Ollama (default: http://localhost:11434) |

### B. Supported File Formats

**Images**:
- PNG (.png)
- JPEG (.jpg, .jpeg)
- BMP (.bmp)
- TIFF (.tif, .tiff)

**Code Output**:
- SQL (.sql)
- Python (.py)
- Text (.txt)

### C. Model Recommendations

**For SQL Generation**:
- **Best Quality**: GPT-4o, Claude 3.5 Sonnet
- **Good Balance**: GPT-3.5-turbo, Gemini Pro
- **Local/Fast**: Ollama phi3, mistral

**For Image Analysis**:
- **Best Quality**: Azure Computer Vision + GPT-4o
- **Good Quality**: Claude 3.5 Sonnet (direct)
- **Fast**: Gemini 2.5 Flash (direct)

**For Error Fixing**:
- **Best**: GPT-4o, Claude 3.5 Sonnet
- **Good**: GPT-3.5-turbo
- **Local**: Ollama mistral

### D. Error Codes Reference

| Error Code | Description | Solution |
|------------|-------------|----------|
| `AZURE_NOT_CONFIGURED` | Azure credentials missing | Configure in Settings |
| `AZURE_RATE_LIMIT` | Azure API rate limit exceeded | Wait 10 seconds, retry |
| `LLM_CONNECTION_ERROR` | Cannot connect to LLM provider | Check internet, API key |
| `LLM_TIMEOUT` | LLM request timed out | Try different model, increase timeout |
| `SQL_SYNTAX_ERROR` | SQL syntax is invalid | Use Error Fixer |
| `SQL_EXECUTION_ERROR` | SQL execution failed | Check database connection, SQL validity |
| `IMAGE_PROCESSING_ERROR` | Image processing failed | Check image format, try different image |

---

## Changelog

### Version 2.0.0
- ✅ Complete feature integration
- ✅ Azure Computer Vision support
- ✅ LLM fallback mechanism
- ✅ Enhanced UI with themes
- ✅ Query history and analytics
- ✅ Batch processing
- ✅ Template management

### Version 1.0.0
- Initial release
- Basic SQL generation
- Error fixing
- Smart assistant

---

## Support & Resources

### Documentation
- [README.md](README.md) - Overview and quick start
- [AZURE_SETUP.md](AZURE_SETUP.md) - Azure configuration
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing procedures

### Getting Help
1. Check Log Messages in QGIS
2. Review documentation files
3. Check error messages (they include solutions)
4. Verify configuration

### Contributing
See contributing guidelines in repository.

---

**Last Updated**: December 2024
**Version**: 2.0.0

