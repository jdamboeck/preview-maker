# Application Analysis: Preview Maker

## Overview
This document provides a comprehensive analysis of the current Preview Maker application, capturing its purpose, features, architecture, and known issues. This serves as a baseline for the rebuild process.

## Application Purpose
Preview Maker is a GTK-based application that analyzes images using Google's Gemini AI to find and highlight interesting details. It creates zoomed-in circular overlays of detected areas of interest, producing visually appealing product highlights or informative focus points.

## Core Features

### 1. AI-Powered Image Analysis
- Uses Google Gemini Vision API to analyze images
- Identifies areas of interest in product or other images
- Detects visually interesting details based on context
- Falls back to deterministic detection when AI unavailable
- Uses custom prompts to guide the AI analysis

### 2. Image Processing
- Creates circular highlight overlays of interesting details
- Produces zoomed-in views of detected areas
- Supports various image formats (JPEG, PNG, BMP, GIF)
- Maintains image quality through configurable processing parameters
- Saves resulting images with appropriate quality settings

### 3. User Interface
- GTK 4.0 based interface with modern design
- Drag and drop interface for images and folders
- Preview panel for viewing results
- Manual selection mode for user-directed highlights
- Notification system for operation feedback
- Configuration options accessible through UI

### 4. Configuration System
- Uses TOML-based configuration file
- Supports customizable paths, AI settings, and processing parameters
- Retains user preferences between sessions
- Includes default configuration for first-time use

## Current Architecture

### Main Components
1. **Main Application Class** (`preview_maker.py`): Monolithic application class handling UI, image processing, and AI integration
2. **Configuration Module** (`src/config.py`): Manages application settings and configuration
3. **Gemini Analyzer** (`src/gemini_analyzer.py`): Handles AI analysis of images
4. **Image Processor** (`src/image_processor.py`): Processes images and creates highlights

### Current Limitations
1. **Monolithic Structure**: Core functionality is not properly modularized
2. **Limited Testing**: No comprehensive test infrastructure
3. **Tight Coupling**: UI and core functionality are tightly coupled
4. **Limited Error Handling**: Some edge cases not properly handled
5. **Documentation Gaps**: Incomplete or missing documentation in some areas

## Known Issues and Challenges

### Technical Issues
1. **AI Dependency**: Heavy reliance on external AI service
2. **Performance with Large Images**: Processing large images can be slow
3. **GTK-Specific Challenges**: Some UI components have platform-specific issues
4. **Error Handling**: Incomplete error handling in some edge cases

### Feature Gaps
1. **Batch Processing**: Limited handling of multiple images
2. **Export Options**: Limited output format options
3. **AI Customization**: Limited ability to customize AI prompts through UI
4. **History Management**: No session history for processed images

## User Workflows

### Primary Workflow
1. User launches the application
2. User drops an image or folder onto the application window
3. Application processes image(s) using AI to detect interesting areas
4. Application creates highlight overlay and zoomed view
5. User views the result and can save or share it
6. User can process additional images

### Alternative Workflows
1. **Manual Selection Mode**: User selects area of interest manually
2. **AI Unavailable Mode**: Application uses fallback detection
3. **Configuration Workflow**: User adjusts settings via dialog

## Technical Details

### Dependencies
- PyGObject (GTK 4.0) for UI
- Pillow for image processing
- Google Generative AI for AI services
- TOML for configuration
- Other standard Python libraries

### Environment Requirements
- Python 3.8+
- GTK 4.0 libraries
- Internet connection for AI services
- Gemini API key

## Conclusion
Preview Maker is a specialized image enhancement tool that combines AI analysis with custom image processing to create focused highlights of interesting details. The application provides an intuitive interface but suffers from architectural limitations that the rebuild aims to address while preserving and enhancing existing functionality.