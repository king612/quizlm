# Product Requirements Document (PRD)

## Document Information
- **Project Name:** QuizLM
- **Version:** 1.0
- **Last Updated:** 12/12/25
- **Author:** John King
- **Status:** MVP In Development

---

## 1. Executive Summary

QuizLM is a local-only desktop application that generates fill-in-the-blank quizzes from source documents (text, images, PDFs, MS Word files) with varying difficulty levels. The application uses modern Vision-Language Models (VLMs) to analyze handwritten quiz examples and generate new quizzes matching that style in PDF format.

---

## 2. Problem Statement

### Current State
Creating quiz sheets by hand is highly effective for learning but extremely time-consuming.

### Desired State
Drag and drop files to automatically generate fill-in-the-blank PDF quiz sheets that follow the style of legacy handwritten quizzes.

### Why Now?
Need to accelerate learning speed by rapidly creating new, high-quality quizzes.

---

## 3. Goals & Success Metrics

### Primary Goals
1. Generate educationally valuable fill-in-the-blank quizzes with user-selectable difficulty levels (Easy, Medium, Hard)
2. Match the style and format of handwritten quiz examples through VLM analysis
3. Produce quiz sheets with answer keys in PDF format
4. Provide a simple UI to manage style learning and quiz generation

### Success Metrics
- **Primary Metric:** Successfully analyze handwritten quiz images and generate new quizzes that match the format, style, and educational quality of the examples
- **Quality Metric:** Generated quizzes effectively test key concepts while avoiding meaningless blanks
- **Usability Metric:** End-to-end quiz generation in under 60 seconds

---

## 4. User Stories & Use Cases

### Primary Persona
**Self-Directed Learner**
- **Pain Point:** Handwritten quiz sheets are highly effective but time-consuming to create
- **Need:** Automated quiz generation from any learning material while maintaining personal quiz style
- **Goal:** Accelerate learning through rapid creation of high-quality study materials

### User Stories

#### US-1: Generate Quiz from Source Material
**As a** learner
**I want to** add a file or paste text to generate a quiz
**So that** I can quickly create study materials from any content

#### US-2: Name and Organize Quizzes
**As a** learner
**I want to** uniquely name each quiz
**So that** I can organize and identify my quizzes easily

#### US-3: View Existing Quizzes
**As a** learner
**I want to** see a list of my generated quizzes
**So that** I can access and print them at any time

#### US-4: Analyze Quiz Style
**As a** learner
**I want to** train the system on my handwritten quiz examples
**So that** generated quizzes match my preferred format and style

#### US-5: Switch Modes
**As a** learner
**I want to** easily switch between Training Mode and Generate Mode
**So that** I can manage my quiz examples and generate new quizzes seamlessly

#### US-6: Control Quiz Difficulty
**As a** learner
**I want to** select difficulty level (Easy, Medium, Hard) when generating
**So that** quizzes match my current learning needs and challenge level

#### US-7: Choose Quiz Layout Style
**As a** learner
**I want to** select between Split Page (side-by-side) or Full Page layout
**So that** generated quizzes match the format of my handwritten examples

---

## 5. Functional Requirements

### Core Features

#### Feature 1: Style Analysis (Training Mode)
**Description:** Analyze handwritten quiz images to extract formatting and style patterns

**Requirements:**
- **REQ-1.1:** Use Vision-Language Model (Claude Vision or GPT-4 Vision) to analyze quiz style
- **REQ-1.2:** Accept training images via upload or drag-and-drop
- **REQ-1.3:** Require unique names for training images, checking for duplicates
- **REQ-1.4:** Store training images in dedicated folder (`data/training_images/`)
- **REQ-1.5:** Provide UI button to analyze/re-analyze all training images
- **REQ-1.6:** Backup existing style data before re-analysis
- **REQ-1.7:** Instruct VLM to ignore annotations like asterisks, checkmarks, or smiley faces
- **REQ-1.8:** Treat all training examples as Medium difficulty baseline

**Implementation:**
- VLM analyzes each image to extract: layout format, blank formatting, hint patterns, word selection rules
- Aggregate analyses into unified style profile stored as JSON
- Style profile used as context for quiz generation

#### Feature 2: Source Document Processing
**Description:** Accept and process various document formats for quiz generation

**Requirements:**
- **REQ-2.1:** Accept source material via:
  - Text pasted into textbox
  - File upload or drag-and-drop
  - Images with text, tables, or figures
- **REQ-2.2:** Support file types:
  - PDF (`.pdf`)
  - Word documents (`.docx`)
  - Plain text (`.txt`)
  - Images (`.png`, `.jpg`, `.jpeg`)
- **REQ-2.3:** Require unique names for quizzes, checking for duplicates
- **REQ-2.4:** Extract text content from all supported formats:
  - PDF: Use PyPDF2 for text extraction
  - Word: Use python-docx for text extraction
  - Images: Use pytesseract OCR for text recognition
  - Text: Direct read
- **REQ-2.5:** Optionally save source documents to `data/source_documents/`
- **REQ-2.6:** Warn user before quitting with unsaved changes

#### Feature 3: Quiz Generation
**Description:** Generate fill-in-the-blank quizzes from source material in PDF format

**Requirements:**
- **REQ-3.1:** Generate quiz via UI button after providing source material
- **REQ-3.2:** Provide difficulty selector: Easy, Medium (default), Hard
- **REQ-3.3:** Provide quiz layout selector: Split Page (default), Full Page
  - **Split Page:** Two-column layout with quiz on left, answers on right (aligned vertically)
  - **Full Page:** Quiz takes full page width, answer key on separate pages at end
- **REQ-3.4:** Generate PDF output saved to `data/quizzes/` folder
- **REQ-3.5:** *(Future)* Display PDF preview in application

**Split Page Layout Requirements:**
- **REQ-3.6-SP:** Use two-column layout:
  - Faint vertical center line
  - Left column: Quiz with blanks
  - Right column: Answers (vertically aligned)

**Full Page Layout Requirements:**
- **REQ-3.6-FP:** Quiz section:
  - Quiz questions use full page width
  - Questions numbered sequentially
  - Normal pagination when needed
- **REQ-3.6-FP-ANSWERS:** Answer key section:
  - Answer key starts on new page after all quiz questions
  - Title: "ANSWER KEY" at top of page
  - Format: "1.    answer    " (4 spaces padding on each side for readability)
  - Answer key continues on additional pages if needed

**General PDF Formatting:**
- **REQ-3.7:** PDF formatting:
  - Font: Helvetica, 12pt (changed from Verdana for better compatibility)
  - Narrow margins (0.5 inch)
  - Clean, readable layout
- **REQ-3.8:** Blank formatting:
  - Replace selected words with underscores matching word length
  - Optionally provide hint letters (first/last characters)
  - Hint letters reduce underscore count to preserve length
- **REQ-3.9:** Difficulty adjustment:
  - **Easy:** Fewer blanks (30-40% of key words), more hints (1-2 starting letters)
  - **Medium:** Moderate blanks (50-60%), occasional hints (first letter sometimes)
  - **Hard:** More blanks (70-80%), minimal/no hints
- **REQ-3.10:** Word selection rules:
  - **Never blank:** Articles (a, an, the), prepositions, conjunctions, common filler words, headings
  - **Prioritize blanking:** Nouns with semantic meaning, key concepts, technical terms, important verbs/adjectives
  - Focus on educationally valuable content
- **REQ-3.11:** *(Stretch Goal)* For diagram images: Generate quiz and answer key on separate pages

## 6. Technical Architecture

### Technology Stack
- **Language:** Python 3.12+
- **UI Framework:** CustomTkinter (modern Tkinter with dark mode)
- **LLM Provider:** Anthropic Claude (primary), OpenAI GPT-4 (fallback)
- **Document Processing:** PyPDF2, python-docx, pytesseract (OCR)
- **PDF Generation:** ReportLab
- **Architecture Pattern:** MVC/MVP (UI separated from business logic)

### ML Model Strategy
**Approach:** Prompt-engineering with Vision-Language Models (No traditional training)

**Why VLM approach over fine-tuning:**
1. No training infrastructure required
2. Excellent few-shot learning from examples
3. Superior reasoning about document content and context
4. Faster iteration and easier customization
5. Handles both vision (analyzing handwritten quizzes) and text (generating new quizzes)

**Implementation:**
1. **Style Analysis Phase:** VLM analyzes handwritten quiz images to extract patterns
2. **Style Storage:** Extracted patterns saved as JSON configuration
3. **Generation Phase:** LLM uses style config + source material to generate quiz content
4. **Rendering Phase:** Python/ReportLab creates PDF with proper formatting

### Data Flow
```
Training Mode:
  Handwritten Images → VLM Analysis → Style JSON → Storage

Generation Mode:
  Source Document → Text Extraction → LLM + Style Context → Quiz JSON → PDF Rendering → Output
```

## 7. MVP Scope

### Included in MVP
✅ CustomTkinter UI with mode switching
✅ Training image upload and management
✅ Style analysis using Claude Vision or GPT-4 Vision
✅ Support for text, PDF, DOCX, image inputs
✅ Three difficulty levels
✅ Two quiz layout options: Split Page and Full Page
✅ PDF generation with split-page (side-by-side) or full-page layouts
✅ Quiz name validation and duplicate checking
✅ View existing quizzes list

### Post-MVP Features
🔮 PDF preview widget in app
🔮 Batch quiz generation
🔮 Quiz templates/presets
🔮 Advanced style customization UI
🔮 Diagram/figure quiz support
🔮 Export to additional formats

## 8. Success Criteria

**MVP is successful when:**
1. Users can analyze 3-5 handwritten quiz images
2. System generates quizzes matching the handwritten style
3. Generated quizzes are educationally valuable (test key concepts)
4. Difficulty levels produce noticeable differences
5. PDF output is professional and print-ready
6. End-to-end workflow takes < 60 seconds

## 9. Open Questions & Risks

### Risks
- **API Costs:** VLM APIs charge per image/request (mitigated by efficient prompting)
- **OCR Accuracy:** Image-to-text may have errors (user can edit extracted text)
- **Style Consistency:** Limited training examples may not capture all nuances

### Future Considerations
- Local LLM option for privacy/offline use (Ollama integration)
- Fine-tuning option for users with many examples
- Collaborative quiz sharing (optional cloud sync)
