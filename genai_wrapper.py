import os
import json
from typing import Optional, Dict, Any, Tuple
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
        self.model = "gemini-2.0-flash-001"  # Using Gemini 2.0 Flash for faster responses
    
    def ask_question(self, question: str, context: Optional[str] = None) -> Tuple[bool, str]:
        """Ask a question to the model."""
        try:
            prompt = question
            if context:
                prompt = f"Context:\n{context}\n\nQuestion: {question}"
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
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
                contents=prompt
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
                contents=prompt
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
                contents=prompt
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
                contents=prompt
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
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            )
            
            return True, response.text
        except Exception as e:
            return False, f"Error in AI processing: {e}"
