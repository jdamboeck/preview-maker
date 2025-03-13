#!/bin/bash
# Setup script for Kimono Textile Analyzer

echo "Setting up Kimono Textile Analyzer..."

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Python 3 is required but not installed. Please install Python 3 first."
    exit 1
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check if PyGObject dependencies are installed (this varies by OS)
if ! python3 -c "import gi" &> /dev/null; then
    echo "GTK dependencies are required. Here's how to install them on various systems:"
    echo "  - Ubuntu/Debian: sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-4.0"
    echo "  - Fedora: sudo dnf install python3-gobject gtk4-devel"
    echo "  - Arch Linux: sudo pacman -S python-gobject gtk4"
    echo "  - macOS: brew install pygobject3 gtk4"
    echo ""
    echo "Please install the appropriate packages for your system and try again."
fi

# Generate sample image
echo "Generating sample test image..."
python3 generate_test_image.py

# Remind user about API key
echo ""
echo "IMPORTANT: Before running the application, you need to set up your Google Gemini API key."
echo "You can either:"
echo "1. Edit the .env file to add your API key"
echo "2. Set the GEMINI_API_KEY environment variable"
echo ""
echo "To run the application, use:"
echo "source venv/bin/activate"  # Already active at this point
echo "python3 kimono_analyzer.py"
echo ""

# Make the script files executable
chmod +x kimono_analyzer.py
chmod +x generate_test_image.py

# Show .env file contents to remind about API key
if [ -f ".env" ]; then
    echo "Current .env file content:"
    cat .env
fi