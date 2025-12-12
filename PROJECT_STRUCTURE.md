# QuizLM Project Structure

## Overview
```
quizlm/
├── main.py                      # Application entry point
├── config.py                    # Configuration management
├── requirements.txt             # Python dependencies
├── setup.sh                     # Automated setup script
├── env.example                  # Environment template
│
├── README.md                    # Full documentation
├── QUICKSTART.md                # Quick start guide
├── PRD.md                       # Product requirements
├── PROJECT_STRUCTURE.md         # This file
│
├── ui/                          # User Interface Layer
│   ├── __init__.py
│   └── main_window.py          # Main window (CustomTkinter)
│
├── logic/                       # Business Logic Layer
│   ├── __init__.py
│   ├── quiz_generator.py       # Quiz generation orchestration
│   ├── model_trainer.py        # Training image analysis
│   ├── document_processor.py   # Document parsing
│   ├── llm_client.py           # LLM API client
│   └── pdf_generator.py        # PDF creation
│
└── data/                        # Data Storage (auto-created)
    ├── training_images/         # Handwritten quiz examples
    ├── source_documents/        # Optional source storage
    ├── quizzes/                 # Generated quiz PDFs
    ├── models/                  # Style configuration
    └── quiz_metadata/           # Quiz metadata
```

## Module Descriptions

### Core Modules

#### `main.py`
- Application entry point
- Initializes and runs the main window
- Handles top-level error catching

#### `config.py`
- Centralized configuration management
- Environment variable loading
- Directory path management
- API key validation
- Creates necessary directories on initialization

### UI Layer (`ui/`)

#### `ui/main_window.py`
- Main application window using CustomTkinter
- Mode switching (Training Mode / Generate Mode)
- File upload and drag-and-drop support
- Quiz generation controls
- Training image management interface
- Event handling and user interactions

**Key Features:**
- Dark mode UI with modern aesthetics
- Segmented button for mode switching
- Text input area for pasting content
- File browser integration
- Status display and feedback
- Quiz name validation

### Business Logic Layer (`logic/`)

#### `logic/quiz_generator.py`
- **Purpose:** Orchestrates quiz generation workflow
- **Key Functions:**
  - `generate_quiz()`: Main generation pipeline
  - Loads style information from training
  - Calls LLM for quiz content generation
  - Triggers PDF generation
  - Saves quiz metadata

#### `logic/model_trainer.py`
- **Purpose:** Manages training image analysis
- **Key Functions:**
  - `add_training_image()`: Add new training example
  - `get_training_images()`: List all training images
  - `train_model()`: Analyze all images for style extraction
  - Backs up existing style data before retraining
  - Aggregates style information from multiple examples

#### `logic/document_processor.py`
- **Purpose:** Extract text from various document formats
- **Supported Formats:**
  - PDF (via PyPDF2)
  - Word documents (via python-docx)
  - Plain text files
  - Images with text (via pytesseract OCR)
- **Key Functions:**
  - `process_document()`: Main processing dispatcher
  - Format-specific processors for each file type

#### `logic/llm_client.py`
- **Purpose:** Interface with Language Model APIs
- **Supported Providers:**
  - Anthropic Claude (with vision)
  - OpenAI GPT-4 (with vision)
  - Extensible for Grok and others
- **Key Functions:**
  - `analyze_quiz_image()`: Analyze handwritten quizzes using vision
  - `generate_quiz_content()`: Generate quiz from source material
  - Handles image encoding and API communication
  - JSON response parsing

#### `logic/pdf_generator.py`
- **Purpose:** Create professional PDF quiz sheets
- **Features:**
  - Two-column layout (quiz | answers)
  - Verdana 12pt font
  - Narrow margins (0.5 inch)
  - Center divider line
  - Text wrapping and pagination
  - Header and footer
- **Key Functions:**
  - `create_quiz_pdf()`: Generate complete PDF
  - Text wrapping and layout management

### Data Layer (`data/`)

#### `data/training_images/`
- Stores user's handwritten quiz examples
- Images used for style analysis
- Formats: PNG, JPG, JPEG

#### `data/source_documents/`
- Optional storage for source materials
- Original files used to generate quizzes

#### `data/quizzes/`
- Generated quiz PDFs
- Named according to user input
- Format: `{quiz_name}.pdf`

#### `data/models/`
- Stores extracted style information
- `style_info.json`: Aggregated style patterns
- `backups/`: Previous style versions

#### `data/quiz_metadata/`
- Metadata for each generated quiz
- JSON files with generation details
- Tracks: difficulty, timestamp, question count

## Architecture Patterns

### MVC/MVP Pattern
- **Model:** `logic/` modules (business logic)
- **View:** `ui/` modules (user interface)
- **Controller/Presenter:** Event handlers in `main_window.py`

### Separation of Concerns
- UI doesn't know about LLM APIs
- Business logic doesn't know about UI widgets
- Configuration is centralized and injectable

### Dependency Flow
```
UI Layer
   ↓
Business Logic Layer
   ↓
External Services (LLM APIs, File System)
```

## Key Design Decisions

### 1. VLM-Based Approach (No Traditional Training)
Rather than training a custom ML model, QuizLM uses:
- Vision-Language Models to analyze handwritten examples
- Prompt engineering to generate quizzes
- Style configuration stored as JSON

**Benefits:**
- No training infrastructure needed
- Fast iteration and customization
- Excellent results with few examples
- Leverages cutting-edge AI capabilities

### 2. Local-First Architecture
- All data stored locally in `data/` directory
- No server deployment required
- API calls only for LLM generation
- User maintains full control of data

### 3. Modular LLM Integration
- Abstract LLM client supports multiple providers
- Easy to add new providers (Ollama, local models)
- Configurable via environment variables

### 4. Type Hints Throughout
- Full type annotations for IDE support
- Better code documentation
- Catch errors early with type checkers

## Extension Points

### Adding New Document Formats
Edit `logic/document_processor.py`:
```python
def _process_new_format(self, file_path: Path) -> str:
    # Implement new format processor
    pass
```

### Adding New LLM Providers
Edit `logic/llm_client.py`:
```python
if self.provider == "new_provider":
    # Implement new provider
    pass
```

### Customizing PDF Layout
Edit `logic/pdf_generator.py`:
- Modify `create_quiz_pdf()` method
- Adjust fonts, margins, layout

### Adding UI Features
Edit `ui/main_window.py`:
- Add new widgets and handlers
- Extend mode switching logic

## Development Workflow

### 1. Setup Development Environment
```bash
./setup.sh
source venv/bin/activate
```

### 2. Install Development Dependencies
```bash
pip install pytest mypy black flake8
```

### 3. Run Type Checking
```bash
mypy main.py ui/ logic/
```

### 4. Run Tests (when added)
```bash
pytest tests/
```

### 5. Format Code
```bash
black main.py ui/ logic/ config.py
```

## Configuration Files

### `.env`
```bash
QUIZLM_LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### `requirements.txt`
Lists all Python dependencies with versions

### `setup.sh`
Automated setup script for Unix-like systems

## Data Flow Diagrams

### Training Mode Flow
```
User uploads image
       ↓
main_window.py: _add_training_image()
       ↓
model_trainer.py: add_training_image()
       ↓
Image saved to data/training_images/
       ↓
User clicks "Train Model"
       ↓
model_trainer.py: train_model()
       ↓
llm_client.py: analyze_quiz_image() [for each image]
       ↓
Aggregate style info
       ↓
Save to data/models/style_info.json
```

### Quiz Generation Flow
```
User provides source + settings
       ↓
main_window.py: _generate_quiz()
       ↓
quiz_generator.py: generate_quiz()
       ↓
document_processor.py: process_document()
       ↓
llm_client.py: generate_quiz_content()
       ↓
pdf_generator.py: create_quiz_pdf()
       ↓
PDF saved to data/quizzes/
       ↓
Metadata saved to data/quiz_metadata/
```

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| UI | CustomTkinter | Modern, native-looking GUI |
| LLM | Claude/GPT-4 Vision | Quiz analysis & generation |
| Document Processing | PyPDF2, python-docx, pytesseract | Extract text from files |
| PDF Generation | ReportLab | Create professional PDFs |
| Configuration | python-dotenv | Environment management |
| Language | Python 3.12+ | Core application |

## File Size Guidelines

- `main.py`: ~30 lines (entry point only)
- `config.py`: ~60 lines (configuration)
- `ui/main_window.py`: ~400 lines (full UI)
- `logic/quiz_generator.py`: ~100 lines (orchestration)
- `logic/model_trainer.py`: ~120 lines (training logic)
- `logic/document_processor.py`: ~100 lines (document parsing)
- `logic/llm_client.py`: ~200 lines (LLM integration)
- `logic/pdf_generator.py`: ~150 lines (PDF creation)

## Future Enhancements

### Planned Features
- [ ] PDF preview widget in UI
- [ ] Batch quiz generation
- [ ] Quiz templates and presets
- [ ] Advanced style customization UI
- [ ] Diagram/figure quiz support
- [ ] Additional export formats
- [ ] Local LLM support (Ollama)
- [ ] Quiz statistics and analytics

### Architectural Improvements
- [ ] Plugin system for document processors
- [ ] Event-driven architecture for long-running operations
- [ ] Caching layer for LLM responses
- [ ] Async operations for better UI responsiveness
- [ ] Comprehensive test suite
- [ ] CI/CD pipeline

---

**Last Updated:** December 12, 2025
**Version:** 1.0 MVP

