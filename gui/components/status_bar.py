import tkinter as tk
from tkinter import ttk
import time

class StatusBar(ttk.Frame):
    """Status bar component for showing messages and operation status."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Configure frame
        self.columnconfigure(0, weight=1)
        
        # Status message label
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(
            self, 
            textvariable=self.status_var, 
            anchor=tk.W,
            padding=(5, 2)
        )
        self.status_label.grid(row=0, column=0, sticky=tk.W+tk.E)
        
        # Progress indicator
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            self, 
            orient=tk.HORIZONTAL, 
            length=100, 
            mode='indeterminate',
            variable=self.progress_var
        )
        self.progress.grid(row=0, column=1, padx=5, pady=2)
        self.progress.grid_remove()  # Hide by default
        
        # Set initial status
        self.set_status("Ready")
        
    def set_status(self, message):
        """Set status message."""
        self.status_var.set(message)
        self.update_idletasks()
    
    def start_progress(self, message=None):
        """Start progress indicator with optional message."""
        if message:
            self.set_status(message)
        self.progress.grid()
        self.progress.start(10)
        self.update_idletasks()
    
    def stop_progress(self, message=None):
        """Stop progress indicator with optional message."""
        self.progress.stop()
        self.progress.grid_remove()
        if message:
            self.set_status(message)
        self.update_idletasks()
    
    def show_message(self, message, duration=5000):
        """Show a temporary message for the specified duration (ms)."""
        previous_message = self.status_var.get()
        self.set_status(message)
        self.after(duration, lambda: self.set_status(previous_message))
        
    def show_error(self, message, duration=5000):
        """Show an error message for the specified duration (ms)."""
        # Save the current style
        original_style = self.status_label.cget("style")
        
        # Create error style
        error_style = ttk.Style()
        error_style.configure("Error.TLabel", foreground="red")
        self.status_label.configure(style="Error.TLabel")
        
        # Show error message
        previous_message = self.status_var.get()
        self.set_status(f"Error: {message}")
        
        # Reset after duration
        def reset():
            self.status_label.configure(style=original_style)
            self.set_status(previous_message)
            
        self.after(duration, reset) 