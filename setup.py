"""Setup script for the Preview Maker package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="preview-maker",
    version="0.1.0",
    author="jdamboeck",
    author_email="jdamboeck@example.com",
    description=(
        "A GTK-based application for creating image previews "
        "with AI-powered highlight overlays"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jdamboeck/preview-maker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "preview-maker=preview_maker.app:main",
        ],
    },
)
