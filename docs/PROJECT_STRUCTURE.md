# Project Structure

This document describes the organization of the GeoAI Assistant Pro plugin.

## Directory Structure

```
GeoAI_Assistant/
├── README.md                    # Main project README
├── LICENSE                      # MIT License
├── metadata.txt                 # QGIS plugin metadata
├── icon.png                     # Plugin icon
├── .gitignore                   # Git ignore rules
├── .env.example                 # Environment variables template
│
├── __init__.py                  # Plugin entry point
├── geo_ai_assistant.py          # Main plugin class
│
├── core/                        # Core business logic
│   └── llm/                     # LLM provider interfaces
│       ├── __init__.py
│       ├── interfaces.py        # Provider interfaces
│       ├── models.py            # Data models
│       └── providers/           # Provider implementations
│           ├── __init__.py
│           ├── base_provider.py
│           └── ollama_provider.py
│
├── modules/                     # Main plugin modules
│   ├── __init__.py
│   ├── llm_handler.py          # LLM interaction handler
│   ├── sql_executor.py         # SQL execution engine
│   ├── error_fixer.py           # Error detection & fixing
│   ├── image_processor.py       # Image analysis
│   ├── smart_assistant.py       # AI suggestions
│   └── query_validator.py       # Query validation
│
├── ui/                          # User interface
│   ├── __init__.py
│   ├── main_window.py           # Main window
│   ├── theme_styles.py          # Theme styles
│   ├── components/              # UI components
│   │   ├── __init__.py
│   │   ├── analytics_dashboard.py
│   │   ├── batch_processor.py
│   │   ├── data_analysis.py
│   │   ├── error_fixer.py
│   │   ├── history_panel.py
│   │   ├── model_converter.py
│   │   ├── model_selector.py
│   │   ├── query_editor.py
│   │   ├── settings_panel.py
│   │   ├── smart_assistant.py
│   │   └── template_manager.py
│   └── themes/                  # Theme management
│       ├── __init__.py
│       └── theme_manager.py
│
├── services/                    # Background services
│   ├── __init__.py
│   ├── cache_service.py         # Caching service
│   ├── history_service.py       # Query history
│   └── query_service.py         # Query management
│
├── infrastructure/              # Infrastructure
│   ├── __init__.py
│   ├── config/                  # Configuration
│   │   ├── __init__.py
│   │   └── config_manager.py
│   └── logging/                 # Logging
│       ├── __init__.py
│       └── logger.py
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── run_all_tests.py
│   ├── run_tests_in_qgis.py
│   ├── test_edge_cases.py
│   ├── test_error_fixer.py
│   ├── test_integration.py
│   ├── test_llm_handler.py
│   ├── test_performance.py
│   └── test_sql_queries.py
│
├── docs/                        # Documentation
│   ├── USER_GUIDE.md            # User guide
│   ├── DOCUMENTATION.md         # Full documentation
│   ├── TESTING_GUIDE.md         # Testing guide
│   ├── AZURE_SETUP.md           # Azure setup
│   ├── documentation.html       # HTML documentation
│   ├── documentation_report.html # PDF-ready HTML
│   ├── GeoAI_Assistant_Pro_Report.pdf
│   ├── GeoAI_Assistant_Pro_Documentation.docx
│   └── [other documentation files]
│
├── scripts/                     # Utility scripts
│   ├── create_both_documents.py
│   ├── generate_pdf_report.py
│   ├── commit_and_push.sh
│   ├── push_to_github.sh
│   └── [other utility scripts]
│
└── media/                       # Media files
    ├── demo-screenshot-1.jpeg
    ├── demo-screenshot-2.jpeg
    ├── demo-workflow-1.mp4
    ├── demo-workflow-2.mp4
    └── demo-workflow-3.mp4
```

## File Organization

### Root Level
- **README.md**: Main project documentation
- **LICENSE**: MIT License
- **metadata.txt**: QGIS plugin metadata
- **.gitignore**: Git ignore rules
- **.env.example**: Environment variables template

### Core Files
- **__init__.py**: Plugin entry point
- **geo_ai_assistant.py**: Main plugin class

### Documentation (docs/)
All documentation files are organized in the `docs/` folder:
- Markdown files (.md)
- HTML files (.html)
- PDF and DOCX files
- Instruction files (.txt)

### Scripts (scripts/)
All utility scripts are in the `scripts/` folder:
- Python scripts (.py)
- Shell scripts (.sh)

### Media (media/)
All media files are in the `media/` folder:
- Screenshots (.jpeg, .png)
- Videos (.mp4)
- Other media assets

## Key Modules

### LLM Handler (`modules/llm_handler.py`)
Handles all interactions with Large Language Models:
- Multiple provider support (OpenAI, Anthropic, Google, Ollama, etc.)
- SQL generation from natural language
- Error fixing suggestions
- Smart recommendations

### SQL Executor (`modules/sql_executor.py`)
Executes SQL queries and manages database connections:
- Query execution
- Result handling
- Database schema discovery
- Error handling

### Error Fixer (`modules/error_fixer.py`)
Automatically detects and fixes SQL errors:
- Error detection
- Multiple fix suggestions
- Automatic application
- Learning from fixes

### Image Processor (`modules/image_processor.py`)
Processes images for Model Builder conversion:
- Azure Computer Vision integration
- Image analysis
- Code generation from screenshots

## Configuration

### Environment Variables
Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```

Then edit `.env` with your API keys and configuration.

### Plugin Settings
Access via QGIS:
```
Plugins → GeoAI Assistant Pro → Settings
```

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Style
- Follow PEP 8
- Use type hints
- Add docstrings
- Write unit tests

## Contributing

See [README.md](../README.md#contributing) for contribution guidelines.

