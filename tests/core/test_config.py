"""Unit tests for the configuration management module."""

import os
from pathlib import Path
import tempfile
import toml
import pytest
from preview_maker.core.config import ConfigManager, PreviewMakerConfig


@pytest.fixture
def config_manager():
    """Fixture providing a fresh ConfigManager instance."""
    # Reset singleton state using a public method
    ConfigManager._reset_for_testing()
    return ConfigManager()


@pytest.fixture
def temp_config_file():
    """Fixture providing a temporary configuration file."""
    config_data = {
        "gemini_api_key": "test_key",
        "window_width": 800,
        "window_height": 600,
        "overlay_color": "#00FF00",
        "overlay_opacity": 0.5,
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        toml.dump(config_data, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


def test_singleton_pattern(config_manager):
    """Test that ConfigManager follows the singleton pattern."""
    another_manager = ConfigManager()
    assert config_manager is another_manager


def test_default_config(config_manager):
    """Test default configuration values."""
    config = config_manager.get_config()
    assert isinstance(config, PreviewMakerConfig)
    assert config.window_width == 1024
    assert config.window_height == 768
    assert config.overlay_color == "#FF0000"
    assert config.overlay_opacity == 0.7


def test_load_from_file(config_manager, temp_config_file):
    """Test loading configuration from a TOML file."""
    config_manager.load_config(temp_config_file)
    config = config_manager.get_config()

    assert config.gemini_api_key == "test_key"
    assert config.window_width == 800
    assert config.window_height == 600
    assert config.overlay_color == "#00FF00"
    assert config.overlay_opacity == 0.5


def test_load_from_env(config_manager):
    """Test loading configuration from environment variables."""
    os.environ["PREVIEW_MAKER_GEMINI_API_KEY"] = "env_test_key"
    os.environ["PREVIEW_MAKER_WINDOW_WIDTH"] = "1200"

    config_manager.load_config()
    config = config_manager.get_config()

    assert config.gemini_api_key == "env_test_key"
    assert config.window_width == 1200

    # Cleanup
    del os.environ["PREVIEW_MAKER_GEMINI_API_KEY"]
    del os.environ["PREVIEW_MAKER_WINDOW_WIDTH"]


def test_update_config(config_manager):
    """Test updating configuration values."""
    updates = {"window_width": 1500, "overlay_color": "#0000FF"}

    config_manager.update_config(updates)
    config = config_manager.get_config()

    assert config.window_width == 1500
    assert config.overlay_color == "#0000FF"


def test_cache_directory_creation(config_manager):
    """Test that cache directory is created when loading config."""
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ["PREVIEW_MAKER_PREVIEWS_DIR"] = temp_dir

        config_manager.load_config()
        config = config_manager.get_config()

        assert Path(temp_dir).exists()
        assert config.previews_dir == Path(temp_dir)

        del os.environ["PREVIEW_MAKER_PREVIEWS_DIR"]
