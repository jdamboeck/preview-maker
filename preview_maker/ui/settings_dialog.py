"""Settings dialog for Preview Maker.

This module provides a dialog for configuring application settings
using GTK 4.0 with a tabbed interface for different setting categories.
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk

import logging
from typing import Dict, Any, Optional, Union, List

from preview_maker.core.config import ConfigManager, config_manager

logger = logging.getLogger(__name__)


class SettingsDialog(Gtk.Dialog):
    """Dialog for configuring application settings."""

    def __init__(self, parent: Gtk.Window):
        """Initialize the settings dialog.
        
        Args:
            parent: The parent window for this dialog
        """
        super().__init__(
            title="Settings",
            transient_for=parent,
            modal=True,
            destroy_with_parent=True
        )
        
        # Set up UI
        self.set_default_size(500, 500)
        
        # Add buttons
        self.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        self.add_button("_Apply", Gtk.ResponseType.APPLY)
        self.add_button("_OK", Gtk.ResponseType.OK)
        
        # Create notebook with tabs
        self._notebook = Gtk.Notebook()
        self._notebook.set_margin_top(12)
        self._notebook.set_margin_bottom(12)
        self._notebook.set_margin_start(12)
        self._notebook.set_margin_end(12)
        
        # Get content area and add notebook
        content_area = self.get_content_area()
        content_area.append(self._notebook)
        
        # Create tabs
        self._create_general_tab()
        self._create_api_tab()
        self._create_overlay_tab()
        self._create_export_tab()
        
        # Connect signals
        self.connect("response", self._on_response)
        
        # Store original settings for cancel
        self._current_settings = {}
        self._load_settings()

    def _create_general_tab(self) -> None:
        """Create the general settings tab."""
        tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        tab.set_margin_top(12)
        tab.set_margin_bottom(12)
        tab.set_margin_start(12)
        tab.set_margin_end(12)
        
        # Debug mode checkbox
        self._debug_checkbox = Gtk.CheckButton()
        self._debug_checkbox.set_label("Debug Mode")
        self._debug_checkbox.set_tooltip_text("Enable detailed debug logging and UI elements")
        tab.append(self._debug_checkbox)
        
        # Window size settings
        size_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        size_box.set_margin_top(12)
        
        width_label = Gtk.Label(label="Window Width:")
        width_label.set_halign(Gtk.Align.START)
        width_label.set_margin_end(6)
        
        self._width_entry = Gtk.Entry()
        self._width_entry.set_name("window-width-entry")
        self._width_entry.set_width_chars(6)
        
        height_label = Gtk.Label(label="Window Height:")
        height_label.set_halign(Gtk.Align.START)
        height_label.set_margin_start(12)
        height_label.set_margin_end(6)
        
        self._height_entry = Gtk.Entry()
        self._height_entry.set_name("window-height-entry")
        self._height_entry.set_width_chars(6)
        
        size_box.append(width_label)
        size_box.append(self._width_entry)
        size_box.append(height_label)
        size_box.append(self._height_entry)
        
        tab.append(size_box)
        
        # Language selection
        language_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        language_box.set_margin_top(12)
        
        language_label = Gtk.Label(label="Language:")
        language_label.set_halign(Gtk.Align.START)
        language_label.set_margin_end(6)
        
        self._language_combo = Gtk.ComboBoxText()
        self._language_combo.set_name("language-combo")
        
        # Add languages
        self._language_combo.append_text("English")
        self._language_combo.append_text("German")
        
        # Default to English for now
        self._language_combo.set_active(0)
        
        language_box.append(language_label)
        language_box.append(self._language_combo)
        
        tab.append(language_box)
        
        # Add tab to notebook
        label = Gtk.Label(label="General")
        self._notebook.append_page(tab, label)

    def _create_api_tab(self) -> None:
        """Create the API settings tab."""
        tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        tab.set_margin_top(12)
        tab.set_margin_bottom(12)
        tab.set_margin_start(12)
        tab.set_margin_end(12)
        
        # API key section
        api_key_label = Gtk.Label()
        api_key_label.set_markup("<b>Gemini API Key</b>")
        api_key_label.set_halign(Gtk.Align.START)
        tab.append(api_key_label)
        
        api_key_desc = Gtk.Label()
        api_key_desc.set_text("Enter your Google Gemini API key. This key is required for image analysis.")
        api_key_desc.set_wrap(True)
        api_key_desc.set_halign(Gtk.Align.START)
        api_key_desc.set_margin_start(12)
        api_key_desc.set_margin_bottom(6)
        tab.append(api_key_desc)
        
        # API key entry
        api_key_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        api_key_box.set_margin_start(12)
        
        api_key_entry_label = Gtk.Label(label="API Key:")
        api_key_entry_label.set_halign(Gtk.Align.START)
        api_key_entry_label.set_margin_end(6)
        
        self._api_key_entry = Gtk.Entry()
        self._api_key_entry.set_name("api-key-entry")
        self._api_key_entry.set_visibility(False)  # Hide API key
        self._api_key_entry.set_hexpand(True)
        self._api_key_entry.set_placeholder_text("Enter your API key")
        
        api_key_box.append(api_key_entry_label)
        api_key_box.append(self._api_key_entry)
        tab.append(api_key_box)
        
        # Model settings section
        model_label = Gtk.Label()
        model_label.set_markup("<b>Model Settings</b>")
        model_label.set_halign(Gtk.Align.START)
        model_label.set_margin_top(12)
        tab.append(model_label)
        
        # Model selection combobox
        model_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        model_box.set_margin_start(12)
        model_box.set_margin_top(6)
        
        model_combo_label = Gtk.Label(label="Model:")
        model_combo_label.set_halign(Gtk.Align.START)
        model_combo_label.set_margin_end(6)
        
        self._model_combo = Gtk.ComboBoxText()
        self._model_combo.set_name("model-combo")
        
        # Add models
        self._model_combo.append_text("gemini-1.5-flash")
        self._model_combo.append_text("gemini-1.5-pro")
        self._model_combo.append_text("gemini-1.0-pro-vision")
        
        model_box.append(model_combo_label)
        model_box.append(self._model_combo)
        tab.append(model_box)
        
        # Temperature setting
        temp_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        temp_box.set_margin_start(12)
        temp_box.set_margin_top(6)
        
        temp_label = Gtk.Label(label="Temperature:")
        temp_label.set_halign(Gtk.Align.START)
        temp_label.set_margin_end(6)
        
        self._temp_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        self._temp_scale.set_name("temperature-scale")
        self._temp_scale.set_range(0.0, 1.0)
        self._temp_scale.set_digits(2)
        self._temp_scale.set_draw_value(True)
        self._temp_scale.set_hexpand(True)
        
        temp_box.append(temp_label)
        temp_box.append(self._temp_scale)
        tab.append(temp_box)
        
        # Add tab to notebook
        label = Gtk.Label(label="API Settings")
        self._notebook.append_page(tab, label)

    def _create_overlay_tab(self) -> None:
        """Create the overlay settings tab."""
        tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        tab.set_margin_top(12)
        tab.set_margin_bottom(12)
        tab.set_margin_start(12)
        tab.set_margin_end(12)
        
        # Selection ratio scale
        ratio_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        ratio_label = Gtk.Label()
        ratio_label.set_markup("<b>Selection Size</b>")
        ratio_label.set_halign(Gtk.Align.START)
        ratio_box.append(ratio_label)
        
        ratio_desc = Gtk.Label()
        ratio_desc.set_text("Set the default size for overlay selections as a percentage of the image")
        ratio_desc.set_wrap(True)
        ratio_desc.set_halign(Gtk.Align.START)
        ratio_desc.set_margin_start(12)
        ratio_box.append(ratio_desc)
        
        self._ratio_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        self._ratio_scale.set_name("selection-ratio-scale")
        self._ratio_scale.set_range(0.01, 0.3)
        self._ratio_scale.set_digits(2)
        self._ratio_scale.set_draw_value(True)
        self._ratio_scale.set_margin_start(12)
        ratio_box.append(self._ratio_scale)
        
        tab.append(ratio_box)
        
        # Zoom factor scale
        zoom_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        zoom_box.set_margin_top(12)
        
        zoom_label = Gtk.Label()
        zoom_label.set_markup("<b>Zoom Factor</b>")
        zoom_label.set_halign(Gtk.Align.START)
        zoom_box.append(zoom_label)
        
        zoom_desc = Gtk.Label()
        zoom_desc.set_text("Set the default zoom level for detail previews")
        zoom_desc.set_wrap(True)
        zoom_desc.set_halign(Gtk.Align.START)
        zoom_desc.set_margin_start(12)
        zoom_box.append(zoom_desc)
        
        self._zoom_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        self._zoom_scale.set_name("zoom-factor-scale")
        self._zoom_scale.set_range(1.0, 5.0)
        self._zoom_scale.set_digits(1)
        self._zoom_scale.set_draw_value(True)
        self._zoom_scale.set_margin_start(12)
        zoom_box.append(self._zoom_scale)
        
        tab.append(zoom_box)
        
        # Overlay color
        color_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        color_box.set_margin_top(12)
        
        color_label = Gtk.Label()
        color_label.set_markup("<b>Overlay Appearance</b>")
        color_label.set_halign(Gtk.Align.START)
        color_box.append(color_label)
        
        # Color picker
        color_picker_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        color_picker_box.set_margin_start(12)
        color_picker_box.set_margin_top(6)
        
        color_picker_label = Gtk.Label(label="Overlay Color:")
        color_picker_label.set_halign(Gtk.Align.START)
        color_picker_label.set_margin_end(6)
        
        self._color_button = Gtk.ColorButton()
        self._color_button.set_name("overlay-color-button")
        
        # Default to red
        rgba = Gdk.RGBA()
        rgba.parse("#FF0000")
        self._color_button.set_rgba(rgba)
        
        color_picker_box.append(color_picker_label)
        color_picker_box.append(self._color_button)
        color_box.append(color_picker_box)
        
        # Overlay opacity
        opacity_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        opacity_box.set_margin_start(12)
        opacity_box.set_margin_top(6)
        
        opacity_label = Gtk.Label(label="Overlay Opacity:")
        opacity_label.set_halign(Gtk.Align.START)
        opacity_label.set_margin_end(6)
        
        self._opacity_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        self._opacity_scale.set_name("overlay-opacity-scale")
        self._opacity_scale.set_range(0.1, 1.0)
        self._opacity_scale.set_digits(1)
        self._opacity_scale.set_draw_value(True)
        self._opacity_scale.set_hexpand(True)
        
        opacity_box.append(opacity_label)
        opacity_box.append(self._opacity_scale)
        color_box.append(opacity_box)
        
        tab.append(color_box)
        
        # Add tab to notebook
        label = Gtk.Label(label="Overlay Settings")
        self._notebook.append_page(tab, label)

    def _create_export_tab(self) -> None:
        """Create the export settings tab."""
        tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        tab.set_margin_top(12)
        tab.set_margin_bottom(12)
        tab.set_margin_start(12)
        tab.set_margin_end(12)
        
        # PNG compression section
        png_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        png_label = Gtk.Label()
        png_label.set_markup("<b>PNG Export Settings</b>")
        png_label.set_halign(Gtk.Align.START)
        png_box.append(png_label)
        
        png_desc = Gtk.Label()
        png_desc.set_text("Set the compression level for PNG exports (0 = best quality, 9 = best compression)")
        png_desc.set_wrap(True)
        png_desc.set_halign(Gtk.Align.START)
        png_desc.set_margin_start(12)
        png_box.append(png_desc)
        
        self._png_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        self._png_scale.set_name("png-compression-scale")
        self._png_scale.set_range(0, 9)
        self._png_scale.set_digits(0)
        self._png_scale.set_draw_value(True)
        self._png_scale.add_mark(0, Gtk.PositionType.BOTTOM, "Quality")
        self._png_scale.add_mark(9, Gtk.PositionType.BOTTOM, "Size")
        self._png_scale.set_margin_start(12)
        self._png_scale.set_margin_top(6)
        png_box.append(self._png_scale)
        
        tab.append(png_box)
        
        # Image quality section
        quality_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        quality_box.set_margin_top(12)
        
        quality_label = Gtk.Label()
        quality_label.set_markup("<b>Image Quality</b>")
        quality_label.set_halign(Gtk.Align.START)
        quality_box.append(quality_label)
        
        # High quality resampling checkbox
        self._high_quality_checkbox = Gtk.CheckButton()
        self._high_quality_checkbox.set_label("Use high quality resampling")
        self._high_quality_checkbox.set_tooltip_text("Uses better quality but slower resampling algorithm")
        self._high_quality_checkbox.set_margin_start(12)
        self._high_quality_checkbox.set_margin_top(6)
        quality_box.append(self._high_quality_checkbox)
        
        # Cache settings
        cache_label = Gtk.Label()
        cache_label.set_markup("Cache Size (MB):")
        cache_label.set_halign(Gtk.Align.START)
        cache_label.set_margin_start(12)
        cache_label.set_margin_top(12)
        quality_box.append(cache_label)
        
        self._cache_entry = Gtk.Entry()
        self._cache_entry.set_name("cache-size-entry")
        self._cache_entry.set_width_chars(6)
        self._cache_entry.set_margin_start(12)
        quality_box.append(self._cache_entry)
        
        tab.append(quality_box)
        
        # Add tab to notebook
        label = Gtk.Label(label="Export Settings")
        self._notebook.append_page(tab, label)

    def _load_settings(self) -> None:
        """Load current settings into the UI."""
        config = config_manager.get_config()
        
        # General tab
        self._debug_checkbox.set_active(config.debug_mode)
        self._width_entry.set_text(str(config.window_width))
        self._height_entry.set_text(str(config.window_height))
        
        # API tab
        self._api_key_entry.set_text("")  # Don't show actual API key
        
        # Set active model
        for i in range(3):  # We have 3 models
            if self._model_combo.get_item_text(i) == config.model_name:
                self._model_combo.set_active(i)
                break
        
        self._temp_scale.set_value(config.temperature)
        
        # Overlay tab
        self._ratio_scale.set_value(config.selection_ratio)
        self._zoom_scale.set_value(config.zoom_factor)
        
        # Set overlay color
        rgba = Gdk.RGBA()
        rgba.parse(config.overlay_color)
        self._color_button.set_rgba(rgba)
        
        self._opacity_scale.set_value(config.overlay_opacity)
        
        # Export tab
        self._png_scale.set_value(config.png_compression)
        self._high_quality_checkbox.set_active(config.high_resampling == 1)
        self._cache_entry.set_text(str(config.max_cache_size_mb))
        
        # Store original settings for cancel
        self._current_settings = {
            "debug_mode": config.debug_mode,
            "window_width": config.window_width,
            "window_height": config.window_height,
            "model_name": config.model_name,
            "temperature": config.temperature,
            "selection_ratio": config.selection_ratio,
            "zoom_factor": config.zoom_factor,
            "overlay_color": config.overlay_color,
            "overlay_opacity": config.overlay_opacity,
            "png_compression": config.png_compression,
            "high_resampling": config.high_resampling,
            "max_cache_size_mb": config.max_cache_size_mb
        }

    def _apply_settings(self) -> None:
        """Apply the current settings in the UI to the configuration."""
        try:
            # Collect settings from UI
            updates = {
                "debug_mode": self._debug_checkbox.get_active(),
                "window_width": int(self._width_entry.get_text()),
                "window_height": int(self._height_entry.get_text()),
                "model_name": self._model_combo.get_active_text(),
                "temperature": self._temp_scale.get_value(),
                "selection_ratio": self._ratio_scale.get_value(),
                "zoom_factor": self._zoom_scale.get_value(),
                "overlay_opacity": self._opacity_scale.get_value(),
                "png_compression": int(self._png_scale.get_value()),
                "high_resampling": 1 if self._high_quality_checkbox.get_active() else 0,
                "max_cache_size_mb": int(self._cache_entry.get_text())
            }
            
            # Get overlay color
            rgba = self._color_button.get_rgba()
            updates["overlay_color"] = rgba.to_string()
            
            # Update API key if provided (non-empty)
            api_key = self._api_key_entry.get_text()
            if api_key:
                updates["gemini_api_key"] = api_key
            
            # Apply updates
            config_manager.update_config(updates)
            logger.debug("Applied settings updates")
        except (ValueError, TypeError) as e:
            logger.error(f"Error applying settings: {e}")
            # Show error dialog
            self._show_error_dialog(f"Error applying settings: {e}")

    def _on_response(self, dialog: Gtk.Dialog, response_id: int) -> None:
        """Handle dialog response.
        
        Args:
            dialog: The dialog
            response_id: The response ID
        """
        if response_id == Gtk.ResponseType.APPLY:
            # Apply changes but don't close
            self._apply_settings()
        elif response_id == Gtk.ResponseType.OK:
            # Apply changes and close
            self._apply_settings()
            self.destroy()
        elif response_id == Gtk.ResponseType.CANCEL:
            # Discard changes and close
            self.destroy()

    def _show_error_dialog(self, message: str) -> None:
        """Show an error dialog.
        
        Args:
            message: The error message
        """
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Error"
        )
        dialog.format_secondary_text(message)
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.show()