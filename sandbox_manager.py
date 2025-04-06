import os
import pathlib
import re
import shutil
from typing import List, Optional, Tuple, Dict

class SandboxManager:
    """Manages all file operations within a sandboxed directory."""
    
    def __init__(self, sandbox_path: str = "~/.my_sandbox"):
        """Initialize the sandbox directory."""
        self.sandbox_dir = os.path.abspath(os.path.expanduser(sandbox_path))
        self._ensure_sandbox_exists()
        
    def _ensure_sandbox_exists(self) -> None:
        """Create the sandbox directory if it doesn't exist."""
        if not os.path.exists(self.sandbox_dir):
            os.makedirs(self.sandbox_dir)
            print(f"Created sandbox directory at: {self.sandbox_dir}")
        else:
            print(f"Using existing sandbox at: {self.sandbox_dir}")
    
    def _validate_path(self, filepath: str) -> Tuple[bool, str]:
        """
        Validate if path is within sandbox and sanitize filename.
        Returns (is_valid, full_path_or_error).
        """
        # Sanitize filename
        filename = os.path.basename(filepath)
        
        # Basic validation - only allow alphanumeric, underscore, dash, dot 
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', filename):
            return False, "Invalid filename. Use only letters, numbers, underscore, dash and dot."
        
        # Prevent hidden files
        if filename.startswith('.'):
            return False, "Hidden files are not allowed."
            
        # Allowed extensions (text-based files only)
        allowed_extensions = ['.py', '.txt', '.md', '.json', '.html', '.css', '.js', '.csv']
        _, ext = os.path.splitext(filename)
        if ext.lower() not in allowed_extensions:
            return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        
        # Construct full path and validate it's within sandbox
        full_path = os.path.abspath(os.path.join(self.sandbox_dir, filename))
        if not os.path.commonpath([self.sandbox_dir]) == os.path.commonpath([self.sandbox_dir, full_path]):
            return False, "Path traversal attempt detected."
            
        return True, full_path
    
    def list_files(self) -> List[str]:
        """List all files in the sandbox."""
        try:
            return [f for f in os.listdir(self.sandbox_dir) 
                   if os.path.isfile(os.path.join(self.sandbox_dir, f))]
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
    
    def read_file(self, filename: str) -> Tuple[bool, str]:
        """Read a file from the sandbox."""
        is_valid, path_or_error = self._validate_path(filename)
        if not is_valid:
            return False, path_or_error
            
        try:
            with open(path_or_error, 'r', encoding='utf-8') as file:
                content = file.read()
            return True, content
        except Exception as e:
            return False, f"Error reading file: {e}"
    
    def write_file(self, filename: str, content: str) -> Tuple[bool, str]:
        """Write content to a file in the sandbox."""
        is_valid, path_or_error = self._validate_path(filename)
        if not is_valid:
            return False, path_or_error
            
        try:
            with open(path_or_error, 'w', encoding='utf-8') as file:
                file.write(content)
            return True, f"Successfully wrote to {filename}"
        except Exception as e:
            return False, f"Error writing file: {e}"
            
    def append_file(self, filename: str, content: str) -> Tuple[bool, str]:
        """Append content to a file in the sandbox."""
        is_valid, path_or_error = self._validate_path(filename)
        if not is_valid:
            return False, path_or_error
            
        try:
            with open(path_or_error, 'a', encoding='utf-8') as file:
                file.write(content)
            return True, f"Successfully appended to {filename}"
        except Exception as e:
            return False, f"Error appending to file: {e}"
    
    def delete_file(self, filename: str) -> Tuple[bool, str]:
        """Delete a file from the sandbox."""
        is_valid, path_or_error = self._validate_path(filename)
        if not is_valid:
            return False, path_or_error
            
        if not os.path.exists(path_or_error):
            return False, f"File {filename} does not exist."
            
        try:
            os.remove(path_or_error)
            return True, f"Successfully deleted {filename}"
        except Exception as e:
            return False, f"Error deleting file: {e}"
            
    def rename_file(self, old_name: str, new_name: str) -> Tuple[bool, str]:
        """Rename a file in the sandbox."""
        is_valid_old, old_path = self._validate_path(old_name)
        if not is_valid_old:
            return False, old_path
            
        is_valid_new, new_path = self._validate_path(new_name)
        if not is_valid_new:
            return False, new_path
            
        if not os.path.exists(old_path):
            return False, f"File {old_name} does not exist."
            
        if os.path.exists(new_path):
            return False, f"File {new_name} already exists."
            
        try:
            shutil.move(old_path, new_path)
            return True, f"Successfully renamed {old_name} to {new_name}"
        except Exception as e:
            return False, f"Error renaming file: {e}"
