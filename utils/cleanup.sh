#!/bin/bash
# Cleanup script to remove original files once the new structure is working

echo "This script will remove the original files that have been migrated to the new structure."
echo "Make sure you've tested the new structure first by running: python preview_maker.py"
echo ""
echo "Press Ctrl+C to cancel or Enter to continue..."
read

# Remove original files
echo "Removing original files..."
rm -f kimono_analyzer.py
rm -f image_processor.py
rm -f gemini_analyzer.py
rm -f sample_kimono.jpg
rm -f prompts/*.txt
rm -f test_with_preview.png
rm -f test_without_preview.png

# Remove additional leftover files
echo "Removing additional leftover files..."
rm -f config.py
rm -f generate_test_image.py
rm -f sample_image.py
rm -f test_image_processor.py

# Remove redundant directories
echo "Removing redundant directories..."
rm -rf debug_output
rm -rf test_images

echo "Cleanup complete!"
echo "You can now use the new structure with 'python preview_maker.py'"