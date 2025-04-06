import tkinter as tk
from tkinter import ttk, simpledialog
import json
import os

class SettingsPanel(ttk.Frame):
    """Settings panel for configuring models and system prompts."""
    
    def __init__(self, parent, genai_wrapper, status_bar=None):
        super().__init__(parent)
        self.parent = parent
        self.genai = genai_wrapper
        self.status_bar = status_bar
        self.settings_file = os.path.join(
            os.path.expanduser("~"), 
            ".sandbox_ide_settings.json"
        )
        
        # Default settings
        self.settings = {
            "model": "gemini-2.0-flash-001",
            "image_model": "imagen-3.0-generate-002",
            "system_prompt": "",
            "temperature": 0.7,
            "max_output_tokens": 8192,
            "top_p": 0.95,
            "top_k": 40
        }
        
        # Available models (could be expanded based on the API's capabilities)
        self.available_models = [
            "gemini-2.0-flash-001",
            "gemini-2.0-pro-001",
            "gemini-1.5-flash-001",
            "gemini-1.5-pro-001",
            "gemini-1.0-pro-001",
            "imagen-3.0-generate-002"  # Image generation model
        ]
        
        # Initialize model variables
        self.model_var = tk.StringVar(value=self.settings["model"])
        self.image_model_var = tk.StringVar(value=self.settings["image_model"])
        self.temp_var = tk.DoubleVar(value=self.settings["temperature"])
        self.max_tokens_var = tk.IntVar(value=self.settings["max_output_tokens"])
        self.top_p_var = tk.DoubleVar(value=self.settings["top_p"])
        self.top_k_var = tk.IntVar(value=self.settings["top_k"])
        
        # Load existing settings
        self.load_settings()
        
        # Update variables with loaded settings
        self.model_var.set(self.settings["model"])
        self.image_model_var.set(self.settings.get("image_model", "imagen-3.0-generate-002"))
        self.temp_var.set(self.settings["temperature"])
        self.max_tokens_var.set(self.settings["max_output_tokens"])
        self.top_p_var.set(self.settings["top_p"])
        self.top_k_var.set(self.settings["top_k"])
        
        # Update the genai wrapper with current settings
        self.apply_settings_to_genai()
        
        # Configure the frame
        self.configure(padding=(10, 5))
        
        # Create layout
        self._create_layout()
    
    def _create_layout(self):
        """Create the settings panel layout."""
        # Main container with tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create Model Settings tab
        self.model_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.model_frame, text="Model Settings")
        
        # Model selection
        ttk.Label(self.model_frame, text="Text Model:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.model_combo = ttk.Combobox(
            self.model_frame, 
            textvariable=self.model_var,
            values=[m for m in self.available_models if not m.startswith("imagen")],
            state="readonly",
            width=30
        )
        self.model_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.model_combo.bind("<<ComboboxSelected>>", self.on_model_change)
        
        # Image generation model
        ttk.Label(self.model_frame, text="Image Model:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.image_model_combo = ttk.Combobox(
            self.model_frame, 
            textvariable=self.image_model_var,
            values=[m for m in self.available_models if m.startswith("imagen")],
            state="readonly",
            width=30
        )
        self.image_model_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Temperature
        ttk.Label(self.model_frame, text="Temperature:").grid(row=2, column=0, sticky=tk.W, pady=5)
        temp_frame = ttk.Frame(self.model_frame)
        temp_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.temp_scale = ttk.Scale(
            temp_frame,
            from_=0.0,
            to=1.0,
            orient=tk.HORIZONTAL,
            variable=self.temp_var,
            length=200,
            command=self._update_temp_label
        )
        self.temp_scale.pack(side=tk.LEFT)
        
        self.temp_label = ttk.Label(temp_frame, text=f"{self.settings['temperature']:.1f}")
        self.temp_label.pack(side=tk.LEFT, padx=5)
        
        # Max output tokens
        ttk.Label(self.model_frame, text="Max Output Tokens:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.max_tokens_entry = ttk.Spinbox(
            self.model_frame,
            from_=100,
            to=32768,
            increment=100,
            textvariable=self.max_tokens_var,
            width=10
        )
        self.max_tokens_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Top P
        ttk.Label(self.model_frame, text="Top P:").grid(row=4, column=0, sticky=tk.W, pady=5)
        top_p_frame = ttk.Frame(self.model_frame)
        top_p_frame.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.top_p_scale = ttk.Scale(
            top_p_frame,
            from_=0.0,
            to=1.0,
            orient=tk.HORIZONTAL,
            variable=self.top_p_var,
            length=200,
            command=self._update_top_p_label
        )
        self.top_p_scale.pack(side=tk.LEFT)
        
        self.top_p_label = ttk.Label(top_p_frame, text=f"{self.settings['top_p']:.2f}")
        self.top_p_label.pack(side=tk.LEFT, padx=5)
        
        # Top K
        ttk.Label(self.model_frame, text="Top K:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.top_k_entry = ttk.Spinbox(
            self.model_frame,
            from_=1,
            to=100,
            increment=1,
            textvariable=self.top_k_var,
            width=10
        )
        self.top_k_entry.grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        
        # System Prompt tab
        self.prompt_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.prompt_frame, text="System Prompt")
        
        # System prompt entry
        ttk.Label(
            self.prompt_frame, 
            text="System Prompt (instructions to guide the model's behavior):"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        prompt_frame = ttk.Frame(self.prompt_frame)
        prompt_frame.pack(fill=tk.BOTH, expand=True)
        
        self.system_prompt = tk.Text(
            prompt_frame,
            height=10,
            width=50,
            wrap=tk.WORD
        )
        self.system_prompt.insert("1.0", self.settings["system_prompt"])
        
        # Add scrollbar
        prompt_scrollbar = ttk.Scrollbar(
            prompt_frame, 
            orient=tk.VERTICAL, 
            command=self.system_prompt.yview
        )
        self.system_prompt.configure(yscrollcommand=prompt_scrollbar.set)
        
        # Pack elements
        self.system_prompt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        prompt_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Apply button
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            btn_frame, 
            text="Apply Settings", 
            command=self.apply_settings
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Reset to Defaults", 
            command=self.reset_to_defaults
        ).pack(side=tk.RIGHT, padx=5)
    
    def _update_temp_label(self, value):
        """Update the temperature label."""
        self.temp_label.config(text=f"{float(value):.1f}")
    
    def _update_top_p_label(self, value):
        """Update the top p label."""
        self.top_p_label.config(text=f"{float(value):.2f}")
    
    def on_model_change(self, event):
        """Handle model selection change."""
        selected_model = self.model_var.get()
        # Update UI or settings based on model selection
        
    def apply_settings(self):
        """Apply the current settings to the genai wrapper."""
        # Collect current settings
        self.settings["model"] = self.model_var.get()
        self.settings["image_model"] = self.image_model_var.get()
        self.settings["temperature"] = self.temp_var.get()
        self.settings["max_output_tokens"] = self.max_tokens_var.get()
        self.settings["top_p"] = self.top_p_var.get()
        self.settings["top_k"] = self.top_k_var.get()
        self.settings["system_prompt"] = self.system_prompt.get("1.0", tk.END).strip()
        
        # Apply to genai wrapper
        self.apply_settings_to_genai()
        
        # Save settings
        self.save_settings()
        
        # Show confirmation
        if self.status_bar:
            self.status_bar.show_message("Settings applied successfully")
    
    def apply_settings_to_genai(self):
        """Apply settings to genai wrapper."""
        self.genai.model = self.settings["model"]
        self.genai.image_model = self.settings["image_model"]
        self.genai.system_prompt = self.settings["system_prompt"]
        self.genai.generation_config = {
            "temperature": self.settings["temperature"],
            "max_output_tokens": self.settings["max_output_tokens"],
            "top_p": self.settings["top_p"],
            "top_k": self.settings["top_k"]
        }
    
    def reset_to_defaults(self):
        """Reset settings to defaults."""
        default_settings = {
            "model": "gemini-2.0-flash-001",
            "image_model": "imagen-3.0-generate-002",
            "system_prompt": "",
            "temperature": 0.7,
            "max_output_tokens": 8192,
            "top_p": 0.95,
            "top_k": 40
        }
        
        # Update UI
        self.model_var.set(default_settings["model"])
        self.image_model_var.set(default_settings["image_model"])
        self.temp_var.set(default_settings["temperature"])
        self._update_temp_label(default_settings["temperature"])
        self.max_tokens_var.set(default_settings["max_output_tokens"])
        self.top_p_var.set(default_settings["top_p"])
        self._update_top_p_label(default_settings["top_p"])
        self.top_k_var.set(default_settings["top_k"])
        
        self.system_prompt.delete("1.0", tk.END)
        self.system_prompt.insert("1.0", default_settings["system_prompt"])
        
        # Apply defaults
        self.settings = default_settings.copy()
        self.apply_settings_to_genai()
        self.save_settings()
        
        if self.status_bar:
            self.status_bar.show_message("Settings reset to defaults")
    
    def load_settings(self):
        """Load settings from file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Update settings with loaded values
                    self.settings.update(loaded_settings)
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save settings to file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}") 