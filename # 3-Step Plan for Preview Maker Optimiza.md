# 3-Step Plan for Preview Maker Optimization

## Phase 1: Fix Code Duplication and Reference Errors

### Comprehensive View
The first phase addresses the critical issue of code duplication and undefined variable references found in the Preview Maker application. The code currently contains nearly identical implementations for setting up the text view (once around line 713 and again around line 1805), with the second instance referencing undefined variables. This duplication can lead to inconsistent behavior, maintenance difficulties, and runtime errors. The goal is to consolidate the duplicated code into a single, reusable method, and ensure all referenced variables are properly defined.

### Steps to Implement
1. **Create a helper method for text view initialization:**
   - Define a new method `_setup_prompt_text_view(self, container)` in the PreviewMaker class
   - Move the common code for initializing TextView, setting properties, and adding controllers
   - See GTK4 documentation: https://docs.gtk.org/gtk4/class.TextView.html

2. **Extract CSS styling to a separate method:**
   - Create a `_setup_prompt_text_view_css(self)` method
   - Implement proper GTK4 CSS provider instantiation and application
   - Reference: https://docs.gtk.org/gtk4/class.CssProvider.html

3. **Fix variable references:**
   - Locate all instances of undefined variables (e.g., `manual_window`, `target_section`)
   - Ensure each variable is properly defined before use
   - Replace duplicate code around line 1805 with calls to the new helper methods

4. **Consolidate placeholder text handling:**
   - Make `prompt_buffer`, `is_placeholder_visible`, and `placeholder_text` instance variables
   - Ensure the focus handlers consistently manage placeholder state
   - Update references to old variables (`prompt_text_view` → `prompt_entry_view`)

### Verification
1. Run the application and verify that the prompt text view initializes correctly
2. Test that placeholder text appears and disappears properly on focus events
3. Confirm that no exceptions are thrown related to undefined variables
4. Validate that all text editing functionality works as expected in the manual mode window

## Phase 2: Update Deprecated GTK4 Methods

### Comprehensive View
The second phase focuses on addressing the use of deprecated GTK4 methods in the Preview Maker application. The code currently uses several deprecated functions, such as `get_style_context()`, `add_class()`, and `set_keep_aspect_ratio()`, which generate warnings and may become unsupported in future GTK4 versions. This phase will modernize the code by replacing these deprecated methods with their recommended alternatives, improve event controller implementation, and ensure proper GTK4 widget management.

### Steps to Implement
1. **Replace deprecated styling methods:**
   - Replace all instances of `widget.get_style_context().add_class()` with `widget.add_css_class()`
   - Update CSS provider loading to use the modern GTK4 approach
   - Documentation: https://docs.gtk.org/gtk4/class.Widget.html#methods

2. **Update Picture widget handling:**
   - Replace `picture.set_keep_aspect_ratio(True)` with the recommended alternative
   - Use `set_content_fit()` to control how the picture scales
   - Reference: https://docs.gtk.org/gtk4/class.Picture.html

3. **Improve event controller implementation:**
   - Review all GestureClick, EventControllerFocus, and other controllers
   - Ensure proper propagation phases are set for each controller
   - Fix the `PickFlags.DEFAULT` usage in `on_window_click()`
   - See: https://docs.gtk.org/gtk4/input-handling.html

4. **Refactor focus management:**
   - Implement a consistent focus management approach across the application
   - Use `set_focusable(True)` where appropriate
   - Update focus handling to follow GTK4 guidelines

### Verification
1. Run the application with `G_ENABLE_DIAGNOSTIC=1` to check for GTK deprecation warnings
2. Verify that no deprecated function warnings appear in the console
3. Test all UI interactions to ensure they work as expected after the updates
4. Confirm that focus handling behaves correctly when clicking inside/outside the text view

## Phase 3: Optimize Code Organization and Error Handling

### Comprehensive View
The third phase addresses broader code quality issues in the Preview Maker application. The current code suffers from excessive length (2489 lines), inconsistent error handling, and suboptimal import organization. This phase will refactor the application to improve maintainability, reliability, and user experience through better code organization, consistent error handling, and improved memory management.

### Steps to Implement
1. **Reorganize and clean up imports:**
   - Move all imports to the top of the file
   - Remove unused imports (toml, json, etc.)
   - Group imports logically (standard library, third-party, local)
   - Properly handle conditional imports for optional dependencies

2. **Refactor large methods:**
   - Break down `open_manual_mode_window()` (497 lines) into smaller, focused functions
   - Create separate methods for UI section creation (e.g., `_create_prompt_section()`, `_create_debug_section()`)
   - Extract repetitive UI building patterns into helper methods
   - Limit method size to 100 lines maximum

3. **Implement consistent error handling:**
   - Create standardized error handling methods for different error types
   - Ensure all file operations have proper try/except blocks
   - Add informative user feedback for all error conditions
   - Handle API failures gracefully with appropriate fallback mechanisms

4. **Improve memory management:**
   - Ensure proper cleanup of controllers and CSS providers
   - Add explicit cleanup in the `do_shutdown()` method
   - Implement resource tracking for dynamic UI elements
   - Fix any potential memory leaks with large objects

### Verification
1. Run static code analysis to verify improved code structure and reduced complexity
2. Test error scenarios (missing files, API failures) to confirm proper error handling
3. Verify that the application starts and runs without warnings or errors
4. Confirm that all functionality works identically to the previous version
5. Check that the application cleanly shuts down without resource leaks

Each of these phases addresses specific aspects of the codebase, and when completed sequentially, will result in a more maintainable, reliable, and future-proof application.
