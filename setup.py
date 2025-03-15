"""Setup configuration for Preview Maker."""

from setuptools import setup, find_packages

setup(
    name="preview-maker",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pillow",
        "pycairo",
        "pygobject",
        "pydantic",
        "toml",
        "google-generativeai",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "black",
            "isort",
            "mypy",
            "pylint",
        ],
    },
    python_requires=">=3.8",
    author="jdamboeck",
    author_email="jdamboeck@example.com",
    description="A tool for creating image previews with overlays",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jdamboeck/preview-maker",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Multimedia :: Graphics",
    ],
)
