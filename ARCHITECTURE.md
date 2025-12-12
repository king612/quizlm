# QuizLM Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        QuizLM                               │
│                 Quiz Generation System                      │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            │                               │
     ┌──────▼──────┐                ┌──────▼──────┐
     │ Training    │                │  Generate   │
     │   Mode      │                │    Mode     │
     └──────┬──────┘                └──────┬──────┘
            │                               │
            │                               │
    ┌───────▼────────┐              ┌──────▼──────────┐
    │ Analyze Quiz   │              │ Process Source  │
    │ Images (VLM)   │              │ Document        │
    └───────┬────────┘              └──────┬──────────┘
            │                               │
            │                               │
    ┌───────▼────────┐              ┌──────▼──────────┐
    │ Extract Style  │              │ Generate Quiz   │
    │ Patterns       │              │ (LLM + Style)   │
    └───────┬────────┘              └──────┬──────────┘
            │                               │
            │                               │
    ┌───────▼────────┐              ┌──────▼──────────┐
    │ Save Style     │              │ Render PDF      │
    │ Config (JSON)  │              │ (ReportLab)     │
    └────────────────┘              └──────┬──────────┘
                                            │
                                    ┌───────▼────────┐
                                    │ Save to        │
                                    │ data/quizzes/  │
                                    └────────────────┘
```

## Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     UI Layer (ui/)                          │
│  - main_window.py: CustomTkinter GUI                        │
│  - Mode switching, file upload, drag-and-drop               │
│  - Event handling and user feedback                         │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                Business Logic Layer (logic/)                │
│  - quiz_generator.py: Orchestration                         │
│  - model_trainer.py: Style analysis                         │
│  - document_processor.py: Multi-format parsing              │
│  - llm_client.py: LLM API integration                       │
│  - pdf_generator.py: PDF creation                           │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│              External Services & Storage                    │
│  - Anthropic Claude API / OpenAI GPT-4 API                  │
│  - Local filesystem (data/ directory)                       │
│  - System file dialogs                                      │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow: Training Mode

```
┌─────────────┐
│   User      │
│ Uploads     │
│ Handwritten │
│ Quiz Image  │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│  MainWindow      │
│ _add_training_   │
│   image()        │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  ModelTrainer    │
│ add_training_    │
│   image()        │
└──────┬───────────┘
       │ (copy file)
       ▼
┌──────────────────────┐
│ data/training_images/│
│ example-quiz-1.png   │
└──────────────────────┘
       │
       │ User clicks "Train Model"
       ▼
┌──────────────────┐
│  ModelTrainer    │
│  train_model()   │
└──────┬───────────┘
       │ (for each image)
       ▼
┌──────────────────┐
│   LLMClient      │
│ analyze_quiz_    │
│   image()        │
└──────┬───────────┘
       │ (API call)
       ▼
┌──────────────────────┐
│  Claude Vision /     │
│  GPT-4 Vision        │
│  Analyzes image      │
└──────┬───────────────┘
       │ (returns JSON)
       ▼
┌──────────────────┐
│  ModelTrainer    │
│ _aggregate_      │
│  style_info()    │
└──────┬───────────┘
       │
       ▼
┌──────────────────────┐
│ data/models/         │
│ style_info.json      │
└──────────────────────┘
```

## Data Flow: Quiz Generation

```
┌─────────────┐
│   User      │
│ Provides    │
│ Source      │
│ Material    │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│  MainWindow      │
│ _generate_quiz() │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ QuizGenerator    │
│ generate_quiz()  │
└──────┬───────────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌────────────────┐  ┌─────────────────┐
│ Document       │  │ Load            │
│ Processor      │  │ style_info.json │
│ process_       │  └────────┬────────┘
│ document()     │           │
└────┬───────────┘           │
     │ (extract text)        │
     │                       │
     └──────┬────────────────┘
            │ (text + style)
            ▼
┌──────────────────┐
│   LLMClient      │
│ generate_quiz_   │
│   content()      │
└──────┬───────────┘
       │ (API call with style context)
       ▼
┌──────────────────────┐
│  Claude / GPT-4      │
│  Generates quiz JSON │
└──────┬───────────────┘
       │ (returns questions + answers)
       ▼
┌──────────────────┐
│  PDFGenerator    │
│ create_quiz_pdf()│
└──────┬───────────┘
       │ (ReportLab)
       ▼
┌──────────────────────┐
│ data/quizzes/        │
│ my-quiz.pdf          │
└──────────────────────┘
```

## Module Interactions

```
main.py
  └── MainWindow (ui/main_window.py)
       ├── QuizGenerator (logic/quiz_generator.py)
       │    ├── DocumentProcessor (logic/document_processor.py)
       │    │    └── [PyPDF2, python-docx, pytesseract]
       │    ├── LLMClient (logic/llm_client.py)
       │    │    └── [Anthropic API, OpenAI API]
       │    └── PDFGenerator (logic/pdf_generator.py)
       │         └── [ReportLab]
       │
       ├── ModelTrainer (logic/model_trainer.py)
       │    └── LLMClient (logic/llm_client.py)
       │         └── [Anthropic API, OpenAI API]
       │
       └── Config (config.py)
            └── [Environment variables, paths]
```

## Key Design Patterns

### 1. Model-View-Presenter (MVP)

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│    View     │◄───────►│  Presenter   │◄───────►│    Model    │
│ (UI Layer)  │         │ (MainWindow) │         │  (Logic)    │
└─────────────┘         └──────────────┘         └─────────────┘
```

- **View:** CustomTkinter widgets (`main_window.py`)
- **Presenter:** Event handlers in `MainWindow` class
- **Model:** Business logic modules (`quiz_generator`, `model_trainer`, etc.)

### 2. Dependency Injection

```python
class MainWindow:
    def __init__(self):
        self.config = Config()
        self.quiz_generator = QuizGenerator(self.config)  # Inject config
        self.model_trainer = ModelTrainer(self.config)    # Inject config
```

### 3. Strategy Pattern (Document Processing)

```python
class DocumentProcessor:
    def process_document(self, file_path: Path) -> str:
        if suffix == '.pdf':
            return self._process_pdf(file_path)
        elif suffix == '.docx':
            return self._process_docx(file_path)
        # ... different strategies for different formats
```

### 4. Facade Pattern (LLM Client)

```python
class LLMClient:
    # Provides simple interface to complex LLM APIs
    def analyze_quiz_image(self, image_path: Path) -> dict: ...
    def generate_quiz_content(self, source: str, ...) -> dict: ...
```

## Configuration Management

```
Environment Variables (.env)
         ↓
┌────────────────────┐
│   Config class     │
│  - API keys        │
│  - Provider choice │
│  - Directory paths │
└─────────┬──────────┘
          │ (injected into)
          ↓
┌────────────────────┐
│  All modules use   │
│  config.data_dir   │
│  config.api_keys   │
└────────────────────┘
```

## File Organization

```
quizlm/
│
├── Entry Point
│   └── main.py
│
├── Configuration
│   ├── config.py
│   ├── .env (user-created)
│   └── env.example
│
├── UI Layer
│   └── ui/
│       ├── __init__.py
│       └── main_window.py
│
├── Business Logic
│   └── logic/
│       ├── __init__.py
│       ├── quiz_generator.py
│       ├── model_trainer.py
│       ├── document_processor.py
│       ├── llm_client.py
│       └── pdf_generator.py
│
├── Data Storage (runtime)
│   └── data/
│       ├── training_images/
│       ├── source_documents/
│       ├── quizzes/
│       ├── models/
│       └── quiz_metadata/
│
└── Documentation
    ├── README.md
    ├── QUICKSTART.md
    ├── PRD.md
    ├── PROJECT_STRUCTURE.md
    ├── ARCHITECTURE.md (this file)
    └── SETUP_COMPLETE.md
```

## Error Handling Strategy

```
UI Layer
  └── Try/Catch → Show user-friendly error dialog
       │
       ▼
Business Logic Layer
  └── Validate inputs → Raise ValueError/TypeError
       │
       ▼
External Services
  └── Handle API errors → Raise meaningful exceptions
```

Example:
```python
# UI Layer (main_window.py)
try:
    output_path = self.quiz_generator.generate_quiz(...)
    messagebox.showinfo("Success", f"Quiz generated: {output_path}")
except Exception as e:
    messagebox.showerror("Error", f"Failed: {str(e)}")

# Business Logic Layer (quiz_generator.py)
def generate_quiz(self, quiz_name: str, ...):
    if not quiz_name:
        raise ValueError("Quiz name is required")
    # ... processing
```

## State Management

```
MainWindow class maintains application state:
  ├── current_mode: "generate" | "train"
  ├── current_source_file: Optional[Path]
  ├── unsaved_changes: bool
  └── UI widgets (entries, text boxes, etc.)

No global state - everything passed via parameters or injected
```

## LLM Integration Architecture

```
┌──────────────────────────────────────────────┐
│           LLMClient (Abstraction)            │
├──────────────────────────────────────────────┤
│  - analyze_quiz_image()                      │
│  - generate_quiz_content()                   │
└───────────┬──────────────────────────────────┘
            │
            ├─── Claude (Anthropic)
            │     └── API: claude-3-5-sonnet-20241022
            │
            ├─── GPT-4 (OpenAI)
            │     └── API: gpt-4o
            │
            └─── Extensible for:
                  ├─── Grok (xAI)
                  ├─── Ollama (local)
                  └─── Custom providers
```

## PDF Generation Pipeline

```
Quiz JSON
    ↓
┌────────────────────┐
│ PDFGenerator       │
│ create_quiz_pdf()  │
└─────────┬──────────┘
          │
          ├─── Create ReportLab canvas
          ├─── Set fonts and layout
          ├─── Draw center divider line
          ├─── Process questions:
          │     ├─── Wrap text (left column)
          │     ├─── Place answers (right column)
          │     └─── Handle pagination
          ├─── Add header/footer
          └─── Save PDF
```

## Security Considerations

### API Key Protection
```
.env file (gitignored)
    ↓
Environment variables
    ↓
Config class (loaded at startup)
    ↓
LLMClient (used for API calls only)

✓ Never logged
✓ Never displayed in UI
✓ Never committed to git
```

### Data Privacy
- All data stored locally in `data/` directory
- No telemetry or analytics
- User maintains complete control
- API calls only for quiz generation (content sent to LLM provider)

## Performance Characteristics

| Operation | Typical Duration | Bottleneck |
|-----------|-----------------|------------|
| UI Launch | < 1 second | Python startup |
| Add training image | < 1 second | File copy |
| Train model (5 images) | 20-40 seconds | LLM API calls |
| Process PDF | 1-3 seconds | PDF parsing |
| Generate quiz | 10-20 seconds | LLM API call |
| Render PDF | < 1 second | ReportLab |

## Extensibility Points

### 1. New Document Formats
```python
# In document_processor.py
def _process_markdown(self, file_path: Path) -> str:
    # Add Markdown support
    pass
```

### 2. New LLM Providers
```python
# In llm_client.py
elif self.provider == "ollama":
    # Add local LLM support
    self.client = Ollama(...)
```

### 3. Custom PDF Styles
```python
# In pdf_generator.py
def create_quiz_pdf(self, ..., style: str = "default"):
    if style == "compact":
        # Implement compact layout
    elif style == "large_print":
        # Implement large print layout
```

### 4. Quiz Export Formats
```python
# New module: logic/quiz_exporter.py
class QuizExporter:
    def to_anki(self, quiz_data: dict) -> Path: ...
    def to_quizlet(self, quiz_data: dict) -> Path: ...
    def to_markdown(self, quiz_data: dict) -> Path: ...
```

## Testing Strategy (Future)

```
tests/
├── unit/
│   ├── test_document_processor.py
│   ├── test_pdf_generator.py
│   └── test_model_trainer.py
├── integration/
│   ├── test_quiz_generation_flow.py
│   └── test_training_flow.py
└── fixtures/
    ├── sample_quiz_images/
    └── sample_documents/
```

## Deployment Model

**Local Desktop Application**
- No server deployment
- No cloud infrastructure
- Runs entirely on user's machine
- External dependency: LLM API only

```
User's Computer
    ├── Python 3.12+
    ├── QuizLM application
    ├── Local data storage
    └── Internet (for LLM API only)
```

---

**Architecture Version:** 1.0
**Last Updated:** December 12, 2025
**Status:** MVP Ready

