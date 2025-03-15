"""Tests for the image cache manager."""

import time
from pathlib import Path
import pytest
from PIL import Image

from preview_maker.core.config import config_manager
from preview_maker.image.cache import CacheManager


@pytest.fixture
def temp_cache_dir(tmp_path):
    """Create a temporary cache directory."""
    cache_dir = tmp_path / "cache"
    config = config_manager.get_config()
    config.cache_dir = cache_dir
    config.max_cache_size_mb = 1  # 1MB for testing
    return cache_dir


@pytest.fixture
def cache_manager(temp_cache_dir):
    """Create a cache manager instance."""
    return CacheManager()


@pytest.fixture
def test_image():
    """Create a test image."""
    image = Image.new("RGB", (100, 100), "red")
    return image


def test_cache_initialization(temp_cache_dir, cache_manager):
    """Test cache manager initialization."""
    assert cache_manager._cache_dir == temp_cache_dir / "images"
    assert cache_manager._cache_dir.exists()
    assert cache_manager.cache_size == 0
    assert len(cache_manager.cached_files) == 0


def test_cache_image(cache_manager, test_image):
    """Test caching an image."""
    cache_manager.cache_image(test_image, "test.png", "test_key")

    # Check that the image was cached
    cache_file = cache_manager._get_cache_file_path("test.png", "test_key")
    assert cache_file.exists()
    assert cache_file in cache_manager.cached_files
    assert cache_manager.cache_size > 0


def test_get_cached_image(cache_manager, test_image):
    """Test retrieving a cached image."""
    # Cache the image
    cache_manager.cache_image(test_image, "test.png", "test_key")

    # Get the cached image
    cached_image = cache_manager.get_cached_image("test.png", "test_key")
    assert cached_image is not None
    assert cached_image.size == test_image.size
    assert cached_image.mode == test_image.mode


def test_cache_cleanup(cache_manager, test_image):
    """Test cache cleanup when size limit is exceeded."""
    # Create multiple images to exceed cache size
    for i in range(20):
        cache_manager.cache_image(test_image, f"test_{i}.png", f"key_{i}")
        time.sleep(0.1)  # Ensure different access times

    # Check that cache size is within limit
    max_size = config_manager.get_config().max_cache_size_mb * 1024 * 1024
    assert cache_manager.cache_size <= max_size


def test_clear_cache(cache_manager, test_image):
    """Test clearing the cache."""
    # Cache some images
    for i in range(3):
        cache_manager.cache_image(test_image, f"test_{i}.png", f"key_{i}")

    # Clear the cache
    cache_manager.clear_cache()

    # Check that cache is empty
    assert cache_manager.cache_size == 0
    assert len(cache_manager.cached_files) == 0
    assert cache_manager._cache_dir.exists()


def test_cache_persistence(temp_cache_dir, test_image):
    """Test that cache persists between manager instances."""
    # Create first manager and cache an image
    manager1 = CacheManager()
    manager1.cache_image(test_image, "test.png", "test_key")

    # Create second manager and check if image is still cached
    manager2 = CacheManager()
    cached_image = manager2.get_cached_image("test.png", "test_key")
    assert cached_image is not None


def test_invalid_cache_operations(cache_manager):
    """Test handling of invalid cache operations."""
    # Try to get non-existent image
    result = cache_manager.get_cached_image("nonexistent.png", "invalid_key")
    assert result is None

    # Try to remove non-existent file
    cache_manager._remove_from_cache(Path("nonexistent.png"))
    assert True  # Should not raise exception
