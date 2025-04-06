import os
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import re

class EditorPanel(ttk.Frame):
    """Editor panel for viewing and editing files."""
    
    def __init__(self, parent, sandbox_manager, status_bar=None):
        super().__init__(parent)
        self.parent = parent
        self.sandbox = sandbox_manager
        self.status_bar = status_bar
        self.current_file = None
        self.modified = False
        
        # Configure frame
        self.configure(padding=(5, 5))
        
        # Create header
        self.header_frame = ttk.Frame(self)
        self.header_frame.pack(fill=tk.X, expand=False, pady=(0, 5))
        
        # File info
        self.file_label = ttk.Label(
            self.header_frame, 
            text="No file open",
            font=("Default", 10, "bold")
        )
        self.file_label.pack(side=tk.LEFT)
        
        # Modified indicator
        self.modified_label = ttk.Label(
            self.header_frame,
            text="*",
            foreground="red",
            font=("Default", 10, "bold")
        )
        # Don't pack yet - only show when modified
        
        # Create toolbar
        toolbar = ttk.Frame(self.header_frame)
        toolbar.pack(side=tk.RIGHT)
        
        # Editor buttons
        self.save_btn = ttk.Button(toolbar, text="Save", width=6, command=self.save_file)
        self.save_btn.pack(side=tk.LEFT, padx=2)
        self.save_btn["state"] = "disabled"  # Disabled until file is opened
        
        # Create editor
        self.editor_frame = ttk.Frame(self)
        self.editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text editor with syntax highlighting
        self.editor = SyntaxHighlightText(
            self.editor_frame,
            wrap=tk.WORD,
            undo=True,
            font=("Courier New", 10)
        )
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(self.editor_frame, orient=tk.VERTICAL, command=self.editor.yview)
        x_scrollbar = ttk.Scrollbar(self.editor_frame, orient=tk.HORIZONTAL, command=self.editor.xview)
        self.editor.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Pack editor and scrollbars
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind events
        self.editor.bind("<<Modified>>", self.on_text_modified)
        self.editor.bind("<Control-s>", self.save_file)
        
    def open_file(self, filename):
        """Open a file for editing."""
        # Check if current file has unsaved changes
        if self.modified:
            self.check_save_changes()
        
        # Reset editor
        self.editor.delete(1.0, tk.END)
        self.current_file = None
        self.modified = False
        self.update_file_label()
        
        # Read file
        success, content = self.sandbox.read_file(filename)
        if not success:
            if self.status_bar:
                self.status_bar.show_error(content)
            return False
        
        # Update editor
        self.editor.insert(1.0, content)
        self.current_file = filename
        self.save_btn["state"] = "normal"
        self.update_file_label()
        
        # Apply syntax highlighting based on file extension
        self.apply_syntax_highlighting(filename)
        
        # Reset modified flag
        self.editor.edit_modified(False)
        if self.status_bar:
            self.status_bar.set_status(f"Opened: {filename}")
            
        # Set focus to editor
        self.editor.focus_set()
        return True
    
    def save_file(self, event=None):
        """Save the current file."""
        if not self.current_file:
            return
        
        content = self.editor.get(1.0, tk.END)
        success, message = self.sandbox.write_file(self.current_file, content)
        
        if success:
            self.editor.edit_modified(False)
            self.modified = False
            self.update_file_label()
            if self.status_bar:
                self.status_bar.show_message(f"Saved: {self.current_file}")
        else:
            if self.status_bar:
                self.status_bar.show_error(message)
    
    def check_save_changes(self):
        """Check if there are unsaved changes and prompt to save."""
        from tkinter import messagebox
        
        if not self.modified or not self.current_file:
            return
        
        answer = messagebox.askyesnocancel(
            "Save Changes", 
            f"Save changes to {self.current_file}?"
        )
        
        if answer is None:  # Cancel
            return False
        elif answer:  # Yes
            self.save_file()
        
        return True
    
    def on_text_modified(self, event):
        """Handle text modification event."""
        if self.editor.edit_modified():
            if not self.modified:
                self.modified = True
                self.update_file_label()
    
    def update_file_label(self):
        """Update the file label with current filename and modified status."""
        if self.current_file:
            self.file_label.configure(text=self.current_file)
            
            if self.modified:
                self.modified_label.pack(side=tk.LEFT, padx=(5, 0))
            else:
                self.modified_label.pack_forget()
        else:
            self.file_label.configure(text="No file open")
            self.modified_label.pack_forget()
            
    def get_content(self):
        """Get the current editor content."""
        return self.editor.get(1.0, tk.END)
        
    def set_content(self, content):
        """Set the editor content."""
        self.editor.delete(1.0, tk.END)
        self.editor.insert(1.0, content)
        self.editor.edit_modified(True)
        self.on_text_modified(None)
    
    def apply_syntax_highlighting(self, filename):
        """Apply syntax highlighting based on file extension."""
        ext = os.path.splitext(filename)[1].lower()
        
        # Reset all highlighting
        self.editor.tag_remove("keyword", "1.0", tk.END)
        self.editor.tag_remove("string", "1.0", tk.END)
        self.editor.tag_remove("comment", "1.0", tk.END)
        self.editor.tag_remove("function", "1.0", tk.END)
        
        # Apply highlighting based on file type
        if ext == '.py':
            self.editor.highlight_python()
        elif ext in ['.html', '.htm']:
            self.editor.highlight_html()
        elif ext == '.js':
            self.editor.highlight_javascript()
        elif ext == '.css':
            self.editor.highlight_css()
        elif ext == '.json':
            self.editor.highlight_json()
        elif ext == '.md':
            self.editor.highlight_markdown()
        
        # For other file types, use basic highlighting
        self.editor.highlight_numbers()


class SyntaxHighlightText(scrolledtext.ScrolledText):
    """Text widget with syntax highlighting capabilities."""
    
    def __init__(self, *args, **kwargs):
        scrolledtext.ScrolledText.__init__(self, *args, **kwargs)
        
        # Configure tags for syntax highlighting
        self.tag_configure("keyword", foreground="blue")
        self.tag_configure("string", foreground="green")
        self.tag_configure("comment", foreground="gray")
        self.tag_configure("function", foreground="purple")
        self.tag_configure("number", foreground="dark orange")
        self.tag_configure("heading", foreground="blue", font=("Courier New", 10, "bold"))
        
    def highlight_pattern(self, pattern, tag, start="1.0", end=tk.END, regexp=True):
        """Apply tag to all text that matches the pattern."""
        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)

        count = tk.IntVar()
        while True:
            index = self.search(pattern, "matchEnd", "searchLimit",
                                count=count, regexp=regexp)
            if index == "" or count.get() == 0:
                break
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", f"{index}+{count.get()}c")
            self.tag_add(tag, "matchStart", "matchEnd")
    
    def highlight_python(self):
        """Apply Python syntax highlighting."""
        # Keywords
        python_keywords = r'\b(and|as|assert|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b'
        self.highlight_pattern(python_keywords, "keyword")
        
        # Strings
        self.highlight_pattern(r'\".*?\"', "string")
        self.highlight_pattern(r"\'.*?\'", "string")
        self.highlight_pattern(r'\"\"\".*?\"\"\"', "string", regexp=False)
        self.highlight_pattern(r"\'\'\'.*?\'\'\'", "string", regexp=False)
        
        # Comments
        self.highlight_pattern(r'#.*$', "comment")
        
        # Functions
        self.highlight_pattern(r'\bdef\s+([a-zA-Z_][a-zA-Z0-9_]*)', "function")
        
        # Highlight numbers
        self.highlight_numbers()
    
    def highlight_html(self):
        """Apply HTML syntax highlighting."""
        # Tags
        self.highlight_pattern(r'<[^>]*>', "keyword")
        
        # Attributes
        self.highlight_pattern(r'\s([a-zA-Z-]+)="', "function")
        
        # Strings
        self.highlight_pattern(r'"[^"]*"', "string")
        
        # Comments
        self.highlight_pattern(r'<!--.*?-->', "comment")
    
    def highlight_javascript(self):
        """Apply JavaScript syntax highlighting."""
        # Keywords
        js_keywords = r'\b(break|case|catch|class|const|continue|debugger|default|delete|do|else|export|extends|finally|for|function|if|import|in|instanceof|new|return|super|switch|this|throw|try|typeof|var|void|while|with|yield)\b'
        self.highlight_pattern(js_keywords, "keyword")
        
        # Strings
        self.highlight_pattern(r'\".*?\"', "string")
        self.highlight_pattern(r"\'.*?\'", "string")
        self.highlight_pattern(r'\`.*?\`', "string")
        
        # Comments
        self.highlight_pattern(r'//.*$', "comment")
        self.highlight_pattern(r'/\*.*?\*/', "comment")
        
        # Functions
        self.highlight_pattern(r'\bfunction\s+([a-zA-Z_][a-zA-Z0-9_]*)', "function")
        
        # Highlight numbers
        self.highlight_numbers()
    
    def highlight_css(self):
        """Apply CSS syntax highlighting."""
        # Selectors
        self.highlight_pattern(r'[a-zA-Z0-9#\.\-_]+\s*\{', "keyword")
        
        # Properties
        self.highlight_pattern(r'\s([a-zA-Z-]+):', "function")
        
        # Values
        self.highlight_pattern(r':\s*([^;]+);', "string")
        
        # Comments
        self.highlight_pattern(r'/\*.*?\*/', "comment")
    
    def highlight_json(self):
        """Apply JSON syntax highlighting."""
        # Keys
        self.highlight_pattern(r'"[^"]*"\s*:', "keyword")
        
        # Strings
        self.highlight_pattern(r':\s*"[^"]*"', "string")
        
        # Booleans and null
        self.highlight_pattern(r':\s*(true|false|null)\b', "function")
        
        # Highlight numbers
        self.highlight_numbers()
    
    def highlight_markdown(self):
        """Apply Markdown syntax highlighting."""
        # Headings
        self.highlight_pattern(r'^#+\s.*$', "heading")
        
        # Bold
        self.highlight_pattern(r'\*\*.*?\*\*', "keyword")
        
        # Italic
        self.highlight_pattern(r'\*.*?\*', "function")
        
        # Links
        self.highlight_pattern(r'\[.*?\]\(.*?\)', "string")
        
        # Code blocks
        self.highlight_pattern(r'`.*?`', "comment")
        self.highlight_pattern(r'```.*?```', "comment")
    
    def highlight_numbers(self):
        """Highlight numeric values."""
        self.highlight_pattern(r'\b\d+\b', "number") 