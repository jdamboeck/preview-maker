#!/usr/bin/env python3
"""
Downloads a sample kimono image for testing the Kimono Textile Analyzer.
"""
import os
import urllib.request
from urllib.error import URLError, HTTPError


def download_sample_image():
    """Download a sample kimono image for testing."""
    # URL of a sample kimono image (a public domain image)
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
    output_path = "sample_kimono.jpg"

    # Check if the file already exists
    if os.path.exists(output_path):
        print(f"Sample image already exists at {output_path}")
        return output_path

    print(f"Downloading sample kimono image to {output_path}...")
    try:
        urllib.request.urlretrieve(sample_url, output_path)
        print("Download complete!")
        return output_path
    except (URLError, HTTPError) as e:
        print(f"Error downloading sample image: {e}")

        # Try alternative URL if the first one fails
        alt_sample_url = (
            "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/"
            "Woman%27s_Kimono_with_Fans_and_Flowers_LACMA_M.62.5.1a-b_"
            "%281_of_2%29.jpg/800px-Woman%27s_Kimono_with_Fans_and_"
            "Flowers_LACMA_M.62.5.1a-b_%281_of_2%29.jpg"
        )
        try:
            print("Trying alternative image URL...")
            urllib.request.urlretrieve(alt_sample_url, output_path)
            print("Download complete!")
            return output_path
        except (URLError, HTTPError) as e2:
            print(f"Error downloading alternative image: {e2}")
            return None
    except Exception as e:
        print(f"Unexpected error downloading image: {e}")
        return None


if __name__ == "__main__":
    sample_path = download_sample_image()
    if sample_path:
        print("\nYou can now run the Kimono Textile Analyzer with this sample image:")
        print("1. Run the main application: python3 kimono_analyzer.py")
        print("2. Drag and drop the sample image into the application window")

        # Try to make the image executable (for Linux users)
        try:
            os.chmod(sample_path, 0o755)
        except (PermissionError, OSError) as e:
            print(f"Could not set permissions: {e}")
