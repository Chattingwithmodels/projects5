import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import threading
import os

class AIToolsPanel(ttk.Frame):
    """AI tools panel for interacting with GenAI."""
    
    def __init__(self, parent, genai_wrapper, editor_panel, status_bar=None, sandbox_manager=None):
        super().__init__(parent)
        self.parent = parent
        self.genai = genai_wrapper
        self.editor = editor_panel
        self.status_bar = status_bar
        self.sandbox = sandbox_manager
        
        # Configure the frame
        self.configure(padding=(5, 5))
        
        # Create main panel with notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_ask_tab()
        self.create_explain_tab()
        self.create_refactor_tab()
        self.create_improve_tab()
        self.create_docs_tab()
        self.create_multi_file_tab()
    
    def create_ask_tab(self):
        """Create the 'Ask AI' tab."""
        ask_frame = ttk.Frame(self.notebook, padding=(10, 10))
        self.notebook.add(ask_frame, text="Ask AI")
        
        # Instructions
        ttk.Label(
            ask_frame, 
            text="Ask a question about the current file",
            font=("Default", 10, "bold")
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # Question input
        ttk.Label(ask_frame, text="Question:").pack(anchor=tk.W, pady=(5, 0))
        self.question_input = tk.Text(ask_frame, height=3, width=40, wrap=tk.WORD)
        self.question_input.pack(fill=tk.X, expand=False, pady=(0, 10))
        
        # Submit button
        ask_btn = ttk.Button(
            ask_frame, 
            text="Ask Question", 
            command=self.ask_question
        )
        ask_btn.pack(anchor=tk.W, pady=(0, 10))
        
        # Response output
        ttk.Label(ask_frame, text="Response:").pack(anchor=tk.W, pady=(5, 0))
        self.ask_output = scrolledtext.ScrolledText(
            ask_frame, 
            height=15, 
            width=40, 
            wrap=tk.WORD, 
            state=tk.DISABLED
        )
        self.ask_output.pack(fill=tk.BOTH, expand=True)
        
        # Save to markdown button - initially disabled
        self.save_ask_btn = ttk.Button(
            ask_frame, 
            text="Save to Markdown", 
            command=self.save_ask_to_markdown,
            state=tk.DISABLED
        )
        self.save_ask_btn.pack(anchor=tk.E, pady=(5, 0))
    
    def create_explain_tab(self):
        """Create the 'Explain Code' tab."""
        explain_frame = ttk.Frame(self.notebook, padding=(10, 10))
        self.notebook.add(explain_frame, text="Explain Code")
        
        # Instructions
        ttk.Label(
            explain_frame, 
            text="Get an explanation of the current file",
            font=("Default", 10, "bold")
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # Submit button
        explain_btn = ttk.Button(
            explain_frame, 
            text="Explain Code", 
            command=self.explain_code
        )
        explain_btn.pack(anchor=tk.W, pady=(0, 10))
        
        # Response output
        ttk.Label(explain_frame, text="Explanation:").pack(anchor=tk.W, pady=(5, 0))
        self.explain_output = scrolledtext.ScrolledText(
            explain_frame, 
            height=20, 
            width=40, 
            wrap=tk.WORD, 
            state=tk.DISABLED
        )
        self.explain_output.pack(fill=tk.BOTH, expand=True)
        
        # Save to markdown button - initially disabled
        self.save_explain_btn = ttk.Button(
            explain_frame, 
            text="Save to Markdown", 
            command=self.save_explain_to_markdown,
            state=tk.DISABLED
        )
        self.save_explain_btn.pack(anchor=tk.E, pady=(5, 0))
    
    def create_refactor_tab(self):
        """Create the 'Refactor Code' tab."""
        refactor_frame = ttk.Frame(self.notebook, padding=(10, 10))
        self.notebook.add(refactor_frame, text="Refactor")
        
        # Instructions
        ttk.Label(
            refactor_frame, 
            text="Refactor the current file",
            font=("Default", 10, "bold")
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # Instruction input
        ttk.Label(refactor_frame, text="Refactoring instructions:").pack(anchor=tk.W, pady=(5, 0))
        self.refactor_input = tk.Text(refactor_frame, height=3, width=40, wrap=tk.WORD)
        self.refactor_input.pack(fill=tk.X, expand=False, pady=(0, 10))
        
        # Submit button
        refactor_btn = ttk.Button(
            refactor_frame, 
            text="Refactor Code", 
            command=self.refactor_code
        )
        refactor_btn.pack(anchor=tk.W, pady=(0, 10))
        
        # Response output
        ttk.Label(refactor_frame, text="Refactored code:").pack(anchor=tk.W, pady=(5, 0))
        self.refactor_output = scrolledtext.ScrolledText(
            refactor_frame, 
            height=15, 
            width=40, 
            wrap=tk.WORD, 
            state=tk.DISABLED
        )
        self.refactor_output.pack(fill=tk.BOTH, expand=True)
        
        # Apply button - initially disabled
        self.apply_refactor_btn = ttk.Button(
            refactor_frame, 
            text="Apply Changes", 
            command=self.apply_refactored_code,
            state=tk.DISABLED
        )
        self.apply_refactor_btn.pack(anchor=tk.E, pady=(5, 0))
    
    def create_improve_tab(self):
        """Create the 'Improve Code' tab."""
        improve_frame = ttk.Frame(self.notebook, padding=(10, 10))
        self.notebook.add(improve_frame, text="Improve")
        
        # Instructions
        ttk.Label(
            improve_frame, 
            text="Get suggestions to improve the current file",
            font=("Default", 10, "bold")
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # Submit button
        improve_btn = ttk.Button(
            improve_frame, 
            text="Suggest Improvements", 
            command=self.suggest_improvements
        )
        improve_btn.pack(anchor=tk.W, pady=(0, 10))
        
        # Response output
        ttk.Label(improve_frame, text="Suggestions:").pack(anchor=tk.W, pady=(5, 0))
        self.improve_output = scrolledtext.ScrolledText(
            improve_frame, 
            height=20, 
            width=40, 
            wrap=tk.WORD, 
            state=tk.DISABLED
        )
        self.improve_output.pack(fill=tk.BOTH, expand=True)
        
        # Apply button - initially disabled
        self.apply_improve_btn = ttk.Button(
            improve_frame, 
            text="Apply Improvements", 
            command=self.apply_improvements,
            state=tk.DISABLED
        )
        self.apply_improve_btn.pack(anchor=tk.E, pady=(5, 0))
    
    def create_docs_tab(self):
        """Create the 'Generate Docs' tab."""
        docs_frame = ttk.Frame(self.notebook, padding=(10, 10))
        self.notebook.add(docs_frame, text="Generate Docs")
        
        # Instructions
        ttk.Label(
            docs_frame, 
            text="Generate documentation for the current file",
            font=("Default", 10, "bold")
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # Submit button
        docs_btn = ttk.Button(
            docs_frame, 
            text="Generate Documentation", 
            command=self.generate_docs
        )
        docs_btn.pack(anchor=tk.W, pady=(0, 10))
        
        # Response output
        ttk.Label(docs_frame, text="Documentation:").pack(anchor=tk.W, pady=(5, 0))
        self.docs_output = scrolledtext.ScrolledText(
            docs_frame, 
            height=20, 
            width=40, 
            wrap=tk.WORD, 
            state=tk.DISABLED
        )
        self.docs_output.pack(fill=tk.BOTH, expand=True)
        
        # Apply button - initially disabled
        self.apply_docs_btn = ttk.Button(
            docs_frame, 
            text="Apply Documentation", 
            command=self.apply_docs,
            state=tk.DISABLED
        )
        self.apply_docs_btn.pack(anchor=tk.E, pady=(5, 0))
    
    def create_multi_file_tab(self):
        """Create the 'Multi-File Analysis' tab."""
        multi_file_frame = ttk.Frame(self.notebook, padding=(10, 10))
        self.notebook.add(multi_file_frame, text="Multi-File Analysis")
        
        # Instructions
        ttk.Label(
            multi_file_frame, 
            text="Analyze multiple files with a single prompt",
            font=("Default", 10, "bold")
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # File selection frame
        files_frame = ttk.LabelFrame(multi_file_frame, text="Files to Analyze")
        files_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
        
        # Available files list
        files_container = ttk.Frame(files_frame)
        files_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        available_files_frame = ttk.Frame(files_container)
        available_files_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Label(available_files_frame, text="Available Files:").pack(anchor=tk.W)
        
        self.available_files_list = tk.Listbox(
            available_files_frame, 
            height=5, 
            selectmode=tk.EXTENDED
        )
        available_scrollbar = ttk.Scrollbar(
            available_files_frame, 
            orient=tk.VERTICAL, 
            command=self.available_files_list.yview
        )
        self.available_files_list.configure(yscrollcommand=available_scrollbar.set)
        
        self.available_files_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        available_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons frame
        btn_frame = ttk.Frame(files_container)
        btn_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame, 
            text=">", 
            command=self._add_selected_files
        ).pack(pady=5)
        
        ttk.Button(
            btn_frame, 
            text="<", 
            command=self._remove_selected_files
        ).pack(pady=5)
        
        # Selected files list
        selected_files_frame = ttk.Frame(files_container)
        selected_files_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(selected_files_frame, text="Selected Files:").pack(anchor=tk.W)
        
        self.selected_files_list = tk.Listbox(
            selected_files_frame, 
            height=5, 
            selectmode=tk.EXTENDED
        )
        selected_scrollbar = ttk.Scrollbar(
            selected_files_frame, 
            orient=tk.VERTICAL, 
            command=self.selected_files_list.yview
        )
        self.selected_files_list.configure(yscrollcommand=selected_scrollbar.set)
        
        self.selected_files_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        selected_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Refresh button
        refresh_btn = ttk.Button(
            files_frame, 
            text="Refresh File List", 
            command=self._refresh_file_lists
        )
        refresh_btn.pack(anchor=tk.E, padx=5, pady=5)
        
        # Prompt section
        prompt_frame = ttk.Frame(multi_file_frame)
        prompt_frame.pack(fill=tk.X, expand=False, pady=(0, 10))
        
        # Prompt input
        ttk.Label(prompt_frame, text="Prompt:").grid(row=0, column=0, sticky=tk.W, pady=(5, 0))
        self.multi_file_input = tk.Text(prompt_frame, height=3, width=40, wrap=tk.WORD)
        self.multi_file_input.grid(row=1, column=0, sticky=tk.EW, columnspan=2, pady=(0, 5))
        prompt_frame.columnconfigure(0, weight=1)
        
        # Example prompts label and dropdown - in the same row
        ttk.Label(prompt_frame, text="Example prompts:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        example_prompts = [
            "Generate a README.md for this project",
            "Find potential bugs across these files",
            "How do these files interact with each other?",
            "Summarize what each file does",
            "Suggest improvements for these files",
            "Create a documentation guide for this codebase"
        ]
        
        self.example_var = tk.StringVar()
        example_combo = ttk.Combobox(
            prompt_frame, 
            textvariable=self.example_var,
            values=example_prompts,
            state="readonly",
            width=40  # Increased width to show full prompts
        )
        example_combo.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        example_combo.bind("<<ComboboxSelected>>", lambda e: self._set_example_prompt(self.example_var.get()))
        
        # Submit button - full width
        analyze_btn = ttk.Button(
            prompt_frame, 
            text="Analyze Files", 
            command=self.analyze_files
        )
        analyze_btn.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=(5, 0))
        
        # Response output
        ttk.Label(multi_file_frame, text="Analysis:").pack(anchor=tk.W, pady=(5, 0))
        self.multi_file_output = scrolledtext.ScrolledText(
            multi_file_frame, 
            height=12, 
            width=40, 
            wrap=tk.WORD, 
            state=tk.DISABLED
        )
        self.multi_file_output.pack(fill=tk.BOTH, expand=True)
        
        # Buttons frame for Save and Apply
        action_buttons = ttk.Frame(multi_file_frame)
        action_buttons.pack(fill=tk.X, expand=False, pady=(5, 0))
        
        # Save to markdown button - initially disabled
        self.save_analysis_btn = ttk.Button(
            action_buttons, 
            text="Save to Markdown", 
            command=self.save_analysis_to_markdown,
            state=tk.DISABLED
        )
        self.save_analysis_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Apply changes button - initially disabled
        self.apply_analysis_btn = ttk.Button(
            action_buttons, 
            text="Apply Suggested Changes", 
            command=self.apply_analysis_changes,
            state=tk.DISABLED
        )
        self.apply_analysis_btn.pack(side=tk.RIGHT)
        
        # Initialize file lists
        self._refresh_file_lists()
    
    def _refresh_file_lists(self):
        """Refresh the file lists in the multi-file tab."""
        if not self.sandbox:
            return
            
        # Clear lists
        self.available_files_list.delete(0, tk.END)
        
        # Add files from sandbox
        files = sorted(self.sandbox.list_files())
        for file in files:
            self.available_files_list.insert(tk.END, file)
    
    def _add_selected_files(self):
        """Add selected files to the selected files list."""
        selected_indices = self.available_files_list.curselection()
        for i in selected_indices:
            file = self.available_files_list.get(i)
            # Only add if not already in selected list
            existing_files = self.selected_files_list.get(0, tk.END)
            if file not in existing_files:
                self.selected_files_list.insert(tk.END, file)
    
    def _remove_selected_files(self):
        """Remove selected files from the selected files list."""
        selected_indices = self.selected_files_list.curselection()
        # Delete in reverse order to avoid index shifting
        for i in sorted(selected_indices, reverse=True):
            self.selected_files_list.delete(i)
    
    def _set_example_prompt(self, example):
        """Set an example prompt in the multi-file input field."""
        self.multi_file_input.delete("1.0", tk.END)
        self.multi_file_input.insert("1.0", example)
    
    def analyze_files(self):
        """Analyze multiple files with the given prompt."""
        selected_files = self.selected_files_list.get(0, tk.END)
        if not selected_files:
            if self.status_bar:
                self.status_bar.show_error("Please select at least one file to analyze")
            return
        
        prompt = self.multi_file_input.get(1.0, tk.END).strip()
        if not prompt:
            if self.status_bar:
                self.status_bar.show_error("Please enter a prompt")
            return
        
        # Get contents of all selected files
        file_contents = {}
        for filename in selected_files:
            success, content = self.sandbox.read_file(filename)
            if success:
                file_contents[filename] = content
            else:
                if self.status_bar:
                    self.status_bar.show_error(f"Failed to read {filename}")
                return
        
        # Start progress indicator
        if self.status_bar:
            self.status_bar.start_progress("Analyzing files...")
        
        def get_analysis():
            try:
                # Format the prompt with file contents
                context = "I'll analyze the following files:\n\n"
                for filename, content in file_contents.items():
                    context += f"## File: {filename}\n```\n{content}\n```\n\n"
                
                context += f"Based on these files, please: {prompt}"
                
                # Call the AI
                success, analysis = self.genai.ask_question(context, "")
                
                # Update UI in main thread
                def update_ui():
                    if self.status_bar:
                        self.status_bar.stop_progress()
                        
                    if success:
                        self.set_text_widget(self.multi_file_output, analysis)
                        self.save_analysis_btn.config(state=tk.NORMAL)
                        
                        # Enable apply button if the prompt is about improvements
                        prompt_lower = prompt.lower()
                        if any(kw in prompt_lower for kw in ["improve", "refactor", "fix", "change", "update", "edit"]):
                            self.apply_analysis_btn.config(state=tk.NORMAL)
                        else:
                            self.apply_analysis_btn.config(state=tk.DISABLED)
                            
                        if self.status_bar:
                            self.status_bar.show_message("Analysis complete")
                    else:
                        self.set_text_widget(self.multi_file_output, f"Error: {analysis}")
                        self.save_analysis_btn.config(state=tk.DISABLED)
                        self.apply_analysis_btn.config(state=tk.DISABLED)
                        if self.status_bar:
                            self.status_bar.show_error("Failed to analyze files")
                
                self.after(0, update_ui)
                
            except Exception as e:
                def show_error():
                    if self.status_bar:
                        self.status_bar.stop_progress()
                        self.status_bar.show_error(f"Error analyzing files: {str(e)}")
                    self.set_text_widget(self.multi_file_output, f"Error analyzing files: {str(e)}")
                    self.save_analysis_btn.config(state=tk.DISABLED)
                    self.apply_analysis_btn.config(state=tk.DISABLED)
                    
                self.after(0, show_error)
        
        # Run in thread to avoid UI freeze
        thread = threading.Thread(target=get_analysis)
        thread.daemon = True
        thread.start()
    
    def save_analysis_to_markdown(self):
        """Save the multi-file analysis to a markdown file."""
        content = self.multi_file_output.get(1.0, tk.END).strip()
        if not content:
            return
        
        # Create a suitable filename
        filename_base = "analysis"
        
        # Ask for a filename
        from tkinter import simpledialog
        filename = simpledialog.askstring(
            "Save to Markdown", 
            "Enter markdown filename:",
            initialvalue=f"{filename_base}.md"
        )
        
        if not filename:
            return
            
        # Add .md extension if not present
        if not filename.endswith('.md'):
            filename += '.md'
            
        # Format the content
        prompt = self.multi_file_input.get(1.0, tk.END).strip()
        files = ", ".join(self.selected_files_list.get(0, tk.END))
        markdown_content = f"# Multi-File Analysis\n\n## Files Analyzed\n\n{files}\n\n## Prompt\n\n{prompt}\n\n## Analysis\n\n{content}"
        
        # Save the file
        success, message = self.sandbox.write_file(filename, markdown_content)
        
        if success:
            if self.status_bar:
                self.status_bar.show_message(f"Saved analysis to {filename}")
            # Trigger an event to refresh the file explorer
            self.event_generate("<<FilesGenerated>>")
        else:
            if self.status_bar:
                self.status_bar.show_error(f"Failed to save: {message}")
    
    def set_text_widget(self, widget, text):
        """Set text in a read-only text widget."""
        widget.config(state=tk.NORMAL)
        widget.delete(1.0, tk.END)
        widget.insert(tk.END, text)
        widget.config(state=tk.DISABLED)
    
    def check_file_opened(self):
        """Check if a file is currently open in the editor."""
        if not self.editor.current_file:
            if self.status_bar:
                self.status_bar.show_error("No file opened. Open a file first.")
            return False
        return True
    
    def run_in_thread(self, task_func, *args, **kwargs):
        """Run a function in a separate thread to avoid UI freezing."""
        if self.status_bar:
            self.status_bar.start_progress("Working...")
        
        def threaded_task():
            try:
                task_func(*args, **kwargs)
            finally:
                if self.status_bar:
                    self.after(100, lambda: self.status_bar.stop_progress())
        
        thread = threading.Thread(target=threaded_task)
        thread.daemon = True
        thread.start()
    
    def ask_question(self):
        """Ask a question about the current file."""
        if not self.check_file_opened():
            return
        
        question = self.question_input.get(1.0, tk.END).strip()
        if not question:
            if self.status_bar:
                self.status_bar.show_error("Please enter a question.")
            return
        
        content = self.editor.get_content()
        
        def get_answer():
            success, answer = self.genai.ask_question(question, content)
            
            def update_ui():
                if success:
                    self.set_text_widget(self.ask_output, answer)
                    self.save_ask_btn.config(state=tk.NORMAL)
                else:
                    self.set_text_widget(self.ask_output, f"Error: {answer}")
                    self.save_ask_btn.config(state=tk.DISABLED)
                    if self.status_bar:
                        self.status_bar.show_error("Failed to get answer from AI.")
            
            self.after(0, update_ui)
        
        self.run_in_thread(get_answer)
    
    def explain_code(self):
        """Get an explanation of the current file."""
        if not self.check_file_opened():
            return
        
        content = self.editor.get_content()
        
        def get_explanation():
            success, explanation = self.genai.explain_code(content)
            
            def update_ui():
                if success:
                    self.set_text_widget(self.explain_output, explanation)
                    self.save_explain_btn.config(state=tk.NORMAL)
                else:
                    self.set_text_widget(self.explain_output, f"Error: {explanation}")
                    self.save_explain_btn.config(state=tk.DISABLED)
                    if self.status_bar:
                        self.status_bar.show_error("Failed to get explanation from AI.")
            
            self.after(0, update_ui)
        
        self.run_in_thread(get_explanation)
    
    def refactor_code(self):
        """Refactor the current file."""
        if not self.check_file_opened():
            return
        
        instruction = self.refactor_input.get(1.0, tk.END).strip()
        if not instruction:
            if self.status_bar:
                self.status_bar.show_error("Please enter refactoring instructions.")
            return
        
        content = self.editor.get_content()
        
        def get_refactored_code():
            success, refactored = self.genai.refactor_code(content, instruction)
            
            def update_ui():
                if success:
                    self.set_text_widget(self.refactor_output, refactored)
                    self.apply_refactor_btn.config(state=tk.NORMAL)
                    if self.status_bar:
                        self.status_bar.show_message("Code refactored. You can apply the changes.")
                else:
                    self.set_text_widget(self.refactor_output, f"Error: {refactored}")
                    self.apply_refactor_btn.config(state=tk.DISABLED)
                    if self.status_bar:
                        self.status_bar.show_error("Failed to refactor code.")
            
            self.after(0, update_ui)
        
        self.run_in_thread(get_refactored_code)
    
    def apply_refactored_code(self):
        """Apply the refactored code to the editor."""
        refactored_code = self.refactor_output.get(1.0, tk.END)
        self.editor.set_content(refactored_code)
        self.apply_refactor_btn.config(state=tk.DISABLED)
        if self.status_bar:
            self.status_bar.show_message("Applied refactored code. Don't forget to save.")
    
    def suggest_improvements(self):
        """Get suggestions to improve the current file."""
        if not self.check_file_opened():
            return
        
        content = self.editor.get_content()
        
        def get_suggestions():
            success, suggestions = self.genai.suggest_improvements(content)
            
            def update_ui():
                if success:
                    self.set_text_widget(self.improve_output, suggestions)
                    self.apply_improve_btn.config(state=tk.NORMAL)
                    if self.status_bar:
                        self.status_bar.show_message("Improvements suggested. You can apply them.")
                else:
                    self.set_text_widget(self.improve_output, f"Error: {suggestions}")
                    self.apply_improve_btn.config(state=tk.DISABLED)
                    if self.status_bar:
                        self.status_bar.show_error("Failed to get improvement suggestions.")
            
            self.after(0, update_ui)
        
        self.run_in_thread(get_suggestions)
    
    def apply_improvements(self):
        """Apply the improved code to the editor."""
        improved_code = self.improve_output.get(1.0, tk.END)
        self.editor.set_content(improved_code)
        self.apply_improve_btn.config(state=tk.DISABLED)
        if self.status_bar:
            self.status_bar.show_message("Applied improvements. Don't forget to save.")
    
    def generate_docs(self):
        """Generate documentation for the current file."""
        if not self.check_file_opened():
            return
        
        content = self.editor.get_content()
        
        def get_docs():
            success, docs = self.genai.generate_documentation(content)
            
            def update_ui():
                if success:
                    self.set_text_widget(self.docs_output, docs)
                    self.apply_docs_btn.config(state=tk.NORMAL)
                    if self.status_bar:
                        self.status_bar.show_message("Documentation generated. You can apply it.")
                else:
                    self.set_text_widget(self.docs_output, f"Error: {docs}")
                    self.apply_docs_btn.config(state=tk.DISABLED)
                    if self.status_bar:
                        self.status_bar.show_error("Failed to generate documentation.")
            
            self.after(0, update_ui)
        
        self.run_in_thread(get_docs)
    
    def apply_docs(self):
        """Apply the generated documentation to the editor."""
        docs = self.docs_output.get(1.0, tk.END)
        self.editor.set_content(docs)
        self.apply_docs_btn.config(state=tk.DISABLED)
        if self.status_bar:
            self.status_bar.show_message("Applied documentation. Don't forget to save.")
    
    def save_ask_to_markdown(self):
        """Save the ask ai response to a markdown file."""
        content = self.ask_output.get(1.0, tk.END).strip()
        if not content:
            return
        
        # Get the current file name without extension to use as a base
        filename_base = "question_answer"
        if self.editor.current_file:
            filename_base = os.path.splitext(os.path.basename(self.editor.current_file))[0] + "_qa"
        
        # Ask for a filename
        from tkinter import simpledialog
        filename = simpledialog.askstring(
            "Save to Markdown", 
            "Enter markdown filename:",
            initialvalue=f"{filename_base}.md"
        )
        
        if not filename:
            return
            
        # Add .md extension if not present
        if not filename.endswith('.md'):
            filename += '.md'
            
        # Format the content
        question = self.question_input.get(1.0, tk.END).strip()
        markdown_content = f"# Question and Answer\n\n## Question\n\n{question}\n\n## Answer\n\n{content}"
        
        # Save the file
        success, message = self.sandbox.write_file(filename, markdown_content)
        
        if success:
            if self.status_bar:
                self.status_bar.show_message(f"Saved Q&A to {filename}")
            # Trigger an event to refresh the file explorer
            self.event_generate("<<FilesGenerated>>")
        else:
            if self.status_bar:
                self.status_bar.show_error(f"Failed to save: {message}")
    
    def save_explain_to_markdown(self):
        """Save the code explanation to a markdown file."""
        content = self.explain_output.get(1.0, tk.END).strip()
        if not content:
            return
        
        # Get the current file name without extension to use as a base
        filename_base = "code_explanation"
        if self.editor.current_file:
            filename_base = os.path.splitext(os.path.basename(self.editor.current_file))[0] + "_explanation"
        
        # Ask for a filename
        from tkinter import simpledialog
        filename = simpledialog.askstring(
            "Save to Markdown", 
            "Enter markdown filename:",
            initialvalue=f"{filename_base}.md"
        )
        
        if not filename:
            return
            
        # Add .md extension if not present
        if not filename.endswith('.md'):
            filename += '.md'
            
        # Format the content
        file_name = self.editor.current_file or "unknown file"
        markdown_content = f"# Code Explanation\n\n## File: {os.path.basename(file_name)}\n\n{content}"
        
        # Save the file
        success, message = self.sandbox.write_file(filename, markdown_content)
        
        if success:
            if self.status_bar:
                self.status_bar.show_message(f"Saved explanation to {filename}")
            # Trigger an event to refresh the file explorer
            self.event_generate("<<FilesGenerated>>")
        else:
            if self.status_bar:
                self.status_bar.show_error(f"Failed to save: {message}")
    
    def apply_analysis_changes(self):
        """Apply changes suggested in the multi-file analysis."""
        # Get the analysis content
        analysis = self.multi_file_output.get(1.0, tk.END)
        if not analysis.strip():
            return
            
        # Get the selected files
        selected_files = self.selected_files_list.get(0, tk.END)
        if not selected_files:
            if self.status_bar:
                self.status_bar.show_error("No files selected to apply changes to")
            return
            
        # Check if the prompt was about improvements or changes
        prompt = self.multi_file_input.get(1.0, tk.END).strip().lower()
        if not any(kw in prompt for kw in ["improve", "refactor", "fix", "change", "update", "edit"]):
            if self.status_bar:
                self.status_bar.show_error("The analysis doesn't appear to contain suggested changes to apply")
            return
            
        # Confirm with user
        from tkinter import messagebox
        confirm = messagebox.askyesno(
            "Confirm Apply Changes",
            "This will attempt to apply changes from the analysis to the selected files. "
            "This is an experimental feature and may not work perfectly. Continue?"
        )
        
        if not confirm:
            return
            
        # Start progress indicator
        if self.status_bar:
            self.status_bar.start_progress("Applying changes...")
            
        changes_made = 0
        errors = 0
        
        def apply_changes():
            nonlocal changes_made, errors
            
            try:
                for filename in selected_files:
                    # Read the original file
                    success, original_content = self.sandbox.read_file(filename)
                    if not success:
                        errors += 1
                        continue
                        
                    # Skip if nothing to process
                    if not original_content.strip():
                        continue
                        
                    # Try to find suggestions specifically for this file in the analysis
                    file_marker = f"### {filename}" 
                    file_sections = analysis.split(file_marker)
                    
                    if len(file_sections) > 1:
                        # Found specific section for this file
                        file_analysis = file_sections[1].split("###")[0]  # Get content until next file section
                    else:
                        # No specific section, use general analysis
                        file_analysis = analysis
                    
                    # Detect code blocks
                    import re
                    code_blocks = re.findall(r"```[a-z]*\n(.*?)```", file_analysis, re.DOTALL)
                    
                    # If we found complete code blocks, use the last one as the new content
                    if code_blocks and len(code_blocks[-1].strip()) > 50:  # Ensure it's substantial
                        new_content = code_blocks[-1].strip()
                        
                        # Write the new content
                        success, message = self.sandbox.write_file(filename, new_content)
                        if success:
                            changes_made += 1
                        else:
                            errors += 1
                            
                # Update UI in main thread
                def update_ui():
                    if self.status_bar:
                        self.status_bar.stop_progress()
                        
                    if changes_made > 0:
                        if self.status_bar:
                            self.status_bar.show_message(
                                f"Applied changes to {changes_made} file(s)" +
                                (f", {errors} errors" if errors > 0 else "")
                            )
                        # Trigger file refresh
                        self.event_generate("<<FilesGenerated>>")
                    else:
                        if self.status_bar:
                            self.status_bar.show_error("No changes were applied")
                
                self.after(0, update_ui)
                
            except Exception as e:
                def show_error():
                    if self.status_bar:
                        self.status_bar.stop_progress()
                        self.status_bar.show_error(f"Error applying changes: {str(e)}")
                    
                self.after(0, show_error)
        
        # Run in thread to avoid UI freeze
        thread = threading.Thread(target=apply_changes)
        thread.daemon = True
        thread.start() 