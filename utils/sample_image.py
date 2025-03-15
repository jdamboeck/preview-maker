#!/usr/bin/env python3
"""
Downloads a sample image for testing the Preview Maker.
"""
import os
import urllib.request
from urllib.error import URLError, HTTPError


def download_sample_image():
    """Download a sample image for testing."""
    # URL of a sample image (a public domain image)
    sample_url = (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/"
        "Kimono_with_Fans_and_Flowers_%28Kosode%29_%28Japan%29%2C_"
        "18th_century%2C_silk_and_paper%2C_plain_weave_with_"
        "supplementary_weft_patterning%2C_resist-dye_paste_%28yuzen%29%2C_"
        "embroidery_and_metallic_paper-wrapped_thread%2C_HAA.JPG/800px-"
        "Kimono_with_Fans_and_Flowers_%28Kosode%29_%28Japan%29%2C_"
        "18th_century%2C_silk_and_paper%2C_plain_weave_with_"
        "supplementary_weft_patterning%2C_resist-dye_paste_%28yuzen%29%2C_"
        "embroidery_and_metallic_paper-wrapped_thread%2C_HAA.JPG"
    )

    # File path to save the image
    output_path = "data/sample_image.jpg"

    # Check if the file already exists
    if os.path.exists(output_path):
        print(f"Sample image already exists at {output_path}")
        return output_path

    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Download the image
    try:
        print(f"Downloading sample image from {sample_url}")
        urllib.request.urlretrieve(sample_url, output_path)
        print(f"Sample image downloaded to {output_path}")
        return output_path
    except (URLError, HTTPError) as e:
        print(f"Error downloading sample image: {e}")
        return None


if __name__ == "__main__":
    download_sample_image()
