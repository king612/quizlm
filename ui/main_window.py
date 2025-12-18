"""
Main application window for QuizLM
Provides UI for training mode and quiz generation mode
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Dict, Optional
from logic.quiz_generator import QuizGenerator
from logic.model_trainer import ModelTrainer
from logic.document_processor import DocumentProcessor
from config import Config


class ErrorDialog(ctk.CTkToplevel):
    """Custom error dialog with copy-to-clipboard functionality"""

    def __init__(self, parent, title: str, message: str):
        super().__init__(parent)

        self.title(title)
        self.geometry("600x400")
        self.resizable(True, True)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title with error icon
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 10))

        error_label = ctk.CTkLabel(
            title_frame,
            text=f"❌ {title}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ff6b6b"
        )
        error_label.pack(anchor="w")

        # Error message in scrollable textbox
        self.textbox = ctk.CTkTextbox(
            main_frame,
            wrap="word",
            font=ctk.CTkFont(size=12)
        )
        self.textbox.pack(fill="both", expand=True, pady=(0, 10))
        self.textbox.insert("1.0", message)
        self.textbox.configure(state="disabled")  # Read-only

        # Button frame
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")

        # Copy button
        copy_btn = ctk.CTkButton(
            button_frame,
            text="📋 Copy to Clipboard",
            command=lambda: self._copy_to_clipboard(message),
            width=150,
            fg_color="#4a9eff",
            hover_color="#3a7edf"
        )
        copy_btn.pack(side="left", padx=(0, 10))

        # OK button
        ok_btn = ctk.CTkButton(
            button_frame,
            text="OK",
            command=self.destroy,
            width=100
        )
        ok_btn.pack(side="right")

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard"""
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()

        # Show brief confirmation
        messagebox.showinfo("Copied", "Error message copied to clipboard!", parent=self)


class MainWindow:
    """Main application window with training and generation modes"""

    def __init__(self, proxies: Optional[Dict] = None):
        """Initialize the main window"""
        self.config = Config()
        self.quiz_generator = QuizGenerator(self.config, proxies=proxies)
        self.model_trainer = ModelTrainer(self.config, proxies=proxies)
        self.doc_processor = DocumentProcessor(self.config)

        # Initialize CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("QuizLM - Quiz Generator")

        # Set window size
        window_width = 1000
        window_height = 700

        # Calculate center position
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)

        # Set geometry with centered position
        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

        # Application state
        self.current_mode = "generate"  # "generate" or "train"
        self.current_source_file: Optional[Path] = None
        self.unsaved_changes = False

        # Setup UI
        self._setup_ui()
        self._bind_events()

        # Bring window to front
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        self.root.focus_force()

    def _setup_ui(self):
        """Setup the user interface"""
        # Main container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header with mode toggle
        self._setup_header()

        # Content area (changes based on mode)
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Setup initial mode (Generate)
        self._setup_generate_mode()

    def _setup_header(self):
        """Setup header with mode toggle"""
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 0))

        # Title
        title = ctk.CTkLabel(
            header_frame,
            text="QuizLM",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left", padx=10)

        # Mode toggle
        self.mode_var = ctk.StringVar(value="Generate Mode")
        mode_toggle = ctk.CTkSegmentedButton(
            header_frame,
            values=["Generate Mode", "Training Mode"],
            command=self._on_mode_change,
            variable=self.mode_var
        )
        mode_toggle.pack(side="right", padx=10)

    def _setup_generate_mode(self):
        """Setup UI for quiz generation mode"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Left panel - Input
        left_panel = ctk.CTkFrame(self.content_frame)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Input section
        input_label = ctk.CTkLabel(
            left_panel,
            text="Source Material",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        input_label.pack(pady=(10, 5), padx=10, anchor="w")

        # File upload button
        upload_btn = ctk.CTkButton(
            left_panel,
            text="📁 Upload File (PDF, DOCX, Image, TXT)",
            command=self._upload_source_file,
            height=40
        )
        upload_btn.pack(pady=5, padx=10, fill="x")

        # Or text input
        or_label = ctk.CTkLabel(left_panel, text="— or paste text —")
        or_label.pack(pady=5)

        # Text input area
        self.text_input = ctk.CTkTextbox(left_panel, height=300)
        self.text_input.pack(pady=5, padx=10, fill="both", expand=True)

        # Quiz name input
        name_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        name_frame.pack(pady=10, padx=10, fill="x")

        name_label = ctk.CTkLabel(name_frame, text="Quiz Name:")
        name_label.pack(side="left", padx=(0, 10))

        self.quiz_name_entry = ctk.CTkEntry(name_frame, placeholder_text="my-quiz")
        self.quiz_name_entry.pack(side="left", fill="x", expand=True)

        # Right panel - Settings and Actions
        right_panel = ctk.CTkFrame(self.content_frame)
        right_panel.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # Settings section
        settings_label = ctk.CTkLabel(
            right_panel,
            text="Quiz Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        settings_label.pack(pady=(10, 5), padx=10, anchor="w")

        # Difficulty selector
        diff_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        diff_frame.pack(pady=10, padx=10, fill="x")

        diff_label = ctk.CTkLabel(diff_frame, text="Difficulty:")
        diff_label.pack(anchor="w", pady=(0, 5))

        self.difficulty_var = ctk.StringVar(value="Medium")
        difficulty_selector = ctk.CTkSegmentedButton(
            diff_frame,
            values=["Easy", "Medium", "Hard"],
            variable=self.difficulty_var
        )
        difficulty_selector.pack(fill="x")

        # Quiz style selector
        style_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        style_frame.pack(pady=10, padx=10, fill="x")

        style_label = ctk.CTkLabel(style_frame, text="Quiz Layout:")
        style_label.pack(anchor="w", pady=(0, 5))

        self.quiz_style_var = ctk.StringVar(value="Full Page")
        style_selector = ctk.CTkSegmentedButton(
            style_frame,
            values=["Full Page", "Split Page"],
            variable=self.quiz_style_var
        )
        style_selector.pack(fill="x")

        # Help text for style
        style_help = ctk.CTkLabel(
            style_frame,
            text="Split: Quiz|Answers side-by-side\nFull: Answers on separate pages",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        style_help.pack(anchor="w", pady=(5, 0))

        # Status section
        status_frame = ctk.CTkFrame(right_panel)
        status_frame.pack(pady=20, padx=10, fill="x")

        status_title = ctk.CTkLabel(
            status_frame,
            text="Status",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        status_title.pack(pady=5, padx=10, anchor="w")

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready to generate quiz",
            wraplength=300
        )
        self.status_label.pack(pady=5, padx=10)

        # Generate button
        self.generate_btn = ctk.CTkButton(
            right_panel,
            text="🎯 Generate Quiz",
            command=self._generate_quiz,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#2b7a0b",
            hover_color="#1f5808"
        )
        self.generate_btn.pack(pady=20, padx=10, fill="x")

        # View existing quizzes
        view_btn = ctk.CTkButton(
            right_panel,
            text="📚 View Existing Quizzes",
            command=self._view_existing_quizzes,
            height=40
        )
        view_btn.pack(pady=5, padx=10, fill="x")

    def _setup_training_mode(self):
        """Setup UI for model training mode"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Main training panel
        train_label = ctk.CTkLabel(
            self.content_frame,
            text="Model Training",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        train_label.pack(pady=(20, 10))

        # Instructions
        instructions = ctk.CTkLabel(
            self.content_frame,
            text="Upload handwritten quiz images or PDFs to train the model.\n"
                 "The model will learn your quiz style and format.\n"
                 "PDFs will be processed page by page.",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        instructions.pack(pady=10)

        # Training images list
        list_frame = ctk.CTkFrame(self.content_frame)
        list_frame.pack(pady=20, padx=20, fill="both", expand=True)

        list_title = ctk.CTkLabel(
            list_frame,
            text="Training Images",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        list_title.pack(pady=10, padx=10, anchor="w")

        # Scrollable frame for training images
        self.training_images_frame = ctk.CTkScrollableFrame(list_frame)
        self.training_images_frame.pack(pady=5, padx=10, fill="both", expand=True)

        self._refresh_training_images_list()

        # Action buttons
        btn_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        btn_frame.pack(pady=20, padx=20, fill="x")

        add_btn = ctk.CTkButton(
            btn_frame,
            text="➕ Add Training Image/PDF",
            command=self._add_training_image,
            height=40
        )
        add_btn.pack(side="left", padx=5, expand=True, fill="x")

        train_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Train Model",
            command=self._train_model,
            height=40,
            fg_color="#2b7a0b",
            hover_color="#1f5808"
        )
        train_btn.pack(side="left", padx=5, expand=True, fill="x")

    def _on_mode_change(self, value: str):
        """Handle mode toggle change"""
        if value == "Generate Mode":
            self.current_mode = "generate"
            self._setup_generate_mode()
        else:
            self.current_mode = "train"
            self._setup_training_mode()

    def _upload_source_file(self):
        """Handle source file upload"""
        filename = filedialog.askopenfilename(
            title="Select Source Document",
            filetypes=[
                ("All Supported", "*.pdf *.docx *.txt *.png *.jpg *.jpeg"),
                ("PDF Files", "*.pdf"),
                ("Word Documents", "*.docx"),
                ("Text Files", "*.txt"),
                ("Images", "*.png *.jpg *.jpeg"),
                ("All Files", "*.*")
            ]
        )

        if filename:
            self.current_source_file = Path(filename)
            self.status_label.configure(
                text=f"Loaded: {self.current_source_file.name}"
            )
            self.unsaved_changes = True

    def _generate_quiz(self):
        """Generate a quiz from current source material"""
        # Get quiz name
        quiz_name = self.quiz_name_entry.get().strip()
        if not quiz_name:
            messagebox.showerror("Error", "Please enter a quiz name")
            return

        # Get source material
        text_content = self.text_input.get("1.0", "end-1c").strip()

        if not text_content and not self.current_source_file:
            messagebox.showerror("Error", "Please provide source material (text or file)")
            return

        # Get difficulty and style
        difficulty = self.difficulty_var.get()
        quiz_style = self.quiz_style_var.get()

        # Update status
        self.status_label.configure(text="Generating quiz...")
        self.generate_btn.configure(state="disabled")
        self.root.update()

        try:
            # Generate quiz
            output_path = self.quiz_generator.generate_quiz(
                quiz_name=quiz_name,
                source_file=self.current_source_file,
                source_text=text_content if text_content else None,
                difficulty=difficulty,
                quiz_style=quiz_style
            )

            self.status_label.configure(text=f"✓ Quiz generated: {output_path.name}")
            messagebox.showinfo(
                "Success",
                f"Quiz generated successfully!\n\nSaved to: {output_path}"
            )
            self.unsaved_changes = False

        except Exception as e:
            error_message = f"Failed to generate quiz:\n\n{str(e)}"
            self.status_label.configure(text=f"Error: {str(e)[:50]}...")
            ErrorDialog(self.root, "Quiz Generation Error", error_message)

        finally:
            self.generate_btn.configure(state="normal")

    def _view_existing_quizzes(self):
        """Open folder with existing quizzes"""
        quizzes_dir = self.config.quizzes_dir
        quizzes_dir.mkdir(parents=True, exist_ok=True)

        # Get list of quizzes
        quizzes = list(quizzes_dir.glob("*.pdf"))

        if not quizzes:
            messagebox.showinfo("No Quizzes", "No quizzes have been generated yet.")
            return

        # Show list dialog
        quiz_list = "\n".join([q.name for q in sorted(quizzes)])
        messagebox.showinfo(
            f"Existing Quizzes ({len(quizzes)})",
            quiz_list
        )

    def _add_training_image(self):
        """Add a new training image or PDF"""
        filename = filedialog.askopenfilename(
            title="Select Training Image or PDF",
            filetypes=[
                ("All Supported", "*.png *.jpg *.jpeg *.pdf"),
                ("Images", "*.png *.jpg *.jpeg"),
                ("PDF Files", "*.pdf"),
                ("All Files", "*.*")
            ]
        )

        if filename:
            try:
                file_path = Path(filename)
                file_type = "PDF" if file_path.suffix.lower() == '.pdf' else "image"

                # Prompt for name
                name = ctk.CTkInputDialog(
                    text=f"Enter a unique name for this training {file_type}:",
                    title=f"Training {file_type.title()} Name"
                ).get_input()

                if name:
                    self.model_trainer.add_training_image(file_path, name)
                    self._refresh_training_images_list()

                    success_msg = f"Training {file_type} added successfully!"
                    if file_type == "PDF":
                        success_msg += "\nEach page will be analyzed during training."
                    messagebox.showinfo("Success", success_msg)

            except Exception as e:
                error_message = f"Failed to add training file:\n\n{str(e)}"
                ErrorDialog(self.root, "Training File Error", error_message)

    def _train_model(self):
        """Train the model on training images"""
        try:
            self.model_trainer.train_model()
            messagebox.showinfo("Success", "Model trained successfully!")
        except Exception as e:
            error_message = f"Failed to train model:\n\n{str(e)}"
            ErrorDialog(self.root, "Model Training Error", error_message)

    def _refresh_training_images_list(self):
        """Refresh the list of training images"""
        # Clear current list
        for widget in self.training_images_frame.winfo_children():
            widget.destroy()

        # Get training images
        training_images = self.model_trainer.get_training_images()

        if not training_images:
            label = ctk.CTkLabel(
                self.training_images_frame,
                text="No training images yet. Add some to get started!",
                text_color="gray"
            )
            label.pack(pady=20)
        else:
            for img_path in training_images:
                # Use different icon for PDFs
                icon = "📑" if img_path.suffix.lower() == '.pdf' else "📄"
                img_label = ctk.CTkLabel(
                    self.training_images_frame,
                    text=f"{icon} {img_path.name}"
                )
                img_label.pack(pady=2, padx=5, anchor="w")

    def _bind_events(self):
        """Bind window events"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        """Handle window close event"""
        if self.unsaved_changes:
            result = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before quitting?"
            )
            if result is None:  # Cancel
                return
            elif result:  # Yes - save
                # TODO: Implement save logic
                pass

        self.root.quit()

    def run(self):
        """Run the application"""
        self.root.mainloop()

