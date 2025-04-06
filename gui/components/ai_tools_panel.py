import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import threading

class AIToolsPanel(ttk.Frame):
    """AI tools panel for interacting with GenAI."""
    
    def __init__(self, parent, genai_wrapper, editor_panel, status_bar=None):
        super().__init__(parent)
        self.parent = parent
        self.genai = genai_wrapper
        self.editor = editor_panel
        self.status_bar = status_bar
        
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
                else:
                    self.set_text_widget(self.ask_output, f"Error: {answer}")
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
                else:
                    self.set_text_widget(self.explain_output, f"Error: {explanation}")
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
                else:
                    self.set_text_widget(self.improve_output, f"Error: {suggestions}")
                    if self.status_bar:
                        self.status_bar.show_error("Failed to get improvement suggestions.")
            
            self.after(0, update_ui)
        
        self.run_in_thread(get_suggestions)
    
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