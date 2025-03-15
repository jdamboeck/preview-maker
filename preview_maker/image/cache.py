"""Image caching functionality for Preview Maker.

This module handles caching of processed images to improve performance.
"""

from pathlib import Path
import threading
from typing import Dict, Optional, Set
import time
import os
import shutil

from PIL import Image

from preview_maker.core.config import config_manager
from preview_maker.core.logging import logger


class CacheManager:
    """Manages image caching operations."""

    def __init__(self) -> None:
        """Initialize the cache manager."""
        self._config = config_manager.get_config()
        self._cache_lock = threading.Lock()
        self._cache_dir = Path(str(self._config.cache_dir)) / "images"
        self._cache_size = 0
        self._cached_files: Set[Path] = set()
        self._last_accessed: Dict[Path, float] = {}

        # Create cache directory if it doesn't exist
        self._cache_dir.mkdir(parents=True, exist_ok=True)

        # Load existing cache info
        self._load_cache_info()

    def _load_cache_info(self) -> None:
        """Load information about existing cached files."""
        try:
            with self._cache_lock:
                # Get all files in cache directory
                for file_path in self._cache_dir.glob("*.png"):
                    if file_path.is_file():
                        self._cached_files.add(file_path)
                        self._last_accessed[file_path] = file_path.stat().st_mtime
                        self._cache_size += file_path.stat().st_size

                # Clean up cache if it exceeds the size limit
                self._cleanup_cache()

        except Exception as e:
            logger.error("Failed to load cache info", error=e)

    def _cleanup_cache(self) -> None:
        """Remove old cache files when cache size exceeds limit."""
        try:
            max_size = (
                self._config.max_cache_size_mb * 1024 * 1024
            )  # Convert MB to bytes
            while self._cache_size > max_size:
                # Find oldest accessed file
                oldest_file = min(self._last_accessed.items(), key=lambda x: x[1])[0]

                # Remove file from cache
                self._remove_from_cache(oldest_file)

        except Exception as e:
            logger.error("Failed to cleanup cache", error=e)

    def _remove_from_cache(self, file_path: Path) -> None:
        """Remove a file from the cache.

        Args:
            file_path: Path to the file to remove
        """
        try:
            with self._cache_lock:
                if file_path in self._cached_files:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    self._cached_files.remove(file_path)
                    del self._last_accessed[file_path]
                    self._cache_size -= file_size

        except Exception as e:
            logger.error(f"Failed to remove file from cache: {file_path}", error=e)

    def get_cached_image(
        self, image_path: str | Path, cache_key: str
    ) -> Optional[Image.Image]:
        """Get an image from the cache.

        Args:
            image_path: Original image path
            cache_key: Cache key for the processed version

        Returns:
            The cached image if found, None otherwise
        """
        try:
            cache_file = self._get_cache_file_path(image_path, cache_key)

            with self._cache_lock:
                if cache_file in self._cached_files:
                    # Update last accessed time
                    current_time = time.time()
                    os.utime(cache_file, (current_time, current_time))
                    self._last_accessed[cache_file] = current_time

                    # Load and return the cached image
                    return Image.open(cache_file)

            return None

        except Exception as e:
            logger.error("Failed to get cached image", error=e)
            return None

    def cache_image(
        self, image: Image.Image, image_path: str | Path, cache_key: str
    ) -> None:
        """Cache a processed image.

        Args:
            image: The image to cache
            image_path: Original image path
            cache_key: Cache key for the processed version
        """
        try:
            cache_file = self._get_cache_file_path(image_path, cache_key)

            with self._cache_lock:
                # Save image to cache
                image.save(cache_file, "PNG")

                # Update cache info
                self._cached_files.add(cache_file)
                current_time = time.time()
                self._last_accessed[cache_file] = current_time
                self._cache_size += cache_file.stat().st_size

                # Clean up if needed
                self._cleanup_cache()

        except Exception as e:
            logger.error("Failed to cache image", error=e)

    def clear_cache(self) -> None:
        """Clear all cached images."""
        try:
            with self._cache_lock:
                # Remove all files
                shutil.rmtree(self._cache_dir)
                self._cache_dir.mkdir(parents=True)

                # Reset cache info
                self._cached_files.clear()
                self._last_accessed.clear()
                self._cache_size = 0

            logger.info("Cache cleared successfully")

        except Exception as e:
            logger.error("Failed to clear cache", error=e)

    def _get_cache_file_path(self, image_path: str | Path, cache_key: str) -> Path:
        """Get the cache file path for an image.

        Args:
            image_path: Original image path
            cache_key: Cache key for the processed version

        Returns:
            Path to the cache file
        """
        # Create a unique filename based on the original path and cache key
        image_path = Path(image_path)
        filename = f"{image_path.stem}_{cache_key}.png"
        return self._cache_dir / filename

    @property
    def cache_size(self) -> int:
        """Get the current cache size in bytes."""
        return self._cache_size

    @property
    def cached_files(self) -> Set[Path]:
        """Get the set of cached file paths."""
        return self._cached_files.copy()
