import os
import json
from typing import Optional, Dict, Any, Tuple, List
import base64
import tempfile
from PIL import Image
import io
from google import genai
from google.genai import types

class GenAIWrapper:
    """Wrapper for Google's GenAI SDK."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the GenAI client."""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Set GOOGLE_API_KEY environment variable or provide directly.")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.0-flash-001"  # Default model - more likely to be available
        self.image_model = "imagen-3.0-generate-002"  # Default image model
        self.system_prompt = ""  # Default system prompt
        self.generation_config = {  # Default generation config
            "temperature": 0.7,
            "max_output_tokens": 8192,
            "top_p": 0.95,
            "top_k": 40
        }
        
        # Initialize available models
        self.available_text_models = []
        self.available_image_models = []
        self.available_embedding_models = []  # New category for embedding models
        self.fetch_available_models()
    
    def fetch_available_models(self) -> Tuple[bool, str]:
        """Fetch available models from the API.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Get all available models
            all_models = self.client.list_models()
            self.available_text_models = []
            self.available_image_models = []
            self.available_embedding_models = []  # New category for embedding models
            
            # Print available models for debugging
            print("Available models from API:")
            for model in all_models:
                model_id = model.name
                if 'gemini' in model_id.lower() and 'embedding' in model_id.lower():
                    print(f"- {model_id} (Embedding model)")
                    self.available_embedding_models.append(model_id)
                elif 'gemini' in model_id.lower():
                    print(f"- {model_id} (Text model)")
                    self.available_text_models.append(model_id)
                elif 'imagen' in model_id.lower():
                    print(f"- {model_id} (Image model)")
                    self.available_image_models.append(model_id)
                elif 'gemma' in model_id.lower():
                    print(f"- {model_id} (Other model)")
                    self.available_text_models.append(model_id)
                elif 'embedding' in model_id.lower():
                    print(f"- {model_id} (Embedding model)")
                    self.available_embedding_models.append(model_id)
                else:
                    print(f"- {model_id} (Other)")
            
            # Default embedding models
            if not self.available_embedding_models:
                self.available_embedding_models = [
                    "gemini-embedding-exp-03-07",  # Experimental Gemini-based embeddings
                    "text-embedding-004"           # Standard text embeddings
                ]
            
            # If no models were found, add these safe defaults including newer models
            if not self.available_text_models:
                self.available_text_models = [
                    "gemini-2.5-pro-preview-03-25",     # Newest Gemini 2.5 Pro (billing enabled)
                    "gemini-2.5-pro-exp-03-25",         # Experimental Gemini 2.5 Pro (free tier)
                    "gemini-2.0-flash-001",             # Gemini 2.0 Flash
                    "gemini-2.0-pro-001",               # Gemini 2.0 Pro
                    "gemini-2.0-flash-lite",            # Gemini 2.0 Flash-Lite
                    "gemini-1.5-flash-001",             # Gemini 1.5 Flash
                    "gemini-1.5-pro-001",               # Gemini 1.5 Pro
                    "gemma-3-27b-it",                   # Gemma 3 27B
                    "gemini-1.0-pro-001"                # Gemini 1.0 Pro (legacy)
                ]
            
            if not self.available_image_models:
                self.available_image_models = [
                    "imagen-3.0-generate-002",
                    "gemini-2.0-flash-imagen"           # Experimental Gemini with image generation/editing
                ]
            
            # Sort models from newest to oldest versions
            def model_priority(model_name):
                model_name = model_name.lower()
                # Version-based priority
                if '2.5' in model_name:
                    base_priority = 0  # Highest priority
                elif '2.0' in model_name:
                    base_priority = 10
                elif '1.5' in model_name:
                    base_priority = 20
                elif 'gemma-3' in model_name:
                    base_priority = 5
                elif '1.0' in model_name:
                    base_priority = 30
                else:
                    base_priority = 40  # Lowest priority
                
                # Model type refinement
                if 'pro' in model_name and 'preview' in model_name:
                    return base_priority     # Pro preview gets highest within version
                elif 'pro' in model_name and 'exp' in model_name:
                    return base_priority + 1 # Experimental pro
                elif 'pro' in model_name:
                    return base_priority + 2 # Regular pro 
                elif 'flash' in model_name and 'lite' in model_name:
                    return base_priority + 4 # Flash lite
                elif 'flash' in model_name:
                    return base_priority + 3 # Flash
                else:
                    return base_priority + 5
                
            self.available_text_models.sort(key=model_priority)
            
            # Ensure current models are in the available lists
            if self.model not in self.available_text_models and self.available_text_models:
                self.model = self.available_text_models[0]
                
            if self.image_model not in self.available_image_models and self.available_image_models:
                self.image_model = self.available_image_models[0]
                
            return True, f"Found {len(self.available_text_models)} text models, {len(self.available_image_models)} image models, and {len(self.available_embedding_models)} embedding models"
        except Exception as e:
            # Use defaults on error including newer models
            self.available_text_models = [
                "gemini-2.5-pro-preview-03-25",     # Newest Gemini 2.5 Pro (billing enabled)
                "gemini-2.5-pro-exp-03-25",         # Experimental Gemini 2.5 Pro (free tier)
                "gemini-2.0-flash-001",             # Gemini 2.0 Flash
                "gemini-2.0-pro-001",               # Gemini 2.0 Pro
                "gemini-2.0-flash-lite",            # Gemini 2.0 Flash-Lite
                "gemini-1.5-flash-001",             # Gemini 1.5 Flash
                "gemini-1.5-pro-001",               # Gemini 1.5 Pro
                "gemma-3-27b-it",                   # Gemma 3 27B
                "gemini-1.0-pro-001"                # Gemini 1.0 Pro (legacy)
            ]
            self.available_image_models = [
                "imagen-3.0-generate-002", 
                "gemini-2.0-flash-imagen"
            ]
            return False, f"Error fetching models: {e}"
    
    def test_model_availability(self, model_name: str) -> Tuple[bool, str]:
        """Test if a specific model is available and working.
        
        Args:
            model_name: The name of the model to test
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Try a simple request to see if the model works
            response = self.client.models.generate_content(
                model=model_name,
                contents="Hello",
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=10
                )
            )
            
            # If we get here, the model is available
            return True, f"Model {model_name} is available"
        except Exception as e:
            return False, f"Model {model_name} is not available: {str(e)}"
    
    def get_available_text_models(self) -> List[str]:
        """Get the list of available text models.
        
        Returns:
            List of model names
        """
        return self.available_text_models
    
    def get_available_image_models(self) -> List[str]:
        """Get the list of available image models.
        
        Returns:
            List of model names
        """
        return self.available_image_models
    
    def ask_question(self, question: str, context: Optional[str] = None) -> Tuple[bool, str]:
        """Ask a question to the model."""
        try:
            prompt = question
            if context:
                prompt = f"Context:\n{context}\n\nQuestion: {question}"
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    temperature=self.generation_config["temperature"],
                    max_output_tokens=self.generation_config["max_output_tokens"],
                    top_p=self.generation_config["top_p"],
                    top_k=self.generation_config["top_k"]
                )
            )
            
            return True, response.text
        except Exception as e:
            return False, f"Error in AI processing: {e}"
    
    def explain_code(self, code: str) -> Tuple[bool, str]:
        """Have the model explain code."""
        try:
            prompt = f"Explain this code in detail, breaking down its functionality and purpose:\n\n```\n{code}\n```"
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    temperature=self.generation_config["temperature"],
                    max_output_tokens=self.generation_config["max_output_tokens"],
                    top_p=self.generation_config["top_p"],
                    top_k=self.generation_config["top_k"]
                )
            )
            
            return True, response.text
        except Exception as e:
            return False, f"Error in AI processing: {e}"
    
    def refactor_code(self, code: str, instruction: str) -> Tuple[bool, str]:
        """Have the model refactor code according to instructions."""
        try:
            prompt = (
                f"Refactor this code according to the following instructions. "
                f"Return only the refactored code, no explanations:\n\n"
                f"Instructions: {instruction}\n\n"
                f"Code:\n```\n{code}\n```"
            )
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    temperature=self.generation_config["temperature"],
                    max_output_tokens=self.generation_config["max_output_tokens"],
                    top_p=self.generation_config["top_p"],
                    top_k=self.generation_config["top_k"]
                )
            )
            
            return True, response.text
        except Exception as e:
            return False, f"Error in AI processing: {e}"
    
    def generate_documentation(self, code: str) -> Tuple[bool, str]:
        """Have the model generate documentation for code."""
        try:
            prompt = (
                f"Generate comprehensive documentation for this code. "
                f"Include docstrings, function/class descriptions, and parameter details:\n\n"
                f"```\n{code}\n```"
            )
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    temperature=self.generation_config["temperature"],
                    max_output_tokens=self.generation_config["max_output_tokens"],
                    top_p=self.generation_config["top_p"],
                    top_k=self.generation_config["top_k"]
                )
            )
            
            return True, response.text
        except Exception as e:
            return False, f"Error in AI processing: {e}"
    
    def suggest_improvements(self, code: str) -> Tuple[bool, str]:
        """Have the model suggest improvements for code."""
        try:
            prompt = (
                f"Analyze this code and suggest improvements for readability, "
                f"performance, and best practices:\n\n"
                f"```\n{code}\n```"
            )
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    temperature=self.generation_config["temperature"],
                    max_output_tokens=self.generation_config["max_output_tokens"],
                    top_p=self.generation_config["top_p"],
                    top_k=self.generation_config["top_k"]
                )
            )
            
            return True, response.text
        except Exception as e:
            return False, f"Error in AI processing: {e}"
    
    def modify_with_instruction(self, code: str, instruction: str) -> Tuple[bool, str]:
        """Modify code based on user instruction."""
        try:
            prompt = (
                f"Modify this code according to the following instruction. "
                f"Return only the modified code, no explanations:\n\n"
                f"Instruction: {instruction}\n\n"
                f"Code:\n```\n{code}\n```"
            )
            
            system_instruction = (
                "You are a code editor assistant. Your task is to modify the provided code "
                "according to the user's instructions. Only return the modified code, "
                "do not include any explanations or markdown formatting."
            )
            
            if self.system_prompt:
                system_instruction = f"{self.system_prompt}\n\n{system_instruction}"
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=self.generation_config["temperature"],
                    max_output_tokens=self.generation_config["max_output_tokens"],
                    top_p=self.generation_config["top_p"],
                    top_k=self.generation_config["top_k"]
                )
            )
            
            return True, response.text
        except Exception as e:
            return False, f"Error in AI processing: {e}"
    
    def generate_files(self, instruction: str, existing_files: Optional[Dict[str, str]] = None) -> Tuple[bool, Dict[str, str]]:
        """Generate multiple files based on an instruction.
        
        Args:
            instruction: The instruction for file generation
            existing_files: Optional dictionary of existing files {filename: content}
            
        Returns:
            Tuple of (success, files_dict) where files_dict is {filename: content}
        """
        try:
            # Prepare context from existing files
            context = ""
            if existing_files:
                context = "Existing files in the project:\n\n"
                for filename, content in existing_files.items():
                    context += f"File: {filename}\n```\n{content}\n```\n\n"
            
            prompt = (
                f"{context}\n"
                f"Based on the following instruction, generate all the necessary files for the task. "
                f"For each file, include the filename and the complete file content.\n\n"
                f"Instruction: {instruction}\n\n"
                f"Format your response like this:\n"
                f"FILENAME: example.py\n"
                f"```python\n"
                f"# File content goes here\n"
                f"```\n\n"
                f"FILENAME: another_file.js\n"
                f"```javascript\n"
                f"// Another file content\n"
                f"```\n"
            )
            
            system_instruction = (
                "You are a helpful programming assistant. Your task is to generate multiple files "
                "based on the user's instructions. For each file, include the complete filename and "
                "the full file content. Use the format 'FILENAME: [filename]' followed by the content "
                "in a code block. Ensure the files work together as a coherent solution."
            )
            
            if self.system_prompt:
                system_instruction = f"{self.system_prompt}\n\n{system_instruction}"
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=self.generation_config["temperature"],
                    max_output_tokens=self.generation_config["max_output_tokens"],
                    top_p=self.generation_config["top_p"],
                    top_k=self.generation_config["top_k"]
                )
            )
            
            # Parse the response to extract files
            files_dict = self._parse_files_response(response.text)
            
            return True, files_dict
        except Exception as e:
            return False, {"error": f"Error in AI processing: {e}"}
    
    def _parse_files_response(self, response_text: str) -> Dict[str, str]:
        """Parse the response text to extract filename and contents."""
        files_dict = {}
        parts = response_text.split("FILENAME: ")
        
        for part in parts[1:]:  # Skip the first empty part
            lines = part.strip().split("\n")
            if not lines:
                continue
                
            filename = lines[0].strip()
            if not filename:
                continue
                
            # Find code block boundaries
            content_start = part.find("```")
            if content_start == -1:
                content = "\n".join(lines[1:])
            else:
                # Find the end of the first code block
                content_start = part.find("\n", content_start) + 1
                content_end = part.find("```", content_start)
                if content_end == -1:
                    content = part[content_start:]
                else:
                    content = part[content_start:content_end]
            
            # Clean up the content
            content = content.strip()
            
            # Store in dictionary
            files_dict[filename] = content
        
        return files_dict
    
    def generate_image(self, prompt: str, model: str = "imagen-3.0-generate-002") -> Tuple[bool, Optional[Image.Image], str]:
        """Generate an image based on a prompt.
        
        Args:
            prompt: Text description of the desired image
            model: Image model to use, defaults to Imagen 3.0
            
        Returns:
            Tuple of (success, image_object, message)
        """
        try:
            # Check if prompt is too short
            if len(prompt.strip()) < 3:
                return False, None, "Prompt is too short. Please provide a more detailed description."
                
            # Prepare configuration
            generation_config = types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type='image/jpeg',
                guidance_scale=9.0  # Higher values adhere more closely to prompt
            )
            
            # Generate image with error handling
            try:
                response = self.client.models.generate_images(
                    model=model,
                    prompt=prompt,
                    config=generation_config
                )
            except genai.ModelError as model_err:
                return False, None, f"Model Error: {str(model_err)}"
            except genai.PermissionDeniedError as perm_err:
                return False, None, f"Permission denied: {str(perm_err)}"
            except genai.QuotaExceededError as quota_err:
                return False, None, f"Quota exceeded: {str(quota_err)}"
            
            # Process response
            if not hasattr(response, 'generated_images') or not response.generated_images:
                return False, None, "No images were generated in the response"
            
            # First image from the response
            if len(response.generated_images) > 0 and hasattr(response.generated_images[0], 'image'):
                image_data = response.generated_images[0].image
                
                # Handle different image return types
                if isinstance(image_data, Image.Image):
                    # Already a PIL Image
                    return True, image_data, "Image generated successfully"
                elif isinstance(image_data, str) and image_data.startswith('data:image'):
                    # Base64 data
                    image_data = image_data.split(',')[1]
                    image = Image.open(io.BytesIO(base64.b64decode(image_data)))
                    return True, image, "Image generated successfully"
                elif isinstance(image_data, bytes):
                    # Raw image bytes
                    image = Image.open(io.BytesIO(image_data))
                    return True, image, "Image generated successfully"
                elif hasattr(image_data, 'data') and isinstance(image_data.data, bytes):
                    # Google API image type with binary data
                    image = Image.open(io.BytesIO(image_data.data))
                    return True, image, "Image generated successfully"
                elif hasattr(image_data, 'data') and isinstance(image_data.data, str):
                    # Google API image type with base64 data
                    image = Image.open(io.BytesIO(base64.b64decode(image_data.data)))
                    return True, image, "Image generated successfully"
                elif hasattr(image_data, '__dict__'):
                    # Google genai types.Image - handle this explicitly 
                    try:
                        # Try to access binary data via an attribute
                        if hasattr(image_data, 'data'):
                            image_bytes = image_data.data
                        elif hasattr(image_data, 'image_bytes'):
                            image_bytes = image_data.image_bytes
                        elif hasattr(image_data, 'bytes'):
                            image_bytes = image_data.bytes
                        else:
                            # Try to get data from the dict
                            dict_data = image_data.__dict__
                            for attr in dict_data:
                                if isinstance(dict_data[attr], bytes):
                                    image_bytes = dict_data[attr]
                                    break
                                elif isinstance(dict_data[attr], str) and dict_data[attr].startswith('data:image'):
                                    data = dict_data[attr].split(',')[1]
                                    image_bytes = base64.b64decode(data)
                                    break
                            else:
                                return False, None, f"Couldn't extract image data from {type(image_data)}"
                        
                        # Convert to PIL Image
                        image = Image.open(io.BytesIO(image_bytes))
                        return True, image, "Image generated successfully"
                    except Exception as e:
                        return False, None, f"Error processing image data: {str(e)}"
                else:
                    return False, None, f"Unsupported image format returned: {type(image_data)}"
            else:
                return False, None, "Generated image data is invalid"
                
        except Exception as e:
            return False, None, f"Error generating image: {str(e)}"
    
    def save_image(self, image: Image.Image, path: str) -> Tuple[bool, str]:
        """Save an image to disk.
        
        Args:
            image: PIL Image object
            path: Path to save the image
            
        Returns:
            Tuple of (success, message)
        """
        try:
            image.save(path)
            return True, f"Image saved to {path}"
        except Exception as e:
            return False, f"Error saving image: {e}"
    
    def generate_embedding(self, text: str, model: Optional[str] = None) -> Tuple[bool, Optional[List[float]], str]:
        """Generate an embedding vector for the given text.
        
        Args:
            text: The text to embed
            model: Optional specific embedding model to use
            
        Returns:
            Tuple of (success, embedding_vector, message)
        """
        try:
            # Use specified model or default to first available embedding model
            embedding_model = model
            if not embedding_model and self.available_embedding_models:
                embedding_model = self.available_embedding_models[0]
                
            if not embedding_model:
                return False, None, "No embedding model available"
                
            # Generate embedding
            response = self.client.models.embed_content(
                model=embedding_model,
                contents=text
            )
            
            # Extract embedding vector
            if hasattr(response, 'embedding'):
                return True, response.embedding, "Embedding generated successfully"
            else:
                return False, None, "Failed to generate embedding"
                
        except Exception as e:
            return False, None, f"Error generating embedding: {str(e)}"
