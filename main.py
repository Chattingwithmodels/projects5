import os
import sys
import argparse

from sandbox_manager import SandboxManager
from genai_wrapper import GenAIWrapper
from sandbox_cli import SandboxCLI

# Import GUI app if available
try:
    from gui.ide_app import IDEApp
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

def main():
    parser = argparse.ArgumentParser(description="Sandbox IDE Assistant")
    parser.add_argument("--sandbox-path", default="~/.my_sandbox", 
                        help="Path to sandbox directory")
    parser.add_argument("--api-key", default=None,
                        help="Google GenAI API key (defaults to GOOGLE_API_KEY env var)")
    parser.add_argument("--gui", action="store_true", 
                        help="Launch graphical interface instead of CLI")
    
    args = parser.parse_args()
    
    # Setup sandbox manager
    try:
        sandbox = SandboxManager(args.sandbox_path)
    except Exception as e:
        print(f"Error setting up sandbox: {e}")
        return 1
    
    # Setup GenAI wrapper
    try:
        api_key = args.api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("API key is required. Set GOOGLE_API_KEY environment variable or use --api-key.")
            return 1
        
        genai_wrapper = GenAIWrapper(api_key)
    except Exception as e:
        print(f"Error setting up GenAI: {e}")
        return 1
    
    # Launch GUI or CLI based on arguments
    if args.gui:
        if not GUI_AVAILABLE:
            print("GUI dependencies not available. Install tkinter.")
            return 1
        
        try:
            app = IDEApp(sandbox, genai_wrapper)
            app.run()
            return 0
        except Exception as e:
            print(f"Error in GUI: {e}")
            return 1
    else:
        # Start CLI
        cli = SandboxCLI(sandbox, genai_wrapper)
        try:
            cli.cmdloop()
        except KeyboardInterrupt:
            print("\nGoodbye!")
        except Exception as e:
            print(f"Error in CLI: {e}")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
