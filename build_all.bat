@echo off
REM 一鍵建置腳本 - 檔案豪幫手 (Windows版本)

setlocal enabledelayedexpansion

set APP_NAME=檔案豪幫手
set APP_VERSION=2.0.0

echo 🚀 Building %APP_NAME% v%APP_VERSION% for Windows...
echo ==================================================

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.7 or higher.
    pause
    exit /b 1
)

REM Create build directory
if not exist builds mkdir builds
cd builds

echo 🪟 Building Windows version...

REM Install PyInstaller if not installed
echo 📥 Installing PyInstaller...
pip install pyinstaller --quiet

REM Copy source files
xcopy /E /I /Y ..\src src >nul
copy ..\main.py . >nul
copy ..\build_windows.py . >nul
copy ..\README.md . >nul

echo 📦 Building Windows executable...
python build_windows.py

REM Check if build was successful
if exist "dist\%APP_NAME%.exe" (
    echo ✅ Windows build successful!
    echo    📁 Location: builds\dist\%APP_NAME%.exe

    REM Check if NSIS is available for installer
    makensis /VERSION >nul 2>&1
    if not errorlevel 1 (
        echo 📦 Creating installer with NSIS...
        makensis installer.nsi
        if exist "%APP_NAME%_%APP_VERSION%_Setup.exe" (
            echo ✅ Installer created: %APP_NAME%_%APP_VERSION%_Setup.exe
        )
    ) else (
        echo ⚠️  NSIS not found - installer creation skipped
        echo    💡 Install NSIS from https://nsis.sourceforge.io/ to create installer
    )
) else (
    echo ❌ Windows build failed!
    pause
    exit /b 1
)

echo ==================================================
echo 🎉 Build process completed!
echo.
echo 📋 Build Summary:
echo    • Version: %APP_VERSION%
echo    • Platform: Windows
echo    • Build directory: %CD%
echo.
echo 📝 Next steps:
echo    1. Test the built application: dist\%APP_NAME%.exe
echo    2. Ensure FFmpeg is installed and in PATH
echo    3. Verify all features work correctly
echo.
echo 📚 For more details, see BUILD_INSTRUCTIONS.md

pause