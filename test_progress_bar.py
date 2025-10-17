#!/usr/bin/env python3
"""
Progress Bar Test
Test the shared progress bar functionality
"""

import sys
import os
import tkinter as tk
import threading
import time

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from media_converter import TabbedMediaConverter

def test_progress_bar_update():
    """Test progress bar update functionality"""
    print("Testing progress bar update...")

    root = tk.Tk()
    app = TabbedMediaConverter(root)

    def test_progress_simulation():
        """Simulate progress updates"""
        print("Starting progress simulation...")

        # Test YouTube-style progress
        for i in range(0, 101, 10):
            print(f"Setting progress to {i}%")

            def update_ui(progress=i):
                app.shared_progress.config(value=progress)
                app.progress_percent.config(text=f"{progress}%")
                app.combined_status.config(text=f"Testing... {progress}%")
                root.update()

            root.after(0, update_ui)
            time.sleep(0.5)

        print("Progress test completed!")

        # Reset
        def reset_ui():
            app.shared_progress.config(value=0)
            app.progress_percent.config(text="0%")
            app.combined_status.config(text="Test completed")

        root.after(0, reset_ui)

    # Start test in separate thread
    test_thread = threading.Thread(target=test_progress_simulation)
    test_thread.daemon = True
    test_thread.start()

    # Run GUI for 10 seconds then close
    root.after(10000, root.quit)
    root.mainloop()

def test_file_size_calculation():
    """Test file size calculation logic"""
    print("\nTesting file size calculation...")

    # Test scenarios
    test_cases = [
        {"file_size_mb": 300, "target_size_mb": 190, "expected_parts": 2},
        {"file_size_mb": 500, "target_size_mb": 100, "expected_parts": 5},
        {"file_size_mb": 150, "target_size_mb": 190, "expected_parts": 1},
        {"file_size_mb": 1000, "target_size_mb": 50, "expected_parts": 20}
    ]

    for case in test_cases:
        file_size_bytes = case["file_size_mb"] * 1024 * 1024
        target_size_bytes = case["target_size_mb"] * 1024 * 1024

        # Current logic calculation
        calculated_parts = max(1, int((file_size_bytes + target_size_bytes - 1) // target_size_bytes))

        print(f"File: {case['file_size_mb']}MB, Target: {case['target_size_mb']}MB")
        print(f"Expected parts: {case['expected_parts']}, Calculated: {calculated_parts}")
        print(f"Match: {'✓' if calculated_parts == case['expected_parts'] else '✗'}")
        print()

if __name__ == "__main__":
    print("=== Progress Bar and Split Logic Test ===")

    # Test file size calculation first
    test_file_size_calculation()

    # Test progress bar updates
    test_progress_bar_update()