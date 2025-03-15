"""Configuration management for Preview Maker.

This module handles loading and managing configuration from both TOML files
and environment variables, with support for runtime updates and validation.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import os
import toml
from pydantic import BaseModel, Field


class PreviewMakerConfig(BaseModel):
    """Configuration schema for Preview Maker."""

    # AI Configuration
    gemini_api_key: str = Field(
        default="", description="Google Gemini API key for image analysis"
    )

    # Image Processing Configuration
    cache_dir: Path = Field(
        default=Path("~/.cache/preview-maker"),
        description="Directory for caching processed images",
    )
    max_cache_size_mb: int = Field(
        default=500, description="Maximum cache size in megabytes"
    )

    # UI Configuration
    window_width: int = Field(default=1024, description="Default window width")
    window_height: int = Field(default=768, description="Default window height")
    overlay_color: str = Field(
        default="#FF0000", description="Color for highlight overlays"
    )
    overlay_opacity: float = Field(
        default=0.7, description="Opacity for highlight overlays (0-1)"
    )


class ConfigManager:
    """Manages application configuration from files and environment variables."""

    # Class-level variables for singleton pattern
    __instance = None
    __initialized = False
    __config = None
    __config_file = None

    def __new__(cls) -> "ConfigManager":
        """Ensure singleton pattern for configuration manager."""
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self) -> None:
        """Initialize the configuration manager."""
        if not self.__initialized:
            self.__config = PreviewMakerConfig()
            self.__config_file = None
            self.__initialized = True

    def _convert_env_value(self, value: str, target_type: type) -> Any:
        """Convert environment variable value to the correct type.

        Args:
            value: The string value from the environment
            target_type: The target type to convert to

        Returns:
            The converted value
        """
        if target_type == bool:
            return value.lower() in ("true", "1", "yes", "on")
        if target_type == Path:
            return Path(value)
        if target_type == float:
            return float(value)
        if target_type == int:
            return int(value)
        return value

    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        env_mapping = {
            "PREVIEW_MAKER_GEMINI_API_KEY": "gemini_api_key",
            "PREVIEW_MAKER_CACHE_DIR": "cache_dir",
            "PREVIEW_MAKER_MAX_CACHE_SIZE": "max_cache_size_mb",
            "PREVIEW_MAKER_WINDOW_WIDTH": "window_width",
            "PREVIEW_MAKER_WINDOW_HEIGHT": "window_height",
            "PREVIEW_MAKER_OVERLAY_COLOR": "overlay_color",
            "PREVIEW_MAKER_OVERLAY_OPACITY": "overlay_opacity",
        }

        for env_var, config_key in env_mapping.items():
            if env_value := os.getenv(env_var):
                field_type = type(getattr(self.__config, config_key))
                converted_value = self._convert_env_value(env_value, field_type)
                setattr(self.__config, config_key, converted_value)

    def load_config(self, config_file: Optional[str] = None) -> None:
        """Load configuration from file and environment variables.

        Args:
            config_file: Optional path to TOML configuration file
        """
        # Load from file if specified
        if config_file:
            config_path = Path(config_file).expanduser().resolve()
            if config_path.exists():
                self.__config_file = config_path
                config_data = toml.load(config_path)
                self.__config = PreviewMakerConfig(**config_data)

        # Override with environment variables
        self._load_from_env()

        # Ensure cache directory exists
        cache_path = Path(str(self.__config.cache_dir)).expanduser()
        cache_path.mkdir(parents=True, exist_ok=True)
        self.__config.cache_dir = cache_path

    def get_config(self) -> PreviewMakerConfig:
        """Get the current configuration.

        Returns:
            The current PreviewMakerConfig instance
        """
        return self.__config

    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values.

        Args:
            updates: Dictionary of configuration updates
        """
        current_dict = self.__config.model_dump()
        current_dict.update(updates)
        self.__config = PreviewMakerConfig(**current_dict)

        # Save to file if one was loaded
        if self.__config_file:
            with open(self.__config_file, "w") as f:
                toml.dump(self.__config.model_dump(), f)


# Global configuration instance
config_manager = ConfigManager()
