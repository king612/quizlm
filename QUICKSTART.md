# QuizLM Quick Start Guide

Get QuizLM running in 5 minutes!

## Prerequisites

- Python 3.12+ installed
- API key for Claude (Anthropic) - **Recommended**
  - Get one at: https://console.anthropic.com/

## Installation (Automated)

### macOS/Linux

```bash
cd /Users/john/projects/quizlm
./setup.sh
```

### Windows

```bash
cd \Users\john\projects\quizlm
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy env.example .env
```

## Configuration

Edit the `.env` file with your API key:

```bash
nano .env
```

Add your Claude API key:

```
QUIZLM_LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

Save and exit (Ctrl+X, then Y, then Enter)

## Run the Application

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Run QuizLM
python main.py
```

## First Use - Step by Step

### 1. Train the System (One-time setup)

1. Click **"Training Mode"** in the header
2. Click **"➕ Add Training Image"**
3. Select a handwritten quiz image
4. Give it a unique name (e.g., "biology-quiz-1")
5. Repeat for 3-5 quiz examples
6. Click **"🔄 Train Model"**
7. Wait ~30 seconds while the system analyzes your style

### 2. Generate Your First Quiz

1. Click **"Generate Mode"** in the header
2. Either:
   - Click **"📁 Upload File"** and select a PDF/Word/image/text file, OR
   - Paste text directly into the text box
3. Enter a quiz name (e.g., "biology-chapter-3")
4. Select difficulty: **Easy**, **Medium**, or **Hard**
5. Select quiz layout: **Split Page** or **Full Page**
   - Split Page: Quiz on left, answers on right (side-by-side)
   - Full Page: Quiz uses full width, answers on separate pages at end
6. Click **"🎯 Generate Quiz"**
7. Your quiz PDF will be saved to `data/quizzes/`

### 3. View Your Quizzes

- Click **"📚 View Existing Quizzes"** to see all generated quizzes
- Open the `data/quizzes/` folder to print or share

## Tips

- **Better Training Results:** Use 5-10 diverse quiz examples
- **Source Material:** Works best with educational content (textbooks, articles, notes)
- **Difficulty:**
  - Easy = Fewer blanks, more hints
  - Medium = Balanced (mimics your training examples)
  - Hard = More blanks, fewer hints
- **Layout:**
  - Split Page = Side-by-side quiz and answers (traditional)
  - Full Page = Full-width quiz, separate answer pages (better for longer content)
- **File Formats:** PDF, Word (.docx), images (.png, .jpg), plain text (.txt)

## Troubleshooting

### "API key not set" error
Make sure you created `.env` file and added your API key.

### Application won't start
```bash
# Check Python version
python3 --version  # Should be 3.12+

# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt
```

### CustomTkinter issues
If you see UI errors, try:
```bash
pip install --upgrade customtkinter
```

## Get More Help

- See `README.md` for detailed documentation
- See `PRD.md` for feature specifications

## Example Workflow

```
1. Collect 3-5 handwritten quiz examples
   └─ Add to Training Mode

2. Train the system (one time)
   └─ Click "Train Model"

3. Prepare source material
   └─ Textbook chapter, article, notes, etc.

4. Generate quiz
   └─ Upload → Name → Select difficulty → Generate

5. Print and study!
   └─ PDFs are in data/quizzes/
```

Happy learning! 🎯

