import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from gui.components.file_explorer import FileExplorer
from gui.components.editor_panel import EditorPanel
from gui.components.ai_tools_panel import AIToolsPanel
from gui.components.status_bar import StatusBar

class IDEApp:
    """Main application class for the GUI version of Sandbox IDE."""
    
    def __init__(self, sandbox_manager, genai_wrapper):
        self.sandbox = sandbox_manager
        self.genai = genai_wrapper
        self.root = None
        
    def run(self):
        """Start the application."""
        # Create the main window
        self.root = tk.Tk()
        self.root.title("Sandbox IDE with GenAI")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Set theme
        self._configure_style()
        
        # Create main layout
        self._create_layout()
        
        # Set up event handlers
        self._setup_event_handlers()
        
        # Start the main loop
        self.root.mainloop()
    
    def _configure_style(self):
        """Configure the theme and styles."""
        style = ttk.Style()
        
        # Try to use a modern theme if available
        try:
            style.theme_use("clam")  # 'clam', 'alt', 'default', 'classic'
        except tk.TclError:
            pass
        
        # Configure colors for better contrast
        style.configure("TFrame", background="#f5f5f5")
        style.configure("TButton", padding=5)
        style.configure("TNotebook", padding=2)
        style.configure("TLabel", background="#f5f5f5")
        
        # Set window icon (if available)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
    def _create_layout(self):
        """Create the main application layout."""
        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        
        # Create status bar at the bottom
        self.status_bar = StatusBar(self.root)
        self.status_bar.grid(row=2, column=0, sticky="ew")
        
        # Create menu
        self._create_menu()
        
        # Create main container
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Configure main container grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Create file explorer in left panel
        self.file_explorer = FileExplorer(main_frame, self.sandbox, self.status_bar)
        self.file_explorer.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Create vertical separator
        ttk.Separator(main_frame, orient=tk.VERTICAL).grid(row=0, column=1, sticky="ns", padx=5)
        
        # Create right panel container
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=0, column=2, sticky="nsew")
        
        # Configure right panel grid
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=2)
        right_panel.rowconfigure(2, weight=1)
        
        # Create editor panel
        self.editor = EditorPanel(right_panel, self.sandbox, self.status_bar)
        self.editor.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Create horizontal separator
        ttk.Separator(right_panel, orient=tk.HORIZONTAL).grid(row=1, column=0, sticky="ew", pady=5)
        
        # Create AI tools panel
        self.ai_tools = AIToolsPanel(right_panel, self.genai, self.editor, self.status_bar)
        self.ai_tools.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        
        # Set initial status
        self.status_bar.set_status(f"Sandbox directory: {self.sandbox.sandbox_dir}")
    
    def _create_menu(self):
        """Create the application menu bar."""
        menu_bar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New File", command=self._on_new_file)
        file_menu.add_command(label="Open File", command=self._on_open_file)
        file_menu.add_command(label="Save", command=self._on_save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Refresh Files", command=self._on_refresh_files)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_exit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self._on_undo)
        edit_menu.add_command(label="Redo", command=self._on_redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self._on_cut)
        edit_menu.add_command(label="Copy", command=self._on_copy)
        edit_menu.add_command(label="Paste", command=self._on_paste)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        
        # AI menu
        ai_menu = tk.Menu(menu_bar, tearoff=0)
        ai_menu.add_command(label="Explain Code", command=self._on_explain_code)
        ai_menu.add_command(label="Suggest Improvements", command=self._on_suggest_improvements)
        ai_menu.add_command(label="Generate Documentation", command=self._on_generate_docs)
        menu_bar.add_cascade(label="AI Tools", menu=ai_menu)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self._on_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menu_bar)
    
    def _setup_event_handlers(self):
        """Set up event handlers for components interaction."""
        # Handle file selection from file explorer
        self.file_explorer.set_file_select_callback(self._on_file_selected)
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_exit)
    
    def _on_file_selected(self, filename, open_file=False):
        """Handle file selection in the file explorer."""
        if open_file:
            self.editor.open_file(filename)
    
    def _on_new_file(self):
        """Create a new file."""
        self.file_explorer.create_file()
    
    def _on_open_file(self):
        """Open the selected file."""
        if self.file_explorer.selected_file:
            self.editor.open_file(self.file_explorer.selected_file)
        else:
            self.status_bar.show_error("No file selected")
    
    def _on_save_file(self):
        """Save the current file."""
        self.editor.save_file()
    
    def _on_refresh_files(self):
        """Refresh the file list."""
        self.file_explorer.refresh_files()
    
    def _on_exit(self):
        """Exit the application."""
        # Check for unsaved changes
        if self.editor.modified:
            if not self.editor.check_save_changes():
                return
        
        # Destroy the main window
        self.root.destroy()
    
    def _on_undo(self):
        """Undo the last edit action."""
        try:
            self.editor.editor.edit_undo()
        except tk.TclError:
            self.status_bar.show_message("Nothing to undo")
    
    def _on_redo(self):
        """Redo the last undone edit action."""
        try:
            self.editor.editor.edit_redo()
        except tk.TclError:
            self.status_bar.show_message("Nothing to redo")
    
    def _on_cut(self):
        """Cut the selected text."""
        try:
            self.editor.editor.event_generate("<<Cut>>")
        except:
            pass
    
    def _on_copy(self):
        """Copy the selected text."""
        try:
            self.editor.editor.event_generate("<<Copy>>")
        except:
            pass
    
    def _on_paste(self):
        """Paste text from clipboard."""
        try:
            self.editor.editor.event_generate("<<Paste>>")
        except:
            pass
    
    def _on_explain_code(self):
        """Open the Explain Code tab and trigger explanation."""
        self.ai_tools.notebook.select(1)  # Select the Explain tab (index 1)
        self.ai_tools.explain_code()
    
    def _on_suggest_improvements(self):
        """Open the Improve tab and trigger suggestions."""
        self.ai_tools.notebook.select(3)  # Select the Improve tab (index 3)
        self.ai_tools.suggest_improvements()
    
    def _on_generate_docs(self):
        """Open the Generate Docs tab and trigger documentation generation."""
        self.ai_tools.notebook.select(4)  # Select the Generate Docs tab (index 4)
        self.ai_tools.generate_docs()
    
    def _on_about(self):
        """Show the About dialog."""
        messagebox.showinfo(
            "About Sandbox IDE",
            "Sandbox IDE with GenAI\n\n"
            "A secure, AI-powered development environment\n"
            "that uses Google's GenAI SDK for code assistance\n\n"
            "All operations are confined to the sandbox directory."
        ) 