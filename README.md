# Sandbox IDE with GenAI Integration

A secure, AI-powered integrated development environment that uses Google's Generative AI SDK to help you code, document, and create within a sandboxed file system.

## Features

- **Secure Sandboxed Environment**: All file operations are constrained to a single secure directory
- **State-of-the-Art Language Models**: Supports latest Gemini 2.5, Gemini 2.0, and Gemini 1.5 models
- **Intelligent Code Assistance**: Powered by Google's Generative AI models
- **Multiple AI Tools**:
  - Code explanation
  - Code refactoring
  - Documentation generation
  - Improvement suggestions
  - Multi-file project generation
  - AI image generation
- **Advanced Model Settings**:
  - Choose from the latest models including Gemini 2.5 Pro (Experimental and Preview)
  - Gemma 3 27B model support
  - Fine-tune temperature, tokens, and sampling parameters
  - Customize system prompts
- **Modern GUI**: Tkinter-based interface with syntax highlighting and file management

## Recent Updates

- **New Models Support**: Added Gemini 2.5 Pro models, Gemma 3 27B, and Gemini 2.0 Flash-Lite
- **Image Generation Improvements**: Using Imagen 3.0 for reliable image generation
- **Enhanced Model Selection**: Better model prioritization and availability testing
- **Model Documentation**: Added detailed model descriptions with token limits
- **Updated SDK**: Using Google GenAI SDK v0.4.0+ with improved reliability and features

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
   - File sorting by name, size, or modification date
   - Can be collapsed to maximize workspace

2. **Editor** (top-right): Edit files with syntax highlighting

3. **AI Tools** (bottom-right): Interact with AI features
   - Ask questions about code
   - Get code explanations
   - Refactor code
   - Generate documentation
   - Suggest improvements
   - Save outputs to markdown files

4. **Multi-File Generator**: Create entire projects with a single prompt

5. **Image Generator**: Create images using AI and save them to your sandbox
   - Uses Google's Imagen 3.0 model for high-quality generation
   - Simple text-to-image interface

6. **Settings**: Configure AI models and parameters
   - Select from latest Gemini models 
   - Adjust generation parameters with detailed descriptions
   - Dark/Light mode options

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
- Limiting file types to text-based files and safe image formats
- Preventing execution of any files in the sandbox

## Customizing AI Models

The Settings panel allows you to:

1. Choose from the latest models:
   - Gemini 2.5 Pro models (Preview and Experimental)
   - Gemini 2.0 Flash and Pro models
   - Gemini 1.5 models
   - Gemma 3 27B model
2. Test model availability in your region/account
3. Set custom system prompts to guide model behavior
4. Adjust temperature and other generation parameters with detailed descriptions

## Building Your Own Projects

The Multi-File Generator lets you:

1. Describe a complete project or component
2. Generate all required files in one operation
3. Preview and save files to your sandbox

## Creating Images

The Image Generator enables you to:

1. Enter detailed text prompts
2. Generate high-quality images using Google's Imagen 3.0 model
3. Save images directly to your sandbox

## License

[MIT License](LICENSE) 