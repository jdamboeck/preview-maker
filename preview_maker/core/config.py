"""Configuration management for Preview Maker.

This module handles loading and managing configuration from both TOML files
and environment variables, with support for runtime updates and validation.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Type, Union
import os
import threading
import toml
from pydantic import BaseModel, Field


class PreviewMakerConfig(BaseModel):
    """Configuration schema for Preview Maker."""

    # Paths Configuration
    previews_dir: Path = Field(
        default=Path("previews"),
        description="Directory for storing preview images",
    )
    debug_dir: Path = Field(
        default=Path("previews/debug"),
        description="Directory for storing debug images",
    )
    prompts_dir: Path = Field(
        default=Path("prompts"),
        description="Directory for storing prompt templates",
    )
    cache_dir: Path = Field(
        default=Path("cache"),
        description="Directory for storing cached images",
    )
    default_prompt_file: Path = Field(
        default=Path("prompts/user_prompt.md"),
        description="Default prompt template file",
    )
    technical_prompt_file: Path = Field(
        default=Path("prompts/technical_prompt.md"),
        description="Technical prompt template file",
    )

    # Image Processing Configuration
    selection_ratio: float = Field(
        default=0.07163781624500666,
        description="Ratio for selection overlay",
    )
    zoom_factor: float = Field(
        default=3.0,
        description="Zoom factor for preview overlay",
    )
    max_cache_size_mb: int = Field(
        default=100,  # 100 MB default cache size
        description="Maximum cache size in megabytes",
    )
    png_compression: int = Field(
        default=4,
        description="PNG compression level (0-9)",
    )
    high_resampling: int = Field(
        default=1,
        description="High quality resampling flag",
    )

    # Gemini API Configuration
    gemini_api_key: str = Field(
        default="",
        description="Google Gemini API key for image analysis",
    )
    model_name: str = Field(
        default="gemini-1.5-flash",
        description="Gemini model to use",
    )
    max_output_tokens: int = Field(
        default=256,
        description="Maximum output tokens for Gemini API",
    )
    temperature: float = Field(
        default=0.1,
        description="Temperature for Gemini API",
    )
    top_p: float = Field(
        default=0.95,
        description="Top-p value for Gemini API",
    )
    top_k: int = Field(
        default=0,
        description="Top-k value for Gemini API",
    )

    # Supported Formats
    image_extensions: list[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".bmp", ".gif"],
        description="Supported image file extensions",
    )

    # Detection Configuration
    default_target_type: str = Field(
        default="Produkt-Highlight",
        description="Default target type for detection",
    )

    # UI Configuration
    debug_mode: bool = Field(
        default=True,
        description="Debug mode flag",
    )
    window_width: int = Field(
        default=1024,
        description="Default window width",
    )
    window_height: int = Field(
        default=768,
        description="Default window height",
    )
    overlay_color: str = Field(
        default="#FF0000",
        description="Color for highlight overlays",
    )
    overlay_opacity: float = Field(
        default=0.7,
        description="Opacity for highlight overlays (0-1)",
    )


class ConfigManager:
    """Manages application configuration from files and environment variables."""

    # Class-level variables for singleton pattern
    _instance: Optional["ConfigManager"] = None
    _lock = threading.RLock()
    _initialized = False
    _config: Optional[PreviewMakerConfig] = None
    _config_file: Optional[Path] = None

    @classmethod
    def _reset_for_testing(cls) -> None:
        """Reset the singleton instance for testing purposes."""
        with cls._lock:
            cls._instance = None
            cls._initialized = False
            cls._config = None
            cls._config_file = None

    def __new__(cls) -> "ConfigManager":
        """Ensure singleton pattern for configuration manager."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self) -> None:
        """Initialize the configuration manager."""
        with self._lock:
            if not self._initialized:
                self._config = PreviewMakerConfig()
                self._config_file = None
                self._initialized = True

    def _convert_env_value(self, value: str, target_type: Type) -> Any:
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
        if target_type == list:
            return value.split(",")
        return value

    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # Map environment variables to config attributes
        env_prefix = "PREVIEW_MAKER_"

        # Dynamically create mapping from config fields
        if not self._config:
            return

        env_mapping = {}
        for field_name in self._config.model_fields:
            env_name = f"{env_prefix}{field_name.upper()}"
            env_mapping[env_name] = field_name

        # Process each environment variable
        for env_var, config_key in env_mapping.items():
            if env_var in os.environ:
                env_value = os.environ[env_var]
                field_info = self._config.model_fields.get(config_key)
                if field_info and hasattr(field_info, "annotation"):
                    annotation = field_info.annotation
                    if annotation == Path:
                        setattr(self._config, config_key, Path(env_value))
                    else:
                        field_type = type(getattr(self._config, config_key))
                        converted_value = self._convert_env_value(env_value, field_type)
                        setattr(self._config, config_key, converted_value)
                else:
                    field_type = type(getattr(self._config, config_key))
                    converted_value = self._convert_env_value(env_value, field_type)
                    setattr(self._config, config_key, converted_value)

    def load_config(
        self, config_file: Optional[Union[str, Path]] = "config.toml"
    ) -> None:
        """Load configuration from file and environment variables.

        Args:
            config_file: Optional path to TOML configuration file
        """
        with self._lock:
            # Load from file if specified
            if config_file:
                config_path = Path(config_file).expanduser().resolve()
                if config_path.exists():
                    self._config_file = config_path
                    try:
                        config_data = toml.load(config_path)

                        # Extract flat configuration from nested TOML structure
                        flat_config = {}
                        for section, values in config_data.items():
                            if isinstance(values, dict):
                                for key, value in values.items():
                                    flat_config[key] = value
                            else:
                                flat_config[section] = values

                        # Update only fields that are present in the config file
                        if not self._config:
                            self._config = PreviewMakerConfig()

                        current_config = self._config.model_dump()
                        for key, value in flat_config.items():
                            if key in current_config:
                                current_config[key] = value

                        self._config = PreviewMakerConfig(**current_config)
                    except Exception as e:
                        # Log error or handle gracefully
                        print(f"Error loading configuration from {config_path}: {e}")

            # Override with environment variables
            self._load_from_env()

            # Ensure all directories exist
            self._ensure_directories_exist()

    def _ensure_directories_exist(self) -> None:
        """Ensure that configured directories exist."""
        if not self._config:
            return

        # Create previews directory
        Path(self._config.previews_dir).mkdir(exist_ok=True, parents=True)

        # Create debug directory
        Path(self._config.debug_dir).mkdir(exist_ok=True, parents=True)

        # Create prompts directory
        Path(self._config.prompts_dir).mkdir(exist_ok=True, parents=True)

        # Create cache directory
        Path(self._config.cache_dir).mkdir(exist_ok=True, parents=True)

    def get_config(self) -> PreviewMakerConfig:
        """Get the current configuration.

        Returns:
            The current PreviewMakerConfig instance
        """
        with self._lock:
            if not self._config:
                self._config = PreviewMakerConfig()
            return self._config

    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values.

        Args:
            updates: Dictionary of configuration updates
        """
        with self._lock:
            if not self._config:
                self._config = PreviewMakerConfig()

            current_dict = self._config.model_dump()
            current_dict.update(updates)
            self._config = PreviewMakerConfig(**current_dict)

            # Save to file if one was loaded
            if self._config_file:
                try:
                    # Convert to nested TOML structure
                    toml_config = {}

                    # Paths section
                    toml_config["paths"] = {
                        "previews_dir": str(self._config.previews_dir),
                        "debug_dir": str(self._config.debug_dir),
                        "prompts_dir": str(self._config.prompts_dir),
                        "cache_dir": str(self._config.cache_dir),
                        "default_prompt_file": str(self._config.default_prompt_file),
                        "technical_prompt_file": str(
                            self._config.technical_prompt_file
                        ),
                    }

                    # Image processing section
                    toml_config["image_processing"] = {
                        "selection_ratio": self._config.selection_ratio,
                        "zoom_factor": self._config.zoom_factor,
                        "max_cache_size_mb": self._config.max_cache_size_mb,
                        "png_compression": self._config.png_compression,
                        "high_resampling": self._config.high_resampling,
                    }

                    # Gemini API section
                    toml_config["gemini_api"] = {
                        "model_name": self._config.model_name,
                        "max_output_tokens": self._config.max_output_tokens,
                        "temperature": self._config.temperature,
                        "top_p": self._config.top_p,
                        "top_k": self._config.top_k,
                    }

                    # Supported formats section
                    toml_config["supported_formats"] = {
                        "image_extensions": self._config.image_extensions,
                    }

                    # Detection section
                    toml_config["detection"] = {
                        "default_target_type": self._config.default_target_type,
                    }

                    # UI section
                    toml_config["ui"] = {
                        "debug_mode": self._config.debug_mode,
                        "window_width": self._config.window_width,
                        "window_height": self._config.window_height,
                        "overlay_color": self._config.overlay_color,
                        "overlay_opacity": self._config.overlay_opacity,
                    }

                    with open(self._config_file, "w") as f:
                        toml.dump(toml_config, f)
                except Exception as e:
                    # Log error or handle gracefully
                    print(f"Error saving configuration to {self._config_file}: {e}")


# Global configuration instance
config_manager = ConfigManager()
