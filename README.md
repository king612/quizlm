# QuizLM - Full-Document Quiz Generator

A local-only Python application that generates comprehensive cloze-deletion study materials by replicating entire source documents with strategic blanks for key terms. Uses Vision-Language Models to learn your quiz style from handwritten examples.

## Features

- 📄 **Full Document Replication**: Transforms entire documents into study materials, not just excerpts
- 🎯 **Smart Blanking**: Strategically blanks 10-35% of key terms based on difficulty
- 📚 **Style Learning**: Train on handwritten quiz examples (images or PDFs) to match your format
- 📊 **Difficulty Levels**: Easy, Medium, and Hard quiz generation
- 📑 **Two Layout Options**: Full Page (separate answer key) or Split Page (side-by-side)
- 📖 **Multi-Page Output**: Generates comprehensive study materials preserving document structure
- 🖥️ **Modern UI**: Clean, dark-mode interface with intuitive controls

## Architecture

### ML Model Approach

QuizLM uses a **prompt-engineering approach** with modern Vision-Language Models (VLMs) rather than traditional ML training:

- **Vision Analysis**: Claude Vision or GPT-4 Vision analyzes your handwritten quiz images to understand format, style, and patterns
- **Style Extraction**: The system extracts key patterns: blank formatting, hint usage, word selection rules
- **Quiz Generation**: The LLM generates educationally valuable quizzes following your extracted style
- **PDF Rendering**: Python (ReportLab) renders the final quiz in PDF format

**Why this approach?**
- ✅ No training infrastructure needed
- ✅ Excellent results with few examples
- ✅ Fast iteration and updates
- ✅ Leverages state-of-the-art language understanding
- ✅ Easy to customize and refine

## Prerequisites

- Python 3.12 or higher
- API key for one of:
  - Anthropic (Claude) - **Recommended**
  - OpenAI (GPT-4)
  - xAI (Grok)

## Installation

### 1. Clone or download this project

```bash
cd quizlm
```

### 2. Create virtual environment

```bash
python3 -m venv venv
```

### 3. Activate virtual environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure API Keys

Create a `.env` file in the project root:

```bash
# Choose your preferred LLM provider (claude, openai, or grok)
QUIZLM_LLM_PROVIDER=claude

# Add your API key (only need one)
ANTHROPIC_API_KEY=your_claude_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here
# GROK_API_KEY=your_grok_api_key_here
```

**Getting API Keys:**
- **Claude (Anthropic)**: https://console.anthropic.com/
- **OpenAI**: https://platform.openai.com/api-keys
- **Grok (xAI)**: https://x.ai/api

### 6. Install OCR support (optional, for image-to-text)

If you want to process images with text:

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

**Windows:**
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

## Usage

### Start the application

```bash
python main.py
```

### Training Mode

1. Click **"Training Mode"** in the header
2. Click **"➕ Add Training Image"** to upload handwritten quiz examples
3. Add multiple examples (3-5+ recommended)
4. Click **"🔄 Train Model"** to analyze your quiz style

The system will analyze your handwritten quizzes and extract:
- Layout and formatting patterns
- How you format blanks (underscores, hints)
- Which words you typically blank out
- Difficulty indicators

### Generate Mode

1. Click **"Generate Mode"** in the header
2. Either:
   - Upload a file (PDF, Word, image, text)
   - Paste text directly
3. Enter a unique quiz name
4. Select difficulty: Easy, Medium, or Hard
5. Select quiz layout: Split Page or Full Page
6. Click **"🎯 Generate Quiz"**

Your quiz will be generated as a PDF in the `data/quizzes/` folder.

### Quiz Format Options

**Split Page Layout:**
- **Left side**: Quiz with blanks (underscores)
- **Right side**: Answers aligned with questions
- Traditional two-column format

**Full Page Layout:**
- **Quiz pages**: Quiz questions use full page width
- **Answer pages**: Separate answer key at end of PDF
- Answers formatted with spacing for easier grading
- Ideal for longer quizzes or figure-based content

**Both formats use:**
- **Helvetica 12pt** font with narrow margins
- Professional, clean layout

## Project Structure

```
quizlm/
├── main.py                 # Application entry point
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── README.md             # This file
│
├── ui/                   # User interface module
│   ├── __init__.py
│   └── main_window.py   # Main window with CustomTkinter
│
├── logic/               # Business logic module
│   ├── __init__.py
│   ├── quiz_generator.py      # Quiz generation orchestration
│   ├── model_trainer.py       # Training image analysis
│   ├── document_processor.py  # Document parsing (PDF, Word, etc.)
│   ├── llm_client.py          # LLM API client (Claude/OpenAI/Grok)
│   └── pdf_generator.py       # PDF creation with ReportLab
│
└── data/                # Data directory (created automatically)
    ├── training_images/ # Your handwritten quiz examples
    ├── source_documents/ # Source materials
    ├── quizzes/        # Generated quiz PDFs
    └── models/         # Extracted style information
```

## Configuration

### Environment Variables

- `QUIZLM_LLM_PROVIDER`: Choose `claude`, `openai`, or `grok` (default: `claude`)
- `ANTHROPIC_API_KEY`: Your Claude API key
- `OPENAI_API_KEY`: Your OpenAI API key
- `GROK_API_KEY`: Your Grok API key

### Customization

Edit `config.py` to customize:
- Directory locations
- Default settings
- Model preferences

## Troubleshooting

### "API key not set" error
Make sure you've created a `.env` file with your API key and it's in the project root.

### CustomTkinter not working
If CustomTkinter has issues, you can modify `ui/main_window.py` to use standard Tkinter or PyQt6.

### OCR not working
Make sure Tesseract is installed and in your PATH. Test with:
```bash
tesseract --version
```

### Import errors
Make sure your virtual environment is activated and all dependencies are installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Development

### Type Hints

The codebase uses type hints throughout for better IDE support and code quality.

### Architecture

- **MVC/MVP Pattern**: UI is separated from business logic
- **Modular Design**: Each component has a single responsibility
- **Configuration**: Centralized configuration management
- **Extensibility**: Easy to add new document formats or LLM providers

## License

This is a personal-use application. Modify as needed for your requirements.

## Future Enhancements

- [ ] PDF preview widget in UI
- [ ] Batch quiz generation
- [ ] Quiz templates
- [ ] Export to other formats
- [ ] Advanced style customization
- [ ] Diagram/figure quiz support
