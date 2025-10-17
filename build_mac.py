#!/usr/bin/env python3
"""
Build script for macOS application using py2app
"""

import sys
import os
import subprocess
from setuptools import setup

# Ensure we're on macOS
if sys.platform != 'darwin':
    print("This script is for macOS only!")
    sys.exit(1)

# Application configuration
APP_NAME = '檔案豪幫手'
APP_VERSION = '2.0.0'
MAIN_SCRIPT = 'main.py'

# py2app options
OPTIONS = {
    'argv_emulation': True,
    'packages': ['tkinter', 'pathlib', 'json', 'subprocess', 'threading'],
    'includes': ['src.media_converter', 'src.media_processor', 'src.media_handlers',
                'src.process_strategies', 'src.app_constants'],
    'excludes': ['matplotlib', 'numpy', 'scipy', 'pandas'],
    'strip': False,  # Don't strip binaries to avoid signature invalidation
    'resources': ['src/', 'README.md'],
    'iconfile': None,  # Add .icns file path if you have an icon
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleVersion': APP_VERSION,
        'CFBundleShortVersionString': APP_VERSION,
        'CFBundleIdentifier': 'com.claude.mediatoolsuite',
        'CFBundleExecutable': APP_NAME,
        'LSMinimumSystemVersion': '10.9.0',
        'NSHumanReadableCopyright': 'Copyright © 2025 Claude Code Assistant',
        'NSRequiresAquaSystemAppearance': False,
    },
}

def sign_app(app_path):
    """Sign the built application and all its components"""
    print(f"Signing {app_path}...")
    try:
        # First, sign all dylibs and frameworks inside the app
        frameworks_path = os.path.join(app_path, 'Contents/Frameworks')
        resources_path = os.path.join(app_path, 'Contents/Resources')

        # Sign all .so and .dylib files
        for root, dirs, files in os.walk(app_path):
            for file in files:
                if file.endswith('.so') or file.endswith('.dylib'):
                    file_path = os.path.join(root, file)
                    print(f"  Signing {file}...")
                    subprocess.run(['codesign', '--force', '--sign', '-', file_path],
                                  capture_output=True, check=False)

        # Remove existing signature from main app
        subprocess.run(['codesign', '--remove-signature', app_path],
                      capture_output=True, check=False)

        # Sign the main app bundle with deep signing
        subprocess.run(['codesign', '--force', '--deep', '--sign', '-', '--options=runtime', app_path],
                      capture_output=True, check=True)

        # Verify signature
        result = subprocess.run(['codesign', '--verify', '--verbose', app_path],
                               capture_output=True, check=True, text=True)
        print("✅ App signed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Code signing failed: {e}")
        print(f"Error output: {e.stderr.decode() if e.stderr else 'No error output'}")
        return False

if __name__ == '__main__':
    setup(
        name=APP_NAME,
        app=[MAIN_SCRIPT],
        version=APP_VERSION,
        setup_requires=['py2app'],
        options={'py2app': OPTIONS},
    )

    # Sign the built app if it exists
    app_path = f"dist/{APP_NAME}.app"
    if os.path.exists(app_path):
        sign_app(app_path)