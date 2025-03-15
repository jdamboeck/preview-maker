#!/usr/bin/env python3
"""Command-line tool for generating AI previews.

This script provides a simple command-line interface for generating
previews with AI-identified regions of interest highlighted.
"""

import argparse
import logging
import os
import sys
from pathlib import Path

from preview_maker.ai import AIPreviewGenerator
from preview_maker.core.logging import setup_logging


def parse_args():
    """Parse command-line arguments.

    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Generate previews with AI-identified regions of interest."
    )
    parser.add_argument(
        "input_path",
        type=str,
        help="Path to the input image or directory of images.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        help="Directory to save the generated previews. If not specified, "
        "previews will be saved in the same directory as the input images "
        "with '_preview' suffix.",
    )
    parser.add_argument(
        "-k",
        "--api-key",
        type=str,
        help="Google API key for Gemini. If not provided, will try to use "
        "the GOOGLE_API_KEY environment variable.",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="gemini-pro-vision",
        help="Gemini model to use. Default: gemini-pro-vision",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )
    return parser.parse_args()


def process_image(
    generator: AIPreviewGenerator, input_path: Path, output_dir: Path
) -> bool:
    """Process a single image.

    Args:
        generator: The AIPreviewGenerator instance.
        input_path: Path to the input image.
        output_dir: Directory to save the preview.

    Returns:
        True if processing was successful, False otherwise.
    """
    try:
        # Create output path
        output_filename = f"{input_path.stem}_preview{input_path.suffix}"
        output_path = output_dir / output_filename

        # Generate preview
        logging.info(f"Processing {input_path}...")
        preview = generator.generate_preview(input_path, output_path)

        if preview:
            logging.info(f"Preview saved to {output_path}")
            return True
        else:
            logging.error(f"Failed to generate preview for {input_path}")
            return False

    except Exception as e:
        logging.error(f"Error processing {input_path}: {e}")
        return False


def process_directory(
    generator: AIPreviewGenerator, input_dir: Path, output_dir: Path
) -> tuple[int, int]:
    """Process all images in a directory.

    Args:
        generator: The AIPreviewGenerator instance.
        input_dir: Directory containing input images.
        output_dir: Directory to save the previews.

    Returns:
        A tuple of (success_count, total_count).
    """
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all image files
    image_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"]
    image_files = [
        f
        for f in input_dir.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]

    # Process each image
    success_count = 0
    for image_file in image_files:
        if process_image(generator, image_file, output_dir):
            success_count += 1

    return success_count, len(image_files)


def main():
    """Main entry point."""
    args = parse_args()

    # Set up logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level=log_level)

    # Create the preview generator
    try:
        api_key = args.api_key or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            logging.error(
                "No API key provided. Please provide an API key with --api-key "
                "or set the GOOGLE_API_KEY environment variable."
            )
            return 1

        generator = AIPreviewGenerator(api_key=api_key, model_name=args.model)

        # Process input path
        input_path = Path(args.input_path)
        if not input_path.exists():
            logging.error(f"Input path does not exist: {input_path}")
            return 1

        # Determine output directory
        if args.output_dir:
            output_dir = Path(args.output_dir)
        elif input_path.is_file():
            output_dir = input_path.parent
        else:
            output_dir = input_path / "previews"

        # Process input
        if input_path.is_file():
            success = process_image(generator, input_path, output_dir)
            return 0 if success else 1
        else:
            success_count, total_count = process_directory(
                generator, input_path, output_dir
            )
            logging.info(
                f"Processed {success_count} of {total_count} images successfully."
            )
            return 0 if success_count == total_count else 1

    except Exception as e:
        logging.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
