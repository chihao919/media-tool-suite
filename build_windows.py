#!/usr/bin/env python3
"""
Build script for Windows executable using PyInstaller
"""

import sys
import os
import subprocess

APP_NAME = '檔案豪幫手'
APP_VERSION = '2.0.0'
MAIN_SCRIPT = 'main.py'

def build_windows_exe():
    """Build Windows executable using PyInstaller"""

    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--name', APP_NAME,
        '--onefile',  # Single executable
        '--windowed',  # GUI application (no console)
        '--add-data', 'src;src',  # Include src directory
        '--add-data', 'README.md;.',  # Include README
        '--hidden-import', 'tkinter',
        '--hidden-import', 'tkinter.ttk',
        '--hidden-import', 'pathlib',
        '--hidden-import', 'json',
        '--hidden-import', 'subprocess',
        '--hidden-import', 'threading',
        '--exclude-module', 'matplotlib',
        '--exclude-module', 'numpy',
        '--exclude-module', 'scipy',
        '--exclude-module', 'pandas',
        # '--icon', 'icon.ico',  # Add icon file if available
        MAIN_SCRIPT
    ]

    print(f"Building {APP_NAME} for Windows...")
    print(f"Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build successful!")
        print(f"Executable created in: dist/{APP_NAME}.exe")
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ PyInstaller not found. Install it with: pip install pyinstaller")
        return False

    return True

def create_installer():
    """Create NSIS installer script"""
    nsis_script = f'''
; NSIS Script for {APP_NAME}
!define APP_NAME "{APP_NAME}"
!define APP_VERSION "{APP_VERSION}"
!define APP_PUBLISHER "Claude Code Assistant"
!define APP_EXE "${{APP_NAME}}.exe"

; Installer settings
Name "${{APP_NAME}} ${{APP_VERSION}}"
OutFile "${{APP_NAME}}_${{APP_VERSION}}_Setup.exe"
InstallDir "$PROGRAMFILES\\${{APP_NAME}}"
RequestExecutionLevel admin

; Pages
Page directory
Page instfiles

Section "Main Application"
    SetOutPath "$INSTDIR"
    File "dist\\${{APP_EXE}}"
    File "README.md"

    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
    CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXE}}"
    CreateShortCut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXE}}"

    ; Registry entries
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayName" "${{APP_NAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "UninstallString" "$INSTDIR\\Uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "Publisher" "${{APP_PUBLISHER}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayVersion" "${{APP_VERSION}}"

    ; Create uninstaller
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\${{APP_EXE}}"
    Delete "$INSTDIR\\README.md"
    Delete "$INSTDIR\\Uninstall.exe"
    RMDir "$INSTDIR"

    Delete "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk"
    RMDir "$SMPROGRAMS\\${{APP_NAME}}"
    Delete "$DESKTOP\\${{APP_NAME}}.lnk"

    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}"
SectionEnd
'''

    with open('installer.nsi', 'w', encoding='utf-8') as f:
        f.write(nsis_script)

    print("✅ NSIS installer script created: installer.nsi")
    print("   To build installer, run: makensis installer.nsi")

if __name__ == '__main__':
    print("Building Windows version of 檔案豪幫手...")

    # Build executable
    if build_windows_exe():
        # Create installer script
        create_installer()
        print("\\n📦 Windows build complete!")
        print(f"   • Executable: dist/{APP_NAME}.exe")
        print("   • Installer script: installer.nsi")
        print("\\nTo create installer:")
        print("   1. Install NSIS from https://nsis.sourceforge.io/")
        print("   2. Run: makensis installer.nsi")
    else:
        print("\\n❌ Build failed!")
        sys.exit(1)