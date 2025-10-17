#!/usr/bin/env python3
"""
Test Canvas Progress Bar Updates
Test if the Canvas-based progress bar updates correctly
"""

import tkinter as tk
from tkinter import ttk
import time
import threading

class ProgressBarTest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Canvas Progress Bar Test")
        self.root.geometry("300x600")

        # Create progress frame
        progress_frame = ttk.Frame(self.root)
        progress_frame.pack(pady=20)

        # Progress label
        ttk.Label(progress_frame, text="Progress Test", font=('Helvetica', 12, 'bold')).pack(pady=(0, 10))

        # Create Canvas progress bar (same as media_converter.py)
        self.progress_canvas = tk.Canvas(progress_frame, width=38, height=400, bg='#E0E0E0',
                                       relief='sunken', bd=1, highlightthickness=0)
        self.progress_canvas.pack(pady=5)

        # Initialize progress bar components
        self._progress_bg = self.progress_canvas.create_rectangle(0, 0, 38, 400,
                                                                fill='#E0E0E0', outline='')
        self._progress_fill = self.progress_canvas.create_rectangle(0, 400, 38, 400,
                                                                  fill='#2E8B57', outline='')
        self._progress_value = 0

        # Progress percentage label
        self.progress_percent = ttk.Label(progress_frame, text="0%", font=('Helvetica', 14, 'bold'))
        self.progress_percent.pack(pady=(10, 0))

        # Test buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="Test Manual Update",
                  command=self.test_manual_update).pack(pady=5)
        ttk.Button(button_frame, text="Test Auto Progress",
                  command=self.test_auto_progress).pack(pady=5)
        ttk.Button(button_frame, text="Reset Progress",
                  command=self.reset_progress).pack(pady=5)

        # Status label
        self.status_label = ttk.Label(self.root, text="Ready for testing",
                                    font=('Helvetica', 10), foreground='blue')
        self.status_label.pack(pady=10)

    def update_progress_bar(self, value):
        """Update the custom progress bar (value: 0-100) - Same as media_converter.py"""
        print(f"DEBUG: update_progress_bar called with value: {value}")

        self._progress_value = max(0, min(100, value))

        # Calculate fill height
        fill_height = (self._progress_value / 100) * 400
        fill_top = 400 - fill_height

        # Update the progress fill rectangle
        self.progress_canvas.coords(self._progress_fill, 0, fill_top, 38, 400)

        # Update percentage label
        self.progress_percent.config(text=f"{int(self._progress_value)}%")

        print(f"DEBUG: Progress set to {self._progress_value}%, fill_height={fill_height}, fill_top={fill_top}")

    def test_manual_update(self):
        """Test manual progress updates"""
        self.status_label.config(text="Testing manual updates...")

        # Test various values
        test_values = [0, 25, 50, 75, 100]

        for i, value in enumerate(test_values):
            def update_ui(v=value):
                self.update_progress_bar(v)
                self.status_label.config(text=f"Manual test: {v}%")

            # Schedule the update after delay
            self.root.after(i * 1000, update_ui)

        # Reset after all tests
        self.root.after(len(test_values) * 1000,
                       lambda: self.status_label.config(text="Manual test completed"))

    def test_auto_progress(self):
        """Test automatic progress simulation"""
        self.status_label.config(text="Starting auto progress test...")
        self.update_progress_bar(0)

        # Start thread for automatic progress
        thread = threading.Thread(target=self._auto_progress_worker)
        thread.daemon = True
        thread.start()

    def _auto_progress_worker(self):
        """Worker thread for automatic progress simulation"""
        try:
            for i in range(101):  # 0 to 100
                progress = i

                # Use root.after to update UI from main thread
                def update_ui(p=progress):
                    self.update_progress_bar(p)
                    self.status_label.config(text=f"Auto progress: {p}%")

                self.root.after(0, update_ui)
                time.sleep(0.05)  # 50ms delay

            # Final message
            self.root.after(0, lambda: self.status_label.config(text="Auto progress completed"))

        except Exception as e:
            print(f"Error in auto progress: {e}")
            self.root.after(0, lambda: self.status_label.config(text=f"Error: {e}"))

    def reset_progress(self):
        """Reset progress to 0"""
        self.update_progress_bar(0)
        self.status_label.config(text="Progress reset to 0%")

    def run(self):
        """Start the test application"""
        print("🎯 Canvas Progress Bar Test Started")
        print("Use the buttons to test different update scenarios")
        self.root.mainloop()

if __name__ == "__main__":
    test_app = ProgressBarTest()
    test_app.run()