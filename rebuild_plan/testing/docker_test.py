#!/usr/bin/env python3
"""
Docker Test for Preview Maker

This simple test verifies that the Docker testing environment is working properly.
"""
import os
import sys
import pytest


def test_environment_variables():
    """Test that the environment variables are set properly."""
    assert os.environ.get("PREVIEW_MAKER_ENV") == "test"
    # Check that PYTHONPATH contains '/app' rather than exact equality
    assert "/app" in os.environ.get("PYTHONPATH", "")


def test_python_version():
    """Test that the Python version is 3.10 or higher."""
    assert sys.version_info.major == 3
    assert sys.version_info.minor >= 10


def test_imports():
    """Test that required packages can be imported."""
    import gi
    import cairo
    from PIL import Image

    # Only test these imports, don't try to configure them
    # to avoid errors in headless environment
    assert gi is not None
    assert cairo is not None
    assert Image is not None


def test_file_access():
    """Test that we can access the filesystem."""
    assert os.path.exists("/app")

    # Verify we can write to /tmp
    test_file = "/tmp/test_file.txt"
    with open(test_file, "w") as f:
        f.write("test")
    assert os.path.exists(test_file)
    os.remove(test_file)
    assert not os.path.exists(test_file)


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
