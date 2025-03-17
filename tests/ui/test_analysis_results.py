"""Tests for the AnalysisResultsDisplay component.

This module contains tests for the AnalysisResultsDisplay class, which provides
a user interface for displaying image analysis results from Gemini AI.
"""

import os
import sys
from unittest import mock

import pytest

# Ensure we're always in headless mode for tests to avoid GTK initialization issues
HEADLESS = True

# Configure mocks before imports if in headless mode
if HEADLESS:
    # Create system-wide mocks before any imports
    sys.modules["gi"] = mock.MagicMock()
    sys.modules["gi"].require_version = mock.MagicMock()
    sys.modules["gi.repository"] = mock.MagicMock()
    sys.modules["gi.repository.Gtk"] = mock.MagicMock()
    sys.modules["gi.repository.Gdk"] = mock.MagicMock()
    sys.modules["gi.repository.GLib"] = mock.MagicMock()

    # Import mocks for testing
    from tests.ui.mocks import MockAnalysisResultsDisplay, process_events
else:
    # In non-headless mode, we import gi directly
    import gi

    gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk, GLib

    def process_events():
        """Process pending GTK events."""
        while GLib.MainContext.default().iteration(False):
            pass

# Import the component under test (after mock setup)
if not HEADLESS:
    from preview_maker.ui.analysis_results import AnalysisResultsDisplay


class TestAnalysisResultsDisplay:
    """Test cases for the AnalysisResultsDisplay component."""

    @pytest.fixture
    def mock_parent(self):
        """Create a mock parent window."""
        return mock.MagicMock()
    
    @pytest.fixture
    def mock_analysis_result(self):
        """Create a mock analysis result."""
        return {
            "description": "This is a sample textile with intricate patterns.",
            "key_points": [
                "Detailed geometric patterns cover the surface",
                "Color palette includes red, blue, and gold",
                "Likely handcrafted using traditional techniques"
            ],
            "technical_details": [
                "Made with silk and cotton blend",
                "Approximately from 19th century",
                "Uses double-weave technique"
            ],
            "metadata": {
                "origin": "Central Asia",
                "condition": "Good",
                "dimensions": "24 x 36 inches"
            }
        }

    @pytest.fixture
    def analysis_display(self, mock_parent):
        """Create an AnalysisResultsDisplay instance for testing."""
        if HEADLESS:
            # Create a mock display in headless mode
            from tests.ui.mocks import MockAnalysisResultsDisplay
            return MockAnalysisResultsDisplay(mock_parent)
        else:
            # Create a real display in non-headless mode
            return AnalysisResultsDisplay(mock_parent)

    def test_display_creation(self, analysis_display):
        """Test that the display is created correctly."""
        assert analysis_display is not None
        
    def test_empty_state(self, analysis_display):
        """Test the initial empty state of the display."""
        assert analysis_display.get_result() is None
        assert analysis_display.has_result() is False
        
    def test_display_result(self, analysis_display, mock_analysis_result):
        """Test displaying an analysis result."""
        analysis_display.display_result(mock_analysis_result)
        
        assert analysis_display.has_result() is True
        assert analysis_display.get_result() == mock_analysis_result
        
    def test_clear_result(self, analysis_display, mock_analysis_result):
        """Test clearing an analysis result."""
        analysis_display.display_result(mock_analysis_result)
        assert analysis_display.has_result() is True
        
        analysis_display.clear()
        assert analysis_display.has_result() is False
        assert analysis_display.get_result() is None
        
    def test_copy_to_clipboard(self, analysis_display, mock_analysis_result):
        """Test copying the result to clipboard."""
        analysis_display.display_result(mock_analysis_result)
        
        # Mock the clipboard
        clipboard_mock = mock.MagicMock()
        analysis_display._get_clipboard = mock.MagicMock(return_value=clipboard_mock)
        
        # Call copy method
        analysis_display.copy_to_clipboard()
        
        # Verify clipboard was called with the formatted text
        clipboard_mock.set_text.assert_called_once()
        
    def test_save_to_file(self, analysis_display, mock_analysis_result, tmp_path):
        """Test saving the result to a file."""
        analysis_display.display_result(mock_analysis_result)
        
        # Create temp file path
        test_file = tmp_path / "analysis_results.txt"
        
        # Mock file dialog to return our test file
        analysis_display._show_save_dialog = mock.MagicMock(return_value=str(test_file))
        
        # Call save method
        analysis_display.save_to_file()
        
        # Verify file exists and contains the result text
        assert test_file.exists()
        content = test_file.read_text()
        assert "sample textile" in content
        assert "geometric patterns" in content
        
    def test_expandable_sections(self, analysis_display, mock_analysis_result):
        """Test expanding and collapsing sections."""
        analysis_display.display_result(mock_analysis_result)
        
        # Check initial state (usually expanded)
        assert analysis_display.is_section_expanded("key_points") is True
        
        # Collapse a section
        analysis_display.set_section_expanded("key_points", False)
        assert analysis_display.is_section_expanded("key_points") is False
        
        # Expand it again
        analysis_display.set_section_expanded("key_points", True)
        assert analysis_display.is_section_expanded("key_points") is True
        
    def test_error_display(self, analysis_display):
        """Test displaying an error message."""
        error_message = "Failed to analyze image: API error"
        
        analysis_display.display_error(error_message)
        
        assert analysis_display.has_result() is False
        assert analysis_display.has_error() is True
        assert analysis_display.get_error() == error_message