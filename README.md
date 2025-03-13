# Kimono Textile Analyzer

A GTK-based application for analyzing kimono textiles using Google's Gemini AI API. The tool finds the most interesting textile parts in kimono images and creates a zoomed-in circular highlight.

## Features

- Drag and drop interface for images or folders
- AI-powered detection of interesting textile patterns
- Creates a circular highlight overlay on the original image
- Shows a zoomed-in view of the detected interesting part

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

## Usage

Run the application:
```
python kimono_analyzer.py
```

Then drag and drop kimono images or folders containing images into the application window.