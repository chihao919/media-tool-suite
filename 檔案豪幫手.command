#!/bin/bash
# 檔案豪幫手 - Media Tool Suite Launcher
# Double-click to run the application

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3 from https://www.python.org/"
    exit 1
fi

# Check if FFmpeg is available
if ! command -v ffmpeg &> /dev/null; then
    echo "Warning: FFmpeg not found in PATH."
    echo "Some features may not work. Install FFmpeg from https://ffmpeg.org/"
fi

# Run the application
echo "Starting 檔案豪幫手..."
python3 main.py

# Keep terminal open if there's an error
if [ $? -ne 0 ]; then
    echo "Press any key to exit..."
    read -n 1
fi