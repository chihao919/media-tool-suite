#!/bin/bash

# Create macOS Application Bundle for Audio Converter

APP_NAME="Audio Converter"
APP_DIR="$APP_NAME.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

# Remove existing app if it exists
[ -d "$APP_DIR" ] && rm -rf "$APP_DIR"

# Create directory structure
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# Create Info.plist
cat > "$CONTENTS_DIR/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Audio Converter</string>
    <key>CFBundleDisplayName</key>
    <string>Audio Converter</string>
    <key>CFBundleIdentifier</key>
    <string>com.local.audioconverter</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.12.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.music</string>
</dict>
</plist>
EOF

# Create launcher script
cat > "$MACOS_DIR/launcher" << 'EOF'
#!/bin/bash

# Get the directory where the app bundle is located
APP_DIR="$( cd "$( dirname "$0" )" && cd ../.. && cd .. && pwd )"

# Change to the directory containing the Python script
cd "$APP_DIR"

# Check dependencies
if ! command -v python3 &> /dev/null; then
    osascript -e 'display dialog "Python 3 is not installed.\nPlease install from python.org" buttons {"OK"} with title "Audio Converter" with icon stop'
    exit 1
fi

if ! command -v ffmpeg &> /dev/null; then
    response=$(osascript -e 'display dialog "FFmpeg is not installed.\n\nInstall with Homebrew?" buttons {"Cancel", "Install"} default button "Install" with title "Audio Converter" with icon caution')
    if [[ "$response" == *"Install"* ]]; then
        osascript -e 'tell application "Terminal" to do script "brew install ffmpeg"'
    fi
    exit 1
fi

# Launch the Python GUI
exec python3 audio_converter_gui.py
EOF

# Make launcher executable
chmod +x "$MACOS_DIR/launcher"

# Copy Python files to Resources
cp audio_converter_gui.py "$RESOURCES_DIR/"
cp audio_processor.py "$RESOURCES_DIR/" 2>/dev/null || true
cp audio_utils.py "$RESOURCES_DIR/" 2>/dev/null || true

# Create a simple icon file (you can replace this with a proper .icns file)
cat > "$RESOURCES_DIR/AppIcon.icns" << 'EOF'
# Placeholder for icon
EOF

echo "✅ macOS App Bundle created: $APP_DIR"
echo ""
echo "You can now:"
echo "1. Double-click '$APP_DIR' to launch the application"
echo "2. Drag it to Applications folder for easy access"
echo "3. Add it to the Dock for quick launch"