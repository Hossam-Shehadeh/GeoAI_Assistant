<div align="center">

# 🤖 GeoAI Assistant Pro

### **Enterprise-Grade AI-Powered Geospatial Assistant for QGIS**

[![QGIS](https://img.shields.io/badge/QGIS-3.0+-green.svg)](https://qgis.org/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.0.0-orange.svg)](metadata.txt)

**Transform your QGIS workflow with AI-powered SQL generation, automatic error fixing, and intelligent geospatial analysis.**

[Features](#-key-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Workflow](#-workflow) • [Documentation](#-documentation) • [Contributing](#-contributing)

---

![GeoAI Assistant Pro Banner](media/demo-screenshot-1.jpeg)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Workflow](#-workflow)
- [Architecture](#-architecture)
- [Configuration](#-configuration)
- [Usage Examples](#-usage-examples)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**GeoAI Assistant Pro** is a cutting-edge QGIS plugin that brings the power of Large Language Models (LLMs) directly into your geospatial workflow. Whether you're generating complex SQL queries, converting model builder workflows to code, or analyzing spatial data, this plugin makes it effortless.

### Why GeoAI Assistant Pro?

- ⚡ **10x Faster**: Generate SQL queries in seconds instead of minutes
- 🎯 **Error-Free**: Automatic error detection and fixing
- 🧠 **Intelligent**: AI-powered suggestions and recommendations
- 🔄 **Multi-Provider**: Support for OpenAI, Anthropic, Google, Ollama, and more
- 🎨 **User-Friendly**: Natural language interface for complex operations
- 📊 **Enterprise-Ready**: Batch processing, templates, and analytics

---

## ✨ Key Features

### 🚀 SQL Generator
Transform natural language into executable SQL queries with AI assistance.

```python
# Example: "Find all buildings within 500 meters of parks"
# Automatically generates:
SELECT b.*, p.name as park_name
FROM buildings b
JOIN parks p ON ST_DWithin(b.geom, p.geom, 500)
```

**Features:**
- ✅ Natural language to SQL conversion
- ✅ Automatic schema detection
- ✅ Query validation and optimization
- ✅ Support for PostGIS functions
- ✅ Context-aware suggestions

### 🖼️ Model Builder Converter
Convert QGIS Model Builder workflows to Python code using AI vision.

**Features:**
- ✅ Screenshot-to-code conversion
- ✅ Azure Computer Vision integration
- ✅ Automatic code generation
- ✅ Error detection and fixing
- ✅ Code optimization suggestions

### 🔧 Smart Assistant
Get intelligent suggestions and recommendations for your geospatial tasks.

**Features:**
- ✅ Context-aware suggestions
- ✅ Workflow recommendations
- ✅ Best practice tips
- ✅ Performance optimization hints

### 🛠️ Error Fixer
Automatically detect and fix SQL errors with AI-powered solutions.

**Features:**
- ✅ Automatic error detection
- ✅ Intelligent error fixing
- ✅ Multiple fix suggestions
- ✅ Error explanation and learning

### 📊 Data Analysis
Quick and custom data analysis with AI-powered insights.

**Features:**
- ✅ Quick analysis templates
- ✅ Custom analysis queries
- ✅ Statistical summaries
- ✅ Visualization suggestions

### 📜 Query History
Track and manage all your SQL queries with full history.

**Features:**
- ✅ Complete query history
- ✅ Search and filter
- ✅ Re-run previous queries
- ✅ Export history

### 🔄 Batch Processing
Process multiple queries and operations in batch.

**Features:**
- ✅ Batch SQL execution
- ✅ Progress tracking
- ✅ Error handling
- ✅ Results aggregation

### 📝 Template Manager
Create and manage SQL query templates for common operations.

**Features:**
- ✅ Template library
- ✅ Custom templates
- ✅ Template variables
- ✅ Quick insertion

### 📈 Analytics Dashboard
Monitor plugin usage and performance metrics.

**Features:**
- ✅ Usage statistics
- ✅ Performance metrics
- ✅ Query success rates
- ✅ Model performance tracking

---

## 🚀 Installation

### Prerequisites

- **QGIS**: Version 3.0 or higher
- **Python**: 3.9+ (included with QGIS)
- **Operating System**: Windows, macOS, or Linux
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Internet**: Required for cloud-based LLM providers (optional for Ollama)

### Step 1: Download Plugin

**Option A: Git Clone (Recommended)**
```bash
cd ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins/
git clone <repository-url> GeoAI_Assistant
```

**Option B: Manual Download**
1. Download the plugin folder
2. Extract to QGIS plugins directory:
   - **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
   - **Windows**: `C:\Users\YourName\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`

### Step 2: Enable Plugin

1. Open QGIS
2. Go to `Plugins → Manage and Install Plugins`
3. Search for "GeoAI Assistant Pro"
4. Check the box to enable
5. Click "Close"

### Step 3: Install Dependencies

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

### Step 4: Configure Environment

1. Copy `.env.example` to `.env` (if available)
2. Or create `.env` file in plugin root directory
3. Add your API keys:

```env
# LLM Provider (ollama, openai, anthropic, google, etc.)
LLM_PROVIDER=ollama

# Model Names
LLM_MODEL_TEXT=phi3
LLM_MODEL_VISION=gpt-4o

# API Keys (for cloud providers)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434

# Azure Computer Vision (for Model Converter)
AZURE_COMPUTER_VISION_ENDPOINT=your_endpoint
AZURE_COMPUTER_VISION_KEY=your_key
```

### Step 5: Restart QGIS

Close and reopen QGIS to ensure all modules load correctly.

---

## 🎬 Quick Start

### 1. Open the Plugin

Click the **GeoAI Assistant Pro** icon in the toolbar, or go to:
```
Plugins → GeoAI Assistant Pro → Open GeoAI Assistant Pro
```

### 2. Select a Model

Use the model selector in the top bar:
- **Ollama** (Local, Free) - Recommended for beginners
- **OpenAI** (Cloud, Paid) - Best quality
- **Anthropic** (Cloud, Paid) - Excellent quality
- **Google** (Cloud, Paid) - Good balance

### 3. Generate Your First SQL Query

1. Go to **SQL Generator** tab
2. Type: `"Find all buildings larger than 1000 square meters"`
3. Click **🚀 Generate SQL**
4. Review the generated SQL
5. Click **▶️ Execute** to run

### 4. Try Model Converter

1. Go to **Model Converter** tab
2. Take a screenshot of your QGIS Model Builder
3. Click **📷 Upload Image**
4. Get Python code automatically generated

---

## 🔄 Workflow

### Complete Workflow Diagram

![Workflow Overview](media/demo-screenshot-2.jpeg)

### Step-by-Step Workflow

#### 1. **SQL Generation Workflow**

```
User Input (Natural Language)
    ↓
AI Processing (LLM)
    ↓
SQL Generation
    ↓
Query Validation
    ↓
Error Detection (if any)
    ↓
Auto-Fix (if needed)
    ↓
Execution
    ↓
Results Display
```

**Video Demo**: [Watch SQL Generation Workflow](media/demo-workflow-1.mp4)

#### 2. **Model Converter Workflow**

```
Screenshot Upload
    ↓
Azure Computer Vision Analysis
    ↓
AI Code Generation
    ↓
Code Validation
    ↓
Error Fixing (if needed)
    ↓
Python Code Output
```

**Video Demo**: [Watch Model Converter Workflow](media/demo-workflow-2.mp4)

#### 3. **Error Fixing Workflow**

```
SQL Error Detected
    ↓
Error Analysis
    ↓
Multiple Fix Suggestions
    ↓
User Selection
    ↓
Auto-Apply Fix
    ↓
Re-execution
```

**Video Demo**: [Watch Error Fixing Workflow](media/demo-workflow-3.mp4)

### Typical Use Cases

#### Use Case 1: Spatial Analysis
```
1. User: "Find all buildings within 500m of parks"
2. AI generates: ST_DWithin query
3. Execute and visualize results
4. Export to new layer
```

#### Use Case 2: Data Aggregation
```
1. User: "Calculate total area by land use category"
2. AI generates: GROUP BY query with SUM
3. Execute and view statistics
4. Create summary report
```

#### Use Case 3: Model Builder Conversion
```
1. User uploads Model Builder screenshot
2. AI analyzes workflow
3. Generates Python script
4. User can run or modify code
```

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    QGIS Plugin Interface                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
┌───────▼────────┐                  ┌────────▼────────┐
│  UI Components │                  │  Core Modules   │
├────────────────┤                  ├─────────────────┤
│ • SQL Editor   │                  │ • LLM Handler   │
│ • Model Conv.  │                  │ • SQL Executor  │
│ • Smart Assist │                  │ • Error Fixer   │
│ • Data Analysis│                  │ • Image Proc.   │
│ • History      │                  │ • Validator     │
│ • Settings     │                  └────────┬────────┘
└───────┬────────┘                           │
        │                                    │
        └──────────────┬─────────────────────┘
                       │
        ┌──────────────▼──────────────┐
        │    Infrastructure Layer     │
        ├─────────────────────────────┤
        │ • Config Manager            │
        │ • Logger                    │
        │ • Cache Service             │
        │ • History Service           │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │    External Services        │
        ├─────────────────────────────┤
        │ • LLM Providers             │
        │   - OpenAI                  │
        │   - Anthropic               │
        │   - Google                  │
        │   - Ollama                  │
        │ • Azure Computer Vision     │
        │ • PostgreSQL/PostGIS        │
        └─────────────────────────────┘
```

### Module Structure

```
GeoAI_Assistant/
├── core/                    # Core business logic
│   └── llm/                # LLM provider interfaces
├── modules/                 # Main plugin modules
│   ├── llm_handler.py      # LLM interaction handler
│   ├── sql_executor.py     # SQL execution engine
│   ├── error_fixer.py      # Error detection & fixing
│   ├── image_processor.py  # Image analysis
│   └── smart_assistant.py  # AI suggestions
├── ui/                      # User interface
│   ├── main_window.py      # Main window
│   └── components/         # UI components
├── services/                # Background services
│   ├── cache_service.py    # Caching
│   ├── history_service.py  # Query history
│   └── query_service.py    # Query management
├── infrastructure/          # Infrastructure
│   ├── config/             # Configuration
│   └── logging/            # Logging
├── tests/                   # Test suite
├── docs/                    # Documentation
├── scripts/                 # Utility scripts
└── media/                   # Media files
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the plugin root directory:

```env
# ============================================
# LLM Provider Configuration
# ============================================
# Options: ollama, openai, anthropic, google, openrouter, huggingface
LLM_PROVIDER=ollama

# Model Names
LLM_MODEL_TEXT=phi3
LLM_MODEL_VISION=gpt-4o

# ============================================
# OpenAI Configuration
# ============================================
OPENAI_API_KEY=sk-...

# ============================================
# Anthropic Configuration
# ============================================
ANTHROPIC_API_KEY=sk-ant-...

# ============================================
# Google Configuration
# ============================================
GOOGLE_API_KEY=...

# ============================================
# Ollama Configuration
# ============================================
OLLAMA_BASE_URL=http://localhost:11434

# ============================================
# Azure Computer Vision (Model Converter)
# ============================================
AZURE_COMPUTER_VISION_ENDPOINT=https://...
AZURE_COMPUTER_VISION_KEY=...

# ============================================
# Database Configuration (Optional)
# ============================================
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_user
DB_PASSWORD=your_password
```

### Plugin Settings

Access settings via:
```
Plugins → GeoAI Assistant Pro → Settings
```

**Available Settings:**
- Model selection
- API key management
- Azure credentials
- Cache configuration
- History retention
- Performance tuning

---

## 💡 Usage Examples

### Example 1: Spatial Query

**Input:**
```
Find all buildings within 500 meters of parks, 
show building type and area
```

**Generated SQL:**
```sql
SELECT 
    b.id,
    b.type,
    b.area,
    p.name as park_name,
    ST_Distance(b.geom, p.geom) as distance
FROM buildings b
JOIN parks p ON ST_DWithin(b.geom, p.geom, 500)
ORDER BY distance;
```

### Example 2: Aggregation Query

**Input:**
```
Calculate total area by land use category
```

**Generated SQL:**
```sql
SELECT 
    category,
    COUNT(*) as count,
    SUM(area) as total_area,
    AVG(area) as avg_area
FROM landuse
GROUP BY category
ORDER BY total_area DESC;
```

### Example 3: Model Builder Conversion

**Input:**
Screenshot of QGIS Model Builder workflow

**Output:**
```python
from qgis.core import *
from qgis.utils import iface

# Load input layer
input_layer = QgsVectorLayer('/path/to/input.shp', 'input', 'ogr')

# Buffer operation
buffer_layer = processing.run("native:buffer", {
    'INPUT': input_layer,
    'DISTANCE': 100,
    'SEGMENTS': 5,
    'END_CAP_STYLE': 0,
    'JOIN_STYLE': 0,
    'MITER_LIMIT': 2,
    'DISSOLVE': False,
    'OUTPUT': 'memory:'
})['OUTPUT']

# Add to map
QgsProject.instance().addMapLayer(buffer_layer)
```

---

## 📚 Documentation

### Available Documentation

All documentation is located in the `docs/` folder:

- **[USER_GUIDE.md](docs/USER_GUIDE.md)** - Complete user guide
- **[DOCUMENTATION.md](docs/DOCUMENTATION.md)** - Full documentation
- **[TESTING_GUIDE.md](docs/TESTING_GUIDE.md)** - Testing guide
- **[AZURE_SETUP.md](docs/AZURE_SETUP.md)** - Azure setup guide
- **[AZURE_QUICK_START.md](docs/AZURE_QUICK_START.md)** - Quick Azure start

### Quick Reference

- **SQL Generator**: See [USER_GUIDE.md](docs/USER_GUIDE.md#sql-generator)
- **Model Converter**: See [USER_GUIDE.md](docs/USER_GUIDE.md#model-converter)
- **Error Fixer**: See [USER_GUIDE.md](docs/USER_GUIDE.md#error-fixer)
- **Configuration**: See [DOCUMENTATION.md](docs/DOCUMENTATION.md#configuration)

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### How to Contribute

1. **Fork the Repository**
   ```bash
   git clone <your-fork-url>
   cd GeoAI_Assistant
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Follow the code style
   - Add tests for new features
   - Update documentation

4. **Test Your Changes**
   ```bash
   # Run tests
   python -m pytest tests/
   ```

5. **Commit and Push**
   ```bash
   git add .
   git commit -m "Add: your feature description"
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Go to GitHub
   - Click "New Pull Request"
   - Describe your changes
   - Submit for review

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd GeoAI_Assistant

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run in QGIS
# Copy to QGIS plugins directory and enable
```

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings
- Write unit tests
- Update documentation

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **QGIS Community** - For the amazing platform
- **LLM Providers** - OpenAI, Anthropic, Google, Ollama
- **Azure** - For Computer Vision API
- **Contributors** - All who helped improve this plugin

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Email**: support@geoai.example.com

---

## 🗺️ Roadmap

- [ ] Support for more LLM providers
- [ ] Enhanced error fixing algorithms
- [ ] Batch processing improvements
- [ ] Advanced analytics dashboard
- [ ] Plugin marketplace integration
- [ ] Multi-language support
- [ ] Cloud sync for templates
- [ ] Collaborative features

---

<div align="center">

**Made with ❤️ for the QGIS Community**

[⭐ Star us on GitHub](https://github.com/your-repo) • [📖 Documentation](docs/) • [🐛 Report Bug](https://github.com/your-repo/issues) • [💡 Request Feature](https://github.com/your-repo/issues)

---

**Version 2.0.0** | **MIT License** | **© 2024 GeoAI Team**

</div>
