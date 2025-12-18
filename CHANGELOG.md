# QuizLM Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2024-12-17

### Major Changes - Full Document Cloze Deletion

#### Changed
- **BREAKING**: Completely redesigned quiz generation approach from numbered questions to full-document cloze deletion
- Quiz now replicates ENTIRE source document with strategic blanks, not just selected questions
- Changed default quiz style from "Split Page" to "Full Page"
- Updated LLM prompt to generate complete document replicas with blanks throughout
- Modified PDF generator to handle paragraph-based continuous text format
- Updated answer key format to sequential numbered list with optional context

#### Added
- New `QUIZ_GENERATION_SPEC.md` documenting the full-document approach
- Dynamic token allocation based on source document length (up to 16k tokens)
- Support for multi-page quiz generation preserving original document structure
- Section heading preservation in quiz output
- Context snippets in answer key for better reference
- Backward compatibility with old question-based format
- PDF training image support with `pdf2image` integration
- Environment variable loading with `python-dotenv` integration

#### Technical Improvements
- Enhanced PDF rendering with better typography (11pt font, 14pt line spacing)
- Improved text wrapping for both Split Page and Full Page layouts
- Better page break handling for long documents
- More efficient answer key rendering with context

#### Fixed
- Claude API model compatibility (using claude-3-haiku-20240307)
- API key persistence across sessions with .env file loading
- Model name 404 errors resolved

### Usage Impact
- Quizzes now suitable for comprehensive document study, not just quick review
- Multi-page output expected for most source documents
- Answer keys can be extensive (50-200+ blanks depending on document length)
- Better for educational contexts requiring full content coverage

---

## [1.1.0] - 2025-12-16

### Added
- **Full Page Quiz Layout Option**: New quiz layout style in addition to split-page
  - UI selector for choosing between "Split Page" and "Full Page" layouts
  - Split Page: Traditional two-column format (quiz on left, answers on right)
  - Full Page: Quiz uses full page width, answer key on separate pages at end
  - Answer keys in full-page layout use padded spacing (4 spaces) for easier grading
  - `quiz_style` parameter added to quiz generation pipeline
  - Metadata now tracks quiz layout style

### Changed
- PDF Generator refactored into separate methods: `_create_split_page_quiz()` and `_create_full_page_quiz()`
- Font changed from Verdana to Helvetica for better compatibility across systems
- PRD updated with new requirements for full-page layout (REQ-3.6-FP)
- Documentation updated across README, QUICKSTART, and START_HERE guides

### Technical Details
- `MainWindow.quiz_style_var`: New UI variable for layout selection
- `QuizGenerator.generate_quiz()`: Added `quiz_style` parameter (default: "Split Page")
- `PDFGenerator.create_quiz_pdf()`: Added `quiz_style` parameter with routing logic
- Answer key formatting in full-page mode: `"1.    answer    "` format

---

## [1.0.0] - 2025-12-12

### Initial Release
- Complete MVP implementation of QuizLM
- CustomTkinter UI with Training Mode and Generate Mode
- Support for multiple input formats (PDF, DOCX, text, images)
- Vision-Language Model integration (Claude/GPT-4)
- Three difficulty levels (Easy, Medium, Hard)
- Split-page PDF generation with quiz and answers
- Style learning from handwritten quiz examples
- Comprehensive documentation suite

### Features
- Training image upload and management
- VLM-based style analysis
- Multi-format document processing
- Intelligent word selection and blank generation
- Professional PDF output
- Quiz name validation and duplicate checking
- Metadata tracking for generated quizzes

### Architecture
- MVC/MVP pattern with clean separation of concerns
- Type-hinted Python 3.12+ codebase
- Modular design with extensibility points
- Configuration management with environment variables
- Local-first data storage

