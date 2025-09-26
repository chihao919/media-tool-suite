#!/bin/bash

# Audio Converter GUI Launcher for macOS

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to that directory
cd "$DIR"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    osascript -e 'display dialog "Python 3 is not installed. Please install Python 3 to use this application." buttons {"OK"} default button "OK" with title "Audio Converter" with icon stop'
    exit 1
fi

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    osascript -e 'display dialog "FFmpeg is not installed. Please install FFmpeg using Homebrew:\nbrew install ffmpeg" buttons {"OK"} default button "OK" with title "Audio Converter" with icon caution'
    exit 1
fi

# Launch the GUI application
python3 audio_converter_gui.py

# Keep terminal open if there was an error
if [ $? -ne 0 ]; then
    echo "Press any key to close..."
    read -n 1
fi