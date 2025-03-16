"""Manual overlay management component for Preview Maker.

This module contains the ManualOverlayManager class, which is responsible for
creating and managing circular overlays on images with manual positioning.
"""

import uuid
from typing import Optional, Tuple, Callable

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from PIL import Image
from preview_maker.core.logging import get_logger
from preview_maker.ui.overlay_manager import OverlayManager

# Get a logger for this component
logger = get_logger("manual_overlay")


class ManualOverlayManager(OverlayManager):
    """Manages manually positioned overlays for highlighting regions of interest on images.

    This class extends OverlayManager to provide manual creation and positioning
    of circular overlays on images, without requiring AI analysis.

    Attributes:
        image_view: The ImageView component this manager works with
        overlays: Dictionary of active overlays with their coordinates
        image_processor: The ImageProcessor for creating overlays
        selected_overlay_id: ID of the currently selected overlay
        default_radius: Default radius for new overlays
        default_color: Default color for new overlays
        on_overlay_selected: Callback for when an overlay is selected
        on_overlay_changed: Callback for when an overlay is modified
    """

    def __init__(self, image_view) -> None:
        """Initialize the ManualOverlayManager.

        Args:
            image_view: The ImageView component this manager works with
        """
        super().__init__(image_view)
        self.selected_overlay_id: Optional[str] = None
        self.default_radius: int = 50
        self.default_color: str = "#ff0000"
        self.on_overlay_selected: Optional[Callable[[Optional[str]], None]] = None
        self.on_overlay_changed: Optional[Callable[[], None]] = None

        # Set up event controllers for the image view
        self._setup_controllers()

        logger.debug("ManualOverlayManager initialized")

    def _setup_controllers(self) -> None:
        """Set up event controllers for mouse interaction with overlays."""
        # Click controller for selecting overlays
        click_controller = Gtk.GestureClick.new()
        click_controller.set_button(1)  # Left mouse button
        click_controller.connect("pressed", self._on_click_pressed)
        self.image_view.add_controller(click_controller)

        # Motion controller for hover effects
        motion_controller = Gtk.EventControllerMotion.new()
        motion_controller.connect("motion", self._on_motion)
        self.image_view.add_controller(motion_controller)

        # Drag controller for moving overlays
        drag_controller = Gtk.GestureDrag.new()
        drag_controller.connect("drag-begin", self._on_drag_begin)
        drag_controller.connect("drag-update", self._on_drag_update)
        drag_controller.connect("drag-end", self._on_drag_end)
        self.image_view.add_controller(drag_controller)

    def create_overlay_at(self, x: int, y: int) -> str:
        """Create a new overlay at the specified position.

        Args:
            x: X-coordinate center of the overlay
            y: Y-coordinate center of the overlay

        Returns:
            ID of the created overlay
        """
        # Generate a unique ID for the overlay
        overlay_id = str(uuid.uuid4())

        # Add the overlay
        success = self.add_overlay(
            overlay_id, x, y, self.default_radius, self.default_color
        )

        if success:
            # Select the new overlay
            self.select_overlay(overlay_id)
            logger.debug(f"Created overlay {overlay_id} at ({x}, {y})")
            return overlay_id
        else:
            logger.warning("Failed to create overlay")
            return ""

    def select_overlay(self, overlay_id: Optional[str]) -> None:
        """Select an overlay by ID.

        Args:
            overlay_id: ID of the overlay to select, or None to deselect
        """
        # Deselect current overlay if different
        if self.selected_overlay_id != overlay_id:
            self.selected_overlay_id = overlay_id

            # Notify listeners
            if self.on_overlay_selected:
                self.on_overlay_selected(overlay_id)

            # Refresh display to show selection highlight
            self._apply_overlays(self.image_view.get_image())

            logger.debug(f"Selected overlay: {overlay_id}")

    def get_selected_overlay(self) -> Optional[Tuple[str, Tuple[int, int, int]]]:
        """Get the currently selected overlay.

        Returns:
            Tuple of (overlay_id, (x, y, radius)) or None if no overlay is selected
        """
        if (
            not self.selected_overlay_id
            or self.selected_overlay_id not in self.overlays
        ):
            return None

        return (self.selected_overlay_id, self.overlays[self.selected_overlay_id])

    def update_selected_overlay(
        self, x: int = None, y: int = None, radius: int = None
    ) -> bool:
        """Update the position or size of the selected overlay.

        Args:
            x: New X-coordinate (optional)
            y: New Y-coordinate (optional)
            radius: New radius (optional)

        Returns:
            True if update was successful, False otherwise
        """
        if (
            not self.selected_overlay_id
            or self.selected_overlay_id not in self.overlays
        ):
            logger.warning("No overlay selected for update")
            return False

        # Get current values
        current_x, current_y, current_radius = self.overlays[self.selected_overlay_id]

        # Update with new values if provided
        new_x = x if x is not None else current_x
        new_y = y if y is not None else current_y
        new_radius = radius if radius is not None else current_radius

        # Update the overlay
        self.overlays[self.selected_overlay_id] = (new_x, new_y, new_radius)

        # Refresh display
        self._apply_overlays(self.image_view.get_image())

        # Notify listeners
        if self.on_overlay_changed:
            self.on_overlay_changed()

        logger.debug(
            f"Updated overlay {self.selected_overlay_id} to ({new_x}, {new_y}, {new_radius})"
        )
        return True

    def set_overlay_radius(self, radius: int) -> bool:
        """Set the radius of the selected overlay.

        Args:
            radius: New radius value

        Returns:
            True if update was successful, False otherwise
        """
        return self.update_selected_overlay(radius=radius)

    def delete_selected_overlay(self) -> bool:
        """Delete the currently selected overlay.

        Returns:
            True if deletion was successful, False otherwise
        """
        if not self.selected_overlay_id:
            logger.warning("No overlay selected for deletion")
            return False

        # Store ID for log message
        overlay_id = self.selected_overlay_id

        # Remove the overlay
        success = self.remove_overlay(overlay_id)

        # Clear selection
        self.selected_overlay_id = None

        # Notify listeners
        if success and self.on_overlay_selected:
            self.on_overlay_selected(None)

        logger.debug(f"Deleted overlay {overlay_id}")
        return success

    def _find_overlay_at_position(self, x: int, y: int) -> Optional[str]:
        """Find the overlay at the given position.

        Args:
            x: X-coordinate
            y: Y-coordinate

        Returns:
            ID of the overlay at the position, or None if no overlay is found
        """
        # Check each overlay
        for overlay_id, (ox, oy, radius) in self.overlays.items():
            # Calculate distance from click to overlay center
            distance = ((x - ox) ** 2 + (y - oy) ** 2) ** 0.5

            # Check if click is within the overlay radius
            if distance <= radius:
                return overlay_id

        return None

    def _on_click_pressed(
        self, controller: Gtk.GestureClick, n_press: int, x: float, y: float
    ) -> None:
        """Handle mouse click events for overlay selection.

        Args:
            controller: The GestureClick controller
            n_press: Number of clicks
            x: X-coordinate of the click
            y: Y-coordinate of the click
        """
        # Convert to integer coordinates
        ix, iy = int(x), int(y)

        # Find if we clicked on an overlay
        overlay_id = self._find_overlay_at_position(ix, iy)

        if overlay_id:
            # Select the overlay
            self.select_overlay(overlay_id)
        else:
            # Deselect if we clicked outside
            self.select_overlay(None)

            # Create a new overlay if double-clicked
            if n_press == 2:
                self.create_overlay_at(ix, iy)

    def _on_motion(
        self, controller: Gtk.EventControllerMotion, x: float, y: float
    ) -> None:
        """Handle mouse motion events for overlay hover effects.

        Args:
            controller: The EventControllerMotion controller
            x: X-coordinate of the mouse
            y: Y-coordinate of the mouse
        """
        # Implementation for hover effects can be added here
        pass

    def _on_drag_begin(self, controller: Gtk.GestureDrag, x: float, y: float) -> None:
        """Handle the start of a drag operation for moving overlays.

        Args:
            controller: The GestureDrag controller
            x: X-coordinate of the drag start
            y: Y-coordinate of the drag start
        """
        # Convert to integer coordinates
        ix, iy = int(x), int(y)

        # Check if we're starting to drag an overlay
        overlay_id = self._find_overlay_at_position(ix, iy)

        if overlay_id:
            # Select the overlay if it's not already selected
            self.select_overlay(overlay_id)

            # Store the start position for reference
            controller.set_data("drag_start_x", ix)
            controller.set_data("drag_start_y", iy)
            controller.set_data("dragging_overlay", True)
        else:
            controller.set_data("dragging_overlay", False)

    def _on_drag_update(
        self, controller: Gtk.GestureDrag, x_offset: float, y_offset: float
    ) -> None:
        """Handle drag updates for moving overlays.

        Args:
            controller: The GestureDrag controller
            x_offset: X-offset from the drag start
            y_offset: Y-offset from the drag start
        """
        # Check if we're dragging an overlay
        dragging_overlay = controller.get_data("dragging_overlay")
        if not dragging_overlay or not self.selected_overlay_id:
            return

        # Get the start position
        start_x = controller.get_data("drag_start_x")
        start_y = controller.get_data("drag_start_y")

        if start_x is None or start_y is None:
            return

        # Calculate new position
        new_x = start_x + int(x_offset)
        new_y = start_y + int(y_offset)

        # Update the overlay position
        self.update_selected_overlay(x=new_x, y=new_y)

    def _on_drag_end(
        self, controller: Gtk.GestureDrag, x_offset: float, y_offset: float
    ) -> None:
        """Handle the end of a drag operation.

        Args:
            controller: The GestureDrag controller
            x_offset: X-offset from the drag start
            y_offset: Y-offset from the drag start
        """
        # Clear drag data
        controller.set_data("drag_start_x", None)
        controller.set_data("drag_start_y", None)
        controller.set_data("dragging_overlay", False)

    def _apply_overlays(self, image: Image.Image, color: str = "#ff0000") -> None:
        """Apply all overlays to the image with selection highlight.

        Overrides the parent method to add visual indication for the selected overlay.

        Args:
            image: The base image to apply overlays to
            color: Default color of the overlays in hex format
        """
        if not image or not self.overlays:
            # No image or no overlays to apply
            return

        # Make a copy of the image to avoid modifying the original
        result_image = image.copy()

        # Apply each overlay
        for overlay_id, (x, y, radius) in self.overlays.items():
            # Use a different color or style for the selected overlay
            overlay_color = (
                "#00ff00" if overlay_id == self.selected_overlay_id else color
            )

            # Create circular overlay
            overlay = self.image_processor.create_circular_overlay(
                (image.width, image.height), (x, y), radius, overlay_color
            )

            # Composite the overlay onto the image
            result_image = Image.alpha_composite(result_image.convert("RGBA"), overlay)

        # Update the image view
        self.image_view.set_image(result_image)
