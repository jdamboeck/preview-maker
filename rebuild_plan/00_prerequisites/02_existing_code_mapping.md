# Existing Code to New Architecture Mapping

## Overview
This document maps functionality from the current monolithic codebase to the planned component-based architecture. This mapping helps both human developers and AI assistants understand how existing code will be refactored and distributed among the new components.

## Current Codebase Structure

```
preview-maker/
├── preview_maker.py       # Main application file (2179 lines)
├── src/                   # Source directory
│   ├── preview_maker.py   # Second copy of application logic (141 lines)
│   ├── config.py          # Configuration management (351 lines)
│   ├── gemini_analyzer.py # AI analysis functionality (331 lines)
│   ├── image_processor.py # Image processing functionality (490 lines)
│   └── __init__.py        # Package initialization
├── prompts/               # AI prompt templates
│   ├── user_prompt.md     # User-editable part of prompt
│   └── technical_prompt.md # Technical part of the prompt
├── config.toml            # Configuration file
├── requirements.txt       # Dependencies
└── README.md              # Documentation
```

## New Architecture Structure

```
preview-maker/
├── app/                   # Application package
│   ├── config/            # Configuration module
│   ├── core/              # Core functionality
│   ├── ui/                # User interface components
│   └── utils/             # Utility functions
├── prompts/               # AI prompt templates
├── resources/             # Application resources
├── tests/                 # Testing infrastructure
├── docs/                  # Documentation
├── config.toml            # Configuration file
├── requirements.txt       # Dependencies
└── README.md              # Documentation
```

## Functionality Mapping

### Configuration System
| Current Location | New Location | Functionality |
|------------------|--------------|--------------|
| `src/config.py:1-100` | `app/config/settings.py` | Settings class and config loading |
| `src/config.py:101-200` | `app/config/defaults.py` | Default configuration values |
| `src/config.py:201-351` | `app/config/migration.py` | Configuration upgrade handling |
| `config.toml` | `config.toml` | Configuration file (preserved) |

### Core Analysis
| Current Location | New Location | Functionality |
|------------------|--------------|--------------|
| `src/gemini_analyzer.py:1-50` | `app/core/ai_service.py` | AI service initialization |
| `src/gemini_analyzer.py:51-150` | `app/core/analyzer.py` | Image analysis functionality |
| `src/gemini_analyzer.py:151-250` | `app/core/analyzer.py` | Detection logic |
| `src/gemini_analyzer.py:251-331` | `app/core/analyzer.py` | Response parsing |
| `preview_maker.py:500-600` | `app/core/analyzer.py` | Additional analysis logic |

### Image Processing
| Current Location | New Location | Functionality |
|------------------|--------------|--------------|
| `src/image_processor.py:1-100` | `app/core/processor.py` | Image loading and validation |
| `src/image_processor.py:101-250` | `app/core/processor.py` | Highlight generation |
| `src/image_processor.py:251-400` | `app/core/processor.py` | Zoom and overlay logic |
| `src/image_processor.py:401-490` | `app/core/processor.py` | Image saving |
| `preview_maker.py:700-800` | `app/core/processor.py` | Additional processing logic |

### User Interface
| Current Location | New Location | Functionality |
|------------------|--------------|--------------|
| `preview_maker.py:1-100` | `app/ui/app_window.py` | Main window setup |
| `preview_maker.py:101-200` | `app/ui/components/drop_zone.py` | Drag and drop handling |
| `preview_maker.py:201-300` | `app/ui/components/preview_panel.py` | Preview display logic |
| `preview_maker.py:301-400` | `app/ui/dialogs/settings_dialog.py` | Settings dialog |
| `preview_maker.py:401-500` | `app/ui/dialogs/manual_mode_dialog.py` | Manual selection mode |
| `preview_maker.py:1000-1100` | `app/ui/components/notification.py` | Notification system |
| `preview_maker.py:1500-1600` | `app/ui/handlers/drop_handler.py` | Drop event handling |
| `preview_maker.py:1600-1700` | `app/ui/handlers/click_handler.py` | Click event handling |

### Utilities
| Current Location | New Location | Functionality |
|------------------|--------------|--------------|
| `preview_maker.py:2000-2100` | `app/utils/file_utils.py` | File handling utilities |
| `preview_maker.py:1800-1900` | `app/utils/image_utils.py` | Image utility functions |
| `preview_maker.py:1200-1300` | `app/utils/threading.py` | Threading and async handling |
| `preview_maker.py:1400-1450` | `app/utils/logging.py` | Logging functionality |

### AI Prompts
| Current Location | New Location | Functionality |
|------------------|--------------|--------------|
| `prompts/user_prompt.md` | `prompts/default_user.md` | User prompt template |
| `prompts/technical_prompt.md` | `prompts/technical.md` | Technical prompt template |

## Key Functions Mapping

### Main Application Functions
| Current Function | New Location | Purpose |
|------------------|--------------|---------|
| `PreviewMaker.__init__` | `app/ui/app_window.py:AppWindow.__init__` | Application initialization |
| `PreviewMaker.on_activate` | `app/ui/app_window.py:AppWindow.on_activate` | Window activation |
| `PreviewMaker.process_image` | `app/core/analyzer.py:analyze_image` | Process image with AI |
| `PreviewMaker.show_notification` | `app/ui/components/notification.py:show_notification` | Display notification |
| `PreviewMaker.on_image_click` | `app/ui/handlers/click_handler.py:handle_click` | Handle image click |
| `PreviewMaker.open_manual_mode_window` | `app/ui/dialogs/manual_mode_dialog.py:show_dialog` | Open manual mode |
| `PreviewMaker._run_detection_thread` | `app/utils/threading.py:run_task` | Run task in thread |

### Configuration Functions
| Current Function | New Location | Purpose |
|------------------|--------------|---------|
| `config.load_config` | `app/config/settings.py:load_config` | Load configuration |
| `config.get_path` | `app/config/settings.py:Settings.get_path` | Get path setting |
| `config.get_image_processing` | `app/config/settings.py:Settings.get_image_processing` | Get processing setting |
| `config.get_gemini_api` | `app/config/settings.py:Settings.get_ai_setting` | Get AI API setting |

### Analyzer Functions
| Current Function | New Location | Purpose |
|------------------|--------------|---------|
| `gemini_analyzer.identify_interesting_area` | `app/core/analyzer.py:Analyzer.analyze_image` | Detect interesting area |
| `gemini_analyzer.fallback_detection` | `app/core/analyzer.py:Analyzer._fallback_detection` | Fallback when AI unavailable |
| `gemini_analyzer._parse_response` | `app/core/analyzer.py:Analyzer._parse_response` | Parse AI response |

### Image Processor Functions
| Current Function | New Location | Purpose |
|------------------|--------------|---------|
| `image_processor.create_highlighted_image` | `app/core/processor.py:Processor.create_highlight` | Create highlight overlay |
| `image_processor.save_debug_image` | `app/core/processor.py:Processor.save_debug_image` | Save debug image |
| `image_processor.save_processed_image` | `app/core/processor.py:Processor.save_image` | Save processed image |

## Special Considerations

### Circular Dependencies
- The current implementation has circular dependencies between UI event handling and image processing
- In the new architecture, these will be resolved through dependency injection and event-based communication

### State Management
- The current app uses global state in various places
- The new architecture will use explicit state management through the Settings class and UI state objects

### Threading Model
- The current implementation uses manual threading
- The new architecture will use a more robust async/threading system with proper error handling

## Conclusion
This mapping provides a guide for how existing functionality will be distributed in the new architecture. During implementation, developers and AI assistants should refer to this document to ensure all existing functionality is properly preserved while following the new component-based design.