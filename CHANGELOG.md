# QuizLM Changelog

All notable changes to this project will be documented in this file.

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

