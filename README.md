# Preview Maker

A GTK-based application for analyzing images using Google's Gemini AI API. The tool finds the most interesting details in images and creates a zoomed-in circular highlight.

## Features

- Drag and drop interface for images or folders
- AI-powered detection of interesting details and patterns
- Creates a circular highlight overlay on the original image
- Shows a zoomed-in view of the detected interesting part
- Configurable parameters via TOML configuration file

## Installation

1. Ensure you have Python 3.8+ installed
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your Google Gemini API key as described in the Setup section

## Setup

1. Get a Google Gemini API key from https://aistudio.google.com/
2. Set your API key as an environment variable:
   ```
   export GEMINI_API_KEY=your_api_key_here
   ```
   Or save it in a `.env` file in the project root directory

## Configuration

The application uses a TOML configuration file (`config.toml`) for customizable settings. On first run, a default configuration file will be created if it doesn't exist.

You can customize the following:

- **File and Directory Paths**: Set custom locations for previews, debug images, and prompts
- **Image Processing Parameters**: Adjust selection ratio, zoom factor, and quality settings
- **Gemini API Settings**: Configure model name, temperature, and token limits
- **Detection Settings**: Set default target types and supported file formats

Example configuration:

```toml
[paths]
previews_dir = "custom_previews"
debug_dir = "custom_previews/debug"

[image_processing]
selection_ratio = 0.15  # 15% of shortest dimension
zoom_factor = 4.0       # 4x zoom

[gemini_api]
model_name = "gemini-1.5-pro-vision"
temperature = 0.2
```

## Usage

Run the application:
```
python preview_maker.py
```

Then drag and drop images or folders containing images into the application window.

## Project Structure

The project is organized as follows:

- `preview_maker.py`: Main application entry point
- `src/`: Core application modules
  - `gemini_analyzer.py`: Handles AI detection with Google Gemini
  - `image_processor.py`: Image processing and highlight creation
  - `config.py`: Configuration management
- `prompts/`: AI prompt files
  - `user_prompt.md`: User-editable part of the prompt
  - `technical_prompt.md`: Technical part of the prompt that controls response format
- `utils/`: Utility scripts
- `tests/`: Test modules
- `data/`: Sample images
- `docs/`: Documentation and example images