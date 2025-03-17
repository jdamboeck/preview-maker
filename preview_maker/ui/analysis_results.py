"""Analysis results display for Preview Maker.

This module provides a component for displaying image analysis results
from the Gemini AI in a structured, readable format with expandable sections.
"""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GLib, Pango

import logging
import os
import json
from typing import Dict, Any, Optional, List, Tuple, Union, Callable

from preview_maker.core.logging import logger


class AnalysisResultsDisplay(Gtk.Box):
    """Widget for displaying structured AI analysis results.

    This component displays Gemini AI analysis results in a structured format
    with expandable/collapsible sections, copy-to-clipboard functionality, and
    save-to-file functionality.

    Attributes:
        _result: The current analysis result
        _error: The current error message, if any
        _scroll_window: ScrolledWindow containing the text view
        _text_view: TextView for displaying formatted text
        _text_buffer: TextBuffer for managing the text content
        _sections: Dictionary of section widgets
        _tag_table: Dictionary of text tags for formatting
    """

    def __init__(self, parent_window: Gtk.Window) -> None:
        """Initialize the analysis results display.

        Args:
            parent_window: The parent window
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)

        self.parent_window = parent_window

        # Result storage
        self._result = None
        self._error = None

        # Setup UI elements
        self._setup_ui()

        # CSS styling
        self._setup_css()

    def _setup_ui(self) -> None:
        """Set up the UI components."""
        # Main container with vertical orientation
        self._main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self._main_container.set_margin_top(12)
        self._main_container.set_margin_bottom(12)
        self._main_container.set_margin_start(12)
        self._main_container.set_margin_end(12)

        # Scrolled window for text
        self._scroll_window = Gtk.ScrolledWindow()
        self._scroll_window.set_vexpand(True)
        self._scroll_window.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )

        # Text view for displaying results
        self._text_view = Gtk.TextView()
        self._text_view.set_editable(False)
        self._text_view.set_cursor_visible(False)
        self._text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self._text_view.set_margin_top(6)
        self._text_view.set_margin_bottom(6)
        self._text_view.set_margin_start(6)
        self._text_view.set_margin_end(6)

        # Get the text buffer
        self._text_buffer = self._text_view.get_buffer()
        self._setup_text_tags()

        # Add text view to scrolled window
        self._scroll_window.set_child(self._text_view)

        # Buttons box
        self._buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self._buttons_box.set_halign(Gtk.Align.END)

        # Action buttons
        self._copy_button = Gtk.Button(label="Copy to Clipboard")
        self._copy_button.connect("clicked", self._on_copy_clicked)

        self._save_button = Gtk.Button(label="Save to File")
        self._save_button.connect("clicked", self._on_save_clicked)

        self._expand_all_button = Gtk.Button(label="Expand All")
        self._expand_all_button.connect("clicked", self._on_expand_all_clicked)

        self._collapse_all_button = Gtk.Button(label="Collapse All")
        self._collapse_all_button.connect("clicked", self._on_collapse_all_clicked)

        # Add buttons to box
        self._buttons_box.append(self._copy_button)
        self._buttons_box.append(self._save_button)
        self._buttons_box.append(self._expand_all_button)
        self._buttons_box.append(self._collapse_all_button)

        # Create expandable sections
        self._create_expandable_sections()

        # Add components to the layout
        self._main_container.append(self._scroll_window)
        self._main_container.append(self._buttons_box)

        # Add main container to self
        self.append(self._main_container)

        # Initially hide buttons
        self._update_button_visibility(False)

    def _setup_css(self) -> None:
        """Set up CSS styling for the component."""
        css_provider = Gtk.CssProvider()
        css = b"""
        .section-header {
            background-color: #f0f0f0;
            border-radius: 4px;
            padding: 4px;
        }

        .section-expander {
            font-weight: bold;
        }

        .content-visible {
            transition: all 0.3s ease-in-out;
            opacity: 1;
        }

        .content-hidden {
            transition: all 0.3s ease-in-out;
            opacity: 0;
            max-height: 0;
            overflow: hidden;
        }

        .error-text {
            color: #cc0000;
            font-weight: bold;
        }
        """
        css_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def _setup_text_tags(self) -> None:
        """Set up text tags for rich text formatting."""
        # Create text tags for formatting
        self._tag_table = {}

        # Title tag
        tag = self._text_buffer.create_tag("title")
        tag.set_property("weight", 800)  # Bold
        tag.set_property("size-points", 16)
        tag.set_property("pixels-above-lines", 6)
        tag.set_property("pixels-below-lines", 12)
        self._tag_table["title"] = tag

        # Heading tag
        tag = self._text_buffer.create_tag("heading")
        tag.set_property("weight", 700)  # Bold
        tag.set_property("size-points", 14)
        tag.set_property("pixels-above-lines", 12)
        tag.set_property("pixels-below-lines", 6)
        self._tag_table["heading"] = tag

        # Subheading tag
        tag = self._text_buffer.create_tag("subheading")
        tag.set_property("weight", 600)  # Semi-bold
        tag.set_property("size-points", 12)
        tag.set_property("pixels-above-lines", 6)
        tag.set_property("pixels-below-lines", 3)
        self._tag_table["subheading"] = tag

        # Bold tag
        tag = self._text_buffer.create_tag("bold")
        tag.set_property("weight", 700)  # Bold
        self._tag_table["bold"] = tag

        # Italic tag
        tag = self._text_buffer.create_tag("italic")
        tag.set_property("style", Pango.Style.ITALIC)
        self._tag_table["italic"] = tag

        # List item tag
        tag = self._text_buffer.create_tag("list_item")
        tag.set_property("left-margin", 20)
        tag.set_property("pixels-above-lines", 3)
        tag.set_property("pixels-below-lines", 3)
        self._tag_table["list_item"] = tag

        # Key tag (for key-value pairs)
        tag = self._text_buffer.create_tag("key")
        tag.set_property("weight", 700)  # Bold
        self._tag_table["key"] = tag

        # Error tag
        tag = self._text_buffer.create_tag("error")
        tag.set_property("foreground", "#cc0000")
        tag.set_property("weight", 700)  # Bold
        self._tag_table["error"] = tag

    def _create_expandable_sections(self) -> None:
        """Create expandable sections for different result categories."""
        # Initialize sections dictionary
        self._sections = {}

        # Create sections for each category
        section_configs = [
            {"name": "description", "label": "Description"},
            {"name": "key_points", "label": "Key Points"},
            {"name": "technical_details", "label": "Technical Details"},
            {"name": "metadata", "label": "Metadata"},
        ]

        for config in section_configs:
            name = config["name"]
            label = config["label"]

            # Create expander button
            expander = Gtk.Button(label=label)
            expander.add_css_class("section-expander")
            expander.connect("clicked", self._on_section_toggle, name)

            # Create content container
            content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            content.add_css_class("content-visible")  # Initially visible

            # Store in sections dictionary
            self._sections[name] = {
                "expander": expander,
                "content": content,
                "expanded": True,
            }

    def _update_button_visibility(self, has_content: bool) -> None:
        """Update the visibility of action buttons based on content availability.

        Args:
            has_content: Whether there is content to act on
        """
        self._copy_button.set_sensitive(has_content)
        self._save_button.set_sensitive(has_content)
        self._expand_all_button.set_sensitive(has_content)
        self._collapse_all_button.set_sensitive(has_content)

    def display_result(self, result: Dict[str, Any]) -> None:
        """Display an analysis result.

        Args:
            result: The analysis result dictionary
        """
        logger.debug(f"Displaying analysis result: {result}")
        self._result = result
        self._error = None

        # Clear existing content
        self._text_buffer.set_text("")

        # Insert title
        self._insert_with_tag("Analysis Results\n", "title")

        # Format and display each section
        if result and "description" in result and result["description"]:
            self._insert_with_tag("Description\n", "heading")
            self._insert_text(result["description"] + "\n\n")

        if result and "key_points" in result and result["key_points"]:
            self._insert_with_tag("Key Points\n", "heading")
            for point in result["key_points"]:
                self._insert_text("• ")
                self._insert_text(point + "\n")
            self._insert_text("\n")

        if result and "technical_details" in result and result["technical_details"]:
            self._insert_with_tag("Technical Details\n", "heading")
            for detail in result["technical_details"]:
                self._insert_text("• ")
                self._insert_text(detail + "\n")
            self._insert_text("\n")

        if result and "metadata" in result and result["metadata"]:
            self._insert_with_tag("Metadata\n", "heading")
            for key, value in result["metadata"].items():
                self._insert_with_tag(f"{key}: ", "key")
                self._insert_text(f"{value}\n")
            self._insert_text("\n")

        # Show buttons
        self._update_button_visibility(True)

    def _insert_with_tag(self, text: str, tag_name: str) -> None:
        """Insert text with a specific tag.

        Args:
            text: The text to insert
            tag_name: The name of the tag to apply
        """
        end_iter = self._text_buffer.get_end_iter()
        self._text_buffer.insert_with_tags(end_iter, text, self._tag_table[tag_name])

    def _insert_text(self, text: str) -> None:
        """Insert plain text.

        Args:
            text: The text to insert
        """
        end_iter = self._text_buffer.get_end_iter()
        self._text_buffer.insert(end_iter, text)

    def clear(self) -> None:
        """Clear the display."""
        self._result = None
        self._error = None
        self._text_buffer.set_text("")
        self._update_button_visibility(False)

    def has_result(self) -> bool:
        """Check if there is a result to display.

        Returns:
            bool: True if there is a result, False otherwise
        """
        return self._result is not None

    def get_result(self) -> Optional[Dict[str, Any]]:
        """Get the current result.

        Returns:
            dict: The current result or None
        """
        return self._result

    def display_error(self, error_message: str) -> None:
        """Display an error message.

        Args:
            error_message: The error message to display
        """
        logger.error(f"Analysis error: {error_message}")
        self._error = error_message
        self._result = None

        # Clear existing content
        self._text_buffer.set_text("")

        # Insert error message
        self._insert_with_tag("Error\n", "heading")
        self._insert_with_tag(error_message + "\n", "error")

        # Hide buttons
        self._update_button_visibility(False)

    def has_error(self) -> bool:
        """Check if there is an error message.

        Returns:
            bool: True if there is an error, False otherwise
        """
        return self._error is not None

    def get_error(self) -> Optional[str]:
        """Get the current error message.

        Returns:
            str: The current error message or None
        """
        return self._error

    def copy_to_clipboard(self) -> None:
        """Copy the result to the clipboard."""
        if not self._result:
            return

        # Get formatted text
        formatted_text = self._format_result_for_clipboard()

        # Get clipboard
        clipboard = self._get_clipboard()

        # Set the text
        clipboard.set_text(formatted_text, -1)

        logger.debug("Copied analysis results to clipboard")

    def _format_result_for_clipboard(self) -> str:
        """Format the result for clipboard copying.

        Returns:
            str: Formatted text for the clipboard
        """
        result = self._result
        if not result:
            return ""

        lines = ["ANALYSIS RESULTS"]

        if "description" in result and result["description"]:
            lines.append("\nDESCRIPTION")
            lines.append(result["description"])

        if "key_points" in result and result["key_points"]:
            lines.append("\nKEY POINTS")
            for point in result["key_points"]:
                lines.append(f"• {point}")

        if "technical_details" in result and result["technical_details"]:
            lines.append("\nTECHNICAL DETAILS")
            for detail in result["technical_details"]:
                lines.append(f"• {detail}")

        if "metadata" in result and result["metadata"]:
            lines.append("\nMETADATA")
            for key, value in result["metadata"].items():
                lines.append(f"{key}: {value}")

        return "\n".join(lines)

    def save_to_file(self, filepath: Optional[str] = None) -> bool:
        """Save the result to a file.

        Args:
            filepath: Optional filepath to save to. If None, a dialog will be shown.

        Returns:
            bool: True if saved successfully, False otherwise
        """
        if not self._result:
            return False

        if not filepath:
            filepath = self._show_save_dialog()

        if not filepath:
            return False

        try:
            # Get formatted text
            formatted_text = self._format_result_for_clipboard()

            # Write to file
            with open(filepath, "w") as f:
                f.write(formatted_text)

            logger.info(f"Saved analysis results to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error saving analysis results: {e}")
            self._show_error_dialog(f"Could not save file: {e}")
            return False

    def _show_save_dialog(self) -> Optional[str]:
        """Show a file save dialog.

        Returns:
            str: The selected filepath or None
        """
        dialog = Gtk.FileChooserDialog(
            title="Save Analysis Results",
            parent=self.parent_window,
            action=Gtk.FileChooserAction.SAVE,
        )

        dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("_Save", Gtk.ResponseType.ACCEPT)

        dialog.set_current_name("analysis_results.txt")
        dialog.set_modal(True)

        # Add file filters
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_mime_type("text/plain")
        dialog.add_filter(filter_text)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("All files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

        # Show the dialog
        response = dialog.run()

        if response == Gtk.ResponseType.ACCEPT:
            filepath = dialog.get_file().get_path()
            dialog.destroy()
            return filepath

        dialog.destroy()
        return None

    def _get_clipboard(self) -> Gdk.Clipboard:
        """Get the system clipboard.

        Returns:
            Gdk.Clipboard: The system clipboard
        """
        return Gdk.Display.get_default().get_clipboard()

    def _show_error_dialog(self, message: str) -> None:
        """Show an error dialog.

        Args:
            message: The error message to display
        """
        dialog = Gtk.MessageDialog(
            transient_for=self.parent_window,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Error",
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def is_section_expanded(self, section_name: str) -> bool:
        """Check if a section is expanded.

        Args:
            section_name: The name of the section

        Returns:
            bool: True if expanded, False otherwise
        """
        if section_name not in self._sections:
            return False

        return self._sections[section_name]["expanded"]

    def set_section_expanded(self, section_name: str, expanded: bool) -> None:
        """Set whether a section is expanded.

        Args:
            section_name: The name of the section
            expanded: True to expand, False to collapse
        """
        if section_name not in self._sections:
            return

        self._sections[section_name]["expanded"] = expanded

        # Update CSS classes
        section = self._sections[section_name]
        content = section["content"]

        if expanded:
            content.remove_css_class("content-hidden")
            content.add_css_class("content-visible")
        else:
            content.remove_css_class("content-visible")
            content.add_css_class("content-hidden")

    def _on_section_toggle(self, button: Gtk.Button, section_name: str) -> None:
        """Handle section expander button click.

        Args:
            button: The clicked button
            section_name: The name of the section to toggle
        """
        currently_expanded = self.is_section_expanded(section_name)
        self.set_section_expanded(section_name, not currently_expanded)

    def _on_copy_clicked(self, button: Gtk.Button) -> None:
        """Handle copy button click.

        Args:
            button: The clicked button
        """
        self.copy_to_clipboard()

    def _on_save_clicked(self, button: Gtk.Button) -> None:
        """Handle save button click.

        Args:
            button: The clicked button
        """
        self.save_to_file()

    def _on_expand_all_clicked(self, button: Gtk.Button) -> None:
        """Handle expand all button click.

        Args:
            button: The clicked button
        """
        for section_name in self._sections.keys():
            self.set_section_expanded(section_name, True)

    def _on_collapse_all_clicked(self, button: Gtk.Button) -> None:
        """Handle collapse all button click.

        Args:
            button: The clicked button
        """
        for section_name in self._sections.keys():
            self.set_section_expanded(section_name, False)
