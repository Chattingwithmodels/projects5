import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json

from gui.components.file_explorer import FileExplorer
from gui.components.editor_panel import EditorPanel
from gui.components.ai_tools_panel import AIToolsPanel
from gui.components.status_bar import StatusBar
from gui.components.settings_panel import SettingsPanel
from gui.components.image_gen_panel import ImageGenPanel
from gui.components.multi_file_gen_panel import MultiFileGenPanel

class IDEApp:
    """Main application class for the GUI version of Sandbox IDE."""
    
    def __init__(self, sandbox_manager, genai_wrapper):
        self.sandbox = sandbox_manager
        self.genai = genai_wrapper
        self.root = None
        self.file_explorer_visible = True
        self.dark_mode = self._load_dark_mode_setting()
        
    def _load_dark_mode_setting(self):
        """Load dark mode setting from settings file."""
        settings_file = os.path.join(
            os.path.expanduser("~"), 
            ".sandbox_ide_settings.json"
        )
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get("dark_mode", False)
        except Exception as e:
            print(f"Error loading settings: {e}")
        return False
        
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
        
        if self.dark_mode:
            # Dark mode colors
            bg_color = "#222222"
            fg_color = "#ffffff"
            select_bg = "#505050"
            text_bg = "#2d2d2d"
            text_fg = "#ffffff"
            button_bg = "#444444"
            highlight_bg = "#3a3a3a"
            
            # Configure dark theme
            style.configure(".", background=bg_color, foreground=fg_color,
                           fieldbackground=bg_color, troughcolor=bg_color)
            style.configure("TFrame", background=bg_color)
            style.configure("TButton", background=button_bg, foreground=fg_color)
            style.configure("TNotebook", background=bg_color, borderwidth=0)
            style.configure("TNotebook.Tab", background=button_bg, foreground=fg_color, padding=(10, 2))
            style.map("TNotebook.Tab", background=[("selected", highlight_bg)], 
                     foreground=[("selected", fg_color)])
            style.configure("TLabel", background=bg_color, foreground=fg_color)
            style.configure("TCheckbutton", background=bg_color, foreground=fg_color)
            style.configure("TRadiobutton", background=bg_color, foreground=fg_color)
            style.configure("TEntry", fieldbackground=text_bg, foreground=text_fg)
            style.configure("TCombobox", fieldbackground=text_bg, foreground=text_fg)
            style.configure("TSpinbox", fieldbackground=text_bg, foreground=text_fg)
            style.configure("TScale", troughcolor=button_bg)
            style.map("Treeview", background=[("selected", select_bg)])
            
            # Configure Tkinter widgets
            self.root.config(background=bg_color)
            self.root.option_add("*Text.Background", text_bg)
            self.root.option_add("*Text.Foreground", text_fg)
            self.root.option_add("*Text.selectBackground", select_bg)
            self.root.option_add("*Text.highlightBackground", highlight_bg)
            self.root.option_add("*ScrolledText.Background", text_bg)
            self.root.option_add("*ScrolledText.Foreground", text_fg)
            
        else:
            # Light mode colors
            bg_color = "#f5f5f5"
            # Configure light theme
            style.configure("TFrame", background=bg_color)
            style.configure("TButton", padding=5)
            style.configure("TNotebook", padding=2)
            style.configure("TLabel", background=bg_color)
        
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
        
        # Create main container - use PanedWindow for resizable sections
        self.main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_pane.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Create file explorer frame with toggle button at top
        self.explorer_container = ttk.Frame(self.main_pane)
        self.main_pane.add(self.explorer_container, weight=1)
        
        # Add toggle button and file explorer label
        explorer_header = ttk.Frame(self.explorer_container)
        explorer_header.pack(fill=tk.X, expand=False)
        
        ttk.Label(explorer_header, text="Files", font=("Default", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        self.toggle_btn = ttk.Button(
            explorer_header, 
            text="◀", 
            width=2,
            command=self._toggle_file_explorer
        )
        self.toggle_btn.pack(side=tk.RIGHT, padx=5)
        
        # Create file explorer
        self.file_explorer = FileExplorer(self.explorer_container, self.sandbox, self.status_bar)
        self.file_explorer.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right panel container (workspace)
        self.workspace = ttk.Frame(self.main_pane)
        self.main_pane.add(self.workspace, weight=3)
        
        # Nested Notebook for editor and tools
        self.workspace_notebook = ttk.Notebook(self.workspace)
        self.workspace_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create editor workspace (editor + AI tools)
        self.editor_workspace = ttk.Frame(self.workspace_notebook)
        self.workspace_notebook.add(self.editor_workspace, text="Editor")
        
        # Create editor paned container (vertical split between editor and tools)
        self.editor_pane = ttk.PanedWindow(self.editor_workspace, orient=tk.VERTICAL)
        self.editor_pane.pack(fill=tk.BOTH, expand=True)
        
        # Create editor panel
        self.editor = EditorPanel(self.editor_pane, self.sandbox, self.status_bar)
        self.editor_pane.add(self.editor, weight=2)
        
        # Create AI tools panel
        self.ai_tools = AIToolsPanel(self.editor_pane, self.genai, self.editor, self.status_bar, self.sandbox)
        self.editor_pane.add(self.ai_tools, weight=1)
        
        # Create multi-file generator tab
        self.multi_file_gen = MultiFileGenPanel(
            self.workspace_notebook, 
            self.genai, 
            self.sandbox, 
            self.status_bar
        )
        self.workspace_notebook.add(self.multi_file_gen, text="Multi-File Generator")
        
        # Create image generator tab
        self.image_gen = ImageGenPanel(
            self.workspace_notebook, 
            self.genai, 
            self.sandbox, 
            self.status_bar
        )
        self.workspace_notebook.add(self.image_gen, text="Image Generator")
        
        # Create settings tab
        self.settings_panel = SettingsPanel(
            self.workspace_notebook, 
            self.genai, 
            self.status_bar
        )
        self.workspace_notebook.add(self.settings_panel, text="Settings")
        
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
        
        # View menu
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="Toggle File Explorer", command=self._toggle_file_explorer)
        view_menu.add_separator()
        view_menu.add_command(label="Editor", command=lambda: self.workspace_notebook.select(0))
        view_menu.add_command(label="Multi-File Generator", command=lambda: self.workspace_notebook.select(1))
        view_menu.add_command(label="Image Generator", command=lambda: self.workspace_notebook.select(2))
        view_menu.add_command(label="Settings", command=lambda: self.workspace_notebook.select(3))
        menu_bar.add_cascade(label="View", menu=view_menu)
        
        # AI menu
        ai_menu = tk.Menu(menu_bar, tearoff=0)
        ai_menu.add_command(label="Explain Code", command=self._on_explain_code)
        ai_menu.add_command(label="Suggest Improvements", command=self._on_suggest_improvements)
        ai_menu.add_command(label="Generate Documentation", command=self._on_generate_docs)
        ai_menu.add_separator()
        ai_menu.add_command(label="Generate Files", command=lambda: self.workspace_notebook.select(1))
        ai_menu.add_command(label="Generate Image", command=lambda: self.workspace_notebook.select(2))
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
        
        # Handle multi-file generation completion
        self.root.bind("<<FilesGenerated>>", self._on_files_generated)
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_exit)
        
        # Handle window resize
        self.root.bind("<Configure>", self._on_window_configure)
    
    def _on_window_configure(self, event):
        """Handle window resize events."""
        # Pass resize event to components that need it
        if hasattr(self, 'image_gen'):
            self.image_gen.on_resize()
    
    def _on_file_selected(self, filename, open_file=False):
        """Handle file selection in the file explorer."""
        if open_file:
            # Switch to editor tab if not already there
            self.workspace_notebook.select(0)
            self.editor.open_file(filename)
    
    def _on_files_generated(self, event):
        """Handle completion of multi-file generation."""
        # Refresh the file explorer
        self.file_explorer.refresh_files()
    
    def _toggle_file_explorer(self):
        """Toggle the visibility of the file explorer."""
        if self.file_explorer_visible:
            # Hide file explorer
            for child in self.explorer_container.winfo_children():
                # Keep the header visible but hide the actual explorer
                if child != self.explorer_container.winfo_children()[0]:
                    child.pack_forget()
            self.toggle_btn.configure(text="▶")
            self.file_explorer_visible = False
        else:
            # Show file explorer
            self.file_explorer.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.toggle_btn.configure(text="◀")
            self.file_explorer_visible = True
    
    def _on_new_file(self):
        """Create a new file."""
        self.file_explorer.create_file()
    
    def _on_open_file(self):
        """Open the selected file."""
        if self.file_explorer.selected_file:
            # Switch to editor tab if not already there
            self.workspace_notebook.select(0)
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
        # Switch to editor tab
        self.workspace_notebook.select(0)
        self.ai_tools.notebook.select(1)  # Select the Explain tab (index 1)
        self.ai_tools.explain_code()
    
    def _on_suggest_improvements(self):
        """Open the Improve tab and trigger suggestions."""
        # Switch to editor tab
        self.workspace_notebook.select(0)
        self.ai_tools.notebook.select(3)  # Select the Improve tab (index 3)
        self.ai_tools.suggest_improvements()
    
    def _on_generate_docs(self):
        """Open the Generate Docs tab and trigger documentation generation."""
        # Switch to editor tab
        self.workspace_notebook.select(0)
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