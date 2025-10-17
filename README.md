# 檔案豪幫手 (Media Tool Suite)

A comprehensive media processing application with GUI support for audio and video conversion, splitting, and more.

## Features

- 🎵 **Audio Conversion**: Convert between MP3, WAV, FLAC, AAC, OGG, M4A formats
- 🎬 **Video Conversion**: Convert between MP4, AVI, MKV, MOV, WebM formats
- ✂️ **Media Splitting**: Split files by duration, size, or number of parts
- 🎥 **Screen Recording**: Record screen with system audio (macOS)
- 📊 **Progress Tracking**: Real-time conversion progress with detailed history
- ⚙️ **Advanced Settings**: Configurable bitrates, sample rates, and quality options
- 🎯 **Smart Detection**: Auto-detect media types and suggest optimal settings

## Project Structure

```
splitvideo/
├── src/                    # Main source code
│   ├── media_converter.py  # Main GUI application
│   ├── media_processor.py  # Core processing logic
│   ├── media_handlers.py   # File type handlers (Factory pattern)
│   ├── process_strategies.py # Processing strategies (Strategy pattern)
│   ├── screen_recorder.py  # Screen recording module
│   └── app_constants.py    # Application constants
├── tests/                  # Test files
│   ├── test_conversion_core.py
│   ├── test_design_patterns.py
│   ├── test_screen_recorder.py
│   └── test_*.py
├── examples/               # Example scripts and legacy code
├── docs/                   # Documentation
│   └── SCREEN_RECORDING_GUIDE.md  # Screen recording usage guide
├── audio/                  # Test audio files
├── video/                  # Test video files
└── main.py                 # Application entry point
```

## Quick Start

### Prerequisites

- Python 3.7+
- FFmpeg installed and accessible in PATH
- tkinter (usually included with Python)

### Installation

1. Clone or download this repository
2. Install FFmpeg if not already installed:
   ```bash
   # macOS
   brew install ffmpeg

   # Ubuntu/Debian
   sudo apt update && sudo apt install ffmpeg

   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

### Running the Application

```bash
python3 main.py
```

Or run directly:

```bash
python3 src/media_converter.py
```

## Usage

### Convert Tab
1. Select media type (Audio/Video/Auto Detect)
2. Add files or folders to convert
3. Choose output format and quality settings
4. Click "🚀 Convert All Files 🚀"

### Split Tab
1. Add media files to split
2. Choose split mode (Duration/Size/Parts)
3. Set split parameters
4. Click "✂️ Split Selected Files"

### Screen Record Tab (macOS)
1. Install BlackHole for system audio recording (see [Screen Recording Guide](docs/SCREEN_RECORDING_GUIDE.md))
2. Select video source (screen) and audio source
3. Choose framerate (24/30/60 fps) and quality
4. Click "🔴 Start Recording"
5. Click "⏹ Stop Recording" when done
6. Recording saved to Desktop

**Note**: To record system audio (not microphone), you need to install [BlackHole](https://github.com/ExistentialAudio/BlackHole) and configure Multi-Output Device. See detailed guide in `docs/SCREEN_RECORDING_GUIDE.md`.

### Settings Tab
- Configure default conversion settings
- Set output directory preferences
- Customize file naming conventions
- View conversion history and statistics

## Architecture

This application uses several design patterns:

- **Factory Pattern**: `MediaHandlerFactory` creates appropriate handlers for different file types
- **Strategy Pattern**: Different processing strategies for conversion, splitting, etc.
- **Builder Pattern**: `MediaProcessorBuilder` for creating configured processors

## Testing

Run tests from the project root:

```bash
# Test core functionality
python3 tests/test_conversion_core.py

# Test design patterns
python3 tests/test_design_patterns.py

# Test video conversion
python3 tests/test_video_conversion.py

# Test screen recording
python3 -m pytest tests/test_screen_recorder.py -v

# Or use make
make test
```

## Building Installers

### Quick Build (Recommended)

**macOS/Linux:**
```bash
./build_all.sh
```

**Windows:**
```cmd
build_all.bat
```

**Using Make:**
```bash
make build          # Build for current platform
make build-mac      # Build macOS app
make build-win      # Build Windows exe
make dist           # Create distribution packages
```

### Manual Build

**macOS Application:**
```bash
pip install py2app
python build_mac.py py2app
```

**Windows Executable:**
```bash
pip install pyinstaller
python build_windows.py
```

### Build Requirements

**macOS:**
- py2app: `pip install py2app`
- Optional: create DMG with `hdiutil`

**Windows:**
- PyInstaller: `pip install pyinstaller`
- Optional: NSIS for installer creation

**All Platforms:**
- Python 3.7+
- FFmpeg installed and in PATH

For detailed build instructions, see [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md).

## Development

```bash
# Install dependencies
make install

# Run in development mode
make dev

# Clean build artifacts
make clean

# Format code
make format

# Run linting
make lint
```

## License

This project is for educational and personal use.