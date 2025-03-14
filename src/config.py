"""
Configuration module for the Preview Maker application.
Manages all configurable settings through a TOML file.
"""

import os

# Define default configuration values
DEFAULT_CONFIG = {
    # File and directory paths
    "paths": {
        "previews_dir": "previews",
        "debug_dir": "previews/debug",
        "prompts_dir": "prompts",
        "default_prompt_file": "prompts/user_prompt.md",
        "technical_prompt_file": "prompts/technical_prompt.md",
    },
    # Image processing parameters
    "image_processing": {
        "selection_ratio": 0.1,  # Selection circle diameter as % of shortest dimension
        "zoom_factor": 3.0,  # How much to zoom the preview
        "png_compression": 4,  # Balanced compression (range 0-9, lower is better quality)
        "high_resampling": 1,  # Image.LANCZOS (1) is highest quality resampling filter
    },
    # Gemini API configuration
    "gemini_api": {
        "model_name": "gemini-1.5-flash",
        "max_output_tokens": 256,
        "temperature": 0.1,  # Low temperature for more deterministic responses
        "top_p": 0.95,
        "top_k": 0,
    },
    # File type support
    "supported_formats": {
        "image_extensions": [".jpg", ".jpeg", ".png", ".bmp", ".gif"],
    },
    # Target type options
    "detection": {
        "default_target_type": "interesting detail",
    },
    # UI settings
    "ui": {
        "debug_mode": False,  # Whether to show detailed debug logs
    },
}

# Path to the config file and workspace root
CONFIG_FILE = "config.toml"
WORKSPACE_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)  # Go up one level to project root
CONFIG_PATH = os.path.join(WORKSPACE_ROOT, CONFIG_FILE)

# Store the configuration instance as a global variable
_CONFIG = None


# Load configuration
def load_config():
    """Load configuration from the config file or create default if not exists."""
    try:
        import toml

        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                # Load the TOML file and merge with defaults
                user_config = toml.load(f)
                # Recursively update the default config with user values
                merged_config = _deep_update(DEFAULT_CONFIG.copy(), user_config)
                return merged_config
        else:
            # Create a default config file
            create_default_config()
            return DEFAULT_CONFIG
    except ImportError:
        print("Warning: toml package not installed. Using default configuration.")
        print("To enable configuration, run: pip install toml")
        return DEFAULT_CONFIG
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return DEFAULT_CONFIG


def create_default_config():
    """Create a default configuration file if it doesn't exist."""
    try:
        import toml

        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

        # Write the default configuration to the file
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            toml.dump(DEFAULT_CONFIG, f)
            print(f"Created default configuration file at {CONFIG_PATH}")
    except ImportError:
        print(
            "Warning: toml package not installed. Cannot create default configuration file."
        )
        print("To enable configuration, run: pip install toml")
    except Exception as e:
        print(f"Error creating default configuration file: {e}")


def _deep_update(original, update):
    """Recursively update a dictionary."""
    for key, value in update.items():
        if (
            key in original
            and isinstance(original[key], dict)
            and isinstance(value, dict)
        ):
            _deep_update(original[key], value)
        else:
            original[key] = value
    return original


def get_config():
    """Get the configuration, loading it if necessary."""
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = load_config()
    return _CONFIG


def get_path(key):
    """
    Get a path from the configuration.

    Returns an absolute path based on the workspace root.
    """
    config = get_config()
    if key in config["paths"]:
        path = config["paths"][key]
        # If path is not absolute, make it absolute based on workspace root
        if not os.path.isabs(path):
            path = os.path.join(WORKSPACE_ROOT, path)
        # Create the directory if it doesn't exist
        if key.endswith("_dir"):
            os.makedirs(path, exist_ok=True)
        return path
    return os.path.join(WORKSPACE_ROOT, DEFAULT_CONFIG["paths"].get(key, ""))


def get_image_processing(key):
    """Get an image processing parameter from the configuration."""
    config = get_config()
    if key in config["image_processing"]:
        return config["image_processing"][key]
    return DEFAULT_CONFIG["image_processing"].get(key, None)


def get_gemini_api(key):
    """Get a Gemini API parameter from the configuration."""
    config = get_config()
    if key in config["gemini_api"]:
        return config["gemini_api"][key]
    return DEFAULT_CONFIG["gemini_api"].get(key, None)


def get_supported_formats():
    """Get the supported file formats."""
    config = get_config()
    return config["supported_formats"]["image_extensions"]


def get_default_target_type():
    """Get the default target type for detection."""
    config = get_config()
    return config["detection"]["default_target_type"]


# Load environment variables
def load_environment_variables():
    """Load environment variables from .env file."""
    try:
        from dotenv import load_dotenv

        # Try to load from .env file
        env_path = os.path.join(WORKSPACE_ROOT, ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
            return True
        else:
            # If .env doesn't exist, try to create it
            try:
                with open(env_path, "w", encoding="utf-8") as f:
                    f.write("# Environment variables for Kimono Textile Analyzer\n")
                    f.write("GEMINI_API_KEY=your_gemini_api_key_here\n")
                print(f"Created template .env file at {env_path}")
            except Exception as e:
                print(f"Warning: Could not create .env file: {e}")
        return False
    except ImportError:
        print(
            "Warning: python-dotenv package not installed. Using environment variables directly."
        )
        print("To enable .env file support, run: pip install python-dotenv")
        return False
    except Exception as e:
        print(f"Error loading environment variables: {e}")
        return False


# Initialize configuration
CONFIG = get_config()

# Ensure required directories exist
for dir_key in ["previews_dir", "debug_dir", "prompts_dir"]:
    path = get_path(dir_key)
    os.makedirs(path, exist_ok=True)


# Create split prompt files if they don't exist
def ensure_prompt_files():
    """Ensure the prompt files exist with appropriate content."""
    # Technical prompt (system/framework part, not intended for user editing)
    tech_prompt_file = get_path("technical_prompt_file")
    if not os.path.exists(tech_prompt_file):
        os.makedirs(os.path.dirname(tech_prompt_file), exist_ok=True)
        with open(tech_prompt_file, "w", encoding="utf-8") as f:
            f.write(DEFAULT_TECHNICAL_PROMPT)
        print(f"Created technical prompt file at {tech_prompt_file}")

    # User-editable prompt (the instructions specific to what to look for)
    user_prompt_file = get_path("default_prompt_file")
    if not os.path.exists(user_prompt_file):
        os.makedirs(os.path.dirname(user_prompt_file), exist_ok=True)
        with open(user_prompt_file, "w", encoding="utf-8") as f:
            f.write(DEFAULT_USER_PROMPT)
        print(f"Created user prompt file at {user_prompt_file}")


# Helper function to load and combine prompts
def get_combined_prompt(target_type=None):
    """
    Load and combine the user and technical prompts.

    Args:
        target_type: The specific target type to look for (replaces {target_type} placeholder)

    Returns:
        str: The combined prompt with target_type replaced if provided
    """
    # Load the technical (system) prompt
    try:
        with open(get_path("technical_prompt_file"), "r", encoding="utf-8") as f:
            technical_prompt = f.read().strip()
    except FileNotFoundError:
        technical_prompt = DEFAULT_TECHNICAL_PROMPT

    # Load the user-editable prompt
    try:
        with open(get_path("default_prompt_file"), "r", encoding="utf-8") as f:
            user_prompt = f.read().strip()
    except FileNotFoundError:
        user_prompt = DEFAULT_USER_PROMPT

    # Combine prompts with a separator
    combined_prompt = f"{user_prompt}\n\n{technical_prompt}"

    # Replace target_type placeholder if provided
    if target_type:
        combined_prompt = combined_prompt.replace("{target_type}", target_type)

    return combined_prompt


# Function to update and save config
def update_config(section, key, value):
    """
    Update a configuration value and save it to the TOML file.

    Args:
        section (str): The configuration section (e.g., 'image_processing')
        key (str): The configuration key to update
        value: The new value to set

    Returns:
        bool: True if the update was successful, False otherwise
    """
    try:
        import toml

        # First make sure we have the latest config
        config = get_config()

        # Update the config value
        if section in config and key in config[section]:
            config[section][key] = value

            # Save the updated config to the TOML file
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                toml.dump(config, f)

            # Reset the cached config so subsequent calls get the new values
            global _CONFIG
            _CONFIG = None

            print(f"Updated config: {section}.{key} = {value}")
            return True
        else:
            print(f"Error: Section '{section}' or key '{key}' not found in config")
            return False
    except ImportError:
        print("Warning: toml package not installed. Cannot update configuration.")
        print("To enable configuration, run: pip install toml")
        return False
    except Exception as e:
        print(f"Error updating configuration: {e}")
        return False


# Default prompts as fallbacks
DEFAULT_TECHNICAL_PROMPT = """
Respond with TWO PARTS:

1. COORDS: Normalized values between 0 and 1 in the format x1,y1,x2,y2 where (x1,y1) is the top-left corner and (x2,y2) is the bottom-right corner.

2. DESCRIPTION: A brief description (1-2 sentences) of what you identified and why it's interesting or visually notable.

Format your response EXACTLY as:
COORDS: x1,y1,x2,y2
DESCRIPTION: Your description here.
""".strip()

DEFAULT_USER_PROMPT = """Please analyze this image and identify ONE SPECIFIC {target_type} that stands out.

I need you to find a SINGLE, DISTINCT object or feature in this image - not a general area.

Step by step:
1. Scan the entire image for distinct {target_type} elements
2. Identify ONE specific element that is:
   - Clearly defined with distinct boundaries
   - Visually separate from its surroundings
   - Small enough to be a precise target (5-15% of the image area)
   - Detailed enough to benefit from magnification

3. Find the exact center point of this specific element
4. Create a tight bounding box directly around ONLY this single element
""".strip()

# Ensure the prompt files exist
ensure_prompt_files()
