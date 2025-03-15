# Rebuild Plan for Preview Maker UI

## Current Issues Assessment

After reviewing the changes made during refactoring, I've identified several critical UI components and functionality that were lost in the manual mode window:

1. **Two-Panel Layout Structure**: The horizontal layout with image on left and controls on right was replaced with a simplified vertical layout
2. **Description Display**: The scrollable AI description section is completely missing
3. **Prompt Configuration**: The prompt customization section with target type selection is absent
4. **Advanced Controls**: Size and zoom sliders for adjusting the detection parameters are gone
5. **Progress Indicators**: The spinner for showing detection progress was removed
6. **Coordinate Initialization**: Several critical coordinate initializations were omitted
7. **Help Text**: User guidance text explaining how to interact with the image is missing
8. **Output Picture Handling**: References to `output_picture` are present but the variable is never defined

## Detailed Rebuild Plan

### Phase 1: Restore Core Layout and Structure

1. Create a `_create_ui_layout` method to establish the two-panel structure:
   - Main horizontal box to contain both panels
   - Left panel for image viewing
   - Right panel for all controls and settings
   - Proper spacing and margins for both panels

2. Fix the missing variable initializations:
   ```python
   # Initialize coordinate tracking
   self.selected_magnification_point_norm = (-1.0, -1.0)
   self.selected_preview_point_norm = (-1.0, -1.0)
   self.selected_magnification_point = (-200, -200)
   self.selected_preview_point = (-600, -600)

   # Initialize display properties
   self.display_width = image.width
   self.display_height = image.height
   self.display_scale = scale_factor
   ```

### Phase 2: Rebuild UI Components

3. Create a `_create_description_section` method:
   - Frame with "AI Description" label
   - Scrollable text area
   - Initial descriptive text
   - Proper CSS styling

4. Create a `_create_prompt_section` method:
   - Frame with "Detection Prompt" label
   - Target type input section
   - Prompt text view with scroll support
   - Reset and save buttons

5. Create a `_create_debug_section` method:
   - Selection size slider (0.05 to 0.3 range)
   - Zoom factor slider (1.5 to 5.0 range)
   - Event handlers for slider changes

6. Add the missing feedback components:
   - Spinner for detection progress
   - Help text explaining click interactions
   - Fix `output_picture` property initialization

### Phase 3: Integration and Testing

7. Update `open_manual_mode_window` to use all new components:
   - Create layout structure
   - Add all UI sections in proper order
   - Ensure all event handlers are connected
   - Restore automatic detection on window creation

8. Test all functionality after rebuilding:
   - Verify image loading and display
   - Test detection with different prompt settings
   - Confirm coordinate tracking works properly
   - Validate that all UI elements respond appropriately

## Detailed Action Plan Prompt

```
# UI Reconstruction Plan for Preview Maker

I need to restore the missing UI components in the manual mode window while maintaining the code quality improvements from our refactoring work. The plan below outlines how to rebuild the interface.

## Step 1: Create Layout Framework Method
Create a new `_create_ui_layout` method that:
- Takes parameters: image, window
- Creates a horizontal box (hbox) for the two-panel layout
- Sets up left panel for image with frame and proper expansion
- Sets up right panel for controls with consistent spacing
- Returns references to both panels for populating

## Step 2: Restore Image Section with Proper Initialization
Update the `_create_image_section` method to:
- Create a proper image container with margins and frame
- Initialize coordinate tracking variables
- Add spinner overlay for processing feedback
- Ensure proper event handling for clicks
- Set all required display properties

## Step 3: Build Description Section
Add a `_create_description_section` method that:
- Creates a framed section with "AI Description" label
- Adds scrollable text area with proper styling
- Sets up the description_label properly
- Returns the frame for adding to the control panel

## Step 4: Rebuild Prompt Configuration
Add a `_create_prompt_section` method that:
- Creates a frame with "Detection Prompt" label
- Sets up target type input
- Integrates the existing prompt text view setup
- Adds buttons for prompt management
- Adds helper text about targeting precision

## Step 5: Add Debug Controls
Create a `_create_debug_section` method for:
- Selection size slider with range 0.05-0.3
- Zoom factor slider with range 1.5-5.0
- Event connections for real-time updates
- Clear explanatory labels

## Step 6: Add Help and Feedback Elements
- Add help text explaining mouse interactions
- Ensure spinner is properly initialized and connected
- Add proper output_picture handling

## Step 7: Update open_manual_mode_window
Modify to:
- Use the layout framework
- Add all sections in the proper order
- Ensure event handlers are connected
- Fix output_picture reference
- Restore automatic detection on window creation

## Step 8: Testing Requirements
Test that:
- Layout appears correctly with proper sizing
- All controls function as expected
- Detection works with different settings
- Image display and overlay rendering works
- Coordinate tracking functions properly
```

Go step by step through this plan till you have a cheack hbehind every step

