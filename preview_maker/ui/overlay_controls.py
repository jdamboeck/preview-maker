"""UI control panel for manual overlay management.

This module contains the OverlayControlPanel class, which provides UI controls
for manipulating overlays in the ManualOverlayManager.
"""

from typing import Optional, Any

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk

from preview_maker.core.logging import get_logger
from preview_maker.ui.manual_overlay_manager import ManualOverlayManager

# Get a logger for this component
logger = get_logger("overlay_controls")


class OverlayControlPanel(Gtk.Box):
    """UI control panel for managing manual overlays.

    This class provides a set of UI controls for creating, selecting,
    and modifying overlays in the ManualOverlayManager.

    Attributes:
        overlay_manager: The ManualOverlayManager instance
        radius_adjustment: Adjustment for the radius slider
        radius_scale: Scale widget for adjusting overlay radius
        create_button: Button for creating a new overlay
        delete_button: Button for deleting the selected overlay
        color_button: Button for selecting overlay color
    """

    def __init__(self, overlay_manager: ManualOverlayManager) -> None:
        """Initialize the overlay control panel.

        Args:
            overlay_manager: The ManualOverlayManager to control
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_margin_start(12)
        self.set_margin_end(12)
        self.set_margin_top(12)
        self.set_margin_bottom(12)

        self.overlay_manager = overlay_manager

        # Set up overlay selection callback
        self.overlay_manager.on_overlay_selected = self._on_overlay_selected

        # Create the controls
        self._create_header()
        self._create_size_controls()
        self._create_color_controls()
        self._create_action_buttons()

        # Initially disable controls until an overlay is selected
        self._update_controls_state(False)

        logger.debug("OverlayControlPanel initialized")

    def _create_header(self) -> None:
        """Create the panel header with title."""
        header_label = Gtk.Label()
        header_label.set_markup("<b>Overlay Controls</b>")
        header_label.set_halign(Gtk.Align.START)
        header_label.set_margin_bottom(6)
        self.append(header_label)

        instruction_label = Gtk.Label(label="Double-click to create, drag to move")
        instruction_label.set_halign(Gtk.Align.START)
        instruction_label.set_margin_bottom(12)
        instruction_label.add_css_class("dim-label")
        self.append(instruction_label)

    def _create_size_controls(self) -> None:
        """Create controls for adjusting overlay size."""
        # Size label
        size_label = Gtk.Label(label="Size:")
        size_label.set_halign(Gtk.Align.START)
        size_label.set_margin_bottom(4)
        self.append(size_label)

        # Size adjustment with slider
        self.radius_adjustment = Gtk.Adjustment(
            value=50,
            lower=10,
            upper=200,
            step_increment=1,
            page_increment=10,
        )
        self.radius_scale = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL,
            adjustment=self.radius_adjustment,
        )
        self.radius_scale.set_digits(0)
        self.radius_scale.set_value_pos(Gtk.PositionType.RIGHT)
        self.radius_scale.set_margin_bottom(12)
        self.radius_scale.connect("value-changed", self._on_radius_changed)
        self.append(self.radius_scale)

    def _create_color_controls(self) -> None:
        """Create controls for selecting overlay color."""
        # Color label
        color_label = Gtk.Label(label="Color:")
        color_label.set_halign(Gtk.Align.START)
        color_label.set_margin_bottom(4)
        self.append(color_label)

        # Color button
        self.color_button = Gtk.ColorButton()
        self.color_button.set_name("overlay-color-button")

        # Set initial color - use RGBA compatible with GTK 4.0
        rgba = Gdk.RGBA()
        rgba.parse("#ff0000")  # Default red color
        self.color_button.set_rgba(rgba)

        self.color_button.set_margin_bottom(12)
        self.color_button.connect("color-set", self._on_color_changed)

        # Color button container for proper alignment
        color_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        color_box.append(self.color_button)
        self.append(color_box)

    def _create_action_buttons(self) -> None:
        """Create action buttons for overlay management."""
        # Button container
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        button_box.set_margin_top(12)

        # Create overlay button
        self.create_button = Gtk.Button(label="Create Overlay")
        self.create_button.set_name("create-overlay-button")
        self.create_button.connect("clicked", self._on_create_clicked)
        button_box.append(self.create_button)

        # Delete button
        self.delete_button = Gtk.Button(label="Delete Overlay")
        self.delete_button.set_name("delete-overlay-button")
        self.delete_button.connect("clicked", self._on_delete_clicked)
        self.delete_button.add_css_class("destructive-action")
        button_box.append(self.delete_button)

        self.append(button_box)

    def _on_radius_changed(self, scale: Any) -> None:
        """Handle changes to the radius slider.

        Args:
            scale: The scale widget that changed
        """
        radius = int(scale.get_value())
        self.overlay_manager.set_overlay_radius(radius)
        logger.debug(f"Changed overlay radius to {radius}")

    def _on_color_changed(self, button: Any) -> None:
        """Handle changes to the color selection.

        Args:
            button: The color button that changed
        """
        rgba = button.get_rgba()
        # Convert RGBA to hex format
        hex_color = "#{:02x}{:02x}{:02x}".format(
            int(rgba.red * 255),
            int(rgba.green * 255),
            int(rgba.blue * 255),
        )

        # Update default color for new overlays
        self.overlay_manager.default_color = hex_color

        # Update the selected overlay if any
        if self.overlay_manager.selected_overlay_id:
            # This would require extending the overlay manager to support color changes
            # For now, we'll just update the default color for new overlays
            pass

        logger.debug(f"Changed overlay color to {hex_color}")

    def _on_create_clicked(self, button: Any) -> None:
        """Handle click on the create overlay button.

        Args:
            button: The button that was clicked
        """
        # Get image dimensions from image view
        image = self.overlay_manager.image_view.get_image()
        if not image:
            logger.warning("Cannot create overlay: No image loaded")
            return

        # Create overlay at center of image
        center_x = image.width // 2
        center_y = image.height // 2
        self.overlay_manager.create_overlay_at(center_x, center_y)
        logger.debug(f"Created overlay at center ({center_x}, {center_y})")

    def _on_delete_clicked(self, button: Any) -> None:
        """Handle click on the delete overlay button.

        Args:
            button: The button that was clicked
        """
        self.overlay_manager.delete_selected_overlay()
        logger.debug("Deleted selected overlay")

    def _on_overlay_selected(self, overlay_id: Optional[str]) -> None:
        """Handle overlay selection changes.

        Args:
            overlay_id: ID of the selected overlay, or None if deselected
        """
        # Update UI state based on selection
        has_selection = overlay_id is not None
        self._update_controls_state(has_selection)

        # Update radius slider if an overlay is selected
        if has_selection:
            selected = self.overlay_manager.get_selected_overlay()
            if selected:
                _, (_, _, radius) = selected
                self.radius_adjustment.set_value(radius)

        logger.debug(f"Selected overlay changed: {overlay_id}")

    def _update_controls_state(self, has_selection: bool) -> None:
        """Update the enabled state of controls based on selection.

        Args:
            has_selection: Whether an overlay is currently selected
        """
        # The radius slider and delete button are only enabled when an overlay is selected
        self.radius_scale.set_sensitive(has_selection)
        self.delete_button.set_sensitive(has_selection)

        # The create button is always enabled as long as there's an image
        has_image = self.overlay_manager.image_view.get_image() is not None
        self.create_button.set_sensitive(has_image)
