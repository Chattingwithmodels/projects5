import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import threading
import io

class ImageGenPanel(ttk.Frame):
    """Panel for generating and managing images using GenAI."""
    
    def __init__(self, parent, genai_wrapper, sandbox_manager, status_bar=None):
        super().__init__(parent)
        self.parent = parent
        self.genai = genai_wrapper
        self.sandbox = sandbox_manager
        self.status_bar = status_bar
        self.current_image = None
        
        # Configure the frame
        self.configure(padding=(10, 5))
        
        # Create layout
        self._create_layout()
    
    def _create_layout(self):
        """Create the image generation panel layout."""
        # Main layout (2 columns)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Input panel (left side)
        input_frame = ttk.LabelFrame(self, text="Image Generation")
        input_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        input_frame.columnconfigure(0, weight=1)
        
        # Prompt input
        ttk.Label(input_frame, text="Enter prompt for image:").pack(anchor=tk.W, pady=(10, 0))
        
        # Prompt text area with scrollbar
        prompt_frame = ttk.Frame(input_frame)
        prompt_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.prompt_input = tk.Text(prompt_frame, height=8, width=40, wrap=tk.WORD)
        self.prompt_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        prompt_scrollbar = ttk.Scrollbar(prompt_frame, orient=tk.VERTICAL, command=self.prompt_input.yview)
        self.prompt_input.configure(yscrollcommand=prompt_scrollbar.set)
        prompt_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Example prompts dropdown
        ttk.Label(input_frame, text="Example prompts:").pack(anchor=tk.W, pady=(10, 0))
        
        example_prompts = [
            "A serene mountain landscape at sunset with a lake reflection",
            "A futuristic city with flying cars and neon lights",
            "A cute robot playing with a kitten in a garden",
            "A magical forest with glowing mushrooms and fairy lights",
            "An underwater scene with colorful coral reef and exotic fish"
        ]
        
        self.example_var = tk.StringVar()
        self.example_combo = ttk.Combobox(
            input_frame, 
            textvariable=self.example_var,
            values=example_prompts,
            state="readonly",
            width=40
        )
        self.example_combo.pack(fill=tk.X, pady=5)
        self.example_combo.bind("<<ComboboxSelected>>", self._on_example_selected)
        
        # Generate button
        generate_btn = ttk.Button(
            input_frame, 
            text="Generate Image", 
            command=self.generate_image
        )
        generate_btn.pack(pady=10)
        
        # Image display area (right side)
        preview_frame = ttk.LabelFrame(self, text="Image Preview")
        preview_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        # Canvas for image display
        self.canvas_frame = ttk.Frame(preview_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(
            self.canvas_frame, 
            bg="white", 
            width=512, 
            height=512,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Save button (initially disabled)
        self.save_btn = ttk.Button(
            preview_frame, 
            text="Save Image to Sandbox", 
            command=self.save_image,
            state=tk.DISABLED
        )
        self.save_btn.pack(pady=10)
        
        # Initial placeholder text
        self.canvas.create_text(
            256, 256, 
            text="Generated image will appear here", 
            fill="gray",
            font=("Default", 12)
        )
    
    def _on_example_selected(self, event):
        """Handle example prompt selection."""
        selected_prompt = self.example_var.get()
        self.prompt_input.delete(1.0, tk.END)
        self.prompt_input.insert(tk.END, selected_prompt)
    
    def generate_image(self):
        """Generate an image based on the prompt."""
        prompt = self.prompt_input.get(1.0, tk.END).strip()
        
        if not prompt:
            if self.status_bar:
                self.status_bar.show_error("Please enter a prompt")
            return
        
        # Show progress
        if self.status_bar:
            self.status_bar.start_progress("Generating image...")
        
        def generate_in_thread():
            try:
                success, image, message = self.genai.generate_image(prompt)
                
                # Update UI in main thread
                self.after(0, lambda: self._handle_image_result(success, image, message))
            except Exception as e:
                self.after(0, lambda: self._handle_image_error(str(e)))
        
        # Run in thread to avoid UI freeze
        thread = threading.Thread(target=generate_in_thread)
        thread.daemon = True
        thread.start()
    
    def _handle_image_result(self, success, image, message):
        """Handle the image generation result."""
        # Stop progress indicator
        if self.status_bar:
            self.status_bar.stop_progress()
        
        if success and image:
            # Store the image
            self.current_image = image
            
            # Display the image on canvas
            self._display_image(image)
            
            # Enable save button
            self.save_btn.config(state=tk.NORMAL)
            
            # Show success message
            if self.status_bar:
                self.status_bar.show_message("Image generated successfully")
        else:
            # Show error
            if self.status_bar:
                self.status_bar.show_error(message)
            
            # Clear canvas and disable save button
            self._clear_canvas()
            self.save_btn.config(state=tk.DISABLED)
    
    def _handle_image_error(self, error_message):
        """Handle image generation error."""
        if self.status_bar:
            self.status_bar.stop_progress()
            self.status_bar.show_error(f"Error generating image: {error_message}")
        
        # Clear canvas and disable save button
        self._clear_canvas()
        self.save_btn.config(state=tk.DISABLED)
    
    def _display_image(self, image):
        """Display an image on the canvas."""
        # Clear canvas
        self.canvas.delete("all")
        
        # Resize image to fit canvas while maintaining aspect ratio
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Ensure canvas dimensions are valid
        if canvas_width <= 1:
            canvas_width = 512
        if canvas_height <= 1:
            canvas_height = 512
            
        # Calculate new dimensions
        img_width, img_height = image.size
        ratio = min(canvas_width/img_width, canvas_height/img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        
        # Resize image
        resized_img = image.resize((new_width, new_height), Image.LANCZOS)
        
        # Convert to PhotoImage for display
        self.photo_image = ImageTk.PhotoImage(resized_img)
        
        # Calculate position for centering
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2
        
        # Display on canvas
        self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo_image)
    
    def _clear_canvas(self):
        """Clear the canvas and display placeholder text."""
        self.canvas.delete("all")
        self.canvas.create_text(
            256, 256, 
            text="Generated image will appear here", 
            fill="gray",
            font=("Default", 12)
        )
    
    def save_image(self):
        """Save the generated image to the sandbox."""
        if not self.current_image:
            return
        
        # Ask for filename
        filename = filedialog.asksaveasfilename(
            initialdir=self.sandbox.sandbox_dir,
            title="Save Image As",
            filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")],
            defaultextension=".jpg"
        )
        
        if not filename:
            return
        
        # Extract just the filename without path
        basename = os.path.basename(filename)
        
        # Check if valid for sandbox
        is_valid, path_or_error = self.sandbox._validate_path(basename)
        if not is_valid:
            if self.status_bar:
                self.status_bar.show_error(path_or_error)
            else:
                messagebox.showerror("Error", path_or_error)
            return
        
        # Save image via genai wrapper
        success, message = self.genai.save_image(self.current_image, path_or_error)
        
        if success:
            if self.status_bar:
                self.status_bar.show_message(f"Image saved to sandbox as {basename}")
        else:
            if self.status_bar:
                self.status_bar.show_error(message)
            else:
                messagebox.showerror("Error", message)
    
    def on_resize(self, event=None):
        """Handle canvas resize event."""
        if hasattr(self, 'current_image') and self.current_image:
            self._display_image(self.current_image) 