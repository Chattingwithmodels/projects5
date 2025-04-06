import tkinter as tk
from tkinter import ttk, messagebox
import threading

class MultiFileGenPanel(ttk.Frame):
    """Panel for generating multiple files from a single prompt."""
    
    def __init__(self, parent, genai_wrapper, sandbox_manager, status_bar=None):
        super().__init__(parent)
        self.parent = parent
        self.genai = genai_wrapper
        self.sandbox = sandbox_manager
        self.status_bar = status_bar
        self.generated_files = {}
        self.unsaved_files = set()  # Track which files haven't been saved yet
        
        # Configure the frame
        self.configure(padding=(10, 5))
        
        # Create layout
        self._create_layout()
    
    def _create_layout(self):
        """Create the multi-file generator panel layout."""
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)  # Instructions
        self.rowconfigure(1, weight=1)  # Input area
        self.rowconfigure(2, weight=0)  # Buttons
        self.rowconfigure(3, weight=1)  # Results
        
        # Instructions
        instructions = (
            "Describe a complete project or set of files you want to generate. "
            "The AI will create all required files for the implementation."
        )
        ttk.Label(self, text=instructions, wraplength=800).grid(
            row=0, column=0, sticky="ew", pady=(0, 10)
        )
        
        # Input area with scrollbar
        input_frame = ttk.LabelFrame(self, text="Project Description")
        input_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)
        
        self.instruction_input = tk.Text(input_frame, wrap=tk.WORD, height=8)
        self.instruction_input.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        input_scrollbar = ttk.Scrollbar(
            input_frame, 
            orient=tk.VERTICAL, 
            command=self.instruction_input.yview
        )
        self.instruction_input.configure(yscrollcommand=input_scrollbar.set)
        input_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Generate button
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, sticky="ew", pady=10)
        
        ttk.Button(
            btn_frame, 
            text="Generate Files", 
            command=self.generate_files
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Clear", 
            command=self.clear_interface
        ).pack(side=tk.LEFT, padx=5)
        
        self.save_all_btn = ttk.Button(
            btn_frame, 
            text="Save All Files", 
            command=self.save_all_files,
            state=tk.DISABLED
        )
        self.save_all_btn.pack(side=tk.RIGHT, padx=5)
        
        # Results area
        result_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        result_pane.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
        
        # File list panel
        file_list_frame = ttk.LabelFrame(result_pane, text="Generated Files")
        result_pane.add(file_list_frame, weight=1)
        
        self.file_list = ttk.Treeview(
            file_list_frame,
            columns=("status",),
            selectmode="browse",
            show="tree"
        )
        self.file_list.column("#0", width=200)
        self.file_list.column("status", width=100, anchor=tk.CENTER)
        self.file_list.heading("status", text="Status")
        self.file_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Preview panel
        preview_frame = ttk.LabelFrame(result_pane, text="File Preview")
        result_pane.add(preview_frame, weight=3)
        
        # File content preview
        preview_inner = ttk.Frame(preview_frame)
        preview_inner.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.preview_text = tk.Text(
            preview_inner, 
            wrap=tk.WORD, 
            state=tk.DISABLED
        )
        preview_scrollbar = ttk.Scrollbar(
            preview_inner, 
            orient=tk.VERTICAL, 
            command=self.preview_text.yview
        )
        self.preview_text.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Save button for individual file
        self.save_file_btn = ttk.Button(
            preview_frame, 
            text="Save This File", 
            command=self.save_selected_file,
            state=tk.DISABLED
        )
        self.save_file_btn.pack(pady=5)
        
        # Bind file selection
        self.file_list.bind("<<TreeviewSelect>>", self.on_file_selected)
    
    def generate_files(self):
        """Generate multiple files based on the instruction."""
        instruction = self.instruction_input.get("1.0", tk.END).strip()
        
        if not instruction:
            if self.status_bar:
                self.status_bar.show_error("Please enter a project description")
            else:
                messagebox.showerror("Error", "Please enter a project description")
            return
        
        # Clear previous results
        self.clear_results()
        
        # Get existing files to provide as context
        existing_files = {}
        for filename in self.sandbox.list_files():
            success, content = self.sandbox.read_file(filename)
            if success:
                existing_files[filename] = content
        
        # Start progress indicator
        if self.status_bar:
            self.status_bar.start_progress("Generating files...")
        
        def generate_in_thread():
            try:
                success, files_dict = self.genai.generate_files(instruction, existing_files)
                
                # Update UI in main thread
                self.after(0, lambda: self._handle_generation_result(success, files_dict))
            except Exception as e:
                self.after(0, lambda: self._handle_generation_error(str(e)))
        
        # Run in thread to avoid UI freeze
        thread = threading.Thread(target=generate_in_thread)
        thread.daemon = True
        thread.start()
    
    def _handle_generation_result(self, success, files_dict):
        """Handle the file generation result."""
        # Stop progress indicator
        if self.status_bar:
            self.status_bar.stop_progress()
        
        if success:
            if not files_dict:
                if self.status_bar:
                    self.status_bar.show_error("No files were generated")
                return
            
            # Store generated files
            self.generated_files = files_dict
            self.unsaved_files = set(files_dict.keys())
            
            # Remove 'error' key from unsaved files if it exists
            if 'error' in self.unsaved_files:
                self.unsaved_files.remove('error')
            
            # Populate file list
            for filename in sorted(files_dict.keys()):
                if filename == "error":  # Skip error messages
                    continue
                self.file_list.insert("", "end", text=filename, values=("Unsaved",))
            
            # Enable Save All button if there are files to save
            if self.unsaved_files:
                self.save_all_btn.config(state=tk.NORMAL)
            
            # Display success message
            file_count = len(files_dict)
            if self.status_bar:
                self.status_bar.show_message(f"Generated {file_count} file(s)")
        else:
            # Show error
            error_msg = files_dict.get("error", "Unknown error during file generation")
            if self.status_bar:
                self.status_bar.show_error(error_msg)
            else:
                messagebox.showerror("Error", error_msg)
    
    def _handle_generation_error(self, error_message):
        """Handle file generation error."""
        if self.status_bar:
            self.status_bar.stop_progress()
            self.status_bar.show_error(f"Error generating files: {error_message}")
        else:
            messagebox.showerror("Error", f"Error generating files: {error_message}")
    
    def on_file_selected(self, event):
        """Handle file selection in the file list."""
        selection = self.file_list.selection()
        if not selection:
            return
        
        item = self.file_list.item(selection[0])
        filename = item["text"]
        
        if filename in self.generated_files:
            # Display file content in preview
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert(tk.END, self.generated_files[filename])
            self.preview_text.config(state=tk.DISABLED)
            
            # Enable save button if file not already saved
            if item["values"][0] == "Unsaved":
                self.save_file_btn.config(state=tk.NORMAL)
            else:
                self.save_file_btn.config(state=tk.DISABLED)
    
    def save_selected_file(self):
        """Save the currently selected file to sandbox."""
        selection = self.file_list.selection()
        if not selection:
            return
        
        item = self.file_list.item(selection[0])
        filename = item["text"]
        
        if filename not in self.generated_files:
            return
        
        # Save the file
        content = self.generated_files[filename]
        success, message = self.sandbox.write_file(filename, content)
        
        if success:
            # Update status in tree view
            self.file_list.item(selection[0], values=("Saved",))
            
            # Remove from unsaved files
            if filename in self.unsaved_files:
                self.unsaved_files.remove(filename)
            
            # Disable save button for this file
            self.save_file_btn.config(state=tk.DISABLED)
            
            # Disable save all button if all files are saved
            if not self.unsaved_files:
                self.save_all_btn.config(state=tk.DISABLED)
            
            # Show success message
            if self.status_bar:
                self.status_bar.show_message(f"Saved file: {filename}")
                
            # Refresh file list in parent application if possible
            self.event_generate("<<FilesGenerated>>")
        else:
            # Show error
            if self.status_bar:
                self.status_bar.show_error(message)
            else:
                messagebox.showerror("Error", message)
    
    def save_all_files(self):
        """Save all generated files to sandbox."""
        saved_count = 0
        error_count = 0
        
        # Make a copy of unsaved_files to iterate over while modifying the original
        files_to_save = list(self.unsaved_files)
        
        for filename in files_to_save:
            if filename == "error":  # Skip error messages
                continue
                
            content = self.generated_files.get(filename, "")
            if not content:
                continue
                
            success, message = self.sandbox.write_file(filename, content)
            
            if success:
                saved_count += 1
                
                # Remove from unsaved files
                self.unsaved_files.remove(filename)
                
                # Find tree item and update status
                for item_id in self.file_list.get_children():
                    item = self.file_list.item(item_id)
                    if item["text"] == filename:
                        self.file_list.item(item_id, values=("Saved",))
                        break
            else:
                error_count += 1
        
        # Update UI status
        if saved_count > 0:
            # Disable save buttons if all files are saved
            if not self.unsaved_files:
                self.save_all_btn.config(state=tk.DISABLED)
                self.save_file_btn.config(state=tk.DISABLED)
            
            # Show success message
            if self.status_bar:
                if error_count > 0:
                    self.status_bar.show_message(
                        f"Saved {saved_count} file(s), {error_count} failed"
                    )
                else:
                    self.status_bar.show_message(f"Saved all {saved_count} file(s)")
            
            # Refresh file list in parent application
            self.event_generate("<<FilesGenerated>>")
    
    def clear_results(self):
        """Clear the results area."""
        # Clear file list
        for item in self.file_list.get_children():
            self.file_list.delete(item)
        
        # Clear preview
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.config(state=tk.DISABLED)
        
        # Clear generated files
        self.generated_files = {}
        self.unsaved_files = set()
        
        # Disable buttons
        self.save_file_btn.config(state=tk.DISABLED)
        self.save_all_btn.config(state=tk.DISABLED)
    
    def clear_interface(self):
        """Clear the entire interface."""
        # Clear input
        self.instruction_input.delete("1.0", tk.END)
        
        # Clear results
        self.clear_results() 