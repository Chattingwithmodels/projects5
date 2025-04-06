import os
import sys
import argparse

from sandbox_manager import SandboxManager
from genai_wrapper import GenAIWrapper
from sandbox_cli import SandboxCLI

def main():
    parser = argparse.ArgumentParser(description="Sandbox IDE Assistant")
    parser.add_argument("--sandbox-path", default="~/.my_sandbox", 
                        help="Path to sandbox directory")
    parser.add_argument("--api-key", default=None,
                        help="Google GenAI API key (defaults to GOOGLE_API_KEY env var)")
    
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
