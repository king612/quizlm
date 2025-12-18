# Quiz Generation Specification

## Overview

QuizLM generates **full-document cloze-deletion quizzes** that replicate entire source documents with strategic blanks inserted for key terms. This is NOT a traditional quiz with numbered questions, but rather a complete replication of the source material transformed into a study tool.

## Core Concept

### What We Generate
- **Full-text replication** of source documents with blanks inserted throughout
- **Multi-page quizzes** that preserve the structure and flow of the original
- **Cloze deletion format** where key terms are replaced with blanks (underscores)
- **Comprehensive coverage** - all content is included, not just selected highlights

### What We Don't Generate
- ❌ Short, numbered question lists (e.g., "1. The ___ is the powerhouse")
- ❌ Summaries or condensed versions of content
- ❌ Multiple choice or other question formats
- ❌ Selective excerpts from the source material

## Generation Strategy (v3.0 - 2-Phase Architecture)

### Two-Phase Approach

QuizLM v3.0 uses a **hybrid approach** that separates semantic reasoning (where LLMs excel) from precise formatting (where code excels):

**Phase 1: LLM Semantic Analysis**
- LLM analyzes source text for educational value
- Identifies which words/terms should be tested
- Returns structured list of words with importance scores
- No formatting involved - pure content analysis

**Phase 2: Local Quiz Building**
- Python code builds quiz with selected words
- Deterministic blank generation with exact proportions
- GUARANTEED: Exactly 2 underscores per missing letter
- Precise hint letter control based on difficulty
- Reliable, testable, and debuggable

### Document Processing

1. **Input**: Accept source documents in various formats (PDF, DOCX, TXT, images)
2. **Text Extraction**: Extract all text content while preserving structure
3. **Phase 1 - Word Selection**: LLM identifies educationally valuable terms
4. **Phase 2 - Quiz Assembly**: Local code builds quiz with precise formatting

### Blanking Strategy

Words are selected by the LLM based on educational value, then formatted locally:

#### Easy (15-20% blanking)
- Fewer blanks overall - focus on most critical terminology
- Show 40-50% of each word as hints (e.g., "mito______________" for "mitochondria")
- Example: "The mito______________ is the powe____________ of the cell"
- Hint algorithm: max(1, min(4, length * 45%)) letters shown

#### Medium (25-35% blanking)
- Moderate number of blanks - key terms and supporting concepts
- Show 25-30% of each word as hints (e.g., "mi__________________" for "mitochondria")
- Example: "The mi____________________ is the po________________ of the ce______"
- Hint algorithm: max(1, min(3, length * 27%)) letters shown

#### Hard (40-50% blanking)
- Aggressive blanking - most key terms blanked
- Show first letter only (e.g., "m________________________" for "mitochondria")
- Example: "The m________________________ is the p__________________ of the c______"
- Hint algorithm: 1 letter shown for most words

### What Gets Blanked

**Always Blank:**
- ✓ Technical terms and specialized vocabulary
- ✓ Key concepts and important nouns
- ✓ Significant verbs and descriptive adjectives
- ✓ Names of people, places, processes, theories
- ✓ Numbers and quantities (when semantically meaningful)
- ✓ Domain-specific terminology

**Never Blank:**
- ✗ Articles (a, an, the)
- ✗ Common prepositions (in, on, at, to, from)
- ✗ Common conjunctions (and, but, or, so)
- ✗ Structural/grammatical words with no semantic content
- ✗ Headings or section titles (preserve for navigation)

## Output Format

### JSON Structure

The LLM returns a JSON object with this structure:

```json
{
  "quiz_title": "Title from source document",
  "paragraphs": [
    {
      "text": "Full paragraph with ___ for blanked words. All original content preserved.",
      "section_heading": "Optional section/chapter heading"
    },
    {
      "text": "Next paragraph continues the document...",
      "section_heading": null
    }
  ],
  "answer_key": [
    {
      "answer": "blanked_word",
      "context": "brief surrounding text for context"
    },
    {
      "answer": "next_blanked_word",
      "context": "more context"
    }
  ]
}
```

### Key Principles

1. **Paragraphs array contains ALL source content** - nothing is omitted
2. **Order is preserved** - paragraphs appear in original document order
3. **Structure is maintained** - headings, sections, and flow are kept intact
4. **Answer key is sequential** - answers appear in order of blanks in text

## PDF Layout Options

### Full Page Layout (DEFAULT)

**Quiz Section:**
- Full-width text with blanks throughout
- Multi-page document preserving original flow
- Section headings maintained for structure
- Natural reading experience like the original document

**Answer Key Section:**
- Separate pages at the end
- Flowing paragraph format with answers separated by 4 spaces
- NO numbered list, NO context or supplemental info
- Just the answer words in order, easy to scan
- Example: "mitochondria    powerhouse    cell    energy    ATP    ..."

**Use Case:** Best for comprehensive study, take-home quizzes, self-paced learning

### Split Page Layout

**Layout:**
- Page divided vertically down the middle
- Left side: Quiz text with blanks
- Right side: Corresponding answers aligned by position

**Advantages:**
- Immediate answer checking
- Useful for quick review
- Less page flipping

**Limitations:**
- Less space per side
- May require more pages overall
- Better for shorter documents

**Use Case:** Quick review sessions, flash-card style study

## Phase 1: LLM Word Selection

### Prompt Strategy

The LLM is asked to perform **pure semantic analysis** without any formatting concerns:

1. **"IDENTIFY EDUCATIONALLY VALUABLE WORDS"** - Focus on learning value
2. **"CONSIDER PEDAGOGICAL IMPORTANCE"** - Which words test understanding?
3. **"RETURN STRUCTURED JSON"** - List of words with importance scores
4. **"NO FORMATTING REQUIRED"** - LLM doesn't generate blanks or underscores

### LLM Output Format

```json
{
  "words_to_blank": [
    {
      "word": "mitochondria",
      "importance": 0.95,
      "word_type": "key_concept",
      "first_occurrence_context": "The mitochondria is the..."
    }
  ],
  "difficulty": "Medium",
  "estimated_coverage": 0.30,
  "total_words_selected": 25
}
```

### Token Management

Much simpler than v2.x:
- LLM only returns word list (not full document)
- Typical output: 100-500 tokens (vs 2000-4000 in v2.x)
- No truncation issues - word lists are small
- Faster and cheaper API calls

## Phase 2: Local Quiz Building

### Quiz Builder Algorithm

Local Python code (`quiz_builder.py`) handles all formatting:

1. **Word Matching**
   - Find all occurrences of selected words in source text
   - Case-insensitive matching with case preservation
   - Handle word boundaries and punctuation correctly

2. **Blank Generation**
   - Calculate hint letters based on difficulty algorithm
   - Generate EXACTLY 2 underscores per missing letter
   - Example: "mitochondria" (13 letters) with 4 hint → "mito__________________" (4 + 18 underscores)

3. **Text Assembly**
   - Replace words with blanks in source text
   - Preserve all formatting, punctuation, spacing
   - Track positions to avoid overlapping blanks
   - Limit replacements (max 2 occurrences per word)

4. **Answer Key Generation**
   - Sequential list of blanked words
   - Include metadata (importance, word type, position)

### Hint Letter Algorithm

```python
def calculate_hint_count(word_length, difficulty):
    if difficulty == "Easy":
        return max(1, min(4, word_length * 45 // 100))
    elif difficulty == "Medium":
        return max(1, min(3, word_length * 27 // 100))
    else:  # Hard
        return 1
```

### Advantages of v3.0 Architecture

1. **Deterministic Output** - Always exactly 2 underscores per letter
2. **Fast Iteration** - Change algorithms without LLM calls
3. **Cheaper** - Simpler prompts, smaller outputs
4. **Debuggable** - Fix formatting in code, not prompts
5. **Testable** - Unit test blank generation
6. **Reliable** - No more inconsistent LLM formatting

## Implementation Details

### New Components (v3.0)

1. **`logic/word_selector.py`** (NEW)
   - Phase 1: LLM-based word selection
   - Simple prompt focused on semantic analysis
   - Returns JSON with word list and importance scores

2. **`logic/quiz_builder.py`** (NEW)
   - Phase 2: Deterministic quiz assembly
   - Precise blank generation with configurable hints
   - Text processing and answer key formatting

3. **`logic/quiz_generator.py`** (UPDATED)
   - Orchestrates 2-phase workflow
   - Calls word_selector, then quiz_builder
   - Converts result to PDF-ready format

4. **`logic/pdf_generator.py`** (UNCHANGED)
   - Same rendering logic as v2.x
   - Works with paragraphs + answer_key structure

### Removed/Deprecated

- **`logic/llm_client.py`** - Old `generate_quiz_content()` method no longer used
- **Style training** - No longer needed (formatting is deterministic)
- **VLM image analysis** - Removed (not needed for v3.0)

## Usage Examples

### Example 1: Biology Textbook Chapter (5 pages)

**Input:** PDF chapter on cellular respiration

**Output:**
- 5-8 page quiz replicating all content
- Key terms blanked: "mitochondria", "ATP", "glycolysis", etc.
- All diagrams referenced in text (descriptions blanked)
- Answer key with 50-100 blanks depending on difficulty
- Complete study guide covering entire chapter

### Example 2: History Lecture Notes (3 pages)

**Input:** Text file with lecture notes on WWI

**Output:**
- 3-4 page quiz with full note content
- Names, dates, events blanked strategically
- Section headings preserved ("Causes of WWI", "Major Battles")
- Answer key in chronological order
- Comprehensive review of all lecture material

### Example 3: Technical Documentation (15 pages)

**Input:** DOCX file with API documentation

**Output:**
- 15-20 page quiz covering all sections
- Technical terms, method names, parameters blanked
- Code examples with key elements blanked
- Structured with original documentation hierarchy
- Complete technical review document

## Future Enhancements

### Potential Improvements

1. **Chunking for Very Long Documents**
   - Split 100+ page documents into manageable sections
   - Generate multiple quiz PDFs (Part 1, Part 2, etc.)
   - Maintain answer key continuity

2. **Intelligent Difficulty Scaling**
   - Analyze document complexity
   - Auto-adjust blanking percentage
   - More blanks in repetitive sections, fewer in dense technical areas

3. **Table and Figure Handling**
   - Better support for blanking within tables
   - Image/diagram description blanking
   - Preserve formatting for complex layouts

4. **Custom Blanking Rules**
   - User-specified terms to always/never blank
   - Domain-specific dictionaries
   - Learning from training images to match style

5. **Multi-Column PDF Support**
   - Match source document layout more closely
   - Handle two-column academic papers
   - Preserve visual structure

## Configuration

### Default Settings

```python
DEFAULT_QUIZ_STYLE = "Full Page"  # Changed from "Split Page"
DEFAULT_DIFFICULTY = "Medium"
FONT_SIZE = 11  # Optimized for readability
LINE_SPACING = 14  # Points between lines
```

### Style Guidelines

From training images (when available):
- Font preferences
- Blank formatting style
- Hint patterns
- Layout preferences

## Success Criteria

A well-generated quiz should:

1. ✅ Include ALL content from source (no omissions)
2. ✅ Maintain original document structure and flow
3. ✅ Have appropriately placed blanks based on difficulty
4. ✅ Preserve readability and context
5. ✅ Provide complete, ordered answer key
6. ✅ Be suitable for comprehensive review/study
7. ✅ Feel like the original document with strategic gaps

## Version History

- **v1.0** (Initial): Numbered question-based quizzes
- **v2.0**: Full-document cloze deletion format
  - Complete document replication
  - Paragraph-based structure
  - Enhanced PDF rendering
  - Full Page as default
  - Dynamic token allocation
- **v2.1**: Handwriting-optimized format (LLM-based)
  - Attempted proportional blank sizing via LLM instructions
  - Mandatory hint letters based on difficulty
  - Simplified answer key (flowing paragraphs, 4-space separation)
  - Status: Unreliable - LLMs can't count underscores precisely
- **v3.0** (Current): 2-Phase Hybrid Architecture
  - Phase 1: LLM semantic word selection (what to blank)
  - Phase 2: Local deterministic quiz building (how to format)
  - GUARANTEED proportional blanks (exactly 2 underscores per letter)
  - Precise hint letter algorithms based on difficulty
  - Faster, cheaper, more reliable than v2.x
  - Separation of concerns: semantic reasoning vs. formatting

---

**Document Version:** 3.0
**Last Updated:** December 18, 2024
**Status:** Active Implementation
