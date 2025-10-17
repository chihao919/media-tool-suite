#!/usr/bin/env python3
"""
檔案豪幫手 - Media Tool Suite
Main entry point for the application
"""

import sys
import os
import tkinter as tk

# Add src directory to Python path
if hasattr(sys, '_MEIPASS'):
    # PyInstaller environment
    src_path = os.path.join(sys._MEIPASS, 'src')
elif getattr(sys, 'frozen', False):
    # py2app environment - files are directly in Resources
    src_path = os.path.join(os.path.dirname(sys.executable), '..', 'Resources')
else:
    # Development environment
    src_path = os.path.join(os.path.dirname(__file__), 'src')

if src_path not in sys.path:
    sys.path.insert(0, src_path)

from media_converter import TabbedMediaConverter

def main():
    """Main application entry point"""
    try:
        root = tk.Tk()
        app = TabbedMediaConverter(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        return 1
    return 0

if __name__ == "__main__":
    exit(main())