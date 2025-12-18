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

## Generation Strategy

### Document Processing

1. **Input**: Accept source documents in various formats (PDF, DOCX, TXT, images)
2. **Text Extraction**: Extract all text content while preserving structure
3. **Full Replication**: Pass entire document content to LLM for blanking
4. **No Truncation**: For long documents, use full context within token limits

### Blanking Strategy

The LLM strategically blanks out terms based on difficulty level:

#### Easy (10-15% blanking)
- Fewer blanks overall
- Focus on most critical terminology
- Provide 1-2 starting letters as hints
- Example: "The m_____ is the powerhouse of the cell"

#### Medium (15-25% blanking)
- Moderate number of blanks
- Mix of key terms and supporting concepts
- Occasional first-letter hints
- Example: "The mitochondria is the p_______ of the ___"

#### Hard (25-35% blanking)
- More aggressive blanking
- Most key terms are blanked
- Minimal or no hints
- Example: "The __________ is the _________ of the ____"

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
- Numbered list of answers in order
- Optional context snippets for each answer
- Easy reference for self-checking

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

## LLM Prompt Strategy

### Critical Instructions

The prompt to the LLM emphasizes:

1. **"REPLICATE THE ENTIRE SOURCE DOCUMENT"** - Not "create questions about"
2. **"DO NOT SUMMARIZE"** - Include all content
3. **"PRESERVE STRUCTURE"** - Keep paragraphs, sections, organization
4. **"DO NOT NUMBER AS QUESTIONS"** - This is continuous text
5. **"STRATEGIC BLANKING"** - Insert blanks throughout based on difficulty

### Token Management

For long documents:
- Calculate appropriate `max_tokens` based on source length
- Use formula: `min(16000, max(4000, content_length * 2))`
- Haiku model supports up to 16k output tokens
- For very long documents (>50 pages), may need chunking or model upgrade

## Implementation Details

### Components Modified

1. **`logic/llm_client.py`**
   - Updated `generate_quiz_content()` with new comprehensive prompt
   - Dynamic token allocation based on content length
   - New JSON structure for paragraphs + answer_key

2. **`logic/pdf_generator.py`**
   - Modified `_create_full_page_quiz()` to render paragraphs sequentially
   - Modified `_create_split_page_quiz()` to handle continuous text format
   - Backward compatibility with old question format
   - Better spacing and typography (11pt font)

3. **`ui/main_window.py`**
   - Changed default quiz style from "Split Page" to "Full Page"
   - Reordered style selector to show Full Page first

4. **`logic/quiz_generator.py`**
   - Updated metadata tracking for new format
   - Changed default quiz style parameter to "Full Page"

### Backward Compatibility

The PDF generator includes fallback logic:
- If `paragraphs` key exists, use new format
- If only `questions` key exists, convert to paragraph format
- Ensures old quizzes still render correctly

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
- **v2.0** (Current): Full-document cloze deletion format
  - Complete document replication
  - Paragraph-based structure
  - Enhanced PDF rendering
  - Full Page as default
  - Dynamic token allocation

---

**Document Version:** 2.0
**Last Updated:** December 17, 2024
**Status:** Active Implementation
