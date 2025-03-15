# Preview Maker

A GTK-based application for analyzing images using Google's Gemini AI API. The tool finds the most interesting details in images and creates a zoomed-in circular highlight.

## Features

- Drag and drop interface for images or folders
- AI-powered detection of interesting details and patterns
- Creates a circular highlight overlay on the original image
- Shows a zoomed-in view of the detected interesting part
- Configurable parameters via TOML configuration file

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/jdamboeck/preview-maker.git
   cd preview-maker
   ```
2. Ensure you have Python 3.8+ installed
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up your Google Gemini API key as described in the Setup section

## Setup

1. Get a Google Gemini API key from https://aistudio.google.com/
2. Set your API key as an environment variable:
   ```
   export GEMINI_API_KEY=your_api_key_here
   ```
   Or save it in a `.env` file in the project root directory (this file is gitignored)

### API Key Security

To ensure your API keys remain secure:

1. **Never commit API keys to the repository**
   - The `.env` file is included in `.gitignore` to prevent accidental commits
   - Use the provided `.env.example` as a template

2. **Rotate API keys regularly**
   - Periodically generate new API keys from the Google AI Studio
   - Update your local `.env` file with the new key

3. **Restrict API key usage**
   - Set appropriate usage limits in the Google Cloud Console
   - Consider adding API key restrictions based on IP or referrer

4. **For production deployments**
   - Use environment variables or a secrets management service
   - Never hardcode API keys in application code

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

## Rebuild Project

The project is currently undergoing a rebuild to improve its architecture and migrate to GTK 4.0:

- **Rebuild Planning**: See the `rebuild_plan/` directory for the rebuild strategy
- **Docker Environment**: Use our Docker environment for consistent development
- **Component Architecture**: Moving from monolithic to component-based architecture

For detailed information on the rebuild, see `rebuild_plan/README.md`.

## Development with Cursor IDE

This project is optimized for development with Cursor IDE:

1. **`.cursorrules` File Location**:
   - Ensure the `.cursorrules` file is in the project root directory
   - This provides AI-assisted development guidance throughout the project
   - If it's missing, copy it from a backup or checkout:
     ```bash
     cp /path/to/backup/.cursorrules /home/jd/dev/projects/preview-maker/
     ```

2. **Working with Dual Structure**:
   - During the rebuild period, both old and new code structures exist
   - See guidance in `rebuild_plan/README.md` for working with both structures
   - The `.cursorrules` file contains detailed guidelines for this situation

3. **Docker Development**:
   - Prefer using the Docker environment for consistent development
   - See Docker commands in `.cursorrules` and `rebuild_plan/docker/README.md`

## Documentation Guidelines

When making changes to the codebase, always update the relevant documentation:

1. **Code Documentation**:
   - Add docstrings to all new functions and classes
   - Update existing docstrings when modifying function behavior
   - Include type annotations for parameters and return values

2. **README Files**:
   - Keep installation and setup instructions current
   - Update directory structure descriptions when files are added/moved
   - Add new features to feature lists when implemented

3. **Technical Documentation**:
   - Update component diagrams when changing dependencies
   - Revise architecture documents when modifying component interfaces
   - Document design decisions for significant changes

4. **Docker Documentation**:
   - Update Docker-related instructions when changing environment requirements
   - Document new or modified Docker commands
   - Update environment variable documentation

See the "Documentation Update Guidelines" section in the `.cursorrules` file for more detailed requirements.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure they pass
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

For detailed information on our Git workflow, branching strategy, and contribution guidelines, see [rebuild_plan/git_workflow.md](rebuild_plan/git_workflow.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Repository

- **GitHub**: [https://github.com/jdamboeck/preview-maker](https://github.com/jdamboeck/preview-maker)
- **Main Branch**: Contains stable, production-ready code
- **Develop Branch**: Integration branch for feature development