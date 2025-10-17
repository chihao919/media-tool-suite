#!/bin/bash
# 一鍵建置腳本 - 檔案豪幫手

set -e  # Exit on error

APP_NAME="檔案豪幫手"
APP_VERSION="2.0.0"

echo "🚀 Building $APP_NAME v$APP_VERSION for multiple platforms..."
echo "=================================================="

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "📍 Using Python $python_version"

# Create build directory
mkdir -p builds
cd builds

# Platform detection
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Detected macOS - Building Mac version..."

    # Install py2app if not installed
    pip3 install py2app --quiet

    # Copy source files
    cp -r ../src .
    cp ../main.py .
    cp ../build_mac.py .
    cp ../README.md .

    echo "📦 Building macOS app..."
    python3 build_mac.py py2app --quiet

    if [ -d "dist/$APP_NAME.app" ]; then
        echo "✅ macOS build successful!"
        echo "   📁 Location: builds/dist/$APP_NAME.app"

        # Create DMG (optional)
        echo "📀 Creating DMG installer..."
        if command -v hdiutil &> /dev/null; then
            hdiutil create -volname "$APP_NAME" -srcfolder dist -ov -format UDZO "${APP_NAME}_v${APP_VERSION}.dmg" > /dev/null
            echo "✅ DMG created: ${APP_NAME}_v${APP_VERSION}.dmg"
        else
            echo "⚠️  hdiutil not found - DMG creation skipped"
        fi
    else
        echo "❌ macOS build failed!"
        exit 1
    fi

elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "🪟 Detected Windows - Building Windows version..."

    # Install PyInstaller if not installed
    pip install pyinstaller --quiet

    # Copy source files
    cp -r ../src .
    cp ../main.py .
    cp ../build_windows.py .
    cp ../README.md .

    echo "📦 Building Windows executable..."
    python build_windows.py

    if [ -f "dist/$APP_NAME.exe" ]; then
        echo "✅ Windows build successful!"
        echo "   📁 Location: builds/dist/$APP_NAME.exe"
    else
        echo "❌ Windows build failed!"
        exit 1
    fi

else
    echo "🐧 Detected Linux - Creating portable version..."

    # Create portable version
    mkdir -p "portable/$APP_NAME"
    cp -r ../src "portable/$APP_NAME/"
    cp ../main.py "portable/$APP_NAME/"
    cp ../README.md "portable/$APP_NAME/"

    # Create launch script
    cat > "portable/$APP_NAME/launch.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 main.py "$@"
EOF

    chmod +x "portable/$APP_NAME/launch.sh"

    # Create archive
    cd portable
    tar -czf "../${APP_NAME}_v${APP_VERSION}_Linux.tar.gz" "$APP_NAME"
    cd ..

    echo "✅ Linux portable version created!"
    echo "   📁 Location: builds/${APP_NAME}_v${APP_VERSION}_Linux.tar.gz"
fi

echo "=================================================="
echo "🎉 Build process completed!"
echo ""
echo "📋 Build Summary:"
echo "   • Version: $APP_VERSION"
echo "   • Platform: $(uname -s)"
echo "   • Build directory: $(pwd)"
echo ""
echo "📝 Next steps:"
echo "   1. Test the built application"
echo "   2. Check FFmpeg dependency installation"
echo "   3. Verify all features work correctly"
echo ""
echo "📚 For more details, see BUILD_INSTRUCTIONS.md"