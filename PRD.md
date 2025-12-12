# Product Requirements Document (PRD)

## Document Information
- **Project Name:** QuizLM
- **Version:** 1.0
- **Last Updated:** 12/12/25
- **Author:** John King
- **Status:** Draft

---

## 1. Executive Summary
A local use only application that accepts source documents in the form of raw text, images, PDF files, MS Word files and from them generates fill-in-the-blank quizzes of varying degrees of difficulty.  The application is built on a ML model that plays the role of an instructor and is trained on images of hand-written quiz sheets (and the corresponding answer keys) to generate new quizzes in PDF format in the same style as the training quiz images for new source documents not previously seen.

---

## 2. Problem Statement

### Current State
I've been making these quiz sheets by hand for years.  They are highly effective for my learnin style but are very time-consuming to construct by hand.

### Desired State
I can drag and drop a file to be used to generate a fill-in-the-blank PDF quiz sheet automatically that follows the style of my legacy hand written quizzes

### Why Now?
I have to accelerate my learning speed and create new quizzes quickly and easily

---

## 3. Goals & Success Metrics

### Primary Goals
1. Generate educationally valuable fill-in-the-blank quiz sheets with user-selectable varying degrees of difficulty
2. Generate these quiz sheets (and the corresponding answer keys) matching the style of several images of hand drawn quizes that are to be used for training
3. Produce the quiz sheets in a PDF format in an output folder
4. Provide a simple User Interface to manage the process of training the model and then creating a new quiz sheet from some inew nput object

### Success Metrics
- **Metric 1:** The model is trainable from many different scanned images of hand written sheets and can
  generate appropriate and educationally valuable quizzes following the requirements provided below.

---

## 4. User Stories & Use Cases

### Primary Personas
**Persona 1:** Interactive User
- Pain points: hand drawn quiz sheets are very time-consuming to build
- Needs: Automate this process for any given text or figure

### User Stories
Format: "As a [user type], I want [capability] so that [benefit]"

#### Story 1: New Quiz
**As a** interactive User
**I want** to add a file or paste a block of text from which to generate a quiz sheet
**So that** the application can produce a PDF file automatically in an output directory

#### Story 2: Name the quiz
**As a** ineractive User
**I want** to name a new quiz when it is created
**So that** the quiz (PDF file) has a name that does not already exist

#### Story 3: List existing quezzes
**As a** ineractive User
**I want** see a listing of existing quiz PDFs
**So that** I can print more copies at any time

#### Story 4: Train the model
**As a** ineractive User
**I want** train a local language model (perhaps a VLM?) on scanned images of hand drawn quiz sheets
**So that** a local model is built, maintained, and augmented over time with additionl hand drawn quiz images

#### Story 5: Switch between two different usage modes
**As a** ineractive User
**I want** to be able to easily switch between Training Mode and Generate Mode
**So that** I can add new training images and generate new quiz sheets from them given a new input

#### Story 6: Provide a new image and generate a new quiz
**As a** ineractive User
**I want** to be able to paste or drag and drop new source material in Generate Mode
**So that** QuizLM can generatre a new quiz sheet, display it, and save it

#### Story 6: Select the difficulty of the generated quiz
**As a** ineractive User
**I want** to have a difficulty choice when generating a new quiz of: Easy, Medium, or Hard
**So that** QuizLM can generatre a new quiz sheet with varying levels of challenge

---

## 5. Functional Requirements

### Core Features

#### Feature 1: Train the QuizLM model
**Description:** Train or retrain the model on a directory of handwritten quiz images

**Requirements:**
- REQ-1.1: Build and maintain a model of the appropriate type for the specifications in this PRD
- REQ-1.2: The applicatiion's model shall accept training documents in these forms: an image document uploaded or dragged and dropped in a landing zone
- REQ-1.3: Require the user to uniquely name the new training image, checking for duplicates
- REQ-1.4: Save the new training image in a folder of training documents
- REQ-1.5: Provide a UI feature to train or re-train the model based on all the training documents
- REQ-1.6: If the model is re-trained, keep one backup copy of the current model
- REQ-1.7: During training, instruct the modal to ignore and disregard annotations in the sample quizzes
  above blanks, such as '*', '(c)', or smiley faces.
	REQ-1.8: During training, the model should assume all training quiz images are of Medium

**Business Logic:**
```
```

#### Feature 2: Accept, store, and prepare new source documents from which quizzes shall be generated
**Requirements:**
- REQ-2.1: The applicatiion's UI shall accept new documents from which to generate a quiz in these forms:
- 1) 	text pasted into a textbox,
- 2) a document uploaded or dragged and dropped in a landing zone, and
- 3) an image 	containing any combination of text, tables, and figures
- REQ-2.2: If a new source document is provided, accept and interpret these files types:
- 1) PDF,
- 2) .docx,
- 3) raw text, and
- 4) image formats: png or jpeg
- REQ-2.3: Require the user to uniquely name the new source file, checking for duplicates
- REQ-2-4: Provide whatever conversions or interpretations are needed for the allowed file types such that
  they are necessary and sufficient for the model to "see" the source document and generate the corresponding quiz sheet.
- REQ-2.5: Prompt the user to save the new source document in a folder of source documents
- REQ-2.6: Prevent quitting the application with unsaved files unless the user explicitly approves this
  after warning them

#### Feature 3: Generate a new quiz sheet
**Requirements:**
- REQ-3.1: Provide a user input button to generate a quiz sheet by selecting a source document from the source folder
- REQ-3.2: Provide a user input choice for level of difficulty: Easy, Medium, or Hard.  Default this choice to Medium
- REQ-3.3: The model shall generate the new quiz in PDF format and store it in a quzzes folder
- REQ-3.4: Display a generated quiz in a PDF preview widget (future)
- REQ-3.5: By default, the quiz sheet should have a faint vertical line down the center of the page with the
  fill-in-the-blank quiz on the left side and the answer key on the right side where the answers align vertically
	with the quiz blanks
- REQ-3.6: The generated PDF shall have narrow margins, Verdana font, 12 pt
- REQ-3.7: The model shall build the quiz by replacing key words in the text, table, or figure as follows:
		- For each letter in a source word chosen to quiz, place an underscore in the quiz text such that
  	the quiz blank has the same length as the source word.
		- Let the model choose whather and which letters to provide as hints, such as first letter(s) or ending letter(s) according to the difficulty setting as specified in REQ-3.8
		- For each hint letter added, deduct one of the underscores to preserve overall length between source word and quiz blank
- REQ-3.8: Adjust the generated quiz according to the difficulty setting as follows:
  - Easy: choose fewer words to include in the quiz and provide more starting or ending hint letters
  - Medium: mimic the number of blanks and hint letters in the training images
  - Hard: choose more words to include in the quiz and provide fewer or no hint letters
- REQ-3-9: Regardless of difficulty setting, follow these rules for choosing words to include in the quiz (that is, to make into blanks):
  - In general, these types of words should never be quizzed (should alwasy just be shown as is): articles, transition language, prepositions, and common words that add no conceptual value
  - Easy mode: include fewer words and provide more letter hints
  - Hard mode: include more words and provide fewer letter hints
  - In all cases, prioritize words with the most semantic or conceptual meaning
  - Headings should always appear in full text (not quizzed)
- REQ-3.10: (Stretch Goal) When the souce document is a diagram image, attempt to recreate the quiz image
  with words replaced following REQ-3.6 through REQ-3.9, but do not try to put quiz and answer key side-by-side
	on the page.  Instead, generate the quiz image and the answer key image on separate pages
