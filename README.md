# Sandbox IDE with GenAI Integration

A secure, AI-powered integrated development environment that uses Google's Generative AI SDK to help you code, document, and create within a sandboxed file system.

## Features

- **Secure Sandboxed Environment**: All file operations are constrained to a single secure directory
- **Intelligent Code Assistance**: Powered by Google's Generative AI models
- **Multiple AI Tools**:
  - Code explanation
  - Code refactoring
  - Documentation generation
  - Improvement suggestions
  - Multi-file project generation
  - AI image generation
- **Customizable**: Select different AI models and adjust generation parameters
- **Modern GUI**: Tkinter-based interface with syntax highlighting and file management

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/sandbox-ide.git
cd sandbox-ide
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Set up your Google GenAI API key:
```
export GOOGLE_API_KEY="your_api_key_here"
```

## Usage

### Starting the IDE

Run the application with either CLI or GUI mode:

```
# CLI mode (for terminal-based operations)
python main.py

# GUI mode (for graphical interface)
python main.py --gui
```

You can specify a custom sandbox directory:

```
python main.py --gui --sandbox-path "~/my_sandbox_folder"
```

### GUI Interface

The GUI interface is divided into several key areas:

1. **File Explorer** (left side): Browse, create, open, rename, and delete files
   - Can be collapsed to maximize workspace

2. **Editor** (top-right): Edit files with syntax highlighting

3. **AI Tools** (bottom-right): Interact with AI features
   - Ask questions about code
   - Get code explanations
   - Refactor code
   - Generate documentation
   - Suggest improvements

4. **Multi-File Generator**: Create entire projects with a single prompt

5. **Image Generator**: Create images using AI and save them to your sandbox

6. **Settings**: Configure AI models and parameters

### Keyboard Shortcuts

- **Ctrl+S**: Save current file
- **Ctrl+Z**: Undo
- **Ctrl+Y**: Redo
- **Ctrl+X**: Cut
- **Ctrl+C**: Copy
- **Ctrl+V**: Paste

## Security

This IDE maintains security by:

- Restricting all file operations to a designated sandbox directory
- Validating filenames and paths to prevent sandbox escape
- Limiting file types to text-based files
- Preventing execution of any files in the sandbox

## Customizing AI Models

The Settings panel allows you to:

1. Change the text generation model
2. Set custom system prompts
3. Adjust temperature and other generation parameters
4. Select image generation models

## Building Your Own Projects

The Multi-File Generator lets you:

1. Describe a complete project or component
2. Generate all required files in one operation
3. Preview and save files to your sandbox

## Creating Images

The Image Generator enables you to:

1. Enter detailed text prompts
2. Generate high-quality images
3. Save images directly to your sandbox

## License

[MIT License](LICENSE) 