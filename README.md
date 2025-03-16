# Preview Maker

A GTK-based application for creating image previews with AI-powered highlight overlays.

## Overview

Preview Maker is a desktop application that helps users create engaging image previews by automatically identifying and highlighting interesting regions in images. It uses Google's Gemini AI to analyze images and identify areas of interest, then creates circular overlays to draw attention to these areas.

## Features

- Load and display images in various formats (JPEG, PNG, BMP, TIFF)
- Analyze images using Google Gemini AI to identify interesting regions
- Create circular highlight overlays on images
- Save processed images with overlays
- Modern GTK 4.0 user interface with drag-and-drop support
- Headless mode for batch processing

## Installation

### Prerequisites

- Python 3.8 or higher
- GTK 4.0
- PyGObject
- Pillow (PIL)
- Google Gemini API key

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/jdamboeck/preview-maker.git
   cd preview-maker
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python -m preview_maker.app
   ```

### Docker

For development and testing, you can use the provided Docker environment:

```bash
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm app
```

## Usage

### GUI Mode

1. Launch the application
2. Click "Open" to select an image
3. Enter your Google Gemini API key when prompted
4. Click "Analyze" to process the image
5. Save the result using the "Save" button

### Headless Mode

For batch processing or integration with other tools, use headless mode:

```bash
python -m preview_maker.app --headless --image input.jpg --output output.jpg --api-key YOUR_API_KEY
```

## Development

### Project Structure

- `preview_maker/` - Main package
  - `app.py` - Application entry point
  - `core/` - Core functionality
  - `image/` - Image processing components
  - `ai/` - AI integration components
  - `ui/` - User interface components
- `tests/` - Test suite
- `rebuild_plan/` - Project documentation and planning

### Running Tests

```bash
# Run all tests
pytest

# Run tests in headless mode (for CI/CD)
HEADLESS=1 pytest

# Run specific test modules
pytest tests/ui/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gemini API for image analysis
- GTK team for the UI toolkit
- PyGObject team for Python bindings

## Contributing

We welcome contributions to Preview Maker! Please follow our Git workflow and contribution guidelines:

- **Git Workflow**: See [git_workflow.md](rebuild_plan/git_workflow.md) for detailed information on our branching strategy, commit message standards, and merge process.
- **GitHub CLI**: For an enhanced workflow using GitHub CLI, see [github_cli_guide.md](docs/github_cli_guide.md).
- **Templates**: We use standardized templates for issues and pull requests to ensure consistent information.
- **Code Quality**: We use pre-commit hooks to maintain code quality standards.
- **CI/CD**: Automated workflows check code quality, run tests, and scan for security issues on every PR. See [ci_cd_guide.md](docs/ci_cd_guide.md).

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/jdamboeck/preview-maker.git
cd preview-maker

# Set up your environment
docker-compose -f rebuild_plan/docker/docker-compose.yml build
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm verify

# Set up pre-commit hooks
pip install pre-commit
pre-commit install
```