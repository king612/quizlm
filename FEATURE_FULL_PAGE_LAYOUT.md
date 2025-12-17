# Full Page Quiz Layout Feature

**Version:** 1.1.0
**Date:** December 16, 2025
**Status:** ✅ Implemented

## Overview

QuizLM now supports two quiz layout styles to match different handwritten quiz formats:

1. **Split Page** (original) - Quiz on left, answers on right
2. **Full Page** (new) - Quiz uses full width, answers on separate pages

## UI Changes

### New Quiz Layout Selector

Added to Generate Mode below the Difficulty selector:

```
┌─────────────────────────────────┐
│  Quiz Layout:                   │
│  [Split Page] [Full Page]       │
│                                 │
│  Split: Quiz|Answers side-by-side│
│  Full: Answers on separate pages │
└─────────────────────────────────┘
```

**Location:** Right panel in Generate Mode, between Difficulty and Status sections

**Default:** Split Page (maintains backward compatibility)

## Layout Comparison

### Split Page Layout (Original)

```
┌─────────────────────────────────────┐
│  Quiz Title                         │
├──────────────────┬──────────────────┤
│  QUIZ            │  ANSWERS         │
├──────────────────┼──────────────────┤
│ 1. The ____ is   │  mitochondria    │
│    the powerhouse│                  │
│    of the cell.  │                  │
│                  │                  │
│ 2. DNA stands for│  deoxyribonucleic│
│    ____________  │  acid            │
│    _____.        │                  │
└──────────────────┴──────────────────┘
```

**Use Cases:**
- Traditional quiz format
- Side-by-side review while studying
- Compact format (both on same page)

### Full Page Layout (New)

**Quiz Pages:**
```
┌─────────────────────────────────────┐
│  Quiz Title                         │
│  QUIZ                               │
├─────────────────────────────────────┤
│  1. The ____ is the powerhouse of   │
│     the cell.                       │
│                                     │
│  2. DNA stands for ____________     │
│     _____.                          │
│                                     │
│  3. Photosynthesis occurs in the    │
│     __________.                     │
│                                     │
│  ... more questions ...             │
└─────────────────────────────────────┘
```

**Answer Key Pages:**
```
┌─────────────────────────────────────┐
│  ANSWER KEY                         │
├─────────────────────────────────────┤
│  1.    mitochondria                 │
│                                     │
│  2.    deoxyribonucleic acid        │
│                                     │
│  3.    chloroplasts                 │
│                                     │
│  ... more answers ...               │
└─────────────────────────────────────┘
```

**Use Cases:**
- Longer quiz questions
- Figure-based or diagram quizzes
- More writing space needed
- Matches handwritten full-page style
- Easier grading (separate answer sheet)

## Answer Key Formatting

### Split Page
- Answers appear directly next to corresponding questions
- Vertically aligned for easy reference

### Full Page
- Answers listed sequentially on separate pages
- Format: `"1.    answer    "` (4 spaces padding each side)
- Padding improves readability when grading
- Each answer on separate line with spacing

## Technical Implementation

### Code Changes

#### 1. UI Layer (`ui/main_window.py`)

**Added Quiz Style Selector:**
```python
# Quiz style selector
self.quiz_style_var = ctk.StringVar(value="Split Page")
style_selector = ctk.CTkSegmentedButton(
    style_frame,
    values=["Split Page", "Full Page"],
    variable=self.quiz_style_var
)
```

**Pass Style to Generator:**
```python
output_path = self.quiz_generator.generate_quiz(
    quiz_name=quiz_name,
    source_file=self.current_source_file,
    source_text=text_content if text_content else None,
    difficulty=difficulty,
    quiz_style=quiz_style  # NEW
)
```

#### 2. Business Logic (`logic/quiz_generator.py`)

**Updated Method Signature:**
```python
def generate_quiz(
    self,
    quiz_name: str,
    source_file: Optional[Path] = None,
    source_text: Optional[str] = None,
    difficulty: str = "Medium",
    quiz_style: str = "Split Page"  # NEW
) -> Path:
```

**Pass to PDF Generator:**
```python
self.pdf_generator.create_quiz_pdf(
    quiz_data=quiz_data,
    output_path=output_path,
    quiz_name=quiz_name,
    quiz_style=quiz_style  # NEW
)
```

**Save in Metadata:**
```python
metadata = {
    "name": quiz_name,
    "difficulty": difficulty,
    "quiz_style": quiz_style,  # NEW
    "generated_at": datetime.now().isoformat(),
    "num_questions": len(quiz_data.get("questions", [])),
}
```

#### 3. PDF Generation (`logic/pdf_generator.py`)

**Refactored Architecture:**
```python
def create_quiz_pdf(self, quiz_data, output_path, quiz_name, quiz_style="Split Page"):
    if quiz_style == "Full Page":
        self._create_full_page_quiz(quiz_data, output_path, quiz_name)
    else:
        self._create_split_page_quiz(quiz_data, output_path, quiz_name)
```

**New Method: `_create_full_page_quiz()`**
- Quiz questions use full page width
- Start answer key on new page
- Format answers with padding for readability

**Refactored: `_create_split_page_quiz()`**
- Original logic extracted into separate method
- Maintains exact same behavior as before

## PRD Updates

### New Requirements

**REQ-3.3:** Provide quiz layout selector: Split Page (default), Full Page

**REQ-3.6-FP:** Full Page quiz section requirements

**REQ-3.6-FP-ANSWERS:** Full Page answer key requirements

### Updated User Story

**US-7:** Choose Quiz Layout Style

## Training Considerations

### Training Images

When training the system, include both layout types in your handwritten examples:

1. **Split Page Examples:** Traditional side-by-side format
2. **Full Page Examples:** Full-width quiz with separate answer sheets

The VLM will analyze both styles and the system will generate accordingly based on user selection.

### Style Analysis

The style info JSON now captures layout preferences:

```json
{
  "format": "two-column",  // or "full-page"
  "layout_patterns": {
    "split_page": {...},
    "full_page": {...}
  }
}
```

## Benefits

### For Users
✅ Matches multiple handwritten quiz styles
✅ Better for longer content (full-page)
✅ Easier grading with separate answer sheets
✅ Traditional side-by-side still available
✅ Flexible to different use cases

### For Development
✅ Clean separation of PDF generation logic
✅ Easy to add more layout styles in future
✅ Backward compatible (default to Split Page)
✅ Metadata tracks layout choice

## Future Enhancements

Potential additions for future versions:

- **Three-column layout** (question, answer, notes)
- **Multiple choice format** (A, B, C, D options)
- **Mixed layouts** (some pages split, some full)
- **Custom spacing** (user-defined line spacing)
- **Answer key variations** (with/without numbers, grouped by topic)

## Testing Scenarios

### Test Case 1: Split Page Generation
1. Select "Split Page" layout
2. Generate quiz with 10 questions
3. Verify two-column layout
4. Verify answers aligned with questions

### Test Case 2: Full Page Generation
1. Select "Full Page" layout
2. Generate quiz with 15 questions
3. Verify full-width quiz section
4. Verify separate answer key pages
5. Verify answer padding format

### Test Case 3: Backward Compatibility
1. Don't select any layout (use default)
2. Verify Split Page is used
3. Verify existing quizzes still work

### Test Case 4: Metadata Tracking
1. Generate one quiz with each layout
2. Check metadata JSON files
3. Verify `quiz_style` field is saved correctly

## Migration Notes

### Existing Users
- No breaking changes
- All existing quizzes continue to work
- Default layout is Split Page (original behavior)
- No action required

### New Users
- Can choose layout based on handwritten examples
- Train with both layout types for flexibility
- Select appropriate layout per quiz

## Documentation Updates

All documentation has been updated:

✅ **README.md** - Added layout options to Generate Mode section
✅ **QUICKSTART.md** - Added layout selector to workflow
✅ **START_HERE.md** - Updated key features list
✅ **PRD.md** - Added requirements and user story
✅ **CHANGELOG.md** - Documented changes in v1.1.0

## Summary

The Full Page Layout feature provides users with flexibility to match different handwritten quiz styles. The implementation is clean, maintainable, and backward compatible, with comprehensive documentation updates.

**Key Achievement:** Users can now generate quizzes matching both traditional side-by-side formats and full-page formats with separate answer keys, accommodating different learning and grading preferences.

---

**Implementation Status:** ✅ Complete
**Code Quality:** ✅ No linter errors
**Documentation:** ✅ Updated
**Testing:** Ready for user testing

