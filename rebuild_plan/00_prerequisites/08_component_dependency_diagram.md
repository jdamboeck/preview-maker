# Component Dependency Diagram

This document provides a textual representation of the component dependencies in the rebuilt Preview Maker application. The purpose is to visualize the relationships between various components and identify potential coupling issues or circular dependencies.

## Core Component Relationships

```
+-----------------+       +-------------------+       +-------------------+
| ApplicationCore |------>| ConfigurationMgr  |------>| FileSystemManager |
+-----------------+       +-------------------+       +-------------------+
        |                          |                          |
        |                          |                          |
        v                          v                          v
+-------------------+       +-------------------+      +-------------------+
| WindowManager     |------>| UIComponentFactory|----->| ImageLoader       |
+-------------------+       +-------------------+      +-------------------+
        |                          |                          |
        |                          |                          |
        v                          v                          v
+-------------------+       +-------------------+      +-------------------+
| ControlPanel      |------>| PreviewPanel      |----->| ImageProcessor    |
+-------------------+       +-------------------+      +-------------------+
        |                          |                          |
        |                          |                          |
        v                          v                          v
+-------------------+       +-------------------+      +-------------------+
| SettingsManager   |------>| ThemeManager      |----->| AIServiceInterface|
+-------------------+       +-------------------+      +-------------------+
                                                                |
                                                                |
                                                                v
                                                      +-------------------+
                                                      | GeminiAIProvider  |
                                                      +-------------------+
                                                                |
                                                                |
                                                                v
                                                      +-------------------+
                                                      | PromptManager     |
                                                      +-------------------+
                                                                |
                                                                |
                                                                v
                                                      +-------------------+
                                                      | ResponseParser    |
                                                      +-------------------+
```

## Component Dependency Description

### Core Layer

1. **ApplicationCore**
   - **Depends on**: ConfigurationMgr
   - **Depended on by**: WindowManager
   - **Responsibility**: Bootstraps the application, manages lifecycle, coordinates major components

2. **ConfigurationMgr**
   - **Depends on**: FileSystemManager
   - **Depended on by**: ApplicationCore, UIComponentFactory, SettingsManager
   - **Responsibility**: Loads, validates, and persists application configuration

3. **FileSystemManager**
   - **Depends on**: None
   - **Depended on by**: ConfigurationMgr, ImageLoader
   - **Responsibility**: Handles file operations, monitors file system changes

### UI Layer

4. **WindowManager**
   - **Depends on**: ApplicationCore, UIComponentFactory
   - **Depended on by**: ControlPanel, PreviewPanel
   - **Responsibility**: Manages application windows, dialogs, and layout

5. **UIComponentFactory**
   - **Depends on**: ConfigurationMgr
   - **Depended on by**: WindowManager, ThemeManager
   - **Responsibility**: Creates and configures UI components with consistent styling

6. **ControlPanel**
   - **Depends on**: WindowManager, SettingsManager
   - **Depended on by**: None
   - **Responsibility**: Provides UI controls for image operations and settings

7. **PreviewPanel**
   - **Depends on**: WindowManager, ImageProcessor
   - **Depended on by**: None
   - **Responsibility**: Displays image previews and visualizes AI processing results

8. **SettingsManager**
   - **Depends on**: ConfigurationMgr
   - **Depended on by**: ControlPanel, ThemeManager
   - **Responsibility**: Exposes settings to UI and enforces validation rules

9. **ThemeManager**
   - **Depends on**: UIComponentFactory, SettingsManager
   - **Depended on by**: None
   - **Responsibility**: Manages application theming and styling

### Image Processing Layer

10. **ImageLoader**
    - **Depends on**: FileSystemManager
    - **Depended on by**: ImageProcessor
    - **Responsibility**: Loads and validates image files

11. **ImageProcessor**
    - **Depends on**: ImageLoader, AIServiceInterface
    - **Depended on by**: PreviewPanel
    - **Responsibility**: Processes images and coordinates with AI services

### AI Integration Layer

12. **AIServiceInterface**
    - **Depends on**: None
    - **Depended on by**: ImageProcessor, GeminiAIProvider
    - **Responsibility**: Defines interface for AI service providers

13. **GeminiAIProvider**
    - **Depends on**: AIServiceInterface, PromptManager
    - **Depended on by**: None
    - **Responsibility**: Integrates with Google Gemini AI API

14. **PromptManager**
    - **Depends on**: None
    - **Depended on by**: GeminiAIProvider, ResponseParser
    - **Responsibility**: Manages AI prompts and templates

15. **ResponseParser**
    - **Depends on**: PromptManager
    - **Depended on by**: GeminiAIProvider
    - **Responsibility**: Parses and validates AI responses

## Component Groupings

### User Interface Group
- WindowManager
- UIComponentFactory
- ControlPanel
- PreviewPanel
- ThemeManager

### Configuration Group
- ConfigurationMgr
- SettingsManager

### Image Processing Group
- ImageLoader
- ImageProcessor

### AI Integration Group
- AIServiceInterface
- GeminiAIProvider
- PromptManager
- ResponseParser

### File System Group
- FileSystemManager

## Potential Dependency Issues

### Circular Dependencies
1. **GeminiAIProvider ↔ ResponseParser**
   - GeminiAIProvider depends on ResponseParser to process AI responses
   - ResponseParser may need to reference GeminiAIProvider for response context
   - **Resolution**: Introduce a response context object that both can share

2. **UIComponentFactory ↔ ThemeManager**
   - UIComponentFactory depends on ThemeManager for styling
   - ThemeManager depends on UIComponentFactory for component creation
   - **Resolution**: Extract a common interface or introduce a mediator

### High Coupling Areas

1. **ImageProcessor**
   - Has multiple dependencies (ImageLoader, AIServiceInterface)
   - Is depended on by PreviewPanel
   - **Mitigation**: Consider breaking into smaller, more focused components

2. **WindowManager**
   - Central hub for UI components
   - **Mitigation**: Consider implementing a pub/sub pattern to reduce direct dependencies

## Implementation Sequence Considerations

Based on the dependencies, a logical implementation sequence would be:

1. First Layer (No Dependencies)
   - FileSystemManager
   - AIServiceInterface
   - PromptManager

2. Second Layer
   - ConfigurationMgr
   - ImageLoader
   - ResponseParser
   - GeminiAIProvider

3. Third Layer
   - ApplicationCore
   - UIComponentFactory
   - ImageProcessor

4. Fourth Layer
   - WindowManager
   - SettingsManager

5. Fifth Layer
   - ControlPanel
   - PreviewPanel
   - ThemeManager

This sequence minimizes the need for mocking during development and enables incremental testing of the components.

## Dependency Injection Strategy

To manage these dependencies effectively, the application will use dependency injection:

1. **Constructor Injection**: For required dependencies
2. **Property Injection**: For optional dependencies
3. **Service Locator Pattern**: For cross-cutting concerns

Example for ImageProcessor:

```python
class ImageProcessor:
    def __init__(self, image_loader: ImageLoader, ai_service: AIServiceInterface):
        self.image_loader = image_loader
        self.ai_service = ai_service

    # Methods that use the injected dependencies
```

## Updating This Diagram

As the implementation progresses, this dependency diagram should be updated to reflect changes in component relationships. When adding new components or modifying dependencies, update both the diagram and the textual descriptions in this document.

---

*Last Updated: [Date]*