import os
import sys
import cmd
from typing import List, Optional

class SandboxCLI(cmd.Cmd):
    """Command-line interface for the sandbox IDE assistant."""
    
    intro = "Welcome to the Sandbox IDE Assistant! Type 'help' to see available commands."
    prompt = "sandbox> "
    
    def __init__(self, sandbox_manager, genai_wrapper):
        super().__init__()
        self.sandbox = sandbox_manager
        self.genai = genai_wrapper
        
    def do_list(self, arg):
        """List all files in the sandbox."""
        files = self.sandbox.list_files()
        if files:
            print("Files in sandbox:")
            for file in files:
                print(f"  - {file}")
        else:
            print("No files found in sandbox.")
    
    def do_read(self, arg):
        """Read a file: read <filename>"""
        if not arg:
            print("Usage: read <filename>")
            return
        
        success, result = self.sandbox.read_file(arg)
        if success:
            print(f"\n--- Content of {arg} ---\n")
            print(result)
            print(f"\n--- End of {arg} ---\n")
        else:
            print(f"Error: {result}")
    
    def do_write(self, arg):
        """Write to a file: write <filename>"""
        if not arg:
            print("Usage: write <filename>")
            return
        
        print(f"Enter content for {arg} (type '###' on a line by itself to finish):")
        content_lines = []
        while True:
            line = input()
            if line.strip() == "###":
                break
            content_lines.append(line)
        
        content = "\n".join(content_lines)
        success, result = self.sandbox.write_file(arg, content)
        print(result)
    
    def do_append(self, arg):
        """Append to a file: append <filename>"""
        if not arg:
            print("Usage: append <filename>")
            return
        
        print(f"Enter content to append to {arg} (type '###' on a line by itself to finish):")
        content_lines = []
        while True:
            line = input()
            if line.strip() == "###":
                break
            content_lines.append(line)
        
        content = "\n".join(content_lines)
        success, result = self.sandbox.append_file(arg, content)
        print(result)
    
    def do_delete(self, arg):
        """Delete a file: delete <filename>"""
        if not arg:
            print("Usage: delete <filename>")
            return
        
        confirm = input(f"Are you sure you want to delete {arg}? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            return
        
        success, result = self.sandbox.delete_file(arg)
        print(result)
    
    def do_rename(self, arg):
        """Rename a file: rename <old_name> <new_name>"""
        parts = arg.split()
        if len(parts) != 2:
            print("Usage: rename <old_name> <new_name>")
            return
        
        old_name, new_name = parts
        success, result = self.sandbox.rename_file(old_name, new_name)
        print(result)
    
    def do_ask_ai(self, arg):
        """Ask AI a question about a file: ask_ai <filename> <question>"""
        parts = arg.split(maxsplit=1)
        if len(parts) != 2:
            print("Usage: ask_ai <filename> <question>")
            return
        
        filename, question = parts
        success, content = self.sandbox.read_file(filename)
        if not success:
            print(f"Error: {content}")
            return
        
        print("Asking AI, please wait...")
        success, answer = self.genai.ask_question(question, content)
        if success:
            print("\n--- AI Response ---\n")
            print(answer)
            print("\n--- End of Response ---\n")
        else:
            print(f"Error: {answer}")
    
    def do_explain(self, arg):
        """Have AI explain code in a file: explain <filename>"""
        if not arg:
            print("Usage: explain <filename>")
            return
        
        success, content = self.sandbox.read_file(arg)
        if not success:
            print(f"Error: {content}")
            return
        
        print("Asking AI to explain code, please wait...")
        success, explanation = self.genai.explain_code(content)
        if success:
            print("\n--- AI Explanation ---\n")
            print(explanation)
            print("\n--- End of Explanation ---\n")
        else:
            print(f"Error: {explanation}")
    
    def do_refactor(self, arg):
        """Have AI refactor code: refactor <filename> <instruction>"""
        parts = arg.split(maxsplit=1)
        if len(parts) != 2:
            print("Usage: refactor <filename> <instruction>")
            return
        
        filename, instruction = parts
        success, content = self.sandbox.read_file(filename)
        if not success:
            print(f"Error: {content}")
            return
        
        print("Asking AI to refactor code, please wait...")
        success, refactored = self.genai.refactor_code(content, instruction)
        if success:
            print("\n--- Refactored Code ---\n")
            print(refactored)
            print("\n--- End of Refactored Code ---\n")
            
            save = input("Do you want to save the refactored code? (y/n): ")
            if save.lower() == 'y':
                success, result = self.sandbox.write_file(filename, refactored)
                print(result)
        else:
            print(f"Error: {refactored}")
    
    def do_improve(self, arg):
        """Have AI suggest improvements: improve <filename>"""
        if not arg:
            print("Usage: improve <filename>")
            return
        
        success, content = self.sandbox.read_file(arg)
        if not success:
            print(f"Error: {content}")
            return
        
        print("Asking AI for improvement suggestions, please wait...")
        success, suggestions = self.genai.suggest_improvements(content)
        if success:
            print("\n--- Improvement Suggestions ---\n")
            print(suggestions)
            print("\n--- End of Suggestions ---\n")
        else:
            print(f"Error: {suggestions}")
    
    def do_docs(self, arg):
        """Have AI generate documentation: docs <filename>"""
        if not arg:
            print("Usage: docs <filename>")
            return
        
        success, content = self.sandbox.read_file(arg)
        if not success:
            print(f"Error: {content}")
            return
        
        print("Asking AI to generate documentation, please wait...")
        success, docs = self.genai.generate_documentation(content)
        if success:
            print("\n--- Generated Documentation ---\n")
            print(docs)
            print("\n--- End of Documentation ---\n")
        else:
            print(f"Error: {docs}")
    
    def do_modify(self, arg):
        """Have AI modify code: modify <filename> <instruction>"""
        parts = arg.split(maxsplit=1)
        if len(parts) != 2:
            print("Usage: modify <filename> <instruction>")
            return
        
        filename, instruction = parts
        success, content = self.sandbox.read_file(filename)
        if not success:
            print(f"Error: {content}")
            return
        
        print("Asking AI to modify code, please wait...")
        success, modified = self.genai.modify_with_instruction(content, instruction)
        if success:
            print("\n--- Modified Code ---\n")
            print(modified)
            print("\n--- End of Modified Code ---\n")
            
            save = input("Do you want to save the modified code? (y/n): ")
            if save.lower() == 'y':
                success, result = self.sandbox.write_file(filename, modified)
                print(result)
        else:
            print(f"Error: {modified}")
    
    def do_exit(self, arg):
        """Exit the program."""
        print("Goodbye!")
        return True
    
    def do_quit(self, arg):
        """Exit the program."""
        return self.do_exit(arg)
