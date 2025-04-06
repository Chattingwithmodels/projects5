import os
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog, messagebox

class FileExplorer(ttk.Frame):
    """File explorer component for viewing and managing sandbox files."""
    
    def __init__(self, parent, sandbox_manager, status_bar=None):
        super().__init__(parent)
        self.parent = parent
        self.sandbox = sandbox_manager
        self.status_bar = status_bar
        self.selected_file = None
        self.on_file_select_callback = None
        
        # Configure the frame
        self.configure(padding=(5, 5))
        
        # Create header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, expand=False, pady=(0, 5))
        
        ttk.Label(header_frame, text="Files", font=("Default", 10, "bold")).pack(side=tk.LEFT)
        
        # Create toolbar
        toolbar = ttk.Frame(header_frame)
        toolbar.pack(side=tk.RIGHT)
        
        # File operation buttons
        self.new_btn = ttk.Button(toolbar, text="New", width=6, command=self.create_file)
        self.new_btn.pack(side=tk.LEFT, padx=2)
        
        self.rename_btn = ttk.Button(toolbar, text="Rename", width=6, command=self.rename_file)
        self.rename_btn.pack(side=tk.LEFT, padx=2)
        
        self.delete_btn = ttk.Button(toolbar, text="Delete", width=6, command=self.delete_file)
        self.delete_btn.pack(side=tk.LEFT, padx=2)
        
        self.refresh_btn = ttk.Button(toolbar, text="Refresh", width=6, command=self.refresh_files)
        self.refresh_btn.pack(side=tk.LEFT, padx=2)
        
        # Create file treeview
        self.tree_frame = ttk.Frame(self)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(
            self.tree_frame, 
            columns=("size", "modified"),
            selectmode="browse"
        )
        
        # Configure columns
        self.tree.column("#0", width=200, stretch=tk.YES)
        self.tree.column("size", width=100, anchor=tk.E)
        self.tree.column("modified", width=150, anchor=tk.W)
        
        self.tree.heading("#0", text="Filename")
        self.tree.heading("size", text="Size")
        self.tree.heading("modified", text="Modified")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind events
        self.tree.bind("<<TreeviewSelect>>", self.on_file_select)
        self.tree.bind("<Double-1>", self.on_file_double_click)
        
        # Initialize
        self.refresh_files()
    
    def set_file_select_callback(self, callback):
        """Set the callback function for when a file is selected."""
        self.on_file_select_callback = callback
    
    def on_file_select(self, event):
        """Handle file selection event."""
        selection = self.tree.selection()
        if not selection:
            self.selected_file = None
            return
        
        item = self.tree.item(selection[0])
        self.selected_file = item["text"]
        
        # Call the external callback if set
        if self.on_file_select_callback:
            self.on_file_select_callback(self.selected_file)
    
    def on_file_double_click(self, event):
        """Handle file double-click event."""
        if self.selected_file and self.on_file_select_callback:
            self.on_file_select_callback(self.selected_file, open_file=True)
    
    def refresh_files(self):
        """Refresh the file list."""
        # Clear the tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get file list
        files = self.sandbox.list_files()
        
        # Display files in tree
        root_path = self.sandbox.sandbox_dir
        for filename in sorted(files):
            file_path = os.path.join(root_path, filename)
            file_stats = os.stat(file_path)
            
            size = self._format_size(file_stats.st_size)
            modified = self._format_time(file_stats.st_mtime)
            
            self.tree.insert("", "end", text=filename, values=(size, modified))
        
        # Update status
        if self.status_bar:
            self.status_bar.set_status(f"{len(files)} files in sandbox")
    
    def create_file(self):
        """Create a new file."""
        filename = simpledialog.askstring("New File", "Enter filename:")
        if not filename:
            return
            
        success, message = self.sandbox.write_file(filename, "")
        
        if success:
            self.refresh_files()
            # Select the new file
            for item in self.tree.get_children():
                if self.tree.item(item, "text") == filename:
                    self.tree.selection_set(item)
                    self.tree.see(item)
                    self.selected_file = filename
                    if self.on_file_select_callback:
                        self.on_file_select_callback(filename, open_file=True)
                    break
            if self.status_bar:
                self.status_bar.show_message(f"Created file: {filename}")
        else:
            if self.status_bar:
                self.status_bar.show_error(message)
            else:
                messagebox.showerror("Error", message)
    
    def rename_file(self):
        """Rename the selected file."""
        if not self.selected_file:
            if self.status_bar:
                self.status_bar.show_error("No file selected")
            else:
                messagebox.showerror("Error", "No file selected")
            return
        
        new_name = simpledialog.askstring(
            "Rename File", 
            "Enter new filename:",
            initialvalue=self.selected_file
        )
        
        if not new_name or new_name == self.selected_file:
            return
        
        success, message = self.sandbox.rename_file(self.selected_file, new_name)
        
        if success:
            old_name = self.selected_file
            self.selected_file = new_name
            self.refresh_files()
            # Select the renamed file
            for item in self.tree.get_children():
                if self.tree.item(item, "text") == new_name:
                    self.tree.selection_set(item)
                    self.tree.see(item)
                    break
            if self.status_bar:
                self.status_bar.show_message(f"Renamed: {old_name} → {new_name}")
        else:
            if self.status_bar:
                self.status_bar.show_error(message)
            else:
                messagebox.showerror("Error", message)
    
    def delete_file(self):
        """Delete the selected file."""
        if not self.selected_file:
            if self.status_bar:
                self.status_bar.show_error("No file selected")
            else:
                messagebox.showerror("Error", "No file selected")
            return
        
        confirm = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to delete {self.selected_file}?"
        )
        
        if not confirm:
            return
        
        success, message = self.sandbox.delete_file(self.selected_file)
        
        if success:
            filename = self.selected_file
            self.selected_file = None
            self.refresh_files()
            if self.status_bar:
                self.status_bar.show_message(f"Deleted: {filename}")
        else:
            if self.status_bar:
                self.status_bar.show_error(message)
            else:
                messagebox.showerror("Error", message)
    
    def _format_size(self, size_bytes):
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} GB"
    
    def _format_time(self, timestamp):
        """Format timestamp in human-readable format."""
        from datetime import datetime
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S") 