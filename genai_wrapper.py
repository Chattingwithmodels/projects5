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
        self.model = "gemini-2.0-flash-001"  # Default model
        self.image_model = "imagen-3.0-generate-002"  # Default image model
        self.system_prompt = ""  # Default system prompt
        self.generation_config = {  # Default generation config
            "temperature": 0.7,
            "max_output_tokens": 8192,
            "top_p": 0.95,
            "top_k": 40
        }
    
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
    
    def generate_image(self, prompt: str) -> Tuple[bool, Optional[Image.Image], str]:
        """Generate an image based on a prompt.
        
        Args:
            prompt: Text description of the desired image
            
        Returns:
            Tuple of (success, image_object, message)
        """
        try:
            response = self.client.models.generate_images(
                model=self.image_model,
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    output_mime_type='image/jpeg',
                    guidance_scale=9.0  # Higher values adhere more closely to prompt
                )
            )
            
            if response.generated_images and len(response.generated_images) > 0:
                # First image from the response
                image = response.generated_images[0].image
                return True, image, "Image generated successfully"
            else:
                return False, None, "No images were generated"
        except Exception as e:
            return False, None, f"Error generating image: {e}"
    
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
