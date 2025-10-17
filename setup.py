#!/usr/bin/env python3
"""
Setup script for 檔案豪幫手 (Media Tool Suite)
"""

from setuptools import setup, find_packages
import sys
import os

# Read README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Application metadata
APP_NAME = "檔案豪幫手"
APP_VERSION = "2.0.0"
APP_AUTHOR = "Claude Code Assistant"
APP_DESCRIPTION = "A comprehensive media processing application"

setup(
    name="media-tool-suite",
    version=APP_VERSION,
    author=APP_AUTHOR,
    description=APP_DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",

    # Package configuration
    packages=find_packages(),
    package_dir={"": "src"},
    py_modules=["main"],

    # Dependencies
    python_requires=">=3.7",
    install_requires=[
        # Core Python modules (no external dependencies required)
    ],

    # Optional dependencies
    extras_require={
        "dragdrop": ["tkinterdnd2>=0.3.0"],
    },

    # Entry points
    entry_points={
        "console_scripts": [
            "media-tool-suite=main:main",
        ],
    },

    # Include non-Python files
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt"],
    },

    # Metadata
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio :: Conversion",
        "Topic :: Multimedia :: Video :: Conversion",
    ],

    # Keywords
    keywords="media audio video conversion ffmpeg gui",
)